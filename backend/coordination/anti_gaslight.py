"""Anti-gaslighting / rover integrity — trust hierarchy + evidence rules.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

Trust levels (hardcoded, non-negotiable — see config.py):
  Level 1  Local sensor data         HIGHEST TRUST
  Level 2  Redis shared map          HIGH   (requires sensor evidence to update)
  Level 3  Inter-rover communication MEDIUM (advisory only)
  Level 4  Cloud agent suggestions   LOWER  (Gemma makes the final call)

Local sensor data cannot be overridden by another rover's verbal claim alone.
Valid influence requires evidence (proximity reading, photo, timestamp).
No evidence = ignored. Disagreements are logged to Weave.
"""
from __future__ import annotations

from config import (
    TRUST_LOCAL_SENSOR,
    TRUST_SHARED_MAP,
    TRUST_INTER_ROVER,
    TRUST_CLOUD_AGENT,
)

# from weave_tracing.tracer import log_disagreement


def has_valid_evidence(message: dict) -> bool:
    """Return True if an inter-rover claim carries acceptable evidence.

    TODO [Person 1]:
      - Require message["evidence"] with at least a proximity_reading or photo,
        plus a fresh timestamp.
      - Return False otherwise (claim is ignored).
    """
    raise NotImplementedError("has_valid_evidence (Person 1)")


def resolve_belief(local_reading: dict, claim: dict) -> dict:
    """Decide whether to update a rover's belief given a conflicting claim.

    TODO [Person 1]:
      - Local sensor (TRUST_LOCAL_SENSOR) always wins unless the claim provides
        stronger evidence at the same or higher trust level.
      - If conflict + no valid evidence: hold position, log disagreement to Weave,
        respond with local sensor reading as evidence.
      - Return {"belief": ..., "updated": bool, "reason": str}.
    """
    raise NotImplementedError("resolve_belief (Person 1)")


def trust_level(source: str) -> int:
    """Map a source string to its trust level constant.

    TODO [Person 1]: "local_sensor"->1, "shared_map"->2, "inter_rover"->3,
    "cloud_agent"->4.
    """
    mapping = {
        "local_sensor": TRUST_LOCAL_SENSOR,
        "shared_map": TRUST_SHARED_MAP,
        "inter_rover": TRUST_INTER_ROVER,
        "cloud_agent": TRUST_CLOUD_AGENT,
    }
    return mapping.get(source, TRUST_CLOUD_AGENT)
