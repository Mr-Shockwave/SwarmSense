"""CrewAI crew definition — mission orchestrator + per-rover manager crews.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

Hackathon-centralized model:
  - mission_crew: orchestrator only (fleet-wide zone split, mission readiness)
  - rover1_crew / rover2_crew: GPT-4o managers with vision / research / error subagents
"""
from __future__ import annotations

from crewai import Crew, Process, Task

from .orchestrator import build_orchestrator_agent
from .rover_managers import build_rover1_crew, build_rover2_crew


def build_mission_crew() -> Crew:
    """Fleet-level crew — orchestrator only."""
    orchestrator = build_orchestrator_agent()

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
        agents=[orchestrator],
        tasks=[kickoff_task],
        process=Process.sequential,
        verbose=True,
    )


def build_crew() -> dict:
    """Construct mission crew + both per-rover manager crews.

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
