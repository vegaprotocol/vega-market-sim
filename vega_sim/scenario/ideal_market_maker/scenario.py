import argparse
import logging
import numpy as np
from typing import Any, Callable, List, Optional
from vega_sim.environment.agent import Agent

from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.ideal_market_maker.utils.price_process import RW_model
from vega_sim.scenario.ideal_market_maker.environments import MarketEnvironment
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.constants import Network
from vega_sim.scenario.ideal_market_maker.agents import (
    MM_WALLET,
    TERMINATE_WALLET,
    TRADER_WALLET,
    RANDOM_WALLET,
    AUCTION1_WALLET,
    AUCTION2_WALLET,
    INFORMED_WALLET,
    LIQUIDITY,
    OptimalLiquidityProvider,
    OptimalMarketMaker,
    MarketOrderTrader,
    LimitOrderTrader,
    OpenAuctionPass,
    InformedTrader,
)


class IdealMarketMaker(Scenario):
    def __init__(
        self,
        num_steps: int = 120,
        dt: float = 1 / 60 / 24 / 365.25,
        market_decimal: int = 5,
        asset_decimal: int = 5,
        market_position_decimal: int = 0,
        market_name: str = "ETH:USD",
        asset_name: str = "tDAI",
        initial_asset_mint: float = 1e6,
        lp_initial_mint: float = 1e6,
        lp_commitamount: float = 20000,
        initial_price: float = 0.3,
        sigma: float = 1,
        kappa: float = 500,
        lambda_val: float = 5,
        q_upper: int = 20,
        q_lower: int = -20,
        alpha: float = 10**-4,
        phi: float = 5 * 10**-6,
        spread: float = 0.00002,
        block_size: int = 1,
        block_length_seconds: int = 1,
        state_extraction_freq: int = 1,
        step_length_seconds: Optional[int] = None,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, List[Agent]], Any]
        ] = None,
        proportion_taken: float = 0.8,
    ):
        self.num_steps = num_steps
        self.dt = dt
        self.market_name = market_name
        self.asset_name = asset_name
        self.market_decimal = market_decimal
        self.asset_decimal = asset_decimal
        self.market_position_decimal = market_position_decimal
        self.lp_commitamount = lp_commitamount
        self.initial_asset_mint = initial_asset_mint
        self.lp_initial_mint = lp_initial_mint
        self.initial_price = initial_price
        self.sigma = sigma
        self.kappa = kappa
        self.lambda_val = lambda_val
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
        self.proportion_taken = proportion_taken

    def set_up_background_market(
        self,
        vega: VegaServiceNull,
        tag: str = "",
        random_state: Optional[np.random.RandomState] = None,
    ) -> MarketEnvironment:
        _, price_process = RW_model(
            T=self.num_steps * self.dt,
            dt=self.dt,
            mdp=self.market_decimal,
            sigma=self.sigma,
            Midprice=self.initial_price,
            random_state=random_state,
        )

        market_name = self.market_name + f"_{tag}" if tag else self.market_name
        asset_name = self.asset_name + f"_{tag}" if tag else self.asset_name

        market_maker = OptimalMarketMaker(
            wallet_name=MM_WALLET.name,
            wallet_pass=MM_WALLET.passphrase,
            terminate_wallet_name=TERMINATE_WALLET.name,
            terminate_wallet_pass=TERMINATE_WALLET.passphrase,
            price_process=price_process,
            spread=self.spread,
            num_steps=self.num_steps,
            market_order_arrival_rate=self.lambda_val,
            pegged_order_fill_rate=self.kappa,
            inventory_upper_boundary=self.q_upper,
            inventory_lower_boundary=self.q_lower,
            terminal_penalty_parameter=self.alpha,
            running_penalty_parameter=self.phi,
            asset_decimal=self.asset_decimal,
            initial_asset_mint=self.lp_initial_mint,
            market_decimal=self.market_decimal,
            market_position_decimal=self.market_position_decimal,
            market_name=market_name,
            asset_name=asset_name,
            commitamount=self.lp_commitamount,
            random_state=random_state,
            tag=str(tag),
        )

        tradingbot = MarketOrderTrader(
            wallet_name=TRADER_WALLET.name,
            wallet_pass=TRADER_WALLET.passphrase,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=self.initial_asset_mint,
            tag=str(tag),
        )

        randomtrader = LimitOrderTrader(
            wallet_name=RANDOM_WALLET.name,
            wallet_pass=RANDOM_WALLET.passphrase,
            price_process=price_process,
            spread=self.spread,
            initial_price=self.initial_price,
            asset_decimal=self.asset_decimal,
            market_decimal=self.market_decimal,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=self.initial_asset_mint,
            tag=str(tag),
        )

        auctionpass1 = OpenAuctionPass(
            wallet_name=AUCTION1_WALLET.name,
            wallet_pass=AUCTION1_WALLET.passphrase,
            side="SIDE_BUY",
            initial_price=self.initial_price,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=self.initial_asset_mint,
            tag=str(tag),
        )

        auctionpass2 = OpenAuctionPass(
            wallet_name=AUCTION2_WALLET.name,
            wallet_pass=AUCTION2_WALLET.passphrase,
            side="SIDE_SELL",
            initial_price=self.initial_price,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=self.initial_asset_mint,
            tag=str(tag),
        )

        liquidityprovider = OptimalLiquidityProvider(
            wallet_name=LIQUIDITY.name,
            wallet_pass=LIQUIDITY.passphrase,
            num_steps=self.num_steps,
            market_order_arrival_rate=self.lambda_val,
            pegged_order_fill_rate=self.kappa,
            inventory_upper_boundary=self.q_upper,
            inventory_lower_boundary=self.q_lower,
            terminal_penalty_parameter=self.alpha,
            running_penalty_parameter=self.phi,
            initial_asset_mint=self.initial_asset_mint,
            market_name=market_name,
            asset_name=asset_name,
            entry_step=5,
            commitamount=self.lp_commitamount,
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

        env = MarketEnvironment(
            base_agents=[
                market_maker,
                tradingbot,
                randomtrader,
                auctionpass1,
                auctionpass2,
                info_trader,
                liquidityprovider,
            ],
            n_steps=self.num_steps,
            transactions_per_block=self.block_size,
            vega_service=vega,
            state_extraction_freq=self.state_extraction_freq,
            step_length_seconds=self.step_length_seconds,
            block_length_seconds=self.block_length_seconds,
            state_extraction_fn=self.state_extraction_fn,
        )
        return env

    def run_iteration(
        self,
        vega: VegaServiceNull,
        network: Optional[Network] = None,
        pause_at_completion: bool = False,
        random_state: Optional[np.random.RandomState] = None,
    ):
        env = self.set_up_background_market(
            vega=vega, tag=str(0), random_state=random_state
        )
        result = env.run(
            pause_at_completion=pause_at_completion,
        )
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

    step_length = 60 * 60

    scenario = IdealMarketMaker(num_steps=100)

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=True,
        seconds_per_block=40,  # Heuristic
    ) as vega:
        scenario.run_iteration(vega=vega, pause_at_completion=True)
