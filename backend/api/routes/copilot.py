"""CopilotKit runtime endpoint — bridges CrewAI agents to the CopilotKit frontend.

Owner: Person 2 (Backend API + Redis + WebSocket), with Person 1 for agent wiring.

The frontend wraps the app in <CopilotKit runtimeUrl="/api/copilot">. This
endpoint is that runtime: it exposes the crew's agents + actions to the UI chat
and ping overlay.
"""
from __future__ import annotations

from fastapi import APIRouter, Request

# from copilotkit import CopilotKitRemoteEndpoint, CrewAIAgent
# from copilotkit.integrations.fastapi import add_fastapi_endpoint
# from agents.crew import get_crew

router = APIRouter()


# TODO [Person 2 + Person 1]:
#   - Build a CopilotKit remote endpoint that exposes the mission crew AND both
#     per-rover manager crews (see agents.rover_managers).
#   - Example: expose build_rover1_manager_agent() and build_rover2_manager_agent()
#     as separate CopilotKit agents so the scientist can chat with each rover lead.
#   - Register actions the scientist can call (ask about mission state, approve
#     targets, query a rover).
#   - Confirm the exact CopilotKit Python API (add_fastapi_endpoint vs manual).
#
# Example shape:
#   from agents import build_rover1_manager_agent, build_rover2_manager_agent, get_crew
#   crews = get_crew()
#   sdk = CopilotKitRemoteEndpoint(agents=[
#       CrewAIAgent(name="mission", crew=crews["mission_crew"]),
#       CrewAIAgent(name="rover1-manager", crew=crews["rover1_crew"]),
#       CrewAIAgent(name="rover2-manager", crew=crews["rover2_crew"]),
#   ])
#   add_fastapi_endpoint(app, sdk, "/api/copilot")


@router.post("/copilot")
async def copilot_runtime(request: Request):
    """CopilotKit runtime handler.

    TODO [Person 2 + Person 1]: forward the request to the CopilotKit SDK and
    return its response (streaming).
    """
    raise NotImplementedError("copilot_runtime (Person 2 + Person 1)")
