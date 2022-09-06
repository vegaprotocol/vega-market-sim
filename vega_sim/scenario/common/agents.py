from __future__ import annotations
from dataclasses import dataclass
from multiprocessing.connection import wait
from random import random
from time import time

import numpy as np

from math import exp

from collections import namedtuple
from typing import List, Optional, Union
from numpy.typing import ArrayLike
from vega_sim.api.data import Order

from vega_sim.environment import VegaState
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import markets as markets_protos, vega as vega_protos

import vega_sim.proto.data_node.api.v1 as data_node_protos


WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Send selling/buying MOs to hit LP orders
TRADER_WALLET = WalletConfig("trader", "trader")

BACKGROUND_MARKET = WalletConfig("market", "market")

# Pass opening auction
AUCTION1_WALLET = WalletConfig("AUCTION1", "AUCTION1pass")
AUCTION2_WALLET = WalletConfig("AUCTION2", "AUCTION2pass")


@dataclass
class MarketRegime:
    spread: float
    tick_spacing: float
    num_levels_per_side: int
    base_volume_size: float
    order_distribution_buy_kappa: float
    order_distribution_sell_kappa: float
    from_timepoint: int  # Inclusive
    thru_timepoint: int  # Inclusive


class MarketOrderTrader(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        market_name: str,
        asset_name: str,
        initial_asset_mint: float = 1000000,
        buy_intensity: float = 1,
        sell_intensity: float = 1,
        tag: str = "",
        random_state: Optional[np.random.RandomState] = None,
        base_order_size: float = 1,
    ):
        super().__init__(wallet_name + str(tag), wallet_pass)
        self.initial_asset_mint = initial_asset_mint
        self.buy_intensity = buy_intensity
        self.sell_intensity = sell_intensity
        self.tag = tag
        self.market_name = market_name
        self.asset_name = asset_name
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )
        self.base_order_size = base_order_size

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet
        super().initialise(vega=vega)
        # Get market id
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]

        # Get asset id
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=self.asset_id,
            amount=self.initial_asset_mint,
        )
        self.vega.wait_fn(5)

    def step(self, vega_state: VegaState):
        buy_first = self.random_state.choice([0, 1])

        buy_vol = self.random_state.poisson(self.buy_intensity) * self.base_order_size
        sell_vol = self.random_state.poisson(self.sell_intensity) * self.base_order_size
        if buy_first:
            self.place_order(
                vega_state=vega_state,
                volume=buy_vol,
                side=vega_protos.SIDE_BUY,
            )

        self.place_order(
            vega_state=vega_state,
            volume=sell_vol,
            side=vega_protos.SIDE_SELL,
        )

        if not buy_first:
            self.place_order(
                vega_state=vega_state,
                volume=buy_vol,
                side=vega_protos.SIDE_BUY,
            )

    def place_order(self, vega_state: VegaState, volume: float, side: vega_protos.Side):
        if (
            (
                vega_state.market_state[self.market_id].trading_mode
                == markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS
            )
            and vega_state.market_state[self.market_id].state
            == markets_protos.Market.State.STATE_ACTIVE
            and volume != 0
        ):
            self.vega.submit_market_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                side=side,
                volume=volume,
                wait=False,
                fill_or_kill=False,
            )


