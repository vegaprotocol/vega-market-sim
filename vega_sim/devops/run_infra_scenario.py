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

    $ python -m vega_sim.devops.run_infra_scenario -s ETHUSD -n NULLCHAIN -d -c -p


"""
import os
import argparse
import logging


from vega_sim.wallet.process import VegaWallet 
from vega_sim.scenario.constants import Network

from vega_sim.network_service import VegaServiceNetwork

from vega_sim.devops.scenario import DevOpsScenario
from vega_sim.devops.registry import SCENARIOS


import multiprocessing
import subprocess

def run_wallet(bin_path: str):
    logger = logging.getLogger("vegawallet")

    wallet_args = (
        bin_path, 
        "service",
        "run",
        "--network",
        "mainnet-mirror",
        "--load-tokens",
        "--automatic-consent",
        "--tokens-passphrase-file",
        "/home/daniel/www/vega-market-sim/wallet-passphrase.txt",
    )

    wallet_process = subprocess.Popen(
        wallet_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    with wallet_process.stdout:
        for line in iter(wallet_process.stdout.readline, b''):
            logger.info(line.decode("utf-8").strip())

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
    parser.add_argument("-w", "--with-wallet")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    scenario: DevOpsScenario = SCENARIOS[args.scenario]()

    scenario.market_name = args.market_name
    scenario.step_length_seconds = args.step_length_seconds

    network_name = str(args.network).lower().replace('_', '-')
    wallet_binary = os.getenv('VEGA_WALLET_PATH')
    wallet_home = os.getenv('VEGA_WALLET_HOME')
    wallet_name = os.getenv('VEGA_USER_WALLET_NAME')
    wallet_passphrase_file = os.getenv('VEGA_WALLET_TOKENS_PASSPHRASE_FILE')

    wallet = VegaWallet(wallet_binary, network_name, wallet_passphrase_file, wallet_home)
    wallet.check_wallet(wallet_name)

    process = wallet.background_run()


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

    process.terminate()


if __name__ == "__main__":
    main()
