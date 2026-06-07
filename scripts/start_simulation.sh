#!/usr/bin/env bash
# Runs the full system in simulation mode (virtual rovers, no hardware).
# Usage: ./scripts/start_simulation.sh [scenario]
#   scenario: basic_exploration | obstacle_course | object_detection
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f .env ]; then
  set -a; source .env; set +a
fi

# Force simulation mode regardless of .env
export SIMULATION_MODE=true

SCENARIO="${1:-basic_exploration}"
echo "🧪 Simulation mode — scenario: ${SCENARIO}"

# TODO [Person 2 / Person 3]: wire this to actually launch the backend in sim mode
#   and kick off the chosen scenario from simulation/test_scenarios/.
if ! redis-cli ping >/dev/null 2>&1; then
  redis-server --daemonize yes
fi

# Start backend (reads SIMULATION_MODE=true -> SimulatedRover)
( cd backend && uvicorn main:app --reload --port "${BACKEND_PORT:-8000}" ) &
BACKEND_PID=$!

# Run the selected scenario
python -m simulation.test_scenarios."${SCENARIO}"

trap "kill $BACKEND_PID 2>/dev/null || true" EXIT
wait