class BackgroundMarket(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        market_name: str,
        asset_name: str,
        price_process: List[float],
        initial_asset_mint: float = 1000000,
        position_decimals: int = 4,
        spread: float = 0.02,
        tick_spacing: float = 0.01,
        num_levels_per_side: int = 20,
        base_volume_size: float = 0.1,
        order_distribution_kappa: float = 1,
        tag: str = "",
    ):
        super().__init__(wallet_name + tag, wallet_pass)
        self.price_process = price_process
        self.initial_asset_mint = initial_asset_mint
        self.spread = spread
        self.current_step = 0
        self.tag = tag
        self.tick_spacing = tick_spacing
        self.num_levels_per_side = num_levels_per_side
        self.base_volume_size = base_volume_size

        self.market_name = market_name
        self.asset_name = asset_name
        self.kappa = order_distribution_kappa
        self.position_decimals = position_decimals

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet
        super().initialise(vega=vega)
        # Get market id
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]

        # Get asset id
        asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=asset_id,
            amount=self.initial_asset_mint,
        )
        self.vega.wait_fn(2)

        initial_price = self.price_process[self.current_step]
        buy_shape = self._calculate_price_volume_levels(
            initial_price - self.spread / 2,
            initial_price,
            side=vega_protos.SIDE_BUY,
        )
        sell_shape = self._calculate_price_volume_levels(
            initial_price + self.spread / 2,
            initial_price,
            side=vega_protos.SIDE_SELL,
        )

        self.vega.wait_for_total_catchup()

        for price, size in buy_shape:
            if price > 0:
                self._submit_order(vega_protos.SIDE_BUY, price, size)
        for price, size in sell_shape:
            if price > 0:
                self._submit_order(vega_protos.SIDE_SELL, price, size)

    def _submit_order(
        self, side: Union[str, vega_protos.Side], price: float, size: float
    ) -> None:
        volume = round(size, self.position_decimals)
        if volume == 0:
            return
        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side=side,
            volume=volume,
            price=price,
            wait=False,
        )

    def _calculate_price_volume_levels(
        self,
        starting_level: float,
        mid_price: float,
        side: Union[str, vega_protos.Side],
        kappa: Optional[float] = None,
    ) -> ArrayLike:
        is_buy = side in ["SIDE_BUY", vega_protos.SIDE_BUY]
        kappa = kappa if kappa is not None else self.kappa

        base_level = abs(starting_level - mid_price)
        final_level = base_level + self.tick_spacing * self.num_levels_per_side
        levels = np.arange(base_level, final_level, self.tick_spacing)
        cumulative_vol = np.exp(kappa * levels) - 1

        level_vol = np.concatenate([cumulative_vol[:1], np.diff(cumulative_vol)])
        level_price = mid_price + (-1 if is_buy else 1) * levels

        return np.c_[level_price, level_vol]

    def step(self, vega_state: VegaState):
        self.current_step += 1

        orders = self.vega.orders_for_party_from_feed(
            self.wallet_name, self.market_id, live_only=True
        )
        new_price = self.price_process[self.current_step]
        new_buy_shape = self._calculate_price_volume_levels(
            new_price - self.spread / 2,
            new_price,
            side=vega_protos.SIDE_BUY,
        )
        new_sell_shape = self._calculate_price_volume_levels(
            new_price + self.spread / 2,
            new_price,
            side=vega_protos.SIDE_SELL,
        )

        buy_orders, sell_orders = [], []

        for order in orders.values():
            if order.side == vega_protos.SIDE_BUY:
                buy_orders.append(order)
            else:
                sell_orders.append(order)

        first_side = (
            vega_protos.SIDE_BUY
            if self.price_process[self.current_step]
            < self.price_process[self.current_step - 1]
            else vega_protos.SIDE_SELL
        )

        if first_side == vega_protos.SIDE_BUY:
            self._move_side(
                vega_protos.SIDE_BUY,
                self.num_levels_per_side,
                buy_orders,
                new_buy_shape,
            )
        self._move_side(
            vega_protos.SIDE_SELL,
            self.num_levels_per_side,
            sell_orders,
            new_sell_shape,
        )
        if first_side == vega_protos.SIDE_SELL:
            self._move_side(
                vega_protos.SIDE_BUY,
                self.num_levels_per_side,
                buy_orders,
                new_buy_shape,
            )

    def _move_side(
        self,
        side: vega_protos.Side,
        num_levels: int,
        orders: List[Order],
        new_shape: List[List[float, float]],
    ) -> None:
        for i in range(num_levels):
            if i < len(orders):
                order_to_amend = orders[i]
                self.vega.amend_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    order_id=order_to_amend.id,
                    price=new_shape[i][0],
                    volume_delta=new_shape[i][1] - order_to_amend.remaining,
                )
            else:
                self._submit_order(side, new_shape[i][0], new_shape[i][1])


