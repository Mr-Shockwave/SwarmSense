"""Per-rover subagents — vision, research, error.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

Each physical rover (rover1, rover2) has its own trio of subagents supervised by
that rover's manager (see rover_managers.py): vision (frame analysis),
research (summarize findings), and error (fault diagnosis).

Pattern: managers invoke subagents via delegation tools (see rover_managers.py),
not hierarchical CrewAI Process — required by CrewAI 1.x (manager agents cannot
hold tools in hierarchical crews).
"""
from __future__ import annotations

import asyncio
import base64
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task

from vision_pipeline.analyzer import analyze_photo
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

SUBAGENT_TOOLS = [redis_get, redis_set, redis_publish]


def _llm() -> LLM | None:
    if not settings.OPENAI_API_KEY:
        return None
    return LLM(model=settings.OPENAI_ORCHESTRATION_MODEL, api_key=settings.OPENAI_API_KEY)


def subagent_label(rover_id: str, role: str) -> str:
    return f"{rover_id}:{role}"


def _run_sync(coro: Any) -> Any:
    """Run an async coroutine from sync code, even if a loop is already running."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    # Already inside a running loop: hop to a worker thread with its own loop.
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(lambda: asyncio.run(coro)).result()


def _latest_frame(images_key: str) -> str | None:
    """Most recent cached base64 frame for a rover, or None if none cached."""
    try:
        client = get_sync_redis()
        raw = client.lindex(images_key, -1)
    except Exception:  # noqa: BLE001
        return None
    if raw is None:
        return None
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "ignore")
    # Frame may be a bare base64 string or wrapped in JSON ({"b64": ...}).
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError):
        return raw
    if isinstance(obj, dict):
        return obj.get("b64") or obj.get("image")
    return raw if isinstance(raw, str) else None


# ── Frame dedup (perceptual hash) ────────────────────────────────────────────

DEDUP_HAMMING_THRESHOLD = 6   # dHash bit distance; <= this => treat as same scene
IMAGE_TTL_SECONDS = 3600      # content-addressed frames expire after an hour


def _perceptual_hash(photo_b64: str) -> int | None:
    """64-bit dHash of a base64 JPEG. None if it can't be decoded (dedup disabled)."""
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
        return bits
    except Exception:  # noqa: BLE001
        return None


def _hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def _store_image(image_id: str, photo_b64: str) -> None:
    """Content-address the frame once, with a TTL so it self-expires."""
    try:
        get_sync_redis().set(f"image:{image_id}", photo_b64, ex=IMAGE_TTL_SECONDS)
    except Exception:  # noqa: BLE001
        pass


# ── Runtimes (used by --dry-run and as reference behaviour) ──────────────────


def run_vision_subagent(rover_id: str) -> dict[str, Any]:
    """Analyze the rover's latest frame against mission criteria.

    Dedupes near-identical frames via a perceptual hash so a static scene
    captured every few seconds doesn't re-run vision or re-store the image. The
    frame is content-addressed at image:<image_id> and referenced by id from the
    findings JSON, rather than inlined on every write (which would bloat Redis).
    Empty `findings` => target not found.
    """
    criteria = redis_get_raw("mission:criteria") or "(no criteria)"
    images_key = f"{rover_id}:images"
    photo_b64 = _latest_frame(images_key)

    phash = _perceptual_hash(photo_b64) if photo_b64 else None
    prev = redis_get_raw(f"{rover_id}:vision:state") or {}
    is_duplicate = (
        phash is not None
        and prev.get("hash") is not None
        and prev.get("criteria") == criteria
        and _hamming(phash, int(prev["hash"])) <= DEDUP_HAMMING_THRESHOLD
    )

    if is_duplicate:
        # Same scene + same criteria as last cycle: reuse, skip vision + re-store.
        image_id = prev.get("image_id")
        cached = redis_get_raw(f"{rover_id}:vision:findings") or {"findings": []}
        findings = cached.get("findings", [])
    else:
        image_id = f"{phash:016x}" if phash is not None else None
        vision: dict[str, Any] = {"findings": []}
        if photo_b64:
            vision = _run_sync(analyze_photo(photo_b64, str(criteria)))
        findings = vision.get("findings", [])
        if photo_b64 and image_id:
            _store_image(image_id, photo_b64)
        redis_set_raw(
            f"{rover_id}:vision:state",
            {"hash": phash, "image_id": image_id, "criteria": criteria},
        )

    # Canonical analyze_photo JSON, now carrying the image reference.
    vision_payload = {"findings": findings, "image_id": image_id}
    redis_set_raw(f"{rover_id}:vision:findings", vision_payload)

    result = {
        "agent": subagent_label(rover_id, "vision"),
        "match": bool(findings),   # derived, for existing consumers of vision:last
        "findings": findings,      # canonical output
        "image_id": image_id,      # fetch the frame at image:<image_id>
        "criteria": criteria,
        "has_frame": photo_b64 is not None,
        "deduped": is_duplicate,
    }
    redis_set_raw(f"{rover_id}:vision:last", result)
    if findings and not is_duplicate:  # don't re-publish a static match every cycle
        redis_publish_raw(f"{rover_id}:vision", vision_payload)
        # TODO [Person 1 + Person 2]: call findings_state.add_finding(...) so the
        # scientist UI receives scientist:ping (see redis_layer/findings_state.py).
    return result


