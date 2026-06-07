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

# from crewai import Agent
# import weave


def build_orchestrator_agent():
    """Build the orchestrator CrewAI Agent.

    TODO [Person 1]:
      role="Mission Orchestrator"
      goal="Coordinate two rovers to fully explore the space and collect approved targets"
      backstory="Veteran exploration mission commander..."
      tools=[read_mission_goal, split_zones, assign_zone, reassign_task, check_complete]
    """
    raise NotImplementedError("build_orchestrator_agent (Person 1)")


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