class MultiRegimeBackgroundMarket(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        market_name: str,
        asset_name: str,
        price_process: List[float],
        market_regimes: List[MarketRegime],
        tag: str = "",
    ):
        """Generate a background market acting differently as time passes.
        Allows specification of varying numbers of non-overlapping regimes
        (with optional gaps in which no orders will be placed).

        Places an exponentially shaped Limit-Order-Book about a moving midprice.

        Args:
            wallet_name:
                str, The name of the wallet to use placing background orders
            wallet_pass:
                str, The password to use for the background order wallet
            market_name:
                str, The name of the market on which the agent will trade
            asset_name:
                str, The name of the asset to trade with
            price_process:
                List[float], A list of prices which the market will follow.
            market_regimes:
                List[MarketRegime], A list of specifications for market
                    regimes, allowing variation over time. Each specifies
                    a start/end date and are interpreted as a sparse set
            tag:
                str, a tag which will be added to the wallet name
        """
        super().__init__(wallet_name + tag, wallet_pass)
        self.price_process = price_process
        self.current_step = 0
        self.tag = tag

        self.market_name = market_name
        self.asset_name = asset_name

        self.market_regimes = self._market_regime_sparse_to_dense(
            market_regimes=market_regimes, num_steps=len(self.price_process) + 1
        )

    @staticmethod
    def _market_regime_sparse_to_dense(
        market_regimes: List[MarketRegime], num_steps: int
    ) -> List[MarketRegime]:
        regimes = []
        regimes_iter = iter(market_regimes)

        market_regime = next(regimes_iter)
        for i in range(num_steps):
            if market_regime.from_timepoint > i:
                regimes.append(None)
                continue
            elif market_regime.thru_timepoint < i:
                next_market_regime = next(regimes_iter)

                if next_market_regime.from_timepoint <= market_regime.thru_timepoint:
                    raise Exception(
                        "Overlapping regimes detected. {} starts before {} ends".format(
                            next_market_regime, market_regime
                        )
                    )
                else:
                    market_regime = next_market_regime

                regimes.append(
                    market_regime
                ) if market_regime.from_timepoint <= i else regimes.append(None)
            else:
                regimes.append(market_regime)
        return regimes

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet
        super().initialise(vega=vega)
        # Get market id
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]

        # Get asset id
        asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=asset_id,
            amount=200000,
        )
        self.vega.wait_fn(2)

        market_regime = self.market_regimes[0]
        initial_price = self.price_process[self.current_step]

        buy_shape = self._calculate_price_volume_levels(
            initial_price - market_regime.spread,
            initial_price,
            side=vega_protos.SIDE_BUY,
            kappa=market_regime.order_distribution_buy_kappa,
            tick_spacing=market_regime.tick_spacing,
            num_levels=market_regime.num_levels_per_side,
        )
        sell_shape = self._calculate_price_volume_levels(
            initial_price + market_regime.spread,
            initial_price,
            side=vega_protos.SIDE_SELL,
            kappa=market_regime.order_distribution_sell_kappa,
            tick_spacing=market_regime.tick_spacing,
            num_levels=market_regime.num_levels_per_side,
        )

        self.vega.wait_for_total_catchup()
        for price, size in buy_shape:
            if price > 0:
                self._submit_order(vega_protos.SIDE_BUY, price, size)
        for price, size in sell_shape:
            if price > 0:
                self._submit_order(vega_protos.SIDE_SELL, price, size)

    def _submit_order(
        self, side: Union[str, vega_protos.Side], price: float, size: float
    ) -> None:
        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side=side,
            volume=round(size, 4),
            price=price,
            wait=False,
        )

    def _calculate_price_volume_levels(
        self,
        starting_level: float,
        mid_price: float,
        side: Union[str, vega_protos.Side],
        kappa: float,
        tick_spacing: float,
        num_levels: int,
    ) -> ArrayLike:
        is_buy = side in ["SIDE_BUY", vega_protos.SIDE_BUY]

        base_level = abs(starting_level - mid_price)
        final_level = base_level + tick_spacing * num_levels
        levels = np.arange(base_level, final_level, tick_spacing)
        cumulative_vol = np.exp(kappa * levels) - 1

        level_vol = np.concatenate([cumulative_vol[:1], np.diff(cumulative_vol)])
        level_price = mid_price + (-1 if is_buy else 1) * levels

        return np.c_[level_price, level_vol]

    def step(self, vega_state: VegaState):
        self.current_step += 1
        market_regime = self.market_regimes[self.current_step]

        orders = self.vega.orders_for_party_from_feed(
            self.wallet_name, self.market_id, live_only=True
        )

        if market_regime is None:
            for order in orders.values():
                self.vega.cancel_order(self.wallet_name, self.market_id, order.id)
        else:
            new_price = self.price_process[self.current_step]
            new_buy_shape = self._calculate_price_volume_levels(
                new_price - market_regime.spread,
                new_price,
                side=vega_protos.SIDE_BUY,
                kappa=market_regime.order_distribution_buy_kappa,
                tick_spacing=market_regime.tick_spacing,
                num_levels=market_regime.num_levels_per_side,
            )
            new_sell_shape = self._calculate_price_volume_levels(
                new_price + market_regime.spread,
                new_price,
                side=vega_protos.SIDE_SELL,
                kappa=market_regime.order_distribution_sell_kappa,
                tick_spacing=market_regime.tick_spacing,
                num_levels=market_regime.num_levels_per_side,
            )

            buy_orders, sell_orders = [], []

            for order in orders.values():
                if order.side == vega_protos.SIDE_BUY:
                    buy_orders.append(order)
                else:
                    sell_orders.append(order)

            # We want to first make the spread wider by moving the side which is in the
            # direction of the move (e.g. if price falls, the bids)
            first_side = (
                vega_protos.SIDE_BUY
                if self.price_process[self.current_step]
                < self.price_process[self.current_step - 1]
                else vega_protos.SIDE_SELL
            )
            if first_side == vega_protos.SIDE_BUY:
                self._move_side(
                    vega_protos.SIDE_BUY,
                    market_regime.num_levels_per_side,
                    buy_orders,
                    new_buy_shape,
                )
            self._move_side(
                vega_protos.SIDE_SELL,
                market_regime.num_levels_per_side,
                sell_orders,
                new_sell_shape,
            )
            if first_side == vega_protos.SIDE_SELL:
                self._move_side(
                    vega_protos.SIDE_BUY,
                    market_regime.num_levels_per_side,
                    buy_orders,
                    new_buy_shape,
                )

    def _move_side(
        self,
        side: vega_protos.Side,
        num_levels: int,
        orders: List[Order],
        new_shape: List[List[float, float]],
    ) -> None:
        for i in range(num_levels):
            if i < len(orders):
                order_to_amend = orders[i]
                self.vega.amend_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    order_id=order_to_amend.id,
                    price=new_shape[i][0],
                    volume_delta=new_shape[i][1] - order_to_amend.remaining,
                )
            else:
                self._submit_order(
                    side,
                    new_shape[i][0],
                    new_shape[i][1],
                )


