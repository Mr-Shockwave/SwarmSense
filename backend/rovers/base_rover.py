"""Abstract rover interface — shared by simulation and hardware.

Owner: Person 3 (Hardware Rover + Gemma Edge)

Both SimulatedRover and HardwareRover implement this exact interface so the
agent logic above is identical in either mode (the contingency contract).
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class BaseRover(ABC):
    """Common contract every rover must satisfy."""

    def __init__(self, rover_id: str) -> None:
        self.rover_id = rover_id

    @abstractmethod
    async def move_forward(self, cm: float) -> None:
        """Drive forward by `cm` centimeters."""
        ...

    @abstractmethod
    async def turn(self, degrees: float) -> None:
        """Turn in place by `degrees` (positive = clockwise)."""
        ...

    @abstractmethod
    async def take_photo(self) -> str:
        """Capture a photo and return it base64-encoded."""
        ...

    @abstractmethod
    async def read_proximity(self) -> float:
        """Return distance (cm) to the nearest obstacle ahead."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Immediately halt all motion."""
        ...

    @abstractmethod
    async def get_position(self) -> dict:
        """Return current {x, y, heading}."""
        ...
