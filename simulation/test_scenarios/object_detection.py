"""Scenario: tests ping + research flow.

Owner: Person 3 (with Person 1 for vision/research agents)

A rover approaches an object of interest, the vision agent matches it against the
scientist criteria, a ping is published, and (on approval) the research agent
streams analysis. Validates the full detection -> ping -> approve -> analyze loop.

Run: python -m simulation.test_scenarios.object_detection
"""
from __future__ import annotations

import asyncio

from simulation.world import World, OBJECTS


async def run() -> None:
    """Drive a rover to an object and exercise the detection pipeline.

    TODO [Person 3 + Person 1]:
      - Set mission criteria (e.g. "anything blue or circular").
      - Route a rover to OBJECTS[0] (blue cylinder); take_photo there.
      - Run agents.vision.evaluate_photo -> expect match + scientist:ping.
      - Simulate scientist approval -> agents.research.stream_analysis.
    """
    world = World()
    _ = OBJECTS
    raise NotImplementedError("object_detection.run (Person 3 + Person 1)")


if __name__ == "__main__":
    asyncio.run(run())
