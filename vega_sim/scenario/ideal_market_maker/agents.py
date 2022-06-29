import numpy as np
import os
from collections import namedtuple
from typing import List

from vega_sim.scenario.ideal_market_maker.utils.strategy import (
    A_S_MMmodel,
)
from vega_sim.scenario.ideal_market_maker.utils.log_data import (
    log_simple_MMmodel,
)
from vega_sim.environment import VegaState
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import markets as markets_protos

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Set up parties in the market/ Submit liquidity provision
MM_WALLET = WalletConfig("mm", "pin")

# Send selling/buying MOs to hit LP orders
TRADER_WALLET = WalletConfig("Zl3pLs6Xk6SwIK7Jlp2x", "bJQDDVGAhKkj3PVCc7Rr")

# Randomly posts LOs at buy/sell side to simulate real Market situation
RANDOM_WALLET = WalletConfig("random", "random")

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
        pegged_order_fill_rate: float = 500,
        inventory_upper_boundary: int = 20,
        inventory_lower_boundary: int = -20,
        terminal_penalty_parameter: float = 10**-4,
        running_penalty_parameter: float = 5 * 10**-6,
        asset_decimal: int = 5,
        market_decimal: int = 5,
        tag: str = "",
    ):
        super().__init__(wallet_name + tag, wallet_pass)
        self.terminate_wallet_name = terminate_wallet_name + tag
        self.terminate_wallet_pass = terminate_wallet_pass

        self.price_process = price_processs
        self.spread = spread
        self.time = num_steps
        self.Lambda = market_order_arrival_rate
        self.kappa = pegged_order_fill_rate
        self.q_upper = inventory_upper_boundary
        self.q_lower = inventory_lower_boundary
        self.alpha = terminal_penalty_parameter
        self.phi = running_penalty_parameter
        self.adp = asset_decimal
        self.mdp = market_decimal
        self.current_step = 0

        self.tag = tag

        self.optimal_bid, self.optimal_ask, _ = A_S_MMmodel(
            T=self.time / 60 / 24 / 365.25,
            dt=1 / 60 / 24 / 365.25,
            length=self.time + 1,
            mdp=self.mdp,
            q_upper=self.q_upper,
            q_lower=self.q_lower,
            kappa=self.kappa,
            Lambda=self.Lambda,
            alpha=self.alpha,
            phi=self.phi,
        )

        # self.optimal_bid, self.optimal_ask = GLFT_approx(
        #     q_upper=self.q_upper,
        #     q_lower=self.q_lower,
        #     kappa=self.kappa,
        #     Lambda=self.Lambda,
        #     alpha=self.alpha,
        #     phi=self.phi,
        # )

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
        self.vega.wait_fn(5)
        self.vega.wait_for_datanode_sync()

        market_name = f"BTC:DAI_{self.tag}"
        # Set up a future market
        self.vega.create_simple_market(
            market_name=market_name,
            proposal_wallet=self.wallet_name,
            settlement_asset_id=self.tdai_id,
            termination_wallet=self.terminate_wallet_name,
            market_decimals=self.mdp,
            future_asset=ccy_name,
            liquidity_commitment=vega.build_new_market_liquidity_commitment(
                asset_id=self.tdai_id,
                commitment_amount=5000,
                fee=0.001,
                buy_specs=[("PEGGED_REFERENCE_MID", 10, 1)],
                sell_specs=[("PEGGED_REFERENCE_MID", 10, 1)],
                market_decimals=5,
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

    def num_MarketOrders(self):
        num_buyMO = np.random.poisson(self.Lambda)
        num_sellMO = np.random.poisson(self.Lambda)
        return num_buyMO, num_sellMO

    def num_LimitOrderHit(self, bid_depth, ask_depth, num_buyMO, num_sellMO):
        poss_bid_filled = np.exp(-self.kappa * bid_depth)
        poss_ask_filled = np.exp(-self.kappa * ask_depth)

        num_BidLimitOrderHit = num_sellMO - np.random.binomial(
            num_sellMO, poss_bid_filled
        )
        num_AskLimitOrderHit = num_buyMO - np.random.binomial(
            num_buyMO, poss_ask_filled
        )

        # If the numebr of LOs at ask side is 0
        if num_AskLimitOrderHit == 0:
            # In this case, the MOs still cannot hit the LP orders
            num_AskLimitOrderHit += 1
            num_buyMO += 1
        if num_BidLimitOrderHit == 0:
            num_BidLimitOrderHit += 1
            num_sellMO += 1

        return num_BidLimitOrderHit, num_AskLimitOrderHit

    def OptimalStrategy(self, current_position):

        if current_position >= self.q_upper:
            current_bid_depth = self.optimal_bid[self.current_step, 0]
            current_ask_depth = 1 / 10**self.mdp
        elif current_position <= self.q_lower:
            current_bid_depth = 1 / 10**self.mdp
            current_ask_depth = self.optimal_ask[self.current_step, -1]
        else:
            current_bid_depth = self.optimal_bid[
                self.current_step, int(self.q_upper - 1 - current_position)
            ]
            current_ask_depth = self.optimal_ask[
                self.current_step, int(self.q_upper - current_position)
            ]

        return current_bid_depth, current_ask_depth

    def AvoidCrossedOrder(self):
        if self.current_step == 0:
            pass
        else:
            if (
                min(self.bid_depth, self.ask_depth)
                > np.abs(
                    self.price_process[self.current_step]
                    - self.price_process[self.current_step - 1]
                )
                / 2
            ):
                pass

            else:
                temp_depth = round(
                    np.abs(
                        self.price_process[self.current_step]
                        - self.price_process[self.current_step - 1]
                    )
                    / 2
                    + 5 * self.spread,
                    self.mdp,
                )
                self.vega.submit_simple_liquidity(
                    wallet_name=self.wallet_name,
                    market_id=self.market_id,
                    commitment_amount=100,
                    fee=0.002,
                    reference_buy="PEGGED_REFERENCE_MID",
                    reference_sell="PEGGED_REFERENCE_MID",
                    delta_buy=temp_depth,
                    delta_sell=temp_depth,
                    is_amendment=True,
                )

    def step(self, vega_state: VegaState):
        # Each step, MM posts optimal bid/ask depths
        position = self.vega.positions_by_market(
            wallet_name=self.wallet_name, market_id=self.market_id
        )

        if not position:
            current_position = 0
        else:
            current_position = int(position[0].open_volume)
        self.bid_depth, self.ask_depth = self.OptimalStrategy(current_position)

        self.num_buyMO, self.num_sellMO = self.num_MarketOrders()
        self.num_bidhit, self.num_askhit = self.num_LimitOrderHit(
            bid_depth=self.bid_depth,
            ask_depth=self.ask_depth,
            num_buyMO=self.num_buyMO,
            num_sellMO=self.num_sellMO,
        )

        self.vega.submit_simple_liquidity(
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            commitment_amount=100,
            fee=0.002,
            reference_buy="PEGGED_REFERENCE_MID",
            reference_sell="PEGGED_REFERENCE_MID",
            delta_buy=self.bid_depth,
            delta_sell=self.ask_depth,
            is_amendment=True,
        )
        self.current_step += 1


class MarketOrderTrader(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        num_buy_market_order: int = None,
        num_sell_market_order: int = None,
        tag: str = "",
    ):
        super().__init__(wallet_name + tag, wallet_pass)
        self.num_buyMO = num_buy_market_order
        self.num_sellMO = num_sell_market_order
        self.tag = tag

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet
        super().initialise(vega=vega)
        market_name = f"BTC:DAI_{self.tag}"
        # Get market id
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

    def step_buy(self, vega_state: VegaState):
        if (
            vega_state.market_state[self.market_id].trading_mode
            == markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS
        ) and vega_state.market_state[
            self.market_id
        ].state == markets_protos.Market.State.STATE_ACTIVE:
            if self.num_buyMO > 0:
                self.vega.submit_market_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    side="SIDE_BUY",
                    volume=self.num_buyMO,
                    wait=False,
                    fill_or_kill=False,
                )

    def step_sell(self, vega_state: VegaState):
        if (
            vega_state.market_state[self.market_id].trading_mode
            == markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS
        ) and vega_state.market_state[
            self.market_id
        ].state == markets_protos.Market.State.STATE_ACTIVE:
            if self.num_sellMO > 0:
                self.vega.submit_market_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    side="SIDE_SELL",
                    volume=self.num_sellMO,
                    wait=False,
                    fill_or_kill=False,
                )