def run_research_subagent(rover_id: str) -> dict[str, Any]:
    """Summarize vision findings for this rover (stub — no LLM required for dry-run)."""
    criteria = redis_get_raw("mission:criteria") or "(no criteria)"
    vision_data = redis_get_raw(f"{rover_id}:vision:findings") or {}
    if not vision_data.get("findings"):
        last = redis_get_raw(f"{rover_id}:vision:last") or {}
        vision_data = {"findings": last.get("findings", []), "image_id": last.get("image_id")}

    findings = vision_data.get("findings", [])
    summary = ""
    if findings:
        labels = [f.get("label", "object") for f in findings]
        summary = (
            f"Research summary for {rover_id}: detected {len(findings)} candidate(s) "
            f"matching criteria {criteria!r}: {', '.join(labels)}."
        )

    result = {
        "agent": subagent_label(rover_id, "research"),
        "findings_count": len(findings),
        "summary": summary or f"No findings to research for {rover_id}.",
        "criteria": criteria,
        "image_id": vision_data.get("image_id"),
    }
    redis_set_raw(f"{rover_id}:research:last", result)
    if findings:
        redis_publish_raw(f"{rover_id}:research", result)
    return result


def run_error_subagent(rover_id: str) -> dict[str, Any]:
    """Diagnose the latest faults logged for this rover (stub)."""
    errors = redis_get_raw(f"{rover_id}:errors") or []
    if not isinstance(errors, list):
        errors = [errors] if errors else []

    diagnosis = ""
    if errors:
        latest = errors[0] if errors else {}
        diagnosis = (
            f"Error analysis for {rover_id}: {len(errors)} fault(s) on record. "
            f"Latest: {latest!r}. Recommend inspect sensors and retry last action."
        )

    result = {
        "agent": subagent_label(rover_id, "error"),
        "error_count": len(errors),
        "diagnosis": diagnosis or f"No faults recorded for {rover_id}.",
        "errors": errors[:5],
    }
    redis_set_raw(f"{rover_id}:error:last", result)
    if errors:
        redis_publish_raw(f"{rover_id}:error", result)
    return result


# ── CrewAI Agent factories ───────────────────────────────────────────────────


def build_vision_subagent(rover_id: str, llm: LLM | None = None) -> Agent:
    return Agent(
        role=f"{rover_id} Vision Specialist",
        goal=f"Detect objects matching mission criteria in {rover_id} photos",
        backstory=(
            f"You are the on-rover vision analyst for {rover_id}. "
            "Read mission:criteria from Redis, inspect cached frames, and report matches."
        ),
        tools=SUBAGENT_TOOLS,
        llm=llm or _llm(),
        verbose=True,
        allow_delegation=False,
    )


def build_research_subagent(rover_id: str, llm: LLM | None = None) -> Agent:
    return Agent(
        role=f"{rover_id} Research Specialist",
        goal=f"Produce contextual analysis of {rover_id}'s vision findings",
        backstory=(
            f"You are the field researcher for {rover_id}. "
            f"Read {rover_id}:vision:findings or {rover_id}:vision:last and mission:criteria; "
            "summarize detected objects for the scientist."
        ),
        tools=SUBAGENT_TOOLS,
        llm=llm or _llm(),
        verbose=True,
        allow_delegation=False,
    )


def build_error_subagent(rover_id: str, llm: LLM | None = None) -> Agent:
    return Agent(
        role=f"{rover_id} Error Analyst",
        goal=f"Diagnose and report faults recorded for {rover_id}",
        backstory=(
            f"You are the error analyst for {rover_id}. "
            f"Read {rover_id}:errors from Redis, diagnose the latest fault, "
            "and recommend remediation."
        ),
        tools=SUBAGENT_TOOLS,
        llm=llm or _llm(),
        verbose=True,
        allow_delegation=False,
    )


def build_rover_subagents(rover_id: str, llm: LLM | None = None) -> dict[str, Agent]:
    shared = llm or _llm()
    return {
        "vision": build_vision_subagent(rover_id, shared),
        "research": build_research_subagent(rover_id, shared),
        "error": build_error_subagent(rover_id, shared),
    }


def run_subagent_crew(rover_id: str, role: str, instruction: str, llm: LLM | None = None) -> str:
    """Run a single subagent in its own one-task crew (invoked by manager delegation tools)."""
    builders = {
        "vision": build_vision_subagent,
        "research": build_research_subagent,
        "error": build_error_subagent,
    }
    agent = builders[role](rover_id, llm)
    task = Task(
        description=instruction,
        expected_output=f"{subagent_label(rover_id, role)} report.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    return str(crew.kickoff())


def format_subagent_result(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2)