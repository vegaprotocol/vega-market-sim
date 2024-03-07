from vega_sim.api.market import MarketConfig

import argparse
import logging
import numpy as np
from typing import Optional, List
from vega_sim.scenario.common.utils.price_process import random_walk

from vega_sim.scenario.scenario import Scenario
from vega_sim.environment.environment import (
    MarketEnvironmentWithState,
    NetworkEnvironment,
)
from vega_sim.scenario.constants import Network
from vega_sim.null_service import VegaServiceNull

# Import agents
from vega_sim.scenario.configurable_market.agents import ConfigurableMarketManager
from vega_sim.scenario.common.agents import (
    StateAgent,
    ExponentialShapedMarketMaker,
    UncrossAuctionAgent,
    MarketOrderTrader,
    LimitOrderTrader,
)
from vega_sim.scenario.fuzzed_markets.agents import (
    RiskyMarketOrderTrader,
)


class LiquidationScenario(Scenario):
    def __init__(
        self,
        num_steps: int = 60 * 24 * 30 * 3,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        step_length_seconds: Optional[float] = None,
        disposal_time_step: Optional[int] = None,
        disposal_fraction: Optional[float] = None,
        full_disposal_size: Optional[int] = None,
        max_fraction_consumed: Optional[float] = None,
        supplied_liquidity: float = 1e6,
        number_risky_traders: int = 5,
        mint_risky_traders: float = 1e3,
        price_sigma: Optional[float] = 1,
        price_drift: Optional[float] = 0,
    ):
        super().__init__()
        self.num_steps = num_steps
        self.step_length_seconds = (
            step_length_seconds
            if step_length_seconds is not None
            else block_length_seconds
        )
        self.block_length_seconds = block_length_seconds
        self.transactions_per_block = transactions_per_block

        self.disposal_time_step = disposal_time_step
        self.disposal_fraction = disposal_fraction
        self.full_disposal_size = full_disposal_size
        self.max_fraction_consumed = max_fraction_consumed

        self.supplied_liquidity = supplied_liquidity
        self.number_risky_traders = number_risky_traders
        self.mint_risky_traders = mint_risky_traders

        self.price_sigma = price_sigma
        self.price_drift = price_drift

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

        # Create market configuration
        market_config = MarketConfig("future")
        market_name = "ETH/USDT Expiry 2023 Sept 30th"
        market_code = "ETH/USDT-230930"
        asset_name = "USDT"
        asset_dp = 18
        for key, value in [
            ("liquidation_strategy.disposal_time_step", self.disposal_time_step),
            ("liquidation_strategy.disposal_fraction", self.disposal_fraction),
            ("liquidation_strategy.full_disposal_size", self.full_disposal_size),
            ("liquidation_strategy.max_fraction_consumed", self.max_fraction_consumed),
        ]:
            if value is not None:
                market_config.set(key, value)
        # Create price process for market
        price_process = random_walk(
            num_steps=self.num_steps,
            sigma=self.price_sigma,
            drift=self.price_drift,
            starting_price=1000,
            decimal_precision=market_config.decimal_places,
        )

        agents: List[StateAgent] = []
        agents.append(
            ConfigurableMarketManager(
                proposal_key_name="PROPOSAL_KEY",
                termination_key_name="TERMINATION_KEY",
                market_config=market_config,
                market_name=market_name,
                market_code=market_code,
                asset_dp=asset_dp,
                asset_name=asset_name,
                settlement_price=price_process[-1],
                tag=f"MARKET_MANAGER",
            )
        )

        agents.append(
            ExponentialShapedMarketMaker(
                key_name="MARKET_MAKER",
                price_process_generator=iter(price_process),
                initial_asset_mint=self.supplied_liquidity * 10,
                market_name=market_name,
                asset_name=asset_name,
                commitment_amount=self.supplied_liquidity,
                market_decimal_places=market_config.decimal_places,
                asset_decimal_places=asset_dp,
                num_steps=self.num_steps,
                kappa=2.4,
                tick_spacing=0.1,
                market_kappa=50,
                state_update_freq=10,
                tag="MARKET_MAKER",
            )
        )

        agents.extend(
            [
                UncrossAuctionAgent(
                    key_name=f"UA_AGENT_{str(i_agent).zfill(3)}",
                    side=side,
                    initial_asset_mint=1e6,
                    price_process=iter(price_process),
                    market_name=market_name,
                    asset_name=asset_name,
                    uncrossing_size=20,
                    tag=str(i_agent).zfill(3),
                )
                for i_agent, side in enumerate(["SIDE_BUY", "SIDE_SELL"])
            ]
        )
        agents.extend(
            [
                MarketOrderTrader(
                    key_name=f"MO_AGENT_{str(i_agent).zfill(3)}",
                    market_name=market_name,
                    asset_name=asset_name,
                    buy_intensity=10,
                    sell_intensity=10,
                    base_order_size=0.01,
                    step_bias=0.1,
                    tag=str(i_agent).zfill(3),
                )
                for i_agent in range(10)
            ]
        )
        agents.extend(
            [
                LimitOrderTrader(
                    key_name=f"LO_AGENT_{str(i_agent).zfill(3)}",
                    market_name=market_name,
                    asset_name=asset_name,
                    time_in_force_opts={"TIME_IN_FORCE_GTT": 1},
                    buy_volume=0.001,
                    sell_volume=0.001,
                    buy_intensity=10,
                    sell_intensity=10,
                    submit_bias=1,
                    cancel_bias=0,
                    duration=120,
                    price_process=price_process,
                    spread=0,
                    mean=-3,
                    sigma=0.5,
                    initial_asset_mint=1e9,
                    tag=str(i_agent).zfill(3),
                )
                for i_agent in range(10)
            ]
        )
        agents.extend(
            [
                RiskyMarketOrderTrader(
                    key_name=f"RO_AGENT_{str(i_agent).zfill(3)}_SIDE_{side}",
                    market_name=market_name,
                    asset_name=asset_name,
                    side=side,
                    initial_asset_mint=self.mint_risky_traders,
                    leverage_factor=0.5,
                    step_bias=0.1,
                    tag=f"{side}_{str(i_agent).zfill(3)}",
                )
                for side in ["SIDE_BUY", "SIDE_SELL"]
                for i_agent in range(self.number_risky_traders)
            ]
        )
        return {agent.name(): agent for agent in agents}

    def configure_environment(
        self,
        vega: VegaServiceNull,
        **kwargs,
    ) -> MarketEnvironmentWithState:
        if kwargs.get("network", Network.NULLCHAIN) == Network.NULLCHAIN:
            return MarketEnvironmentWithState(
                agents=list(self.agents.values()),
                n_steps=self.num_steps,
                random_agent_ordering=False,
                transactions_per_block=self.transactions_per_block,
                vega_service=vega,
                step_length_seconds=self.step_length_seconds,
                block_length_seconds=vega.seconds_per_block,
            )
        else:
            return NetworkEnvironment(
                agents=list(self.agents.values()),
                n_steps=self.num_steps,
                vega_service=vega,
                step_length_seconds=self.step_length_seconds,
                raise_datanode_errors=kwargs.get("raise_datanode_errors", False),
                raise_step_errors=kwargs.get("raise_step_errors", False),
                random_state=self.random_state,
                create_keys=True,
                mint_keys=True,
            )
