#!/usr/bin/env bash

set -e

WORK_DIR="$(realpath "$(dirname "$0")/..")"
RESULT_DIR="${WORK_DIR}/test_logs/$(date '+%F_%H%M%S')-notebook"
mkdir -p "${RESULT_DIR}"

docker run --rm \
    --platform linux/amd64 \
    -v "${RESULT_DIR}:/tmp" \
    vega_sim_test:latest \
        pytest \
            --junitxml /tmp/notebook-test-results.xml \
            --log-cli-level INFO \
            --nbmake examples/notebooks
