"""Pub/Sub channel definitions + async listeners.

Owner: Person 2 (Backend API + Redis + WebSocket)

Channels are the real-time nervous system: rover-to-rover comms, red zone
broadcasts, position sharing, and scientist pings.
"""
from __future__ import annotations

import asyncio
from typing import Awaitable, Callable

# from . import client

# ─────────────────────────────────────────────────────────────
# Channel constants
# ─────────────────────────────────────────────────────────────
CHANNEL_ROVER1_POSITION = "rover1:position"
CHANNEL_ROVER2_POSITION = "rover2:position"
CHANNEL_REDZONE_UPDATE = "redzone:update"
CHANNEL_ROVER_COMMS = "rover:comms"
CHANNEL_SCIENTIST_PING = "scientist:ping"
CHANNEL_MAP_UPDATE = "map:update"

ALL_CHANNELS = [
    CHANNEL_ROVER1_POSITION,
    CHANNEL_ROVER2_POSITION,
    CHANNEL_REDZONE_UPDATE,
    CHANNEL_ROVER_COMMS,
    CHANNEL_SCIENTIST_PING,
    CHANNEL_MAP_UPDATE,
]


async def publish(channel: str, message) -> None:
    """Publish a JSON message on a channel.

    TODO [Person 2]: delegate to client.publish (JSON-encode message).
    """
    raise NotImplementedError("publish (Person 2)")


async def subscribe(channel: str, handler: Callable[[dict], Awaitable[None]]) -> asyncio.Task:
    """Subscribe to a channel and run handler on each message.

    TODO [Person 2]:
      - Create a pubsub from the Redis client, subscribe(channel).
      - Spawn an asyncio task that loops messages and awaits handler(parsed).
      - Return the task so the caller can cancel it on shutdown.
    """
    raise NotImplementedError("subscribe (Person 2)")


async def start_listeners(on_map_update=None, on_scientist_ping=None, on_redzone=None) -> list[asyncio.Task]:
    """Start all background listeners at app startup.

    TODO [Person 2]:
      - Subscribe to CHANNEL_MAP_UPDATE / CHANNEL_SCIENTIST_PING / CHANNEL_REDZONE_UPDATE
        and forward to the WebSocket broadcaster (api/websocket.py).
      - Return the list of tasks for clean shutdown.
    """
    raise NotImplementedError("start_listeners (Person 2)")
