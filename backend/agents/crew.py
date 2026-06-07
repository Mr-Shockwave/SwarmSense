"""CrewAI crew definition — mission cloud crew + per-rover manager crews.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

Mission-level agents (orchestrator, research, debug) handle fleet-wide work.
Per-rover manager crews (rover_managers.py) use GPT-4o managers with Redis tools
and delegation tools that invoke vision / navigation / collection subagents.
"""
from __future__ import annotations

from crewai import Crew, Process, Task

from .debug import build_debug_agent
from .orchestrator import build_orchestrator_agent
from .research import build_research_agent
from .rover_managers import build_rover1_crew, build_rover2_crew

# Mission-level vision / collection_planner remain stubs — see their module docstrings
# for how they differ from per-rover subagents in rover_subagents.py.


def build_mission_crew() -> Crew:
    """Minimal mission-level crew for smoke testing (orchestrator-led)."""
    orchestrator = build_orchestrator_agent()
    research = build_research_agent()
    debug = build_debug_agent()

    kickoff_task = Task(
        description=(
            "Read mission:goal and mission:status from Redis. "
            "Confirm rover1:zone and rover2:zone are assigned. "
            "Summarize mission readiness for the fleet."
        ),
        expected_output="Mission readiness summary with zone assignments.",
        agent=orchestrator,
    )

    return Crew(
        agents=[orchestrator, research, debug],
        tasks=[kickoff_task],
        process=Process.sequential,
        verbose=True,
    )


def build_crew() -> dict:
    """Construct mission crew + both per-rover hierarchical crews.

    Returns:
        dict with keys mission_crew, rover1_crew, rover2_crew for smoke testing
        and API wiring.
    """
    return {
        "mission_crew": build_mission_crew(),
        "rover1_crew": build_rover1_crew(),
        "rover2_crew": build_rover2_crew(),
    }


_crew = None


def get_crew():
    global _crew
    if _crew is None:
        _crew = build_crew()
    return _crew
