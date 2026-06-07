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

import time

from . import client


async def set_mission(goal: str, criteria: str) -> dict:
    """Store mission goal + criteria and mark status running.

    The scientist's prompt lands in Redis here; the two per-robot agents read it
    from `mission:goal` / `mission:criteria` (and the published mission channel).
    """
    record = {"goal": goal, "criteria": criteria, "status": "running", "ts": time.time()}
    await client.set("mission:goal", goal)
    await client.set("mission:criteria", criteria)
    await client.set("mission:status", "running")
    await client.set("mission:record", record)
    # Notify the rover agents that a new mission prompt is available.
    await client.publish("rover:comms", {"type": "mission", **record})
    return record


async def get_mission() -> dict:
    """Return {goal, criteria, status}."""
    record = await client.get("mission:record")
    if record:
        return record
    return {
        "goal": await client.get("mission:goal"),
        "criteria": await client.get("mission:criteria"),
        "status": await client.get("mission:status") or "idle",
    }


async def set_status(status: str) -> None:
    """idle | running | complete."""
    await client.set("mission:status", status)


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
