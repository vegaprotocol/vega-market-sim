import argparse
import logging

from vega_sim.scenario.constants import Network

from vega_sim.null_service import VegaServiceNull
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.scenario.registry import SCENARIOS
from vega_sim.scenario.scenario import Scenario
from vega_sim.service import VegaService


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--scenario")
    parser.add_argument("--console", action="store_true")
    parser.add_argument("--graphql", action="store_true")
    parser.add_argument("--pause", action="store_true")
    parser.add_argument(
        "--network",
        choices=[network.name for network in Network],
        default=Network.NULLCHAIN.name,
    )
    parser.add_argument(
        "-p",
        "--pause_every_n_steps",
        default=None,
        type=int,
    )
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    scenario: Scenario = SCENARIOS[args.scenario]()

    scenario.pause_every_n_steps = args.pause_every_n_steps

    if Network[args.network] == Network.NULLCHAIN:
        with VegaServiceNull(
            run_with_console=args.console,
            launch_graphql=args.graphql,
            warn_on_raw_data_access=False,
            seconds_per_block=scenario.block_length_seconds,
            transactions_per_block=(
                scenario.transactions_per_block
                if hasattr(scenario, "transactions_per_block")
                else 100
            ),
            retain_log_files=True,
            use_full_vega_wallet=False,
        ) as vega:
            scenario.run_iteration(
                vega=vega,
                network=Network[args.network],
                pause_at_completion=args.pause,
            )
    else:
        with VegaServiceNetwork(
            network=Network[args.network].value,
            automatic_consent=True,
            no_version_check=True,
        ) as vega:
            scenario.run_iteration(
                vega=vega,
                network=Network[args.network],
            )


if __name__ == "__main__":
    main()
