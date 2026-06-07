"""WebSocket endpoint — live map + state updates to the frontend.

Owner: Person 2 (Backend API + Redis + WebSocket)

On every Redis state change (map:update, scientist:ping, redzone:update,
rover positions) this pushes a message to all connected UI clients.
"""
from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("roverswarm.ws")

router = APIRouter()

# Redis pub/sub channels the bridge forwards to the UI. Each carries a JSON dict
# with a "type" field ("frame" | "finding") that the frontend switches on.
LIVE_CHANNELS = ("rover:frames", "scientist:ping")


class ConnectionManager:
    """Tracks active WebSocket clients and broadcasts to them."""

    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict) -> None:
        """Send a message to every connected client, dropping dead sockets."""
        dead: list[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:  # noqa: BLE001  (client gone / send failed)
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


async def redis_bridge() -> None:
    """Subscribe to live Redis channels and fan each message out to all WS clients.

    Runs as a background task started in main.py's lifespan. Reconnects with a
    short backoff if the Redis subscription drops, so it survives transient
    network blips without taking the API down.
    """
    from redis_layer import client

    while True:
        try:
            async for channel, data in client.subscribe(*LIVE_CHANNELS):
                if isinstance(data, dict):
                    await manager.broadcast(data)
                else:
                    await manager.broadcast({"channel": channel, "data": data})
        except asyncio.CancelledError:
            raise  # shutting down — let the task end
        except Exception as exc:  # noqa: BLE001
            logger.warning("redis_bridge error: %s", exc)
        # subscribe() returned (connection dropped) — wait, then retry.
        await asyncio.sleep(2)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Live update channel for the frontend.

    TODO [Person 2]:
      - On connect, send the current map snapshot (map_state.get_full_grid()).
      - Keep the socket open; pubsub listeners call manager.broadcast(...).
      - Handle WebSocketDisconnect cleanly.
    """
    await manager.connect(ws)
    try:
        while True:
            # TODO [Person 2]: optionally receive client messages (e.g. cell clicks).
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