class OpenAuctionPass(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        side: str,
        market_name: str,
        asset_name: str,
        initial_asset_mint: float = 1000000,
        initial_price: float = 0.3,
        opening_auction_trade_amount: float = 1,
        tag: str = "",
    ):
        super().__init__(wallet_name + str(tag), wallet_pass)
        self.side = side
        self.initial_asset_mint = initial_asset_mint
        self.initial_price = initial_price
        self.tag = tag
        self.market_name = market_name
        self.asset_name = asset_name
        self.opening_auction_trade_amount = opening_auction_trade_amount

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet
        super().initialise(vega=vega)
        # Get market id
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]

        self.vega.wait_for_total_catchup()
        # Get asset id
        asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=asset_id,
            amount=self.initial_asset_mint,
        )
        self.vega.wait_fn(10)
        self.vega.wait_for_total_catchup()

        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side=self.side,
            volume=self.opening_auction_trade_amount,
            price=self.initial_price,
            wait=False,
        )

    def step(self, vega_state: VegaState):
        pass


class MarketManager(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        terminate_wallet_name: str,
        terminate_wallet_pass: str,
        market_name: str,
        asset_name: str,
        asset_decimal: int = 5,
        market_decimal: int = 5,
        market_position_decimal: int = 2,
        commitment_amount: float = 0,
        settlement_price: Optional[float] = None,
        tag: str = "",
    ):
        super().__init__(wallet_name + str(tag), wallet_pass)
        self.terminate_wallet_name = terminate_wallet_name + str(tag)
        self.terminate_wallet_pass = terminate_wallet_pass

        self.adp = asset_decimal
        self.mdp = market_decimal
        self.market_position_decimal = market_position_decimal
        self.commitment_amount = commitment_amount

        self.current_step = 0

        self.tag = tag

        self.market_name = market_name
        self.asset_name = asset_name
        self.settlement_price = settlement_price

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet for LP/ Settle Party
        super().initialise(vega=vega)
        self.vega.create_wallet(self.terminate_wallet_name, self.terminate_wallet_pass)

        # Faucet vega tokens
        self.vega.wait_for_total_catchup()
        self.vega.mint(
            self.wallet_name,
            asset="VOTE",
            amount=1e4,
        )
        self.vega.wait_fn(5)
        self.vega.wait_for_total_catchup()

        # Create asset
        self.vega.create_asset(
            self.wallet_name,
            name=self.asset_name,
            symbol=self.asset_name,
            decimals=self.adp,
            max_faucet_amount=5e10,
        )
        self.vega.wait_fn(5)
        self.vega.wait_for_total_catchup()
        # Get asset id
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.initial = 2 * self.commitment_amount
        self.vega.mint(
            self.wallet_name,
            asset=self.asset_id,
            amount=self.initial,
        )
        self.vega.wait_fn(5)
        self.vega.wait_for_total_catchup()

        self.vega.update_network_parameter(
            self.wallet_name,
            "market.liquidity.minimum.probabilityOfTrading.lpOrders",
            "0.001",
        )

        self.vega.wait_for_total_catchup()
        self.vega.update_network_parameter(
            self.wallet_name,
            "market.liquidity.stakeToCcySiskas",
            "0.001",
        )

        self.vega.wait_for_total_catchup()
        # Set up a future market
        self.vega.create_simple_market(
            market_name=self.market_name,
            proposal_wallet=self.wallet_name,
            settlement_asset_id=self.asset_id,
            termination_wallet=self.terminate_wallet_name,
            market_decimals=self.mdp,
            position_decimals=self.market_position_decimal,
            future_asset=self.asset_name,
        )
        self.vega.wait_fn(5)

        # Get market id
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]
        if self.commitment_amount:
            self.vega.submit_liquidity(
                wallet_name=self.wallet_name,
                market_id=self.market_id,
                commitment_amount=self.commitment_amount,
                fee=0.002,
                buy_specs=[("PEGGED_REFERENCE_BEST_BID", 5, 1)],
                sell_specs=[("PEGGED_REFERENCE_BEST_ASK", 5, 1)],
                is_amendment=False,
            )

    def finalise(self):
        if self.settlement_price is not None:
            self.vega.settle_market(
                self.terminate_wallet_name, self.settlement_price, self.market_id
            )


