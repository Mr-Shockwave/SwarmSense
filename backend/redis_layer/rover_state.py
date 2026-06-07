"""Rover positions, zones, assignments, error logs.

Owner: Person 2 (Backend API + Redis + WebSocket)

Keys:
  rover1:position / rover2:position  -> {x, y, heading}
  rover1:zone / rover2:zone          -> {x_min, x_max, y_min, y_max}
  rover1:errors / rover2:errors      -> list (lpush on each fault)
"""
from __future__ import annotations

import time

from . import client
# from .pubsub import publish, CHANNEL_ROVER1_POSITION, CHANNEL_ROVER2_POSITION


# ─────────────────────────────────────────────────────────────
# Captured frames — photos a rover takes every ~5-6s. The UI polls these per
# node (N1, N2, ...) and renders them one-by-one in the expandable sections.
#   Key: {rover_id}:images  (list, newest first)
# ─────────────────────────────────────────────────────────────

def _images_key(rover_id: str) -> str:
    return f"{rover_id}:images"


async def add_image(rover_id: str, photo: str, caption: str = "", coord: dict | None = None) -> dict:
    """Append a captured frame for a rover (newest first)."""
    frame = {
        "ts": time.time(),
        "photo": photo,        # base64 data-uri or raw base64
        "caption": caption,
        "coord": coord or {},
    }
    await client.lpush(_images_key(rover_id), frame)
    return frame


async def get_images(rover_id: str, limit: int = 100) -> list[dict]:
    """Return a rover's captured frames, newest first."""
    return await client.lrange(_images_key(rover_id), 0, limit - 1)


async def count_images(rover_id: str) -> int:
    return await client.llen(_images_key(rover_id))


async def set_position(rover_id: str, x: int, y: int, heading: float) -> None:
    """Persist a rover position and publish on its position channel.

    TODO [Person 2]:
      - client.set(f"{rover_id}:position", json{x, y, heading})
      - publish CHANNEL_ROVER{1,2}_POSITION with the new position.
    """
    raise NotImplementedError("set_position (Person 2)")


async def get_position(rover_id: str) -> dict:
    """TODO [Person 2]: return {x, y, heading} or a default."""
    raise NotImplementedError("get_position (Person 2)")


async def set_zone(rover_id: str, zone: dict) -> None:
    """TODO [Person 2]: client.set(f"{rover_id}:zone", json(zone))."""
    raise NotImplementedError("set_zone (Person 2)")


async def get_zone(rover_id: str) -> dict:
    """TODO [Person 2]: return {x_min, x_max, y_min, y_max}."""
    raise NotImplementedError("get_zone (Person 2)")


async def log_error(rover_id: str, error: dict) -> None:
    """Append a fault to the rover's error log (consumed by the per-rover error subagent).

    TODO [Person 2]: client.lpush(f"{rover_id}:errors", json(error)).
    """
    raise NotImplementedError("log_error (Person 2)")


async def get_errors(rover_id: str, limit: int = 20) -> list[dict]:
    """TODO [Person 2]: client.lrange(f"{rover_id}:errors", 0, limit-1)."""
    raise NotImplementedError("get_errors (Person 2)")


async def get_all_rover_status() -> dict:
    """Aggregate position + zone + last error for every rover (GET /rovers/status).

    TODO [Person 2].
    """
    raise NotImplementedError("get_all_rover_status (Person 2)")
