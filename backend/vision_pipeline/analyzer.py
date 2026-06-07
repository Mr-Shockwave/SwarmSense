from __future__ import annotations

import weave
from openai import AsyncOpenAI
from pydantic import BaseModel

from config import settings


class VisionVerdict(BaseModel):
    found: bool


_SYSTEM = (
    "You are a planetary rover's vision analyst. You are given the scientist's target "
    "criteria and one camera frame. Reason about the image and decide whether the "
    "target is present. Return found=true only if an object clearly matching the "
    "criteria is visible in the frame; otherwise found=false. Do not guess."
)


@weave.op()
async def analyze_photo(photo_b64: str, criteria: str) -> bool:
    """Reason about the frame and return whether the target (criteria) is present."""
    if not settings.OPENAI_API_KEY:
        return False

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    completion = await client.beta.chat.completions.parse(
        model=settings.OPENAI_VISION_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Target criteria: {criteria}\n\nIs the target present in this frame?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{photo_b64}"}},
                ],
            },
        ],
        response_format=VisionVerdict,
    )
    parsed = completion.choices[0].message.parsed
    return bool(parsed.found) if parsed else False