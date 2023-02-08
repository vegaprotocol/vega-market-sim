"""run.py

Script used to test vega-market-sim on a nullchain network or run on a live network.

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
from vega_sim.environment.agent import StateAgentWithWallet

from devops.scenario import DevOpsScenario
from devops.registry import SCENARIOS, AGENTS


def main():
    parser = argparse.ArgumentParser()

    # Agent flags
    parser.add_argument("-a", "--agent")
    parser.add_argument("-wn", "--wallet_name")
    parser.add_argument("-wp", "--wallet_pass")
    parser.add_argument("-wk", "--wallet_key")

    # Target flags
    parser.add_argument(
        "-n",
        "--network",
        choices=[network.name for network in Network],
        default=Network.FAIRGROUND.name,
    )
    parser.add_argument("-m", "--market")

    # Simulation flags
    parser.add_argument("-s", "--scenario")
    parser.add_argument("-c", "--console", action="store_true")
    parser.add_argument("-p", "--pause", action="store_true")

    # Developer flags
    parser.add_argument("-g", "--graphql", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if args.scenario is not None:
        scenario: Scenario = SCENARIOS[args.scenario]()
    else:
        scenario: Scenario = DevOpsScenario(
            binance_code=None,
            market_manager_args=None,
            market_maker_args=None,
            auction_trader_args=None,
            random_trader_args=None,
            momentum_trader_args=None,
            sensitive_trader_args=None,
            simulation_args=None,
        )

    if args.agent is not None:
        agent: StateAgentWithWallet = AGENTS[args.agent]()
        agent.wallet_name = args.wallet_name
        agent.wallet_pass = args.wallet_pass
        agent.key_name = args.wallet_key

    if Network[args.network] == Network.NULLCHAIN:
        with VegaServiceNull(
            seconds_per_block=1,
            transactions_per_block=1000,
            retain_log_files=True,
            use_full_vega_wallet=False,
            warn_on_raw_data_access=False,
            run_with_console=args.console,
            launch_graphql=args.graphql,
            start_live_feeds=True,
        ) as vega:
            scenario.run_iteration(
                vega=vega,
                network=Network[args.network],
                pause_at_completion=args.pause,
                agent=agent,
                run_background=True,
            )

    else:
        with VegaServiceNetwork(
            network=Network[args.network],
            start_live_feeds=False,
        ) as vega:
            if agent is not None:
                agent.market_name = args.market
                agent.asset_name = vega.asset_info(
                    asset_id=vega.market_info(
                        vega.find_market_id(name=args.market, raise_on_missing=True)
                    ).tradable_instrument.instrument.future.settlement_asset
                ).details.symbol

            scenario.run_iteration(
                vega=vega,
                network=Network[args.network],
                pause_at_completion=args.pause,
                raise_datanode_errors=False,
                raise_step_errors=False,
                agent=agent,
                run_background=False,
            )


if __name__ == "__main__":
    main()
