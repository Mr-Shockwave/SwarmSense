"""Dynamic task reassignment between rovers.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

If Rover 1 finds an interesting object but Rover 2 is physically closer, the
orchestrator reassigns the collection task mid-mission. Rover 2 reroutes; Rover 1
keeps mapping. The change is visible live in the UI.
"""
from __future__ import annotations

# from redis_layer.rover_state import get_position
# from redis_layer.mission_state import set_assignment
# import weave


# @weave.op()
def reassign_to_nearest(target_id: str, target_coord: tuple[int, int]) -> str:
    """Reassign a target to whichever rover is closest.

    TODO [Person 1]:
      - Read both rover positions from Redis.
      - Compute distances (respect red zones if feasible).
      - Write the new assignment (mission_state.set_assignment).
      - Return the chosen rover_id.
      - Weave should trace the reassignment decision.
    """
    raise NotImplementedError("reassign_to_nearest (Person 1)")


def distance(a: tuple[int, int], b: tuple[int, int]) -> float:
    """Euclidean grid distance helper. TODO [Person 1] (or Manhattan — decide)."""
    raise NotImplementedError("distance (Person 1)")
