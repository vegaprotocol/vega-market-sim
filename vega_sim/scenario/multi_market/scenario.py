"""vega_load_test.scenario.py

Module contains a VegaLoadTest class for setting up a vega-market-sim scenario capable
of load testing the vega node and data nodes as well as generating data across long
periods.The number of parties, orders per second, and trades per second can be 
configured to vary the load on the vega node and date node.

A VegaLoadTest scenario contains the following agents for each market:

    • MarketManager - propose and settle markets
    • ExponentialShapedMarketMaker - provide order book depth
    • OpenAuctionPass - provide limit orders to pass opening auction
    • LimitOrderTrader - provide limit orders to meet orders per second quota
    • MarketOrderTrader - provide market orders to meet trades per second quota

Arguments:

    Currently market makers are optimised for the hard-coded default market arguments 
    and data sources which are configured by the following module level arguments.

    • START_DATE: start date for price data source
    • MARKET_A_ARGS: dictionary defining market a parameters
    • MARKET_B_ARGS: dictionary defining market b parameters
    • MARKET_C_ARGS: dictionary defining market c parameters


Examples:

    Runs a standard a preconfigured load test scenario with realistic market traffic
    parameters. The market will appear in opening auction for a minute whilst the agents
    are initiated.

    $ python -m vega_sim.scenario.adhoc -s vega_load_test --console --pause --debug

"""

import argparse
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Callable, List
from vega_sim.scenario.common.utils.price_process import (
    Granularity,
    get_historic_price_series,
)

from vega_sim.scenario.scenario import Scenario
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.multi_market.agents import (
    MARKET_MANAGERS,
    MARKET_MAKERS,
    MARKET_PASSERS,
    MARKET_TRADERS,
)
from vega_sim.scenario.common.agents import (
    MarketManager,
    StateAgent,
    OpenAuctionPass,
    ExponentialShapedMarketMaker,
    MarketOrderTrader,
    LimitOrderTrader,
)

START_DATE = "2021-06-01 00:00:00"

MARKET_A_ARGS = {
    "name": "ETH:USD (12 Month)",
    "restarts": 1,
    "oracle": "ETH-USD",
    "asset": "tUSD",
    "mdp": 5,
    "pdp": 2,
    "adp": 5,
}

MARKET_B_ARGS = {
    "name": "ETH:GBP (6 Month)",
    "restarts": 2,
    "oracle": "ETH-GBP",
    "asset": "tGBP",
    "mdp": 5,
    "pdp": 2,
    "adp": 5,
}

MARKET_C_ARGS = {
    "name": "BTC:EUR (1 Month)",
    "restarts": 12,
    "oracle": "BTC-EUR",
    "asset": "tEUR",
    "mdp": 5,
    "pdp": 2,
    "adp": 5,
}


