#!/usr/bin/env bash
# Starts backend + frontend + Redis locally for development.
# Usage: ./scripts/start_dev.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Load .env if present
if [ -f .env ]; then
  set -a; source .env; set +a
fi

# TODO [Person 2]: make Redis startup robust (detect existing instance, Redis Cloud, etc.)
echo "🔴 Starting Redis..."
if ! redis-cli ping >/dev/null 2>&1; then
  redis-server --daemonize yes
fi

echo "🐍 Starting FastAPI backend on port ${BACKEND_PORT:-8000}..."
( cd backend && uvicorn main:app --reload --port "${BACKEND_PORT:-8000}" ) &
BACKEND_PID=$!

echo "⚛️  Starting frontend on port ${FRONTEND_PORT:-5173}..."
( cd frontend && npm run dev -- --port "${FRONTEND_PORT:-5173}" ) &
FRONTEND_PID=$!

# TODO [Person 2]: graceful shutdown — trap SIGINT/SIGTERM and kill child PIDs
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true" EXIT
wait
