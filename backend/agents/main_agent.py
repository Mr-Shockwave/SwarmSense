"""Main agent — GPT-4o CrewAI orchestrator over an image-dedup gate.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

A single GPT-4o agent for the rover fleet. For each rover's latest frame it
decides whether work is needed, using two delegation tools:

  - check_frame(rover_id)   -> is this frame already analyzed? (by image id)
  - analyze_frame(rover_id) -> if new, create {image_id, findings, errors} and
                               dispatch the frame to the subagents.

Design note: the tools take a rover_id, NOT the image. They read the frame from
Redis internally and return only its image_id, so the raw base64 never enters
the LLM context (a base64 blob in tool-call args would blow the token budget).
The agent reasons over small JSON; the deterministic engine below does the
hashing, the Redis existence check, and the dispatch. This mirrors the
delegation-tool pattern in rover_managers.py.
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool

from agents.vision import analyze_photo
from config import settings
from tools.redis_tools import (
    get_sync_redis,
    redis_get,
    redis_get_raw,
    redis_publish,
    redis_publish_raw,
    redis_set,
    redis_set_raw,
)

log = logging.getLogger(__name__)

FLEET = ("rover1", "rover2")
IMAGE_TTL_SECONDS = 3600
ANALYSIS_TTL_SECONDS = 3600
MAIN_AGENT_REDIS_TOOLS = [redis_get, redis_set, redis_publish]


# ── Deterministic engine ─────────────────────────────────────────────────────


def _analysis_key(image_id: str) -> str:
    return f"analysis:{image_id}"


def _run_sync(coro: Any) -> Any:
    """Run an async coroutine from sync (tool) code, loop or no loop."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(lambda: asyncio.run(coro)).result()


def compute_image_id(photo_b64: str) -> str | None:
    """Perceptual fingerprint (dHash) of the frame's pixels -> 16-hex id.

    Decodes the JPEG, reduces it, and hashes the structure so visually-identical
    frames map to the same id (a crypto hash would not, due to sensor noise /
    re-encoding). Returns None if the frame can't be decoded.

    NOTE: duplicates rover_subagents._perceptual_hash — promote both to a shared
    util (e.g. tools/image_utils.py) so the gate and the vision backstop agree.
    """
    try:
        import cv2
        import numpy as np

        arr = np.frombuffer(base64.b64decode(photo_b64), dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
        small = cv2.resize(img, (9, 8), interpolation=cv2.INTER_AREA)
        diff = small[:, 1:] > small[:, :-1]  # 8x8 = 64 bits
        bits = 0
        for v in diff.flatten():
            bits = (bits << 1) | int(v)
        return f"{bits:016x}"
    except Exception:  # noqa: BLE001
        return None


def _latest_frame(rover_id: str) -> str | None:
    """Most recent cached base64 frame for a rover, or None."""
    try:
        raw = get_sync_redis().lindex(f"{rover_id}:images", -1)
    except Exception:  # noqa: BLE001
        return None
    if raw is None:
        return None
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "ignore")
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError):
        return raw
    if isinstance(obj, dict):
        return obj.get("b64") or obj.get("image")
    return raw if isinstance(raw, str) else None


def _store_image(image_id: str, photo_b64: str) -> None:
    try:
        get_sync_redis().set(f"image:{image_id}", photo_b64, ex=IMAGE_TTL_SECONDS)
    except Exception:  # noqa: BLE001
        pass


def _claim_new(image_id: str, record: dict) -> bool:
    """Atomically create the analysis record only if absent (SETNX)."""
    try:
        return bool(
            get_sync_redis().set(
                _analysis_key(image_id),
                json.dumps(record),
                nx=True,
                ex=ANALYSIS_TTL_SECONDS,
            )
        )
    except Exception:  # noqa: BLE001
        return False


def _save_record(image_id: str, record: dict) -> None:
    try:
        get_sync_redis().set(
            _analysis_key(image_id), json.dumps(record), ex=ANALYSIS_TTL_SECONDS
        )
    except Exception:  # noqa: BLE001
        redis_set_raw(_analysis_key(image_id), record)


async def process_image(photo_b64: str, rover_id: str | None = None, coord: Any = None) -> dict:
    """Dedup an incoming frame by image id, dispatch to subagents if new.

    Returns {"status": "cached"|"analyzed"|"unhashable", "image_id", "analysis"}.
    """
    image_id = compute_image_id(photo_b64)
    if image_id is None:
        return {"status": "unhashable", "image_id": None, "analysis": None}

    existing = redis_get_raw(_analysis_key(image_id))
    if existing is not None:
        return {"status": "cached", "image_id": image_id, "analysis": existing}

    record: dict[str, Any] = {"image_id": image_id, "findings": [], "errors": []}
    if rover_id:
        record["rover_id"] = rover_id
    if coord is not None:
        record["coord"] = coord

    if not _claim_new(image_id, record):
        return {
            "status": "cached",
            "image_id": image_id,
            "analysis": redis_get_raw(_analysis_key(image_id)),
        }

    _store_image(image_id, photo_b64)
    criteria = redis_get_raw("mission:criteria") or "(no criteria)"
    try:
        vision = await analyze_photo(photo_b64, str(criteria))
        record["findings"] = vision.get("findings", [])
    except Exception as exc:  # noqa: BLE001
        record["errors"].append({"stage": "vision", "error": str(exc)})
        log.warning("process_image vision failed for %s: %s", image_id, exc)

    _save_record(image_id, record)
    redis_publish_raw("analysis:new", record)
    return {"status": "analyzed", "image_id": image_id, "analysis": record}


