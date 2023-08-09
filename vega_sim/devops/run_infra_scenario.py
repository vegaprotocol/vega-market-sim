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


from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("OK", "utf-8"))

def health_check():
    webServer = HTTPServer(("0.0.0.0", 80), MyServer)
    print("Server started %s:%s" % ("0.0.0.0", 80))
    webServer.serve_forever()
    
    webServer.server_close()
    print("Server stopped.")

    
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

    t = threading.Thread(target=health_check)
    t.start()
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

    t.join()

if __name__ == "__main__":
    main()
