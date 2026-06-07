"""Mission routes — POST /mission/start, GET /mission/status.

Owner: Person 2 (Backend API + Redis + WebSocket)
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

# from redis_layer import mission_state
# from agents.crew import get_crew

router = APIRouter()


class MissionStartRequest(BaseModel):
    """Scientist's mission input."""
    goal: str
    criteria: str  # e.g. "ping me if you see anything blue or circular"


@router.post("/start")
async def start_mission(req: MissionStartRequest):
    """Begin a mission.

    TODO [Person 2]:
      - mission_state.set_mission(req.goal, req.criteria)
      - Kick off the orchestrator (split zones, assign, begin exploration).
      - Coordinate with Person 1's get_crew() to launch the agent loop.
      - Return {"status": "running"}.
    """
    raise NotImplementedError("start_mission (Person 2)")


@router.post("/stop")
async def stop_mission():
    """Stop the current mission. TODO [Person 2]: set status idle, halt rovers."""
    raise NotImplementedError("stop_mission (Person 2)")


@router.get("/status")
async def mission_status():
    """Return mission goal/criteria/status.

    TODO [Person 2]: return mission_state.get_mission().
    """
    raise NotImplementedError("mission_status (Person 2)")
