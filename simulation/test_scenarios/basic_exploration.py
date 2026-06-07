"""Scenario: simple room exploration.

Owner: Person 3 (with Person 1/Person 2 for the agent/Redis wiring)

Two virtual rovers split the room and explore. Validates the end-to-end
simulation loop (movement -> Redis position -> map updates -> UI).

Run: python -m simulation.test_scenarios.basic_exploration
"""
from __future__ import annotations

import asyncio

from simulation.world import World, ROVER_SPAWNS

# from rovers import make_rover


async def run() -> None:
    """Drive both rovers through a basic exploration sweep.

    TODO [Person 3]:
      - Build a shared World.
      - Instantiate two SimulatedRovers (via rovers.make_rover) seeded at ROVER_SPAWNS.
      - Loop: move/turn each rover to cover its zone, marking explored cells.
      - Stop when the map is fully explored.
    """
    world = World()
    _ = ROVER_SPAWNS  # spawns to seed the rovers
    raise NotImplementedError("basic_exploration.run (Person 3)")


if __name__ == "__main__":
    asyncio.run(run())
