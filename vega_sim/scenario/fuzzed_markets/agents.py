import copy
import os
from typing import Optional, Dict, List

import pandas as pd
from numpy.random import RandomState

import vega_sim.proto.vega as vega_protos
from vega_sim.api.market import MarketConfig, Successor
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import markets as markets_protos
from vega_sim.service import VegaService


class FuzzingAgent(StateAgentWithWallet):
    NAME_BASE = "fuzzing_agent"

    # Set the memory which all instances can modify
    MEMORY = {
        key: []
        for key in (
            "TRADING_MODE",
            "COMMAND",
            "TYPE",
            "SIDE",
            "TIME_IN_FORCE",
            "PEGGED_REFERENCE",
            "POST_ONLY",
            "REDUCE_ONLY",
        )
    }
    # Set the output flag which all instances can modify
    OUTPUTTED = False

    def __init__(
        self,
        key_name: str,
        market_name: str,
        asset_name: str,
        tag: Optional[str] = None,
        wallet_name: Optional[str] = None,
        state_update_freq: Optional[int] = None,
        initial_asset_mint: float = 1e9,
        random_state: Optional[RandomState] = None,
        output_plot_on_finalise: bool = False,
    ):
        super().__init__(
            key_name=key_name,
            tag=tag,
            wallet_name=wallet_name,
            state_update_freq=state_update_freq,
        )

        self.market_name = market_name
        self.asset_name = asset_name
        self.initial_asset_mint = initial_asset_mint
        self.random_state = random_state if random_state is not None else RandomState()
        self.output_plot_on_finalise = output_plot_on_finalise

    def initialise(
        self, vega: VegaServiceNull, create_key: bool = True, mint_key: bool = True
    ):
        super().initialise(vega, create_key)

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

    def step(self, vega_state):
        self.live_orders = self.vega.orders_for_party_from_feed(
            key_name=self.key_name,
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            live_only=True,
        )

        self.curr_price = vega_state.market_state[self.market_id].midprice

        submissions = [self.create_fuzzed_submission(vega_state) for _ in range(20)]
        amendments = [self.create_fuzzed_amendment(vega_state) for _ in range(10)]
        cancellations = [self.create_fuzzed_cancellation(vega_state) for _ in range(1)]

        self.vega.submit_instructions(
            key_name=self.key_name,
            wallet_name=self.wallet_name,
            submissions=submissions,
            amendments=amendments,
            cancellations=cancellations,
        )

    def create_fuzzed_cancellation(self, vega_state):
        order_id = self._select_order_id()

        return self.vega.create_order_cancellation(
            order_id=order_id,
            market_id=self.market_id,
        )

    def create_fuzzed_amendment(self, vega_state):
        order_id = self._select_order_id()

        return self.vega.create_order_amendment(
            order_id=order_id,
            market_id=self.market_id,
            size_delta=self.random_state.normal(loc=0, scale=5),
            time_in_force=self.random_state.choice(
                a=[
                    "TIME_IN_FORCE_UNSPECIFIED",
                    "TIME_IN_FORCE_GTC",
                    "TIME_IN_FORCE_GTT",
                    "TIME_IN_FORCE_GFN",
                    "TIME_IN_FORCE_GFA",
                    "TIME_IN_FORCE_FOK",
                    "TIME_IN_FORCE_IOC",
                ]
            ),
            price=self.random_state.choice(
                a=[None, self.random_state.normal(loc=self.curr_price, scale=20)]
            ),
            expires_at=int(
                self.vega.get_blockchain_time()
                + self.random_state.normal(loc=60, scale=60) * 1e9
            ),
            pegged_reference=self.random_state.choice(
                a=[
                    "PEGGED_REFERENCE_UNSPECIFIED",
                    "PEGGED_REFERENCE_MID",
                    "PEGGED_REFERENCE_BEST_BID",
                    "PEGGED_REFERENCE_BEST_ASK",
                ],
                p=[0.5, 0.5 / 3, 0.5 / 3, 0.5 / 3],
            ),
            pegged_offset=self.random_state.normal(loc=0, scale=10),
        )

    def create_fuzzed_submission(self, vega_state):
        FuzzingAgent.MEMORY["TRADING_MODE"].append(
            markets_protos.Market.TradingMode.Name(
                vega_state.market_state[self.market_id].trading_mode
            )
        )
        FuzzingAgent.MEMORY["COMMAND"].append("ORDER_SUBMISSION")
        FuzzingAgent.MEMORY["SIDE"].append(
            self.random_state.choice(
                a=[
                    "SIDE_UNSPECIFIED",
                    "SIDE_BUY",
                    "SIDE_SELL",
                ]
            )
        )
        FuzzingAgent.MEMORY["TYPE"].append(
            self.random_state.choice(
                a=[
                    "TYPE_UNSPECIFIED",
                    "TYPE_MARKET",
                    "TYPE_LIMIT",
                ]
            )
        )
        FuzzingAgent.MEMORY["TIME_IN_FORCE"].append(
            self.random_state.choice(
                a=[
                    "TIME_IN_FORCE_UNSPECIFIED",
                    "TIME_IN_FORCE_GTC",
                    "TIME_IN_FORCE_GTT",
                    "TIME_IN_FORCE_GFN",
                    "TIME_IN_FORCE_GFA",
                    "TIME_IN_FORCE_FOK",
                    "TIME_IN_FORCE_IOC",
                ]
            )
        )
        FuzzingAgent.MEMORY["PEGGED_REFERENCE"].append(
            self.random_state.choice(
                a=[
                    "PEGGED_REFERENCE_UNSPECIFIED",
                    "PEGGED_REFERENCE_MID",
                    "PEGGED_REFERENCE_BEST_BID",
                    "PEGGED_REFERENCE_BEST_ASK",
                ],
                p=[0.5, 0.5 / 3, 0.5 / 3, 0.5 / 3],
            )
        )
        FuzzingAgent.MEMORY["REDUCE_ONLY"].append(
            self.random_state.choice(
                a=[
                    True,
                    False,
                ],
            )
        )
        FuzzingAgent.MEMORY["POST_ONLY"].append(
            self.random_state.choice(
                a=[
                    True,
                    False,
                ],
            )
        )

        return self.vega.create_order_submission(
            market_id=self.market_id,
            side=FuzzingAgent.MEMORY["SIDE"][-1],
            size=self.random_state.poisson(lam=10),
            order_type=FuzzingAgent.MEMORY["TYPE"][-1],
            time_in_force=FuzzingAgent.MEMORY["TIME_IN_FORCE"][-1],
            price=self.random_state.choice(
                a=[None, self.random_state.normal(loc=self.curr_price, scale=10)]
            ),
            expires_at=int(
                self.vega.get_blockchain_time()
                + self.random_state.normal(loc=60, scale=60) * 1e9
            ),
            pegged_reference=FuzzingAgent.MEMORY["PEGGED_REFERENCE"][-1],
            pegged_offset=self.random_state.normal(loc=0, scale=10),
            reduce_only=FuzzingAgent.MEMORY["REDUCE_ONLY"][-1],
            post_only=FuzzingAgent.MEMORY["POST_ONLY"][-1],
        )

    def _select_order_id(self):
        if self.live_orders != {}:
            order_key = self.random_state.choice(list(self.live_orders.keys()))
            order = self.live_orders.get(order_key)
            return order.id if order is not None else None
        else:
            return None

    def finalise(self):
        if self.output_plot_on_finalise:
            if not FuzzingAgent.OUTPUTTED:
                import plotly.express as px

                FuzzingAgent.OUTPUTTED = True
                df = pd.DataFrame.from_dict(FuzzingAgent.MEMORY)
                df = (
                    df.groupby(list(FuzzingAgent.MEMORY.keys()))
                    .size()
                    .reset_index()
                    .rename(columns={0: "count"})
                )

                range_color = (10, 5000)
                custom_color_scale = [
                    [0, "red"],
                    [range_color[0] / range_color[1], "red"],
                    [range_color[0] / range_color[1], "yellow"],
                    [1, "green"],
                ]

                fig = px.treemap(
                    df,
                    title="Fuzzed Trader Coverage",
                    path=list(self.__class__.MEMORY.keys()),
                    values="count",
                    color="count",
                    color_continuous_scale=custom_color_scale,
                    range_color=range_color,
                )
                fig.update_traces(marker=dict(cornerradius=5))

                if not os.path.exists("fuzz_plots"):
                    os.mkdir("fuzz_plots")

                fig.write_html("fuzz_plots/coverage.html")


