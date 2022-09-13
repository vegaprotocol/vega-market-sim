from typing import Dict, List, Optional, Set

import requests
import toml
from urllib3.exceptions import MaxRetryError

from vega_sim import vega_bin_path, vega_home_path
from vega_sim.service import VegaService
from vega_sim.wallet.base import Wallet
from vega_sim.wallet.slim_wallet import SlimWallet
from vega_sim.wallet.vega_wallet import VegaWallet


class VegaServiceFairground(VegaService):
    def __init__(
        self,
        use_full_vega_wallet: bool = True,
    ):
        super().__init__(
            can_control_time=False,
        )

        self._wallet = None
        self._use_full_vega_wallet = use_full_vega_wallet

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    @property
    def data_node_grpc_url(self) -> str:
        return "api.n07.testnet.vega.xyz:3007"

    @property
    def wallet_url(self) -> str:
        return "http://127.0.0.1:1789"


    @property
    def wallet(self) -> Wallet:
        if self._wallet is None:
            if self._use_full_vega_wallet:
                self._wallet = VegaWallet(self.wallet_url)
            else:
                self._wallet = SlimWallet(
                    self.core_client,
                    full_wallet=VegaWallet(self.wallet_url)
                    if self.run_with_console
                    else None,
                )
        return self._wallet
