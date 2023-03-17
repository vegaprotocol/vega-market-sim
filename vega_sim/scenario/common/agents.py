from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from math import exp
from queue import Queue

import numpy as np

try:
    import talib
except ImportError:
    pass  # TA-Lib not installed, but most agents don't need

import time
from collections import namedtuple
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

from numpy.typing import ArrayLike

import vega_sim.api.faucet as faucet
from vega_sim.api.data import AccountData, MarketDepth, Order, Trade
from vega_sim.api.trading import OrderRejectedError
from vega_sim.environment import VegaState
from vega_sim.environment.agent import Agent, StateAgent, StateAgentWithWallet
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.null_service import VegaService, VegaServiceNull
from vega_sim.proto.vega import markets as markets_protos
from vega_sim.proto.vega import vega as vega_protos
from vega_sim.scenario.common.utils.ideal_mm_models import GLFT_approx, a_s_mm_model

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])


@dataclass
class MarketHistoryData:
    at_time: datetime.datetime
    market_info: Dict[str, vega_protos.markets.Market]
    market_data: Dict[str, vega_protos.markets.MarketData]
    accounts: List[AccountData]
    market_depth: Dict[str, MarketDepth]
    trades: Dict[str, List[Trade]]


# Send selling/buying MOs to hit LP orders
TRADER_WALLET = WalletConfig("trader", "trader")

BACKGROUND_MARKET = WalletConfig("market", "market")

# Pass opening auction
AUCTION1_WALLET = WalletConfig("AUCTION1", "AUCTION1pass")
AUCTION2_WALLET = WalletConfig("AUCTION2", "AUCTION2pass")

ITOrder = namedtuple("ITOrder", ["side", "size"])
MMOrder = namedtuple("MMOrder", ["size", "price"])

LiquidityProvision = namedtuple(
    "LiquidityProvision", ["amount", "fee", "buy_specs", "sell_specs"]
)

logger = logging.getLogger(__name__)


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


class TradeSignal(Enum):
    NOACTION = 0
    BUY = 1
    SELL = 2


class MarketOrderTrader(StateAgentWithWallet):
    NAME_BASE = "mo_trader"

    def __init__(
        self,
        key_name: str,
        market_name: str,
        asset_name: str,
        initial_asset_mint: float = 1000000,
        buy_intensity: float = 1,
        sell_intensity: float = 1,
        tag: str = "",
        random_state: Optional[np.random.RandomState] = None,
        base_order_size: float = 1,
        wallet_name: Optional[str] = None,
        step_bias: Optional[float] = 1,
    ):
        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)
        self.initial_asset_mint = initial_asset_mint
        self.buy_intensity = buy_intensity
        self.sell_intensity = sell_intensity
        self.market_name = market_name
        self.asset_name = asset_name
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )
        self.base_order_size = base_order_size
        self.step_bias = step_bias

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        # Initialise key
        super().initialise(vega=vega, create_key=create_key)
        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        # Get asset id
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            # Top up asset
            self.vega.mint(
                key_name=self.key_name,
                asset=self.asset_id,
                amount=self.initial_asset_mint,
                wallet_name=self.wallet_name,
            )
        self.vega.wait_fn(5)
        self.pdp = self.vega.market_pos_decimals.get(self.market_id, {})
        self.mdp = self.vega.market_price_decimals.get(self.market_id, {})
        self.adp = self.vega.asset_decimals.get(self.asset_id, {})

    def step(self, vega_state: VegaState):
        if self.random_state.rand() > self.step_bias:
            return

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
                trading_key=self.key_name,
                market_id=self.market_id,
                side=side,
                volume=volume,
                wait=False,
                fill_or_kill=False,
                trading_wallet=self.wallet_name,
            )


class PriceSensitiveMarketOrderTrader(StateAgentWithWallet):
    NAME_BASE = "price_sensitive_mo_trader"

    def __init__(
        self,
        key_name: str,
        market_name: str,
        asset_name: str,
        price_process_generator: Iterable[float],
        initial_asset_mint: float = 1000000,
        buy_intensity: float = 1,
        sell_intensity: float = 1,
        price_half_life: float = 1,
        tag: str = "",
        random_state: Optional[np.random.RandomState] = None,
        base_order_size: float = 1,
        wallet_name: str = None,
    ):
        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)
        self.initial_asset_mint = initial_asset_mint
        self.buy_intensity = buy_intensity
        self.sell_intensity = sell_intensity
        self.market_name = market_name
        self.asset_name = asset_name
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )
        self.base_order_size = base_order_size
        self.probability_decay = np.log(2) / price_half_life
        self.price_process_generator = price_process_generator

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        # Initialise wallet
        super().initialise(vega=vega, create_key=create_key)
        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        # Get asset id
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            # Top up asset
            self.vega.mint(
                key_name=self.key_name,
                asset=self.asset_id,
                amount=self.initial_asset_mint,
                wallet_name=self.wallet_name,
            )
        self.vega.wait_fn(5)

    def step(self, vega_state: VegaState):
        self.curr_price = next(self.price_process_generator)

        buy_first = self.random_state.choice([0, 1])

        buy_vol = self.random_state.poisson(self.buy_intensity) * self.base_order_size
        sell_vol = self.random_state.poisson(self.sell_intensity) * self.base_order_size

        best_bid, best_ask = self.vega.best_prices(self.market_id)

        will_buy = self.random_state.rand() < np.exp(
            -1 * self.probability_decay * max([best_ask - self.curr_price, 0])
        )
        will_sell = self.random_state.rand() < np.exp(
            -1 * self.probability_decay * max([self.curr_price - best_bid, 0])
        )

        if buy_first and will_buy:
            self.place_order(
                vega_state=vega_state,
                volume=buy_vol,
                side=vega_protos.SIDE_BUY,
            )

        if will_sell:
            self.place_order(
                vega_state=vega_state,
                volume=sell_vol,
                side=vega_protos.SIDE_SELL,
            )

        if not buy_first and will_buy:
            self.place_order(
                vega_state=vega_state,
                volume=buy_vol,
                side=vega_protos.SIDE_BUY,
            )

    def place_order(self, vega_state: VegaState, volume: float, side: vega_protos.Side):
        try:
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
                    trading_key=self.key_name,
                    market_id=self.market_id,
                    side=side,
                    volume=volume,
                    wait=False,
                    fill_or_kill=False,
                    trading_wallet=self.wallet_name,
                )
        except:
            import pdb

            pdb.set_trace()
            a = 4


class PriceSensitiveLimitOrderTrader(StateAgentWithWallet):
    NAME_BASE = "price_sensitive_lo_trader"

    def __init__(
        self,
        key_name: str,
        market_name: str,
        asset_name: str,
        price_process_generator: Iterable[float],
        initial_asset_mint: float = 1000000,
        scale: float = 0.5,
        max_order_size: float = 100,
        random_state: Optional[np.random.RandomState] = None,
        wallet_name: str = None,
        tag: str = "",
    ):
        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)
        self.market_name = market_name
        self.asset_name = asset_name
        self.price_process_generator = price_process_generator
        self.initial_asset_mint = initial_asset_mint
        self.scale = scale
        self.max_order_size = max_order_size
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        # Initialise wallet
        super().initialise(vega=vega, create_key=create_key)
        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        # Get asset id
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            # Top up asset
            self.vega.mint(
                key_name=self.key_name,
                asset=self.asset_id,
                amount=self.initial_asset_mint,
                wallet_name=self.wallet_name,
            )
        self.vega.wait_fn(5)

    def step(self, vega_state: VegaState):
        self.curr_price = next(self.price_process_generator)

        bid_price = self.curr_price + self.random_state.exponential(scale=self.scale)
        self.place_order(side="SIDE_BUY", price=bid_price)

        ask_price = self.curr_price - self.random_state.exponential(scale=self.scale)
        self.place_order(side="SIDE_SELL", price=ask_price)

    def place_order(
        self,
        side,
        price,
    ):
        self.vega.submit_order(
            trading_key=self.key_name,
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_IOC",
            side=side,
            volume=self.max_order_size,
            price=price,
            wait=False,
        )


