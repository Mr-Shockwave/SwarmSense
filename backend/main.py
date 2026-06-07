"""FastAPI application entry point for Project RoverSwarm.

Owner: Person 2 (Backend API + Redis + WebSocket)

On startup this:
  1. Initializes Weave  (weave.init)               -> Person 1 provides tracer
  2. Connects to Redis                              -> redis_layer.client
  3. Initializes the map grid as fully unexplored   -> redis_layer.map_state
  4. Determines simulation vs hardware mode         -> config.SIMULATION_MODE
  5. Logs which mode is active
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings

# Routers
from api.routes import mission, map as map_routes, rovers, targets, copilot, findings, admin
from api import websocket as ws

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("roverswarm")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # --- 1. Weave ---
    # TODO [Person 1]: call weave_tracing.tracer.init_weave() here.
    try:
        from weave_tracing.tracer import init_weave
        init_weave()
        logger.info("Weave initialized (project=%s)", settings.WEAVE_PROJECT)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Weave init skipped/failed: %s", exc)

    # --- 2. Redis ---
    try:
        from redis_layer.client import get_redis, ping
        app.state.redis = get_redis()
        await ping()
        logger.info("Redis connected: %s", settings.REDIS_URL)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Redis connect failed: %s", exc)

    # --- 2b. Flush Redis on startup (gated by FLUSH_ON_STARTUP) ---
    if settings.FLUSH_ON_STARTUP:
        try:
            await get_redis().flushdb()
            logger.info("Redis flushed on startup (FLUSH_ON_STARTUP=true)")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis flush failed: %s", exc)

    # --- 3. Initialize map grid as fully unexplored ---
    # TODO [Person 2]: call map_state.initialize_grid().
    try:
        from redis_layer.map_state import initialize_grid
        await initialize_grid()
        logger.info("Map grid initialized as unexplored")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Map grid init failed: %s", exc)

    # --- 4 & 5. Mode ---
    mode = "SIMULATION" if settings.SIMULATION_MODE else "HARDWARE"
    logger.info("RoverSwarm starting in %s mode", mode)

    # --- 6. Live Redis -> WebSocket bridge ---
    # Forwards rover:frames + scientist:ping pub/sub messages to connected UIs.
    import asyncio
    from api.websocket import redis_bridge
    app.state.ws_bridge = asyncio.create_task(redis_bridge())
    logger.info("WebSocket live bridge started")

    # --- 7. Event-driven agent runner ---
    # Listens on rover:frames and runs a subagent cycle per new frame. Gated by
    # AGENTS_AUTORUN so the UI can be developed without per-frame vision cost.
    app.state.agent_listener = None
    if settings.AGENTS_AUTORUN:
        try:
            from agents.rover_managers import agent_frame_listener
            app.state.agent_listener = asyncio.create_task(agent_frame_listener())
            logger.info("Agent frame listener started (event-driven)")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Agent frame listener failed to start: %s", exc)

    # TODO [Person 3]: instantiate rovers (SimulatedRover vs HardwareRover) per mode.

    yield

    # --- Shutdown ---
    for task_attr in ("ws_bridge", "agent_listener"):
        task = getattr(app.state, task_attr, None)
        if task is not None:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
    logger.info("RoverSwarm shutting down")


app = FastAPI(title="Project RoverSwarm", version="0.1.0", lifespan=lifespan)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
# TODO [Person 2]: confirm prefixes/tags as routes are fleshed out.
app.include_router(mission.router, prefix="/mission", tags=["mission"])
app.include_router(map_routes.router, prefix="/map", tags=["map"])
app.include_router(rovers.router, prefix="/rovers", tags=["rovers"])
app.include_router(targets.router, prefix="/targets", tags=["targets"])
app.include_router(findings.router, prefix="/findings", tags=["findings"])
app.include_router(copilot.router, prefix="/api", tags=["copilot"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# --- WebSocket ---
app.include_router(ws.router, tags=["websocket"])


@app.get("/health")
async def health():
    """Liveness probe."""
    return {
        "status": "ok",
        "mode": "simulation" if settings.SIMULATION_MODE else "hardware",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.BACKEND_PORT, reload=True)
