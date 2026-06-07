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
#   - Build a CopilotKit remote endpoint that exposes the CrewAI crew/agents.
#   - Register actions the scientist can call (ask about mission state, approve
#     targets, query a rover).
#   - Confirm the exact CopilotKit Python API (add_fastapi_endpoint vs manual).
#
# Example shape:
#   sdk = CopilotKitRemoteEndpoint(agents=[CrewAIAgent(name="roverswarm", crew=get_crew())])
#   add_fastapi_endpoint(app, sdk, "/api/copilot")


@router.post("/copilot")
async def copilot_runtime(request: Request):
    """CopilotKit runtime handler.

    TODO [Person 2 + Person 1]: forward the request to the CopilotKit SDK and
    return its response (streaming).
    """
    raise NotImplementedError("copilot_runtime (Person 2 + Person 1)")
