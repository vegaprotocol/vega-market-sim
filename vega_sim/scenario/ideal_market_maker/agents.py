import numpy as np
from collections import namedtuple
from typing import List, Optional

from vega_sim.scenario.ideal_market_maker.utils.strategy import A_S_MMmodel, GLFT_approx
from vega_sim.environment import VegaState
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import vega as vega_protos

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Set up parties in the market/ Submit liquidity provision
MM_WALLET = WalletConfig("mm", "pin")

# Send selling/buying MOs to hit LP orders
TRADER_WALLET = WalletConfig("trader", "trader")

# Randomly posts LOs at buy/sell side to simulate real Market situation
RANDOM_WALLET = WalletConfig("random", "random")

# Pass opening auction
AUCTION1_WALLET = WalletConfig("AUCTION1", "AUCTION1pass")
AUCTION2_WALLET = WalletConfig("AUCTION2", "AUCTION2pass")

# Add another liquidity provider
LIQUIDITY = WalletConfig("liquidity", "liquiditypass")

# Terminate the market and send settlment price
TERMINATE_WALLET = WalletConfig("terminate", "terminate")

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
        market_position_decimal: int = 0,
        initial_asset_mint: float = 1e8,
        market_name: str = None,
        asset_name: str = None,
        commitamount: float = 100000,
        lp_fee: float = 0.001,
        settlement_price: Optional[float] = None,
        tag: str = "",
        random_state: Optional[np.random.RandomState] = None,
    ):
        super().__init__(wallet_name + tag, wallet_pass)
        self.terminate_wallet_name = terminate_wallet_name + tag
        self.terminate_wallet_pass = terminate_wallet_pass

        self.price_process = price_process
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
        self.market_position_decimal = market_position_decimal
        self.current_step = 0
        self.initial_asset_mint = initial_asset_mint
        self.commitamount = commitamount
        self.lp_fee = lp_fee
        self.settlement_price = (
            self.price_process[-1] if settlement_price is None else settlement_price
        )
        self.tag = tag
        self.market_name = f"ETH:USD_{self.tag}" if market_name is None else market_name
        self.asset_name = f"tDAI_{self.tag}" if asset_name is None else asset_name
        self.random_state = (
            random_state
            if random_state is not None
            else np.random.RandomState(seed=123)
        )

        self.long_horizon_estimate = num_steps >= 200

        if not self.long_horizon_estimate:
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
        self.current_step += 1
        self.vega.settle_market(
            self.terminate_wallet_name, self.settlement_price, self.market_id
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

        # Create asset
        self.vega.create_asset(
            self.wallet_name,
            name=self.asset_name,
            symbol=self.asset_name,
            decimals=self.adp,
            max_faucet_amount=1e20,
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
        self.vega.wait_for_total_catchup()

        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        vega.submit_liquidity(
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            commitment_amount=self.commitamount,
            fee=self.lp_fee,
            buy_specs=[("PEGGED_REFERENCE_MID", 0.1, 1)],
            sell_specs=[("PEGGED_REFERENCE_MID", 0.1, 1)],
            is_amendment=False,
        )
        self.bid_depth, self.ask_depth = self.OptimalStrategy(0)

    def num_MarketOrders(self):
        num_buyMO = self.random_state.poisson(self.Lambda)
        num_sellMO = self.random_state.poisson(self.Lambda)
        return num_buyMO, num_sellMO

    def num_LimitOrderHit(self, bid_depth, ask_depth, num_buyMO, num_sellMO):
        poss_bid_filled = np.exp(-self.kappa * bid_depth)
        poss_ask_filled = np.exp(-self.kappa * ask_depth)

        num_BidLimitOrderHit = num_sellMO - self.random_state.binomial(
            num_sellMO, poss_bid_filled
        )
        num_AskLimitOrderHit = num_buyMO - self.random_state.binomial(
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
            current_bid_depth = (
                self.optimal_bid[self.current_step, 0]
                if not self.long_horizon_estimate
                else self.optimal_bid[0]
            )
            current_ask_depth = 1 / 10**self.mdp
        elif current_position <= self.q_lower:
            current_bid_depth = 1 / 10**self.mdp
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

    def AvoidCrossedOrder(self):
        new_price = self.price_process[self.current_step]
        price = (
            self.price_process[self.current_step - 1]
            if self.current_step > 0
            else self.price_process[self.current_step]
        )

        if min(self.bid_depth, self.ask_depth) > np.abs(new_price - price) / 2:
            pass

        else:
            temp_depth = round(
                np.abs(new_price - price) / 2 + 5 * self.spread,
                self.mdp,
            )
            self.vega.submit_simple_liquidity(
                wallet_name=self.wallet_name,
                market_id=self.market_id,
                commitment_amount=self.commitamount,
                fee=self.lp_fee,
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

        current_position = int(position[0].open_volume) if position else 0
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
            commitment_amount=self.commitamount,
            fee=self.lp_fee,
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
        market_name: str = None,
        asset_name: str = None,
        initial_asset_mint: float = 1e8,
        num_buy_market_order: int = None,
        num_sell_market_order: int = None,
        tag: str = "",
    ):
        super().__init__(wallet_name + str(tag), wallet_pass)
        self.initial_asset_mint = initial_asset_mint
        self.num_buyMO = num_buy_market_order
        self.num_sellMO = num_sell_market_order
        self.tag = tag
        self.market_name = f"ETH:USD_{self.tag}" if market_name is None else market_name
        self.asset_name = f"tDAI_{self.tag}" if asset_name is None else asset_name

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet
        super().initialise(vega=vega)

        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        # Get asset id
        tDAI_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=tDAI_id,
            amount=self.initial_asset_mint,
        )
        self.vega.wait_fn(2)

    def step_buy(self, vega_state: VegaState):
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
        initial_asset_mint: float = 1e8,
        market_name: str = None,
        asset_name: str = None,
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
        self.initial_asset_mint = initial_asset_mint
        self.current_step = 0
        self.tag = tag
        self.market_name = f"ETH:USD_{self.tag}" if market_name is None else market_name
        self.asset_name = f"tDAI_{self.tag}" if asset_name is None else asset_name

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet
        super().initialise(vega=vega)
        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        # Get asset id
        tDAI_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=tDAI_id,
            amount=self.initial_asset_mint,
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
        new_price = self.price_process[self.current_step]
        price = (
            self.price_process[self.current_step - 1]
            if self.current_step > 0
            else self.price_process[self.current_step]
        )

        first_side = (
            vega_protos.SIDE_BUY if new_price < price else vega_protos.SIDE_SELL
        )

        if first_side == vega_protos.SIDE_BUY:
            self.vega.amend_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                order_id=self.buy_order_id,
                price=round(
                    new_price - self.spread / 2,
                    self.mdp,
                ),
            )

        self.vega.amend_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_id=self.sell_order_id,
            price=round(
                new_price + self.spread / 2,
                self.mdp,
            ),
        )

        if first_side == vega_protos.SIDE_SELL:
            self.vega.amend_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                order_id=self.buy_order_id,
                price=round(
                    new_price - self.spread / 2,
                    self.mdp,
                ),
            )

    def step_limitorders(self, vega_state: VegaState):
        if self.num_post_at_bid > 1:
            random_delta = self.spread / 2

            self.vega.submit_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                time_in_force="TIME_IN_FORCE_GTC",
                order_type="TYPE_LIMIT",
                side="SIDE_BUY",
                volume=self.num_post_at_bid - 1,
                price=self.price_process[self.current_step] - random_delta,
                wait=False,
            )

        if self.num_post_at_ask > 1:
            random_delta = self.spread / 2

            self.vega.submit_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                time_in_force="TIME_IN_FORCE_GTC",
                order_type="TYPE_LIMIT",
                side="SIDE_SELL",
                volume=self.num_post_at_ask - 1,
                price=self.price_process[self.current_step] + random_delta,
                wait=False,
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
        market_name: str = None,
        asset_name: str = None,
        initial_asset_mint: float = 1e8,
        initial_price: float = 0.3,
        tag: str = "",
    ):
        super().__init__(wallet_name + tag, wallet_pass)
        self.side = side
        self.initial_price = initial_price
        self.initial_asset_mint = initial_asset_mint
        self.tag = tag
        self.market_name = f"ETH:USD_{self.tag}" if market_name is None else market_name
        self.asset_name = f"tDAI_{self.tag}" if asset_name is None else asset_name

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet
        super().initialise(vega=vega)
        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        # Get asset id
        tDAI_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=tDAI_id,
            amount=self.initial_asset_mint,
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


