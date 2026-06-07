"""Orchestrator agent — mission planning and coordination.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

Responsibilities:
  - Reads mission goal from Redis.
  - Splits the map into rover zones (left/right to start).
  - Assigns zones to each rover.
  - Makes dynamic task reassignment (e.g. nearest rover collects an object).
  - Decides when the mission is complete.
"""
from __future__ import annotations

from crewai import Agent, LLM

from config import settings
from tools.redis_tools import redis_get, redis_publish, redis_set

# import weave


def _llm() -> LLM | None:
    if not settings.OPENAI_API_KEY:
        return None
    return LLM(model=settings.OPENAI_ORCHESTRATION_MODEL, api_key=settings.OPENAI_API_KEY)


def build_orchestrator_agent(llm: LLM | None = None) -> Agent:
    """Build the mission-level orchestrator CrewAI Agent."""
    return Agent(
        role="Mission Orchestrator",
        goal="Coordinate two rovers to fully explore the space and collect approved targets",
        backstory=(
            "Veteran exploration mission commander. Splits zones across rover1/rover2, "
            "monitors mission-wide progress, and reassigns tasks when finds occur."
        ),
        tools=[redis_get, redis_set, redis_publish],
        llm=llm or _llm(),
        verbose=True,
        allow_delegation=False,
    )


# @weave.op()
def split_zones(grid_width: int, grid_height: int, rover_ids: list[str]) -> dict:
    """Split the map into one zone per rover.

    TODO [Person 1]: return {rover_id: {x_min, x_max, y_min, y_max}}.
    Default strategy: vertical split (rover1 left half, rover2 right half).
    Write the assignments to Redis (rover_state.set_zone).
    """
    raise NotImplementedError("split_zones (Person 1)")


# @weave.op()
def assign_zones_to_rovers(zones: dict) -> None:
    """Persist zone assignments to Redis. TODO [Person 1]."""
    raise NotImplementedError("assign_zones_to_rovers (Person 1)")


# @weave.op()
def check_mission_complete() -> bool:
    """Return True when every cell is explored and all targets collected.

    TODO [Person 1]: read map_state + targets:assignments to decide.
    """
    raise NotImplementedError("check_mission_complete (Person 1)")