class BackgroundMarket(StateAgentWithWallet):
    NAME_BASE = "background_market"

    def __init__(
        self,
        key_name: str,
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
        wallet_name: Optional[str] = None,
    ):
        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)
        self.price_process = price_process
        self.initial_asset_mint = initial_asset_mint
        self.spread = spread
        self.current_step = 0
        self.tick_spacing = tick_spacing
        self.num_levels_per_side = num_levels_per_side
        self.base_volume_size = base_volume_size

        self.market_name = market_name
        self.asset_name = asset_name
        self.kappa = order_distribution_kappa
        self.position_decimals = position_decimals

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        # Initialise wallet
        super().initialise(vega=vega, create_key=create_key)
        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        # Get asset id
        asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            # Top up asset
            self.vega.mint(
                wallet_name=self.wallet_name,
                asset=asset_id,
                amount=self.initial_asset_mint,
                key_name=self.key_name,
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
            trading_key=self.key_name,
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
            self.key_name, self.market_id, live_only=True, wallet_name=self.wallet_name
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
                    trading_key=self.key_name,
                    wallet_name=self.wallet_name,
                    market_id=self.market_id,
                    order_id=order_to_amend.id,
                    price=new_shape[i][0],
                    volume_delta=new_shape[i][1] - order_to_amend.remaining,
                )
            else:
                self._submit_order(side, new_shape[i][0], new_shape[i][1])


class MultiRegimeBackgroundMarket(StateAgentWithWallet):
    NAME_BASE = "multi_regime_background_market"

    def __init__(
        self,
        key_name: str,
        market_name: str,
        asset_name: str,
        price_process: List[float],
        market_regimes: List[MarketRegime],
        tag: str = "",
        wallet_name: Optional[str] = None,
    ):
        """Generate a background market acting differently as time passes.
        Allows specification of varying numbers of non-overlapping regimes
        (with optional gaps in which no orders will be placed).

        Places an exponentially shaped Limit-Order-Book about a moving midprice.

        Args:
            key_name:
                str, The name of the key in the wallet to use
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
            wallet_name:
                str, optional, The name of the wallet to use placing background orders
        """
        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)
        self.price_process = price_process
        self.current_step = 0

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
                (
                    regimes.append(market_regime)
                    if market_regime.from_timepoint <= i
                    else regimes.append(None)
                )
            else:
                regimes.append(market_regime)
        return regimes

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        # Initialise wallet
        super().initialise(vega=vega, create_key=create_key)
        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        # Get asset id
        asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            # Top up asset
            self.vega.mint(
                key_name=self.key_name,
                asset=asset_id,
                amount=200000,
                wallet_name=self.wallet_name,
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
            trading_key=self.key_name,
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
        min_price: float = 0.01,
    ) -> ArrayLike:
        is_buy = side in ["SIDE_BUY", vega_protos.SIDE_BUY]

        base_level = abs(starting_level - mid_price)
        final_level = base_level + tick_spacing * num_levels
        levels = np.arange(base_level, final_level, tick_spacing)
        cumulative_vol = np.exp(kappa * levels) - 1

        level_vol = np.concatenate([cumulative_vol[:1], np.diff(cumulative_vol)])
        level_price = np.clip(
            mid_price + (-1 if is_buy else 1) * levels, min_price, None
        )

        return np.c_[level_price, level_vol]

    def step(self, vega_state: VegaState):
        self.current_step += 1
        market_regime = self.market_regimes[self.current_step]

        orders = self.vega.orders_for_party_from_feed(
            self.key_name, self.market_id, live_only=True, wallet_name=self.wallet_name
        )

        if market_regime is None:
            for order in orders.values():
                self.vega.cancel_order(
                    self.key_name,
                    self.market_id,
                    order.id,
                    wallet_name=self.wallet_name,
                )
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
                    wallet_name=self.wallet_name,
                    trading_key=self.key_name,
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
    NAME_BASE = "open_auction_pass"

    def __init__(
        self,
        key_name: str,
        side: str,
        market_name: str,
        asset_name: str,
        initial_asset_mint: float = 1000000,
        initial_price: float = 0.3,
        opening_auction_trade_amount: float = 1,
        tag: str = "",
        wallet_name: str = None,
    ):
        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)
        self.side = side
        self.initial_asset_mint = initial_asset_mint
        self.initial_price = initial_price
        self.market_name = market_name
        self.asset_name = asset_name
        self.opening_auction_trade_amount = opening_auction_trade_amount

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        # Initialise wallet
        super().initialise(vega=vega, create_key=create_key)
        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        self.vega.wait_for_total_catchup()
        # Get asset id
        asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            # Top up asset
            self.vega.mint(
                wallet_name=self.wallet_name,
                asset=asset_id,
                amount=self.initial_asset_mint,
                key_name=self.key_name,
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
            trading_key=self.key_name,
        )

    def step(self, vega_state: VegaState):
        pass


class MarketManager(StateAgentWithWallet):
    NAME_BASE = "market_manager"

    def __init__(
        self,
        key_name: str,
        terminate_key_name: str,
        market_name: str,
        asset_name: str,
        asset_decimal: int = 5,
        market_decimal: int = 5,
        market_position_decimal: int = 2,
        initial_mint: Optional[float] = None,
        commitment_amount: Optional[float] = None,
        settlement_price: Optional[float] = None,
        tag: str = "",
        wallet_name: str = None,
        terminate_wallet_name: str = None,
    ):
        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)
        self.terminate_wallet_name = terminate_wallet_name
        self.terminate_key_name = terminate_key_name

        self.adp = asset_decimal
        self.mdp = market_decimal
        self.market_position_decimal = market_position_decimal
        self.commitment_amount = commitment_amount

        self.current_step = 0

        self.initial_mint = (
            initial_mint
            if initial_mint is not None
            else (2 * commitment_amount) if commitment_amount is not None else 100
        )

        self.market_name = market_name
        self.asset_name = asset_name
        self.settlement_price = settlement_price

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        # Initialise wallet for LP/ Settle Party
        super().initialise(vega=vega, create_key=create_key)
        self.vega.create_key(
            wallet_name=self.terminate_wallet_name,
            name=self.terminate_key_name,
        )

        # Faucet vega tokens
        self.vega.wait_for_total_catchup()
        self.vega.mint(
            wallet_name=self.wallet_name,
            asset="VOTE",
            amount=1e4,
            key_name=self.key_name,
        )
        self.vega.wait_fn(5)
        self.vega.wait_for_total_catchup()
        if vega.find_asset_id(symbol=self.asset_name) is None:
            # Create asset
            self.vega.create_asset(
                wallet_name=self.wallet_name,
                name=self.asset_name,
                symbol=self.asset_name,
                decimals=self.adp,
                max_faucet_amount=5e10,
                key_name=self.key_name,
            )
        self.vega.wait_fn(5)
        self.vega.wait_for_total_catchup()
        # Get asset id
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            # Top up asset
            self.vega.mint(
                wallet_name=self.wallet_name,
                asset=self.asset_id,
                amount=self.initial_mint,
                key_name=self.key_name,
            )
        self.vega.wait_fn(5)

        self.vega.wait_for_total_catchup()
        # Set up a future market
        self.vega.create_simple_market(
            market_name=self.market_name,
            wallet_name=self.wallet_name,
            proposal_key=self.key_name,
            settlement_asset_id=self.asset_id,
            market_decimals=self.mdp,
            position_decimals=self.market_position_decimal,
            future_asset=self.asset_name,
            termination_key=self.terminate_key_name,
            termination_wallet_name=self.terminate_wallet_name,
        )
        self.vega.wait_for_total_catchup()

        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)
        if self.commitment_amount:
            self.vega.submit_liquidity(
                wallet_name=self.wallet_name,
                market_id=self.market_id,
                commitment_amount=self.commitment_amount,
                fee=0.002,
                buy_specs=[("PEGGED_REFERENCE_BEST_BID", 5, 1)],
                sell_specs=[("PEGGED_REFERENCE_BEST_ASK", 5, 1)],
                is_amendment=False,
                key_name=self.key_name,
            )

    def finalise(self):
        if self.settlement_price is not None:
            self.vega.settle_market(
                self.terminate_key_name,
                self.settlement_price,
                self.market_id,
                self.terminate_wallet_name,
            )
            self.vega.wait_for_total_catchup()


