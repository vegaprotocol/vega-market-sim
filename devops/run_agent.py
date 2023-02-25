"""run.py

Script used to run vega-market-sim agents on a nullchain network or on a live network.

Flags:

    -a, --agent                 controls which agent to run
    -k, --key                   controls which key to use
    -n, --network string        controls which network the agent is run on
    -m, --market_name           controls which market the agent is run on
    -l, --step_length_seconds   controls the frequency at which the agent steps
    -s, --scenario              scenario to use for testing simulations

    -d, --debug                 controls whether to log debug messages
    -c, --console               whether to launch a console
    -g, --graphql               whether to launch a graphql playground 
    -p, --pause                 whether to pause a the end of a simulation

"""

import os
import dotenv
import argparse
import logging

from vega_sim.scenario.constants import Network

from vega_sim.null_service import VegaServiceNull
from vega_sim.network_service import VegaServiceNetwork

from vega_sim.scenario.scenario import Scenario
from vega_sim.environment.agent import StateAgentWithWallet

from devops.scenario import DevOpsScenario
from devops.classes import SimulationArgs
from devops.registry import SCENARIOS, AGENTS


def main():
    parser = argparse.ArgumentParser()

    # Simulation / deployment arguments
    parser.add_argument("-a", "--agent")
    parser.add_argument("-k", "--key")
    parser.add_argument("-l", "--step_length_seconds", default=10, type=int)
    parser.add_argument(
        "-n",
        "--network",
        choices=[network.name for network in Network],
        default=Network.FAIRGROUND.name,
    )
    parser.add_argument("-m", "--market_name", default=None, type=str)
    parser.add_argument("-s", "--scenario")

    # Developer flags
    parser.add_argument("-p", "--pause", action="store_true")
    parser.add_argument("-c", "--console", action="store_true")
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
            sensitive_trader_args=None,
            simulation_args=SimulationArgs(
                n_steps=None,
                granularity=None,
                coinbase_code=None,
            ),
        )
    scenario.market_name = args.market_name
    scenario.step_length_seconds = args.step_length_seconds

    if args.agent is not None:
        agent: StateAgentWithWallet = AGENTS[args.agent]()

        dotenv.load_dotenv()
        agent.wallet_name = os.environ.get("VEGA_USER_WALLET_NAME", "")
        agent.key_name = args.key
        agent.market_name = scenario.market_name

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
                agent=agent,
                run_background=True,
            )

    else:
        with VegaServiceNetwork(
            network=Network[args.network],
            run_with_console=args.console,
        ) as vega:
            if agent is not None:
                agent.asset_name = vega.asset_info(
                    asset_id=vega.market_info(
                        vega.find_market_id(
                            name=agent.market_name, raise_on_missing=True
                        )
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
