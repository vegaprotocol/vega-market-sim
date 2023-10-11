from typing import Iterable, List, Optional, Tuple, Union

import numpy as np

from vega_sim.proto.vega import vega as vega_protos
from vega_sim.scenario.common.agents import (
    LiquidityProvision,
    MMOrder,
    ShapedMarketMaker,
    VegaState,
)


class CFMMarketMaker(ShapedMarketMaker):
    NAME_BASE = "cfm_market_maker"

    def __init__(
        self,
        key_name: str,
        num_steps: int,
        price_process_generator: Iterable[float],
        initial_asset_mint: float = 1000000,
        market_name: str = None,
        asset_name: str = None,
        commitment_amount: float = 6000,
        supplied_amount: Optional[float] = None,
        market_decimal_places: int = 5,
        fee_amount: float = 0.001,
        k_scaling: float = 1,
        num_levels: int = 25,
        tick_spacing: float = 1,
        asset_decimal_places: int = 0,
        tag: str = "",
        wallet_name: str = None,
        orders_from_stream: Optional[bool] = True,
        state_update_freq: Optional[int] = None,
        order_validity_length: Optional[float] = None,
    ):
        super().__init__(
            wallet_name=wallet_name,
            price_process_generator=price_process_generator,
            initial_asset_mint=initial_asset_mint,
            market_name=market_name,
            asset_name=asset_name,
            commitment_amount=commitment_amount,
            supplied_amount=supplied_amount,
            market_decimal_places=market_decimal_places,
            asset_decimal_places=asset_decimal_places,
            tag=tag,
            shape_fn=self._generate_shape,
            best_price_offset_fn=self._optimal_strategy,
            liquidity_commitment_fn=self._liq_provis,
            key_name=key_name,
            orders_from_stream=orders_from_stream,
            state_update_freq=state_update_freq,
            order_validity_length=order_validity_length,
        )
        self.k_scaling = k_scaling
        self.tick_spacing = tick_spacing
        self.num_levels = num_levels
        self.fee_amount = fee_amount

        self.num_steps = num_steps

        self.curr_bids, self.curr_asks = None, None

    def _liq_provis(self, state: VegaState) -> LiquidityProvision:
        return LiquidityProvision(
            amount=self.commitment_amount,
            fee=self.fee_amount,
        )

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
        cumulative_vol = np.exp(self.k_scaling * levels)
        level_vol = (1 / cumulative_vol[0]) * cumulative_vol

        base_price = self.curr_price + mult_factor * price_depth
        level_price = np.arange(
            base_price,
            base_price + mult_factor * self.num_levels * self.tick_spacing,
            mult_factor * self.tick_spacing,
        )
        level_price[level_price < 1 / 10**self.mdp] = 1 / 10**self.mdp

        return [MMOrder(vol, price) for vol, price in zip(level_vol, level_price)]
