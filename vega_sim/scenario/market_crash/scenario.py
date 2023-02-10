import argparse
import logging
from typing import Any, Callable, List, Optional, Dict
from vega_sim.environment.agent import Agent
from vega_sim.scenario.market_crash.price_process import regime_change_random_walk

from vega_sim.scenario.scenario import Scenario

from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.ideal_market_maker_v2.agents import (
    MM_WALLET,
    TERMINATE_WALLET,
    TRADER_WALLET,
    BACKGROUND_MARKET,
    AUCTION1_WALLET,
    AUCTION2_WALLET,
)
from vega_sim.scenario.common.agents import (
    MarketManager,
    StateAgent,
    MarketOrderTrader,
    MultiRegimeBackgroundMarket,
    MarketRegime,
    OpenAuctionPass,
)

import numpy as np


class MarketCrash(Scenario):
    def __init__(
        self,
        num_steps: int = 120,
        dt: float = 1 / 60 / 24 / 365.25,
        market_decimal: int = 5,
        asset_decimal: int = 5,
        initial_price: float = 100,
        initial_asset_mint: float = 1000,
        sigma_pre: float = 1,
        sigma_post: float = 2,
        drift_pre: float = 0,
        drift_post: float = -1,
        break_point: int = 50,
        kappa: float = 1,
        q_upper: int = 20,
        q_lower: int = -20,
        alpha: float = 10**-4,
        phi: float = 5 * 10**-6,
        spread: float = 0.02,
        block_size: int = 1,
        block_length_seconds: int = 1,
        position_taker_mint: float = 1000,
        position_taker_buy_intensity: float = 5,
        position_taker_sell_intensity: float = 5,
        noise_buy_intensity: float = 1,
        noise_sell_intensity: float = 1,
        num_position_traders: int = 5,
        num_noise_traders: int = 5,
        step_length_seconds: int = 1,
        settle_at_end: bool = True,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, Dict[str, Agent]], Any]
        ] = None,
        pause_every_n_steps: Optional[int] = None,
        trim_to_min: Optional[float] = None,
        price_process_fn: Optional[Callable] = None,
    ):
        super().__init__(state_extraction_fn=state_extraction_fn)
        self.num_steps = num_steps
        self.dt = dt
        self.market_decimal = market_decimal
        self.asset_decimal = asset_decimal
        self.initial_price = initial_price
        self.sigma_pre = sigma_pre
        self.sigma_post = sigma_post
        self.drift_pre = drift_pre
        self.drift_post = drift_post
        self.break_point = break_point
        self.kappa = kappa
        self.q_upper = q_upper
        self.q_lower = q_lower
        self.alpha = alpha
        self.phi = phi
        self.spread = spread
        self.block_size = block_size
        self.block_length_seconds = block_length_seconds
        self.step_length_seconds = step_length_seconds
        self.position_taker_buy_intensity = position_taker_buy_intensity
        self.position_taker_sell_intensity = position_taker_sell_intensity
        self.noise_buy_intensity = noise_buy_intensity
        self.noise_sell_intensity = noise_sell_intensity
        self.pause_every_n_steps = pause_every_n_steps
        self.trim_to_min = trim_to_min
        self.position_taker_mint = position_taker_mint
        self.num_position_traders = num_position_traders
        self.num_noise_traders = num_noise_traders
        self.settle_at_end = settle_at_end
        self.initial_asset_mint = initial_asset_mint
        self.price_process_fn = price_process_fn

    def _generate_price_process(
        self,
        random_state: Optional[np.random.RandomState] = None,
    ):
        return regime_change_random_walk(
            num_steps=self.num_steps + 1,  # Number of steps plus 'initial' state
            sigma_pre=self.sigma_pre,
            sigma_post=self.sigma_post,
            drift_pre=self.drift_pre,
            drift_post=self.drift_post,
            starting_price=self.initial_price,
            break_point=self.break_point,
            decimal_precision=self.market_decimal,
            trim_to_min=self.trim_to_min,
            random_state=random_state,
        )

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: str,
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> List[StateAgent]:
        self.market_name = f"BTC:DAI_{tag}"
        self.asset_name = f"tDAI{tag}"

        self.price_process = (
            self.price_process_fn()
            if self.price_process_fn is not None
            else self._generate_price_process()
        )

        market_maker = MarketManager(
            key_name=MM_WALLET.name,
            terminate_key_name=TERMINATE_WALLET.name,
            asset_decimal=self.asset_decimal,
            market_decimal=self.market_decimal,
            commitment_amount=60000,
            settlement_price=self.price_process[-1] if self.settle_at_end else None,
            market_name=self.market_name,
            asset_name=self.asset_name,
            tag=str(tag),
        )

        position_traders = []
        noise_traders = []

        for i in range(self.num_noise_traders):
            noise_traders.append(
                MarketOrderTrader(
                    market_name=self.market_name,
                    asset_name=self.asset_name,
                    tag=f"{tag}_noise_{i}",
                    initial_asset_mint=self.position_taker_mint,
                    buy_intensity=self.noise_buy_intensity,
                    sell_intensity=self.noise_sell_intensity,
                    random_state=random_state,
                    key_name=f"{tag}_noise_{i}",
                )
            )
        for i in range(self.num_position_traders):
            position_traders.append(
                MarketOrderTrader(
                    market_name=self.market_name,
                    asset_name=self.asset_name,
                    initial_asset_mint=self.position_taker_mint,
                    tag=f"{tag}_pos_{i}",
                    buy_intensity=self.position_taker_buy_intensity,
                    sell_intensity=self.position_taker_sell_intensity,
                    random_state=random_state,
                    key_name=f"{tag}_pos_{i}",
                )
            )

        background_market = MultiRegimeBackgroundMarket(
            key_name=BACKGROUND_MARKET.name,
            market_name=self.market_name,
            asset_name=self.asset_name,
            market_regimes=[
                MarketRegime(
                    spread=self.spread,
                    tick_spacing=0.1,
                    num_levels_per_side=25,
                    base_volume_size=1,
                    order_distribution_buy_kappa=self.kappa,
                    order_distribution_sell_kappa=self.kappa,
                    from_timepoint=0,
                    thru_timepoint=10000,
                )
            ],
            price_process=self.price_process,
            tag=str(tag),
        )

        auctionpass1 = OpenAuctionPass(
            key_name=AUCTION1_WALLET.name,
            side="SIDE_BUY",
            initial_price=self.initial_price,
            market_name=self.market_name,
            asset_name=self.asset_name,
            initial_asset_mint=self.initial_asset_mint,
            tag=f"1_{tag}",
        )

        auctionpass2 = OpenAuctionPass(
            key_name=AUCTION2_WALLET.name,
            side="SIDE_SELL",
            initial_price=self.initial_price,
            market_name=self.market_name,
            asset_name=self.asset_name,
            initial_asset_mint=self.initial_asset_mint,
            tag=f"2_{tag}",
        )

        agents = (
            [
                market_maker,
                background_market,
                auctionpass1,
                auctionpass2,
            ]
            + noise_traders
            + position_traders
        )
        return {agent.name(): agent for agent in agents}

    def configure_environment(
        self,
        vega: VegaServiceNull,
        tag: str,
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> MarketEnvironmentWithState:
        return MarketEnvironmentWithState(
            agents=list(self.agents.values()),
            n_steps=self.num_steps,
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

    scenario = MarketCrash(
        num_steps=200,
        sigma_pre=1,
        sigma_post=2,
        drift_pre=0.1,
        drift_post=-0.2,
        break_point=800,
        initial_price=10,
        # step_length_seconds=60,
    )

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=True,
        seconds_per_block=40,  # Heuristic
    ) as vega:
        scenario.run_iteration(vega=vega, pause_at_completion=True)
