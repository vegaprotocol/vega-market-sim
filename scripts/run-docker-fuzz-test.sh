#!/usr/bin/env bash

set -e

WORK_DIR="$(realpath "$(dirname "$0")/..")"
RESULT_DIR="${WORK_DIR}/test_logs/$(date '+%F_%H%M%S')-integration"
mkdir -p "${RESULT_DIR}"

docker rm fuzz_test || true
docker run \
    --platform linux/amd64 \
    --name fuzz_test \
    -v "${RESULT_DIR}:/tmp" \
    vega_sim_learning:latest \
        python -m vega_sim.scenario.fuzzed_markets.run_fuzz_test --steps 2880

docker cp fuzz_test:/vega_market_sim/fuzz_plots/. .
docker rm fuzz_test
