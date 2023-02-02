"""scenario.py

Module contains the ParameterExperiment scenario class, which simulates a scenario for
use in network parameter and market parameter experiments. The scenario uses the
following suite of vega-market-sim agents.

- ConfigurableMarketManager:        proposes and settles a fully configurable market.
- ExponentialShapedMarketMaker:     provides liquidity and an order book in the market.
- RandomMarketOrderTrader:          trades each side of the book every step.
- PriceSensitiveLimitOrderTrader:   trades on orders close to an external price.
- InformedTrader:                   trades on orders which will be in-the-money soon.

"""

import numpy as np

from datetime import datetime, timedelta
from typing import Any, Dict, Callable, Optional

from vega_sim.api.market import MarketConfig
from vega_sim.scenario.scenario import Scenario
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull

from vega_sim.environment.agent import Agent
from vega_sim.scenario.configurable_market.scenario import ConfigurableMarketManager
from vega_sim.scenario.common.agents import (
    OpenAuctionPass,
    MarketOrderTrader,
    ExponentialShapedMarketMaker,
    PriceSensitiveLimitOrderTrader,
    InformedTrader,
    StateAgent,
    SimpleLiquidityProvider,
)

from vega_sim.scenario.common.utils.price_process import (
    Granularity,
    get_historic_price_series,
)


