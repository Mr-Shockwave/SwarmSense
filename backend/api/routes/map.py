"""Map routes — GET /map/state.

Owner: Person 2 (Backend API + Redis + WebSocket)
"""
from __future__ import annotations

from fastapi import APIRouter

# from redis_layer import map_state

router = APIRouter()


@router.get("/state")
async def map_state_endpoint():
    """Return the full map grid + red zones for the UI.

    TODO [Person 2]:
      - grid = map_state.get_full_grid()
      - redzones = map_state.get_redzones()
      - return {"grid": grid, "redzones": redzones, "width": ..., "height": ...}
    """
    raise NotImplementedError("map_state_endpoint (Person 2)")
