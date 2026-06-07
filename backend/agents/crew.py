"""CrewAI crew definition — wires together all five agents.

Owner: Person 1 (Agent Logic + CrewAI + Weave)

The crew is the cloud "brain". Each agent has a role, goal, backstory, and tools.
Every agent call is traced by Weave (see weave_tracing/tracer.py).
"""
from __future__ import annotations

# from crewai import Agent, Crew, Process, Task

from .orchestrator import build_orchestrator_agent
from .vision import build_vision_agent
from .research import build_research_agent
from .collection_planner import build_collection_planner_agent
from .debug import build_debug_agent


def build_crew():
    """Construct and return the full CrewAI crew.

    TODO [Person 1]:
      - Instantiate all five agents via their build_* factories.
      - Define the Tasks each agent performs and their wiring (sequential vs
        hierarchical Process).
      - Attach shared tools (Redis read/write, vision API, web search).
      - Wrap with Weave tracing so every agent step is logged.

    Returns:
        crewai.Crew configured for the mission loop.
    """
    orchestrator = build_orchestrator_agent()
    vision = build_vision_agent()
    research = build_research_agent()
    collection_planner = build_collection_planner_agent()
    debug = build_debug_agent()

    agents = [orchestrator, vision, research, collection_planner, debug]

    # TODO [Person 1]: define Tasks and assemble the Crew.
    # crew = Crew(agents=agents, tasks=[...], process=Process.hierarchical)
    # return crew
    raise NotImplementedError("build_crew: assemble Tasks + Crew (Person 1)")


# TODO [Person 1]: provide a singleton accessor so the API layer reuses one crew.
_crew = None


def get_crew():
    global _crew
    if _crew is None:
        _crew = build_crew()
    return _crew
