#!/usr/bin/env bash

set -e

WORK_DIR="$(realpath "$(dirname "$0")/..")"
RESULT_DIR="${WORK_DIR}/test_logs/$(date '+%F_%H%M%S')-integration"
mkdir -p "${RESULT_DIR}"

docker run \
    --platform linux/amd64 \
    -v "${WORK_DIR}:/tmp" \
    vega_sim_test:latest \
        pytest -s -v \
            -m integration \
            --junitxml /tmp/integration-test-results.xml \
            --log-cli-level INFO 
