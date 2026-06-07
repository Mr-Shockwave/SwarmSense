"""Photo capture — real or simulated.

Owner: Person 3 (Hardware Rover + Gemma Edge)

Thin adapter over the phone camera stream that the per-rover vision subagent
calls on a cadence. Uses OpenCV to read the rover's phone camera MJPEG/RTSP
stream, grabs the freshest frame, downscales + JPEG-compresses it, and returns
base64 for GPT-4o vision.

Strategy: try the live MJPEG stream (CAP_FFMPEG backend) first; if that fails
or returns a bad frame, fall back to a single-shot JPEG fetch from IP Webcam's
/shot.jpg endpoint. This keeps latency low when the stream is healthy and stays
robust when it isn't.

The stream URL is read from env (kept out of the repo). Per-rover first, then a
shared fallback:
    STREAM_URL_ROVER1=http://<phone-ip>:8080/video   # rover-specific
    STREAM_URL_ROVER2=http://<phone-ip>:8080/video
    STREAM_URL=http://<phone-ip>:8080/video          # fallback (single camera)

capture.py stays decoupled from Redis/vision: it captures and invokes on_photo.
Whoever wires on_photo decides whether frames go to Redis ({rover_id}:images)
or straight to the vision entrypoint.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import os
import urllib.request

import cv2

from config import PHOTO_INTERVAL_SECONDS

log = logging.getLogger(__name__)

# Tuning (move to config if you want them mission-configurable).
CAPTURE_MAX_WIDTH = 1024   # downscale wide frames before upload
JPEG_QUALITY = 80          # 0-100; 80 is a good size/clarity tradeoff
BUFFER_FLUSH = 4           # grab() calls to drop stale buffered frames
STILL_TIMEOUT = 3          # seconds for /shot.jpg HTTP request

# Persistent VideoCapture per stream URL — reopening per frame is slow and laggy.
_caps: dict[str, cv2.VideoCapture] = {}

STREAM_URL_ENV = "STREAM_URL"


def _stream_url(rover=None) -> str:
    """Resolve the base stream URL for this rover from env vars.

    Prefer STREAM_URL_ROVER1 / STREAM_URL_ROVER2 so each phone maps to its own
    rover. Fall back to the shared STREAM_URL.
    """
    rover_id = getattr(rover, "rover_id", None)
    if rover_id:
        per_rover = os.getenv(f"{STREAM_URL_ENV}_{rover_id.upper()}")
        if per_rover:
            return per_rover

    url = os.getenv(STREAM_URL_ENV)
    if not url:
        raise RuntimeError(
            f"No stream URL set for {rover_id or 'rover'}: expected "
            f"{STREAM_URL_ENV}_{(rover_id or 'ROVERN').upper()} or {STREAM_URL_ENV} "
            "(e.g. http://<phone-ip>:8080/video)"
        )
    return url


def _still_url(stream_url: str) -> str:
    """Derive IP Webcam's single-shot JPEG endpoint from the stream URL.

    http://192.0.0.4:8080/video  ->  http://192.0.0.4:8080/shot.jpg
    Any trailing path is replaced; query params are dropped.
    """
    # Strip path and params, keep scheme + host:port.
    from urllib.parse import urlparse, urlunparse
    parts = urlparse(stream_url)
    base = urlunparse((parts.scheme, parts.netloc, "/shot.jpg", "", "", ""))
    return base


# ---------------------------------------------------------------------------
# Stream capture (MJPEG via OpenCV + FFMPEG backend)
# ---------------------------------------------------------------------------

def _get_capture(url: str) -> cv2.VideoCapture:
    cap = _caps.get(url)
    if cap is None or not cap.isOpened():
        # CAP_FFMPEG handles IP Webcam's MJPEG multipart stream reliably.
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        _caps[url] = cap
    return cap


def _grab_frame_b64_stream(url: str) -> str | None:
    """Try to grab the freshest frame from the MJPEG stream.

    Returns base64 JPEG string, or None if the stream is unavailable/broken.
    """
    cap = _get_capture(url)
    if not cap.isOpened():
        log.debug("stream not opened: %s", url)
        return None

    # Drop buffered frames so we analyze what the camera sees *now*.
    for _ in range(BUFFER_FLUSH):
        cap.grab()
    ok, frame = cap.read()

    if not ok or frame is None:
        # Stream hiccup — release and attempt one reconnect.
        log.debug("stream read failed, reconnecting: %s", url)
        cap.release()
        _caps.pop(url, None)
        cap = _get_capture(url)
        ok, frame = cap.read()
        if not ok or frame is None:
            return None

    return _encode_frame(frame)


# ---------------------------------------------------------------------------
# Still-JPEG fallback (IP Webcam /shot.jpg)
# ---------------------------------------------------------------------------

def _grab_frame_b64_still(still_url: str) -> str | None:
    """Fetch a single JPEG from IP Webcam's /shot.jpg endpoint.

    Returns base64 JPEG string, or None on any HTTP/IO error.
    """
    try:
        with urllib.request.urlopen(still_url, timeout=STILL_TIMEOUT) as resp:
            data = resp.read()
        if not data:
            return None
        # Optionally downscale: decode → resize → re-encode.
        arr = __import__("numpy").frombuffer(data, dtype="uint8")
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            # Couldn't decode — return raw bytes as-is (already a JPEG).
            return base64.b64encode(data).decode("ascii")
        return _encode_frame(frame)
    except Exception as exc:
        log.warning("still fetch failed (%s): %s", still_url, exc)
        return None


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _encode_frame(frame) -> str | None:
    """Downscale if needed and return base64 JPEG."""
    h, w = frame.shape[:2]
    if w > CAPTURE_MAX_WIDTH:
        scale = CAPTURE_MAX_WIDTH / w
        frame = cv2.resize(frame, (CAPTURE_MAX_WIDTH, int(h * scale)))

    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    if not ok:
        return None
    return base64.b64encode(buf.tobytes()).decode("ascii")


def _grab_frame_b64(stream_url: str) -> str | None:
    """Stream-first capture with automatic fallback to /shot.jpg.

    1. Try the live MJPEG stream (low latency when healthy).
    2. On failure, fall back to IP Webcam's still endpoint (always works).
    """
    b64 = _grab_frame_b64_stream(stream_url)
    if b64 is not None:
        return b64

    log.info("stream unavailable, falling back to still JPEG")
    still = _still_url(stream_url)
    return _grab_frame_b64_still(still)


# ---------------------------------------------------------------------------
# Public async API (unchanged interface)
# ---------------------------------------------------------------------------

async def capture_photo(rover) -> str:
    """Capture a single photo from the rover's phone camera, base64-encoded JPEG.

    cv2 is blocking, so the read runs in a worker thread to keep the event loop free.
    """
    url = _stream_url(rover)
    b64 = await asyncio.to_thread(_grab_frame_b64, url)
    if b64 is None:
        raise RuntimeError(
            f"capture failed for {getattr(rover, 'rover_id', '?')} @ {url} "
            f"(stream and still-JPEG both failed)"
        )
    return b64


async def capture_loop(rover, on_photo) -> None:
    """Capture every PHOTO_INTERVAL_SECONDS and invoke on_photo(rover_id, photo, coord).

    A single bad frame (stream blip) is logged and skipped — the loop survives.
    Cancel the task to stop; the rover's VideoCapture is released on exit.
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