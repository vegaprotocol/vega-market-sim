import argparse
import datetime
import itertools
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

import vega_sim.proto.vega as vega_protos
from vega_sim.api.market import MarketConfig
from vega_sim.environment.environment import (
    MarketEnvironmentWithState,
)
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.common.agents import (
    ExponentialShapedMarketMaker,
    LimitOrderTrader,
    MarketOrderTrader,
    PriceSensitiveMarketOrderTrader,
    StateAgent,
    UncrossAuctionAgent,
)
from vega_sim.scenario.common.utils.price_process import random_walk
from vega_sim.scenario.configurable_market.agents import ConfigurableMarketManager
from vega_sim.scenario.constants import Network
from vega_sim.scenario.scenario import Scenario


class CFMScenario(Scenario):
    def __init__(
        self,
        num_steps: int = 60 * 24 * 30 * 3,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        step_length_seconds: Optional[float] = None,
        market_config: Optional[dict] = None,
        output: bool = True,
    ):
        super().__init__()

        self.market_config = market_config

        self.num_steps = num_steps
        self.step_length_seconds = (
            step_length_seconds
            if step_length_seconds is not None
            else block_length_seconds
        )

        self.block_length_seconds = block_length_seconds
        self.transactions_per_block = transactions_per_block

        self.output = output

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: str,
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> List[StateAgent]:
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

        self.agents = []
        self.initial_asset_mint = 10e9

        # Define the market and the asset:
        market_name = "CFM:Perp"
        asset_name = "USD"
        asset_dp = 18

        market_agents = {}
        # Create fuzzed market config
        market_config = MarketConfig()

        if self.market_config is not None:
            for param in self.market_config:
                market_config.set(param=self.market_config[param])

        i_market = 0
        # Create fuzzed price process
        price_process = random_walk(
            random_state=self.random_state,
            starting_price=1000,
            num_steps=self.num_steps,
            decimal_precision=int(market_config.decimal_places),
        )

        # Create fuzzed market managers
        market_agents["market_managers"] = [
            ConfigurableMarketManager(
                proposal_wallet_name="MARKET_MANAGER",
                proposal_key_name="PROPOSAL_KEY",
                termination_wallet_name="MARKET_MANAGER",
                termination_key_name="TERMINATION_KEY",
                market_config=market_config,
                market_name=market_name,
                market_code=market_name,
                asset_dp=asset_dp,
                asset_name=asset_name,
                settlement_price=price_process[-1],
                tag="MARKET",
            )
        ]

        market_agents["market_makers"] = [
            ExponentialShapedMarketMaker(
                wallet_name="MARKET_MAKERS",
                key_name=f"MARKET_{str(i_market).zfill(3)}",
                price_process_generator=iter(price_process),
                initial_asset_mint=self.initial_asset_mint,
                market_name=market_name,
                asset_name=asset_name,
                commitment_amount=1e6,
                market_decimal_places=market_config.decimal_places,
                asset_decimal_places=asset_dp,
                num_steps=self.num_steps,
                kappa=2.4,
                tick_spacing=0.05,
                market_kappa=50,
                state_update_freq=10,
                tag=f"MARKET_{str(i_market).zfill(3)}",
            )
        ]

        market_agents["auction_traders"] = [
            UncrossAuctionAgent(
                wallet_name="AUCTION_TRADERS",
                key_name=f"MARKET_{str(i_market).zfill(3)}_{side}",
                side=side,
                initial_asset_mint=self.initial_asset_mint,
                price_process=iter(price_process),
                market_name=market_name,
                asset_name=asset_name,
                uncrossing_size=20,
                tag=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
            )
            for i_agent, side in enumerate(["SIDE_BUY", "SIDE_SELL"])
        ]

        market_agents["random_traders"] = [
            MarketOrderTrader(
                wallet_name="RANDOM_TRADERS",
                key_name=(
                    f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
                ),
                market_name=market_name,
                asset_name=asset_name,
                buy_intensity=10,
                sell_intensity=10,
                base_order_size=1,
                step_bias=1,
                tag=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
            )
            for i_agent in range(5)
        ]

        # for i_agent in range(5):
        #     market_agents["random_traders"].append(
        #         LimitOrderTrader(
        #             wallet_name=f"RANDOM_TRADERS",
        #             key_name=(
        #                 f"LIMIT_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
        #             ),
        #             market_name=market_name,
        #             asset_name=asset_name,
        #             time_in_force_opts={"TIME_IN_FORCE_GTT": 1},
        #             buy_volume=1,
        #             sell_volume=1,
        #             buy_intensity=10,
        #             sell_intensity=10,
        #             submit_bias=1,
        #             cancel_bias=0,
        #             duration=120,
        #             price_process=price_process,
        #             spread=0,
        #             mean=-3,
        #             sigma=0.5,
        #             tag=(
        #                 f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
        #             ),
        #         )
        #     )

        for _, agent_list in market_agents.items():
            self.agents.extend(agent_list)

        return {agent.name(): agent for agent in self.agents}

    def configure_environment(
        self,
        vega: VegaServiceNull,
        **kwargs,
    ) -> MarketEnvironmentWithState:
        return MarketEnvironmentWithState(
            agents=list(self.agents.values()),
            n_steps=self.num_steps,
            random_agent_ordering=False,
            transactions_per_block=self.transactions_per_block,
            vega_service=vega,
            step_length_seconds=self.step_length_seconds,
            block_length_seconds=vega.seconds_per_block,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

    scenario = CFMScenario(
        num_steps=100,
        step_length_seconds=5,
        block_length_seconds=1,
        transactions_per_block=4096,
    )

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=False,
        use_full_vega_wallet=False,
        retain_log_files=True,
        launch_graphql=False,
        seconds_per_block=scenario.block_length_seconds,
        transactions_per_block=scenario.transactions_per_block,
    ) as vega:
        scenario.run_iteration(
            vega=vega, pause_at_completion=False, log_every_n_steps=100
        )
