"""Red zone broadcast + avoidance.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

When a rover hits an obstacle it broadcasts a red zone over Redis Pub/Sub.
The other rover receives it and reroutes before reaching the area. No LLM call
needed — pure Redis. The UI renders the red zone in real time.

Flow:
  Rover 1 hits flower pot at (45, 32)
    -> redis.sadd("map:redzones", {x:45, y:32, radius, reported_by})
    -> redis.publish("redzone:update", {x:45, y:32})
    -> Rover 2 (subscribed) reroutes
    -> CopilotKit UI renders the red zone
"""
from __future__ import annotations

from config import REDZONE_RADIUS_CM

# from redis_layer.map_state import add_redzone
# from redis_layer.pubsub import publish, CHANNEL_REDZONE_UPDATE
# import weave


# @weave.op()
async def broadcast_redzone(x: int, y: int, reported_by: str, radius: int = REDZONE_RADIUS_CM) -> None:
    """Record + broadcast a new red zone.

    TODO [Person 1]:
      - map_state.add_redzone(x, y, radius, reported_by)
      - publish(CHANNEL_REDZONE_UPDATE, {x, y, radius, reported_by})
      - Weave should trace every red zone broadcast.
    """
    raise NotImplementedError("broadcast_redzone (Person 1)")


def is_in_redzone(x: int, y: int, redzones: set) -> bool:
    """Return True if (x, y) falls within any known red zone radius.

    TODO [Person 1]: account for radius (cm -> grid cells).
    """
    raise NotImplementedError("is_in_redzone (Person 1)")
