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