class RiskyMarketOrderTrader(StateAgentWithWallet):
    NAME_BASE = "risky_market_order_trader"

    def __init__(
        self,
        key_name: str,
        market_name: str,
        asset_name: str,
        tag: Optional[str] = None,
        wallet_name: Optional[str] = None,
        state_update_freq: Optional[int] = None,
        random_state: Optional[RandomState] = None,
        side: str = "SIDE_BUY",
        size_factor: float = 0.6,
        initial_asset_mint: float = 1e5,
        step_bias: float = 0.05,
    ):
        super().__init__(key_name, tag, wallet_name, state_update_freq)

        self.market_name = market_name
        self.asset_name = asset_name

        self.size_factor = size_factor
        self.side = side
        self.random_state = random_state if random_state is not None else RandomState()
        self.initial_asset_mint = initial_asset_mint
        self.step_bias = step_bias

        self.close_outs = 0

    def initialise(self, vega: VegaServiceNull, create_key: bool = True, mint_key=True):
        super().initialise(vega, create_key)

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

    def step(self, vega_state):
        account = self.vega.party_account(
            key_name=self.key_name,
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            asset_id=self.asset_id,
        )

        if account.general + account.margin == 0:
            self.vega.mint(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                amount=self.initial_asset_mint,
                asset=self.asset_id,
            )
            self.close_outs += 1
            self.commitment_amount = 0
            return

        if (
            vega_state.market_state[self.market_id].trading_mode
            != markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS
        ):
            return
        if self.random_state.rand() > self.step_bias:
            return

        midprice = vega_state.market_state[self.market_id].midprice

        if account.general > 0:
            add_to_margin = max(
                (account.general + account.margin) * self.size_factor - account.margin,
                0,
            )

            risk_factors = self.vega.get_risk_factors(market_id=self.market_id)
            risk_factor = (
                risk_factors.long if self.side == "SIDE_BUY" else risk_factors.short
            )

            size = add_to_margin / (midprice * risk_factor + 1e-20)

            try:
                self.vega.submit_market_order(
                    trading_key=self.key_name,
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    side=self.side,
                    volume=size,
                    wait=False,
                )
            except Exception as e:
                import pdb

                pdb.set_trace()
                print(f"There was an error {e}")


