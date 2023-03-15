"""run.py

Script used to run vega-market-sim scenarios configure for devops.

Flags:

    -n, --network string    controls which network the scenario is run on
    -d, --debug             controls whether to log debug messages

    -c, --console           whether to launch a console (nullchain only)
    -g, --graphql           whether to launch a graphql playground (nullchain only)
    -p, --pause             whether to pause a the end of a simulation (nullchain only)
    

Examples:

    Test the ETHUSD scenario with a simulation on a nullchain network.

    $ python -m vega_sim.devops.run -s ETHUSD -n NULLCHAIN -d -c -p


    Deploy the tested scenario to the stagnet1 network:

    $ python -m vega_sim.devops.run -s ETHUSD -n STAGNET1 -d

"""

import argparse
import logging

from vega_sim.scenario.constants import Network

from vega_sim.null_service import VegaServiceNull
from vega_sim.network_service import VegaServiceNetwork

from vega_sim.scenario.scenario import Scenario
from devops.registry import SCENARIOS


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-n",
        "--network",
        choices=[network.name for network in Network],
        default=Network.FAIRGROUND.name,
    )

    parser.add_argument("-s", "--scenario")
    parser.add_argument("-g", "--graphql", action="store_true")
    parser.add_argument("-c", "--console", action="store_true")
    parser.add_argument("-p", "--pause", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    scenario: Scenario = SCENARIOS[args.scenario]()

    if Network[args.network] == Network.NULLCHAIN:
        with VegaServiceNull(
            seconds_per_block=1,
            transactions_per_block=1000,
            retain_log_files=True,
            use_full_vega_wallet=False,
            warn_on_raw_data_access=False,
            run_with_console=args.console,
            launch_graphql=args.graphql,
        ) as vega:
            scenario.run_iteration(
                vega=vega,
                network=Network[args.network],
                pause_at_completion=args.pause,
            )

    else:
        with VegaServiceNetwork(
            network=Network[args.network],
        ) as vega:
            scenario.run_iteration(
                vega=vega,
                network=Network[args.network],
                pause_at_completion=args.pause,
                raise_datanode_errors=False,
                raise_step_errors=False,
            )


if __name__ == "__main__":
    main()