class LimitOrderTrader(StateAgentWithWallet):
    """Agent which randomly submits and cancels limit orders.

    At initialisation; the agent creates a wallet, identifies the market id and
    the asset for that market, and mints itself the specified quantity of the
    required asset.

    At any given step; the agent has an adjustable probability of submitting
    an order and an adjustable probability of cancelling a randomly
    selected order.

    When submitting an order; the agent choses a price following a lognormal
    distribution where the underlying normal distribution can be adjusted.

    """

    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        market_name: str,
        asset_name: str,
        initial_asset_mint: float = 1000000,
        buy_volume: float = 1.0,
        sell_volume: float = 1.0,
        buy_intensity: float = 5,
        sell_intensity: float = 5,
        tag: str = "",
        random_state: Optional[np.random.RandomState] = None,
        submit_bias: float = 0.5,
        cancel_bias: float = 0.5,
        side_opts: Optional[dict] = None,
        time_in_force_opts: Optional[dict] = None,
        duration: Optional[float] = 120,
        price_process: Optional[list] = None,
        spread: Optional[float] = None,
        mean: Optional[float] = 2.0,
        sigma: Optional[float] = 1.0,
    ):
        """Init the object and class attributes.

        Args:
            wallet_name (str):
                Name of the agents wallet.
            wallet_pass (str):
                Passcode used by the agent to login to its wallet.
            market_name (str):
                Name of the market the agent is to place orders in.
            asset_name: (str):
                Name of the asset needed for the market.
            initial_asset_mint (float, optional):
                Quantity of the asset the agent should initially mint.
            buy_volume (float, optional):
                Volume used by agent on buy orders.
            sell_volume (float, optional):
                Volume used by agent on sell orders.
            tag (str, optional):
                String to tag to the market and asset name.
            random_state: (np.random.RandomState, optional):
                Object for creating distributions to randomly sampling from.
            submit_bias (float, optional):
                Probability agent attempts to submit a random order.
            cancel_bias (float, optional):
                Probability agent attempts to cancel a random order.
            side_opts(dict, optional):
                Dictionary of side options and probabilities.
            time_in_force_opts (dict, optional):
                Dictionary of time in force options and probabilities.
            duration (int, optional):
                Duration unfilled GTT orders should remain open in seconds.
            price_process(List[float]):
                Random walk (RW) of asset price.
            spread (int):
                Spread of the agent.
            mean (float, optional):
                Mean of the log-normal distribution.
            sigma (float, optional):
                Standard deviation of the log-normal distribution.
        """

        super().__init__(wallet_name + str(tag), wallet_pass)

        self.current_step = 0

        self.market_name = market_name
        self.asset_name = asset_name
        self.initial_asset_mint = initial_asset_mint
        self.buy_intensity = buy_intensity
        self.sell_intensity = sell_intensity
        self.buy_volume = buy_volume
        self.sell_volume = sell_volume
        self.tag = tag
        self.submit_bias = submit_bias
        self.cancel_bias = cancel_bias
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )
        self.side_opts = (
            side_opts if side_opts is not None else {"SIDE_BUY": 0.5, "SIDE_SELL": 0.5}
        )
        self.time_in_force_opts = (
            time_in_force_opts
            if time_in_force_opts is not None
            else {
                "TIME_IN_FORCE_GTC": 0.4,
                "TIME_IN_FORCE_GTT": 0.3,
                "TIME_IN_FORCE_IOC": 0.2,
                "TIME_IN_FORCE_FOK": 0.1,
            }
        )
        self.duration = duration
        self.price_process = price_process
        self.spread = spread
        self.mean = mean
        self.sigma = sigma

    def initialise(self, vega: VegaServiceNull):
        """Initialise the agents wallet and mint the required market asset.

        Args:
            vega (VegaServiceNull):
                Object running a locally-hosted Vega service.
        """

        super().initialise(vega=vega)

        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        self.vega.mint(
            self.wallet_name,
            asset=self.asset_id,
            amount=self.initial_asset_mint,
        )
        self.vega.wait_fn(2)

    def step(self, vega_state: VegaState):
        """Randomly submits and cancels limit orders.

        Args:
            vega_state (VegaState):
                Object describing the state of the network and the market.
        """

        self.current_step += 1

        if self.random_state.rand() <= self.submit_bias:
            self._submit_order(vega_state=vega_state)

            if self.random_state.rand() <= self.cancel_bias:
                self._cancel_order(vega_state=vega_state)

    def _submit_order(self, vega_state: VegaState):
        # Calculate reference_buy_price and reference_sell_price of price distribution
        if (self.spread is None) or (self.price_process is None):
            # If agent does not have price_process data, offset orders from best bid/ask
            best_bid_price, best_offer_price = self.vega.best_prices(
                market_id=self.market_id
            )
            reference_buy_price = best_bid_price
            reference_sell_price = best_offer_price
        else:
            # If agent does have price_process data, offset orders from market price
            reference_buy_price = (
                self.price_process[self.current_step] - self.spread / 2
            )
            reference_sell_price = (
                self.price_process[self.current_step] + self.spread / 2
            )

        side = self.random_state.choice(
            a=list(self.side_opts.keys()),
            p=list(self.side_opts.values()),
        )
        time_in_force = self.random_state.choice(
            a=list(self.time_in_force_opts.keys()),
            p=list(self.time_in_force_opts.values()),
        )

        random_offset = self.random_state.lognormal(
            mean=self.mean,
            sigma=self.sigma,
        )
        ln_mean = exp(self.mean + self.sigma**2 / 2)

        if side == "SIDE_BUY":
            volume = self.buy_volume * self.random_state.poisson(self.buy_intensity)
            price = reference_buy_price + (random_offset - ln_mean)

        elif side == "SIDE_SELL":
            volume = self.sell_volume * self.random_state.poisson(self.sell_intensity)
            price = reference_sell_price - (random_offset - ln_mean)

        expires_at = (self.vega.get_blockchain_time() + self.duration) * 1e9

        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            price=price,
            side=side,
            volume=volume,
            order_type=vega_protos.Order.Type.TYPE_LIMIT,
            wait=False,
            time_in_force=time_in_force,
            expires_at=expires_at,
        )

    def _cancel_order(self, vega_state: VegaState):
        orders = vega_state.market_state.get(self.market_id, {}).orders.get(
            self.vega.wallet.public_key(self.wallet_name), {}
        )

        if len(orders) > 0:
            order_key = self.random_state.choice(list(orders.keys()))
            order = orders[order_key]

            self.vega.cancel_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                order_id=order.id,
            )