class VegaLoadTest(Scenario):
    def __init__(
        self,
        num_steps: int = 60 * 24 * 30 * 3,
        granularity: Granularity = Granularity.HOUR,
        step_length_seconds: float = 60,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        parties_per_market: int = 1000,
        orders_per_second: int = 100,
        trades_per_second: int = 1,
        start_date: str = None,
        market_a_args: Optional[dict] = None,
        market_b_args: Optional[dict] = None,
        market_c_args: Optional[dict] = None,
        initial_asset_mint=1e9,
        price_process_fn: Optional[Callable] = None,
    ):
        super().__init__()

        self.num_steps = num_steps
        self.granularity = granularity
        self.step_length_seconds = step_length_seconds
        self.interpolation = (
            f"{step_length_seconds}S"
            if step_length_seconds < granularity.value
            else None
        )

        self.block_length_seconds = block_length_seconds
        self.transactions_per_block = transactions_per_block

        self.start_date = start_date if start_date is not None else START_DATE

        self.market_a_args = (
            market_a_args if market_a_args is not None else MARKET_A_ARGS
        )
        self.market_b_args = (
            market_b_args if market_b_args is not None else MARKET_B_ARGS
        )
        self.market_c_args = (
            market_c_args if market_c_args is not None else MARKET_C_ARGS
        )

        self.initial_asset_mint = initial_asset_mint

        self.num_lo_traders_per_market = min(
            [orders_per_second, parties_per_market - 1]
        )
        self.num_mo_traders_per_market = (
            parties_per_market - self.num_lo_traders_per_market
        )

        self.market_order_trader_step_bias = (
            trades_per_second / self.num_mo_traders_per_market
        ) * self.granularity.value

        self.price_process_fn = price_process_fn

    def _generate_price_process(self, asset: str) -> list:
        start = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
        end = start + timedelta(seconds=self.num_steps * self.step_length_seconds)

        price_process = get_historic_price_series(
            product_id=asset,
            granularity=self.granularity,
            start=str(start),
            end=str(end),
            interpolation=self.interpolation,
        )

        return list(price_process)

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: str,
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> List[StateAgent]:
        logging.info(f"Downloading historical data for Market A.")
        market_a_price_process = (
            self.price_process_fn()
            if self.price_process_fn is not None
            else self._generate_price_process(asset=self.market_a_args["oracle"])
        )
        logging.info(f"Downloading historical data for Market B.")
        market_b_price_process = (
            self.price_process_fn()
            if self.price_process_fn is not None
            else self._generate_price_process(asset=self.market_b_args["oracle"])
        )
        logging.info(f"Downloading historical data for Market C.")
        market_c_price_process = (
            self.price_process_fn()
            if self.price_process_fn is not None
            else self._generate_price_process(asset=self.market_c_args["oracle"])
        )

        # Create MarketManager agents
        market_a_manager = MarketManager(
            wallet_name=MARKET_MANAGERS["MARKET_A_CREATOR"].wallet_name,
            key_name=MARKET_MANAGERS["MARKET_A_CREATOR"].key_name,
            terminate_wallet_name=MARKET_MANAGERS["MARKET_A_SETTLER"].wallet_name,
            terminate_key_name=MARKET_MANAGERS["MARKET_A_SETTLER"].key_name,
            market_name=self.market_a_args["name"],
            asset_decimal=self.market_a_args["adp"],
            market_decimal=self.market_a_args["mdp"],
            market_position_decimal=self.market_a_args["pdp"],
            settlement_price=market_a_price_process[-1],
            tag="a",
        )
        market_b_manager = MarketManager(
            wallet_name=MARKET_MANAGERS["MARKET_B_CREATOR"].wallet_name,
            key_name=MARKET_MANAGERS["MARKET_B_CREATOR"].key_name,
            terminate_wallet_name=MARKET_MANAGERS["MARKET_B_SETTLER"].wallet_name,
            terminate_key_name=MARKET_MANAGERS["MARKET_B_SETTLER"].key_name,
            market_name=self.market_b_args["name"],
            asset_decimal=self.market_b_args["adp"],
            market_decimal=self.market_b_args["mdp"],
            market_position_decimal=self.market_b_args["pdp"],
            settlement_price=market_b_price_process[-1],
            tag="b",
        )
        market_c_manager = MarketManager(
            wallet_name=MARKET_MANAGERS["MARKET_B_CREATOR"].wallet_name,
            key_name=MARKET_MANAGERS["MARKET_B_CREATOR"].key_name,
            terminate_wallet_name=MARKET_MANAGERS["MARKET_C_SETTLER"].wallet_name,
            terminate_key_name=MARKET_MANAGERS["MARKET_C_SETTLER"].key_name,
            market_name=self.market_c_args["name"],
            asset_name=self.market_c_args["asset"],
            asset_decimal=self.market_c_args["adp"],
            market_decimal=self.market_c_args["mdp"],
            market_position_decimal=self.market_c_args["pdp"],
            settlement_price=market_c_price_process[-1],
            tag="c",
        )

        #  Create ExponentialShapedMarketMaker agents
        market_a_maker = ExponentialShapedMarketMaker(
            wallet_name=MARKET_MAKERS["MARKET_A_MAKER"].wallet_name,
            key_name=MARKET_MAKERS["MARKET_A_MAKER"].key_name,
            price_process_generator=iter(market_a_price_process),
            initial_asset_mint=self.initial_asset_mint,
            market_name=self.market_a_args["name"],
            commitment_amount=1e6,
            market_decimal_places=self.market_a_args["mdp"],
            num_steps=self.num_steps,
            kappa=0.2,
            tick_spacing=1,
            market_kappa=10,
            state_update_freq=10,
            tag="a",
        )
        market_b_maker = ExponentialShapedMarketMaker(
            wallet_name=MARKET_MAKERS["MARKET_B_MAKER"].wallet_name,
            key_name=MARKET_MAKERS["MARKET_B_MAKER"].key_name,
            price_process_generator=iter(market_b_price_process),
            initial_asset_mint=self.initial_asset_mint,
            market_name=self.market_b_args["name"],
            commitment_amount=1e6,
            market_decimal_places=self.market_b_args["mdp"],
            num_steps=self.num_steps,
            kappa=0.2,
            tick_spacing=1,
            market_kappa=10,
            state_update_freq=10,
            tag="b",
        )
        market_c_maker = ExponentialShapedMarketMaker(
            wallet_name=MARKET_MAKERS["MARKET_C_MAKER"].wallet_name,
            key_name=MARKET_MAKERS["MARKET_C_MAKER"].key_name,
            price_process_generator=iter(market_c_price_process),
            initial_asset_mint=self.initial_asset_mint,
            market_name=self.market_c_args["name"],
            commitment_amount=1e6,
            market_decimal_places=self.market_c_args["mdp"],
            num_steps=self.num_steps,
            kappa=0.1,
            tick_spacing=2,
            market_kappa=5,
            state_update_freq=10,
            tag="c",
        )

        # Setup agents for passing auction
        market_a_passer_bid = OpenAuctionPass(
            wallet_name=MARKET_PASSERS["MARKET_A_PASSER_BID"].wallet_name,
            key_name=MARKET_PASSERS["MARKET_A_PASSER_BID"].key_name,
            side="SIDE_BUY",
            initial_asset_mint=self.initial_asset_mint,
            initial_price=market_a_price_process[0],
            market_name=self.market_a_args["name"],
            opening_auction_trade_amount=1,
            tag="a_bid",
        )
        market_a_passer_ask = OpenAuctionPass(
            wallet_name=MARKET_PASSERS["MARKET_A_PASSER_ASK"].wallet_name,
            key_name=MARKET_PASSERS["MARKET_A_PASSER_ASK"].key_name,
            side="SIDE_SELL",
            initial_asset_mint=self.initial_asset_mint,
            initial_price=market_a_price_process[0],
            market_name=self.market_a_args["name"],
            opening_auction_trade_amount=1,
            tag="a_ask",
        )
        market_b_passer_bid = OpenAuctionPass(
            wallet_name=MARKET_PASSERS["MARKET_B_PASSER_BID"].wallet_name,
            key_name=MARKET_PASSERS["MARKET_B_PASSER_BID"].key_name,
            side="SIDE_BUY",
            initial_asset_mint=self.initial_asset_mint,
            initial_price=market_b_price_process[0],
            market_name=self.market_b_args["name"],
            opening_auction_trade_amount=1,
            tag="b_bid",
        )
        market_b_passer_ask = OpenAuctionPass(
            wallet_name=MARKET_PASSERS["MARKET_B_PASSER_ASK"].wallet_name,
            key_name=MARKET_PASSERS["MARKET_B_PASSER_ASK"].key_name,
            side="SIDE_SELL",
            initial_asset_mint=self.initial_asset_mint,
            initial_price=market_b_price_process[0],
            market_name=self.market_b_args["name"],
            opening_auction_trade_amount=1,
            tag="b_ask",
        )
        market_c_passer_bid = OpenAuctionPass(
            wallet_name=MARKET_PASSERS["MARKET_C_PASSER_BID"].wallet_name,
            key_name=MARKET_PASSERS["MARKET_C_PASSER_BID"].key_name,
            side="SIDE_BUY",
            initial_asset_mint=self.initial_asset_mint,
            initial_price=market_c_price_process[0],
            market_name=self.market_c_args["name"],
            opening_auction_trade_amount=1,
            tag="c_bid",
        )
        market_c_passer_ask = OpenAuctionPass(
            wallet_name=MARKET_PASSERS["MARKET_C_PASSER_ASK"].wallet_name,
            key_name=MARKET_PASSERS["MARKET_C_PASSER_ASK"].key_name,
            side="SIDE_SELL",
            initial_asset_mint=self.initial_asset_mint,
            initial_price=market_c_price_process[0],
            market_name=self.market_c_args["name"],
            opening_auction_trade_amount=1,
            tag="c_ask",
        )

        market_a_lo_traders = [
            LimitOrderTrader(
                wallet_name=MARKET_TRADERS[
                    f"MARKET_A_TRADER_{str(i).zfill(4)}"
                ].wallet_name,
                key_name=MARKET_TRADERS[f"MARKET_A_TRADER_{str(i).zfill(4)}"].key_name,
                market_name=self.market_a_args["name"],
                buy_intensity=10,
                sell_intensity=10,
                buy_volume=1,
                sell_volume=1,
                submit_bias=1,
                cancel_bias=1,
                tag="market_a_" + str(i),
            )
            for i in range(self.num_lo_traders_per_market)
        ]

        market_b_lo_traders = [
            LimitOrderTrader(
                wallet_name=MARKET_TRADERS[
                    f"MARKET_A_TRADER_{str(i).zfill(4)}"
                ].wallet_name,
                key_name=MARKET_TRADERS[f"MARKET_A_TRADER_{str(i).zfill(4)}"].key_name,
                market_name=self.market_a_args["name"],
                buy_intensity=10,
                sell_intensity=10,
                buy_volume=1,
                sell_volume=1,
                submit_bias=1,
                cancel_bias=1,
                tag="market_b_" + str(i),
            )
            for i in range(self.num_lo_traders_per_market)
        ]

        market_c_lo_traders = [
            LimitOrderTrader(
                wallet_name=MARKET_TRADERS[
                    f"MARKET_A_TRADER_{str(i).zfill(4)}"
                ].wallet_name,
                key_name=MARKET_TRADERS[f"MARKET_A_TRADER_{str(i).zfill(4)}"].key_name,
                market_name=self.market_a_args["name"],
                buy_intensity=10,
                sell_intensity=10,
                buy_volume=0.1,
                sell_volume=0.1,
                submit_bias=1,
                cancel_bias=1,
                tag="market_c_" + str(i),
            )
            for i in range(self.num_lo_traders_per_market)
        ]

        market_a_mo_traders = [
            MarketOrderTrader(
                wallet_name=MARKET_TRADERS[
                    f"MARKET_A_TRADER_{str(i).zfill(4)}"
                ].wallet_name,
                key_name=MARKET_TRADERS[f"MARKET_A_TRADER_{str(i).zfill(4)}"].key_name,
                market_name=self.market_a_args["name"],
                buy_intensity=10,
                sell_intensity=10,
                base_order_size=1,
                step_bias=self.market_order_trader_step_bias,
                tag="market_a_" + str(i),
            )
            for i in range(self.num_mo_traders_per_market)
        ]
        market_b_mo_traders = [
            MarketOrderTrader(
                wallet_name=MARKET_TRADERS[
                    f"MARKET_B_TRADER_{str(i).zfill(4)}"
                ].wallet_name,
                key_name=MARKET_TRADERS[f"MARKET_B_TRADER_{str(i).zfill(4)}"].key_name,
                market_name=self.market_b_args["name"],
                buy_intensity=10,
                sell_intensity=10,
                base_order_size=1,
                step_bias=self.market_order_trader_step_bias,
                tag="market_b_" + str(i),
            )
            for i in range(self.num_mo_traders_per_market)
        ]
        market_c_mo_traders = [
            MarketOrderTrader(
                wallet_name=MARKET_TRADERS[
                    f"MARKET_C_TRADER_{str(i).zfill(4)}"
                ].wallet_name,
                key_name=MARKET_TRADERS[f"MARKET_C_TRADER_{str(i).zfill(4)}"].key_name,
                market_name=self.market_c_args["name"],
                buy_intensity=10,
                sell_intensity=10,
                base_order_size=0.1,
                step_bias=self.market_order_trader_step_bias,
                tag="market_c_" + str(i),
            )
            for i in range(self.num_mo_traders_per_market)
        ]

        agents = (
            [
                market_a_manager,
                market_b_manager,
                market_c_manager,
                market_a_passer_bid,
                market_a_passer_ask,
                market_b_passer_bid,
                market_b_passer_ask,
                market_c_passer_bid,
                market_c_passer_ask,
                market_a_maker,
                market_b_maker,
                market_c_maker,
            ]
            + market_a_lo_traders
            + market_b_lo_traders
            + market_c_lo_traders
            + market_a_mo_traders
            + market_b_mo_traders
            + market_c_mo_traders
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

    scenario = VegaLoadTest(
        num_steps=10000,
        granularity=Granularity.FIFTEEN_MINUTE,
        block_length_seconds=1,
        transactions_per_block=4096,
    )

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=False,
        use_full_vega_wallet=False,
        retain_log_files=True,
        launch_graphql=False,
        seconds_per_block=scenario.block_length_seconds,
        transactions_per_block=scenario.transactions_per_block,
    ) as vega:
        scenario.run_iteration(
            vega=vega,
            pause_at_completion=False,
        )
