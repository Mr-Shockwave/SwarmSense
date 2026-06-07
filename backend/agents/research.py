"""Research agent — streamed contextual analysis of an approved object.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

Responsibilities:
  - Triggered when the scientist approves an object ping.
  - GPT-4o analyzes the photo in detail.
  - Web search for scientific context.
  - Streams the full analysis to the UI card in real time.
"""
from __future__ import annotations

from typing import AsyncIterator

# from crewai import Agent
# import weave


def build_research_agent():
    """Build the research CrewAI Agent.

    TODO [Person 1]:
      role="Field Research Scientist"
      goal="Produce a rich, sourced analysis of a detected object"
      backstory="A curious polymath with web-search superpowers..."
      tools=[gpt4o_vision_describe, web_search]
    """
    raise NotImplementedError("build_research_agent (Person 1)")


# @weave.op()
async def stream_analysis(object_description: str, photo_b64: str) -> AsyncIterator[str]:
    """Yield analysis text chunks as they are produced.

    TODO [Person 1]:
      - Call GPT-4o with the photo + description.
      - Run web search for scientific context.
      - Stream tokens/chunks back (async generator) so the UI card fills live.
      - Weave should trace the full research stream.
    """
    raise NotImplementedError("stream_analysis (Person 1)")
    yield  # pragma: no cover  (marks this as an async generator)