class InformedTrader(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        price_process: List[float],
        market_name: str = None,
        asset_name: str = None,
        initial_asset_mint: float = 1e8,
        proportion_taken: float = 0.5,
        tag: str = "",
    ):
        super().__init__(wallet_name + str(tag), wallet_pass)
        self.initial_asset_mint = initial_asset_mint
        self.price_process = price_process
        self.current_step = 0
        self.sim_length = len(price_process)
        self.tag = tag
        self.proportion_taken = proportion_taken
        self.market_name = f"ETH:USD_{self.tag}" if market_name is None else market_name
        self.asset_name = f"tDAI_{self.tag}" if asset_name is None else asset_name

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet
        super().initialise(vega=vega)

        # Get market id
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]

        # Get asset id
        tDAI_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=tDAI_id,
            amount=self.initial_asset_mint,
        )

        self.pdp = self.vega._market_pos_decimals.get(self.market_id, {})
        self.vega.wait_for_total_catchup()

    def step(self, vega_state: VegaState):
        position = self.vega.positions_by_market(
            wallet_name=self.wallet_name, market_id=self.market_id
        )
        current_position = int(position[0].open_volume) if position else 0
        trade_side = (
            vega_protos.vega.Side.SIDE_BUY
            if current_position < 0
            else vega_protos.vega.Side.SIDE_SELL
        )
        if current_position:
            self.vega.submit_market_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                side=trade_side,
                volume=current_position,
                wait=True,
                fill_or_kill=False,
            )

        order_book = self.vega.market_depth(market_id=self.market_id)

        price = self.price_process[self.current_step]
        next_price = self.price_process[self.current_step + 1]

        trade_side = (
            vega_protos.SIDE_BUY if price < next_price else vega_protos.SIDE_SELL
        )

        if price < next_price:
            volume = sum(
                [order.volume for order in order_book.sells if order.price < next_price]
            )
        else:
            volume = sum(
                [order.volume for order in order_book.buys if order.price > next_price]
            )

        volume = round(self.proportion_taken * volume, self.pdp)

        if volume:
            self.vega.submit_market_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                side=trade_side,
                volume=volume,
                wait=False,
                fill_or_kill=False,
            )


class LiquidityProvider(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        market_name: str,
        asset_name: str,
        initial_asset_mint: float,
        commitment_amount: float = 6000,
        offset: float = 0.01,
        fee: float = 0.001,
        tag: str = "",
    ):
        super().__init__(wallet_name + str(tag), wallet_pass)

        self.market_name = market_name
        self.asset_name = asset_name

        self.initial_asset_mint = initial_asset_mint

        self.offset = offset

        self.fee = fee

        self.commitment_amount = commitment_amount

    def initialise(self, vega: VegaServiceNull):
        super().initialise(vega=vega)

        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        self.vega.mint(
            self.wallet_name,
            asset=self.asset_id,
            amount=self.initial_asset_mint,
        )
        self.vega.wait_fn(2)

        self.vega.wait_for_total_catchup()

        self.vega.submit_simple_liquidity(
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            commitment_amount=self.commitment_amount,
            fee=0.001,
            reference_buy="PEGGED_REFERENCE_BEST_BID",
            reference_sell="PEGGED_REFERENCE_BEST_ASK",
            delta_buy=self.offset,
            delta_sell=self.offset,
        )
