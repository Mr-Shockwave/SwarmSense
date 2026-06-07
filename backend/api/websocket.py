"""WebSocket endpoint — live map + state updates to the frontend.

Owner: Person 2 (Backend API + Redis + WebSocket)

On every Redis state change (map:update, scientist:ping, redzone:update,
rover positions) this pushes a message to all connected UI clients.
"""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Tracks active WebSocket clients and broadcasts to them."""

    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        """TODO [Person 2]: accept + append to self.active."""
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict) -> None:
        """Send a message to every connected client.

        TODO [Person 2]: iterate self.active, send_json, drop dead sockets.
        Called by redis_layer.pubsub listeners on each state change.
        """
        raise NotImplementedError("ConnectionManager.broadcast (Person 2)")


manager = ConnectionManager()


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
