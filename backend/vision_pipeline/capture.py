"""Photo capture — real or simulated.

Owner: Person 3 (Hardware Rover + Gemma Edge)

Thin adapter over rover.take_photo() that the vision agent calls on a cadence.
"""
from __future__ import annotations

from config import PHOTO_INTERVAL_SECONDS

# from rovers.base_rover import BaseRover


async def capture_photo(rover) -> str:
    """Capture a single photo from a rover, base64-encoded.

    TODO [Person 3]: return await rover.take_photo(). Optionally downscale /
    compress for faster upload to GPT-4o vision.
    """
    raise NotImplementedError("capture_photo (Person 3)")


async def capture_loop(rover, on_photo) -> None:
    """Continuously capture every PHOTO_INTERVAL_SECONDS and invoke on_photo.

    TODO [Person 3]:
      - Loop with asyncio.sleep(PHOTO_INTERVAL_SECONDS).
      - photo = await capture_photo(rover); coord = await rover.get_position()
      - await on_photo(rover.rover_id, photo, coord)   # vision agent entrypoint
    """
    raise NotImplementedError("capture_loop (Person 3)")
