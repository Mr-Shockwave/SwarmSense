"""Per-rover conductor + asyncio runner + frame-event listener.

Owner: Person 1 (Agent Logic), workaround wiring by the team.

This is the "conductor" the rest of the agent layer expected but that never
existed (crew.py / agents/__init__.py import from here). It does three jobs:

  1. build_rover_crew(rover_id) — a CrewAI sequential crew wiring the three
     subagents with Task(context=...) so the research agent's prompt contains
     BOTH the vision findings and the error diagnosis. This is the agentic /
     LLM-driven path and the upgrade target once the team settles the main-agent
     refactor.

  2. run_rover_cycle / run_fleet_cycle — an asyncio runner that drives the
     deterministic subagent functions (run_vision/error/research_subagent) in
     order, concurrently across rovers. This is the path that actually executes
     on each new frame today: reliable, fast, and degrades gracefully without an
     orchestration LLM (only analyze_photo uses the OpenAI key). Completion is
     just the awaited return value — no pub/sub control channel, no polling.

  3. agent_frame_listener — subscribes to the existing `rover:frames` channel
     and fires run_rover_cycle(rover_id) for whichever rover produced a frame.
     This is the event-driven trigger; main.py starts it as a background task.

Cross-feed: the deterministic path gets the "error alters research" behaviour
because run_research_subagent now reads {rover_id}:error:last (see
rover_subagents.py). The CrewAI path gets it via Task(context=[...]).

Workaround scope: NONE of this edits main_agent.py. The main-agent refactor
(deciding whether the main agent delegates here vs. keeps its inline
analyze_photo) is a separate decision for the backend owner.
"""
from __future__ import annotations

import asyncio
import json
import logging

import weave
from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool

from config import ROVER_IDS
from tools.redis_tools import redis_get, redis_get_raw, redis_publish, redis_set
from .rover_subagents import (
    _llm,
    build_error_subagent,
    build_research_subagent,
    build_vision_subagent,
    run_error_subagent,
    run_research_subagent,
    run_vision_subagent,
)

logger = logging.getLogger("roverswarm.agents")


# ── CrewAI conductor (LLM-driven, upgrade path) ──────────────────────────────


@tool("analyze_latest_frame")
def analyze_latest_frame(rover_id: str) -> str:
    """Run the vision model on the rover's latest cached frame; returns findings JSON."""
    return json.dumps(run_vision_subagent(rover_id))


def build_rover_manager_agent(rover_id: str, llm: LLM | None = None) -> Agent:
    """A per-rover manager agent (kept for callers that want a supervisor handle)."""
    return Agent(
        role=f"{rover_id} Manager",
        goal=f"Coordinate {rover_id}'s vision, research, and error subagents into one report",
        backstory=(
            f"You supervise {rover_id}'s on-rover subagents. You ensure each frame is "
            "analyzed, faults are diagnosed, and the research summary reflects both."
        ),
        tools=[redis_get, redis_set, redis_publish],
        llm=llm or _llm(),
        verbose=True,
        allow_delegation=False,
    )


def build_rover1_manager_agent(llm: LLM | None = None) -> Agent:
    return build_rover_manager_agent("rover1", llm)


def build_rover2_manager_agent(llm: LLM | None = None) -> Agent:
    return build_rover_manager_agent("rover2", llm)


def build_rover_crew(rover_id: str, llm: LLM | None = None) -> Crew:
    """Sequential crew: vision + error run, research consumes BOTH via task context.

    The research task lists vision_task and error_task in its `context`, so CrewAI
    injects their outputs into the research agent's prompt — that's the
    subagent->subagent comm (e.g. an error diagnosis caveats the research summary).
    """
    shared = llm or _llm()

    # Vision agent needs the real vision tool (the base builder ships Redis tools
    # only); without it the LLM agent can't actually analyze a frame.
    vision = build_vision_subagent(rover_id, shared)
    vision.tools = list(vision.tools) + [analyze_latest_frame]
    error = build_error_subagent(rover_id, shared)
    research = build_research_subagent(rover_id, shared)

    vision_task = Task(
        description=(
            f"Call analyze_latest_frame('{rover_id}') and report the findings JSON "
            "exactly as returned. Do not invent objects."
        ),
        expected_output="The vision findings JSON for this frame.",
        agent=vision,
    )
    error_task = Task(
        description=(
            f"Read '{rover_id}:errors' with redis_get and diagnose any faults. "
            "If there are none, say so."
        ),
        expected_output="A short fault diagnosis (or 'no faults').",
        agent=error,
    )
    research_task = Task(
        description=(
            f"Write a concise scientist-facing summary for {rover_id}. Use the vision "
            "findings and the error diagnosis provided as context. If a fault could "
            "affect the detection (e.g. occlusion), note it as a caveat."
        ),
        expected_output="A scientist-facing research summary with any error caveats.",
        agent=research,
        context=[vision_task, error_task],
    )

    return Crew(
        agents=[vision, error, research],
        tasks=[vision_task, error_task, research_task],
        process=Process.sequential,
        verbose=True,
    )