class ShapedMarketMaker(StateAgentWithWallet):
    """Utilises the Ideal market maker formulation from
        Algorithmic and High-Frequency Trading by Cartea, Jaimungal and Penalva.

    Unlike the purer Ideal Market Makers elsewhere in Vega sim,
    here we use the positional depth logic to create a best bid/ask
    for the MM, but behind those the MM will also create a shape
    (by default an exponential curve). This allows this MM to be the sole liquidity
    source in the market but still to maintain an interesting full LOB.
    """

    NAME_BASE = "shaped_market_maker"

    def __init__(
        self,
        key_name: str,
        price_process_generator: Iterable[float],
        best_price_offset_fn: Callable[[float, int], Tuple[float, float]],
        shape_fn: Callable[
            [
                float,
                float,
            ],
            Tuple[List[MMOrder], List[MMOrder]],
        ],
        liquidity_commitment_fn: Optional[
            Callable[[Optional[VegaState]], Optional[LiquidityProvision]]
        ],
        initial_asset_mint: float = 1000000,
        market_name: Optional[str] = None,
        asset_name: Optional[str] = None,
        commitment_amount: float = 6000,
        market_decimal_places: int = 5,
        asset_decimal_places: int = 0,
        tag: str = "",
        wallet_name: str = None,
        orders_from_stream: Optional[bool] = True,
        state_update_freq: Optional[int] = None,
        safety_factor: Optional[float] = 1.2,
        max_order_size: float = 10000,
        order_validity_length: Optional[float] = None,
    ):
        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)
        self.price_process_generator = price_process_generator
        self.commitment_amount = commitment_amount
        self.initial_asset_mint = initial_asset_mint
        self.mdp = market_decimal_places
        self.adp = asset_decimal_places

        self.shape_fn = shape_fn
        self.best_price_offset_fn = best_price_offset_fn
        self.liquidity_commitment_fn = liquidity_commitment_fn

        self.current_step = 0
        self.curr_price = None
        self.prev_price = None

        self.market_name = f"ETH:USD_{self.tag}" if market_name is None else market_name
        self.asset_name = f"tDAI{self.tag}" if asset_name is None else asset_name

        self.orders_from_stream = orders_from_stream

        self.safety_factor = safety_factor
        self.state_update_freq = state_update_freq
        self.max_order_size = max_order_size

        self.bid_depth = None
        self.ask_depth = None

        self.order_validity_length = order_validity_length

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        # Initialise wallet for LP/ Settle Party
        super().initialise(vega=vega, create_key=create_key)

        # Get asset id
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            # Top up asset
            self.vega.mint(
                wallet_name=self.wallet_name,
                asset=self.asset_id,
                amount=self.initial_asset_mint,
                key_name=self.key_name,
            )
            self.vega.wait_for_total_catchup()

        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        self._update_state(current_step=self.current_step)

        if (
            initial_liq := (
                self.liquidity_commitment_fn(None)
                if self.liquidity_commitment_fn is not None
                else None
            )
        ) is not None:
            self.vega.submit_liquidity(
                wallet_name=self.wallet_name,
                market_id=self.market_id,
                commitment_amount=initial_liq.amount,
                fee=initial_liq.fee,
                buy_specs=initial_liq.buy_specs,
                sell_specs=initial_liq.sell_specs,
                is_amendment=False,
                key_name=self.key_name,
            )

    def step(self, vega_state: VegaState):
        self.current_step += 1
        self.prev_price = self.curr_price
        self.curr_price = next(self.price_process_generator)

        self._update_state(current_step=self.current_step)

        # Each step, MM posts optimal bid/ask depths
        position = self.vega.positions_by_market(
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            key_name=self.key_name,
        )

        current_position = int(position.open_volume) if position is not None else 0
        self.bid_depth, self.ask_depth = self.best_price_offset_fn(
            current_position, self.current_step
        )
        if (self.bid_depth is None) or (self.ask_depth is None):
            return

        new_buy_shape, new_sell_shape = self.shape_fn(self.bid_depth, self.ask_depth)
        scaled_buy_shape, scaled_sell_shape = self._scale_orders(
            buy_shape=new_buy_shape, sell_shape=new_sell_shape
        )

        curr_buy_orders, curr_sell_orders = [], []

        if self.orders_from_stream:
            orders = (
                (
                    vega_state.market_state[self.market_id]
                    .orders.get(
                        self.vega.wallet.public_key(
                            wallet_name=self.wallet_name, name=self.key_name
                        ),
                        {},
                    )
                    .values()
                )
                if self.market_id in vega_state.market_state
                else []
            )
        else:
            orders = self.vega.list_orders(
                wallet_name=self.wallet_name,
                key_name=self.key_name,
                market_id=self.market_id,
                live_only=True,
            )

        for order in orders:
            if order.side == vega_protos.SIDE_BUY:
                curr_buy_orders.append(order)
            else:
                curr_sell_orders.append(order)

        # We want to first make the spread wider by moving the side which is in the
        # direction of the move (e.g. if price falls, the bids)
        first_side = (
            (
                vega_protos.SIDE_BUY
                if scaled_sell_shape[0].price < curr_buy_orders[0].price
                else vega_protos.SIDE_SELL
            )
            if (scaled_sell_shape != []) and (curr_buy_orders != [])
            else vega_protos.SIDE_BUY
        )
        if first_side == vega_protos.SIDE_BUY:
            self._move_side(
                vega_protos.SIDE_BUY,
                curr_buy_orders,
                scaled_buy_shape,
            )
        self._move_side(
            vega_protos.SIDE_SELL,
            curr_sell_orders,
            scaled_sell_shape,
        )
        if first_side == vega_protos.SIDE_SELL:
            self._move_side(
                vega_protos.SIDE_BUY,
                curr_buy_orders,
                scaled_buy_shape,
            )

        if (
            liq := (
                self.liquidity_commitment_fn(vega_state)
                if self.liquidity_commitment_fn is not None
                else None
            )
        ) is not None:
            self.vega.submit_liquidity(
                wallet_name=self.wallet_name,
                market_id=self.market_id,
                commitment_amount=liq.amount,
                fee=liq.fee,
                buy_specs=liq.buy_specs,
                sell_specs=liq.sell_specs,
                is_amendment=True,
                key_name=self.key_name,
            )

    def _scale_orders(
        self,
        buy_shape: List[MMOrder],
        sell_shape: List[MMOrder],
    ):
        buy_scaling_factor = (
            self.safety_factor * self.commitment_amount * self.stake_to_ccy_volume
        ) / self._calculate_liquidity(
            orders=buy_shape,
        )

        sell_scaling_factor = (
            self.safety_factor * self.commitment_amount * self.stake_to_ccy_volume
        ) / self._calculate_liquidity(
            orders=sell_shape,
        )

        # Scale the shapes
        scaled_buy_shape = [
            MMOrder(
                min([order.size * buy_scaling_factor, self.max_order_size]), order.price
            )
            for order in buy_shape
        ]
        scaled_sell_shape = [
            MMOrder(
                min([order.size * sell_scaling_factor, self.max_order_size]),
                order.price,
            )
            for order in sell_shape
        ]

        return scaled_buy_shape, scaled_sell_shape

    def _calculate_liquidity(
        self,
        orders: List[MMOrder],
    ) -> float:
        provided_liquidity = 0

        for vol, price in orders:
            if price <= 0:
                continue

            provided_liquidity += vol * price

        return provided_liquidity

    def _move_side(
        self,
        side: vega_protos.Side,
        orders: List[Order],
        new_shape: List[MMOrder],
    ) -> None:
        amendments = []
        submissions = []
        cancellations = []

        expires_at = (
            int((self.vega.get_blockchain_time() + self.order_validity_length) * 1e9)
            if self.order_validity_length is not None
            else None
        )

        for i, order in enumerate(new_shape):
            if i < len(orders):
                order_to_amend = orders[i]

                transaction = self.vega.create_order_amendment(
                    market_id=self.market_id,
                    order_id=order_to_amend.id,
                    price=order.price,
                    time_in_force=(
                        "TIME_IN_FORCE_GTT"
                        if self.order_validity_length is not None
                        else "TIME_IN_FORCE_GTC"
                    ),
                    size_delta=order.size - order_to_amend.remaining,
                    expires_at=expires_at,
                )

                amendments.append(transaction)

            else:
                transaction = self.vega.create_order_submission(
                    market_id=self.market_id,
                    price=order.price,
                    size=order.size,
                    order_type="TYPE_LIMIT",
                    time_in_force=(
                        "TIME_IN_FORCE_GTT"
                        if self.order_validity_length is not None
                        else "TIME_IN_FORCE_GTC"
                    ),
                    side=side,
                    expires_at=expires_at,
                )

                submissions.append(transaction)

        if len(orders) > len(new_shape):
            for order in orders[len(new_shape) :]:
                transaction = self.vega.create_order_cancellation(
                    order_id=order.id,
                    market_id=self.market_id,
                )

                cancellations.append(transaction)

        if submissions is not []:
            self.vega.submit_instructions(
                wallet_name=self.wallet_name,
                key_name=self.key_name,
                amendments=amendments,
                submissions=submissions,
                cancellations=cancellations,
            )

    def _update_state(self, current_step: int):
        if self.state_update_freq and current_step % self.state_update_freq == 0:
            market_info = self.vega.market_info(market_id=self.market_id)

            self.tau = market_info.tradable_instrument.log_normal_risk_model.tau
            self.mu = market_info.tradable_instrument.log_normal_risk_model.params.mu
            self.sigma = (
                market_info.tradable_instrument.log_normal_risk_model.params.sigma
            )

            self.tau_scaling = self.vega.get_network_parameter(
                key="market.liquidity.probabilityOfTrading.tau.scaling", to_type="float"
            )
            self.min_probability_of_trading = self.vega.get_network_parameter(
                key="market.liquidity.minimum.probabilityOfTrading.lpOrders",
                to_type="float",
            )
            self.stake_to_ccy_volume = self.vega.get_network_parameter(
                key="market.liquidity.stakeToCcyVolume", to_type="float"
            )


