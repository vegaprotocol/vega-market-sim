import logging
import argparse

from typing import Optional

from vega_sim.scenario.constants import Network
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.scenario.fuzzed_markets.scenario import FuzzingScenario


class NetworkHistoryDivergenceError(Exception):
    def __init__(self, from_height, to_height):
        message = f"Divergence occurred between blocks {from_height} and {to_height}"
        super().__init__(message)


def check_divergence(vega):
    # Check all data nodes have matching network history segments
    nodes_checked = set()
    previous_node_segments = None
    while vega.data_node_grpc_url not in nodes_checked:
        # Check the network history segments of the current node match the previous
        current_node_segments = vega.list_all_network_history_segments()
        if previous_node_segments is not None:
            if previous_node_segments != current_node_segments:
                from_height, to_height = find_block_range(
                    current_node_segments, previous_node_segments
                )
                raise NetworkHistoryDivergenceError(from_height, to_height)
        previous_node_segments = current_node_segments

        # Add node to the checked nodes then switch node
        nodes_checked.add(vega.data_node_grpc_url)
        vega.switch_datanode()


def find_block_range(current_node_segments, previous_node_segments):
    for i in range(1, len(current_node_segments) + 1):
        if (
            current_node_segments[-i].history_segment_id
            != previous_node_segments[-i].history_segment_id
        ):
            return (
                current_node_segments[-i].from_height,
                current_node_segments[-i].to_height,
            )


def _run(
    steps: int,
    test_dir: Optional[str] = None,
    console: Optional[bool] = False,
    network_on_host: bool = False,
):
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
        run_with_console=console,
        vega_home_path=f"{test_dir}/vegahome",
        wallet_home_path=f"{test_dir}/vegahome/wallet",
        wallet_path="vega_sim/bin/vegawallet",
        network_config_path=f"{test_dir}/vegahome/wallet",
        wallet_passphrase_path="vega_sim/vegacapsule/passphrase-file",
        wallet_url="http://localhost:1789",
        faucet_url="http://localhost:1790",
        load_existing_keys=False,
        governance_symbol="VEGA",
        network_on_host=network_on_host,
    ) as vega:
        # Run the fuzzing scenario
        scenario.run_iteration(
            vega=vega,
            network=Network.CAPSULE,
            log_every_n_steps=100,
        )

        check_divergence(vega)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--steps", type=int, default=100)
    parser.add_argument("--test-dir", type=str, default=None)

    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--console", action="store_true")
    parser.add_argument("--network_on_host", action="store_true")

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    _run(
        steps=args.steps,
        console=args.console,
        test_dir=args.test_dir,
        network_on_host=args.network_on_host,
    )
