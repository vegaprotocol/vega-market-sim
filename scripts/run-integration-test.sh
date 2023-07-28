#!/usr/bin/env bash
set -e


# Default values for environment variables. Those variables may be exported with bash `export <ENV_NAME>=value`
# Jenkins provides definition of the below variables
: "${PARALLEL_WORKERS:=0}"
: "${TEST_FUNCTION:=}"
: "${LOG_LEVEL:=INFO}"

WORK_DIR="$(realpath "$(dirname "$0")/..")"
RESULT_DIR="${WORK_DIR}/test_logs/$(date '+%F_%H%M%S')-integration"
mkdir -p "${RESULT_DIR}"


set -x
pytest -s -v -m integration \
    --junitxml ${RESULT_DIR}/integration-test-results.xml \
    --log-cli-level "${LOG_LEVEL}" \
    -n "${PARALLEL_WORKERS}" \
    -k "${TEST_FUNCTION}" 
