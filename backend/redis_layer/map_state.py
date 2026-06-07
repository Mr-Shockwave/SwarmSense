"""Shared map grid read/write.

Owner: Person 2 (Backend API + Redis + WebSocket)

Cell states (config.py): unexplored, explored, redzone, object, target.
Keys:
  map:coord_X_Y    -> cell state
  map:redzones     -> set of blocked coordinates {x, y, radius, reported_by}
"""
from __future__ import annotations

from config import (
    GRID_WIDTH,
    GRID_HEIGHT,
    CELL_UNEXPLORED,
)

# from . import client


def _cell_key(x: int, y: int) -> str:
    return f"map:coord_{x}_{y}"


async def initialize_grid() -> None:
    """Set every cell to unexplored at mission start.

    TODO [Person 2]:
      - Loop GRID_WIDTH x GRID_HEIGHT, set each _cell_key to CELL_UNEXPLORED.
      - Use a pipeline for speed.
      - Clear map:redzones.
    """
    raise NotImplementedError("initialize_grid (Person 2)")


async def set_cell(x: int, y: int, state: str) -> None:
    """Set a single cell's state and publish a map update.

    TODO [Person 2]:
      - client.set(_cell_key(x, y), state)
      - publish CHANNEL_MAP_UPDATE so the WebSocket pushes to the UI.
    """
    raise NotImplementedError("set_cell (Person 2)")


async def get_cell(x: int, y: int) -> str:
    """TODO [Person 2]: return cell state or CELL_UNEXPLORED if unset."""
    raise NotImplementedError("get_cell (Person 2)")


async def get_full_grid() -> list[list[str]]:
    """Return the entire grid as a 2D list for the UI / GET /map/state.

    TODO [Person 2]: read all cells (pipeline) into [y][x] states.
    """
    raise NotImplementedError("get_full_grid (Person 2)")


async def add_redzone(x: int, y: int, radius: int, reported_by: str) -> None:
    """Add a red zone to the set and mark affected cells.

    TODO [Person 2]:
      - client.sadd("map:redzones", json{x, y, radius, reported_by})
      - mark cells within radius as CELL_REDZONE.
    (Broadcasting/publish handled by coordination/redzone.py.)
    """
    raise NotImplementedError("add_redzone (Person 2)")


async def get_redzones() -> list[dict]:
    """TODO [Person 2]: return parsed members of map:redzones."""
    raise NotImplementedError("get_redzones (Person 2)")
