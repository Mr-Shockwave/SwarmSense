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

from crewai import Agent, LLM

from config import settings
from tools.redis_tools import redis_get, redis_publish, redis_set

# import weave


def _llm() -> LLM | None:
    if not settings.OPENAI_API_KEY:
        return None
    return LLM(model=settings.OPENAI_ORCHESTRATION_MODEL, api_key=settings.OPENAI_API_KEY)


def build_research_agent(llm: LLM | None = None) -> Agent:
    """Build the mission-level research CrewAI Agent."""
    return Agent(
        role="Field Research Scientist",
        goal="Produce a rich, sourced analysis of a detected object",
        backstory=(
            "A curious polymath triggered when the scientist approves an object ping. "
            "Streams contextual analysis to the UI."
        ),
        tools=[redis_get, redis_set, redis_publish],
        llm=llm or _llm(),
        verbose=True,
        allow_delegation=False,
    )


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
