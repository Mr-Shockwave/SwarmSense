"""Dev-only capture simulator.

When SIMULATION_MODE is on and no real rovers are producing photos yet, this
pushes synthetic frames into Redis every ~PHOTO_INTERVAL_SECONDS per rover so the
UI's node sections visibly fill one-by-one — exactly like the real pipeline will.

Frames are tiny inline SVG data-URIs, so they render in <img> with zero assets.
Replace this with the real vision_pipeline.capture loop (Person 3) once rovers
produce actual photos.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import random
import time

from config import PHOTO_INTERVAL_SECONDS, GRID_WIDTH, GRID_HEIGHT
from redis_layer import rover_state

logger = logging.getLogger("roverswarm.dev_capture")

_tasks: dict[str, asyncio.Task] = {}

_PALETTE = ["#2980b9", "#27ae60", "#c0392b", "#8e44ad", "#d35400", "#16a085"]


def _placeholder_frame(rover_id: str, n: int, coord: dict) -> str:
    """Build an inline SVG data-URI standing in for a captured photo."""
    bg = random.choice(_PALETTE)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200">'
        f'<rect width="320" height="200" fill="#0d1117"/>'
        f'<rect x="8" y="8" width="304" height="184" rx="10" fill="{bg}" opacity="0.18"/>'
        f'<circle cx="{40 + (n * 37) % 240}" cy="{60 + (n * 53) % 90}" r="26" fill="{bg}"/>'
        f'<text x="16" y="36" fill="#e6edf3" font-family="monospace" font-size="16">'
        f'{rover_id.upper()} · frame {n:03d}</text>'
        f'<text x="16" y="180" fill="#8b949e" font-family="monospace" font-size="13">'
        f'({coord.get("x")}, {coord.get("y")})</text>'
        f'</svg>'
    )
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


async def _capture_loop(rover_id: str) -> None:
    n = 0
    while True:
        n += 1
        coord = {"x": random.randint(0, GRID_WIDTH - 1), "y": random.randint(0, GRID_HEIGHT - 1)}
        photo = _placeholder_frame(rover_id, n, coord)
        await rover_state.add_image(
            rover_id,
            photo=photo,
            caption=f"Auto-capture #{n} @ {time.strftime('%H:%M:%S')}",
            coord=coord,
        )
        await asyncio.sleep(PHOTO_INTERVAL_SECONDS)


def start(rover_ids: list[str]) -> None:
    """(Re)start the synthetic capture loop for each rover."""
    stop()
    for rid in rover_ids:
        _tasks[rid] = asyncio.create_task(_capture_loop(rid))
    logger.info("Dev capture started for %s (every %ss)", rover_ids, PHOTO_INTERVAL_SECONDS)


def stop() -> None:
    for task in _tasks.values():
        task.cancel()
    _tasks.clear()