class ExponentialShapedMarketMaker(ShapedMarketMaker):
    """Utilises the Ideal market maker formulation from
        Algorithmic and High-Frequency Trading by Cartea, Jaimungal and Penalva.

    Unlike the purer Ideal Market Makers elsewhere in Vega sim,
    here we use the positional depth logic to create a best bid/ask
    for the MM, but behind those the MM will also create a shape
    (by default an exponential curve). This allows this MM to be the sole liquidity
    source in the market but still to maintain an interesting full LOB.
    """

    NAME_BASE = "expon_shaped_market_maker"

    def __init__(
        self,
        key_name: str,
        num_steps: int,
        price_process_generator: Iterable[float],
        initial_asset_mint: float = 1000000,
        market_name: str = None,
        asset_name: str = None,
        commitment_amount: float = 6000,
        market_decimal_places: int = 5,
        fee_amount: float = 0.001,
        kappa: float = 1,
        num_levels: int = 25,
        tick_spacing: float = 1,
        inventory_upper_boundary: float = 20,
        inventory_lower_boundary: float = -20,
        terminal_penalty_parameter: float = 10**-4,
        running_penalty_parameter: float = 5 * 10**-6,
        market_order_arrival_rate: float = 5,
        market_kappa: float = 1,
        asset_decimal_places: int = 0,
        tag: str = "",
        wallet_name: str = None,
        orders_from_stream: Optional[bool] = True,
        state_update_freq: Optional[int] = None,
        max_order_size: float = 10000,
        order_validity_length: Optional[float] = None,
    ):
        super().__init__(
            wallet_name=wallet_name,
            price_process_generator=price_process_generator,
            initial_asset_mint=initial_asset_mint,
            market_name=market_name,
            asset_name=asset_name,
            commitment_amount=commitment_amount,
            market_decimal_places=market_decimal_places,
            asset_decimal_places=asset_decimal_places,
            tag=tag,
            shape_fn=self._generate_shape,
            best_price_offset_fn=self._optimal_strategy,
            liquidity_commitment_fn=self._liq_provis,
            key_name=key_name,
            orders_from_stream=orders_from_stream,
            state_update_freq=state_update_freq,
            max_order_size=max_order_size,
            order_validity_length=order_validity_length,
        )
        self.kappa = kappa
        self.tick_spacing = tick_spacing
        self.num_levels = num_levels
        self.fee_amount = fee_amount

        self.num_steps = num_steps
        self.long_horizon_estimate = num_steps >= 200
        self.q_upper = inventory_upper_boundary
        self.q_lower = inventory_lower_boundary
        self.market_order_arrival_rate = market_order_arrival_rate
        self.market_kappa = market_kappa
        self.alpha = terminal_penalty_parameter
        self.phi = running_penalty_parameter

        self.curr_bids, self.curr_asks = None, None

        if not self.long_horizon_estimate:
            self.optimal_bid, self.optimal_ask, _ = a_s_mm_model(
                T=self.num_steps / 60 / 24 / 365.25,
                dt=1 / 60 / 24 / 365.25,
                length=self.num_steps + 1,
                q_upper=self.q_upper,
                q_lower=self.q_lower,
                mdp=self.mdp,
                kappa=self.market_kappa,
                Lambda=self.market_order_arrival_rate,
                alpha=self.alpha,
                phi=self.phi,
            )
        else:
            self.optimal_bid, self.optimal_ask = GLFT_approx(
                q_upper=self.q_upper,
                q_lower=self.q_lower,
                kappa=self.market_kappa,
                Lambda=self.market_order_arrival_rate,
                alpha=self.alpha,
                phi=self.phi,
            )

    def _liq_provis(self, state: VegaState) -> LiquidityProvision:
        if (self.curr_asks is not None) and (self.curr_bids is not None):
            est_mid_price = (self.curr_bids[0].price + self.curr_asks[0].price) * 0.5
        elif state is not None:
            est_mid_price = state.market_state[self.market_id].midprice
        else:
            est_mid_price = None
            buy_specs = [["PEGGED_REFERENCE_BEST_BID", 5, 1]]
            sell_specs = [["PEGGED_REFERENCE_BEST_ASK", 5, 1]]

        if self.curr_asks is not None:
            next_ask_step = self.curr_asks[-1].price + self.tick_spacing
            sell_specs = [
                [
                    "PEGGED_REFERENCE_MID",
                    next_ask_step - est_mid_price,
                    1,
                ]
            ]
        if self.curr_bids is not None:
            next_bid_step = self.curr_bids[-1].price - self.tick_spacing
            buy_specs = [
                [
                    "PEGGED_REFERENCE_MID",
                    est_mid_price - next_bid_step,
                    1,
                ]
            ]

        return LiquidityProvision(
            amount=self.commitment_amount,
            fee=self.fee_amount,
            buy_specs=buy_specs,
            sell_specs=sell_specs,
        )

    def _optimal_strategy(
        self, current_position: float, current_step: int
    ) -> Tuple[float, float]:
        if current_position >= self.q_upper:
            current_bid_depth = (
                self.optimal_bid[current_step, 0]
                if not self.long_horizon_estimate
                else self.optimal_bid[0]
            )
            current_ask_depth = (
                1 / 10**self.mdp
            )  # Sell for the smallest possible amount above mid
        elif current_position <= self.q_lower:
            current_bid_depth = (
                1 / 10**self.mdp
            )  # Buy for the smallest possible amount below mid
            current_ask_depth = (
                self.optimal_ask[current_step, -1]
                if not self.long_horizon_estimate
                else self.optimal_ask[-1]
            )
        else:
            current_bid_depth = (
                self.optimal_bid[current_step, int(self.q_upper - 1 - current_position)]
                if not self.long_horizon_estimate
                else self.optimal_bid[int(self.q_upper - 1 - current_position)]
            )
            current_ask_depth = (
                self.optimal_ask[current_step, int(self.q_upper - current_position)]
                if not self.long_horizon_estimate
                else self.optimal_ask[int(self.q_upper - current_position)]
            )

        return current_bid_depth, current_ask_depth

    def _generate_shape(
        self, bid_price_depth: float, ask_price_depth: float
    ) -> Tuple[List[MMOrder], List[MMOrder]]:
        bid_orders = self._calculate_price_volume_levels(
            bid_price_depth, vega_protos.Side.SIDE_BUY
        )
        ask_orders = self._calculate_price_volume_levels(
            ask_price_depth, vega_protos.Side.SIDE_SELL
        )
        self.curr_bids = bid_orders
        self.curr_asks = ask_orders
        return bid_orders, ask_orders

    def _calculate_price_volume_levels(
        self,
        price_depth: float,
        side: Union[str, vega_protos.Side],
    ) -> List[MMOrder]:
        is_buy = side in ["SIDE_BUY", vega_protos.SIDE_BUY]
        mult_factor = -1 if is_buy else 1

        levels = np.arange(0, self.tick_spacing * self.num_levels, self.tick_spacing)
        cumulative_vol = np.exp(self.kappa * levels)
        level_vol = (1 / cumulative_vol[0]) * cumulative_vol

        base_price = self.curr_price + mult_factor * price_depth
        level_price = np.arange(
            base_price,
            base_price + mult_factor * self.num_levels * self.tick_spacing,
            mult_factor * self.tick_spacing,
        )
        level_price[level_price < 1 / 10**self.mdp] = 1 / 10**self.mdp

        return [MMOrder(vol, price) for vol, price in zip(level_vol, level_price)]


