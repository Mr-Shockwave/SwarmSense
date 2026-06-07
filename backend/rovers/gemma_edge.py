"""Gemma 2B edge logic — instant local decisions on each rover.

Owner: Person 3 (Hardware Rover + Gemma Edge)

Runs locally on the rover (no cloud round-trip). Handles:
  - Obstacle detection from the proximity sensor
  - Emergency stop trigger
  - Inter-rover communication handler
  - Anti-gaslight enforcement (trust hierarchy, evidence-based belief updates)
  - Red zone check before each move
  - Photo trigger on timer + significant movement threshold

The cloud crew (Person 1) only advises; per the trust hierarchy, Gemma makes the
final call (TRUST_CLOUD_AGENT is the lowest level).
"""
from __future__ import annotations

from config import PHOTO_INTERVAL_SECONDS, REDZONE_RADIUS_CM

# from .base_rover import BaseRover
# from coordination.anti_gaslight import resolve_belief, has_valid_evidence
# from coordination.redzone import is_in_redzone, broadcast_redzone


class GemmaEdge:
    """Local decision loop running alongside a rover."""

    def __init__(self, rover) -> None:
        self.rover = rover
        # TODO [Person 3]: load Gemma 2B (path/endpoint from settings.GEMMA_MODEL_PATH).

    async def detect_obstacle(self) -> bool:
        """Return True if an obstacle is too close (read_proximity threshold).

        TODO [Person 3]: compare rover.read_proximity() to a safety threshold;
        on hit, broadcast a red zone via coordination.redzone.broadcast_redzone.
        """
        raise NotImplementedError("GemmaEdge.detect_obstacle (Person 3)")

    async def emergency_stop(self) -> None:
        """Immediately stop the rover and log the fault.

        TODO [Person 3]: rover.stop(); rover_state.log_error(...).
        """
        raise NotImplementedError("GemmaEdge.emergency_stop (Person 3)")

    async def handle_comms(self, message: dict) -> dict:
        """Process an inter-rover message under the anti-gaslight rules.

        TODO [Person 3]:
          - If not has_valid_evidence(message): ignore (advisory only).
          - Else resolve_belief(local_reading, message) and act/respond.
          - Coordinate with coordination/anti_gaslight.py (Person 1).
        """
        raise NotImplementedError("GemmaEdge.handle_comms (Person 3)")

    async def check_redzone_before_move(self, target_x: int, target_y: int) -> bool:
        """Return True if the move is safe (not into a red zone).

        TODO [Person 3]: read red zones, call coordination.redzone.is_in_redzone.
        """
        raise NotImplementedError("GemmaEdge.check_redzone_before_move (Person 3)")

    async def maybe_take_photo(self, distance_since_last: float, seconds_since_last: float) -> bool:
        """Decide whether to capture a photo this tick.

        TODO [Person 3]: trigger if seconds_since_last >= PHOTO_INTERVAL_SECONDS
        OR distance_since_last exceeds a movement threshold.
        """
        raise NotImplementedError("GemmaEdge.maybe_take_photo (Person 3)")
