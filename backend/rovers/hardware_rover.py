"""Hardware rover — real Lego motor/sensor commands.

Owner: Person 3 (Hardware Rover + Gemma Edge)

Same interface as SimulatedRover, but motion is driven by the physical Lego hub.
This class does NOT talk to BLE directly — it enqueues line-protocol commands on
the Redis list ``{rover_id}:commands``; the BLE sidecar (ble_sidecar.py) pops them
FIFO and writes them to the hub over Nordic UART. Sensor/position reads come back
the other way as telemetry the sidecar lands in Redis.

Command line-protocol (must match the hub firmware):
    FWD:<cm>      drive forward <cm> centimetres
    TURN:<deg>    turn in place <deg> degrees (positive = clockwise)
    STOP          halt all motion
"""
from __future__ import annotations

import logging

from .base_rover import BaseRover
from redis_layer import client, rover_state

log = logging.getLogger("roverswarm.hardware_rover")

# A "far / clear path" sentinel when no proximity telemetry is available yet.
# Finite (not inf) so it stays JSON-serialisable downstream.
_NO_OBSTACLE_CM = 999.0


def _commands_key(rover_id: str) -> str:
    return f"{rover_id}:commands"


class HardwareRover(BaseRover):
    """Physical Lego rover, commanded over Redis -> BLE sidecar -> hub."""

    def __init__(self, rover_id: str) -> None:
        super().__init__(rover_id)

    async def _send(self, command: str) -> None:
        """Enqueue one line-protocol command for the BLE sidecar to deliver.

        lpush + the sidecar's brpop give FIFO ordering. Degrades gracefully: if
        Redis is down, client.lpush logs and no-ops rather than raising.
        """
        log.info("[%s] enqueue command: %s", self.rover_id, command)
        await client.lpush(_commands_key(self.rover_id), command)

    async def move_forward(self, cm: float) -> None:
        await self._send(f"FWD:{cm:g}")

    async def turn(self, degrees: float) -> None:
        await self._send(f"TURN:{degrees:g}")

    async def stop(self) -> None:
        await self._send("STOP")

    async def take_photo(self) -> str:
        """Return the latest captured frame (base64) for this rover.

        Frames are produced by the phone-camera pipeline (vision_pipeline.capture)
        and stored newest-first in ``{rover_id}:images``. Returns "" if none yet.
        """
        images = await rover_state.get_images(self.rover_id, limit=1)
        if images:
            return images[0].get("photo", "") or ""
        return ""

    async def read_proximity(self) -> float:
        """Distance (cm) to the nearest obstacle ahead, from telemetry cache.

        The sidecar/firmware can publish readings to ``{rover_id}:proximity``.
        Until then we report a clear path so navigation logic doesn't stall.
        """
        value = await client.get(f"{self.rover_id}:proximity")
        try:
            return float(value)
        except (TypeError, ValueError):
            return _NO_OBSTACLE_CM

    async def get_position(self) -> dict:
        """Return {x, y, heading} from Redis (telemetry/odometry), or origin."""
        pos = await client.get(f"{self.rover_id}:position")
        if isinstance(pos, dict):
            return pos
        return {"x": 0, "y": 0, "heading": 0.0}
