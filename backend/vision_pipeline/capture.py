"""Photo capture — real or simulated.

Owner: Person 3 (Hardware Rover + Gemma Edge)

Thin adapter over the phone camera stream that the vision agent calls on a
cadence. Uses OpenCV to read the rover's phone camera MJPEG/RTSP stream, grabs
the freshest frame, downscales + JPEG-compresses it, and returns base64 for
GPT-4o vision.

The stream URL is read from a single env var (kept out of the repo):
    STREAM_URL=http://<phone-ip>:8080/video

capture.py stays decoupled from Redis/vision: it captures and invokes on_photo.
Whoever wires on_photo decides whether frames go to Redis ({rover_id}:images)
or straight to the vision entrypoint.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import os

import cv2

from config import PHOTO_INTERVAL_SECONDS

# from rovers.base_rover import BaseRover

log = logging.getLogger(__name__)

# Tuning (move to config if you want them mission-configurable).
CAPTURE_MAX_WIDTH = 1024   # downscale wide frames before upload
JPEG_QUALITY = 80          # 0-100; 80 is a good size/clarity tradeoff
BUFFER_FLUSH = 4           # grab() calls to drop stale buffered frames

# Persistent VideoCapture per stream URL — reopening per frame is slow and laggy.
_caps: dict[str, cv2.VideoCapture] = {}


STREAM_URL_ENV = "STREAM_URL"


def _stream_url(rover=None) -> str:
    url = os.getenv(STREAM_URL_ENV)
    if not url:
        raise RuntimeError(
            f"{STREAM_URL_ENV} is not set (expected the phone camera stream, "
            "e.g. http://<phone-ip>:8080/video)"
        )
    return url


def _get_capture(url: str) -> cv2.VideoCapture:
    cap = _caps.get(url)
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # minimize latency on supported backends
        _caps[url] = cap
    return cap


def _grab_frame_b64(url: str) -> str | None:
    """Blocking: read the freshest frame from the stream and return base64 JPEG."""
    cap = _get_capture(url)
    if not cap.isOpened():
        return None

    # Drop buffered frames so we analyze what the camera sees *now*, not seconds ago.
    for _ in range(BUFFER_FLUSH):
        cap.grab()
    ok, frame = cap.read()

    if not ok or frame is None:
        # Stream hiccup — drop the capture and try a clean reconnect once.
        cap.release()
        _caps.pop(url, None)
        cap = _get_capture(url)
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


async def capture_photo(rover) -> str:
    """Capture a single photo from the rover's phone camera, base64-encoded JPEG.

    cv2 is blocking, so the read runs in a worker thread to keep the event loop free.
    """
    url = _stream_url(rover)
    b64 = await asyncio.to_thread(_grab_frame_b64, url)
    if b64 is None:
        raise RuntimeError(f"capture failed for {getattr(rover, 'rover_id', '?')} @ {url}")
    return b64


async def capture_loop(rover, on_photo) -> None:
    """Capture every PHOTO_INTERVAL_SECONDS and invoke on_photo(rover_id, photo, coord).

    A single bad frame (stream blip) is logged and skipped — the loop survives.
    Cancel the task to stop; the rover's capture is released on exit.
    """
    url = _stream_url(rover)
    try:
        while True:
            try:
                photo = await capture_photo(rover)
                coord = await rover.get_position()
                await on_photo(rover.rover_id, photo, coord)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 — never let one frame kill the loop
                log.warning("capture_loop %s: %s", getattr(rover, "rover_id", "?"), exc)
            await asyncio.sleep(PHOTO_INTERVAL_SECONDS)
    finally:
        cap = _caps.pop(url, None)
        if cap is not None:
            cap.release()