from typing import Dict, List, Optional, Set

import time
import subprocess

from os import path

from vega_sim import vega_bin_path, vega_home_path
from vega_sim.service import VegaService
from vega_sim.wallet.base import Wallet
from vega_sim.wallet.slim_wallet import SlimWallet
from vega_sim.wallet.vega_wallet import VegaWallet


def start_wallet_service():

    wallet_args = [
        "vega",
        "wallet",
        "service",
        "run",
        "--network",
        "fairground",
        "--automatic-consent",
    ]

    process = subprocess.Popen(args=wallet_args)

    return process


class VegaServiceFairground(VegaService):
    def __init__(
        self,
        warn_on_raw_data_access: bool = False,
    ):
        super().__init__(
            can_control_time=False, warn_on_raw_data_access=warn_on_raw_data_access
        )
        self._wallet = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        self.process = start_wallet_service()

    def stop(self):
        self.process.kill()

    @property
    def data_node_grpc_url(self) -> str:
        return "api.n09.testnet.vega.xyz:3007"

    @property
    def wallet_url(self) -> str:
        return "http://127.0.0.1:1789"

    @property
    def wallet(self) -> Wallet:
        if self._wallet is None:
            self._wallet = VegaWallet(self.wallet_url)
        return self._wallet
