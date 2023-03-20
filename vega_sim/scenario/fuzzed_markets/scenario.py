from vega_sim.api.market import MarketConfig

import argparse
import logging
import numpy as np
from typing import Optional, List
from vega_sim.scenario.common.utils.price_process import random_walk

from vega_sim.scenario.scenario import Scenario
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull

from vega_sim.scenario.configurable_market.agents import ConfigurableMarketManager
from vega_sim.scenario.common.agents import (
    StateAgent,
    OpenAuctionPass,
    ExponentialShapedMarketMaker,
    MarketOrderTrader,
)
from vega_sim.scenario.fuzzed_markets.agents import (
    FuzzingAgent,
    DegenerateTrader,
    DegenerateLiquidityProvider,
    FuzzyLiquidityProvider,
)

import datetime
from typing import Optional, Dict
from dataclasses import dataclass
from vega_sim.scenario.common.agents import ExponentialShapedMarketMaker
import pandas as pd


@dataclass
class MarketHistoryAdditionalData:
    at_time: datetime.datetime
    external_prices: Dict[str, float]
    trader_close_outs: Dict[str, int]
    liquidity_provider_close_outs: Dict[str, int]


def state_extraction_fn(vega: VegaServiceNull, agents: dict):
    at_time = vega.get_blockchain_time()

    external_prices = {}
    trader_close_outs = {}
    liquidity_provider_close_outs = {}

    for _, agent in agents.items():
        if isinstance(agent, ExponentialShapedMarketMaker):
            external_prices[agent.market_id] = agent.curr_price
        if isinstance(agent, DegenerateTrader):
            trader_close_outs[agent.market_id] = (
                trader_close_outs.get(agent.market_id, 0) + agent.close_outs
            )
        if isinstance(agent, DegenerateLiquidityProvider):
            liquidity_provider_close_outs[agent.market_id] = (
                liquidity_provider_close_outs.get(agent.market_id, 0) + agent.close_outs
            )

    return MarketHistoryAdditionalData(
        at_time=at_time,
        external_prices=external_prices,
        trader_close_outs=trader_close_outs,
        liquidity_provider_close_outs=liquidity_provider_close_outs,
    )


def additional_data_to_rows(data) -> List[pd.Series]:
    results = []
    for market_id in data.external_prices.keys():
        results.append(
            {
                "time": data.at_time,
                "market_id": market_id,
                "external_price": data.external_prices.get(market_id, np.NaN),
                "trader_close_outs": data.trader_close_outs.get(market_id, 0),
                "liquidity_provider_close_outs": data.liquidity_provider_close_outs.get(
                    market_id, 0
                ),
            }
        )
    return results


