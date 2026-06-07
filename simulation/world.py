"""Simulated physical world — obstacles, objects of interest, rover spawns.

Owner: Person 3 (with Person 2/Person 1 consuming it)

Pre-defined test world:
  - 20x20 grid (matches config.GRID_WIDTH/GRID_HEIGHT)
  - 3 obstacles at fixed positions (flower pot, wall corner, chair leg)
  - 4 objects of interest (blue cylinder, red sphere, circular disc, green box)
  - 2 rover starting positions
"""
from __future__ import annotations

from dataclasses import dataclass, field

from config import GRID_WIDTH, GRID_HEIGHT

# --- Fixed obstacles (red-zone sources) ---
OBSTACLES: list[dict] = [
    {"name": "flower_pot", "x": 5, "y": 14},
    {"name": "wall_corner", "x": 12, "y": 3},
    {"name": "chair_leg", "x": 16, "y": 11},
]

# --- Objects of interest (vision targets) ---
OBJECTS: list[dict] = [
    {"id": "obj_blue_cylinder", "label": "blue cylinder", "x": 8, "y": 17},
    {"id": "obj_red_sphere", "label": "red sphere", "x": 3, "y": 6},
    {"id": "obj_circular_disc", "label": "circular disc", "x": 15, "y": 15},
    {"id": "obj_green_box", "label": "green box", "x": 18, "y": 5},
]

# --- Rover spawns ---
ROVER_SPAWNS: dict[str, dict] = {
    "rover1": {"x": 1, "y": 1, "heading": 0.0},
    "rover2": {"x": 18, "y": 1, "heading": 0.0},
}


@dataclass
class World:
    """Holds the static world + dynamic state for the simulation."""

    width: int = GRID_WIDTH
    height: int = GRID_HEIGHT
    obstacles: list[dict] = field(default_factory=lambda: list(OBSTACLES))
    objects: list[dict] = field(default_factory=lambda: list(OBJECTS))

    def is_obstacle(self, x: int, y: int) -> bool:
        """TODO [Person 3]: return True if (x, y) is on/near an obstacle."""
        raise NotImplementedError("World.is_obstacle (Person 3)")

    def object_at(self, x: int, y: int):
        """TODO [Person 3]: return the object in front of/at (x, y), or None.
        Used by SimulatedRover.take_photo to synthesize a photo."""
        raise NotImplementedError("World.object_at (Person 3)")

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
