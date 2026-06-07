# Project RoverSwarm 🤖🛰️

An autonomous **multi-robot exploration system** with a **multi-agent AI brain**.

Two Lego rovers explore a physical space, build a shared 2D map, detect
user-defined objects of interest, ping a scientist via a live UI, and coordinate
with each other through Redis. The system runs in **simulation mode** (virtual
rovers on a 2D grid) or **real hardware mode** (same codebase, different
execution layer) — flip a single environment variable to switch.

---

## Architecture

```
[ Scientist ] → [ CopilotKit UI ] → [ FastAPI Gateway ]
                                          │
                            ┌─────────────┴─────────────┐
                            │   CrewAI Cloud Agent Crew  │
                            │  orchestrator / vision /   │
                            │  research / collection /   │
                            │  debug                     │
                            └─────────────┬─────────────┘
                                          │
                                    [ Redis Layer ]
                              KV state · Pub/Sub · error logs
                                          │
                              ┌───────────┴───────────┐
                          [ Rover 1 ]             [ Rover 2 ]
                          Gemma 2B (edge)         Gemma 2B (edge)
```

- **Backend:** Python (FastAPI)
- **Agent framework:** CrewAI
- **LLMs:** OpenAI GPT-4o (orchestration, vision, research) + Gemma 2B (local, per rover)
- **Memory/State:** Redis (KV + Pub/Sub)
- **Observability:** Weights & Biases Weave
- **Frontend:** React + Vite + CopilotKit + AG-UI
- **Map viz:** React canvas (2D grid)
- **Hardware:** Lego Mindstorms / SPIKE API
- **Simulation:** Pure-Python virtual rover (identical interface to hardware)

---

## Quick Start (Simulation Mode)

Simulation mode is the default — the project runs out of the box without hardware.

```bash
# 1. Clone + configure
cp .env.example .env          # SIMULATION_MODE=true is the default
#   edit .env and add your OPENAI_API_KEY and WANDB_API_KEY

# 2. Make sure Redis is running locally (or set REDIS_URL to Redis Cloud)
redis-server &

# 3. Backend deps
cd backend && pip install -r requirements.txt && cd ..

# 4. Frontend deps
cd frontend && npm install && cd ..

# 5. Run everything
./scripts/start_dev.sh        # backend + frontend + redis
# or, simulation only:
./scripts/start_simulation.sh
```

Open the UI at http://localhost:5173 and the API at http://localhost:8000.

---

## Running With Real Hardware

1. Set `SIMULATION_MODE=false` in `.env`.
2. Flash / deploy the edge code to each Lego rover:
   ```bash
   ./scripts/deploy_rover.sh rover1 <rover1_host>
   ./scripts/deploy_rover.sh rover2 <rover2_host>
   ```
3. Ensure both rovers can reach the Mac server's Redis instance (`REDIS_URL`).
4. Start the backend as usual (`./scripts/start_dev.sh`).

The agent logic is identical in both modes — only the hardware command layer
(`HardwareRover` vs `SimulatedRover`) changes.

---

## Environment Variables

| Variable           | Required | Default          | Description                                  |
| ------------------ | -------- | ---------------- | -------------------------------------------- |
| `OPENAI_API_KEY`   | yes      | —                | GPT-4o orchestration, vision, research       |
| `REDIS_URL`        | yes      | `redis://localhost:6379` | Redis KV + Pub/Sub connection        |
| `WANDB_API_KEY`    | yes      | —                | Weights & Biases Weave tracing               |
| `SIMULATION_MODE`  | no       | `true`           | `true` = virtual rovers, `false` = hardware  |
| `WEAVE_PROJECT`    | no       | `roverswarm`     | Weave project name                           |
| `BACKEND_PORT`     | no       | `8000`           | FastAPI port                                 |
| `FRONTEND_PORT`    | no       | `5173`           | Vite dev server port                         |

See `.env.example` for the full template.

---

## Team Assignments

| Person   | Area                                       | Directories                                                          |
| -------- | ------------------------------------------ | ------------------------------------------------------------------- |
| Person 1 | Agent logic + CrewAI + Weave + coordination| `backend/agents/`, `backend/weave_tracing/`, `backend/coordination/`|
| Person 2 | Backend API + Redis + WebSocket            | `backend/api/`, `backend/redis_layer/`, `backend/main.py`, `config.py`|
| Person 3 | Hardware rover + Gemma edge                | `backend/rovers/`, `backend/vision_pipeline/`, `scripts/deploy_rover.sh`|
| Person 4 | Frontend + UI + CopilotKit                 | `frontend/`                                                          |

Every file is tagged with `# TODO [Person N]` comments marking exactly what
needs to be implemented.

---

## Demo Arc

1. **Split & explore** — rovers take left/right zones, map builds live.
2. **Interesting find** — vision agent detects an object, pings scientist,
   research agent streams analysis, orchestrator reassigns to nearest rover.
3. **Red zone propagation** — one rover hits an obstacle, broadcasts a red zone,
   the other reroutes before reaching it.
4. **Anti-gaslight moment** — rovers disagree; local sensor data wins; the
   disagreement is logged to Weave.
5. **Self-healing** — a rover fault is diagnosed by the debug agent via Weave
   traces and a fix is pushed.
6. **Collection & return** — rovers retrieve approved targets and return home.
