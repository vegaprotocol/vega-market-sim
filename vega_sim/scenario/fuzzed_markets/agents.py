import logging
import copy
import os
from typing import Optional, Dict, List

import pandas as pd
from numpy import array
from numpy.random import RandomState
from datetime import datetime

import vega_sim.proto.vega as vega_protos
from vega_sim.api.market import MarketConfig, Successor
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import markets as markets_protos
from vega_sim.service import VegaService, PeggedOrder, VegaCommandError
from vega_sim.api.governance import ProposalNotAcceptedError
from requests.exceptions import HTTPError

import vega_sim.builders as builders

from uuid import uuid4

import vega_sim.scenario.fuzzed_markets.fuzzers as fuzzers


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
        self.curr_time = self.vega.get_blockchain_time(in_seconds=True)

        submissions = [self.create_fuzzed_submission(vega_state) for _ in range(20)]
        amendments = [self.create_fuzzed_amendment(vega_state) for _ in range(10)]
        cancellations = [self.create_fuzzed_cancellation(vega_state) for _ in range(1)]
        stop_orders_submissions = [
            self.create_fuzzed_stop_orders_submission(vega_state) for _ in range(10)
        ]

        self.vega.submit_instructions(
            key_name=self.key_name,
            wallet_name=self.wallet_name,
            submissions=submissions,
            amendments=amendments,
            cancellations=cancellations,
            stop_orders_submission=stop_orders_submissions,
        )

    def create_fuzzed_cancellation(self, vega_state):
        order_id = self._select_order_id()

        return self.vega.build_order_cancellation(
            order_id=order_id,
            market_id=self.market_id,
        )

    def create_fuzzed_amendment(self, vega_state):
        order_id = self._select_order_id()

        return self.vega.build_order_amendment(
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
                vega_state.time + self.random_state.normal(loc=60, scale=60) * 1e9
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
                    vega_protos.vega.PEGGED_REFERENCE_UNSPECIFIED,
                    vega_protos.vega.PEGGED_REFERENCE_MID,
                    vega_protos.vega.PEGGED_REFERENCE_BEST_BID,
                    vega_protos.vega.PEGGED_REFERENCE_BEST_ASK,
                ],
                p=[0.1, 0.3, 0.3, 0.3],
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

        try:
            return self.vega.build_order_submission(
                market_id=self.market_id,
                side=FuzzingAgent.MEMORY["SIDE"][-1],
                size=self.random_state.poisson(lam=10),
                order_type=FuzzingAgent.MEMORY["TYPE"][-1],
                time_in_force=FuzzingAgent.MEMORY["TIME_IN_FORCE"][-1],
                price=self.random_state.choice(
                    a=[None, self.random_state.normal(loc=self.curr_price, scale=10)]
                ),
                expires_at=int(
                    vega_state.time + self.random_state.normal(loc=60, scale=60) * 1e9
                ),
                pegged_order=self.random_state.choice(
                    [
                        None,
                        builders.commands.commands.pegged_order(
                            market_price_decimals=self.vega.market_price_decimals,
                            market_id=self.market_id,
                            reference=FuzzingAgent.MEMORY["PEGGED_REFERENCE"][-1],
                            offset=self.random_state.normal(loc=0, scale=10),
                        ),
                    ]
                ),
                iceberg_opts=self.random_state.choice(
                    [
                        None,
                        builders.commands.commands.iceberg_opts(
                            market_pos_decimals=self.vega.market_pos_decimals,
                            market_id=self.market_id,
                            peak_size=self.random_state.normal(loc=100, scale=20),
                            minimum_visible_size=self.random_state.normal(
                                loc=100, scale=20
                            ),
                        ),
                    ]
                ),
                reduce_only=FuzzingAgent.MEMORY["REDUCE_ONLY"][-1],
                post_only=FuzzingAgent.MEMORY["POST_ONLY"][-1],
            )
        except VegaCommandError:
            return None

    def create_fuzzed_stop_orders_submission(self, vega_state):
        try:
            return builders.commands.commands.stop_orders_submission(
                rises_above=self.random_state.choice(
                    [self.create_fuzzed_stop_orders_setup(vega_state), None]
                ),
                falls_below=self.random_state.choice(
                    [self.create_fuzzed_stop_orders_setup(vega_state), None]
                ),
            )
        except VegaCommandError:
            return None

    def create_fuzzed_stop_orders_setup(self, vega_state):
        return builders.commands.commands.stop_order_setup(
            market_price_decimals=self.vega.market_price_decimals,
            market_id=self.market_id,
            order_submission=self.create_fuzzed_submission(vega_state=vega_state),
            expires_at=datetime.utcfromtimestamp(
                self.random_state.normal(loc=self.curr_time + 120, scale=30)
            ),
            expiry_strategy=self.random_state.choice(
                [
                    None,
                    vega_protos.vega.StopOrder.EXPIRY_STRATEGY_UNSPECIFIED,
                    vega_protos.vega.StopOrder.EXPIRY_STRATEGY_CANCELS,
                    vega_protos.vega.StopOrder.EXPIRY_STRATEGY_SUBMIT,
                ]
            ),
            price=self.random_state.choice(
                [None, self.random_state.normal(loc=self.curr_price, scale=10)]
            ),
            trailing_percent_offset=self.random_state.choice(
                [None, self.random_state.rand()]
            ),
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

        midprice = vega_state.market_state[self.market_id].midprice

        if (
            vega_state.market_state[self.market_id].trading_mode
            != markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS
            or midprice == 0
        ):
            return
        if self.random_state.rand() > self.step_bias:
            return

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
            pegged_order=PeggedOrder(
                reference=vega_protos.vega.PEGGED_REFERENCE_BEST_BID, offset=0
            ),
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
            pegged_order=PeggedOrder(
                reference=vega_protos.vega.PEGGED_REFERENCE_BEST_ASK, offset=0
            ),
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
            # vega_protos.vega.PeggedReference.PEGGED_REFERENCE_UNSPECIFIED,
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
            3 * self.random_state.random(),
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
            [
                vega_protos.vega.SIDE_BUY,
                self._gen_spec(vega_protos.vega.SIDE_BUY, valid),
            ]
            for _ in range(self.random_state.randint(1, 50))
        ]

        sell_specs = [
            [
                vega_protos.vega.SIDE_SELL,
                self._gen_spec(vega_protos.vega.SIDE_SELL, valid),
            ]
            for _ in range(self.random_state.randint(1, 50))
        ]

        self.vega.cancel_order(
            trading_key=self.key_name,
            wallet_name=self.wallet_name,
            market_id=self.market_id,
        )
        for side, spec in buy_specs + sell_specs:
            try:
                self.vega.submit_order(
                    trading_key=self.key_name,
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    order_type="TYPE_LIMIT",
                    time_in_force="TIME_IN_FORCE_GTC",
                    pegged_order=PeggedOrder(reference=spec[0], offset=spec[1]),
                    volume=spec[2] * commitment_amount,
                    side=side,
                    wait=False,
                )
            except HTTPError:
                continue
        try:
            self.vega.submit_liquidity(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                market_id=self.market_id,
                fee=fee,
                commitment_amount=commitment_amount,
                is_amendment=self.random_state.choice([True, False, None]),
            )
        except HTTPError:
            return


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
            self.vega.submit_termination_and_settlement_data(
                self._get_termination_key_name(),
                self.settlement_price,
                self.market_id,
                self.termination_wallet_name,
            )
            self.vega.wait_for_total_catchup()

    def step(self, vega_state) -> None:
        if self.needs_to_update_markets:
            self.vega.submit_termination_and_settlement_data(
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


class FuzzyReferralProgramManager(StateAgentWithWallet):
    """Agent proposes sensible and fuzzed update referral program proposals at a
    controlled frequency.
    """

    def __init__(
        self,
        key_name: str,
        step_bias=0.5,
        attempts_per_step=100,
        stake_key: bool = False,
        wallet_name: Optional[str] = None,
        random_state: Optional[RandomState] = None,
        tag: Optional[str] = None,
    ):
        self.key_name = key_name
        self.wallet_name = wallet_name
        self.tag = tag
        self.stake_key = stake_key

        self.step_bias = step_bias
        self.attempts_per_step = attempts_per_step

        self.random_state = random_state if random_state is not None else RandomState()

    def initialise(self, vega: VegaServiceNull, create_key: bool = True, mint_key=True):
        super().initialise(vega, create_key)
        self.vega.wait_for_total_catchup()
        if mint_key:
            self.vega.mint(
                wallet_name=self.wallet_name,
                asset="VOTE",
                amount=1e4,
                key_name=self.key_name,
            )
        self.vega.wait_for_total_catchup()
        if self.stake_key:
            self.vega.stake(
                amount=1,
                key_name=self.key_name,
                wallet_name=self.wallet_name,
            )
        self.vega.wait_for_total_catchup()
        self._sensible_proposal()

    def step(self, vega_state):
        if self.random_state.rand() > self.step_bias:
            for i in range(self.attempts_per_step):
                try:
                    self._fuzzed_proposal()
                    return
                except (HTTPError, ProposalNotAcceptedError):
                    continue
            logging.info(
                "All fuzzed UpdateReferralProgram proposals failed, submitting sensible proposal."
            )
            self._sensible_proposal()

    def _sensible_proposal(self):
        self.vega.update_referral_program(
            forward_time_to_enactment=False,
            proposal_key=self.key_name,
            wallet_name=self.wallet_name,
            benefit_tiers=[
                {
                    "minimum_running_notional_taker_volume": 1,
                    "minimum_epochs": 1,
                    "referral_reward_factor": 0.1,
                    "referral_discount_factor": 0.1,
                },
                {
                    "minimum_running_notional_taker_volume": 2,
                    "minimum_epochs": 2,
                    "referral_reward_factor": 0.2,
                    "referral_discount_factor": 0.2,
                },
                {
                    "minimum_running_notional_taker_volume": 3,
                    "minimum_epochs": 3,
                    "referral_reward_factor": 0.3,
                    "referral_discount_factor": 0.3,
                },
            ],
            staking_tiers=[
                {"minimum_staked_tokens": 1, "referral_reward_multiplier": 1},
            ],
            window_length=1,
        )

    def _fuzzed_proposal(self):
        self.vega.update_referral_program(
            forward_time_to_enactment=False,
            proposal_key=self.key_name,
            wallet_name=self.wallet_name,
            benefit_tiers=[
                {
                    "minimum_running_notional_taker_volume": self.random_state.randint(
                        1, 1e6
                    ),
                    "minimum_epochs": self.random_state.randint(1, 10),
                    "referral_reward_factor": self.random_state.rand(),
                    "referral_discount_factor": self.random_state.rand(),
                }
                for _ in range(self.random_state.randint(1, 5))
            ],
            staking_tiers=[
                {
                    "minimum_staked_tokens": self.random_state.randint(1, 10),
                    "referral_reward_multiplier": self.random_state.randint(1, 10),
                }
                for _ in range(self.random_state.randint(1, 5))
            ],
            window_length=self.random_state.randint(1, 100),
            end_of_program_timestamp=datetime.fromtimestamp(
                self.vega.get_blockchain_time(in_seconds=True)
                + self.random_state.normal(
                    loc=600 * self.vega.seconds_per_block,
                    scale=300 * self.vega.seconds_per_block,
                )
            ),
        )


class FuzzyVolumeDiscountProgramManager(StateAgentWithWallet):
    """Agent proposes sensible and fuzzed update referral program proposals at a
    controlled frequency.
    """

    def __init__(
        self,
        key_name: str,
        step_bias=0.5,
        attempts_per_step=100,
        stake_key: bool = False,
        wallet_name: Optional[str] = None,
        random_state: Optional[RandomState] = None,
        tag: Optional[str] = None,
    ):
        self.key_name = key_name
        self.wallet_name = wallet_name
        self.tag = tag
        self.stake_key = stake_key

        self.step_bias = step_bias
        self.attempts_per_step = attempts_per_step

        self.random_state = random_state if random_state is not None else RandomState()

    def initialise(self, vega: VegaServiceNull, create_key: bool = True, mint_key=True):
        super().initialise(vega, create_key)
        self.vega.wait_for_total_catchup()
        if mint_key:
            self.vega.mint(
                wallet_name=self.wallet_name,
                asset="VOTE",
                amount=1e4,
                key_name=self.key_name,
            )
        self.vega.wait_for_total_catchup()
        if self.stake_key:
            self.vega.stake(
                amount=1,
                key_name=self.key_name,
                wallet_name=self.wallet_name,
            )
        self.vega.wait_for_total_catchup()
        self._sensible_proposal()

    def step(self, vega_state):
        if self.random_state.rand() > self.step_bias:
            for i in range(self.attempts_per_step):
                try:
                    self._fuzzed_proposal()
                    return
                except (HTTPError, ProposalNotAcceptedError):
                    continue
            logging.info(
                "All fuzzed UpdateReferralProgram proposals failed, submitting sensible proposal."
            )
            self._sensible_proposal()

    def _sensible_proposal(self):
        self.vega.update_volume_discount_program(
            forward_time_to_enactment=False,
            proposal_key=self.key_name,
            wallet_name=self.wallet_name,
            benefit_tiers=[
                {
                    "minimum_running_notional_taker_volume": 1000,
                    "volume_discount_factor": 0.01,
                },
                {
                    "minimum_running_notional_taker_volume": 2000,
                    "volume_discount_factor": 0.02,
                },
                {
                    "minimum_running_notional_taker_volume": 3000,
                    "volume_discount_factor": 0.03,
                },
            ],
            window_length=1,
        )

    def _fuzzed_proposal(self):
        self.vega.update_volume_discount_program(
            forward_time_to_enactment=False,
            proposal_key=self.key_name,
            wallet_name=self.wallet_name,
            benefit_tiers=[
                {
                    "minimum_running_notional_taker_volume": self.random_state.randint(
                        1, 1e6
                    ),
                    "volume_discount_factor": self.random_state.rand(),
                }
                for _ in range(self.random_state.randint(1, 5))
            ],
            window_length=self.random_state.randint(1, 100),
            end_of_program_timestamp=datetime.fromtimestamp(
                self.vega.get_blockchain_time(in_seconds=True)
                + self.random_state.normal(
                    loc=600 * self.vega.seconds_per_block,
                    scale=300 * self.vega.seconds_per_block,
                )
            ),
        )


class FuzzyRewardFunder(StateAgentWithWallet):
    NAME_BASE = "fuzzy_reward_funder"

    # List of valid dispatch metrics
    DISPATCH_METRICS = [
        vega_protos.vega.DISPATCH_METRIC_UNSPECIFIED,
        vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_PAID,
        vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_RECEIVED,
        vega_protos.vega.DISPATCH_METRIC_LP_FEES_RECEIVED,
        vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE,
        vega_protos.vega.DISPATCH_METRIC_AVERAGE_POSITION,
        vega_protos.vega.DISPATCH_METRIC_RELATIVE_RETURN,
        vega_protos.vega.DISPATCH_METRIC_RETURN_VOLATILITY,
        vega_protos.vega.DISPATCH_METRIC_VALIDATOR_RANKING,
    ]
    # Map of valid dispatch metrics to relevant account type
    ACCOUNT_TYPES = {
        vega_protos.vega.DISPATCH_METRIC_UNSPECIFIED: vega_protos.vega.ACCOUNT_TYPE_UNSPECIFIED,
        vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_PAID: vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_PAID_FEES,
        vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_RECEIVED: vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_RECEIVED_FEES,
        vega_protos.vega.DISPATCH_METRIC_LP_FEES_RECEIVED: vega_protos.vega.ACCOUNT_TYPE_REWARD_LP_RECEIVED_FEES,
        vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE: vega_protos.vega.ACCOUNT_TYPE_REWARD_MARKET_PROPOSERS,
        vega_protos.vega.DISPATCH_METRIC_AVERAGE_POSITION: vega_protos.vega.ACCOUNT_TYPE_REWARD_AVERAGE_POSITION,
        vega_protos.vega.DISPATCH_METRIC_RELATIVE_RETURN: vega_protos.vega.ACCOUNT_TYPE_REWARD_RELATIVE_RETURN,
        vega_protos.vega.DISPATCH_METRIC_RETURN_VOLATILITY: vega_protos.vega.ACCOUNT_TYPE_REWARD_RETURN_VOLATILITY,
        vega_protos.vega.DISPATCH_METRIC_VALIDATOR_RANKING: vega_protos.vega.ACCOUNT_TYPE_REWARD_VALIDATOR_RANKING,
    }

    # List of valid entity scopes
    ENTITY_SCOPE = {
        vega_protos.vega.ENTITY_SCOPE_UNSPECIFIED: 0.1,
        vega_protos.vega.ENTITY_SCOPE_INDIVIDUALS: 0.45,
        vega_protos.vega.ENTITY_SCOPE_TEAMS: 0.45,
    }
    # List of valid individual scopes
    INDIVIDUAL_SCOPE = {
        vega_protos.vega.INDIVIDUAL_SCOPE_UNSPECIFIED: 0.1,
        vega_protos.vega.INDIVIDUAL_SCOPE_ALL: 0.3,
        vega_protos.vega.INDIVIDUAL_SCOPE_IN_TEAM: 0.3,
        vega_protos.vega.INDIVIDUAL_SCOPE_NOT_IN_TEAM: 0.3,
    }
    # List of valid distribution strategies
    DISTRIBUTION_STRATEGIES = {
        vega_protos.vega.DISTRIBUTION_STRATEGY_UNSPECIFIED: 0.1,
        vega_protos.vega.DISTRIBUTION_STRATEGY_PRO_RATA: 0.45,
        vega_protos.vega.DISTRIBUTION_STRATEGY_RANK: 0.45,
    }

    def __init__(
        self,
        key_name: str,
        asset_name: str,
        step_bias: float = 0.1,
        validity_bias: float = 0.8,
        attempts_per_step: int = 20,
        initial_mint: float = 1e9,
        wallet_name: Optional[str] = None,
        stake_key: bool = False,
        random_state: Optional[RandomState] = None,
        tag: Optional[str] = None,
    ):
        super().__init__(wallet_name=wallet_name, key_name=key_name, tag=tag)

        self.asset_name = asset_name
        self.initial_mint = initial_mint
        self.stake_key = stake_key
        self.step_bias = step_bias
        self.validity_bias = validity_bias
        self.attempts_per_step = attempts_per_step

        self.random_state = random_state if random_state is not None else RandomState()

    def initialise(
        self,
        vega: VegaService,
        create_key: bool = True,
        mint_key: bool = True,
    ):
        # Initialise wallet
        super().initialise(vega=vega, create_key=create_key)

        # Get asset id
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            # Top up asset
            self.vega.mint(
                key_name=self.key_name,
                asset=self.asset_id,
                amount=self.initial_mint,
                wallet_name=self.wallet_name,
            )
        if self.stake_key:
            self.vega.stake(
                amount=1,
                key_name=self.key_name,
                wallet_name=self.wallet_name,
            )

    def step(self, vega_state):
        if self.random_state.rand() > self.step_bias:
            return
        for _ in range(self.attempts_per_step):
            try:
                self._fuzzed_transfer(vega_state)
            except HTTPError:
                continue

    def _fuzzed_transfer(self, vega_state):
        # Pick transfer durations
        current_epoch = self.vega.statistics().epoch_seq
        start_epoch = self._pick_start_epoch(current_epoch)
        end_epoch = self._pick_end_epoch(start_epoch)

        # Pick driving parameters
        entity_scope = self.random_state.choice(
            list(self.ENTITY_SCOPE.keys()), p=list(self.ENTITY_SCOPE.values())
        )
        dispatch_metric = self.random_state.choice(self.DISPATCH_METRICS)
        distribution_strategy = self.random_state.choice(
            list(self.DISTRIBUTION_STRATEGIES.keys()),
            p=list(self.DISTRIBUTION_STRATEGIES.values()),
        )

        self.vega.recurring_transfer(
            start_epoch=start_epoch,
            end_epoch=end_epoch,
            asset=self.asset_id,
            amount=self.random_state.normal(loc=150, scale=10),
            from_wallet_name=self.wallet_name,
            from_key_name=self.key_name,
            asset_for_metric=self._pick_asset_for_metric(dispatch_metric),
            metric=dispatch_metric,
            from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            to_account_type=self._pick_account_type(dispatch_metric),
            factor=self.random_state.rand(),
            markets=self._pick_markets(list(vega_state.market_state.keys())),
            entity_scope=entity_scope,
            individual_scope=self._pick_individual_scope(entity_scope),
            n_top_performers=self._pick_n_top_performers(entity_scope),
            notional_time_weighted_average_position_requirement=self._pick_notional_time_weighted_average_position_requirement(),
            window_length=self._pick_window_length(dispatch_metric),
            lock_period=self._pick_window_length(dispatch_metric),
            distribution_strategy=distribution_strategy,
            rank_table=self._pick_rank_table(distribution_strategy),
        )

    def _valid(self):
        return self.random_state.rand() < self.validity_bias

    def _pick_start_epoch(self, current_epoch):
        """Given a current_epoch, pick either a valid or random start_epoch."""
        if self._valid():
            return current_epoch + self.random_state.randint(1, 5)
        else:
            return max(current_epoch + self.random_state.randint(-5, 5), 0)

    def _pick_end_epoch(self, start_epoch):
        """Given a start_epoch, pick either a valid or random end_epoch."""
        if self._valid():
            return start_epoch + self.random_state.randint(1, 5)
        else:
            return max(start_epoch + self.random_state.randint(-5, 5), 0)

    def _pick_account_type(self, dispatch_metric):
        """Given a dispatch_metric, pick either a valid or random account_type."""
        if self._valid():
            return self.ACCOUNT_TYPES[dispatch_metric]
        else:
            return self.random_state.choice([None] + list(self.ACCOUNT_TYPES.values()))

    def _pick_asset_for_metric(self, dispatch_metric):
        """Given a dispatch_metric, pick either a valid or random asset_for_metric."""
        if self._valid():
            if dispatch_metric == vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE:
                return None
            else:
                return self.asset_id
        else:
            return self.random_state.choice([None, self.asset_id])

    def _pick_individual_scope(self, entity_scope):
        """Given an entity_scope, pick either a valid or random individual_scope."""
        if self._valid():
            if entity_scope == vega_protos.vega.ENTITY_SCOPE_INDIVIDUALS:
                return self.random_state.choice(
                    list(self.INDIVIDUAL_SCOPE.keys()),
                    p=list(self.INDIVIDUAL_SCOPE.values()),
                )
            if entity_scope == vega_protos.vega.ENTITY_SCOPE_TEAMS:
                return None
        else:
            return self.random_state.choice([None] + list(self.INDIVIDUAL_SCOPE.keys()))

    def _pick_n_top_performers(self, entity_scope):
        """Given an entity_scope, pick either a valid or random n_top_performers."""
        if self._valid():
            if entity_scope == vega_protos.vega.ENTITY_SCOPE_INDIVIDUALS:
                return None
            if entity_scope == vega_protos.vega.ENTITY_SCOPE_TEAMS:
                return self.random_state.rand()
        else:
            return self.random_state.choice([None, self.random_state.rand()])

    def _pick_markets(self, markets):
        """Given a list of markets, pick either no markets or a subset of markets"""
        if len(markets) <= 1:
            return None
        if self.random_state.rand() < 0.5:
            return None
        else:
            return self.random_state.choice(
                markets, self.random_state.randint(1, len(markets))
            )

    def _pick_notional_time_weighted_average_position_requirement(self):
        """Pick a random notional_time_weighted_average_position_requirement"""
        return self.random_state.choice([None, self.random_state.randint(0, 1000)])

    def _pick_window_length(self, dispatch_metric):
        """Given a dispatch_metric, pick either a valid or random window_length"""
        if self._valid():
            if dispatch_metric == vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE:
                return None
            if dispatch_metric == vega_protos.vega.DISPATCH_METRIC_RETURN_VOLATILITY:
                return self.random_state.randint(2, 5)
            return self.random_state.randint(1, 5)
        else:
            return self.random_state.choice([None, self.random_state.randint(0, 5)])

    def _pick_lock_period(self):
        """Pick either a valid or random lock_period"""
        if self._valid():
            return self.random_state.randint(0, 5)
        else:
            return self.random_state.choice([None, self.random_state.randint(0, 5)])

    def _pick_rank_table(self, distribution_strategy):
        """Given a distribution_strategy, pick either a valid or random rank_table"""
        if self._valid():
            if distribution_strategy == vega_protos.vega.DISTRIBUTION_STRATEGY_PRO_RATA:
                return None
            if distribution_strategy == vega_protos.vega.DISTRIBUTION_STRATEGY_RANK:
                rank_table = [
                    vega_protos.vega.Rank(
                        start_rank=1,
                        share_ratio=self.random_state.randint(1, 100),
                    )
                ]
                for _ in range(self.random_state.randint(1, 10)):
                    rank_table.append(
                        vega_protos.vega.Rank(
                            start_rank=rank_table[-1].start_rank
                            + self.random_state.randint(1, 10),
                            share_ratio=self.random_state.randint(1, 10),
                        )
                    )
                return rank_table
            return self.random_state.choice(
                array(
                    [
                        None,
                        [
                            vega_protos.vega.Rank(
                                start_rank=self.random_state.randint(1, 10),
                                share_ratio=self.random_state.randint(1, 10),
                            )
                            for _ in range(5)
                        ],
                    ],
                    dtype=object,
                )
            )


class FuzzyGovernanceTransferAgent(FuzzyRewardFunder):
    NAME_BASE = "FuzzyGovernanceTransferAgent"

    SOURCE_TYPES = {
        vega_protos.vega.ACCOUNT_TYPE_UNSPECIFIED: 0.1,
        vega_protos.vega.ACCOUNT_TYPE_GLOBAL_INSURANCE: 0.45,
        vega_protos.vega.ACCOUNT_TYPE_NETWORK_TREASURY: 0.45,
    }

    TRANSFER_TYPES = {
        vega_protos.governance.GOVERNANCE_TRANSFER_TYPE_UNSPECIFIED: 0.1,
        vega_protos.governance.GOVERNANCE_TRANSFER_TYPE_ALL_OR_NOTHING: 0.45,
        vega_protos.governance.GOVERNANCE_TRANSFER_TYPE_BEST_EFFORT: 0.45,
    }

    DESTINATION_TYPES = {
        vega_protos.vega.ACCOUNT_TYPE_UNSPECIFIED: 0.0,
        vega_protos.vega.ACCOUNT_TYPE_INSURANCE: 0.2,
        vega_protos.vega.ACCOUNT_TYPE_GENERAL: 0.2,
        vega_protos.vega.ACCOUNT_TYPE_GLOBAL_INSURANCE: 0.2,
        vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_PAID_FEES: 0.05,
        vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_RECEIVED_FEES: 0.05,
        vega_protos.vega.ACCOUNT_TYPE_REWARD_LP_RECEIVED_FEES: 0.05,
        vega_protos.vega.ACCOUNT_TYPE_REWARD_MARKET_PROPOSERS: 0.05,
        vega_protos.vega.ACCOUNT_TYPE_REWARD_AVERAGE_POSITION: 0.05,
        vega_protos.vega.ACCOUNT_TYPE_REWARD_RELATIVE_RETURN: 0.05,
        vega_protos.vega.ACCOUNT_TYPE_REWARD_RETURN_VOLATILITY: 0.05,
        vega_protos.vega.ACCOUNT_TYPE_REWARD_VALIDATOR_RANKING: 0.05,
    }

    def initialise(
        self,
        vega: VegaService,
        create_key: bool = True,
        mint_key: bool = True,
    ):
        # Initialise wallet
        super().initialise(vega=vega, create_key=create_key)

        # Get asset id
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        if mint_key:
            # Top up asset
            self.vega.mint(
                key_name=self.key_name,
                asset=self.asset_id,
                amount=self.initial_mint,
                wallet_name=self.wallet_name,
            )
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

    def step(self, vega_state):
        if self.random_state.rand() > self.step_bias:
            return
        for _ in range(self.attempts_per_step):
            try:
                self._fuzzed_transfer(vega_state)
            except (HTTPError, ProposalNotAcceptedError):
                print("Transaction successful")
                continue

    def _fuzzed_transfer(self, vega_state):
        # Pick drivers
        one_off = self.random_state.choice([True, False])
        source_type = self._pick_source_type()
        destination_type = self._pick_destination_type(one_off)

        new_transfer = builders.governance.new_transfer(
            changes=builders.governance.new_transfer_configuration(
                asset_decimals=self.vega.asset_decimals,
                source_type=source_type,
                transfer_type=self._pick_transfer_type(),
                amount=100,
                asset=self.asset_id,
                fraction_of_balance=self.random_state.rand(),
                destination="",
                destination_type=destination_type,
                source=self._pick_source(
                    source_type=source_type,
                    markets=list(vega_state.market_state.keys()),
                ),
                one_off=self._pick_one_off(one_off),
                recurring=self._pick_recurring(one_off, destination_type, vega_state),
            )
        )
        blockchain_time = self.vega.get_blockchain_time(in_seconds=True)
        closing = datetime.fromtimestamp(int(blockchain_time + 50))
        enactment = datetime.fromtimestamp(int(blockchain_time + 50))
        terms = builders.governance.proposal_terms(
            closing_timestamp=closing,
            enactment_timestamp=enactment,
            new_transfer=new_transfer,
        )
        rationale = builders.governance.proposal_rational(
            description="fuzzed-proposal",
            title="fuzzed-proposal",
        )
        proposal_submission = builders.commands.commands.proposal_submission(
            reference=str(uuid4()), terms=terms, rationale=rationale
        )
        self.vega.submit_proposal(
            key_name=self.key_name,
            proposal_submission=proposal_submission,
            approve_proposal=True,
            wallet_name=self.wallet_name,
        )

    def _pick_source_type(self):
        return self.random_state.choice(
            list(self.SOURCE_TYPES.keys()), p=list(self.SOURCE_TYPES.values())
        )

    def _pick_transfer_type(self):
        return self.random_state.choice(
            list(self.TRANSFER_TYPES.keys()), p=list(self.TRANSFER_TYPES.values())
        )

    def _pick_source(self, source_type, markets):
        if self._valid():
            if source_type in [
                vega_protos.vega.ACCOUNT_TYPE_GLOBAL_INSURANCE,
                vega_protos.vega.ACCOUNT_TYPE_NETWORK_TREASURY,
            ]:
                return None
        return self.random_state.choice(markets + [None])

    def _pick_destination_type(self, one_off):
        if self._valid():
            if one_off:
                return self.random_state.choice(
                    [
                        vega_protos.vega.ACCOUNT_TYPE_INSURANCE,
                        vega_protos.vega.ACCOUNT_TYPE_GENERAL,
                        vega_protos.vega.ACCOUNT_TYPE_GLOBAL_INSURANCE,
                    ]
                )
        return self.random_state.choice(
            list(self.DESTINATION_TYPES.keys()), p=list(self.DESTINATION_TYPES.values())
        )

    def _pick_kind(self, destination_type, vega_state):
        if self.valid:
            if destination_type in []:
                return self._pick_one_off()
            else:
                return self._pick_recurring_transfer(self, destination_type, vega_state)

    def _pick_one_off(self, one_off):
        if self._valid():
            if one_off:
                return builders.governance.one_off_transfer()
            else:
                return None
        return self.random_state.choice([builders.governance.one_off_transfer(), None])

    def _pick_dispatch_metric(self, destination_type):
        if self._valid():
            if destination_type == vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_PAID_FEES:
                return vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_PAID
            if (
                destination_type
                == vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_RECEIVED_FEES
            ):
                return vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_RECEIVED
            if (
                destination_type
                == vega_protos.vega.ACCOUNT_TYPE_REWARD_LP_RECEIVED_FEES
            ):
                return vega_protos.vega.DISPATCH_METRIC_LP_FEES_RECEIVED
            if (
                destination_type
                == vega_protos.vega.ACCOUNT_TYPE_REWARD_MARKET_PROPOSERS
            ):
                return vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE
            if (
                destination_type
                == vega_protos.vega.ACCOUNT_TYPE_REWARD_AVERAGE_POSITION
            ):
                return vega_protos.vega.DISPATCH_METRIC_AVERAGE_POSITION
            if destination_type == vega_protos.vega.ACCOUNT_TYPE_REWARD_RELATIVE_RETURN:
                return vega_protos.vega.DISPATCH_METRIC_RELATIVE_RETURN
            if (
                destination_type
                == vega_protos.vega.ACCOUNT_TYPE_REWARD_RETURN_VOLATILITY
            ):
                return vega_protos.vega.DISPATCH_METRIC_RETURN_VOLATILITY
            if (
                destination_type
                == vega_protos.vega.ACCOUNT_TYPE_REWARD_VALIDATOR_RANKING
            ):
                return vega_protos.vega.DISPATCH_METRIC_VALIDATOR_RANKING
        else:
            return self.random_state.choice(list(self.DISPATCH_METRICS.keys()))

    def _pick_recurring(self, one_off, destination_type, vega_state):
        # Pick transfer durations
        current_epoch = self.vega.statistics().epoch_seq
        start_epoch = self._pick_start_epoch(current_epoch)
        end_epoch = self._pick_end_epoch(start_epoch)

        # Pick driving parameters
        entity_scope = self.random_state.choice(
            list(self.ENTITY_SCOPE.keys()), p=list(self.ENTITY_SCOPE.values())
        )
        dispatch_metric = self.random_state.choice(self.DISPATCH_METRICS)
        distribution_strategy = self.random_state.choice(
            list(self.DISTRIBUTION_STRATEGIES.keys()),
            p=list(self.DISTRIBUTION_STRATEGIES.values()),
        )

        dispatch_strategy = builders.vega.dispatch_strategy(
            metric=dispatch_metric,
            asset_for_metric=self._pick_asset_for_metric(
                dispatch_metric=dispatch_metric
            ),
            entity_scope=entity_scope,
            window_length=self._pick_window_length(dispatch_metric=dispatch_metric),
            lock_period=self._pick_lock_period(),
            distribution_strategy=distribution_strategy,
            markets=None,
            individual_scope=self._pick_individual_scope(entity_scope=entity_scope),
            team_scope=None,
            n_top_performers=self._pick_n_top_performers(entity_scope=entity_scope),
            notional_time_weighted_average_position_requirement=self._pick_notional_time_weighted_average_position_requirement(),
            rank_table=self._pick_rank_table(
                distribution_strategy=distribution_strategy
            ),
        )
        recurring_transfer = builders.governance.recurring_transfer(
            start_epoch=start_epoch,
            end_epoch=end_epoch,
            dispatch_strategy=dispatch_strategy,
        )

        if self._valid():
            if one_off:
                return None
            else:
                return recurring_transfer
        return self.random_state.choice([recurring_transfer, None])
