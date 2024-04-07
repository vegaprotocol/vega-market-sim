from typing import Iterable, List, Optional, Tuple, Union
from logging import getLogger

import numpy as np

from vega_sim.proto.vega import vega as vega_protos
from vega_sim.scenario.common.agents import (
    LiquidityProvision,
    MMOrder,
    ShapedMarketMaker,
    VegaState,
)

logger = getLogger(__name__)


def _price_for_size(
    side: vega_protos.Side,
    position: float,
    ref_price: float,
    k_scaling_large: float,
    k_scaling_small: float,
    trade_size: float,
) -> float:
    if side == vega_protos.Side.SIDE_SELL:
        k_scaling = k_scaling_small if position >= 0 else k_scaling_large

        virtual_sell = (k_scaling / ref_price) ** 0.5
        virtual_buy = (k_scaling * ref_price) ** 0.5

        return (virtual_buy + trade_size * ref_price) / virtual_sell
    elif side == vega_protos.Side.SIDE_BUY:
        k_scaling = k_scaling_small if position <= 0 else k_scaling_large

        virtual_sell = (k_scaling / ref_price) ** 0.5
        virtual_buy = (k_scaling * ref_price) ** 0.5

        return virtual_buy / (virtual_sell + trade_size)


def _build_price_levels(
    position: float,
    ref_price: float,
    min_trade_unit: float,
    num_steps: int,
    tick_spacing: float,
    k_scaling_large: float,
    k_scaling_small: float,
):
    buy_prices = []
    sell_prices = []
    buy_price = ref_price
    sell_price = ref_price
    for i in range(0, num_steps):
        buy_price = _price_for_size(
            side=vega_protos.Side.SIDE_BUY,
            position=position + i * min_trade_unit,
            ref_price=buy_price,
            k_scaling_large=k_scaling_large,
            k_scaling_small=k_scaling_small,
            trade_size=min_trade_unit,
        )
        buy_prices.append(buy_price)

        sell_price = _price_for_size(
            vega_protos.Side.SIDE_SELL,
            position=position - i * min_trade_unit,
            ref_price=sell_price,
            k_scaling_large=k_scaling_large,
            k_scaling_small=k_scaling_small,
            trade_size=min_trade_unit,
        )
        sell_prices.append(sell_price)

    return sorted(buy_prices, reverse=True), sorted(sell_prices, reverse=False)


def _aggregate_price_levels(
    prices: List[float],
    side: vega_protos.Side,
    tick_spacing: float,
    starting_price: float,
    min_trade_unit: float,
    max_levels: Optional[int] = None,
) -> List[MMOrder]:
    shifter = 1 if side == vega_protos.Side.SIDE_SELL else -1
    outputs = []

    current_price_level = starting_price + shifter * tick_spacing
    price_level_vol = 0

    while len(prices) > 0:
        price, prices = prices[0], prices[1:]

        if shifter * price <= shifter * current_price_level:
            price_level_vol += min_trade_unit
        else:
            current_price_level += shifter * tick_spacing

            if price_level_vol > 0:
                outputs.append(
                    MMOrder(
                        size=price_level_vol,
                        price=current_price_level,
                    )
                )
            price_level_vol = 0
            if max_levels is not None and len(outputs) == max_levels:
                break
    if price_level_vol > 0:
        outputs.append(
            MMOrder(
                size=price_level_vol,
                price=current_price_level,
            )
        )

    return outputs


