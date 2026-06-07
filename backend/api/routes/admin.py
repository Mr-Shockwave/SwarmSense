"""Admin routes — dev/reset utilities."""
from __future__ import annotations

from fastapi import APIRouter

import dev_capture
from redis_layer.client import get_redis
from redis_layer import mission_state
import agents.rover_managers as rover_managers

router = APIRouter()


@router.post("/reset")
async def reset():
    """Flush Redis, stop capture, reset runtime state. Dev use only."""
    dev_capture.stop()

    try:
        await get_redis().flushdb()
    except Exception:  # noqa: BLE001
        pass

    # Reset the first-cycle flag so stage 5 fires again on the next mission.
    rover_managers._first_cycle_done = False

    return {"ok": True, "message": "Redis flushed, capture stopped, state reset."}
