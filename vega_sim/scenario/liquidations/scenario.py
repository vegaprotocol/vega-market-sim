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
from vega_sim.scenario.common.agents import ExponentialShapedMarketMaker
from vega_sim.scenario.common.agents import (
    StateAgent,
    UncrossAuctionAgent,
    ExponentialShapedMarketMaker,
)
from vega_sim.scenario.configurable_market.agents import ConfigurableMarketManager
from vega_sim.scenario.fuzzed_markets.agents import (
    RiskyMarketOrderTrader,
)


def _create_price_process(
    random_state: np.random.RandomState, num_steps, decimal_places
):
    price_process = [1500]

    while len(price_process) < num_steps + 1:
        # Add a stable price-process with a random duration of 5-20% of the sim
        price_process = np.concatenate(
            (
                price_process,
                random_walk(
                    num_steps=random_state.randint(
                        int(0.05 * num_steps), int(0.20 * num_steps)
                    ),
                    sigma=2,
                    starting_price=price_process[-1],
                    decimal_precision=decimal_places,
                ),
            )
        )
        # Add an unstable price-process with a random duration of 5-10% of the sim
        price_process = np.concatenate(
            (
                price_process,
                random_walk(
                    num_steps=random_state.randint(
                        int(0.05 * num_steps), int(0.10 * num_steps)
                    ),
                    sigma=2,
                    drift=random_state.uniform(-1, 1),
                    starting_price=price_process[-1],
                    decimal_precision=decimal_places,
                ),
            )
        )

    # Add spikes to the price monitoring auction
    spike_at = random_state.randint(0, num_steps, size=3)
    for i in spike_at:
        price_process[i] = price_process[i] * random_state.choice([0.95, 1.05])

    return price_process


class LiquidationScenario(Scenario):
    def __init__(
        self,
        num_steps: int = 60 * 24 * 30 * 3,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        step_length_seconds: Optional[float] = None,
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

        market_name = "ETH/USDT Expiry 2023 Sept 30th"
        market_code = "ETH/USDT-230930"
        asset_name = "USDT"
        asset_dp = 18

        self.agents = []
        self.initial_asset_mint = 10e9

        market_config = MarketConfig()

        # Create fuzzed price process
        price_process = _create_price_process(
            random_state=self.random_state,
            num_steps=self.num_steps,
            decimal_places=int(market_config.decimal_places),
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
                tag="MARKET_MAKER",
            )
        )

        agents.extend(
            [
                UncrossAuctionAgent(
                    key_name=f"AGENT_{str(i_agent).zfill(3)}",
                    side=side,
                    initial_asset_mint=self.initial_asset_mint,
                    price_process=iter(price_process),
                    market_name=market_name,
                    asset_name=asset_name,
                    uncrossing_size=20,
                    tag=(f"AGENT_{str(i_agent).zfill(3)}"),
                )
                for i_agent, side in enumerate(["SIDE_BUY", "SIDE_SELL"])
            ]
        )

        agents.extend(
            [
                RiskyMarketOrderTrader(
                    key_name=f"SIDE_{side}_AGENT_{str(i_agent).zfill(3)}",
                    market_name=market_name,
                    asset_name=asset_name,
                    side=side,
                    initial_asset_mint=1_000,
                    size_factor=0.6,
                    step_bias=0.1,
                    tag=f"SIDE_{side}_AGENT_{str(i_agent).zfill(3)}",
                )
                for side in ["SIDE_BUY", "SIDE_SELL"]
                for i_agent in range(10)
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
