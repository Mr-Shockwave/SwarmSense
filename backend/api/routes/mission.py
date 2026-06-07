"""Mission routes — POST /mission/start, GET /mission/status.

Owner: Person 2 (Backend API + Redis + WebSocket)
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from config import settings, ROVER_IDS
from redis_layer import mission_state
import dev_capture

router = APIRouter()


# Workflow stages surfaced to the UI checklist above the chat box.
# TODO [Person 1/Person 2]: drive these from real crew progress events.
WORKFLOW_STAGES = [
    "Received mission prompt",
    "Saved prompt to shared memory (Redis)",
    "Splitting map into agent zones",
    "Dispatching mission to Agent N1",
    "Dispatching mission to Agent N2",
    "Agents exploring & capturing",
]


class MissionStartRequest(BaseModel):
    """Scientist's mission input."""
    goal: str
    criteria: str = ""  # e.g. "ping me if you see anything blue or circular"


async def _publish_stage(index: int) -> None:
    from redis_layer import client as redis_client
    await redis_client.publish("mission:progress", {"type": "stage", "index": index})


@router.post("/start")
async def start_mission(req: MissionStartRequest):
    """Begin a mission.

    Stores the prompt in Redis (where the two per-robot agents read it) and, in
    simulation mode, kicks off the synthetic capture loop so frames stream to the
    UI nodes.

    TODO [Person 1]: launch the CrewAI orchestrator here (get_crew()) so real
    agents pick up mission:goal / mission:criteria and begin exploring.
    """
    # Stage 0: prompt received
    await _publish_stage(0)

    record = await mission_state.set_mission(req.goal, req.criteria)

    # Stage 1: saved to Redis
    await _publish_stage(1)

    # Stage 2: zone splitting (placeholder — real split not yet implemented)
    await _publish_stage(2)

    rover_ids = list(ROVER_IDS)

    # Stage 3 + 4: dispatching to each rover
    for i, _ in enumerate(rover_ids):
        await _publish_stage(3 + i)

    if settings.SIMULATION_MODE:
        dev_capture.start(rover_ids)

    return {
        "status": "running",
        "mission": record,
        "rovers": rover_ids,
        "stages": WORKFLOW_STAGES,
    }


@router.post("/stop")
async def stop_mission():
    """Stop the current mission."""
    dev_capture.stop()
    await mission_state.set_status("idle")
    return {"status": "idle"}


@router.get("/status")
async def mission_status():
    """Return mission goal/criteria/status."""
    return await mission_state.get_mission()
