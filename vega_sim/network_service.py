from typing import Dict, List, Optional, Set

import time
import subprocess

import toml

from os import getcwd, path

from vega_sim import vega_bin_path, vega_home_path
from vega_sim.service import VegaService
from vega_sim.wallet.base import Wallet
from vega_sim.wallet.slim_wallet import SlimWallet
from vega_sim.wallet.vega_wallet import VegaWallet


def start_wallet_service(network):

    wallet_args = [
        "vega",
        "wallet",
        "service",
        "run",
        "--network",
        network,
        "--automatic-consent",
    ]

    process = subprocess.Popen(args=wallet_args)

    return process


def add_network_config(network_config_path: str):

    wallet_args = [
        "vega",
        "wallet",
        "network",
        "import",
        "--from-file",
        network_config_path,
        "--force",
    ]

    process = subprocess.Popen(args=wallet_args)

    return process


class VegaServiceNetwork(VegaService):
    def __init__(
        self,
        network: str = "fairground",
        warn_on_raw_data_access: bool = False,
    ):
        super().__init__(
            can_control_time=False, warn_on_raw_data_access=warn_on_raw_data_access
        )
        self._wallet = None
        self._wallet_url = None
        self._data_node_grpc_url = None
        self.network = network
        self._network_config = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        self.process = start_wallet_service(self.network)

    def stop(self):
        self.process.kill()

    @property
    def network_config(self) -> str:
        if self._network_config is None:

            public_path = path.join(
                getcwd(),
                "vega_sim",
                "bin",
                "networks-internal",
                self.network,
                f"{self.network}.toml",
            )
            internal_path = path.join(
                getcwd(),
                "vega_sim",
                "bin",
                "networks",
                self.network,
                f"{self.network}.toml",
            )

            if path.exists(public_path):
                self._network_config = toml.load(public_path)
                process = add_network_config(public_path)
                time.sleep(3)
                process.kill()

            elif path.exists(internal_path):
                self._network_config = toml.load(internal_path)
                process = add_network_config(internal_path)
                time.sleep(3)
                process.kill()

            else:

                raise ValueError(f"ERROR! {self.network} network does not exist")

        return self._network_config

    @property
    def data_node_grpc_url(self) -> str:
        if self._data_node_grpc_url is None:
            self._data_node_grpc_url = self.network_config["API"]["GRPC"]["Hosts"][0]
        return self._data_node_grpc_url

    @property
    def wallet_url(self) -> str:
        if self._wallet_url is None:
            self._wallet_url = (
                f"http://{self.network_config['Host']}:{self.network_config['Port']}"
            )
        return self._wallet_url

    @property
    def wallet(self) -> Wallet:
        if self._wallet is None:
            self._wallet = VegaWallet(self.wallet_url)
        return self._wallet
