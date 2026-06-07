"""Rover routes — status + captured frames per node.

Owner: Person 2 (Backend API + Redis + WebSocket)
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from config import ROVER_IDS
from redis_layer import rover_state

router = APIRouter()


@router.get("/status")
async def rovers_status():
    """Return per-rover position, zone, current task, last error.

    TODO [Person 2]: return rover_state.get_all_rover_status() once implemented.
    For now report each rover's captured-frame count so the UI can badge nodes.
    """
    out = {}
    for rid in ROVER_IDS:
        out[rid] = {"frames": await rover_state.count_images(rid)}
    return out


@router.get("/{rover_id}/images")
async def rover_images(rover_id: str, limit: int = 100):
    """Return a rover's captured frames (newest first) for its node section."""
    frames = await rover_state.get_images(rover_id, limit=limit)
    return {"rover_id": rover_id, "count": len(frames), "frames": frames}


class ImagePush(BaseModel):
    photo: str           # base64 / data-uri
    caption: str = ""
    coord: Optional[dict] = None


@router.post("/{rover_id}/images")
async def push_image(rover_id: str, body: ImagePush):
    """Append a captured frame (used by the capture pipeline / dev tooling)."""
    frame = await rover_state.add_image(
        rover_id, photo=body.photo, caption=body.caption, coord=body.coord
    )
    return {"ok": True, "frame": frame}