class LimitOrderTrader(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        price_process: List[float],
        num_post_at_bid: int = None,
        num_post_at_ask: int = None,
        spread: float = 0.00002,
        initial_price: float = 0.3,
        market_decimal: int = 5,
        asset_decimal: int = 5,
        tag: str = "",
    ):
        super().__init__(wallet_name + tag, wallet_pass)
        self.num_post_at_bid = num_post_at_bid
        self.num_post_at_ask = num_post_at_ask
        self.price_process = price_process
        self.spread = spread
        self.initial_price = initial_price
        self.mdp = market_decimal
        self.adp = asset_decimal
        self.current_step = 0
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

        self.buy_order_id = self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY",
            volume=1,
            price=round(self.initial_price - self.spread, self.mdp),
            wait=True,
        )

        self.sell_order_id = self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_SELL",
            volume=1,
            price=round(self.initial_price + self.spread, self.mdp),
            wait=True,
        )

    def step_amendprice(self, vega_state: VegaState):
        if self.current_step == 0:
            pass
        else:
            if (
                self.price_process[self.current_step]
                > self.price_process[self.current_step - 1]
            ):
                self.vega.amend_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    order_id=self.sell_order_id,
                    price=round(
                        self.price_process[self.current_step] + self.spread, self.mdp
                    ),
                )
                self.vega.amend_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    order_id=self.buy_order_id,
                    price=round(
                        self.price_process[self.current_step] - self.spread, self.mdp
                    ),
                )
            else:
                self.vega.amend_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    order_id=self.buy_order_id,
                    price=round(
                        self.price_process[self.current_step] - self.spread, self.mdp
                    ),
                )
                self.vega.amend_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    order_id=self.sell_order_id,
                    price=round(
                        self.price_process[self.current_step] + self.spread, self.mdp
                    ),
                )

    def step_limitorders(self, vega_state: VegaState):
        for _ in range(self.num_post_at_bid - 1):
            random_delta = (
                np.random.randint(
                    int(self.spread * 10**self.mdp),
                    int(30 * self.spread * 10**self.mdp),
                )
                / 10**self.mdp
            )

            self.vega.submit_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                time_in_force="TIME_IN_FORCE_GTC",
                order_type="TYPE_LIMIT",
                side="SIDE_BUY",
                volume=1,
                price=self.price_process[self.current_step] - random_delta,
            )

        for _ in range(self.num_post_at_ask - 1):
            random_delta = (
                np.random.randint(
                    int(self.spread * 10**self.mdp),
                    int(30 * self.spread * 10**self.mdp),
                )
                / 10**self.mdp
            )

            self.vega.submit_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                time_in_force="TIME_IN_FORCE_GTC",
                order_type="TYPE_LIMIT",
                side="SIDE_SELL",
                volume=1,
                price=self.price_process[self.current_step] + random_delta,
            )

    def step_limitorderask(self, vega_state: VegaState):
        self.sell_order_id = self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_SELL",
            volume=1,
            price=round(self.price_process[self.current_step] + self.spread, self.mdp),
            wait=True,
        )

    def step_limitorderbid(self, vega_state: VegaState):
        self.buy_order_id = self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY",
            volume=1,
            price=round(self.price_process[self.current_step] - self.spread, self.mdp),
            wait=True,
        )

        self.current_step += 1


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
