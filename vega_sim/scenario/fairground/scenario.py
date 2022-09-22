import argparse
import logging
import numpy as np
from typing import Any, Callable, List, Optional
from vega_sim.environment.agent import Agent

from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.ideal_market_maker_v2.utils.price_process import (
    RW_model,
)
from vega_sim.environment.environment import NetworkEnvironment
from vega_sim.network_service import VegaServiceNetwork

from vega_sim.scenario.common.agents import (
    MarketOrderTrader,
    BackgroundMarket,
)


class Fairground(Scenario):
    def __init__(
        self,
        num_steps: int = 5,
        step_length_seconds: int = 1,
        market_name: str = None,
        bm_kappa: float = 1,
        bm_spread: int = 2,
        mo_buy_intensity: float = 200,
        mo_sell_intensity: float = 200,
        mo_base_order_size: float = 0.01,
        bm_tick_spacing: float = 0.002,
        bm_number_levels_per_side: int = 20,
        state_extraction_freq: int = 1,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNetwork, List[Agent]], Any]
        ] = None,
        pp_fn: Optional[Callable[[None], List[float]]] = None,
        pp_sigma: float = 0.01,
    ):

        self.num_steps = num_steps
        self.step_length_seconds = step_length_seconds

        self.market_name = market_name
        self.market_decimal = None
        self.asset_name = None
        self.asset_decimal = None
        self.market_position_decimal = None

        self.bm_kappa = bm_kappa
        self.bm_spread = bm_spread
        self.bm_tick_spacing = bm_tick_spacing
        self.bm_number_levels_per_side = bm_number_levels_per_side

        self.mo_buy_intensity = mo_buy_intensity
        self.mo_sell_intensity = mo_sell_intensity
        self.mo_base_order_size = mo_base_order_size

        self.state_extraction_freq = state_extraction_freq
        self.state_extraction_fn = state_extraction_fn

        self.pp_fn = pp_fn
        self.pp_sigma = pp_sigma

    def set_up_background_market(
        self,
        vega: VegaServiceNetwork,
        tag: str = "",
        random_state: Optional[np.random.RandomState] = None,
    ) -> NetworkEnvironment:

        self.market_id = [
            m.id
            for m in vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]

        market_info = vega.market_info(market_id=self.market_id)
        market_data = vega.market_data(market_id=self.market_id)

        self.market_decimal = market_info.decimal_places
        initial_price = int(market_data.static_mid_price) * 10 ** -int(
            self.market_decimal
        )

        self.asset_name = (
            market_info.tradable_instrument.instrument.future.settlement_asset
        )
        self.asset_id = vega.find_asset_id(symbol=self.asset_name)

        mo_trader_a = MarketOrderTrader(
            wallet_name="MarketOrderTraderA",
            wallet_pass="walletpass",
            market_name=self.market_name,
            asset_name=self.asset_name,
            tag=str(tag),
            buy_intensity=self.mo_buy_intensity,
            sell_intensity=self.mo_sell_intensity,
            base_order_size=self.mo_base_order_size,
            random_state=random_state,
        )
        mo_trader_b = MarketOrderTrader(
            wallet_name="MarketOrderTraderB",
            wallet_pass="walletpass",
            market_name=self.market_name,
            asset_name=self.asset_name,
            tag=str(tag),
            buy_intensity=self.mo_buy_intensity,
            sell_intensity=self.mo_sell_intensity,
            base_order_size=self.mo_base_order_size,
            random_state=random_state,
        )
        mo_trader_c = MarketOrderTrader(
            wallet_name="MarketOrderTraderC",
            wallet_pass="walletpass",
            market_name=self.market_name,
            asset_name=self.asset_name,
            tag=str(tag),
            buy_intensity=self.mo_buy_intensity,
            sell_intensity=self.mo_sell_intensity,
            base_order_size=self.mo_base_order_size,
            random_state=random_state,
        )

        env = NetworkEnvironment(
            agents=[
                mo_trader_a,
                mo_trader_b,
                mo_trader_c,
            ],
            n_steps=self.num_steps,
            vega_service=vega,
            step_length_seconds=self.step_length_seconds,
            state_extraction_freq=self.state_extraction_freq,
            state_extraction_fn=self.state_extraction_fn,
        )

        return env

    def run_iteration(
        self,
        vega: VegaServiceNetwork,
        random_state: Optional[np.random.RandomState] = None,
    ):
        env = self.set_up_background_market(
            vega=vega, tag="", random_state=random_state
        )
        result = env.run()
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

    scenario = Fairground(
        num_steps=200,
        step_length_seconds=1,
        market_name="UNIDAI Monthly (30 Jun 2022)",
    )

    with VegaServiceNetwork(
        warn_on_raw_data_access=False,
    ) as vega:
        scenario.run_iteration(vega=vega)
