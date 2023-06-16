#!/usr/bin/env bash

set -e

WORK_DIR="$(realpath "$(dirname "$0")/..")"
RESULT_DIR="${WORK_DIR}/test_logs/$(date '+%F_%H%M%S')-capsule"
mkdir -p "${RESULT_DIR}"

VEGA_BINS="${WORK_DIR}/vega_sim/bin"
VEGA_HOME="${RESULT_DIR}/vegahome"
mkdir -p "${VEGA_HOME}"

cleanup() {
    # Cleanup vegacapsule network
    eval "${VEGA_BINS}/vegacapsule network destroy"
    # Cleanup hanging vegacapsule or nomad_1.3.1 processes
    processes=("nomad_1.3.1" "vegacapsule")
    for process_name in "${processes[@]}"; do
        pids=$(pgrep "$process_name")
        if [ -n "$pids" ]; then
            echo "Killing processes with name $process_name..."
            for pid in $pids; do
                kill "$pid"
            done
        else
            echo "No processes found with name $process_name."
        fi
    done
}
trap cleanup EXIT

echo "Spinning up a nomad server"
eval "${VEGA_BINS}/vegacapsule nomad --home-path ${VEGA_HOME} --install-path ${VEGA_BINS}" >/dev/null 2>&1 &
sleep 15
echo "Spinning up a vegacapsule network"
eval "${VEGA_BINS}/vegacapsule network bootstrap --config-path ${WORK_DIR}/vega_sim/vegacapsule/config.hcl --home-path ${VEGA_HOME}"
eval "${VEGA_BINS}/vegacapsule ethereum multisig init --home-path ${VEGA_HOME}"

docker run \
    --platform linux/amd64 \
    --network host \
    -v "${RESULT_DIR}:/tmp" \
    vega_sim_learning:latest \
        python -m vega_sim.scenario.fuzzed_markets.run_capsule_test --steps $1 --test-dir "/tmp" --debug --network_on_host