class HedgedMarketMaker(ExponentialShapedMarketMaker):
    def __init__(
        self,
        key_name: str,
        num_steps: int,
        price_process_generator: Iterable[float],
        internal_key_mint: float = 1000000,
        external_key_mint: float = 1000000,
        market_name: str = None,
        external_market_name: str = None,
        asset_name: str = None,
        commitment_amount: float = 6000,
        market_decimal_places: int = 5,
        fee_amount: float = 0.001,
        kappa: float = 1,
        num_levels: int = 25,
        tick_spacing: float = 1,
        inventory_upper_boundary: float = 20,
        inventory_lower_boundary: float = -20,
        terminal_penalty_parameter: float = 10**-4,
        running_penalty_parameter: float = 5 * 10**-6,
        market_order_arrival_rate: float = 5,
        market_kappa: float = 1,
        asset_decimal_places: int = 0,
        tag: str = "",
        wallet_name: str = None,
        external_key_name: Optional[float] = "Hedging Key",
        orders_from_stream: Optional[bool] = True,
        state_update_freq: Optional[int] = None,
        profit_margin: Optional[float] = 0.01,
        internal_delay: int = 60 * 60,
        external_delay: int = 5 * 60,
        transfer_threshold: float = 500,
    ):
        super().__init__(
            wallet_name=wallet_name,
            num_steps=num_steps,
            price_process_generator=price_process_generator,
            initial_asset_mint=internal_key_mint,
            market_name=market_name,
            asset_name=asset_name,
            commitment_amount=commitment_amount,
            market_decimal_places=market_decimal_places,
            fee_amount=fee_amount,
            kappa=kappa,
            num_levels=num_levels,
            tick_spacing=tick_spacing,
            inventory_upper_boundary=inventory_upper_boundary,
            inventory_lower_boundary=inventory_lower_boundary,
            terminal_penalty_parameter=terminal_penalty_parameter,
            running_penalty_parameter=running_penalty_parameter,
            market_order_arrival_rate=market_order_arrival_rate,
            market_kappa=market_kappa,
            asset_decimal_places=asset_decimal_places,
            tag=tag,
            key_name=key_name,
            orders_from_stream=orders_from_stream,
            state_update_freq=state_update_freq,
        )

        self.profit_margin = profit_margin

        self.external_market_name = external_market_name
        self.external_market_id = None

        self.external_key_name = external_key_name
        self.internal_delay = internal_delay
        self.external_delay = external_delay

        self.transfer_threshold = transfer_threshold
        self.external_key_mint = external_key_mint

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        # Initialise the parent ExponentialShapedMarketMaker
        super().initialise(vega, create_key, mint_key)

        self.external_market_id = self.vega.find_market_id(
            name=self.external_market_name
        )
        self._update_state(current_step=self.current_step)

        if vega.create_key:
            vega.create_key(
                wallet_name=self.wallet_name,
                passphrase=self.wallet_pass,
                name=self.external_key_name,
            )
        if mint_key:
            vega.mint(
                wallet_name=self.wallet_name,
                asset=self.asset_id,
                amount=self.external_key_mint,
                key_name=self.external_key_name,
            )

    def _update_state(self, current_step: int):
        super()._update_state(current_step)

        if self.state_update_freq and current_step % self.state_update_freq == 0:
            if self.market_id is None:
                self.int_mkr_fee = 0
                self.int_liq_fee = 0
                self.int_inf_fee = 0
            else:
                int_market_info = self.vega.market_info(market_id=self.market_id)
                self.int_mkr_fee = float(int_market_info.fees.factors.maker_fee)
                self.int_liq_fee = float(int_market_info.fees.factors.liquidity_fee)
                self.int_inf_fee = float(
                    int_market_info.fees.factors.infrastructure_fee
                )

            if self.external_market_id is None:
                self.ext_mkr_fee = 0
                self.ext_liq_fee = 0
                self.ext_inf_fee = 0

            else:
                ext_market_info = self.vega.market_info(market_id=self.market_id)
                self.ext_mkr_fee = float(ext_market_info.fees.factors.maker_fee)
                self.ext_liq_fee = float(ext_market_info.fees.factors.liquidity_fee)
                self.ext_inf_fee = float(
                    ext_market_info.fees.factors.infrastructure_fee
                )

    def _optimal_strategy(self, current_position, current_step):
        ext_best_bid, ext_best_ask = self.vega.best_prices(
            market_id=self.external_market_id
        )

        if (ext_best_bid == 0) or (ext_best_ask == 0):
            return None, None

        fee_share = self.vega.get_liquidity_fee_shares(
            market_id=self.market_id,
            wallet_name=self.wallet_name,
            key_name=self.key_name,
        )

        int_fee = self.int_mkr_fee + self.int_liq_fee * fee_share
        ext_fee = self.ext_mkr_fee + self.ext_liq_fee + self.ext_inf_fee

        required_bid_price = (
            ext_best_bid * (1 - ext_fee) / (1 - int_fee + self.profit_margin)
        )
        required_ask_price = (
            ext_best_ask * (1 + ext_fee) / (1 + int_fee - self.profit_margin)
        )

        current_bid_depth = self.curr_price - required_bid_price
        current_ask_depth = required_ask_price - self.curr_price

        return current_bid_depth, current_ask_depth

    def _balance_positions(self):
        # Determine the delta between the position on the internal and external market

        positions = self.vega.positions_by_market(
            wallet_name=self.wallet_name,
            key_name=self.key_name,
        )
        current_int_position = (
            float(positions[self.market_id].open_volume)
            if positions is not None and self.market_id in positions
            else 0
        )
        current_ext_position = (
            float(positions[self.external_market_id].open_volume)
            if positions is not None and self.external_market_id in positions
            else 0
        )
        position_delta = current_int_position + current_ext_position

        # Hedge the position on the internal market on the external market

        if position_delta == 0:
            return
        elif position_delta < 0:
            side = vega_protos.SIDE_BUY
        elif position_delta > 0:
            side = vega_protos.SIDE_SELL

        self.vega.submit_market_order(
            trading_wallet=self.wallet_name,
            trading_key=self.external_key_name,
            market_id=self.external_market_id,
            volume=abs(position_delta),
            side=side,
            wait=False,
            fill_or_kill=False,
        )

    def _balance_accounts(self):
        # Get the total balance on the internal market (excluding bond)
        internal_account = self.vega.party_account(
            wallet_name=self.wallet_name,
            asset_id=self.asset_id,
            market_id=self.market_id,
            key_name=self.key_name,
        )
        internal_account_balance = internal_account.general + internal_account.margin

        # Get the total balance on the external market (excluding bond)
        external_account = self.vega.party_account(
            wallet_name=self.wallet_name,
            asset_id=self.asset_id,
            market_id=self.market_id,
            key_name=self.external_key_name,
        )
        external_account_balance = external_account.general + external_account.margin

        # Get the balance currently locked in transfers inbound to the internal market
        transfers = self.vega.transfer_status_from_feed(live_only=True)
        internal_transfers_balance = sum(
            [
                transfer.amount
                for transfer in transfers.get(
                    self.vega.wallet.public_key(
                        name=self.key_name, wallet_name=self.wallet_name
                    ),
                    {},
                ).values()
            ]
        )
        # Get the balance currently locked in transfers inbound to the external market
        external_transfers_balance = sum(
            [
                transfer.amount
                for transfer in transfers.get(
                    self.vega.wallet.public_key(
                        name=self.key_name, wallet_name=self.external_key_name
                    ),
                    {},
                ).values()
            ]
        )

        # Calculate the difference between the total balance on the markets
        delta = (internal_account_balance + internal_transfers_balance) - (
            external_account_balance + external_transfers_balance
        )

        # Create a transfer to balance the internal and external accounts
        if abs(delta) < self.transfer_threshold:
            return

        if delta > 0:
            from_key = self.key_name
            to_key = self.external_key_name
            delay = self.internal_delay

        elif delta < 0:
            from_key = self.external_key_name
            to_key = self.key_name
            delay = self.external_delay

        else:
            return

        self.vega.one_off_transfer(
            from_wallet_name=self.wallet_name,
            to_wallet_name=self.wallet_name,
            from_key_name=from_key,
            to_key_name=to_key,
            from_account_type=vega_protos.ACCOUNT_TYPE_GENERAL,
            to_account_type=vega_protos.ACCOUNT_TYPE_GENERAL,
            asset=self.asset_id,
            amount=abs(delta),
            delay=delay,
        )

    def step(self, vega_state: VegaState):
        super().step(vega_state=vega_state)
        self._balance_positions()
        self._balance_accounts()


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

    NAME_BASE = "lo_trader"

    def __init__(
        self,
        key_name: str,
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
        wallet_name: str = None,
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

        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)

        self.current_step = 0

        self.market_name = market_name
        self.asset_name = asset_name
        self.initial_asset_mint = initial_asset_mint
        self.buy_intensity = buy_intensity
        self.sell_intensity = sell_intensity
        self.buy_volume = buy_volume
        self.sell_volume = sell_volume
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

    def initialise(
        self,
        vega: VegaService,
        create_key: bool = True,
        mint_key: bool = False,
    ):
        """Initialise the agents wallet and mint the required market asset.

        Args:
            vega (VegaServiceNull):
                Object running a locally-hosted Vega service.
        """

        super().initialise(vega=vega, create_key=create_key)
        self.market_id = self.vega.find_market_id(name=self.market_name)

        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            self.vega.mint(
                wallet_name=self.wallet_name,
                asset=self.asset_id,
                amount=self.initial_asset_mint,
                key_name=self.key_name,
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
            trading_key=self.key_name,
        )

    def _cancel_order(self, vega_state: VegaState):
        orders = vega_state.market_state.get(self.market_id, {}).orders.get(
            self.vega.wallet.public_key(
                wallet_name=self.wallet_name, name=self.key_name
            ),
            {},
        )

        if len(orders) > 0:
            order_key = self.random_state.choice(list(orders.keys()))
            order = orders[order_key]

            self.vega.cancel_order(
                wallet_name=self.wallet_name,
                market_id=self.market_id,
                order_id=order.id,
                trading_key=self.key_name,
            )


