"""Scenario: tests red zone propagation.

Owner: Person 3 (with Person 1 for redzone broadcast)

Rover 1 drives into the flower pot, broadcasts a red zone, and Rover 2 reroutes
before reaching it. Validates coordination/redzone.py + the UI red-zone overlay.

Run: python -m simulation.test_scenarios.obstacle_course
"""
from __future__ import annotations

import asyncio

from simulation.world import World, OBSTACLES


async def run() -> None:
    """Force Rover 1 into an obstacle and verify Rover 2 avoids it.

    TODO [Person 3 + Person 1]:
      - Route Rover 1 straight at OBSTACLES[0] (flower_pot).
      - On collision, ensure a red zone is broadcast (coordination.redzone).
      - Route Rover 2 toward the same area; assert it reroutes around the zone.
    """
    world = World()
    _ = OBSTACLES
    raise NotImplementedError("obstacle_course.run (Person 3 + Person 1)")


if __name__ == "__main__":
    asyncio.run(run())
