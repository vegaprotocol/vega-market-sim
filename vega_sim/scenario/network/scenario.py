"""network.py

Module for running a predefined scenario on a Vega network.
"""

import os
import dotenv
import argparse
import logging
from random import random
import numpy as np
from typing import Any, Callable, List, Optional
from vega_sim.environment.agent import Agent

from vega_sim.scenario.scenario import Scenario
from vega_sim.environment.environment import NetworkEnvironment
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.scenario.constants import Network
from vega_sim.scenario.common.agents import (
    MarketOrderTrader,
    LimitOrderTrader,
)


class Fairground(Scenario):
    def __init__(
        self,
        num_steps: int = 5,
        step_length_seconds: int = 1,
        market_name: str = None,
    ):

        dotenv.load_dotenv()
        self.wallet_name = os.environ.get("VEGA_USER_WALLET_NAME")
        self.wallet_pass = os.environ.get("VEGA_USER_WALLET_PASS")

        self.num_steps = num_steps
        self.step_length_seconds = step_length_seconds

        self.market_name = market_name
        self.market_id = None
        self.asset_name = None

        self.random_state = np.random.RandomState()

    def set_up_background_market(
        self,
        vega: VegaServiceNetwork,
        tag: str = "",
        random_state: Optional[np.random.RandomState] = None,
    ) -> NetworkEnvironment:

        self.market_id = [
            m.id
            for m in vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]
        market_info = vega.market_info(market_id=self.market_id)
        self.asset_name = (
            market_info.tradable_instrument.instrument.future.settlement_asset
        )

        mo_trader = MarketOrderTrader(
            wallet_name=self.wallet_name,
            wallet_pass=self.wallet_pass,
            market_name=self.market_name,
            asset_name=self.asset_name,
            tag=str(tag),
            buy_intensity=200,
            sell_intensity=200,
            base_order_size=0.01,
            random_state=random_state,
        )

        lo_trader = LimitOrderTrader(
            wallet_name=self.wallet_name,
            wallet_pass=self.wallet_pass,
            market_name=self.market_name,
            asset_name=self.asset_name,
            tag=str(tag),
            random_state=random_state,
            side_opts={"SIDE_BUY": 0.5, "SIDE_SELL": 0.5},
            time_in_force_opts={"TIME_IN_FORCE_GTC": 1.0},
            buy_intensity=200,
            sell_intensity=200,
            buy_volume=0.01,
            sell_volume=0.01,
            mean=-5,
            sigma=0.5,
        )

        env = NetworkEnvironment(
            agents=[
                mo_trader,
                lo_trader,
            ],
            n_steps=self.num_steps,
            vega_service=vega,
            step_length_seconds=self.step_length_seconds,
        )

        return env

    def run_iteration(
        self,
        vega: VegaServiceNetwork,
        network: Optional[Network] = None,
        random_state: Optional[np.random.RandomState] = None,
    ):
        env = self.set_up_background_market(
            vega=vega, tag="", random_state=random_state
        )
        result = env.run()
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--network")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

    scenario = Fairground(
        num_steps=200,
        step_length_seconds=1,
        market_name="UNIDAI Monthly (30 Jun 2022)",
    )

    with VegaServiceNetwork(
        network=("fairground" if args.network is None else args.network),
        automatic_consent=True,
        no_version_check=True,
    ) as vega:
        scenario.run_iteration(vega=vega)
