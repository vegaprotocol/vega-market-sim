from __future__ import annotations
from dataclasses import dataclass

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
        initial_asset_mint: float = 1000000,
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
            initial_price - self.spread,
            initial_price,
            side=vega_protos.SIDE_BUY,
        )
        sell_shape = self._calculate_price_volume_levels(
            initial_price + self.spread,
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

            for i in range(market_regime.num_levels_per_side):
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
                        vega_protos.SIDE_SELL,
                        new_sell_shape[i][0],
                        new_sell_shape[i][1],
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
        tag: str = "",
    ):
        super().__init__(wallet_name + tag, wallet_pass)
        self.side = side
        self.initial_asset_mint = initial_asset_mint
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

        self.vega.wait_for_total_catchup()
        # Get asset id
        tDAI_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=tDAI_id,
            amount=self.initial_asset_mint,
        )
        self.vega.wait_fn(2)
        self.vega.wait_for_total_catchup()

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
        commitment_amount: float = 6000,
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
            liquidity_commitment=vega.build_new_market_liquidity_commitment(
                asset_id=self.asset_id,
                commitment_amount=self.commitment_amount,
                fee=0.001,
                buy_specs=[("PEGGED_REFERENCE_BEST_BID", 5, 1)],
                sell_specs=[("PEGGED_REFERENCE_BEST_ASK", 5, 1)],
                market_decimals=self.mdp,
            ),
        )
        self.vega.wait_fn(5)

        # Get market id
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]

    def finalise(self):
        if self.settlement_price is not None:
            self.vega.settle_market(
                self.terminate_wallet_name, self.settlement_price, self.market_id
            )
