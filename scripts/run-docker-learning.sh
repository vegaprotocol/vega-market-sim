#!/usr/bin/env bash

set -e

WORK_DIR="$(realpath "$(dirname "$0")/..")"
RESULT_DIR="${WORK_DIR}/test_logs/$(date '+%F_%H%M%S')-integration"
mkdir -p "${RESULT_DIR}"

docker run \
    --platform linux/amd64 \
    -v "${RESULT_DIR}:/tmp" \
    vega_sim_learning:latest \
        python -m vega_sim.reinforcement.run_rl_agent --rl-max-it 1000
