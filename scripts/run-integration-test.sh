#!/usr/bin/env bash

set -e

WORK_DIR="$(realpath "$(dirname "$0")/..")"
RESULT_DIR="${WORK_DIR}/test_logs/$(date '+%F_%H%M%S')-integration"
mkdir -p "${RESULT_DIR}"

poetry install --all-extras

poetry run pytest -s -v -m integration --junitxml ${RESULT_DIR}/integration-test-results.xml --log-cli-level INFO 
