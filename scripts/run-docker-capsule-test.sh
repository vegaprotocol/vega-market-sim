#!/usr/bin/env bash

set -e


WORK_DIR="$(realpath "$(dirname "$0")/..")"
RESULT_DIR="${WORK_DIR}/test_logs/$(date '+%F_%H%M%S')-capsule"
mkdir -p "${RESULT_DIR}"


docker rm capsule_test || true
docker run \
    --platform linux/amd64 \
    --name capsule_test \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 4646:4646 \
    vega_sim_learning:latest \
        python -m vega_sim.scenario.fuzzed_markets.run_capsule_test --steps $1 \