# ── GPT-4o main agent (CrewAI) ───────────────────────────────────────────────


def _llm() -> LLM | None:
    if not settings.OPENAI_API_KEY:
        return None
    return LLM(model=settings.OPENAI_ORCHESTRATION_MODEL, api_key=settings.OPENAI_API_KEY)


def _main_agent_tools() -> list:
    """Delegation tools that wrap the deterministic engine. They take a rover_id
    and read the frame from Redis — the raw image never reaches the LLM."""

    @tool("check_frame")
    def check_frame(rover_id: str) -> str:
        """Check whether a rover's latest frame has already been analyzed.

        Reads the frame from Redis, computes its image id, and reports status.
        Returns JSON: {rover_id, image_id, already_analyzed, has_frame}.
        """
        photo_b64 = _latest_frame(rover_id)
        if not photo_b64:
            return json.dumps({"rover_id": rover_id, "has_frame": False})
        image_id = compute_image_id(photo_b64)
        analyzed = image_id is not None and redis_get_raw(_analysis_key(image_id)) is not None
        return json.dumps(
            {
                "rover_id": rover_id,
                "image_id": image_id,
                "already_analyzed": bool(analyzed),
                "has_frame": True,
            }
        )

    @tool("analyze_frame")
    def analyze_frame(rover_id: str) -> str:
        """Analyze a rover's latest frame if it is new.

        Creates the {image_id, findings, errors} record and dispatches the frame
        to the vision subagent. No-op (status=cached) if already analyzed.
        Returns JSON: {status, image_id, findings, errors}.
        """
        photo_b64 = _latest_frame(rover_id)
        if not photo_b64:
            return json.dumps({"status": "no_frame", "rover_id": rover_id})
        result = _run_sync(process_image(photo_b64, rover_id=rover_id))
        analysis = result.get("analysis") or {}
        return json.dumps(
            {
                "status": result.get("status"),
                "image_id": result.get("image_id"),
                "findings": analysis.get("findings", []),
                "errors": analysis.get("errors", []),
            }
        )

    return [check_frame, analyze_frame]


def build_main_agent(llm: LLM | None = None) -> Agent:
    """The single GPT-4o main agent for the fleet."""
    shared = llm or _llm()
    return Agent(
        role="Mission Main Agent",
        goal=(
            "Avoid redundant analysis: for each rover's latest frame, check whether "
            "it is already analyzed and only analyze genuinely new frames."
        ),
        backstory=(
            "You are the single main agent for the rover fleet. Every frame is "
            "identified by a perceptual image id. If a frame's id already has an "
            "analysis record, the work is done — do nothing. Otherwise create the "
            "{image_id, findings, errors} record and dispatch the frame to the "
            "subagents. You never inspect raw image bytes yourself; use check_frame "
            "and analyze_frame, which operate on frames stored in Redis."
        ),
        tools=MAIN_AGENT_REDIS_TOOLS + _main_agent_tools(),
        llm=shared,
        verbose=True,
        allow_delegation=False,
    )


def _main_task_description(rovers: tuple[str, ...]) -> str:
    listed = ", ".join(rovers)
    return f"""
You are the main agent for the rover fleet ({listed}). For EACH rover, in order:

1. Call check_frame(rover_id).
2. If has_frame is false, skip that rover.
3. If already_analyzed is true, the analysis is complete — do nothing for it.
4. If already_analyzed is false, call analyze_frame(rover_id) to create the
   {{image_id, findings, errors}} record and dispatch the frame to the subagents.

Return a concise summary: for each rover, its image_id and whether it was newly
analyzed, already complete, or had no frame.
""".strip()


def build_main_crew(llm: LLM | None = None, rovers: tuple[str, ...] = FLEET) -> Crew:
    agent = build_main_agent(llm)
    task = Task(
        description=_main_task_description(rovers),
        expected_output="Per-rover summary: image_id + newly-analyzed | already-complete | no-frame.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)


def run_main_dry(rovers: tuple[str, ...] = FLEET) -> dict[str, Any]:
    """No-LLM path: run the gate deterministically over each rover's latest frame."""
    out: dict[str, Any] = {}
    for rover_id in rovers:
        photo_b64 = _latest_frame(rover_id)
        if not photo_b64:
            out[rover_id] = {"status": "no_frame"}
            continue
        out[rover_id] = _run_sync(process_image(photo_b64, rover_id=rover_id))
    return out
