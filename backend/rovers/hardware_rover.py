"""Hardware rover — real Lego motor/sensor commands.

Owner: Person 3 (Hardware Rover + Gemma Edge)

Same interface as SimulatedRover, but each method drives the physical Lego
Mindstorms / SPIKE hardware and reads real sensors. Position is dead-reckoned
(or from an external tracker) and written to Redis just like the sim.
"""
from __future__ import annotations

from .base_rover import BaseRover

# TODO [Person 3]: import the Lego SDK (pybricks / SPIKE API / hub comms).
# from redis_layer import rover_state


class HardwareRover(BaseRover):
    """Physical Lego rover."""

    def __init__(self, rover_id: str) -> None:
        super().__init__(rover_id)
        # TODO [Person 3]: connect to the hub, init motor ports + sensors + camera.

    async def move_forward(self, cm: float) -> None:
        """TODO [Person 3]: run drive motors for the distance, update odometry +
        rover_state.set_position(...)."""
        raise NotImplementedError("HardwareRover.move_forward (Person 3)")

    async def turn(self, degrees: float) -> None:
        """TODO [Person 3]: differential turn, update heading in Redis."""
        raise NotImplementedError("HardwareRover.turn (Person 3)")

    async def take_photo(self) -> str:
        """TODO [Person 3]: capture from the rover camera, return base64."""
        raise NotImplementedError("HardwareRover.take_photo (Person 3)")

    async def read_proximity(self) -> float:
        """TODO [Person 3]: read the ultrasonic/IR distance sensor (cm)."""
        raise NotImplementedError("HardwareRover.read_proximity (Person 3)")

    async def stop(self) -> None:
        """TODO [Person 3]: brake all motors immediately."""
        raise NotImplementedError("HardwareRover.stop (Person 3)")

    async def get_position(self) -> dict:
        """TODO [Person 3]: return {x, y, heading} from odometry/tracker."""
        raise NotImplementedError("HardwareRover.get_position (Person 3)")