class OptimalLiquidityProvider(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        num_steps: int = 100,
        market_order_arrival_rate: float = 10,
        pegged_order_fill_rate: float = 500,
        inventory_upper_boundary: int = 20,
        inventory_lower_boundary: int = -20,
        terminal_penalty_parameter: float = 10**-4,
        running_penalty_parameter: float = 5 * 10**-6,
        initial_asset_mint: float = 1e8,
        market_name: str = None,
        asset_name: str = None,
        entry_step: int = 0,
        commitamount: float = 100000,
        lp_fee: float = 0.001,
        tag: str = "",
    ):
        super().__init__(wallet_name + tag, wallet_pass)
        self.current_step = 0
        self.initial_asset_mint = initial_asset_mint
        self.entry_step = entry_step
        self.commitamount = commitamount
        self.lp_fee = lp_fee
        self.time = num_steps
        self.Lambda = market_order_arrival_rate
        self.kappa = pegged_order_fill_rate
        self.q_upper = inventory_upper_boundary
        self.q_lower = inventory_lower_boundary
        self.alpha = terminal_penalty_parameter
        self.phi = running_penalty_parameter
        self.tag = tag
        self.market_name = f"ETH:USD_{self.tag}" if market_name is None else market_name
        self.asset_name = f"tDAI_{self.tag}" if asset_name is None else asset_name
        self.long_horizon_estimate = num_steps >= 200

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet for LP/ Settle Party
        super().initialise(vega=vega)

        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        # Get asset id
        tDAI_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=tDAI_id,
            amount=self.initial_asset_mint,
        )
        # Get asset id
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=self.asset_id,
            amount=self.initial_asset_mint,
        )
        self.vega.wait_for_total_catchup()

        # Get market decimal place/asset decimal place
        self.mdp = list(self.vega._market_price_decimals.values())[0]
        self.adp = list(self.vega._asset_decimals.values())[0]

        # Get optimal market making strategy
        if not self.long_horizon_estimate:
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
        else:
            self.optimal_bid, self.optimal_ask = GLFT_approx(
                q_upper=self.q_upper,
                q_lower=self.q_lower,
                kappa=self.kappa,
                Lambda=self.Lambda,
                alpha=self.alpha,
                phi=self.phi,
            )

    def OptimalStrategy(self, current_position):
        if current_position >= self.q_upper:
            current_bid_depth = (
                self.optimal_bid[self.current_step, 0]
                if not self.long_horizon_estimate
                else self.optimal_bid[0]
            )
            current_ask_depth = 1 / 10**self.mdp
        elif current_position <= self.q_lower:
            current_bid_depth = 1 / 10**self.mdp
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
        if self.current_step < self.entry_step:
            self.current_step += 1
            return

        elif self.current_step == self.entry_step:
            current_position = 0
            self.bid_depth, self.ask_depth = self.OptimalStrategy(current_position)
            self.vega.submit_simple_liquidity(
                wallet_name=self.wallet_name,
                market_id=self.market_id,
                commitment_amount=self.commitamount,
                fee=self.lp_fee,
                reference_buy="PEGGED_REFERENCE_MID",
                reference_sell="PEGGED_REFERENCE_MID",
                delta_buy=self.bid_depth,
                delta_sell=self.ask_depth,
                is_amendment=False,
            )
            self.current_step += 1
            return

        position = self.vega.positions_by_market(
            wallet_name=self.wallet_name, market_id=self.market_id
        )

        current_position = int(position[0].open_volume) if position else 0
        self.bid_depth, self.ask_depth = self.OptimalStrategy(current_position)

        self.vega.submit_simple_liquidity(
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            commitment_amount=self.commitamount,
            fee=self.lp_fee,
            reference_buy="PEGGED_REFERENCE_MID",
            reference_sell="PEGGED_REFERENCE_MID",
            delta_buy=self.bid_depth,
            delta_sell=self.ask_depth,
            is_amendment=True,
        )

        self.current_step += 1


class InformedTrader(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        price_process: List[float],
        market_name: str = None,
        asset_name: str = None,
        initial_asset_mint: float = 1e8,
        proportion_taken: float = 0.8,
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
        self.market_id = self.vega.find_market_id(name=self.market_name)

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
