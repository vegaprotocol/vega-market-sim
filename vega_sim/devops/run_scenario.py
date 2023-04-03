"""run_scenario.py

Script used to run vega-market-sim scenarios configure for devops.

Flags:

    -s, --scenario          controls which scenario to test/deploy
    -n, --network           controls which network the scenario should run on
    -m, --market            controls which market the market should run on

    -d, --debug             controls whether to log debug messages
    -c, --console           whether to launch a console
    -g, --graphql           whether to launch a graphql playground 
    -p, --pause             whether to pause a the end of a simulation
    

Examples:

    Test the ETHUSD scenario with a simulation on a nullchain network.

    $ python -m vega_sim.devops.run -s ETHUSD -n NULLCHAIN -d -c -p


"""

import argparse
import logging

from vega_sim.scenario.constants import Network

from vega_sim.null_service import VegaServiceNull
from vega_sim.network_service import VegaServiceNetwork

from devops.scenario import DevOpsScenario
from devops.registry import SCENARIOS


def main():
    parser = argparse.ArgumentParser()

    # Simulation / deployment arguments
    parser.add_argument(
        "-n",
        "--network",
        choices=[network.name for network in Network],
        default=Network.FAIRGROUND.name,
    )
    parser.add_argument("-s", "--scenario", default=None, type=str)
    parser.add_argument("-m", "--market_name", default=None, type=str)
    parser.add_argument("-l", "--step_length_seconds", default=10, type=int)

    # Developer arguments
    parser.add_argument("-c", "--console", action="store_true")
    parser.add_argument("-p", "--pause", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    scenario: DevOpsScenario = SCENARIOS[args.scenario]()

    scenario.market_name = args.market_name
    scenario.step_length_seconds = args.step_length_seconds

    if Network[args.network] == Network.NULLCHAIN:
        with VegaServiceNull(
            seconds_per_block=1,
            transactions_per_block=1000,
            retain_log_files=True,
            use_full_vega_wallet=False,
            warn_on_raw_data_access=False,
            run_with_console=args.console,
        ) as vega:
            scenario.run_iteration(
                vega=vega,
                network=Network[args.network],
                pause_at_completion=args.pause,
            )

    else:
        with VegaServiceNetwork(
            network=Network[args.network],
            run_with_console=args.console,
        ) as vega:
            scenario.run_iteration(
                vega=vega,
                network=Network[args.network],
                pause_at_completion=args.pause,
                raise_datanode_errors=False,
                raise_step_errors=False,
                run_with_snitch=False,
            )


if __name__ == "__main__":
    main()
