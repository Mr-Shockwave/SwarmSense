"""Findings routes — the scientist-relevant detections shown on the Findings screen.

Owner: Person 2 (Backend API + Redis + WebSocket)
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from redis_layer import findings_state

router = APIRouter()


@router.get("")
async def list_findings(limit: int = 200):
    """All findings, newest first. The frontend polls this and diffs by id."""
    items = await findings_state.list_findings(limit=limit)
    return {"count": len(items), "findings": items}


class FindingIn(BaseModel):
    rover_id: Optional[str] = None
    label: str = "Unknown object"
    summary: str = ""
    description: str = ""
    photo: str = ""              # data-uri or URL
    coord: Optional[dict] = None
    criteria: str = ""
    confidence: Optional[float] = None


@router.post("")
async def create_finding(body: FindingIn):
    """Create a finding (used by the agents / dev tooling)."""
    finding = await findings_state.add_finding(body.model_dump())
    return {"ok": True, "finding": finding}


class StatusIn(BaseModel):
    status: str  # new | collected | ignored


@router.post("/{finding_id}/status")
async def update_status(finding_id: str, body: StatusIn):
    await findings_state.set_status(finding_id, body.status)
    return {"ok": True, "id": finding_id, "status": body.status}
