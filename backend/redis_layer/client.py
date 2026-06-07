"""Redis connection + low-level helpers.

Owner: Person 2 (Backend API + Redis + WebSocket)

Single async Redis client shared across the backend. All other redis_layer
modules build on the helpers here.
"""
from __future__ import annotations

from typing import Any, Optional

# import redis.asyncio as aioredis

from config import settings

_redis = None  # module-level singleton


def get_redis():
    """Return (and lazily create) the shared async Redis client.

    TODO [Person 2]:
      - _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
      - return _redis
    """
    global _redis
    if _redis is None:
        # _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        raise NotImplementedError("get_redis: create aioredis client (Person 2)")
    return _redis


async def ping() -> bool:
    """Health-check the connection. TODO [Person 2]: await get_redis().ping()."""
    raise NotImplementedError("ping (Person 2)")


# --- Thin typed helpers (wrap for JSON + Weave-friendliness) ---

async def get(key: str) -> Optional[str]:
    """TODO [Person 2]: await get_redis().get(key)."""
    raise NotImplementedError("get (Person 2)")


async def set(key: str, value: Any) -> None:
    """TODO [Person 2]: await get_redis().set(key, value) (JSON-encode if needed)."""
    raise NotImplementedError("set (Person 2)")


async def lpush(key: str, value: Any) -> None:
    """TODO [Person 2]: await get_redis().lpush(key, value)."""
    raise NotImplementedError("lpush (Person 2)")


async def lrange(key: str, start: int = 0, end: int = -1) -> list:
    """TODO [Person 2]: await get_redis().lrange(key, start, end)."""
    raise NotImplementedError("lrange (Person 2)")


async def sadd(key: str, value: Any) -> None:
    """TODO [Person 2]: await get_redis().sadd(key, value)."""
    raise NotImplementedError("sadd (Person 2)")


async def smembers(key: str) -> set:
    """TODO [Person 2]: await get_redis().smembers(key)."""
    raise NotImplementedError("smembers (Person 2)")


async def publish(channel: str, message: Any) -> None:
    """TODO [Person 2]: await get_redis().publish(channel, message) (JSON-encode)."""
    raise NotImplementedError("publish (Person 2)")
