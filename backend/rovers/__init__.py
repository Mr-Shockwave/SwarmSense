"""Rover interface + simulated/hardware implementations + Gemma edge. Owner: Person 3."""

from config import settings


def make_rover(rover_id: str):
    """Factory: pick SimulatedRover or HardwareRover based on SIMULATION_MODE.

    TODO [Person 3]:
      - if settings.SIMULATION_MODE: return SimulatedRover(rover_id)
      - else: return HardwareRover(rover_id)
    """
    if settings.SIMULATION_MODE:
        from .simulated_rover import SimulatedRover
        return SimulatedRover(rover_id)
    from .hardware_rover import HardwareRover
    return HardwareRover(rover_id)