class RiskySimpleLiquidityProvider(StateAgentWithWallet):
    NAME_BASE = "risky_simple_liquidity_provider"

    def __init__(
        self,
        key_name: str,
        market_name: str,
        asset_name: str,
        tag: Optional[str] = None,
        wallet_name: Optional[str] = None,
        state_update_freq: Optional[int] = None,
        random_state: Optional[RandomState] = None,
        commitment_factor: float = 0.5,
        initial_asset_mint: float = 1e5,
        step_bias: float = 0.05,
    ):
        super().__init__(key_name, tag, wallet_name, state_update_freq)

        self.market_name = market_name
        self.asset_name = asset_name

        self.commitment_factor = commitment_factor
        self.random_state = random_state if random_state is not None else RandomState()
        self.initial_asset_mint = initial_asset_mint
        self.step_bias = step_bias

        self.commitment_amount = 0

        self.close_outs = 0

    def initialise(self, vega: VegaServiceNull, create_key: bool = True, mint_key=True):
        super().initialise(vega, create_key)

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

    def step(self, vega_state):
        account = self.vega.party_account(
            key_name=self.key_name,
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            asset_id=self.asset_id,
        )

        total_balance = account.general + account.margin + account.bond

        if total_balance == 0:
            self.vega.mint(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                amount=self.initial_asset_mint,
                asset=self.asset_id,
            )
            self.close_outs += 1
            self.commitment_amount = 0
            return

        if self.random_state.rand() > self.step_bias:
            return

        if self.commitment_amount < self.commitment_factor * (total_balance):
            self.commitment_amount = self.commitment_factor * (total_balance)

            self.vega.submit_simple_liquidity(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                market_id=self.market_id,
                fee=0.0001,
                commitment_amount=self.commitment_amount,
            )

        self.vega.cancel_order(
            trading_key=self.key_name,
            market_id=self.market_id,
            wallet_name=self.wallet_name,
        )
        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            trading_key=self.key_name,
            side="SIDE_BUY",
            order_type="TYPE_LIMIT",
            pegged_order=PeggedOrder(reference="PEGGED_REFERENCE_BEST_BID", offset=0),
            wait=False,
            time_in_force="TIME_IN_FORCE_GTC",
            volume=(
                (
                    1.2
                    * self.commitment_amount
                    / vega_state.market_state[self.market_id].midprice
                )
                if vega_state.market_state[self.market_id].midprice
                else 1
            ),
        )
        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            trading_key=self.key_name,
            side="SIDE_SELL",
            order_type="TYPE_LIMIT",
            pegged_order=PeggedOrder(reference="PEGGED_REFERENCE_BEST_ASK", offset=0),
            wait=False,
            time_in_force="TIME_IN_FORCE_GTC",
            volume=(
                (
                    1.2
                    * self.commitment_amount
                    / vega_state.market_state[self.market_id].midprice
                )
                if vega_state.market_state[self.market_id].midprice
                else 1
            ),
        )


