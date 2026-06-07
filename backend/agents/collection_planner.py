"""Collection planner agent — mission-level target assignment.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

NOTE: Per-rover pickup execution lives in each rover's collection *subagent*
(agents/rover_subagents.py). This mission-level planner assigns targets across
rovers (targets:assignments) and plans fleet-wide routes — it does not drive
individual {rover_id}:collection subagents directly.

Responsibilities:
  - Maintains the approved-targets list (targets:approved in Redis).
  - Assigns each target to the nearest rover.
  - Plans the optimal retrieval route at the end of the mission.
"""
from __future__ import annotations

# from crewai import Agent
# import weave


def build_collection_planner_agent():
    """Build the collection planner CrewAI Agent.

    TODO [Person 1]:
      role="Collection Route Planner"
      goal="Retrieve every approved target with minimal total travel"
      backstory="A logistics optimizer..."
      tools=[read_approved_targets, assign_nearest_rover, plan_route]
    """
    raise NotImplementedError("build_collection_planner_agent (Person 1)")


# @weave.op()
def assign_targets_to_nearest_rover() -> dict:
    """Map each approved target to the closest rover.

    TODO [Person 1]:
      - Read targets:approved and current rover positions from Redis.
      - Compute nearest rover per target (consider red zones).
      - Write targets:assignments {target_id: rover_id}.
      - Return the assignment map.
    """
    raise NotImplementedError("assign_targets_to_nearest_rover (Person 1)")


# @weave.op()
def plan_route(rover_id: str, target_coords: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Order a rover's targets into an optimal route.

    TODO [Person 1]: nearest-neighbor / simple TSP over the grid, avoiding red zones.
    """
    raise NotImplementedError("plan_route (Person 1)")
