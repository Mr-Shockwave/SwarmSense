"""Redis connection + low-level helpers.

Owner: Person 2 (Backend API + Redis + WebSocket)

Single async Redis client shared across the backend. All other redis_layer
modules build on the helpers here. Every call degrades gracefully: if Redis is
unreachable the helpers return safe empties / no-ops and log a warning, so the
API and UI keep working during early development.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

import redis.asyncio as aioredis

from config import settings

logger = logging.getLogger("roverswarm.redis")

_redis: Optional[aioredis.Redis] = None
_warned = False


def get_redis() -> aioredis.Redis:
    """Return (and lazily create) the shared async Redis client."""
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def ping() -> bool:
    """Health-check the connection (never raises)."""
    try:
        return bool(await get_redis().ping())
    except Exception as exc:  # noqa: BLE001
        _warn_once(exc)
        return False


def _warn_once(exc: Exception) -> None:
    global _warned
    if not _warned:
        logger.warning("Redis unavailable (%s) — running in degraded mode", exc)
        _warned = True


def _encode(value: Any) -> str:
    return value if isinstance(value, str) else json.dumps(value)


def _decode(value: Optional[str]) -> Any:
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


# --- KV ---

async def get(key: str) -> Any:
    try:
        return _decode(await get_redis().get(key))
    except Exception as exc:  # noqa: BLE001
        _warn_once(exc)
        return None


async def set(key: str, value: Any) -> None:
    try:
        await get_redis().set(key, _encode(value))
    except Exception as exc:  # noqa: BLE001
        _warn_once(exc)


# --- Lists ---

async def lpush(key: str, value: Any) -> None:
    try:
        await get_redis().lpush(key, _encode(value))
    except Exception as exc:  # noqa: BLE001
        _warn_once(exc)


async def lrange(key: str, start: int = 0, end: int = -1) -> list:
    try:
        raw = await get_redis().lrange(key, start, end)
        return [_decode(v) for v in raw]
    except Exception as exc:  # noqa: BLE001
        _warn_once(exc)
        return []


async def llen(key: str) -> int:
    try:
        return int(await get_redis().llen(key))
    except Exception as exc:  # noqa: BLE001
        _warn_once(exc)
        return 0


# --- Sets ---

async def sadd(key: str, value: Any) -> None:
    try:
        await get_redis().sadd(key, _encode(value))
    except Exception as exc:  # noqa: BLE001
        _warn_once(exc)


async def smembers(key: str) -> list:
    try:
        raw = await get_redis().smembers(key)
        return [_decode(v) for v in raw]
    except Exception as exc:  # noqa: BLE001
        _warn_once(exc)
        return []


# --- Pub/Sub ---

async def publish(channel: str, message: Any) -> None:
    try:
        await get_redis().publish(channel, _encode(message))
    except Exception as exc:  # noqa: BLE001
        _warn_once(exc)


async def close() -> None:
    global _redis
    if _redis is not None:
        try:
            await _redis.aclose()
        except Exception:  # noqa: BLE001
            pass
        _redis = None