class CFMMarketMaker(ShapedMarketMaker):
    NAME_BASE = "cfm_market_maker"

    def __init__(
        self,
        key_name: str,
        num_steps: int,
        initial_asset_mint: float = 1000000,
        market_name: str = None,
        asset_name: str = None,
        commitment_amount: float = 6000,
        supplied_amount: Optional[float] = None,
        market_decimal_places: int = 5,
        fee_amount: float = 0.001,
        k_scaling_large: float = 2,
        k_scaling_small: float = 1,
        min_trade_unit: float = 0.01,
        initial_price: float = 100,
        volume_per_side: float = 10,
        num_levels: int = 25,
        tick_spacing: float = 1,
        asset_decimal_places: int = 0,
        tag: str = "",
        wallet_name: str = None,
        orders_from_stream: Optional[bool] = True,
        state_update_freq: Optional[int] = None,
        order_validity_length: Optional[float] = None,
        price_process_generator: Optional[Iterable[float]] = None,
    ):
        super().__init__(
            wallet_name=wallet_name,
            initial_asset_mint=initial_asset_mint,
            market_name=market_name,
            asset_name=asset_name,
            commitment_amount=commitment_amount,
            supplied_amount=supplied_amount,
            market_decimal_places=market_decimal_places,
            asset_decimal_places=asset_decimal_places,
            tag=tag,
            shape_fn=self._generate_shape,
            best_price_offset_fn=lambda *args, **kwargs: (0, 0),
            liquidity_commitment_fn=self._liq_provis,
            key_name=key_name,
            orders_from_stream=orders_from_stream,
            state_update_freq=state_update_freq,
            order_validity_length=order_validity_length,
            price_process_generator=price_process_generator,
        )
        if k_scaling_large < k_scaling_small:
            raise Exception("k_scaling_large should be larger than k_scaling_small")
        self.k_scaling_large = k_scaling_large
        self.k_scaling_small = k_scaling_small
        self.tick_spacing = tick_spacing
        self.num_levels = num_levels
        self.fee_amount = fee_amount
        self.volume_per_side = volume_per_side

        self.num_steps = num_steps
        self.min_trade_unit = min_trade_unit

        self.curr_bids, self.curr_asks = None, None

    def _liq_provis(self, state: VegaState) -> LiquidityProvision:
        return LiquidityProvision(
            amount=self.commitment_amount,
            fee=self.fee_amount,
        )

    def _scale_orders(
        self,
        buy_shape: List[MMOrder],
        sell_shape: List[MMOrder],
    ):
        return (buy_shape, sell_shape)

    def _generate_shape(
        self, bid_price_depth: float, ask_price_depth: float
    ) -> Tuple[List[MMOrder], List[MMOrder]]:
        # ref_price = self.curr_price
        ref_price = self.vega.last_trade_price(market_id=self.market_id)

        if ref_price == 0:
            ref_price = self.curr_price

        bid_orders, ask_orders = _build_price_levels(
            position=self.current_position,
            ref_price=ref_price,
            min_trade_unit=self.min_trade_unit,
            num_steps=int(self.volume_per_side / self.min_trade_unit),
            tick_spacing=self.tick_spacing,
            k_scaling_large=self.k_scaling_large,
            k_scaling_small=self.k_scaling_small,
        )
        agg_bids = _aggregate_price_levels(
            bid_orders,
            side=vega_protos.Side.SIDE_BUY,
            tick_spacing=self.tick_spacing,
            starting_price=ref_price,
            min_trade_unit=self.min_trade_unit,
            max_levels=self.num_levels,
        )
        agg_asks = _aggregate_price_levels(
            ask_orders,
            side=vega_protos.Side.SIDE_SELL,
            tick_spacing=self.tick_spacing,
            starting_price=ref_price,
            min_trade_unit=self.min_trade_unit,
            max_levels=self.num_levels,
        )
        self.curr_bids = agg_bids
        self.curr_asks = agg_asks

        return agg_bids, agg_asks


