"""scenario.py
 
Module runs a Fairground scenario on the specified network. The nullchain
network can be used to test market and agent parameters before deploying the
scenario on a live network such as fairground.
 
The default wallet names, keys, and passes are contained in the agents.py file
can be modified to match the users local wallet (required for running on a
Vega network, not required for running on nullchain).
 
"""
import requests
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Union

from vega_sim.scenario.constants import Network

from vega_sim.scenario.scenario import Scenario
from vega_sim.null_service import VegaServiceNull
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.environment.environment import (
    MarketEnvironmentWithState,
    NetworkEnvironment,
)
from vega_sim.environment.agent import Agent
from vega_sim.scenario.common.utils.price_process import (
    get_historic_price_series,
    Granularity,
)
from vega_sim.scenario.common.agents import (
    MarketManager,
    ExponentialShapedMarketMaker,
    OpenAuctionPass,
    MarketOrderTrader,
    MomentumTrader,
    PriceSensitiveMarketOrderTrader,
)
from vega_sim.scenario.fairground.agents import (
    WALLET_NAME,
    WALLET_PASS,
    MARKET_MANAGER_KEY,
    MARKET_MAKER_KEY,
    AUCTION_PASS_KEYS,
    RANDOM_MARKET_ORDER_AGENT_KEYS,
    MOMENTUM_MARKET_ORDER_AGENT_KEYS,
    SENSITIVE_MARKET_ORDER_AGENT_KEYS,
)


class LivePrice:
    """Iterator for getting a live product price process.

    Class is to be used when running the scenario on fairground incentives. The
    iterator can be passed to the market-maker agent and the price-sensitive
    agents to give them information regarding the live product price.

    """

    def __init__(self, product: str = "ADAUSDT"):
        self.product = product

    def __iter__(self):
        return self

    def __getitem__(self, index):
        return self._get_price()

    def __next__(self):
        return self._get_price()

    def _get_price(self):
        url = f"https://api.binance.com/api/v3/avgPrice?symbol={self.product}"
        return float(requests.get(url).json()["price"])


# Set default scenario arguments
PRICE_PROCESS_ARGS = {
    "binance_product": "ADAUSDT",
    "coinbase_product": "ADA-USD",
    "start": "2022-08-01 00:00:00",
    "randomise": False,
}
MARKET_MANAGER_ARGS = {
    "initial_mint": 1e08,
    "commitment_amount": 1e02,
    "market_name": "ADA Monthly (Historic)",
    "asset_name": "tUSD",
    "adp": 4,
    "mdp": 4,
    "pdp": 4,
}
MARKET_MAKER_ARGS = {
    "initial_asset_mint": 1e08,
    "commitment_amount": 1e03,
    "kappa": 1000,
    "market_kappa": 2000,
    "market_order_arrival_rate": 400,
    "num_levels": 20,
    "tick_spacing": 0.001,
    "order_unit_size": 100,
    "inventory_upper_boundary": 80,
    "inventory_lower_boundary": -80,
}
AUCTION_PASS_ARGS = {
    "initial_asset_mint": 1e06,
    "side": ["SIDE_BUY", "SIDE_SELL"],
    "initial_price": None,
    "opening_auction_trade_amount": 10,
}
RANDOM_MARKET_ORDER_ARG = {
    "initial_asset_mint": 1e06,
    "buy_intensity": 1,
    "sell_intensity": 1,
}
MOMENTUM_MARKET_ORDER_ARGS = {
    "initial_asset_mint": 1e06,
    "momentum_strategies": ["MACD", "APO", "RSI", "STOCHRSI", "CPO"],
    "order_intensity": 5,
}
SENSITIVE_MARKET_ORDER_ARGS = {
    "initial_asset_mint": 1e06,
    "buy_intensity": 5,
    "sell_intensity": 5,
}


