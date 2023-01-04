#!/usr/bin/env bash

set -e

WORK_DIR="$(realpath "$(dirname "$0")/..")"
RESULT_DIR="${WORK_DIR}/test_logs/$(date '+%F_%H%M%S')-integration"
mkdir -p "${RESULT_DIR}"

docker run \
    --platform linux/amd64 \
    -v "${RESULT_DIR}:/tmp" \
    -v "${WORK_DIR}:/vega_market_sim" \
    vega_sim_test:latest \
         python -m tests.integration.test_plot_gen