class FuzzingScenario(Scenario):
    def __init__(
        self,
        num_steps: int = 60 * 24 * 30 * 3,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        n_markets: int = 5,
        step_length_seconds: Optional[float] = None,
        fuzz_market_config: Optional[dict] = None,
    ):
        super().__init__()

        self.n_markets = n_markets
        self.fuzz_market_config = fuzz_market_config

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
        random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

        market_managers = []
        market_makers = []
        auction_traders = []
        random_traders = []
        fuzz_traders = []
        degenerate_traders = []
        fuzz_liquidity_providers = []
        degenerate_liquidity_providers = []

        self.initial_asset_mint = 1e9

        for i_market in range(self.n_markets):
            # Define the market and the asset:
            market_name = f"ASSET_{str(i_market).zfill(3)}"
            asset_name = f"ASSET_{str(i_market).zfill(3)}"
            asset_dp = 18

            # Create fuzzed market config
            market_config = MarketConfig()
            if self.fuzz_market_config is not None:
                for param in self.fuzz_market_config:
                    market_config.set(param=self.fuzz_market_config[param])

            # Create fuzzed price process
            price_process = random_walk(
                num_steps=self.num_steps + 1,
                sigma=random_state.rand(),
                drift=random_state.rand() * 1e-3,
                starting_price=1000,
                decimal_precision=int(market_config.decimal_places),
            )

            # Create fuzzed market managers
            market_managers.append(
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
                    tag=f"MARKET_{str(i_market).zfill(3)}",
                )
            )

            market_makers.append(
                ExponentialShapedMarketMaker(
                    wallet_name="MARKET_MAKERS",
                    key_name=f"MARKET_{str(i_market).zfill(3)}",
                    price_process_generator=iter(price_process),
                    initial_asset_mint=self.initial_asset_mint,
                    market_name=market_name,
                    asset_name=asset_name,
                    commitment_amount=1e6,
                    market_decimal_places=market_config.decimal_places,
                    asset_decimal_places=asset_name,
                    num_steps=self.num_steps,
                    kappa=0.6,
                    tick_spacing=0.1,
                    market_kappa=20,
                    state_update_freq=10,
                    tag=f"MARKET_{str(i_market).zfill(3)}",
                )
            )

            for i_agent, side in enumerate(["SIDE_BUY", "SIDE_SELL"]):
                auction_traders.append(
                    OpenAuctionPass(
                        wallet_name=f"AUCTION_TRADERS",
                        key_name=f"MARKET_{str(i_market).zfill(3)}_{side}",
                        side=side,
                        initial_asset_mint=self.initial_asset_mint,
                        initial_price=price_process[0],
                        market_name=market_name,
                        asset_name=asset_name,
                        opening_auction_trade_amount=1,
                        tag=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                    )
                )

            for i_agent in range(5):
                random_traders.append(
                    MarketOrderTrader(
                        wallet_name=f"RANDOM_TRADERS",
                        key_name=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                        market_name=market_name,
                        asset_name=asset_name,
                        buy_intensity=10,
                        sell_intensity=10,
                        base_order_size=1,
                        step_bias=1,
                        tag=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                    )
                )

            for i_agent in range(10):
                fuzz_traders.append(
                    FuzzingAgent(
                        wallet_name="FUZZING_TRADERS",
                        key_name=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                        market_name=market_name,
                        asset_name=asset_name,
                        tag=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                    )
                )

            for side in ["SIDE_BUY", "SIDE_SELL"]:
                for i_agent in range(10):
                    degenerate_traders.append(
                        DegenerateTrader(
                            wallet_name="DEGENERATE_TRADERS",
                            key_name=f"MARKET_{str(i_market).zfill(3)}_SIDE_{side}_AGENT_{str(i_agent).zfill(3)}",
                            market_name=market_name,
                            asset_name=asset_name,
                            side=side,
                            initial_asset_mint=5_000,
                            size_factor=0.7,
                            tag=f"MARKET_{str(i_market).zfill(3)}_SIDE_{side}_AGENT_{str(i_agent).zfill(3)}",
                        )
                    )

            for i_agent in range(5):
                degenerate_liquidity_providers.append(
                    DegenerateLiquidityProvider(
                        wallet_name="DEGENERATE_LIQUIDITY_PROVIDERS",
                        key_name=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                        market_name=market_name,
                        asset_name=asset_name,
                        initial_asset_mint=5_000,
                        commitment_factor=0.7,
                        tag=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                    )
                )

            for i_agent in range(5):
                fuzz_liquidity_providers.append(
                    FuzzyLiquidityProvider(
                        wallet_name="FUZZY_LIQUIDITY_PROVIDERS",
                        key_name=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                        market_name=market_name,
                        asset_name=asset_name,
                        initial_asset_mint=5_000,
                        tag=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                    )
                )

        agents = (
            market_managers
            + market_makers
            + auction_traders
            + random_traders
            + fuzz_traders
            + degenerate_traders
            + degenerate_liquidity_providers
            + fuzz_liquidity_providers
        )
        return {agent.name(): agent for agent in agents}

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

    scenario = FuzzingScenario(
        num_steps=10000,
        step_length_seconds=5,
        block_length_seconds=1,
        transactions_per_block=4096,
    )

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=True,
        use_full_vega_wallet=False,
        retain_log_files=True,
        launch_graphql=True,
        seconds_per_block=scenario.block_length_seconds,
        transactions_per_block=scenario.transactions_per_block,
    ) as vega:
        scenario.run_iteration(
            vega=vega,
            pause_at_completion=False,
        )
