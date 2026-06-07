#!/usr/bin/env bash
# Pushes edge code (rovers/ + gemma_edge) to a physical Lego rover device.
# Usage: ./scripts/deploy_rover.sh <rover_id> <rover_host>
#   e.g. ./scripts/deploy_rover.sh rover1 192.168.1.50
set -euo pipefail

ROVER_ID="${1:?Usage: deploy_rover.sh <rover_id> <rover_host>}"
ROVER_HOST="${2:?Usage: deploy_rover.sh <rover_id> <rover_host>}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 Deploying edge code to ${ROVER_ID} @ ${ROVER_HOST}..."

# TODO [Person 3]: implement the real deploy.
#   - Package backend/rovers/{base_rover,hardware_rover,gemma_edge}.py
#   - Copy Gemma 2B weights / config to the device
#   - rsync/scp over to the Lego SPIKE / Mindstorms runtime
#   - Restart the rover edge service
#   Example skeleton:
# rsync -avz "$ROOT/backend/rovers/" "robot@${ROVER_HOST}:/home/robot/roverswarm/rovers/"
# ssh "robot@${ROVER_HOST}" "sudo systemctl restart roverswarm-edge"

echo "⚠️  deploy_rover.sh is a stub — implement the device push (Person 3)."
