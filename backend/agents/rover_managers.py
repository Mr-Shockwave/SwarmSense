"""Per-rover manager agents — one GPT-4o CrewAI manager per physical rover.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

Each manager supervises vision / research / error subagents via delegation
tools (CrewAI 1.x does not allow tools on hierarchical manager agents).
"""
from __future__ import annotations

import time
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool

from config import settings
from tools.redis_tools import redis_get, redis_publish, redis_set, redis_set_raw, redis_publish_raw

from .rover_subagents import (
    format_subagent_result,
    run_error_subagent,
    run_research_subagent,
    run_subagent_crew,
    run_vision_subagent,
    subagent_label,
)

MANAGER_REDIS_TOOLS = [redis_get, redis_set, redis_publish]


def _llm() -> LLM | None:
    if not settings.OPENAI_API_KEY:
        return None
    return LLM(model=settings.OPENAI_ORCHESTRATION_MODEL, api_key=settings.OPENAI_API_KEY)


def _delegation_tools(rover_id: str, llm: LLM | None) -> list:
    """Build per-rover tools that delegate to vision / research / error."""

    @tool(f"delegate_{rover_id}_vision")
    def delegate_vision(instruction: str) -> str:
        """Delegate vision work to the rover vision subagent (analyze criteria / photos)."""
        return run_subagent_crew(
            rover_id,
            "vision",
            instruction or f"Analyze mission:criteria for {rover_id} and report any matches.",
            llm,
        )

    @tool(f"delegate_{rover_id}_research")
    def delegate_research(instruction: str) -> str:
        """Delegate research work to summarize {rover_id}'s vision findings."""
        return run_subagent_crew(
            rover_id,
            "research",
            instruction or f"Summarize {rover_id}:vision:findings against mission:criteria.",
            llm,
        )

    @tool(f"delegate_{rover_id}_error")
    def delegate_error(instruction: str) -> str:
        """Delegate error analysis for faults logged on {rover_id}."""
        return run_subagent_crew(
            rover_id,
            "error",
            instruction or f"Diagnose any faults in {rover_id}:errors and recommend fixes.",
            llm,
        )

    return [delegate_vision, delegate_research, delegate_error]


def build_rover_manager_agent(rover_id: str, llm: LLM | None = None) -> Agent:
    """Build the GPT-4o manager Agent for a rover."""
    shared_llm = llm or _llm()
    tools = MANAGER_REDIS_TOOLS + _delegation_tools(rover_id, shared_llm)
    return Agent(
        role=f"{rover_id} Manager",
        goal=(
            f"Supervise {rover_id} exploration: read mission state from Redis, "
            "update rover status, and delegate to vision/research/error subagents."
        ),
        backstory=(
            f"You command {rover_id} in the RoverSwarm fleet. "
            "Mission goals live in mission:goal / mission:criteria. "
            f"Publish heartbeat on {rover_id}:status. "
            "Use delegate_* tools for specialist work — never analyze photos yourself."
        ),
        tools=tools,
        llm=shared_llm,
        verbose=True,
        allow_delegation=False,
    )


def build_rover1_manager_agent(llm: LLM | None = None) -> Agent:
    return build_rover_manager_agent("rover1", llm)


def build_rover2_manager_agent(llm: LLM | None = None) -> Agent:
    return build_rover_manager_agent("rover2", llm)


def _manager_task_description(rover_id: str) -> str:
    return f"""
You are the manager for {rover_id}. Complete these steps in order:

1. redis_get mission:goal, mission:criteria, {rover_id}:zone, and {rover_id}:position.
2. redis_set {rover_id}:status to a JSON object with state=active, phase=exploring, rover_id={rover_id}.
3. redis_publish the same JSON on channel {rover_id}:status.
4. Call delegate_{rover_id}_vision to analyze mission criteria for {rover_id}.
5. Call delegate_{rover_id}_research to summarize vision findings for {rover_id}.
6. Call delegate_{rover_id}_error to check and diagnose any faults in {rover_id}:errors.
7. Return a concise summary naming each subagent and what it reported.
""".strip()


def build_rover_crew(rover_id: str, llm: LLM | None = None) -> Crew:
    """Single-manager crew with Redis tools + subagent delegation tools."""
    manager = build_rover_manager_agent(rover_id, llm)
    task = Task(
        description=_manager_task_description(rover_id),
        expected_output=(
            f"Summary of {rover_id} mission read, status publish, and subagent delegation results."
        ),
        agent=manager,
    )
    return Crew(
        agents=[manager],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )


def build_rover1_crew(llm: LLM | None = None) -> Crew:
    return build_rover_crew("rover1", llm)


def build_rover2_crew(llm: LLM | None = None) -> Crew:
    return build_rover_crew("rover2", llm)


def run_manager_dry(rover_id: str) -> dict[str, Any]:
    """Execute manager workflow without LLM (Redis + subagent stubs)."""
    from tools.redis_tools import redis_get_raw

    goal = redis_get_raw("mission:goal")
    criteria = redis_get_raw("mission:criteria")
    zone = redis_get_raw(f"{rover_id}:zone")
    position = redis_get_raw(f"{rover_id}:position")

    status = {
        "rover_id": rover_id,
        "state": "active",
        "phase": "exploring",
        "ts": time.time(),
        "goal": goal,
    }
    redis_set_raw(f"{rover_id}:status", status)
    redis_publish_raw(f"{rover_id}:status", status)

    vision_out = run_vision_subagent(rover_id)
    research_out = run_research_subagent(rover_id)
    error_out = run_error_subagent(rover_id)

    return {
        "manager": f"{rover_id} Manager",
        "mission": {"goal": goal, "criteria": criteria},
        "rover": {"zone": zone, "position_before": position, "status": status},
        "delegations": {
            subagent_label(rover_id, "vision"): vision_out,
            subagent_label(rover_id, "research"): research_out,
            subagent_label(rover_id, "error"): error_out,
        },
    }


def print_dry_run_report(rover_id: str, report: dict[str, Any]) -> None:
    print(f"\n=== {report['manager']} (dry-run) ===")
    print(f"  mission:goal     -> {report['mission']['goal']!r}")
    print(f"  mission:criteria -> {report['mission']['criteria']!r}")
    print(f"  {rover_id}:zone   -> {report['rover']['zone']}")
    print(f"  {rover_id}:status -> published {report['rover']['status']}")
    for name, payload in report["delegations"].items():
        print(f"  delegated -> {name}")
        print(f"    {format_subagent_result(payload)}")
