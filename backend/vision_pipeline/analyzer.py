<<<<<<< HEAD
"""GPT-4o vision call + criteria matching.

Owner: Person 3 (pipeline) + Person 1 (agent consumes this)

Given a photo and the scientist's criteria, decide whether the photo contains a
matching object and describe it.

Canonical output shape:
    {"findings": [{"label": str, "description": str, "confidence": float}, ...]}
An empty `findings` list means nothing in the frame matched the criteria.
"""
=======
>>>>>>> 513345842c1fa96d1404d68bdac41230871762d8
from __future__ import annotations

import weave
from openai import AsyncOpenAI
<<<<<<< HEAD
from pydantic import BaseModel, Field
=======
from pydantic import BaseModel
>>>>>>> 513345842c1fa96d1404d68bdac41230871762d8

from config import settings


<<<<<<< HEAD
class Finding(BaseModel):
    label: str = Field(description="Short name of the matching object, e.g. 'red cube'.")
    description: str = Field(description="What it looks like and roughly where it sits in the frame.")
    confidence: float = Field(ge=0.0, le=1.0, description="Likelihood this object satisfies the criteria.")


class VisionResult(BaseModel):
    findings: list[Finding]
=======
class VisionVerdict(BaseModel):
    found: bool
>>>>>>> 513345842c1fa96d1404d68bdac41230871762d8


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

    Accepts either a raw base64 string or a full data URI
    (data:image/jpeg;base64,...). SVG images are skipped — GPT-4o doesn't
    support them and dev_capture uses SVGs as placeholders.
    """
    if not settings.OPENAI_API_KEY:
        return {"findings": []}

    # Parse data URI if present, extract mime + raw base64.
    if photo_b64.startswith("data:"):
        try:
            header, raw = photo_b64.split(",", 1)
            mime = header.split(";")[0].split(":")[1]
        except (ValueError, IndexError):
            return {"findings": []}
        # SVG is a placeholder from dev_capture — skip rather than 400.
        if "svg" in mime:
            return {"findings": []}
        image_url = f"data:{mime};base64,{raw}"
    else:
        image_url = f"data:image/jpeg;base64,{photo_b64}"

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
                        "image_url": {"url": image_url},
                    },
                ],
            },
        ],
        response_format=VisionResult,
    )
    parsed = completion.choices[0].message.parsed
    return parsed.model_dump() if parsed else {"findings": []}
