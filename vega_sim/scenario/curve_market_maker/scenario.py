import argparse
import logging
import numpy as np
from typing import Any, Callable, List, Optional, Dict
from vega_sim.environment.agent import Agent
from vega_sim.scenario.common.utils.price_process import (
    Granularity,
    get_historic_price_series,
)

from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.common.utils.price_process import random_walk
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.ideal_market_maker_v2.agents import (
    MM_WALLET,
    TERMINATE_WALLET,
    TRADER_WALLET,
    AUCTION1_WALLET,
    AUCTION2_WALLET,
    INFORMED_WALLET,
)
from vega_sim.scenario.common.agents import (
    MarketManager,
    OpenAuctionPass,
    ExponentialShapedMarketMaker,
    PriceSensitiveMarketOrderTrader,
    InformedTrader,
    StateAgent,
)


class CurveMarketMaker(Scenario):
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
        num_lp_levels: int = 25,
        sigma: float = 1,
        market_maker_curve_kappa: float = 1,
        market_maker_assumed_market_kappa: float = 1,
        q_upper: int = 20,
        q_lower: int = -20,
        alpha: float = 10**-4,
        phi: float = 5 * 10**-6,
        lp_commitamount: float = 200000,
        block_size: int = 1,
        block_length_seconds: int = 1,
        buy_intensity: float = 5,
        sell_intensity: float = 5,
        step_length_seconds: int = 1,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, Dict[str, Agent]], Any]
        ] = None,
        price_process_fn: Optional[Callable[[None], List[float]]] = None,
        pause_every_n_steps: Optional[int] = None,
        settle_at_end: bool = True,
        opening_auction_trade_amount: float = 1,
        market_order_trader_base_order_size: float = 1,
        sensitive_price_taker_half_life: float = 0.5,
        market_maker_base_order_size: float = 0.1,
        market_maker_tick_spacing: float = 1,
        market_maker_max_order: float = 200,
        proportion_taken: float = 0.8,
    ):
        super().__init__(state_extraction_fn=state_extraction_fn)
        if buy_intensity != sell_intensity:
            raise Exception("Model currently requires buy_intensity == sell_intensity")

        self.num_steps = num_steps
        self.random_agent_ordering = random_agent_ordering
        self.market_decimal = market_decimal
        self.asset_decimal = asset_decimal
        self.market_position_decimal = market_position_decimal
        self.initial_price = initial_price
        self.sigma = sigma
        self.market_kappa = market_maker_assumed_market_kappa
        self.curve_kappa = market_maker_curve_kappa
        self.q_upper = q_upper
        self.q_lower = q_lower
        self.alpha = alpha
        self.phi = phi
        self.block_size = block_size
        self.block_length_seconds = block_length_seconds
        self.step_length_seconds = step_length_seconds
        self.buy_intensity = buy_intensity
        self.sell_intensity = sell_intensity
        self.pause_every_n_steps = pause_every_n_steps
        self.lp_commitamount = lp_commitamount
        self.initial_asset_mint = initial_asset_mint
        self.market_name = "ETH:USD" if market_name is None else market_name
        self.asset_name = "tDAI" if asset_name is None else asset_name
        self.settle_at_end = settle_at_end
        self.price_process_fn = price_process_fn
        self.price_process = None
        self.opening_auction_trade_amount = opening_auction_trade_amount
        self.market_order_trader_base_order_size = market_order_trader_base_order_size
        self.sensitive_price_taker_half_life = sensitive_price_taker_half_life
        self.num_lp_levels = num_lp_levels
        self.market_maker_base_order_size = market_maker_base_order_size
        self.market_maker_tick_spacing = market_maker_tick_spacing
        self.market_maker_max_order = market_maker_max_order
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
        tag: Optional[str],
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> List[StateAgent]:
        # Set up market name and settlement asset
        market_name = self.market_name + (f"_{tag}" if tag else "")
        asset_name = self.asset_name

        price_process = (
            self.price_process_fn()
            if self.price_process_fn is not None
            else self._generate_price_process(random_state=random_state)
        )
        self.price_process = price_process
        self.initial_price = (
            self.initial_price if self.initial_price is not None else price_process[0]
        )

        market_manager = MarketManager(
            key_name=MM_WALLET.name,
            terminate_key_name=TERMINATE_WALLET.name,
            asset_decimal=self.asset_decimal,
            market_decimal=self.market_decimal,
            market_position_decimal=self.market_position_decimal,
            market_name=market_name,
            asset_name=asset_name,
            tag=str(tag) if tag is not None else None,
            settlement_price=price_process[-1] if self.settle_at_end else None,
        )

        shaped_mm = ExponentialShapedMarketMaker(
            key_name="expon",
            price_process_generator=iter(price_process),
            initial_asset_mint=self.initial_asset_mint,
            market_name=market_name,
            asset_name=asset_name,
            commitment_amount=self.lp_commitamount,
            market_decimal_places=self.market_decimal,
            asset_decimal_places=self.asset_decimal,
            num_steps=self.num_steps,
            num_levels=self.num_lp_levels,
            tag=str(tag) if tag is not None else None,
            kappa=self.curve_kappa,
            tick_spacing=self.market_maker_tick_spacing,
            inventory_upper_boundary=self.q_upper,
            inventory_lower_boundary=self.q_lower,
            terminal_penalty_parameter=self.alpha,
            running_penalty_parameter=self.phi,
            market_order_arrival_rate=self.buy_intensity,
            market_kappa=self.market_kappa,
            state_update_freq=10,
        )

        sensitive_mo_trader = PriceSensitiveMarketOrderTrader(
            key_name=TRADER_WALLET.name,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=self.initial_asset_mint,
            buy_intensity=self.buy_intensity,
            sell_intensity=self.sell_intensity,
            price_half_life=self.sensitive_price_taker_half_life,
            price_process_generator=iter(price_process),
            tag=str(tag) if tag is not None else None,
            base_order_size=self.market_order_trader_base_order_size,
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

        info_trader = InformedTrader(
            key_name=INFORMED_WALLET.name,
            price_process=price_process,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=self.initial_asset_mint,
            proportion_taken=self.proportion_taken,
            tag=str(tag) if tag is not None else None,
        )

        agents = [
            market_manager,
            shaped_mm,
            sensitive_mo_trader,
            auctionpass1,
            auctionpass2,
            info_trader,
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

    scenario = CurveMarketMaker(
        market_name="ETH",
        asset_name="USD",
        num_steps=290,
        market_decimal=2,
        asset_decimal=4,
        market_position_decimal=4,
        price_process_fn=lambda: get_historic_price_series(
            product_id="ETH-USD", granularity=Granularity.HOUR
        ).values,
        lp_commitamount=250_000,
        initial_asset_mint=10_000_000,
        step_length_seconds=60,
        # step_length_seconds=Granularity.HOUR.value,
        block_length_seconds=1,
        buy_intensity=500,
        sell_intensity=500,
        q_upper=5,
        q_lower=-5,
        kappa=0.2,
        opening_auction_trade_amount=0.0001,
        market_order_trader_base_order_size=0.01,
        pause_every_n_steps=25,
    )

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=True,
        use_full_vega_wallet=False,
        retain_log_files=True,
        launch_graphql=True,
        seconds_per_block=1,  # Heuristic
    ) as vega:
        scenario.run_iteration(
            vega=vega,
            pause_at_completion=True,
        )
