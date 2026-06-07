"""Weave initialization + custom scorers.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

Weave should trace:
  - Every CrewAI agent call
  - Every vision API call (input photo + output match/description)
  - Every inter-rover disagreement (anti-gaslight events)
  - Every red zone broadcast
  - Every research subagent stream
  - Every error subagent fix attempt
"""
from __future__ import annotations

# import weave

from config import settings

_initialized = False


def init_weave() -> None:
    """Initialize Weave once at startup.

    TODO [Person 1]:
      - weave.init(settings.WEAVE_PROJECT)
      - Register custom scorers (see below).
    """
    global _initialized
    if _initialized:
        return
    # weave.init(settings.WEAVE_PROJECT)
    _initialized = True
    raise NotImplementedError("init_weave: call weave.init() (Person 1)")


# ─────────────────────────────────────────────────────────────
# Custom scorers — quantify agent output quality in the Weave dashboard.
# ─────────────────────────────────────────────────────────────

# @weave.op()
def score_vision_match(output: dict) -> dict:
    """Score a vision subagent result.

    TODO [Person 1]: return {"confidence": float, "has_description": bool}.
    """
    raise NotImplementedError("score_vision_match (Person 1)")


# @weave.op()
def score_research_quality(output: str) -> dict:
    """Score a research stream (length, citations, on-topic).

    TODO [Person 1].
    """
    raise NotImplementedError("score_research_quality (Person 1)")


# @weave.op()
def log_disagreement(event: dict) -> None:
    """Log an inter-rover anti-gaslight disagreement to Weave.

    TODO [Person 1]: structured event {from, to, claim, evidence, resolution}.
    Called by coordination/anti_gaslight.py.
    """
    raise NotImplementedError("log_disagreement (Person 1)")