class Fairground(Scenario):
    """Scenario for simulating a realistic market on Fairground.

    Creates a scenario which can be run locally on a nullchain network and
    run on an existing public or internal Vega network. The scenario contains
    the following features:

    • ExponentialShapedMarketMaker agent which provides a market for traders
    • OpenAuctionPass agents which provide an initial best bid and ask
    • MarketOrderTrader agents which provide trades.
    • MomentumTrader agents which provide trades.
    • PriceSensitiveMarketOrder agents which provide trades.

    • MarketManager agent which proposes and settles a market (only required
      when scenario is run on a local nullchain network).

    """

    def __init__(
        self,
        block_length_seconds: int = 1,
        n_steps: int = 60 * 24 * 2,
        granularity: Optional[Granularity] = Granularity.MINUTE,
        market_manager_args: Optional[dict] = None,
        market_maker_args: Optional[dict] = None,
        auction_pass_args: Optional[dict] = None,
        random_market_order_args: Optional[dict] = None,
        momentum_market_order_args: Optional[dict] = None,
        sensitive_market_order_args: Optional[dict] = None,
        price_process_args: Optional[dict] = None,
    ):
        """_summary_

        Args:
            block_length_seconds (float):
                Length of each block in seconds.
            n_steps (int, optional):
                Number of steps to run scenario for. Defaults to 60*24.
            granularity (Optional[Granularity], optional):
                Granularity of each step. Defaults to Granularity.MINUTE.
            price_process args (Optional[dict], optional):
                Args used to setup the price-process.
            market_manager_args (Optional[dict], optional):
                Args used to setup MarketManager agent.
            market_maker_args (Optional[dict], optional):
                Args used to setup ExponentialShapedMarketMaker agent.
            auction_pass_args (Optional[dict], optional):
                Args used to setup OpenAuctionPass agent.
            random_market_order_args (Optional[dict], optional):
                Args used to setup MarketOrderTrader agents.
            momentum_market_order_args (Optional[dict], optional):
                Args used to setup MomentumTrader agents.
            sensitive_market_order_args (Optional[dict], optional):
                Args used to setup PriceSensitveMarketOrder agents.
        """

        self.block_length_seconds = block_length_seconds
        self.n_steps = n_steps
        self.granularity = granularity

        # Set price-process arguments
        # Set agent arguments
        self.price_process_args = (
            price_process_args
            if market_manager_args is not None
            else PRICE_PROCESS_ARGS
        )

        # Set agent arguments
        self.market_manager_args = (
            market_manager_args
            if market_manager_args is not None
            else MARKET_MANAGER_ARGS
        )
        self.market_maker_args = (
            market_maker_args if market_maker_args is not None else MARKET_MAKER_ARGS
        )
        self.auction_pass_args = (
            auction_pass_args if auction_pass_args is not None else AUCTION_PASS_ARGS
        )
        self.random_market_order_args = (
            random_market_order_args
            if random_market_order_args is not None
            else RANDOM_MARKET_ORDER_ARG
        )
        self.momentum_market_order_args = (
            momentum_market_order_args
            if momentum_market_order_args is not None
            else MOMENTUM_MARKET_ORDER_ARGS
        )
        self.sensitive_market_order_args = (
            sensitive_market_order_args
            if sensitive_market_order_args is not None
            else SENSITIVE_MARKET_ORDER_ARGS
        )

    def _get_price_process(
        self,
        random_state,
    ) -> list:

        start = datetime.strptime(self.price_process_args["start"], "%Y-%m-%d %H:%M:%S")
        if self.price_process_args["randomise"]:
            start = start + timedelta(days=int(random_state.choice(range(30))))

        end = start + timedelta(seconds=self.n_steps * self.granularity.value)

        price_process = get_historic_price_series(
            product_id=self.price_process_args["coinbase_product"],
            granularity=self.granularity,
            start=str(start),
            end=str(end),
        )

        return list(price_process)

    def _setup(
        self,
        network: Network,
        random_state: Optional[np.random.RandomState] = None,
    ):

        random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

        if network == Network.NULLCHAIN:

            self.price_process = self._get_price_process(random_state=random_state)

            # Setup agent for proposing and settling the market
            market_manager = MarketManager(
                wallet_name=WALLET_NAME,
                wallet_pass=WALLET_PASS,
                key_name=MARKET_MANAGER_KEY,
                terminate_wallet_name=WALLET_NAME,
                terminate_wallet_pass=WALLET_PASS,
                terminate_key_name="TERMINATE_KEY",
                market_name=self.market_manager_args["market_name"],
                asset_name=self.market_manager_args["asset_name"],
                asset_decimal=self.market_manager_args["adp"],
                market_decimal=self.market_manager_args["mdp"],
                market_position_decimal=self.market_manager_args["pdp"],
                initial_mint=self.market_manager_args["initial_mint"],
                commitment_amount=self.market_manager_args["commitment_amount"],
                settlement_price=self.price_process[-1],
            )

        else:

            market_manager = Agent()
            self.price_process = LivePrice(
                product=self.price_process_args["binance_product"]
            )

        # Setup agent for proving a market for traders
        market_maker = ExponentialShapedMarketMaker(
            wallet_name=WALLET_NAME,
            wallet_pass=WALLET_PASS,
            key_name=MARKET_MAKER_KEY,
            market_name=self.market_manager_args["market_name"],
            asset_name=self.market_manager_args["asset_name"],
            initial_asset_mint=self.market_maker_args["initial_asset_mint"],
            commitment_amount=self.market_maker_args["commitment_amount"],
            market_kappa=self.market_maker_args["market_kappa"],
            kappa=self.market_maker_args["kappa"],
            num_levels=self.market_maker_args["num_levels"],
            tick_spacing=self.market_maker_args["tick_spacing"],
            order_unit_size=self.market_maker_args["order_unit_size"],
            inventory_lower_boundary=self.market_maker_args["inventory_lower_boundary"],
            inventory_upper_boundary=self.market_maker_args["inventory_upper_boundary"],
            num_steps=self.n_steps,
            price_process_generator=iter(self.price_process),
            orders_from_stream=False,
        )

        # Setup agents for passing opening auction
        auction_pass_agents = [
            OpenAuctionPass(
                wallet_name=WALLET_NAME,
                wallet_pass=WALLET_PASS,
                key_name=key,
                market_name=self.market_manager_args["market_name"],
                asset_name=self.market_manager_args["asset_name"],
                initial_asset_mint=self.auction_pass_args["initial_asset_mint"],
                initial_price=(
                    self.auction_pass_args["initial_price"]
                    if self.auction_pass_args["initial_price"] is not None
                    else self.price_process[0]
                ),
                side=self.auction_pass_args["side"][i],
            )
            for i, key in enumerate(AUCTION_PASS_KEYS)
        ]

        # Setup agents for placing random market orders
        random_market_order_traders = [
            MarketOrderTrader(
                wallet_name=WALLET_NAME,
                wallet_pass=WALLET_PASS,
                key_name=key,
                market_name=self.market_manager_args["market_name"],
                asset_name=self.market_manager_args["asset_name"],
                initial_asset_mint=self.random_market_order_args["initial_asset_mint"],
                buy_intensity=self.random_market_order_args["buy_intensity"],
                sell_intensity=self.random_market_order_args["sell_intensity"],
            )
            for i, key in enumerate(RANDOM_MARKET_ORDER_AGENT_KEYS)
        ]

        # Setup agents for placing momentum based market orders
        momentum_market_order_traders = [
            MomentumTrader(
                wallet_name=WALLET_NAME,
                wallet_pass=WALLET_PASS,
                key_name=key,
                market_name=self.market_manager_args["market_name"],
                asset_name=self.market_manager_args["asset_name"],
                momentum_strategy=self.momentum_market_order_args[
                    "momentum_strategies"
                ][i],
                initial_asset_mint=self.momentum_market_order_args[
                    "initial_asset_mint"
                ],
                order_intensity=self.momentum_market_order_args["order_intensity"],
            )
            for i, key in enumerate(MOMENTUM_MARKET_ORDER_AGENT_KEYS)
        ]

        # Setup agents for placing price-sensitive market orders
        sensitive_market_order_traders = [
            PriceSensitiveMarketOrderTrader(
                wallet_name=WALLET_NAME,
                wallet_pass=WALLET_PASS,
                key_name=key,
                market_name=self.market_manager_args["market_name"],
                asset_name=self.market_manager_args["asset_name"],
                price_process_generator=iter(self.price_process),
                initial_asset_mint=self.sensitive_market_order_args[
                    "initial_asset_mint"
                ],
                buy_intensity=self.sensitive_market_order_args["buy_intensity"],
                sell_intensity=self.sensitive_market_order_args["sell_intensity"],
            )
            for i, key in enumerate(SENSITIVE_MARKET_ORDER_AGENT_KEYS)
        ]

        agents = (
            [
                market_manager,
                market_maker,
            ]
            + auction_pass_agents
            + random_market_order_traders
            + momentum_market_order_traders
            + sensitive_market_order_traders
        )

        return agents

    def run_iteration(
        self,
        network: Network,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        pause_at_completion: bool = False,
        run_with_console: bool = False,
        random_state: Optional[np.random.RandomState] = None,
    ):

        agents = self._setup(network=network, random_state=random_state)

        if network == Network.NULLCHAIN:
            env = MarketEnvironmentWithState(
                agents=agents,
                n_steps=self.n_steps,
                vega_service=vega,
                step_length_seconds=self.granularity.value,
                block_length_seconds=self.block_length_seconds,
            )
            env.run(
                run_with_console=run_with_console,
                pause_at_completion=pause_at_completion,
            )
        else:
            env = NetworkEnvironment(
                agents=agents,
                n_steps=self.n_steps,
                vega_service=vega,
                step_length_seconds=self.granularity.value,
            )
            env.run()


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    scenario = Fairground()

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=True,
        seconds_per_block=1,
        transactions_per_block=100,
    ) as vega:
        scenario.run_scenario(vega=vega)
