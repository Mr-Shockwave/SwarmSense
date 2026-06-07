"""Rover routes — GET /rovers/status.

Owner: Person 2 (Backend API + Redis + WebSocket)
"""
from __future__ import annotations

from fastapi import APIRouter

# from redis_layer import rover_state

router = APIRouter()


@router.get("/status")
async def rovers_status():
    """Return per-rover position, zone, current task, last error.

    TODO [Person 2]: return rover_state.get_all_rover_status().
    """
    raise NotImplementedError("rovers_status (Person 2)")
