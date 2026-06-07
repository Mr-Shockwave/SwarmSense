"""Findings — the user-requested objects the agents actually detected.

Owner: Person 2 (Backend API + Redis), consumed by per-rover vision/research subagents.

Distinct from the periodic rover*:images captures. A "finding" is a confirmed
match against the scientist's criteria, with a photo + description + location.

Redis layout (the contract the frontend Findings screen polls):
    findings          LIST  (newest first) of finding JSON blobs
    findings:status   HASH  {finding_id: "new|collected|ignored"}

The per-robot agents create findings by calling add_finding() (or LPUSH'ing the
same shape directly into the `findings` list).
"""
from __future__ import annotations

import time
import uuid

from . import client

KEY = "findings"
STATUS_KEY = "findings:status"


def _normalize(raw: dict) -> dict:
    return {
        "id": raw.get("id") or f"find_{uuid.uuid4().hex[:8]}",
        "rover_id": raw.get("rover_id"),
        "label": raw.get("label") or "Unknown object",
        "summary": raw.get("summary", ""),
        "description": raw.get("description", ""),
        "photo": raw.get("photo", ""),            # data-uri or URL
        "coord": raw.get("coord") or {},
        "criteria": raw.get("criteria", ""),       # what the user asked for
        "confidence": raw.get("confidence"),
        "status": raw.get("status", "new"),
        "ts": raw.get("ts") or time.time(),
    }


async def add_finding(raw: dict) -> dict:
    """Append a finding and publish a ping for the scientist UI."""
    finding = _normalize(raw)
    await client.lpush(KEY, finding)
    # Real-time notify (WebSocket bridge can forward this later).
    await client.publish("scientist:ping", {"type": "finding", **finding})
    return finding


async def list_findings(limit: int = 200) -> list[dict]:
    """Return findings, newest first, with any status overrides applied."""
    items = await client.lrange(KEY, 0, limit - 1)
    overrides = await client.hgetall(STATUS_KEY)
    for f in items:
        if isinstance(f, dict) and f.get("id") in overrides:
            f["status"] = overrides[f["id"]]
    return items


async def set_status(finding_id: str, status: str) -> None:
    """Mark a finding collected/ignored/new (stored as an override hash)."""
    await client.hset(STATUS_KEY, finding_id, status)
