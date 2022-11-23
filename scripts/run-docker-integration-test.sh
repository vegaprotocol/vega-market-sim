#!/usr/bin/env bash

set -e

WORK_DIR="$(realpath "$(dirname "$0")/..")"
RESULT_DIR="${WORK_DIR}/test_logs/$(date '+%F_%H%M%S')-integration"
PROF_DIR="${WORK_DIR}/prof/$(date '+%F_%H%M%S')-integration"
mkdir -p "${RESULT_DIR}"
mkdir -p "${PROF_DIR}"

docker run \
    --platform linux/amd64 \
    -v "${RESULT_DIR}:/tmp" \
    -v "${PROF_DIR}:/vega_market_sim/prof" \
    vega_sim_test:latest \
        pytest -s -v --profile \
            -m integration \
            --junitxml /tmp/integration-test-results.xml \
            --log-cli-level INFO 
