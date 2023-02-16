import argparse
import logging
import numpy as np
from typing import Any, Callable, List, Optional, Dict
from vega_sim.environment.agent import Agent

from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.common.utils.price_process import random_walk
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.ideal_market_maker_v2.agents import (
    MM_WALLET,
    TERMINATE_WALLET,
    TRADER_WALLET,
    BACKGROUND_MARKET,
    AUCTION1_WALLET,
    AUCTION2_WALLET,
    OptimalMarketMaker,
)
from vega_sim.scenario.common.agents import (
    MarketOrderTrader,
    BackgroundMarket,
    OpenAuctionPass,
    StateAgent,
)


class IdealMarketMaker(Scenario):
    def __init__(
        self,
        num_steps: int = 120,
        random_agent_ordering: bool = True,
        market_decimal: int = 5,
        asset_decimal: int = 5,
        market_position_decimal: int = 2,
        market_name: str = None,
        asset_name: str = None,
        initial_asset_mint: float = 1000000,
        initial_price: Optional[float] = None,
        sigma: float = 1,
        kappa: float = 1,
        q_upper: int = 20,
        q_lower: int = -20,
        alpha: float = 10**-4,
        phi: float = 5 * 10**-6,
        market_marker_limit_order_size: float = 10,
        lp_commitamount: float = 200000,
        spread: int = 2,
        block_size: int = 1,
        block_length_seconds: int = 1,
        buy_intensity: float = 5,
        sell_intensity: float = 5,
        backgroundmarket_tick_spacing: float = 0.002,
        backgroundmarket_number_levels_per_side: int = 20,
        step_length_seconds: int = 1,
        opening_auction_trade_amount: float = 1,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, Dict[str, Agent]], Any]
        ] = None,
        pause_every_n_steps: Optional[int] = None,
        price_process_fn: Optional[Callable[[None], List[float]]] = None,
        market_order_trader_base_order_size: float = 1,
        settle_at_end: bool = True,
        proportion_taken: float = 0.8,
    ):
        super().__init__(state_extraction_fn=state_extraction_fn)
        self.num_steps = num_steps
        self.random_agent_ordering = random_agent_ordering
        self.market_decimal = market_decimal
        self.asset_decimal = asset_decimal
        self.market_position_decimal = market_position_decimal
        self.initial_price = initial_price
        self.sigma = sigma
        self.kappa = kappa
        self.q_upper = q_upper
        self.q_lower = q_lower
        self.alpha = alpha
        self.phi = phi
        self.spread = spread / 10**self.market_decimal
        self.block_size = block_size
        self.block_length_seconds = block_length_seconds
        self.step_length_seconds = step_length_seconds
        self.buy_intensity = buy_intensity
        self.sell_intensity = sell_intensity
        self.pause_every_n_steps = pause_every_n_steps
        self.lp_commitamount = lp_commitamount
        self.initial_asset_mint = initial_asset_mint
        self.backgroundmarket_tick_spacing = backgroundmarket_tick_spacing
        self.market_marker_limit_order_size = market_marker_limit_order_size
        self.backgroundmarket_number_levels_per_side = (
            backgroundmarket_number_levels_per_side
        )
        self.market_name = "ETH:USD" if market_name is None else market_name
        self.asset_name = "tDAI" if asset_name is None else asset_name
        self.price_process_fn = price_process_fn
        self.opening_auction_trade_amount = opening_auction_trade_amount
        self.market_order_trader_base_order_size = market_order_trader_base_order_size
        self.settle_at_end = settle_at_end
        self.price_process = None
        self.proportion_taken = proportion_taken

    def _generate_price_process(
        self,
        random_state: Optional[np.random.RandomState] = None,
    ):
        return random_walk(
            num_steps=self.num_steps,
            sigma=self.sigma,
            starting_price=self.initial_price,
            random_state=random_state,
        )

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: str,
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> List[StateAgent]:
        # Set up market name and settlement asset
        market_name = self.market_name + f"_{tag}"
        asset_name = self.asset_name + f"_{tag}"

        price_process = (
            self.price_process_fn()
            if self.price_process_fn is not None
            else self._generate_price_process(random_state=random_state)
        )
        self.price_process = price_process

        market_maker = OptimalMarketMaker(
            key_name=MM_WALLET.name,
            terminate_key_name=TERMINATE_WALLET.name,
            initial_asset_mint=self.initial_asset_mint,
            price_process=price_process,
            spread=self.spread,
            num_steps=self.num_steps,
            market_order_arrival_rate=self.buy_intensity,
            kappa=self.kappa,
            limit_order_size=self.market_marker_limit_order_size,
            inventory_upper_boundary=self.q_upper,
            inventory_lower_boundary=self.q_lower,
            terminal_penalty_parameter=self.alpha,
            running_penalty_parameter=self.phi,
            asset_decimal=self.asset_decimal,
            market_decimal=self.market_decimal,
            market_position_decimal=self.market_position_decimal,
            market_name=market_name,
            asset_name=asset_name,
            commitment_amount=self.lp_commitamount,
            tag=str(tag),
            settlement_price=price_process[-1] if self.settle_at_end else None,
        )

        trader = MarketOrderTrader(
            key_name=TRADER_WALLET.name,
            initial_asset_mint=self.initial_asset_mint,
            market_name=market_name,
            asset_name=asset_name,
            tag=str(tag),
            buy_intensity=self.buy_intensity,
            sell_intensity=self.sell_intensity,
            random_state=random_state,
            base_order_size=self.market_order_trader_base_order_size,
        )

        background_market = BackgroundMarket(
            key_name=BACKGROUND_MARKET.name,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=self.initial_asset_mint,
            price_process=price_process,
            spread=self.spread,
            tick_spacing=self.backgroundmarket_tick_spacing,
            order_distribution_kappa=self.kappa,
            num_levels_per_side=self.backgroundmarket_number_levels_per_side,
            tag=str(tag),
            position_decimals=self.market_position_decimal,
        )

        auctionpass1 = OpenAuctionPass(
            key_name=AUCTION1_WALLET.name,
            side="SIDE_BUY",
            initial_asset_mint=self.initial_asset_mint,
            initial_price=self.initial_price
            if self.initial_price is not None
            else price_process[0],
            market_name=market_name,
            asset_name=asset_name,
            opening_auction_trade_amount=self.opening_auction_trade_amount,
            tag=f"1_{tag}",
        )

        auctionpass2 = OpenAuctionPass(
            key_name=AUCTION2_WALLET.name,
            side="SIDE_SELL",
            initial_asset_mint=self.initial_asset_mint,
            initial_price=self.initial_price
            if self.initial_price is not None
            else price_process[0],
            market_name=market_name,
            asset_name=asset_name,
            opening_auction_trade_amount=self.opening_auction_trade_amount,
            tag=f"2_{tag}",
        )

        # info_trader = InformedTrader(
        #     key_name=INFORMED_WALLET.name,
        #     price_process=price_process,
        #     market_name=market_name,
        #     asset_name=asset_name,
        #     initial_asset_mint=self.initial_asset_mint,
        #     proportion_taken=self.proportion_taken,
        #     tag=str(tag),
        # )

        agents = [
            market_maker,
            background_market,
            auctionpass1,
            auctionpass2,
            trader,
        ]
        return {agent.name(): agent for agent in agents}

    def configure_environment(
        self,
        vega: VegaServiceNull,
        **kwargs,
    ) -> MarketEnvironmentWithState:
        return MarketEnvironmentWithState(
            agents=list(self.agents.values()),
            n_steps=self.num_steps,
            random_agent_ordering=self.random_agent_ordering,
            transactions_per_block=self.block_size,
            vega_service=vega,
            step_length_seconds=self.step_length_seconds,
            block_length_seconds=self.block_length_seconds,
            pause_every_n_steps=self.pause_every_n_steps,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

    step_length = 60 * 60

    scenario = IdealMarketMaker(num_steps=200)

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=True,
        seconds_per_block=40,  # Heuristic
    ) as vega:
        scenario.run_iteration(
            vega=vega,
            pause_at_completion=True,
        )