class ParameterExperiment(Scenario):
    """Class simulates a scenario for use in parameter experiments.

    The default values for the ParameterExperiment scenario are to simulate an hours
    trading activity in 10 second intervals.

    """

    def __init__(
        self,
        num_steps: int = 600,
        step_length_seconds=10,
        granularity: Optional[Granularity] = Granularity.MINUTE,
        block_size: int = 100,
        block_length_seconds: int = 1,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, Dict[str, Agent]], Any]
        ] = None,
        settle_at_end: bool = True,
        price_process_fn: Optional[Callable] = None,
        market_name: Optional[str] = "ETH:USD (6hr Future)",
        market_code: str = "ETHUSD",
        asset_name: str = "ETH",
        asset_dp: str = 18,
        rt_mint: int = 100_000,
        it_mint: int = 100_000,
        st_mint: int = 1_000_000,
    ):
        super().__init__(state_extraction_fn=state_extraction_fn)

        # Simulation settings
        self.num_steps = num_steps
        self.step_length_seconds = step_length_seconds
        self.granularity = granularity
        self.interpolation = (
            f"{step_length_seconds}S"
            if step_length_seconds < granularity.value
            else None
        )
        self.block_size = block_size
        self.block_length_seconds = block_length_seconds
        self.settle_at_end = settle_at_end
        self.price_process_fn = price_process_fn

        # Asset info parameters
        self.asset_name = asset_name
        self.asset_decimal = asset_dp

        # Market info parameters
        self.market_name = market_name
        self.market_code = market_code

        # Agent mint parameters
        self.rt_mint = rt_mint
        self.st_mint = st_mint
        self.it_mint = it_mint

    def _generate_price_process(
        self,
        random_state: np.random.RandomState,
    ) -> list:
        # Select a random start and end datetime
        start = datetime.strptime(
            "2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
        ) + timedelta(days=int(random_state.choice(range(90))))
        end = start + timedelta(seconds=(self.num_steps + 1) * self.granularity.value)

        # Get the historic price process between the randomly generated dates
        price_process = get_historic_price_series(
            product_id="ETH-USD",
            granularity=self.granularity,
            interpolation=self.interpolation,
            start=str(start),
            end=str(end),
        )

        return list(price_process)

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: str,
        market_config: Optional[MarketConfig] = None,
        random_state: Optional[np.random.RandomState] = None,
    ) -> Dict[str, StateAgent]:
        market_config = market_config if market_config is not None else MarketConfig()

        random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

        market_name = self.market_name
        asset_name = self.asset_name

        price_process = (
            self.price_process_fn()
            if self.price_process_fn is not None
            else self._generate_price_process(random_state=random_state)
        )

        market_manager = ConfigurableMarketManager(
            proposal_wallet_name="vega",
            proposal_wallet_pass="pass",
            proposal_key_name="market_proposer",
            termination_wallet_name="vega",
            termination_wallet_pass="pass",
            termination_key_name="market_settler",
            market_config=market_config,
            market_name=market_name,
            market_code=self.market_code,
            asset_dp=self.asset_decimal,
            asset_name=asset_name,
            settlement_price=price_process[-1] if self.settle_at_end else None,
            tag=None,
        )

        market_maker = ExponentialShapedMarketMaker(
            wallet_name="vega",
            wallet_pass="pass",
            key_name="market_maker",
            price_process_generator=iter(price_process),
            initial_asset_mint=1e10,
            commitment_amount=1_000_000,
            fee_amount=0.001,
            market_name=market_name,
            asset_name=asset_name,
            market_decimal_places=market_config.decimal_places,
            asset_decimal_places=self.asset_decimal,
            num_steps=self.num_steps,
            kappa=5,
            num_levels=20,
            tick_spacing=0.01,
            inventory_upper_boundary=20,
            inventory_lower_boundary=-20,
            market_kappa=5,
            market_order_arrival_rate=0.5,
            state_update_freq=10,
            tag=None,
            orders_from_stream=True,
        )

        simple_liquidity_providers = [
            SimpleLiquidityProvider(
                wallet_name="vega",
                wallet_pass="pass",
                key_name="simple_lp_c",
                market_name=market_name,
                asset_name=asset_name,
                initial_asset_mint=1e10,
                commitment_amount=100_000,
                bid_inner_bound_fn=lambda vega_state, market_id: vega_state.market_state[
                    market_id
                ].midprice,
                bid_outer_bound_fn=lambda vega_state, market_id: vega_state.market_state[
                    market_id
                ].min_valid_price,
                ask_inner_bound_fn=lambda vega_state, market_id: vega_state.market_state[
                    market_id
                ].midprice,
                ask_outer_bound_fn=lambda vega_state, market_id: vega_state.market_state[
                    market_id
                ].max_valid_price,
                offset_proportion=0.06,
                fee=0.001,
            )
            for i, offset in enumerate([0.02, 0.04, 0.06])
        ]

        # Create fixed auction pass agents
        open_auction_pass_bid = OpenAuctionPass(
            wallet_name="vega",
            wallet_pass="pass",
            key_name="auction_trader_bid",
            side="SIDE_BUY",
            initial_asset_mint=1e9,
            initial_price=price_process[0],
            market_name=market_name,
            asset_name=asset_name,
            opening_auction_trade_amount=market_config.position_decimal_places,
            tag="bid",
        )
        open_auction_pass_ask = OpenAuctionPass(
            wallet_name="vega",
            wallet_pass="pass",
            key_name="auction_trader_ask",
            side="SIDE_SELL",
            initial_asset_mint=1e9,
            initial_price=price_process[0],
            market_name=market_name,
            asset_name=asset_name,
            opening_auction_trade_amount=market_config.position_decimal_places,
            tag="ask",
        )

        informed_trader = InformedTrader(
            wallet_name="vega",
            wallet_pass="pass",
            key_name="informed_trade",
            price_process=price_process,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=self.it_mint,
            proportion_taken=0.05,
            lookahead=5,
            accuracy=0.8,
            max_abs_position=20,
            tag=None,
            random_state=random_state,
        )

        random_traders = [
            MarketOrderTrader(
                wallet_name="vega",
                wallet_pass="pass",
                key_name=f"random_trader_{i}",
                market_name=market_name,
                asset_name=asset_name,
                initial_asset_mint=self.rt_mint,
                base_order_size=0.1,
                buy_intensity=buy_intensity,
                sell_intensity=sell_intensity,
                tag=str(i),
                random_state=random_state,
            )
            for i, (buy_intensity, sell_intensity) in enumerate(
                [(50, 10), (30, 30), (30, 30), (30, 30), (10, 50)]
            )
        ]

        # Create fixed sensitive_traders
        sensitive_traders = [
            PriceSensitiveLimitOrderTrader(
                wallet_name="vega",
                wallet_pass="pass",
                key_name="sensitive_trader",
                market_name=market_name,
                asset_name=asset_name,
                initial_asset_mint=self.st_mint,
                max_order_size=50,
                scale=0.035,
                price_process_generator=iter(price_process),
                random_state=random_state,
            )
            for _ in range(5)
        ]

        agents = (
            [
                market_manager,
                market_maker,
                open_auction_pass_bid,
                open_auction_pass_ask,
                informed_trader,
            ]
            + simple_liquidity_providers
            + sensitive_traders
            + random_traders
        )
        return {agent.name(): agent for agent in agents}

    def configure_environment(
        self,
        vega: VegaServiceNull,
        random_state: Optional[np.random.RandomState] = None,
        **kwargs,
    ) -> MarketEnvironmentWithState:
        return MarketEnvironmentWithState(
            agents=list(self.agents.values()),
            n_steps=self.num_steps,
            step_length_seconds=self.step_length_seconds,
            random_agent_ordering=True,
            transactions_per_block=self.block_size,
            vega_service=vega,
            block_length_seconds=self.block_length_seconds,
            random_state=random_state,
        )