class FuzzyLiquidityProvider(StateAgentWithWallet):
    NAME_BASE = "fuzzy_liquidity_provider"

    def __init__(
        self,
        key_name: str,
        market_name: str,
        asset_name: str,
        tag: Optional[str] = None,
        wallet_name: Optional[str] = None,
        state_update_freq: Optional[int] = None,
        random_state: Optional[RandomState] = None,
        commitment_factor_min: float = 0.1,
        commitment_factor_max: float = 0.6,
        initial_asset_mint: float = 1e5,
    ):
        super().__init__(key_name, tag, wallet_name, state_update_freq)

        self.market_name = market_name
        self.asset_name = asset_name

        self.commitment_factor_min = commitment_factor_min
        self.commitment_factor_max = commitment_factor_max
        self.random_state = random_state if random_state is not None else RandomState()
        self.initial_asset_mint = initial_asset_mint

    def initialise(self, vega: VegaServiceNull, create_key: bool = True, mint_key=True):
        super().initialise(vega, create_key)

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

    def _gen_spec(self, side: vega_protos.vega.Side, is_valid: bool):
        refs = [
            vega_protos.vega.PeggedReference.PEGGED_REFERENCE_UNSPECIFIED,
            vega_protos.vega.PeggedReference.PEGGED_REFERENCE_MID,
            vega_protos.vega.PeggedReference.PEGGED_REFERENCE_BEST_BID,
            vega_protos.vega.PeggedReference.PEGGED_REFERENCE_BEST_ASK,
        ]
        invalid_ref = (
            vega_protos.vega.PeggedReference.PEGGED_REFERENCE_BEST_BID
            if side == vega_protos.vega.SIDE_SELL
            else vega_protos.vega.PeggedReference.PEGGED_REFERENCE_BEST_ASK
        )
        if is_valid:
            refs = [r for r in refs if r != invalid_ref]

        return (
            self.random_state.choice(refs),
            (
                self.random_state.randint(low=1, high=400)
                if is_valid
                else self.random_state.randint(-5, 5)
            ),
            self.random_state.randint(low=0, high=4000000),
        )

    def step(self, vega_state):
        commitment_factor = (
            self.random_state.random_sample()
            * (self.commitment_factor_max - self.commitment_factor_min)
            + self.commitment_factor_min
        )
        account = self.vega.party_account(
            key_name=self.key_name,
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            asset_id=self.asset_id,
        )

        total_balance = account.general + account.margin + account.bond

        if total_balance == 0:
            self.vega.mint(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                amount=self.initial_asset_mint,
                asset=self.asset_id,
            )
            return

        commitment_amount = commitment_factor * (total_balance)

        valid = self.random_state.choice([1, 0], p=[0.95, 0.05])
        fee = (
            self.random_state.random_sample() * 0.05
            if valid
            else self.random_state.random_sample() * 200 - 100
        )

        buy_specs = [
            self._gen_spec(vega_protos.vega.SIDE_BUY, valid)
            for _ in range(self.random_state.randint(1, 50))
        ]

        sell_specs = [
            self._gen_spec(vega_protos.vega.SIDE_SELL, valid)
            for _ in range(self.random_state.randint(1, 50))
        ]

        self.vega.submit_liquidity(
            key_name=self.key_name,
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            fee=fee,
            commitment_amount=commitment_amount,
            buy_specs=buy_specs,
            sell_specs=sell_specs,
            is_amendment=self.random_state.choice([True, False]),
        )