def build_rover1_crew(llm: LLM | None = None) -> Crew:
    return build_rover_crew("rover1", llm)


def build_rover2_crew(llm: LLM | None = None) -> Crew:
    return build_rover_crew("rover2", llm)


# ── asyncio runner (the path that runs on each frame today) ───────────────────

# Guard against overlapping cycles for the same rover (a slow vision call must
# not pile up behind a burst of frames). Per-rover, in-process.
_inflight: set[str] = set()


async def _bridge_findings(rover_id: str, vision: dict) -> None:
    """Push each fresh detection into the findings list so the scientist UI sees it.

    This closes the long-standing gap where vision detected objects but they never
    reached `findings` (the list GET /findings serves). add_finding() also publishes
    `scientist:ping`, which the WebSocket bridge forwards to the browser.
    """
    from redis_layer import findings_state

    image_id = vision.get("image_id")
    photo = ""
    if image_id:
        raw = redis_get_raw(f"image:{image_id}")
        if isinstance(raw, str) and raw:
            photo = raw if raw.startswith("data:") else f"data:image/jpeg;base64,{raw}"

    criteria = vision.get("criteria", "")
    for f in vision.get("findings", []):
        desc = f.get("description", "")
        # Preview = first sentence (clean break), full text on card expand.
        summary = desc.split(". ")[0].strip()
        if summary and not summary.endswith("."):
            summary += "."
        await findings_state.add_finding(
            {
                "rover_id": rover_id,
                "label": f.get("label", "Unknown object"),
                "summary": summary,
                "description": desc,
                "confidence": f.get("confidence"),
                "photo": photo,
                "criteria": criteria,
            }
        )


@weave.op()
async def run_rover_cycle(rover_id: str) -> dict | None:
    """Run one full subagent cycle for a rover and bridge any new findings.

    vision -> error -> research (research reads vision+error for the cross-feed).
    The subagent functions are sync (they use the sync Redis client), so each runs
    in a worker thread to avoid blocking the event loop. Returns the aggregated
    result, or None if a cycle for this rover is already in flight.
    """
    if rover_id in _inflight:
        return None
    _inflight.add(rover_id)
    try:
        vision = await asyncio.to_thread(run_vision_subagent, rover_id)
        error = await asyncio.to_thread(run_error_subagent, rover_id)
        research = await asyncio.to_thread(run_research_subagent, rover_id)

        # Only bridge genuinely new detections — deduped frames reuse cached
        # findings and must not re-ping the UI every cycle.
        if vision.get("findings") and not vision.get("deduped"):
            await _bridge_findings(rover_id, vision)

        return {"rover_id": rover_id, "vision": vision, "error": error, "research": research}
    except Exception as exc:  # noqa: BLE001
        logger.warning("run_rover_cycle(%s) failed: %s", rover_id, exc)
        return None
    finally:
        _inflight.discard(rover_id)


async def run_fleet_cycle(rover_ids: tuple[str, ...] = ROVER_IDS) -> list:
    """Run cycles for every rover concurrently; await = all subagents done."""
    return await asyncio.gather(*(run_rover_cycle(r) for r in rover_ids))


# ── event-driven trigger ──────────────────────────────────────────────────────


async def _publish_stage(index: int) -> None:
    from redis_layer import client as redis_client
    await redis_client.publish("mission:progress", {"type": "stage", "index": index})


_first_cycle_done = False


async def _on_frame(rover_id: str) -> None:
    """Fires stage 5 on the very first frame, then runs the cycle."""
    global _first_cycle_done
    if not _first_cycle_done:
        _first_cycle_done = True
        await _publish_stage(5)
    await run_rover_cycle(rover_id)


async def agent_frame_listener() -> None:
    """Subscribe to `rover:frames` and fire a cycle for each new frame.

    Runs as a background task (started in main.py's lifespan). Reconnects with a
    short backoff if the subscription drops. Cycles are launched as detached tasks
    so consuming the next frame is never blocked by a slow vision call; the
    per-rover _inflight guard prevents overlap.
    """
    from redis_layer import client

    logger.info("agent_frame_listener started (event-driven on rover:frames)")
    while True:
        try:
            async for _channel, data in client.subscribe("rover:frames"):
                rover_id = data.get("rover_id") if isinstance(data, dict) else None
                if rover_id:
                    asyncio.create_task(_on_frame(rover_id))
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.warning("agent_frame_listener error: %s", exc)
        await asyncio.sleep(2)
