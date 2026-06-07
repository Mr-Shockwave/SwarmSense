"""Central configuration — env vars and project-wide constants.

Owner: Person 2 (Backend API + Redis + WebSocket)

All tunable values live here so every module imports from one place.
Loads from environment (and a local .env via python-dotenv).
"""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _get_bool(key: str, default: bool) -> bool:
    return os.getenv(key, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    """Runtime settings sourced from environment variables."""

    # --- LLM ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_ORCHESTRATION_MODEL: str = os.getenv("OPENAI_ORCHESTRATION_MODEL", "gpt-4o")
    OPENAI_VISION_MODEL: str = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")

    # --- Redis ---
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # --- Weave / W&B ---
    WANDB_API_KEY: str = os.getenv("WANDB_API_KEY", "")
    WEAVE_PROJECT: str = os.getenv("WEAVE_PROJECT", "roverswarm")

    # --- Execution mode ---
    SIMULATION_MODE: bool = _get_bool("SIMULATION_MODE", True)

    # --- Ports ---
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "5173"))

    # --- Hardware mode ---
    ROVER1_HOST: str = os.getenv("ROVER1_HOST", "")
    ROVER2_HOST: str = os.getenv("ROVER2_HOST", "")
    GEMMA_MODEL_PATH: str = os.getenv("GEMMA_MODEL_PATH", "")

    # --- CORS (frontend origin) ---
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


# ─────────────────────────────────────────────────────────────
# Project-wide constants (shared by sim, hardware, agents, UI)
# ─────────────────────────────────────────────────────────────

# Map grid dimensions (must match simulation/world.py)
GRID_WIDTH: int = 20
GRID_HEIGHT: int = 20

# Cell states used in the shared map (see redis_layer/map_state.py)
CELL_UNEXPLORED: str = "unexplored"
CELL_EXPLORED: str = "explored"
CELL_REDZONE: str = "redzone"
CELL_OBJECT: str = "object"
CELL_TARGET: str = "target"  # scientist-approved

# Rover identifiers
ROVER_IDS: tuple[str, str] = ("rover1", "rover2")

# Photo cadence (seconds) — vision pipeline trigger
PHOTO_INTERVAL_SECONDS: float = 5.5

# Red zone default radius (cm) broadcast on obstacle hit
REDZONE_RADIUS_CM: int = 20

# Anti-gaslight trust hierarchy (lower number = higher trust). See
# coordination/anti_gaslight.py. These are hardcoded / non-negotiable.
TRUST_LOCAL_SENSOR: int = 1   # HIGHEST
TRUST_SHARED_MAP: int = 2
TRUST_INTER_ROVER: int = 3
TRUST_CLOUD_AGENT: int = 4    # LOWEST — Gemma makes the final call


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()
