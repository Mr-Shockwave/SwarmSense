"""Per-rover subagents — vision, navigation, collection.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

Each physical rover (rover1, rover2) has its own trio of subagents supervised by
that rover's manager (see rover_managers.py). These replace rover-specific work
that mission-level agents/vision.py and collection_planner.py handle at the
*mission* scope (cross-rover photo review, nearest-rover target assignment).

Pattern: managers invoke subagents via delegation tools (see rover_managers.py),
not hierarchical CrewAI Process — required by CrewAI 1.x (manager agents cannot
hold tools in hierarchical crews).
"""
from __future__ import annotations

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task

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


# ── Runtimes (used by --dry-run and as reference behaviour) ──────────────────


def run_vision_subagent(rover_id: str) -> dict[str, Any]:
    """Analyze the rover's latest frame against mission criteria.

    Calls the shared GPT-4o vision primitive (agents.vision.analyze_photo) and
    emits the canonical findings shape. Empty `findings` => target not found.
    """
    criteria = redis_get_raw("mission:criteria") or "(no criteria)"
    images_key = f"{rover_id}:images"
    photo_b64 = _latest_frame(images_key)

    findings: list[dict[str, Any]] = []
    if photo_b64:
        vision = _run_sync(analyze_photo(photo_b64, str(criteria)))
        findings = vision.get("findings", [])

    result = {
        "agent": subagent_label(rover_id, "vision"),
        "match": bool(findings),   # derived, for existing consumers of vision:last
        "findings": findings,      # canonical output
        "criteria": criteria,
        "has_frame": photo_b64 is not None,
    }
    redis_set_raw(f"{rover_id}:vision:last", result)
    if findings:
        redis_publish_raw(f"{rover_id}:vision", result)
    return result


def run_navigation_subagent(rover_id: str) -> dict[str, Any]:
    """Plan the next exploration step inside the rover's assigned zone."""
    zone = redis_get_raw(f"{rover_id}:zone") or {}
    position = redis_get_raw(f"{rover_id}:position") or {"x": zone.get("x_min", 0), "y": 0, "heading": 0}
    x = int(position.get("x", zone.get("x_min", 0)))
    y = int(position.get("y", 0))
    next_x = min(x + 1, zone.get("x_max", x))
    next_pos = {"x": next_x, "y": y, "heading": position.get("heading", 0)}
    redis_set_raw(f"{rover_id}:position", next_pos)
    result = {
        "agent": subagent_label(rover_id, "navigation"),
        "action": "explore_step",
        "from": position,
        "to": next_pos,
        "zone": zone,
    }
    redis_publish_raw(f"{rover_id}:position", next_pos)
    return result


def run_collection_subagent(rover_id: str) -> dict[str, Any]:
    """Check approved targets assigned to this rover (stub)."""
    assignments = redis_get_raw("targets:assignments") or {}
    mine = {tid: rid for tid, rid in assignments.items() if rid == rover_id}
    result = {
        "agent": subagent_label(rover_id, "collection"),
        "assigned_targets": mine,
        "action": "idle" if not mine else "plan_pickup",
    }
    redis_set_raw(f"{rover_id}:collection:last", result)
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


def build_navigation_subagent(rover_id: str, llm: LLM | None = None) -> Agent:
    return Agent(
        role=f"{rover_id} Navigation Specialist",
        goal=f"Explore {rover_id}'s assigned zone and coordinate obstacle avoidance via Redis",
        backstory=(
            f"You plan safe exploration steps for {rover_id} within its zone bounds. "
            f"Read/write {rover_id}:zone and {rover_id}:position; publish position updates."
        ),
        tools=SUBAGENT_TOOLS,
        llm=llm or _llm(),
        verbose=True,
        allow_delegation=False,
    )


def build_collection_subagent(rover_id: str, llm: LLM | None = None) -> Agent:
    return Agent(
        role=f"{rover_id} Collection Specialist",
        goal=f"Retrieve scientist-approved targets assigned to {rover_id}",
        backstory=(
            f"You handle pickup logic for {rover_id}. "
            "Read targets:assignments and report whether any targets need collection."
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
        "navigation": build_navigation_subagent(rover_id, shared),
        "collection": build_collection_subagent(rover_id, shared),
    }


def run_subagent_crew(rover_id: str, role: str, instruction: str, llm: LLM | None = None) -> str:
    """Run a single subagent in its own one-task crew (invoked by manager delegation tools)."""
    builders = {
        "vision": build_vision_subagent,
        "navigation": build_navigation_subagent,
        "collection": build_collection_subagent,
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