class InformedTrader(StateAgentWithWallet):
    NAME_BASE = "informed_trader"

    def __init__(
        self,
        key_name: str,
        price_process: List[float],
        market_name: str = None,
        asset_name: str = None,
        initial_asset_mint: float = 1e8,
        proportion_taken: float = 0.8,
        accuracy: float = 1.0,
        lookahead: int = 1,
        max_abs_position: float = 100,
        tag: str = "",
        wallet_name: Optional[str] = None,
        random_state: Optional[np.random.RandomState] = None,
    ):
        """Agent capable of placing informed market orders.

        At each step, the agent is able to lookahead a specified number of steps and
        determine whether orders currently on the book are profitable to fill. The
        agent will then fill a specified proportion of those orders. This order will
        then be recorded in a FIFO queue.

        At each step, if the queue is full, the agent will get an order from the queue
        and place a market order to close the position created by the original order.
        Following the above logic, orders should be "closed" n steps after they are
        placed, i.e. when they are in the money.

        Additionally the accuracy arg can be used to configure the accuracy of the agent
        (1.0 being well-informed, 0.0 being ill-informed). If the agent is ill-informed
        it has a random probability of placing its orders on the wrong side.

        Args:
            wallet_name (str):
                Name of the wallet.
            price_process (List[float]):
                List of price history for agent to look-ahead.
            market_name (str, optional):
                Name of the market to trade in. Defaults to None.
            asset_name (str, optional):
                Name of the settlement asset used in the market. Defaults to None.
            initial_asset_mint (float, optional):
                Initial amount of asset to mint. Defaults to 1e8.
            proportion_taken (float, optional):
                Proportion of profitable orders filled at each step. Defaults to 0.8.
            accuracy (float, optional):
                Accuracy of agent's speculations. Defaults to 1.0.
            lookahead (int, optional):
                Number of steps to look ahead. Defaults to 1.
            max_abs_position (float, optional):
                The maximum absolute position the trader can have. Defaults to 100.
            tag (str, optional):
                Market tag. Defaults to "".
            key_name (Optional[str], optional):
                Name of key in wallet. Defaults to None.
            random_state (Optional[np.random.RandomState], optional):
                RandomState object used to generate randomness. Defaults to None.
        """
        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)
        self.initial_asset_mint = initial_asset_mint
        self.price_process = price_process
        self.current_step = 0
        self.sim_length = len(price_process)
        self.proportion_taken = proportion_taken
        self.market_name = f"ETH:USD_{self.tag}" if market_name is None else market_name
        self.asset_name = f"tDAI_{self.tag}" if asset_name is None else asset_name
        self.key_name = key_name
        self.accuracy = accuracy
        self.lookahead = lookahead
        self.max_abs_position = max_abs_position
        self.current_step = 0
        self.queue = Queue()

        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        # Initialise wallet
        super().initialise(vega=vega, create_key=create_key)

        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        # Get asset id
        tDAI_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            # Top up asset
            self.vega.mint(
                wallet_name=self.wallet_name,
                asset=tDAI_id,
                amount=self.initial_asset_mint,
                key_name=self.key_name,
            )

        self.pdp = self.vega._market_pos_decimals.get(self.market_id, {})
        self.vega.wait_for_total_catchup()

    def step(self, vega_state: VegaState):
        # Increment the current step
        self.current_step += 1

        # Skip stepping if the market is in auction
        trading_mode = vega_state.market_state[self.market_id].trading_mode
        if (
            not trading_mode
            == markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS
        ):
            return

        # If the queue is full, settle an order
        if self.queue.full():
            self._settle_order(self.queue.get())

        # Create an order, submit it, and add it to the queue to be settled
        self.queue.put(self._create_order())

    def _create_order(self) -> ITOrder:
        # Determine the correct side
        price = self.price_process[self.current_step]
        next_price = self.price_process[
            min([self.current_step + self.lookahead + 1, len(self.price_process) - 1])
        ]
        side = vega_protos.SIDE_BUY if price < next_price else vega_protos.SIDE_SELL

        # Determine the volume of orders which can be profited from
        order_book = self.vega.market_depth(market_id=self.market_id)
        if side == vega_protos.SIDE_BUY:
            volume = sum(
                [order.volume for order in order_book.sells if order.price < next_price]
            )
        else:
            volume = sum(
                [order.volume for order in order_book.buys if order.price > next_price]
            )

        # Determine the size of the order
        size = round(self.proportion_taken * volume, self.pdp)

        # Limit order size to not exceed max allowable position
        position = self.vega.positions_by_market(
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            key_name=self.key_name,
        )
        cur_position = int(position.open_volume) if position is not None else 0
        new_position = (
            cur_position + size if side == vega_protos.SIDE_BUY else cur_position - size
        )
        if abs(new_position) > self.max_abs_position:
            size = max([0, self.max_abs_position - abs(cur_position)])

        # Add a random probability the agent speculates the wrong side
        if self.random_state.rand() <= self.accuracy:
            side = side
        else:
            side = (
                vega_protos.SIDE_BUY
                if side == vega_protos.SIDE_SELL
                else vega_protos.SIDE_SELL
            )

        # Attempt to submit the order and add it to the queue
        try:
            self.vega.submit_market_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                side=side,
                volume=size,
                wait=False,
                fill_or_kill=False,
                trading_key=self.key_name,
            )
            return ITOrder(side=side, size=size)

        except OrderRejectedError:
            logger.debug("Order rejected")
            return None

    def _close_positions(self, order: ITOrder):
        # If order is blank
        if order is None:
            return

        # If original order was a buy, agent sells, and visa versa
        if order.side == vega_protos.SIDE_BUY:
            side = vega_protos.SIDE_SELL
        elif order.side == vega_protos.SIDE_SELL:
            side = vega_protos.SIDE_BUY
        else:
            return

        # Try to settle the order
        try:
            self.vega.submit_market_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                side=side,
                volume=order.volume,
                wait=True,
                fill_or_kill=False,
                trading_key=self.key_name,
            )
        except OrderRejectedError:
            logger.debug("Order rejected")


