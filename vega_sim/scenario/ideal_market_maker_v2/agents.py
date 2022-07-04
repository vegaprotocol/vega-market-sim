from __future__ import annotations

import numpy as np
from collections import namedtuple
from typing import List, Optional, Union
from numpy.typing import ArrayLike
from vega_sim.api.data import Order

from vega_sim.scenario.ideal_market_maker_v2.utils.strategy import (
    A_S_MMmodel,
    GLFT_approx,
)
from vega_sim.environment import VegaState
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import markets as markets_protos, vega as vega_protos
from vega_sim.service import PeggedOrder

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Set up parties in the market/ Submit liquidity provision
MM_WALLET = WalletConfig("mm", "pin")

# Send selling/buying MOs to hit LP orders
TRADER_WALLET = WalletConfig("trader", "trader")

BACKGROUND_MARKET = WalletConfig("market", "market")

# Pass opening auction
AUCTION1_WALLET = WalletConfig("AUCTION1", "AUCTION1pass")
AUCTION2_WALLET = WalletConfig("AUCTION2", "AUCTION2pass")

# Terminate the market and send settlment price
TERMINATE_WALLET = WalletConfig("FJMKnwfZdd48C8NqvYrG", "bY3DxwtsCstMIIZdNpKs")


class OptimalMarketMaker(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        terminate_wallet_name: str,
        terminate_wallet_pass: str,
        price_processs: List[float],
        spread: float = 0.00002,
        num_steps: int = 180,
        market_order_arrival_rate: float = 5,
        kappa: float = 500,
        inventory_upper_boundary: int = 20,
        inventory_lower_boundary: int = -20,
        terminal_penalty_parameter: float = 10**-4,
        running_penalty_parameter: float = 5 * 10**-6,
        asset_decimal: int = 5,
        market_decimal: int = 5,
        market_position_decimal: int = 2,
        commitment_amount: float = 6000,
        tag: str = "",
    ):
        super().__init__(wallet_name + str(tag), wallet_pass)
        self.terminate_wallet_name = terminate_wallet_name + str(tag)
        self.terminate_wallet_pass = terminate_wallet_pass

        self.price_process = price_processs
        self.spread = spread
        self.time = num_steps
        self.Lambda = market_order_arrival_rate
        self.kappa = kappa
        self.q_upper = inventory_upper_boundary
        self.q_lower = inventory_lower_boundary
        self.alpha = terminal_penalty_parameter
        self.phi = running_penalty_parameter
        self.adp = asset_decimal
        self.mdp = market_decimal
        self.market_position_decimal = market_position_decimal
        self.commitment_amount = commitment_amount

        self.current_step = 0

        self.tag = tag

        self.long_horizon_estimate = num_steps >= 200

        if not self.long_horizon_estimate:
            self.optimal_bid, self.optimal_ask, _ = A_S_MMmodel(
                T=self.time / 60 / 24 / 365.25,
                dt=1 / 60 / 24 / 365.25,
                length=self.time + 1,
                q_upper=self.q_upper,
                q_lower=self.q_lower,
                mdp=self.mdp,
                kappa=self.kappa,
                Lambda=self.Lambda,
                alpha=self.alpha,
                phi=self.phi,
            )
        else:
            self.optimal_bid, self.optimal_ask = GLFT_approx(
                q_upper=self.q_upper,
                q_lower=self.q_lower,
                kappa=self.kappa,
                Lambda=self.Lambda,
                alpha=self.alpha,
                phi=self.phi,
            )

    def finalise(self):
        self.vega.settle_market(
            self.terminate_wallet_name, self.price_process[-1], self.market_id
        )

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet for LP/ Settle Party
        super().initialise(vega=vega)
        self.vega.create_wallet(self.terminate_wallet_name, self.terminate_wallet_pass)

        # Faucet vega tokens
        self.vega.wait_for_datanode_sync()
        self.vega.mint(
            self.wallet_name,
            asset="VOTE",
            amount=1e4,
        )
        self.vega.wait_fn(5)

        ccy_name = f"tDAI{self.tag}"
        # Create asset
        self.vega.create_asset(
            self.wallet_name,
            name=ccy_name,
            symbol=ccy_name,
            decimals=self.adp,
            max_faucet_amount=5e10,
        )
        self.vega.wait_fn(5)
        # Get asset id
        self.tdai_id = self.vega.find_asset_id(symbol=ccy_name)
        # Top up asset
        self.initial = 100000
        self.vega.wait_for_datanode_sync()
        self.vega.mint(
            self.wallet_name,
            asset=self.tdai_id,
            amount=self.initial,
        )
        self.vega.wait_for_datanode_sync()

        self.vega.update_network_parameter(
            self.wallet_name,
            "market.liquidity.minimum.probabilityOfTrading.lpOrders",
            "0.001",
        )
        self.vega.update_network_parameter(
            self.wallet_name,
            "market.liquidity.stakeToCcySiskas",
            "0.001",
        )
        market_name = f"BTC:DAI_{self.tag}"

        # Set up a future market
        self.vega.create_simple_market(
            market_name=market_name,
            proposal_wallet=self.wallet_name,
            settlement_asset_id=self.tdai_id,
            termination_wallet=self.terminate_wallet_name,
            market_decimals=self.mdp,
            position_decimals=self.market_position_decimal,
            future_asset=ccy_name,
            liquidity_commitment=vega.build_new_market_liquidity_commitment(
                asset_id=self.tdai_id,
                commitment_amount=self.commitment_amount,
                fee=0.001,
                buy_specs=[("PEGGED_REFERENCE_BEST_BID", 0.2, 1)],
                sell_specs=[("PEGGED_REFERENCE_BEST_ASK", 0.2, 1)],
                market_decimals=self.mdp,
            ),
        )
        self.vega.wait_fn(5)

        market_name = f"BTC:DAI_{self.tag}"
        # Get market id
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == market_name
        ][0]

    def optimal_strategy(self, current_position):

        if current_position >= self.q_upper:
            current_bid_depth = (
                self.optimal_bid[self.current_step, 0]
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
                self.optimal_ask[self.current_step, -1]
                if not self.long_horizon_estimate
                else self.optimal_ask[-1]
            )
        else:
            current_bid_depth = (
                self.optimal_bid[
                    self.current_step, int(self.q_upper - 1 - current_position)
                ]
                if not self.long_horizon_estimate
                else self.optimal_bid[int(self.q_upper - 1 - current_position)]
            )
            current_ask_depth = (
                self.optimal_ask[
                    self.current_step, int(self.q_upper - current_position)
                ]
                if not self.long_horizon_estimate
                else self.optimal_ask[int(self.q_upper - current_position)]
            )

        return current_bid_depth, current_ask_depth

    def step(self, vega_state: VegaState):
        # Each step, MM posts optimal bid/ask depths
        position = self.vega.positions_by_market(
            wallet_name=self.wallet_name, market_id=self.market_id
        )

        current_position = int(position[0].open_volume) if position else 0
        self.bid_depth, self.ask_depth = self.optimal_strategy(current_position)

        buy_order, sell_order = None, None

        for order in (
            vega_state.market_state[self.market_id]
            .orders[self.vega.wallet.public_key(self.wallet_name)]
            .values()
        ):
            if order.side == vega_protos.SIDE_BUY:
                buy_order = order
            else:
                sell_order = order

        # self.vega.submit_simple_liquidity(
        #     wallet_name=self.wallet_name,
        #     market_id=self.market_id,
        #     commitment_amount=self.commitment_amount,
        #     fee=0.002,
        #     reference_buy="PEGGED_REFERENCE_MID",
        #     reference_sell="PEGGED_REFERENCE_MID",
        #     delta_buy=self.bid_depth,
        #     delta_sell=self.ask_depth,
        # )

        self._place_orders(
            buy_offset=self.bid_depth,
            sell_offset=self.ask_depth,
            volume=1,
            buy_order=buy_order,
            sell_order=sell_order,
        )
        self.current_step += 1

    def _place_orders(
        self,
        buy_offset: float,
        sell_offset: float,
        volume: float,
        buy_order: Optional[str] = None,
        sell_order: Optional[str] = None,
    ):
        self._place_or_amend_order(
            offset=buy_offset, volume=volume, order=buy_order, side=vega_protos.SIDE_BUY
        )
        self._place_or_amend_order(
            offset=sell_offset,
            volume=volume,
            order=sell_order,
            side=vega_protos.SIDE_SELL,
        )

    def _place_or_amend_order(
        self,
        offset: float,
        volume: float,
        side: vega_protos.Side,
        order: Optional[Order] = None,
    ):
        if order is None:
            self.vega.submit_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                pegged_order=PeggedOrder(
                    reference=vega_protos.PEGGED_REFERENCE_MID, offset=offset
                ),
                side=side,
                volume=volume,
                order_type=vega_protos.Order.Type.TYPE_LIMIT,
                wait=False,
                time_in_force=vega_protos.Order.TimeInForce.TIME_IN_FORCE_GTC,
            )
        else:
            self.vega.amend_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                order_id=order.id,
                pegged_reference=vega_protos.PEGGED_REFERENCE_MID,
                pegged_offset=offset,
                volume_delta=volume - order.size,
            )


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
        initial_price: float = 0.3,
        tag: str = "",
    ):
        super().__init__(wallet_name + tag, wallet_pass)
        self.side = side
        self.initial_price = initial_price
        self.tag = tag

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet
        super().initialise(vega=vega)
        # Get market id
        market_name = f"BTC:DAI_{self.tag}"
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == market_name
        ][0]

        # Get asset id
        tDAI_id = self.vega.find_asset_id(symbol=f"tDAI{self.tag}")
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
