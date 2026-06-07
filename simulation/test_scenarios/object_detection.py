"""Scenario: tests ping + research flow.

Owner: Person 3 (with Person 1 for per-rover vision/research subagents)

A rover approaches an object of interest, the vision subagent matches it against
the scientist criteria, a ping is published, and (on approval) the research
subagent summarizes findings. Validates the full detection -> ping -> approve -> analyze loop.

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
      - Run agents.rover_subagents.run_vision_subagent(rover_id) -> expect match;
        wire findings_state.add_finding / scientist:ping when findings exist.
      - Simulate scientist approval -> agents.rover_subagents.run_research_subagent(rover_id).
    """
    world = World()
    _ = OBJECTS
    raise NotImplementedError("object_detection.run (Person 3 + Person 1)")


if __name__ == "__main__":
    asyncio.run(run())