class CFMV3MarketMaker(ShapedMarketMaker):
    NAME_BASE = "cfm_v3_market_maker"

    def __init__(
        self,
        key_name: str,
        num_steps: int,
        initial_price: float = 100,
        price_width_below: float = 0.05,
        price_width_above: float = 0.05,
        margin_multiple_at_lower: float = 0.8,
        margin_multiple_at_upper: float = 0.8,
        base_balance: float = 100,
        initial_asset_mint: float = 1000000,
        market_name: str = None,
        asset_name: str = None,
        commitment_amount: float = 6000,
        supplied_amount: Optional[float] = None,
        market_decimal_places: int = 5,
        fee_amount: float = 0.001,
        volume_per_side: float = 10,
        num_levels: int = 25,
        tick_spacing: float = 1,
        asset_decimal_places: int = 0,
        bound_perc: float = 0.2,
        tag: str = "",
        wallet_name: str = None,
        orders_from_stream: Optional[bool] = True,
        state_update_freq: Optional[int] = None,
        order_validity_length: Optional[float] = 5,
        price_process_generator: Optional[Iterable[float]] = None,
        use_last_price_as_ref: bool = False,
        position_offset: float = 0,
    ):
        super().__init__(
            wallet_name=wallet_name,
            initial_asset_mint=initial_asset_mint,
            market_name=market_name,
            asset_name=asset_name,
            commitment_amount=commitment_amount,
            supplied_amount=supplied_amount,
            market_decimal_places=market_decimal_places,
            asset_decimal_places=asset_decimal_places,
            tag=tag,
            shape_fn=self._generate_shape,
            best_price_offset_fn=lambda *args, **kwargs: (0, 0),
            liquidity_commitment_fn=self._liq_provis,
            key_name=key_name,
            orders_from_stream=orders_from_stream,
            state_update_freq=state_update_freq,
            order_validity_length=order_validity_length,
            price_process_generator=price_process_generator,
        )
        self.base_price = initial_price
        self.upper_price = (1 + price_width_above) * initial_price
        self.lower_price = (1 - price_width_below) * initial_price

        self.base_price_sqrt = initial_price**0.5
        self.upper_price_sqrt = self.upper_price**0.5
        self.lower_price_sqrt = self.lower_price**0.5

        self.lower_liq_factor = 1 / (self.base_price_sqrt - self.lower_price_sqrt)
        self.upper_liq_factor = 1 / (self.upper_price_sqrt - self.base_price_sqrt)

        self.base_balance = base_balance
        # self.max_loss_at_bound_above = max_loss_at_bound_above
        # self.max_loss_at_bound_below = max_loss_at_bound_below

        self.margin_multiple_at_lower = margin_multiple_at_lower
        self.margin_multiple_at_upper = margin_multiple_at_upper

        self.tick_spacing = tick_spacing
        self.num_levels = num_levels
        self.fee_amount = fee_amount
        self.volume_per_side = volume_per_side

        self.curr_bids, self.curr_asks = None, None
        self.use_last_price_as_ref = use_last_price_as_ref
        self.bound_perc = bound_perc
        self.position_offset = position_offset

    def initialise(
        self,
        vega,
        create_key: bool = True,
        mint_key: bool = True,
    ):
        super().initialise(vega=vega, create_key=create_key, mint_key=mint_key)

        logger.info(
            f"Quoting for key {self.vega.wallet.public_key(self.key_name, self.wallet_name)}"
        )
        risk_factors = vega.get_risk_factors(self.market_id)
        self.short_factor, self.long_factor = risk_factors.short, risk_factors.long

    def _liq_provis(self, state: VegaState) -> LiquidityProvision:
        return LiquidityProvision(
            amount=self.commitment_amount,
            fee=self.fee_amount,
        )

    def _scale_orders(
        self,
        shape: List[MMOrder],
    ):
        return shape

    def _quantity_for_move(
        self,
        start_price_sqrt,
        end_price_sqrt,
        range_upper_price_sqrt,
        liquidity_factor,
    ) -> Optional[float]:
        if liquidity_factor == 0:
            return None
        start_fut_pos = (
            liquidity_factor
            * (range_upper_price_sqrt - start_price_sqrt)
            / (start_price_sqrt * range_upper_price_sqrt)
        )
        end_fut_pos = (
            liquidity_factor
            * (range_upper_price_sqrt - end_price_sqrt)
            / (end_price_sqrt * range_upper_price_sqrt)
        )

        return abs(start_fut_pos - end_fut_pos)

    def _add_orders_at_bounds(
        self,
        bound_perc: float,
        existing_orders: List[MMOrder],
    ) -> List[MMOrder]:
        existing_buys = []
        existing_sells = []

        for o in existing_orders:
            if o.side == vega_protos.SIDE_BUY:
                existing_buys.append(o)
            else:
                existing_sells.append(o)
        best_bid, best_ask = self.vega.best_prices(self.market_id)

        best_ask = min(
            min([x.price for x in existing_sells]),
            best_ask if best_ask != 0.0 else 999999999,
        )
        best_bid = max(max([x.price for x in existing_buys]), best_bid)

        mid = (best_ask + best_bid) / 2
        lower = mid * (1 - bound_perc)
        upper = mid * (1 + bound_perc)

        market_data = self.vega.market_info(self.market_id)
        scaler = 10**market_data.decimal_places
        buy_vol = sum(
            a.price * scaler * round(a.size / scaler)
            for a in existing_buys
            if a.price >= lower
        )
        sell_vol = sum(
            a.price * scaler * round(a.size / scaler)
            for a in existing_sells
            if a.price <= upper
        )

        required_vol = self.commitment_amount * 24

        buy_orders = (
            [
                MMOrder(
                    (required_vol - buy_vol) / lower,
                    lower,
                    vega_protos.SIDE_BUY,
                    time_in_force=vega_protos.Order.TIME_IN_FORCE_GFN,
                )
            ]
            if buy_vol < required_vol
            else []
        )

        sell_orders = (
            [
                MMOrder(
                    (required_vol - sell_vol) / upper,
                    upper,
                    vega_protos.SIDE_SELL,
                    time_in_force=vega_protos.Order.TIME_IN_FORCE_GFN,
                )
            ]
            if sell_vol < required_vol
            else []
        )

        return buy_orders + sell_orders

    def _generate_shape(
        self, bid_price_depth: float, ask_price_depth: float
    ) -> Tuple[List[MMOrder], List[MMOrder]]:
        base_calcs = self._generate_shape_calcs(
            balance=sum(
                a.balance
                for a in self.vega.get_accounts_from_stream(
                    key_name=self.key_name,
                    wallet_name=self.wallet_name,
                    market_id=self.market_id,
                )
            ),
            position=self.current_position + self.position_offset,
        )
        additional_price_bounds = self._add_orders_at_bounds(
            bound_perc=self.bound_perc, existing_orders=base_calcs
        )
        return base_calcs + additional_price_bounds

    def _generate_shape_calcs(
        self,
        balance: float,
        position: float,
    ) -> Tuple[List[MMOrder], List[MMOrder]]:
        if balance == 0:
            print("No funds, no orders")
            return ([], [])
        unit_upper_L = (
            self.upper_price_sqrt
            * self.base_price_sqrt
            / (self.upper_price_sqrt - self.base_price_sqrt)
        )

        unit_lower_L = (
            self.lower_price_sqrt
            * self.base_price_sqrt
            / (self.base_price_sqrt - self.lower_price_sqrt)
        )
        aep_lower = (
            -1
            * unit_lower_L
            * self.base_price_sqrt
            * ((unit_lower_L / (unit_lower_L + self.base_price_sqrt)) - 1)
        )
        aep_upper = (
            -1
            * unit_upper_L
            * self.upper_price_sqrt
            * ((unit_upper_L / (unit_upper_L + self.upper_price_sqrt)) - 1)
        )

        # volume_at_lower = (
        #     self.base_balance
        #     * self.max_loss_at_bound_below
        #     / (aep_lower - self.lower_price)
        # )
        # volume_at_upper = (
        #     self.base_balance
        #     * self.max_loss_at_bound_above
        #     / (self.upper_price - aep_upper)
        # )

        volume_at_lower = (
            self.margin_multiple_at_lower
            * balance
            / (
                self.lower_price * (1 - self.margin_multiple_at_lower)
                + self.margin_multiple_at_lower * aep_lower
            )
        )
        volume_at_upper = (
            self.margin_multiple_at_upper
            * balance
            / (
                self.upper_price * (1 + self.margin_multiple_at_upper)
                - self.margin_multiple_at_upper * aep_upper
            )
        )

        upper_L = (
            volume_at_upper
            * self.upper_price_sqrt
            * self.base_price_sqrt
            / (self.upper_price_sqrt - self.base_price_sqrt)
        )

        lower_L = (
            volume_at_lower
            * self.lower_price_sqrt
            * self.base_price_sqrt
            / (self.base_price_sqrt - self.lower_price_sqrt)
        )

        if position > 0:
            L = lower_L
            upper_bound = self.base_price_sqrt
            rt_ref_price = upper_bound / (position * upper_bound / L + 1)
        else:
            L = upper_L
            upper_bound = self.upper_price_sqrt
            rt_ref_price = upper_bound / (
                (volume_at_upper + position) * upper_bound / L + 1
            )

        print(f"At position {position} quoting around fair price {rt_ref_price ** 2}")
        return self._calculate_price_levels(
            ref_price=rt_ref_price**2,
            upper_L=upper_L,
            lower_L=lower_L,
            position=position,
        )

    def _calculate_liq_val(
        self, margin_frac: float, balance: float, risk_factor: float, liq_factor: float
    ) -> float:
        return margin_frac * (balance / risk_factor) * liq_factor

    def _calculate_price_levels(
        self,
        ref_price: float,
        upper_L: float,
        lower_L: float,
        position: float,
    ) -> Tuple[List[MMOrder], List[MMOrder]]:
        if ref_price == 0:
            ref_price = self.curr_price

        agg_bids = []
        agg_asks = []

        pos = position

        for i in range(1, self.num_levels):
            pre_price_sqrt = (ref_price + (i - 1) * self.tick_spacing) ** 0.5
            price = ref_price + i * self.tick_spacing

            if price > self.upper_price or price < self.lower_price:
                continue

            volume = self._quantity_for_move(
                pre_price_sqrt,
                price**0.5,
                self.upper_price_sqrt if pos <= 0 else self.base_price_sqrt,
                upper_L if pos <= 0 else lower_L,
            )

            if volume is not None:
                if pos > 0 and pos - volume < 0:
                    volume = pos
                agg_asks.append(MMOrder(volume, price, vega_protos.SIDE_SELL))
                pos -= volume

        pos = position
        for i in range(1, self.num_levels):
            pre_price_sqrt = (ref_price - (i - 1) * self.tick_spacing) ** 0.5
            price = ref_price - i * self.tick_spacing

            if price > self.upper_price or price < self.lower_price:
                continue

            volume = abs(
                self._quantity_for_move(
                    pre_price_sqrt,
                    price**0.5,
                    self.upper_price_sqrt if pos < 0 else self.base_price_sqrt,
                    upper_L if pos < 0 else lower_L,
                )
            )
            if volume is not None:
                if pos < 0 and pos + volume >= 0:
                    volume = abs(pos)
                agg_bids.append(MMOrder(volume, price, vega_protos.SIDE_BUY))
                pos += volume

        self.curr_bids = agg_bids
        self.curr_asks = agg_asks

        return agg_bids + agg_asks