class SimpleLiquidityProvider(StateAgentWithWallet):
    NAME_BASE = "simple_liq_provider"

    def __init__(
        self,
        key_name: str,
        market_name: str,
        asset_name: str,
        bid_inner_bound_fn: Callable,
        bid_outer_bound_fn: Callable,
        ask_inner_bound_fn: Callable,
        ask_outer_bound_fn: Callable,
        offset_proportion: int,
        initial_asset_mint: float,
        commitment_amount: float = 6000,
        fee: float = 0.001,
        tag: str = "",
        wallet_name: Optional[str] = None,
    ):
        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)

        self.market_name = market_name
        self.asset_name = asset_name

        self.initial_asset_mint = initial_asset_mint

        self.bid_inner_bound_fn = bid_inner_bound_fn
        self.bid_outer_bound_fn = bid_outer_bound_fn
        self.ask_inner_bound_fn = ask_inner_bound_fn
        self.ask_outer_bound_fn = ask_outer_bound_fn
        self.offset_proportion = offset_proportion

        self.fee = fee

        self.commitment_amount = commitment_amount

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        super().initialise(vega=vega, create_key=create_key)

        self.market_id = self.vega.find_market_id(name=self.market_name)
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            self.vega.mint(
                wallet_name=self.wallet_name,
                asset=self.asset_id,
                amount=self.initial_asset_mint,
                key_name=self.key_name,
            )
            self.vega.wait_fn(2)

        self.vega.submit_simple_liquidity(
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            key_name=self.key_name,
            commitment_amount=self.commitment_amount,
            fee=self.fee,
            reference_buy="PEGGED_REFERENCE_MID",
            reference_sell="PEGGED_REFERENCE_MID",
            delta_buy=5,
            delta_sell=5,
            is_amendment=False,
        )

    def step(self, vega_state: VegaState):
        # Don't amend offset if in auction
        if (
            vega_state.market_state[self.market_id].trading_mode
            != markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS
        ):
            return

        # Get the lower and upper bounds liquidity can be pegged between
        bid_inner_bound = self.bid_inner_bound_fn(
            vega_state=vega_state, market_id=self.market_id
        )
        bid_outer_bound = self.bid_outer_bound_fn(
            vega_state=vega_state, market_id=self.market_id
        )
        ask_inner_bound = self.ask_inner_bound_fn(
            vega_state=vega_state, market_id=self.market_id
        )
        ask_outer_bound = self.ask_outer_bound_fn(
            vega_state=vega_state, market_id=self.market_id
        )

        bid_price = (
            bid_inner_bound
            - (bid_inner_bound - bid_outer_bound) * self.offset_proportion
        )
        ask_price = (
            ask_inner_bound
            + (ask_outer_bound - ask_inner_bound) * self.offset_proportion
        )

        # Calculate offsets for the bid and ask pegs from the mid-price
        bid_offset = vega_state.market_state[self.market_id].midprice - bid_price
        ask_offset = ask_price - vega_state.market_state[self.market_id].midprice

        # Submit liquidity
        self.vega.submit_simple_liquidity(
            wallet_name=self.wallet_name,
            key_name=self.key_name,
            market_id=self.market_id,
            commitment_amount=self.commitment_amount,
            fee=self.fee,
            reference_buy="PEGGED_REFERENCE_MID",
            reference_sell="PEGGED_REFERENCE_MID",
            delta_buy=bid_offset,
            delta_sell=ask_offset,
            is_amendment=True,
        )


