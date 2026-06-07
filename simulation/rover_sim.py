"""Virtual rover movement engine.

Owner: Person 3 (Hardware Rover + Gemma Edge)

The physics/body for a simulated rover: tracks (x, y, heading) inside a World and
resolves movement against obstacles. SimulatedRover (backend) drives this and
mirrors position to Redis.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .world import World


@dataclass
class RoverSim:
    """A virtual rover body within the world."""

    rover_id: str
    world: World
    x: float
    y: float
    heading: float = 0.0  # degrees, 0 = +x axis

    def move_forward(self, cm: float) -> bool:
        """Advance along heading; return False if blocked by an obstacle/edge.

        TODO [Person 3]:
          - Compute target cell from heading + distance (scale cm->cells).
          - If world.is_obstacle(target) or out of bounds: stop, return False
            (caller broadcasts a red zone).
          - Else update self.x/self.y, return True.
        """
        raise NotImplementedError("RoverSim.move_forward (Person 3)")

    def turn(self, degrees: float) -> None:
        """TODO [Person 3]: self.heading = (self.heading + degrees) % 360."""
        raise NotImplementedError("RoverSim.turn (Person 3)")

    def proximity(self) -> float:
        """TODO [Person 3]: distance (cm) to the nearest obstacle along heading."""
        raise NotImplementedError("RoverSim.proximity (Person 3)")

    def position(self) -> dict:
        return {"x": round(self.x), "y": round(self.y), "heading": self.heading}