class CFMV3LastTradeMarketMaker(ShapedMarketMaker):
    NAME_BASE = "cfm_v3_market_maker"

    def __init__(
        self,
        key_name: str,
        num_steps: int,
        initial_price: float = 100,
        price_width_below: float = 0.05,
        price_width_above: float = 0.05,
        margin_usage_at_bound_above: float = 0.8,
        margin_usage_at_bound_below: float = 0.8,
        initial_asset_mint: float = 1000000,
        market_name: str = None,
        asset_name: str = None,
        commitment_amount: float = 6000,
        supplied_amount: Optional[float] = None,
        market_decimal_places: int = 5,
        fee_amount: float = 0.001,
        volume_per_side: float = 10,
        num_levels: int = 25,
        tick_spacing: float = 1,
        asset_decimal_places: int = 0,
        tag: str = "",
        wallet_name: str = None,
        orders_from_stream: Optional[bool] = True,
        state_update_freq: Optional[int] = None,
        order_validity_length: Optional[float] = None,
        price_process_generator: Optional[Iterable[float]] = None,
        use_last_price_as_ref: bool = False,
    ):
        super().__init__(
            wallet_name=wallet_name,
            initial_asset_mint=initial_asset_mint,
            market_name=market_name,
            asset_name=asset_name,
            commitment_amount=commitment_amount,
            supplied_amount=supplied_amount,
            market_decimal_places=market_decimal_places,
            asset_decimal_places=asset_decimal_places,
            tag=tag,
            shape_fn=self._generate_shape,
            best_price_offset_fn=lambda *args, **kwargs: (0, 0),
            liquidity_commitment_fn=self._liq_provis,
            key_name=key_name,
            orders_from_stream=orders_from_stream,
            state_update_freq=state_update_freq,
            order_validity_length=order_validity_length,
            price_process_generator=price_process_generator,
        )
        self.base_price = initial_price
        self.upper_price = (1 + price_width_above) * initial_price
        self.lower_price = (1 - price_width_below) * initial_price

        self.base_price_sqrt = initial_price**0.5
        self.upper_price_sqrt = self.upper_price**0.5
        self.lower_price_sqrt = self.lower_price**0.5

        self.lower_liq_factor = 1 / (self.base_price_sqrt - self.lower_price_sqrt)
        self.upper_liq_factor = 1 / (self.upper_price_sqrt - self.base_price_sqrt)

        self.margin_usage_at_bound_above = margin_usage_at_bound_above
        self.margin_usage_at_bound_below = margin_usage_at_bound_below

        self.tick_spacing = tick_spacing
        self.num_levels = num_levels
        self.fee_amount = fee_amount
        self.volume_per_side = volume_per_side

        self.curr_bids, self.curr_asks = None, None
        self.use_last_price_as_ref = use_last_price_as_ref

    def initialise(
        self,
        vega,
        create_key: bool = True,
        mint_key: bool = True,
    ):
        super().initialise(vega=vega, create_key=create_key, mint_key=mint_key)

        risk_factors = vega.get_risk_factors(self.market_id)
        self.short_factor, self.long_factor = risk_factors.short, risk_factors.long

    def _liq_provis(self, state: VegaState) -> LiquidityProvision:
        return LiquidityProvision(
            amount=self.commitment_amount,
            fee=self.fee_amount,
        )

    def _scale_orders(
        self,
        buy_shape: List[MMOrder],
        sell_shape: List[MMOrder],
    ):
        return (buy_shape, sell_shape)

    def _quantity_for_move(
        self,
        start_price_sqrt,
        end_price_sqrt,
        range_upper_price_sqrt,
        liquidity_factor,
    ) -> Optional[float]:
        if liquidity_factor == 0:
            return None
        start_fut_pos = (
            liquidity_factor
            * (range_upper_price_sqrt - start_price_sqrt)
            / (start_price_sqrt * range_upper_price_sqrt)
        )
        end_fut_pos = (
            liquidity_factor
            * (range_upper_price_sqrt - end_price_sqrt)
            / (end_price_sqrt * range_upper_price_sqrt)
        )

        return abs(start_fut_pos - end_fut_pos)

    def _generate_shape(
        self, bid_price_depth: float, ask_price_depth: float
    ) -> Tuple[List[MMOrder], List[MMOrder]]:
        balance = sum(
            a.balance
            for a in self.vega.get_accounts_from_stream(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                market_id=self.market_id,
            )
        )

        upper_L = self._calculate_liq_val(
            self.margin_usage_at_bound_above,
            balance,
            self.short_factor,
            self.upper_liq_factor,
        )
        lower_L = self._calculate_liq_val(
            self.margin_usage_at_bound_below,
            balance,
            self.long_factor,
            self.lower_liq_factor,
        )
        if self.use_last_price_as_ref:
            ref_price = self.vega.last_trade_price(market_id=self.market_id)
        else:
            average_entry = (
                self.vega.positions_by_market(
                    wallet_name=self.wallet_name,
                    market_id=self.market_id,
                    key_name=self.key_name,
                ).average_entry_price
                if self.current_position + self.position_offset != 0
                else 0
            )
            if self.current_position > 0:
                L = lower_L
                lower_bound = self.lower_price_sqrt
                upper_bound = self.base_price
                usd_total = (
                    self.margin_usage_at_bound_below * balance / self.long_factor
                )
            else:
                L = upper_L
                lower_bound = self.base_price
                upper_bound = self.upper_price_sqrt
                usd_total = (
                    self.margin_usage_at_bound_above * balance / self.short_factor
                )
            if L == 0:
                ref_price = self.base_price
            else:
                virt_x = self.current_position + upper_bound / L
                virt_y = (
                    usd_total - self.current_position * average_entry
                ) + L * lower_bound
                ref_price = virt_y / virt_x

        return self._calculate_price_levels(
            ref_price=ref_price, balance=balance, upper_L=upper_L, lower_L=lower_L
        )

    def _calculate_liq_val(
        self, margin_frac: float, balance: float, risk_factor: float, liq_factor: float
    ) -> float:
        return margin_frac * (balance / risk_factor) * liq_factor

    def _calculate_price_levels(
        self, ref_price: float, balance: float, upper_L: float, lower_L: float
    ) -> Tuple[List[MMOrder], List[MMOrder]]:
        if ref_price == 0:
            ref_price = self.curr_price

        agg_bids = []
        agg_asks = []

        for i in range(1, self.num_levels):
            pre_price_sqrt = (ref_price + (i - 1) * self.tick_spacing) ** 0.5
            price = ref_price + i * self.tick_spacing

            if price > self.upper_price or price < self.lower_price:
                continue

            volume = self._quantity_for_move(
                pre_price_sqrt,
                price**0.5,
                self.upper_price_sqrt,
                upper_L if price > self.base_price else lower_L,
            )
            if volume is not None:
                agg_asks.append(MMOrder(volume, price))

        for i in range(1, self.num_levels):
            pre_price_sqrt = (ref_price - (i - 1) * self.tick_spacing) ** 0.5
            price = ref_price - i * self.tick_spacing

            if price > self.upper_price or price < self.lower_price:
                continue

            volume = self._quantity_for_move(
                pre_price_sqrt,
                price**0.5,
                self.upper_price_sqrt,
                upper_L if price > self.base_price else lower_L,
            )

            if volume is not None:
                agg_bids.append(MMOrder(volume, price))

        self.curr_bids = agg_bids
        self.curr_asks = agg_asks

        return agg_bids, agg_asks


