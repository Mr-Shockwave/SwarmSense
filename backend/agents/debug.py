"""Debug / self-healing agent — diagnoses rover faults and pushes fixes.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

Responsibilities:
  - Monitors rover error logs in Redis (rover1:errors, rover2:errors).
  - Diagnoses failures using Weave traces.
  - Generates and pushes a code/config fix back to the rover.
"""
from __future__ import annotations

from crewai import Agent, LLM

from config import settings
from tools.redis_tools import redis_get, redis_publish, redis_set

# import weave


def _llm() -> LLM | None:
    if not settings.OPENAI_API_KEY:
        return None
    return LLM(model=settings.OPENAI_ORCHESTRATION_MODEL, api_key=settings.OPENAI_API_KEY)


def build_debug_agent(llm: LLM | None = None) -> Agent:
    """Build the mission-level debug / self-healing CrewAI Agent."""
    return Agent(
        role="Self-Healing Engineer",
        goal="Detect, diagnose, and remediate rover faults autonomously",
        backstory=(
            "An SRE that reads rover error logs and Weave traces to propose fixes."
        ),
        tools=[redis_get, redis_set, redis_publish],
        llm=llm or _llm(),
        verbose=True,
        allow_delegation=False,
    )


# @weave.op()
def diagnose(rover_id: str) -> dict:
    """Diagnose the latest fault for a rover.

    TODO [Person 1]:
      - Read the rover's error log (rover_state.get_errors).
      - Correlate with recent Weave traces.
      - Return {"diagnosis": str, "proposed_fix": str, "confidence": float}.
      - Weave should trace each debug fix attempt.
    """
    raise NotImplementedError("diagnose (Person 1)")


# @weave.op()
def push_fix(rover_id: str, fix: dict) -> bool:
    """Apply / push a fix to the rover. TODO [Person 1] (coordinate with Person 3)."""
    raise NotImplementedError("push_fix (Person 1)")
