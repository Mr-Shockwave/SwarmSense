"""Snapshot capture — pull fresh JPEGs from a phone camera or local webcam device.

Owner: Person 2 (Backend + capture).

Two modes (auto-detected from env):

1. HTTP snapshot (IP Webcam /shot.jpg):
   STREAM_URL=http://<phone-ip>:8080
   Per-rover: STREAM_URL_ROVER1=..., STREAM_URL_ROVER2=...
   A bare base URL, /video, /videofeed, or /shot.jpg suffix all work.

2. Local device (Continuity Camera / built-in webcam):
   CAMERA_DEVICE=1   (integer device index, e.g. 1 for iPhone via Continuity Camera)
   Per-rover: CAMERA_DEVICE_ROVER1=1, CAMERA_DEVICE_ROVER2=0
   Uses OpenCV VideoCapture — no network needed. Ideal when IP networking is blocked
   (campus WiFi isolation) but iPhone is paired via Continuity Camera over USB/BT.

CAMERA_DEVICE takes priority over STREAM_URL when both are set.

Each tick: grab frame -> base64 -> rover_state.add_image() -> publishes rover:frames
-> triggers agent pipeline.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import os

import httpx

from config import PHOTO_INTERVAL_SECONDS
from redis_layer import rover_state

log = logging.getLogger("roverswarm.snapshot")

_tasks: dict[str, asyncio.Task] = {}
SNAPSHOT_TIMEOUT = 5.0
JPEG_QUALITY = 80
CAPTURE_MAX_WIDTH = 1024


# ── device index helpers ──────────────────────────────────────────────────────

def _camera_device(rover_id: str | None = None) -> int | None:
    """Return the OpenCV device index for a rover, or None if not configured."""
    if rover_id:
        val = os.getenv(f"CAMERA_DEVICE_{rover_id.upper()}")
        if val is not None:
            return int(val)
    val = os.getenv("CAMERA_DEVICE")
    return int(val) if val is not None else None


def _grab_device_frame(device: int) -> str | None:
    """Blocking: grab one frame from a local camera device, return base64 JPEG."""
    import cv2
    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        return None
    try:
        ok, frame = cap.read()
        if not ok or frame is None:
            return None
        h, w = frame.shape[:2]
        if w > CAPTURE_MAX_WIDTH:
            scale = CAPTURE_MAX_WIDTH / w
            frame = cv2.resize(frame, (CAPTURE_MAX_WIDTH, int(h * scale)))
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        if not ok:
            return None
        return base64.b64encode(buf.tobytes()).decode("ascii")
    finally:
        cap.release()


async def grab_device_snapshot(rover_id: str | None = None) -> str | None:
    """Grab one frame from the configured local camera device (non-blocking)."""
    device = _camera_device(rover_id)
    if device is None:
        return None
    b64 = await asyncio.to_thread(_grab_device_frame, device)
    if b64 is None:
        log.warning("device capture failed for %s @ device %s", rover_id or "?", device)
    return b64


# ── HTTP snapshot helpers ─────────────────────────────────────────────────────

def stream_base(rover_id: str | None = None) -> str | None:
    """Return the configured stream URL for a rover (per-rover, then shared)."""
    if rover_id:
        per = os.getenv(f"STREAM_URL_{rover_id.upper()}")
        if per:
            return per
    return os.getenv("STREAM_URL")


def _shot_url(base: str) -> str:
    """Derive the /shot.jpg snapshot URL from any IP Webcam URL form."""
    base = base.rstrip("/")
    for suffix in ("/video", "/videofeed", "/shot.jpg"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return f"{base}/shot.jpg"


async def grab_snapshot(rover_id: str | None = None) -> str | None:
    """Fetch one fresh JPEG as base64 (no data-uri prefix), or None on failure."""
    base = stream_base(rover_id)
    if not base:
        return None
    url = _shot_url(base)
    try:
        async with httpx.AsyncClient(timeout=SNAPSHOT_TIMEOUT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return base64.b64encode(resp.content).decode("ascii")
    except Exception as exc:  # noqa: BLE001
        log.warning("snapshot failed for %s @ %s: %s", rover_id or "?", url, exc)
        return None


# ── unified capture loop ──────────────────────────────────────────────────────

async def _capture_loop(rover_id: str) -> None:
    device = _camera_device(rover_id)
    if device is not None:
        log.info("Snapshot capture started for %s via local device %s", rover_id, device)
    else:
        base = stream_base(rover_id)
        log.info("Snapshot capture started for %s @ %s", rover_id, _shot_url(base) if base else "(no URL)")

    while True:
        if device is not None:
            b64 = await grab_device_snapshot(rover_id)
        else:
            b64 = await grab_snapshot(rover_id)

        if b64:
            await rover_state.add_image(
                rover_id,
                photo=f"data:image/jpeg;base64,{b64}",
                caption="live snapshot",
            )
        await asyncio.sleep(PHOTO_INTERVAL_SECONDS)


def start(rover_ids: list[str]) -> None:
    """(Re)start the snapshot loop for each rover that has a stream or device configured."""
    stop()
    for rid in rover_ids:
        if _camera_device(rid) is not None or stream_base(rid):
            _tasks[rid] = asyncio.create_task(_capture_loop(rid))
        else:
            log.warning("No STREAM_URL or CAMERA_DEVICE for %s — skipping real capture", rid)


def stop() -> None:
    for task in _tasks.values():
        task.cancel()
    _tasks.clear()


def any_stream_configured(rover_ids: list[str]) -> bool:
    """True if at least one rover has a stream URL or device index set."""
    return any(_camera_device(rid) is not None or stream_base(rid) for rid in rover_ids)
