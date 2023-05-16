import os
import time
import atexit
import logging
import argparse
import functools
import subprocess

from io import BufferedWriter
from typing import Optional, List, Dict
from datetime import datetime

from vega_sim.scenario.constants import Network
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.scenario.fuzzed_markets.scenario import FuzzingScenario


def _terminate_proc(
    proc: subprocess.Popen[bytes], out_file: BufferedWriter, err_file: BufferedWriter
) -> None:
    subprocess.run(
        [
            "vega_sim/bin/vegacapsule",
            "network",
            "destroy",
        ]
    )
    proc.terminate()
    out_file.close()
    err_file.close()


def _popen_process(
    popen_args: List[str],
    dir_root: str,
    log_name: str,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.Popen[bytes]:
    out = open(os.path.join(dir_root, f"{log_name}.out"), "wb")
    err = open(os.path.join(dir_root, f"{log_name}.err"), "wb")
    sub_proc = subprocess.Popen(
        popen_args, stdout=out, stderr=err, env=env, close_fds=True
    )

    atexit.register(functools.partial(_terminate_proc, sub_proc, out, err))
    return sub_proc


def _run(
    steps: int,
    test_dir: Optional[str] = None,
):
    test_dir = (
        test_dir
        if test_dir is not None
        else os.path.abspath(
            f"test_logs/{datetime.now().strftime('%Y-%m-%d_%H%M%S')}-capsule"
        )
    )
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    _popen_process(
        [
            "vega_sim/bin/vegacapsule",
            "nomad",
            "--home-path",
            f"{test_dir}/vegahome",
            "--install-path",
            "./vega_sim/bin",
        ],
        dir_root=test_dir,
        log_name="nomad",
    )
    # Sleep to allow nomad server to finish setup
    time.sleep(10)
    subprocess.run(
        [
            "vega_sim/bin/vegacapsule",
            "network",
            "bootstrap",
            "--config-path",
            "vega_sim/vegacapsule/config.hcl",
            "--home-path",
            f"{test_dir}/vegahome",
        ]
    )
    subprocess.run(
        [
            "vega_sim/bin/vegacapsule",
            "ethereum",
            "multisig",
            "init",
            "--home-path",
            f"{test_dir}/vegahome",
        ]
    )

    scenario = FuzzingScenario(
        num_steps=steps,
        step_length_seconds=2,
        block_length_seconds=1,
        transactions_per_block=4096,
        n_markets=1,
    )

    with VegaServiceNetwork(
        network=Network.CAPSULE,
        run_with_wallet=False,
        run_with_console=True,
        vega_home_path=f"{test_dir}/vegahome",
        wallet_home_path=f"{test_dir}/vegahome/wallet",
        network_config_path=f"{test_dir}/vegahome/wallet",
        wallet_passphrase_path="vega_sim/vegacapsule/passphrase-file",
        faucet_url="http://localhost:1790",
        load_existing_keys=False,
        governance_symbol="VEGA",
    ) as vega:
        # Run the fuzzing scenario
        scenario.run_iteration(
            vega=vega,
            network=Network.CAPSULE,
            log_every_n_steps=100,
        )

        # Check all data nodes have matching network history segments
        nodes_checked = set()
        previous_node_segments = None
        while vega.data_node_grpc_url not in nodes_checked:
            # Check the network history segments of the current node match the previous
            current_node_segments = vega.list_all_network_history_segments()
            # print(current_node_segments)
            if previous_node_segments is not None:
                assert previous_node_segments == current_node_segments
            previous_node_segments = current_node_segments

            # Add node to the checked nodes then switch node
            nodes_checked.add(vega.data_node_grpc_url)
            vega.switch_datanode()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--steps", type=int, default=100)
    parser.add_argument("--test-dir", type=str, default=None)

    parser.add_argument("-d", "--debug", action="store_true")

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    _run(
        steps=args.steps,
        test_dir=args.test_dir,
    )