class MomentumTrader(StateAgentWithWallet):
    """
    Trading Agent that can follow multiple momentum trading strategies.

    At each step, the trading agent collects future price and trades under
    certain momentum indicator.
    """

    NAME_BASE = "mom_trader"

    def __init__(
        self,
        key_name: str,
        market_name: str,
        asset_name: str,
        momentum_strategy: str = "RSI",
        momentum_strategy_args: Dict[str, float] = None,
        indicator_threshold: Tuple[float, float] = (70, 30),
        initial_asset_mint: float = 1e5,
        order_intensity: float = 5,
        base_order_size: float = 1,
        trading_proportion: float = 1,
        random_state: Optional[np.random.RandomState] = None,
        send_limit_order: bool = False,
        time_in_force_opt: Union[vega_protos.vega.Order.TimeInForce, str] = None,
        duration: Optional[float] = 120,
        offset_levels: int = 10,
        tag: str = "",
        wallet_name: str = None,
    ):
        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)
        self.market_name = market_name
        self.asset_name = asset_name
        self.initial_asset_mint = initial_asset_mint
        self.order_intensity = order_intensity
        self.base_order_size = base_order_size
        self.trading_proportion = trading_proportion
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

        # Order Type
        self.send_limit_order = send_limit_order
        if send_limit_order:
            self.time_in_force_opt = (
                time_in_force_opt
                if time_in_force_opt is not None
                else "TIME_IN_FORCE_IOC"
            )
            self.duration = duration
            self.offset_levels = offset_levels

        # Momentum Strategy
        self.momentum_strategy = momentum_strategy
        self.momentum_strategy_args = momentum_strategy_args
        self.indicator_threshold = indicator_threshold
        self.momentum_func_dict = {
            "RSI": self._RSI,
            "CMO": self._CMO,
            "STOCHRSI": self._STOCHRSI,
            "APO": self._APO,
            "MACD": self._MACD,
        }

        self.prices = np.array([])
        self.indicators = []

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        super().initialise(vega=vega, create_key=create_key)

        self.market_id = self.vega.find_market_id(name=self.market_name)

        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            self.vega.mint(
                wallet_name=self.wallet_name,
                asset=self.asset_id,
                amount=self.initial_asset_mint,
                key_name=self.key_name,
            )

        self.pdp = self.vega._market_pos_decimals.get(self.market_id, {})
        self.mdp = self.vega._market_price_decimals.get(self.market_id, {})
        self.adp = self.vega._asset_decimals.get(self.asset_id, {})
        self.vega.wait_for_total_catchup()

    def step(self, vega_state: VegaState):
        self.prices = np.append(
            self.prices, vega_state.market_state[self.market_id].midprice
        )

        signal = self.momentum_func_dict.get(self.momentum_strategy, self._RSI)()
        if signal == TradeSignal.NOACTION:
            return

        trade_side = (
            vega_protos.SIDE_BUY if signal == TradeSignal.BUY else vega_protos.SIDE_SELL
        )
        volume = self.random_state.poisson(self.order_intensity)

        volume *= self.trading_proportion * self.base_order_size

        if volume:
            if not self.send_limit_order:
                self.vega.submit_market_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    side=trade_side,
                    volume=volume,
                    wait=False,
                    fill_or_kill=False,
                    trading_key=self.key_name,
                )
            else:
                best_bid, best_ask = self.vega.best_prices(market_id=self.market_id)
                price = (
                    best_ask + self.offset_levels / 10**self.mdp
                    if signal == TradeSignal.BUY
                    else best_bid - self.offset_levels / 10**self.mdp
                )
                expires_at = int(self.vega.get_blockchain_time() + self.duration * 1e9)
                self.vega.submit_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    order_type="TYPE_LIMIT",
                    time_in_force=self.time_in_force_opt,
                    side=trade_side,
                    volume=volume,
                    price=price,
                    expires_at=expires_at,
                    wait=False,
                    trading_key=self.key_name,
                )

    def _MACD(self):
        _, _, macdhist = (
            talib.MACD(self.prices)
            if self.momentum_strategy_args is None
            else talib.MACD(
                self.prices,
                fastperiod=self.momentum_strategy_args["fastperiod"],
                slowperiod=self.momentum_strategy_args["slowperiod"],
                signalperiod=self.momentum_strategy_args["signalperiod"],
            )
        )
        self.indicators = macdhist

        if len(self.indicators) == 1:
            return 0

        if self.indicators[-2] < 0 and self.indicators[-1] >= 0:
            signal = TradeSignal.BUY

        elif self.indicators[-2] > 0 and self.indicators[-1] <= 0:
            signal = TradeSignal.SELL

        else:
            signal = TradeSignal.NOACTION
        return signal

    def _APO(self):
        self.indicators = (
            talib.APO(self.prices)
            if self.momentum_strategy_args is None
            else talib.APO(
                self.prices,
                fastperiod=self.momentum_strategy_args["fastperiod"],
                slowperiod=self.momentum_strategy_args["slowperiod"],
            )
        )

        if len(self.indicators) == 1:
            return TradeSignal.NOACTION

        if self.indicators[-2] < 0 and self.indicators[-1] >= 0:
            signal = TradeSignal.BUY

        elif self.indicators[-2] > 0 and self.indicators[-1] <= 0:
            signal = TradeSignal.SELL

        else:
            signal = TradeSignal.NOACTION
        return signal

    def _RSI(self):
        self.indicators = (
            talib.RSI(self.prices)
            if self.momentum_strategy_args is None
            else talib.RSI(
                self.prices,
                timeperiod=self.momentum_strategy_args["timeperiod"],
            )
        )

        if self.indicators[-1] >= max(self.indicator_threshold):
            signal = TradeSignal.SELL

        elif self.indicators[-1] <= min(self.indicator_threshold):
            signal = TradeSignal.BUY

        else:
            signal = TradeSignal.NOACTION
        return signal

    def _CMO(self):
        self.indicators = (
            talib.CMO(self.prices)
            if self.momentum_strategy_args is None
            else talib.CMO(
                self.prices,
                timeperiod=self.momentum_strategy_args["timeperiod"],
            )
        )

        if self.indicators[-1] >= max(self.indicator_threshold):
            signal = TradeSignal.SELL

        elif self.indicators[-1] <= min(self.indicator_threshold):
            signal = TradeSignal.BUY

        else:
            signal = TradeSignal.NOACTION
        return signal

    def _STOCHRSI(self):
        fastk, fastd = (
            talib.STOCHRSI(self.prices)
            if self.momentum_strategy_args is None
            else talib.STOCHRSI(
                self.prices,
                timeperiod=self.momentum_strategy_args["timeperiod"],
                fastk_period=self.momentum_strategy_args["fastk_period"],
                fastd_period=self.momentum_strategy_args["fastd_period"],
            )
        )
        self.indicators = fastk
        crossover = fastd - fastk
        if len(crossover) == 1:
            return TradeSignal.NOACTION

        if (
            self.indicators[-1] >= max(self.indicator_threshold)
            and crossover[-2] < 0
            and crossover[-1] >= 0
        ):
            signal = TradeSignal.SELL

        elif (
            self.indicators[-1] <= min(self.indicator_threshold)
            and crossover[-2] > 0
            and crossover[-1] <= 0
        ):
            signal = TradeSignal.BUY

        else:
            signal = TradeSignal.NOACTION
        return signal


class Snitch(StateAgent):
    NAME_BASE = "snitch"

    def __init__(
        self,
        agents: Optional[Dict[str, Agent]] = None,
        additional_state_fn: Optional[
            Callable[[VegaService, Dict[str, Agent]], Any]
        ] = None,
        only_extract_additional: bool = False,
    ):
        self.tag = None
        self.states = []
        self.additional_states = []
        self.agents = agents
        self.additional_state_fn = additional_state_fn
        self.seen_trades = set()
        self.only_extract_additional = only_extract_additional

    def step(self, vega_state: VegaState):
        if not self.only_extract_additional:
            market_infos = {}
            market_datas = {}
            market_depths = {}
            market_trades = {}

            start_time = self.vega.get_blockchain_time()

            all_markets = self.vega.all_markets()
            for market in all_markets:
                market_infos[market.id] = market
                market_datas[market.id] = self.vega.market_data_from_feed(market.id)
                market_depths[market.id] = self.vega.market_depth(
                    market.id, num_levels=50
                )

            all_trades = self.vega.get_trades_from_stream(
                exclude_trade_ids=self.seen_trades
            )
            for trade in all_trades:
                if trade.id not in self.seen_trades:
                    self.seen_trades.add(trade.id)
                    market_trades.setdefault(market.id, []).append(trade)

            accounts = self.vega.list_accounts()
            self.states.append(
                MarketHistoryData(
                    at_time=start_time,
                    market_info=market_infos,
                    market_data=market_datas,
                    accounts=accounts,
                    market_depth=market_depths,
                    trades=market_trades,
                )
            )
        if self.additional_state_fn is not None:
            self.additional_states.append(
                self.additional_state_fn(self.vega, self.agents)
            )


class KeyFunder(Agent):
    NAME_BASE = "key_funder"

    def __init__(
        self,
        keys_to_fund: List[str],
        asset_to_fund: str,
        amount_to_fund: float,
        tag: Optional[str] = None,
    ):
        super().__init__(tag=tag)
        self.keys_to_fund = keys_to_fund
        self.amount_to_fund = amount_to_fund
        self.asset_to_fund = asset_to_fund

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        self.vega = vega
        asset_id = self.vega.find_asset_id(self.asset_to_fund)
        amount = self.amount_to_fund * 10 ** self.vega.asset_decimals[asset_id]
        for key in self.keys_to_fund:
            faucet.mint(key, asset_id, amount=amount, faucet_url=self.vega.faucet_url)
        time.sleep(1)

    def step(self, vega_state: VegaState):
        pass
