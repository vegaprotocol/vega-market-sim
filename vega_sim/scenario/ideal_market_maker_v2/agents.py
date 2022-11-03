from __future__ import annotations

import numpy as np
from collections import namedtuple
from typing import List, Optional, Union
from numpy.typing import ArrayLike
from vega_sim.api.data import Order
from vega_sim.scenario.common.agents import MomentumTrader

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

MOMENTUM_WALLET = WalletConfig("momentum", "momentum")

# Pass opening auction
AUCTION1_WALLET = WalletConfig("AUCTION1", "AUCTION1pass")
AUCTION2_WALLET = WalletConfig("AUCTION2", "AUCTION2pass")

# Terminate the market and send settlment price
TERMINATE_WALLET = WalletConfig("FJMKnwfZdd48C8NqvYrG", "bY3DxwtsCstMIIZdNpKs")

# informed trader wallet
INFORMED_WALLET = WalletConfig("INFORMED", "INFORMEDpass")


class OptimalMarketMaker(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        terminate_wallet_name: str,
        terminate_wallet_pass: str,
        price_process: List[float],
        initial_asset_mint: float = 1000000,
        spread: float = 0.002,
        num_steps: int = 180,
        limit_order_size: float = 10,
        market_order_arrival_rate: float = 5,
        kappa: float = 500,
        inventory_upper_boundary: int = 20,
        inventory_lower_boundary: int = -20,
        terminal_penalty_parameter: float = 10**-4,
        running_penalty_parameter: float = 5 * 10**-6,
        asset_decimal: int = 5,
        market_decimal: int = 5,
        market_position_decimal: int = 2,
        market_name: str = None,
        asset_name: str = None,
        set_up_market: bool = True,
        commitment_amount: float = 6000,
        settlement_price: Optional[float] = None,
        tag: str = "",
    ):
        super().__init__(wallet_name + str(tag), wallet_pass)
        self.terminate_wallet_name = terminate_wallet_name + str(tag)
        self.terminate_wallet_pass = terminate_wallet_pass

        self.price_process = price_process
        self.spread = spread
        self.time = num_steps
        self.Lambda = market_order_arrival_rate
        self.kappa = kappa
        self.limit_order_size = limit_order_size
        self.q_upper = inventory_upper_boundary
        self.q_lower = inventory_lower_boundary
        self.alpha = terminal_penalty_parameter
        self.phi = running_penalty_parameter
        self.adp = asset_decimal
        self.mdp = market_decimal
        self.market_position_decimal = market_position_decimal
        self.commitment_amount = commitment_amount
        self.settlement_price = settlement_price
        self.initial_asset_mint = initial_asset_mint

        self.current_step = 0

        self.tag = tag
        self.set_up_market = set_up_market

        self.market_name = f"ETH:USD_{self.tag}" if market_name is None else market_name
        self.asset_name = f"tDAI{self.tag}" if asset_name is None else asset_name

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
        if self.settlement_price:
            self.vega.settle_market(
                self.terminate_wallet_name, self.settlement_price, self.market_id
            )
            self.current_step += 1

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet for LP/ Settle Party
        super().initialise(vega=vega)
        self.vega.create_wallet(self.terminate_wallet_name, self.terminate_wallet_pass)

        # Faucet vega tokens
        self.vega.wait_fn(10)
        self.vega.wait_for_total_catchup()
        self.vega.mint(
            self.wallet_name,
            asset="VOTE",
            amount=1e4,
        )
        self.vega.wait_fn(10)
        self.vega.wait_for_total_catchup()
        if self.set_up_market:
            # Create asset
            self.vega.create_asset(
                self.wallet_name,
                name=self.asset_name,
                symbol=self.asset_name,
                decimals=self.adp,
            )
            self.vega.wait_fn(5)
            self.vega.wait_for_total_catchup()
        # Get asset id
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=self.asset_id,
            amount=self.initial_asset_mint,
        )
        self.vega.wait_fn(10)
        self.vega.wait_for_total_catchup()

        if self.set_up_market:
            self.vega.update_network_parameter(
                self.wallet_name,
                "market.liquidity.minimum.probabilityOfTrading.lpOrders",
                "1e-6",
            )

            self.vega.wait_for_total_catchup()
            self.vega.update_network_parameter(
                self.wallet_name,
                "market.liquidity.stakeToCcySiskas",
                "0.001",
            )

            self.vega.wait_for_datanode_sync()

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
            self.vega.wait_for_total_catchup()

        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        vega.submit_liquidity(
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            commitment_amount=self.commitment_amount,
            fee=0.0015,
            buy_specs=[("PEGGED_REFERENCE_BEST_BID", 5, 1)],
            sell_specs=[("PEGGED_REFERENCE_BEST_ASK", 5, 1)],
            is_amendment=False,
        )

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
        self.current_step += 1

        # Each step, MM posts optimal bid/ask depths
        position = self.vega.positions_by_market(
            wallet_name=self.wallet_name, market_id=self.market_id
        )

        current_position = int(position[0].open_volume) if position else 0
        self.bid_depth, self.ask_depth = self.optimal_strategy(current_position)

        buy_order, sell_order = None, None

        for order in (
            vega_state.market_state.get(self.market_id, {})
            .orders.get(self.vega.wallet.public_key(self.wallet_name), {})
            .values()
        ):
            if order.side == vega_protos.SIDE_BUY:
                buy_order = order
            else:
                sell_order = order

        self._place_orders(
            buy_offset=self.bid_depth - self.spread / 2,
            sell_offset=self.ask_depth - self.spread / 2,
            volume=self.limit_order_size,
            buy_order=buy_order,
            sell_order=sell_order,
        )

    def _place_orders(
        self,
        buy_offset: float,
        sell_offset: float,
        volume: float,
        buy_order: Optional[str] = None,
        sell_order: Optional[str] = None,
    ):
        self._place_or_amend_order(
            offset=buy_offset,
            volume=volume,
            order=buy_order,
            side=vega_protos.SIDE_BUY,
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
        is_buy = side in ["SIDE_BUY", vega_protos.SIDE_BUY]
        reference = (
            vega_protos.PEGGED_REFERENCE_BEST_BID
            if is_buy
            else vega_protos.PEGGED_REFERENCE_BEST_ASK
        )

        if order is None:
            self.vega.submit_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                pegged_order=PeggedOrder(reference=reference, offset=offset),
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
                pegged_reference=reference,
                pegged_offset=offset,
                volume_delta=volume - order.size,
            )
