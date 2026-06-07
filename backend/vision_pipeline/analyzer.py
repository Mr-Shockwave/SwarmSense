"""GPT-4o vision call + criteria matching.

Owner: Person 3 (pipeline) + Person 1 (agent consumes this)

Given a photo and the scientist's criteria, decide whether the photo contains a
matching object and describe it. Used by agents/vision.py and the per-rover
vision subagent (rover_subagents.run_vision_subagent).

Canonical output shape:
    {"findings": [{"label": str, "description": str, "confidence": float}, ...]}
An empty `findings` list means nothing in the frame matched the criteria
(i.e. target not found in this frame).
"""
from __future__ import annotations

import weave
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from config import settings


class Finding(BaseModel):
    label: str = Field(description="Short name of the matching object, e.g. 'red cube'.")
    description: str = Field(description="What it looks like and roughly where it sits in the frame.")
    confidence: float = Field(ge=0.0, le=1.0, description="Likelihood this object satisfies the criteria.")


class VisionResult(BaseModel):
    findings: list[Finding]


_SYSTEM = (
    "You are a planetary rover's vision analyst. Inspect the image and report ONLY "
    "objects that satisfy the scientist's criteria. Emit one finding per matching "
    "object, with a calibrated confidence in [0, 1]. If nothing in the frame matches "
    "the criteria, return an empty findings list. Never invent objects that are not "
    "clearly visible."
)


@weave.op()
async def analyze_photo(photo_b64: str, criteria: str) -> dict:
    """Run GPT-4o vision and match against scientist criteria.

    Returns {"findings": [...]} where each finding satisfies `criteria`.
    An empty list means the target was not found in this frame.
    """
    if not settings.OPENAI_API_KEY:
        # No key (e.g. --dry-run / offline): behave like "nothing matched".
        return {"findings": []}

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    completion = await client.beta.chat.completions.parse(
        model=settings.OPENAI_VISION_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Scientist criteria: {criteria}"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{photo_b64}"},
                    },
                ],
            },
        ],
        response_format=VisionResult,
    )
    parsed = completion.choices[0].message.parsed
    return parsed.model_dump() if parsed else {"findings": []}