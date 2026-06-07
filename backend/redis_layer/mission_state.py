"""Mission goals, criteria, approved targets, collection assignments.

Owner: Person 2 (Backend API + Redis + WebSocket)

Keys:
  mission:goal            -> scientist's input string
  mission:criteria        -> object detection rules
  mission:status          -> idle | running | complete
  targets:approved        -> list of {target_id, x, y, description, photo}
  targets:assignments     -> {target_id: rover_id}
"""
from __future__ import annotations

# from . import client


async def set_mission(goal: str, criteria: str) -> None:
    """Store mission goal + criteria and mark status running.

    TODO [Person 2].
    """
    raise NotImplementedError("set_mission (Person 2)")


async def get_mission() -> dict:
    """TODO [Person 2]: return {goal, criteria, status}."""
    raise NotImplementedError("get_mission (Person 2)")


async def set_status(status: str) -> None:
    """TODO [Person 2]: idle | running | complete."""
    raise NotImplementedError("set_status (Person 2)")


async def add_approved_target(target: dict) -> None:
    """Append a scientist-approved target.

    TODO [Person 2]: client.lpush("targets:approved", json(target)).
    """
    raise NotImplementedError("add_approved_target (Person 2)")


async def list_approved_targets() -> list[dict]:
    """TODO [Person 2]: return parsed targets:approved."""
    raise NotImplementedError("list_approved_targets (Person 2)")


async def set_assignment(target_id: str, rover_id: str) -> None:
    """TODO [Person 2]: hset targets:assignments target_id -> rover_id."""
    raise NotImplementedError("set_assignment (Person 2)")


async def get_assignments() -> dict:
    """TODO [Person 2]: return {target_id: rover_id}."""
    raise NotImplementedError("get_assignments (Person 2)")
