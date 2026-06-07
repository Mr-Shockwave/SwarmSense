"""Simulated rover — virtual operations that update Redis position.

Owner: Person 3 (Hardware Rover + Gemma Edge)

Drives the virtual world in simulation/. All BaseRover methods are pure-Python
operations against simulation.world; position updates are written to Redis so the
rest of the system can't tell it apart from a real rover.
"""
from __future__ import annotations

from .base_rover import BaseRover

# from redis_layer import rover_state
# from simulation.world import World
# from simulation.rover_sim import RoverSim


class SimulatedRover(BaseRover):
    """Virtual rover backed by the 2D simulation world."""

    def __init__(self, rover_id: str, world=None) -> None:
        super().__init__(rover_id)
        # TODO [Person 3]: hold a reference to the shared simulation World +
        #   this rover's RoverSim body (position, heading).
        self.world = world

    async def move_forward(self, cm: float) -> None:
        """TODO [Person 3]: advance the virtual body, collision-check against
        world obstacles, then rover_state.set_position(...)."""
        raise NotImplementedError("SimulatedRover.move_forward (Person 3)")

    async def turn(self, degrees: float) -> None:
        """TODO [Person 3]: update heading, write to Redis."""
        raise NotImplementedError("SimulatedRover.turn (Person 3)")

    async def take_photo(self) -> str:
        """TODO [Person 3]: render/return a simulated photo (base64) of whatever
        object sits in front of the rover in the world."""
        raise NotImplementedError("SimulatedRover.take_photo (Person 3)")

    async def read_proximity(self) -> float:
        """TODO [Person 3]: return simulated distance to nearest obstacle ahead."""
        raise NotImplementedError("SimulatedRover.read_proximity (Person 3)")

    async def stop(self) -> None:
        """TODO [Person 3]: no-op / halt the virtual body."""
        raise NotImplementedError("SimulatedRover.stop (Person 3)")

    async def get_position(self) -> dict:
        """TODO [Person 3]: return {x, y, heading} from the virtual body."""
        raise NotImplementedError("SimulatedRover.get_position (Person 3)")
