from typing import Iterable, List, Optional, Tuple, Union

import numpy as np

from vega_sim.proto.vega import vega as vega_protos
from vega_sim.scenario.common.agents import (
    LiquidityProvision,
    MMOrder,
    ShapedMarketMaker,
    VegaState,
)


def _price_for_size(
    side: vega_protos.Side,
    position: float,
    ref_price: float,
    k_scaling_large: float,
    k_scaling_small: float,
    trade_size: float,
    # pool_size: float,
) -> float:
    # sell_pool = pool_size / (last_trade + 1)
    # buy_pool = pool_size - sell_pool
    # mid = buy_pool / sell_pool

    if side == vega_protos.Side.SIDE_SELL:
        k_scaling = k_scaling_large if position >= 0 else k_scaling_small

        virtual_sell = (k_scaling / ref_price) ** 0.5
        virtual_buy = (k_scaling * ref_price) ** 0.5

        return (virtual_buy + trade_size * ref_price) / virtual_sell
    elif side == vega_protos.Side.SIDE_BUY:
        k_scaling = k_scaling_large if position <= 0 else k_scaling_small

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


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    buy_pri1, sell_pri1 = _build_price_levels(
        position=0,
        ref_price=100,
        min_trade_unit=0.002,
        num_steps=1,
        tick_spacing=0.01,
        k_scaling_small=1e6,
        k_scaling_large=1e6,
    )

    print(f"Spread Bid @ {buy_pri1[0]} - Ask @ {sell_pri1[0]}")
    bids, asks = _build_price_levels(
        position=-1,
        ref_price=100,
        min_trade_unit=0.01,
        num_steps=1000,
        tick_spacing=0.01,
        k_scaling_small=7e6,
        k_scaling_large=100e6,
    )

    x = []
    y = []

    cumsum = 0
    for bid in bids:
        x.append(bid.price)
        cumsum += bid.size
        y.append(cumsum)

    plt.plot(x, y, color="blue")
    x = []
    y = []

    cumsum = 0
    for ask in asks:
        x.append(ask.price)
        cumsum += ask.size
        y.append(cumsum)
    plt.plot(x, y, color="red")
    plt.show()
