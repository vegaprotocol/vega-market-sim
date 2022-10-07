import argparse
import logging
import numpy as np
from typing import Any, Callable, List, Optional
from vega_sim.environment.agent import Agent

from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.ideal_market_maker_v2.utils.price_process import RW_model
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.constants import Network
from vega_sim.scenario.ideal_market_maker_v2.agents import (
    MM_WALLET,
    TERMINATE_WALLET,
    TRADER_WALLET,
    BACKGROUND_MARKET,
    AUCTION1_WALLET,
    AUCTION2_WALLET,
    INFORMED_WALLET,
    OptimalMarketMaker,
)
from vega_sim.scenario.common.agents import (
    MarketOrderTrader,
    BackgroundMarket,
    OpenAuctionPass,
    InformedTrader,
)


class IdealMarketMaker(Scenario):
    def __init__(
        self,
        num_steps: int = 120,
        random_agent_ordering: bool = True,
        dt: float = 1 / 60 / 24 / 365.25,
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
        state_extraction_freq: int = 1,
        buy_intensity: float = 5,
        sell_intensity: float = 5,
        backgroundmarket_tick_spacing: float = 0.002,
        backgroundmarket_number_levels_per_side: int = 20,
        step_length_seconds: int = 1,
        opening_auction_trade_amount: float = 1,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, List[Agent]], Any]
        ] = None,
        pause_every_n_steps: Optional[int] = None,
        price_process_fn: Optional[Callable[[None], List[float]]] = None,
        market_order_trader_base_order_size: float = 1,
        settle_at_end: bool = True,
        proportion_taken: float = 0.8,
    ):
        self.num_steps = num_steps
        self.random_agent_ordering = random_agent_ordering
        self.dt = dt
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
        self.state_extraction_freq = state_extraction_freq
        self.step_length_seconds = step_length_seconds
        self.state_extraction_fn = state_extraction_fn
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
        _, price_process = RW_model(
            T=self.num_steps * self.dt,
            dt=self.dt,
            mdp=self.market_decimal,
            sigma=self.sigma,
            Midprice=self.initial_price,
            random_state=random_state,
        )
        return price_process

    def set_up_background_market(
        self,
        vega: VegaServiceNull,
        tag: str = "",
        random_state: Optional[np.random.RandomState] = None,
    ) -> MarketEnvironmentWithState:
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
            wallet_name=MM_WALLET.name,
            wallet_pass=MM_WALLET.passphrase,
            terminate_wallet_name=TERMINATE_WALLET.name,
            terminate_wallet_pass=TERMINATE_WALLET.passphrase,
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
            wallet_name=TRADER_WALLET.name,
            wallet_pass=TRADER_WALLET.passphrase,
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
            wallet_name=BACKGROUND_MARKET.name,
            wallet_pass=BACKGROUND_MARKET.passphrase,
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
            wallet_name=AUCTION1_WALLET.name,
            wallet_pass=AUCTION1_WALLET.passphrase,
            side="SIDE_BUY",
            initial_asset_mint=self.initial_asset_mint,
            initial_price=self.initial_price
            if self.initial_price is not None
            else price_process[0],
            market_name=market_name,
            asset_name=asset_name,
            opening_auction_trade_amount=self.opening_auction_trade_amount,
            tag=str(tag),
        )

        auctionpass2 = OpenAuctionPass(
            wallet_name=AUCTION2_WALLET.name,
            wallet_pass=AUCTION2_WALLET.passphrase,
            side="SIDE_SELL",
            initial_asset_mint=self.initial_asset_mint,
            initial_price=self.initial_price
            if self.initial_price is not None
            else price_process[0],
            market_name=market_name,
            asset_name=asset_name,
            opening_auction_trade_amount=self.opening_auction_trade_amount,
            tag=str(tag),
        )

        info_trader = InformedTrader(
            wallet_name=INFORMED_WALLET.name,
            wallet_pass=INFORMED_WALLET.passphrase,
            price_process=price_process,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=self.initial_asset_mint,
            proportion_taken=self.proportion_taken,
            tag=str(tag),
        )

        env = MarketEnvironmentWithState(
            agents=[
                market_maker,
                background_market,
                auctionpass1,
                auctionpass2,
                trader,
            ],
            n_steps=self.num_steps,
            random_agent_ordering=self.random_agent_ordering,
            transactions_per_block=self.block_size,
            vega_service=vega,
            state_extraction_freq=self.state_extraction_freq,
            step_length_seconds=self.step_length_seconds,
            block_length_seconds=self.block_length_seconds,
            state_extraction_fn=self.state_extraction_fn,
            pause_every_n_steps=self.pause_every_n_steps,
        )
        return env

    def run_iteration(
        self,
        vega: VegaServiceNull,
        network: Optional[Network] = None,
        pause_at_completion: bool = False,
        run_with_console: bool = False,
        random_state: Optional[np.random.RandomState] = None,
    ):
        env = self.set_up_background_market(
            vega=vega, tag=str(0), random_state=random_state
        )
        result = env.run(
            pause_at_completion=pause_at_completion,
            run_with_console=run_with_console,
        )
        return result


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
