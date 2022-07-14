import argparse
import logging
from typing import Any, Callable, List, Optional
from vega_sim.environment.agent import Agent

from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.ideal_market_maker_v2.utils.price_process import (
    RW_model,
)
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
)


class IdealMarketMaker(Scenario):
    def __init__(
        self,
        num_steps: int = 120,
        dt: float = 1 / 60 / 24 / 365.25,
        market_decimal: int = 5,
        asset_decimal: int = 5,
        market_position_decimal: int = 2,
        initial_price: float = 100,
        sigma: float = 1,
        kappa: float = 1,
        q_upper: int = 20,
        q_lower: int = -20,
        alpha: float = 10**-4,
        phi: float = 5 * 10**-6,
        lp_commitamount: float = 200000,
        spread: float = 0.02,
        block_size: int = 1,
        block_length_seconds: int = 1,
        state_extraction_freq: int = 1,
        buy_intensity: float = 5,
        sell_intensity: float = 5,
        step_length_seconds: int = 1,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, List[Agent]], Any]
        ] = None,
        pause_every_n_steps: Optional[int] = None,
    ):
        if buy_intensity != sell_intensity:
            raise Exception("Model currently requires buy_intensity == sell_intensity")

        self.num_steps = num_steps
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
        self.spread = spread
        self.block_size = block_size
        self.block_length_seconds = block_length_seconds
        self.state_extraction_freq = state_extraction_freq
        self.step_length_seconds = step_length_seconds
        self.state_extraction_fn = state_extraction_fn
        self.buy_intensity = buy_intensity
        self.sell_intensity = sell_intensity
        self.pause_every_n_steps = pause_every_n_steps
        self.lp_commitamount = lp_commitamount

    def set_up_background_market(
        self,
        vega: VegaServiceNull,
        tag: str = "",
    ) -> MarketEnvironmentWithState:
        _, price_process = RW_model(
            T=self.num_steps * self.dt,
            dt=self.dt,
            mdp=self.market_decimal,
            sigma=self.sigma,
            Midprice=self.initial_price,
        )
        
        # Set up market name and settlement asset
        market_name = f"ETH:USD_{tag}"
        asset_name = f"tDAI{tag}"

        market_maker = OptimalMarketMaker(
            wallet_name=MM_WALLET.name,
            wallet_pass=MM_WALLET.passphrase,
            terminate_wallet_name=TERMINATE_WALLET.name,
            terminate_wallet_pass=TERMINATE_WALLET.passphrase,
            price_processs=price_process,
            spread=self.spread,
            num_steps=self.num_steps,
            market_order_arrival_rate=self.buy_intensity,
            kappa=self.kappa,
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
        )

        trader = MarketOrderTrader(
            wallet_name=TRADER_WALLET.name,
            wallet_pass=TRADER_WALLET.passphrase,
            market_name=market_name,
            asset_name=asset_name,
            tag=str(tag),
            buy_intensity=self.buy_intensity,
            sell_intensity=self.sell_intensity,
        )

        background_market = BackgroundMarket(
            wallet_name=BACKGROUND_MARKET.name,
            wallet_pass=BACKGROUND_MARKET.passphrase,
            market_name=market_name,
            asset_name=asset_name,
            price_process=price_process,
            spread=self.spread,
            tick_spacing=0.002,
            order_distribution_kappa=self.kappa,
            num_levels_per_side=40,
            tag=str(tag),
        )

        auctionpass1 = OpenAuctionPass(
            wallet_name=AUCTION1_WALLET.name,
            wallet_pass=AUCTION1_WALLET.passphrase,
            side="SIDE_BUY",
            initial_price=self.initial_price,
            market_name=market_name,
            asset_name=asset_name,
            tag=str(tag),
        )

        auctionpass2 = OpenAuctionPass(
            wallet_name=AUCTION2_WALLET.name,
            wallet_pass=AUCTION2_WALLET.passphrase,
            side="SIDE_SELL",
            initial_price=self.initial_price,
            market_name=market_name,
            asset_name=asset_name,
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
        pause_at_completion: bool = False,
        run_with_console: bool = False,
    ):
        env = self.set_up_background_market(
            vega=vega,
            tag=str(0),
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
            run_with_console=False,
        )
