"""Target routes — POST /targets/approve, GET /targets/list.

Owner: Person 2 (Backend API + Redis + WebSocket)
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

# from redis_layer import mission_state
# from agents.research import stream_analysis
# from coordination.task_assignment import reassign_to_nearest

router = APIRouter()


class ApprovalRequest(BaseModel):
    """Scientist's decision on a detected object."""
    target_id: str
    decision: str  # "collect" | "ignore" | "investigate"
    x: int
    y: int
    description: str | None = None


@router.post("/approve")
async def approve_target(req: ApprovalRequest):
    """Handle a COLLECT / IGNORE / INVESTIGATE decision.

    TODO [Person 2]:
      - "collect":    mission_state.add_approved_target(...) then
                      coordination.reassign_to_nearest(...) (Person 1).
      - "investigate": trigger agents.research.stream_analysis (stream to UI).
      - "ignore":     no-op / log.
      - Return the resulting state.
    """
    raise NotImplementedError("approve_target (Person 2)")


@router.get("/list")
async def list_targets():
    """Return approved targets + their assignments.

    TODO [Person 2]: mission_state.list_approved_targets() + get_assignments().
    """
    raise NotImplementedError("list_targets (Person 2)")
