"""Sync CrewAI tools for Redis KV + Pub/Sub.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

Key/channel conventions match backend/redis_layer/:
  mission:goal, mission:criteria, mission:status
  {rover_id}:position, {rover_id}:zone, {rover_id}:status (pub channel)
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

import redis
from crewai.tools import tool

from config import settings

logger = logging.getLogger("roverswarm.redis_tools")

_warned = False


class _MemoryRedis:
    """In-process fallback when Redis is unreachable."""

    def __init__(self) -> None:
        self._kv: dict[str, str] = {}
        self._pub_log: list[tuple[str, str]] = []

    def ping(self) -> bool:
        return True

    def get(self, key: str) -> Optional[str]:
        return self._kv.get(key)

    def set(self, key: str, value: str) -> None:
        self._kv[key] = value

    def publish(self, channel: str, message: str) -> int:
        self._pub_log.append((channel, message))
        return 1


_client: redis.Redis | _MemoryRedis | None = None
_using_mock = False


def _warn_once(exc: Exception) -> None:
    global _warned
    if not _warned:
        logger.warning("Redis unavailable (%s) — using in-memory mock", exc)
        _warned = True


def get_sync_redis() -> redis.Redis | _MemoryRedis:
    """Return a sync Redis client (or in-memory mock)."""
    global _client, _using_mock
    if _client is not None:
        return _client
    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        client.ping()
        _client = client
        _using_mock = False
    except Exception as exc:  # noqa: BLE001
        _warn_once(exc)
        _client = _MemoryRedis()
        _using_mock = True
    return _client


def reset_redis_client() -> None:
    """Reset the cached client (for tests)."""
    global _client, _using_mock, _warned
    _client = None
    _using_mock = False
    _warned = False


def is_using_mock_redis() -> bool:
    get_sync_redis()
    return _using_mock


def _encode(value: Any) -> str:
    return value if isinstance(value, str) else json.dumps(value)


def _decode(value: Optional[str]) -> Any:
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def redis_get_raw(key: str) -> Any:
    """Read a Redis key (non-tool helper)."""
    try:
        raw = get_sync_redis().get(key)
        return _decode(raw)
    except Exception as exc:  # noqa: BLE001
        _warn_once(exc)
        return None


def redis_set_raw(key: str, value: Any) -> str:
    """Write a Redis key (non-tool helper)."""
    get_sync_redis().set(key, _encode(value))
    return f"OK set {key}"


def redis_publish_raw(channel: str, message: Any) -> str:
    """Publish on a Redis channel (non-tool helper)."""
    payload = _encode(message)
    get_sync_redis().publish(channel, payload)
    return f"OK published to {channel}"


def redis_get_image(image_id: str) -> str | None:
    """Read content-addressed frame bytes at image:{image_id}; return base64 or None."""
    if not image_id:
        return None
    try:
        raw = get_sync_redis().get(f"image:{image_id}")
    except Exception as exc:  # noqa: BLE001
        _warn_once(exc)
        return None
    if raw is None:
        return None
    return raw if isinstance(raw, str) else raw.decode("utf-8", "ignore")


def redis_get_vision_last(rover_id: str) -> dict[str, Any] | None:
    """Read {rover_id}:vision:last; return dict or None."""
    value = redis_get_raw(f"{rover_id}:vision:last")
    return value if isinstance(value, dict) else None


@tool("redis_get")
def redis_get(key: str) -> str:
    """Read a value from Redis by key (mission:goal, rover1:zone, etc.)."""
    value = redis_get_raw(key)
    if value is None:
        return f"(nil) key={key}"
    if isinstance(value, str):
        return value
    return json.dumps(value)


@tool("redis_set")
def redis_set(key: str, value: str) -> str:
    """Write a string or JSON value to Redis."""
    parsed: Any = value
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        pass
    return redis_set_raw(key, parsed)


@tool("redis_publish")
def redis_publish(channel: str, message: str) -> str:
    """Publish a message on a Redis Pub/Sub channel."""
    parsed: Any = message
    try:
        parsed = json.loads(message)
    except (json.JSONDecodeError, TypeError):
        pass
    return redis_publish_raw(channel, parsed)


@tool("get_vision_match")
def get_vision_match(rover_id: str) -> str:
    """Return the latest vision verdict for a rover ({rover_id}:vision:last)."""
    result = redis_get_vision_last(rover_id)
    if result is None:
        return json.dumps({"status": "missing"})
    return json.dumps(result)


@tool("get_cached_image")
def get_cached_image(image_id: str) -> str:
    """Check whether a content-addressed frame exists at image:{image_id} (metadata only)."""
    photo_b64 = redis_get_image(image_id)
    byte_length = 0
    if photo_b64:
        try:
            import base64

            byte_length = len(base64.b64decode(photo_b64))
        except Exception:  # noqa: BLE001
            byte_length = len(photo_b64)
    return json.dumps(
        {
            "image_id": image_id,
            "has_image": photo_b64 is not None,
            "byte_length": byte_length,
        }
    )


@tool("save_research_result")
def save_research_result(rover_id: str, result_json: str) -> str:
    """Parse JSON and write {rover_id}:research:last, then publish on {rover_id}:research."""
    try:
        parsed = json.loads(result_json)
    except (json.JSONDecodeError, TypeError) as exc:
        return f"ERROR invalid JSON: {exc}"
    if not isinstance(parsed, dict):
        return "ERROR result_json must be a JSON object"
    redis_set_raw(f"{rover_id}:research:last", parsed)
    redis_publish_raw(f"{rover_id}:research", parsed)
    return f"OK saved research for {rover_id}"
