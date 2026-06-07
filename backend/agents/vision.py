"""Vision agent — photo analysis against scientist criteria.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

Responsibilities:
  - Receives a photo (every ~5-6s per rover) from the vision pipeline.
  - Calls GPT-4o vision and checks the photo against the scientist's criteria.
  - Returns match / no-match + object description.
  - Publishes a ping to CopilotKit (scientist:ping) on a match.
"""
from __future__ import annotations

# from crewai import Agent
# import weave

# from vision_pipeline.analyzer import analyze_photo   # Person 3 provides this
# from redis_layer.pubsub import publish, CHANNEL_SCIENTIST_PING


def build_vision_agent():
    """Build the vision CrewAI Agent.

    TODO [Person 1]:
      role="Vision Analyst"
      goal="Detect objects matching the scientist's criteria in rover photos"
      backstory="A sharp-eyed field biologist..."
      tools=[analyze_photo_tool, publish_ping_tool]
    """
    raise NotImplementedError("build_vision_agent (Person 1)")


# @weave.op()
def evaluate_photo(rover_id: str, photo_b64: str, criteria: str, coord: tuple[int, int]) -> dict:
    """Run the vision check for one photo.

    TODO [Person 1]:
      - Call vision_pipeline.analyzer.analyze_photo(photo_b64, criteria).
      - If match: build ping payload (photo thumb, coord, description) and
        publish to CHANNEL_SCIENTIST_PING.
      - Return {"match": bool, "description": str, "confidence": float}.
      - Weave should trace input photo + output match/description.
    """
    raise NotImplementedError("evaluate_photo (Person 1)")
