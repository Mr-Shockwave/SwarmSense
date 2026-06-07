"""Mission routes — POST /mission/start, GET /mission/status.

Owner: Person 2 (Backend API + Redis + WebSocket)
"""
from __future__ import annotations

import logging

from fastapi import APIRouter
from pydantic import BaseModel

from config import ROVER_IDS
from redis_layer import mission_state
import dev_capture
import snapshot_capture

log = logging.getLogger("roverswarm.mission")
router = APIRouter()

WORKFLOW_STAGES = [
    "Received mission prompt",
    "Saved prompt to shared memory (Redis)",
    "Splitting map into agent zones",
] + [f"Dispatching mission to Agent N{i+1}" for i in range(len(ROVER_IDS))] + [
    "Agents exploring & capturing",
]


class MissionStartRequest(BaseModel):
    goal: str
    criteria: str = ""


async def _publish_stage(index: int) -> None:
    from redis_layer import client as redis_client
    await redis_client.publish("mission:progress", {"type": "stage", "index": index})


def _stop_capture() -> None:
    snapshot_capture.stop()
    dev_capture.stop()


@router.post("/start")
async def start_mission(req: MissionStartRequest):
    _stop_capture()

    await _publish_stage(0)
    record = await mission_state.set_mission(req.goal, req.criteria)
    await _publish_stage(1)
    await _publish_stage(2)

    rover_ids = list(ROVER_IDS)
    for i in range(len(rover_ids)):
        await _publish_stage(3 + i)

    # Real phone camera if a STREAM_URL is configured; else SVG placeholders.
    if snapshot_capture.any_stream_configured(rover_ids):
        snapshot_capture.start(rover_ids)
        capture_mode = "live"
    else:
        dev_capture.start(rover_ids)
        capture_mode = "simulation"
    log.info("Mission started in %s capture mode for %s", capture_mode, rover_ids)

    return {
        "status": "running",
        "mission": record,
        "rovers": rover_ids,
        "stages": WORKFLOW_STAGES,
        "capture_mode": capture_mode,
    }


@router.post("/stop")
async def stop_mission():
    _stop_capture()
    await mission_state.set_status("idle")
    return {"status": "idle"}


@router.get("/status")
async def mission_status():
    return await mission_state.get_mission()