class SuccessorMarketCreatorAgent(StateAgentWithWallet):
    NAME_BASE = "successor_market_creator"

    def __init__(
        self,
        key_name: str,
        market_name: str,
        asset_name: str,
        tag: Optional[str] = None,
        wallet_name: Optional[str] = None,
        state_update_freq: Optional[int] = None,
        random_state: Optional[RandomState] = None,
        initial_asset_mint: float = 1e5,
        new_market_prob: float = 0.02,
    ):
        super().__init__(key_name, tag, wallet_name, state_update_freq)

        self.market_name = market_name
        self.asset_name = asset_name

        self.random_state = random_state if random_state is not None else RandomState()
        self.initial_asset_mint = initial_asset_mint

    def initialise(self, vega: VegaServiceNull, create_key: bool = True, mint_key=True):
        super().initialise(vega, create_key)

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


class FuzzySuccessorConfigurableMarketManager(StateAgentWithWallet):
    def __init__(
        self,
        proposal_key_name: str,
        termination_key_name: str,
        market_name: str,
        market_code: str,
        asset_name: str,
        asset_dp: int,
        proposal_wallet_name: Optional[str] = None,
        termination_wallet_name: Optional[str] = None,
        market_config: Optional[MarketConfig] = None,
        tag: Optional[str] = None,
        settlement_price: Optional[float] = None,
        initial_mint: Optional[float] = 1e9,
        successor_probability: float = 0.02,
        random_state: Optional[RandomState] = None,
        market_agents: Optional[Dict[str, List[StateAgentWithWallet]]] = None,
        stake_key: bool = False,
    ):
        super().__init__(
            wallet_name=proposal_wallet_name,
            key_name=proposal_key_name,
            tag=tag,
        )

        self.termination_wallet_name = termination_wallet_name
        self.termination_key_base = termination_key_name
        self.latest_key_idx = 0
        self.market_agents = market_agents if market_agents is not None else {}

        self.successor_probability = successor_probability
        self.random_state = random_state if random_state is not None else RandomState()

        self.market_name_base = market_name
        self.market_code_base = market_code

        self.asset_dp = asset_dp
        self.asset_name = asset_name

        self.initial_mint = initial_mint

        self.market_config = (
            market_config if market_config is not None else MarketConfig()
        )

        self.settlement_price = settlement_price
        self.needs_to_update_markets = False
        self.stake_key = stake_key

    def _get_termination_key_name(self):
        return (
            f"{self.termination_key_base}_{self.latest_key_idx}"
            if self.latest_key_idx > 0
            else self.termination_key_base
        )

    def _get_market_name(self):
        return (
            f"{self.market_name_base}_{self.latest_key_idx}"
            if self.latest_key_idx > 0
            else self.market_name_base
        )

    def _get_market_code(self):
        return (
            f"{self.market_code_base}_{self.latest_key_idx}"
            if self.latest_key_idx > 0
            else self.market_code_base
        )

    def initialise(
        self,
        vega: VegaServiceNull,
        create_key: bool = True,
        mint_key: bool = True,
    ):
        super().initialise(vega=vega, create_key=create_key)
        if create_key:
            self.vega.create_key(
                wallet_name=self.termination_wallet_name,
                name=self._get_termination_key_name(),
            )

        self.vega.wait_for_total_catchup()
        if mint_key:
            self.vega.mint(
                wallet_name=self.wallet_name,
                asset="VOTE",
                amount=1e4,
                key_name=self.key_name,
            )

        if self.stake_key:
            self.vega.stake(
                amount=1,
                key_name=self.key_name,
                wallet_name=self.wallet_name,
            )

        self.vega.wait_for_total_catchup()

        if self.vega.find_asset_id(symbol=self.asset_name) is None:
            self.vega.create_asset(
                wallet_name=self.wallet_name,
                name=self.asset_name,
                symbol=self.asset_name,
                decimals=self.asset_dp,
                quantum=int(10 ** (self.asset_dp)),
                max_faucet_amount=10_000_000_000,
                key_name=self.key_name,
            )

        self.vega.wait_for_total_catchup()
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)

        self.vega.wait_for_total_catchup()
        if mint_key:
            self.vega.mint(
                wallet_name=self.wallet_name,
                asset=self.asset_id,
                amount=self.initial_mint,
                key_name=self.key_name,
            )

        self.vega.wait_for_total_catchup()
        self.market_id = self.vega.find_market_id(name=self._get_market_name())

        if self.market_id is None:
            self._create_latest_market()

    def _create_latest_market(self, parent_market_id: Optional[str] = None):
        # Add market information and asset information to market config
        mkt_config = copy.deepcopy(self.market_config)
        mkt_config.set("instrument.name", self._get_market_name())
        mkt_config.set("instrument.code", self._get_market_code())
        mkt_config.set("instrument.future.settlement_asset", self.asset_id)
        mkt_config.set("instrument.future.quote_name", self.asset_name)
        mkt_config.set("instrument.future.number_decimal_places", self.asset_dp)
        mkt_config.set(
            "instrument.future.terminating_key",
            self.vega.wallet.public_key(
                wallet_name=self.termination_wallet_name,
                name=self._get_termination_key_name(),
            ),
        )

        if parent_market_id is not None:
            mkt_config.set(
                "successor",
                Successor(
                    opt={
                        "parent_market_id": parent_market_id,
                        "insurance_pool_fraction": 1,
                    }
                ),
            )

        self.vega.wait_for_total_catchup()
        self.vega.create_market_from_config(
            proposal_wallet_name=self.wallet_name,
            proposal_key_name=self.key_name,
            market_config=mkt_config,
        )

        self.vega.wait_for_total_catchup()
        self.market_id = self.vega.find_market_id(name=self._get_market_name())

    def finalise(self):
        if self.settlement_price is not None:
            self.vega.settle_market(
                self._get_termination_key_name(),
                self.settlement_price,
                self.market_id,
                self.termination_wallet_name,
            )
            self.vega.wait_for_total_catchup()

    def step(self, vega_state) -> None:
        if self.needs_to_update_markets:
            self.vega.settle_market(
                self.old_termination_key,
                self.vega.market_data_from_feed(self.old_market_id).last_traded_price,
                self.market_id,
                self.termination_wallet_name,
            )

            self.market_id = self.vega.find_market_id(name=self._get_market_name())
            for agents in self.market_agents.values():
                for agent in agents:
                    agent.market_id = self.market_id
                    agent.market_name = self._get_market_name()
            self.needs_to_update_markets = False

        if self.random_state.random() < self.successor_probability:
            self.old_market_id = self.market_id
            self.old_termination_key = self._get_termination_key_name()
            self.latest_key_idx += 1

            self.vega.create_key(
                wallet_name=self.termination_wallet_name,
                name=self._get_termination_key_name(),
            )

            self._create_latest_market(parent_market_id=self.market_id)
            self.needs_to_update_markets = True
