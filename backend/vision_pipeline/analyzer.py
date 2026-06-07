"""GPT-4o vision call + criteria matching.

Owner: Person 3 (pipeline) + Person 1 (agent consumes this)

Given a photo and the scientist's criteria, decide whether the photo contains a
matching object and describe it. Used by agents/vision.py.
"""
from __future__ import annotations

# from openai import OpenAI
# import weave
from config import settings


# @weave.op()
async def analyze_photo(photo_b64: str, criteria: str) -> dict:
    """Run GPT-4o vision and match against scientist criteria.

    TODO [Person 3]:
      - Call the OpenAI vision model (settings.OPENAI_VISION_MODEL) with the
        image + a prompt embedding `criteria`.
      - Parse a structured result.
      - Return {"match": bool, "description": str, "confidence": float, "label": str}.
      - Weave should trace input photo + output match/description.
    """
    raise NotImplementedError("analyze_photo (Person 3)")