# if __name__ == "__main__":
#     import matplotlib.pyplot as plt

#     buy_pri1, sell_pri1 = _build_price_levels(
#         position=0,
#         ref_price=100,
#         min_trade_unit=0.002,
#         num_steps=1,
#         tick_spacing=0.01,
#         k_scaling_small=1e6,
#         k_scaling_large=1e6,
#     )

#     print(f"Spread Bid @ {buy_pri1[0]} - Ask @ {sell_pri1[0]}")
#     bids, asks = _build_price_levels(
#         position=-1,
#         ref_price=100,
#         min_trade_unit=0.01,
#         num_steps=1000,
#         tick_spacing=0.01,
#         k_scaling_small=7e6,
#         k_scaling_large=100e6,
#     )

#     x = []
#     y = []

#     cumsum = 0
#     for bid in bids:
#         x.append(bid.price)
#         cumsum += bid.size
#         y.append(cumsum)

#     plt.plot(x, y, color="blue")
#     x = []
#     y = []

#     cumsum = 0
#     for ask in asks:
#         x.append(ask.price)
#         cumsum += ask.size
#         y.append(cumsum)
#     plt.plot(x, y, color="red")
#     plt.show()

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    mm = CFMV3MarketMaker(
        "fawfa",
        num_steps=12,
        initial_price=2000,
        price_width_above=10,
        price_width_below=0.9,
        margin_usage_at_bound_above=0.8,
        margin_usage_at_bound_below=0.8,
        initial_asset_mint=100_000,
        market_name="MKT",
        num_levels=2000,
        tick_spacing=1,
    )
    balance = 1000

    mm.short_factor = 0.02
    mm.long_factor = 0.02

    volume_at_upper = (
        mm.margin_usage_at_bound_above * (balance / mm.short_factor) / mm.upper_price
    )
    upper_L = (
        volume_at_upper
        * mm.upper_price_sqrt
        * mm.base_price_sqrt
        / (mm.upper_price_sqrt - mm.base_price_sqrt)
    )

    lower_L = (
        mm.margin_usage_at_bound_below
        * (balance / mm.long_factor)
        * mm.lower_liq_factor
    )

    to_price = 2000
    pos = mm._quantity_for_move(
        mm.base_price_sqrt,
        to_price**0.5,
        mm.base_price_sqrt if to_price < mm.base_price else mm.upper_price_sqrt,
        lower_L,
    )
    print(f"pos would be {pos}")
    bids, asks = mm._generate_shape_calcs(balance=balance, position=pos)

    # x = []
    # y = []

    # cumsum = 0
    # for bid in bids:
    #     x.append(bid.price)
    #     cumsum += bid.size
    #     y.append(cumsum)

    # plt.plot(x, y, color="blue")
    x = []
    y = []

    # cumsum = 0
    # for ask in asks:
    #     x.append(ask.price)
    #     cumsum += ask.size
    #     y.append(cumsum)
    # plt.plot(x, y, color="red")
    # plt.show()

    cumsum = 0
    for bid in bids:
        x.append(bid.price)
        cumsum += bid.size
        y.append(bid.size)

    plt.bar(x, y, color="blue")
    x = []
    y = []

    cumsum = 0
    for ask in asks:
        x.append(ask.price)
        cumsum += ask.size
        y.append(ask.size)
    plt.bar(x, y, color="red")
    plt.show()
