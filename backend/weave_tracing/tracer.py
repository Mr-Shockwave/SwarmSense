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

import logging

import weave

from config import settings

log = logging.getLogger("roverswarm.weave")

_initialized = False


def init_weave() -> None:
    """Initialize Weave once at startup.

    Calls weave.init(WEAVE_PROJECT) so every @weave.op() in the codebase (vision
    analysis, the per-rover cycle, the subagents) is traced — including per-call
    latency, which Weave records automatically for each op. Requires WANDB_API_KEY
    to be set; main.py wraps this in try/except so a missing key degrades to "no
    tracing" rather than crashing startup.
    """
    global _initialized
    if _initialized:
        return
    weave.init(settings.WEAVE_PROJECT)
    _initialized = True
    log.info("Weave tracing initialized (project=%s)", settings.WEAVE_PROJECT)


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
