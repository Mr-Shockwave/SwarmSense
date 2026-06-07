"""Admin routes — dev/reset utilities."""
from __future__ import annotations

from fastapi import APIRouter

import dev_capture
import snapshot_capture
from config import ROVER_IDS
from redis_layer.client import get_redis
import agents.rover_managers as rover_managers

router = APIRouter()


@router.post("/reset")
async def reset():
    """Flush Redis, stop capture, reset runtime state. Dev use only."""
    dev_capture.stop()
    snapshot_capture.stop()

    try:
        await get_redis().flushdb()
    except Exception:  # noqa: BLE001
        pass

    # Reset the first-cycle flag so stage 5 fires again on the next mission.
    rover_managers._first_cycle_done = False

    return {"ok": True, "message": "Redis flushed, capture stopped, state reset."}


@router.get("/capture/test")
async def capture_test(rover_id: str = "rover1"):
    """Grab one snapshot from the phone stream to verify connectivity.

    Returns whether a frame was fetched + its byte size, without pushing to Redis.
    """
    base = snapshot_capture.stream_base(rover_id)
    if not base:
        return {
            "ok": False,
            "error": f"No STREAM_URL set for {rover_id}. Set STREAM_URL or STREAM_URL_{rover_id.upper()} in .env.",
        }
    shot_url = snapshot_capture._shot_url(base)
    b64 = await snapshot_capture.grab_snapshot(rover_id)
    if not b64:
        return {"ok": False, "url": shot_url, "error": "Could not fetch a frame (phone unreachable / wrong URL?)."}
    return {"ok": True, "url": shot_url, "bytes": len(b64), "rover_id": rover_id}
