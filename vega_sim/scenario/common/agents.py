from __future__ import annotations

import numpy as np
from collections import namedtuple
from typing import List, Optional, Union
from numpy.typing import ArrayLike

from vega_sim.environment import VegaState
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import markets as markets_protos, vega as vega_protos


WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Send selling/buying MOs to hit LP orders
TRADER_WALLET = WalletConfig("trader", "trader")

BACKGROUND_MARKET = WalletConfig("market", "market")

# Pass opening auction
AUCTION1_WALLET = WalletConfig("AUCTION1", "AUCTION1pass")
AUCTION2_WALLET = WalletConfig("AUCTION2", "AUCTION2pass")


class MarketOrderTrader(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        market_name: str,
        asset_name: str,
        buy_intensity: float = 1,
        sell_intensity: float = 1,
        tag: str = "",
        random_state: Optional[np.random.RandomState] = None,
    ):
        super().__init__(wallet_name + str(tag), wallet_pass)
        self.buy_intensity = buy_intensity
        self.sell_intensity = sell_intensity
        self.tag = tag
        self.market_name = market_name
        self.asset_name = asset_name
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

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
            amount=100000,
        )
        self.vega.wait_fn(2)

    def step(self, vega_state: VegaState):
        buy_first = self.random_state.choice([0, 1])

        buy_vol = self.random_state.poisson(self.buy_intensity)
        sell_vol = self.random_state.poisson(self.sell_intensity)

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
            vega_state.market_state[self.market_id].trading_mode
            == markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS
        ) and vega_state.market_state[
            self.market_id
        ].state == markets_protos.Market.State.STATE_ACTIVE:
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
        spread: float = 0.02,
        tick_spacing: float = 0.01,
        num_levels_per_side: int = 20,
        base_volume_size: float = 0.1,
        order_distribution_kappa: float = 1,
        tag: str = "",
    ):
        super().__init__(wallet_name + tag, wallet_pass)
        self.price_process = price_process
        self.spread = spread
        self.current_step = 0
        self.tag = tag
        self.tick_spacing = tick_spacing
        self.num_levels_per_side = num_levels_per_side
        self.base_volume_size = base_volume_size

        self.market_name = market_name
        self.asset_name = asset_name
        self.kappa = order_distribution_kappa

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

        initial_price = self.price_process[self.current_step]
        buy_shape = self._calculate_price_volume_levels(
            initial_price - self.spread,
            initial_price,
            side=vega_protos.SIDE_BUY,
        )
        sell_shape = self._calculate_price_volume_levels(
            initial_price + self.spread,
            initial_price,
            side=vega_protos.SIDE_SELL,
        )

        for price, size in buy_shape:
            self._submit_order(vega_protos.SIDE_BUY, price, size)
        for price, size in sell_shape:
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
            new_price - self.spread,
            new_price,
            side=vega_protos.SIDE_BUY,
        )
        new_sell_shape = self._calculate_price_volume_levels(
            new_price + self.spread,
            new_price,
            side=vega_protos.SIDE_SELL,
        )

        buy_orders, sell_orders = [], []

        for order in orders.values():
            if order.side == vega_protos.SIDE_BUY:
                buy_orders.append(order)
            else:
                sell_orders.append(order)

        for i in range(self.num_levels_per_side):
            if i < len(buy_orders):
                order_to_amend = buy_orders[i]
                self.vega.amend_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    order_id=order_to_amend.id,
                    price=new_buy_shape[i][0],
                    volume_delta=new_buy_shape[i][1] - order_to_amend.remaining,
                )
            else:
                self._submit_order(
                    vega_protos.SIDE_BUY, new_buy_shape[i][0], new_buy_shape[i][1]
                )

            if i < len(sell_orders):
                order_to_amend = sell_orders[i]
                self.vega.amend_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    order_id=order_to_amend.id,
                    price=new_sell_shape[i][0],
                    volume_delta=new_sell_shape[i][1] - order_to_amend.remaining,
                )
            else:
                self._submit_order(
                    vega_protos.SIDE_SELL, new_sell_shape[i][0], new_sell_shape[i][1]
                )


class OpenAuctionPass(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        side: str,
        market_name: str,
        asset_name: str,
        initial_price: float = 0.3,
        tag: str = "",
    ):
        super().__init__(wallet_name + tag, wallet_pass)
        self.side = side
        self.initial_price = initial_price
        self.tag = tag
        self.market_name = market_name
        self.asset_name = asset_name

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
            amount=100000,
        )
        self.vega.wait_fn(2)

        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side=self.side,
            volume=1,
            price=self.initial_price,
        )

    def step(self, vega_state: VegaState):
        pass
