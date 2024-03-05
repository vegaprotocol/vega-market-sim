import logging
import copy
import os
from typing import Optional, Dict, List, Iterable

import pandas as pd
from numpy import array
from numpy.random import RandomState
from datetime import datetime
from typing import NamedTuple

import vega_sim.proto.vega as vega_protos
from vega_sim.api.market import MarketConfig, Successor
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import markets as markets_protos
from vega_sim.service import (
    VegaService,
    PeggedOrder,
    MarketStateUpdateType,
)
from vega_sim.api.governance import ProposalNotAcceptedError
from requests.exceptions import HTTPError

import vega_sim.builders as builders

from uuid import uuid4

import vega_sim.scenario.fuzzed_markets.fuzzers as fuzzers


class FuzzingAgent(StateAgentWithWallet):
    NAME_BASE = "fuzzing_agent"

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

        submissions = []
        for _ in range(50):
            submission = self.create_fuzzed_submission(vega_state)
            if submission is None:
                continue
            if self.random_state.rand() < 0.1:
                submissions.append(submission)
            else:
                try:
                    self.vega.submit_transaction(
                        key_name=self.key_name,
                        wallet_name=self.wallet_name,
                        transaction=submission,
                        transaction_type="order_submission",
                    )
                except HTTPError:
                    continue
                except AttributeError as e:
                    raise e
        amendments = []
        for _ in range(25):
            amendment = self.create_fuzzed_amendment(vega_state)
            if amendment is None:
                continue
            if self.random_state.rand() < 0.1:
                amendments.append(amendment)
            else:
                try:
                    self.vega.submit_transaction(
                        key_name=self.key_name,
                        wallet_name=self.wallet_name,
                        transaction=amendment,
                        transaction_type="order_amendment",
                    )
                except HTTPError:
                    continue
        cancellations = []
        for _ in range(0):
            cancellation = self.create_fuzzed_cancellation(vega_state)
            if cancellation is None:
                continue
            if self.random_state.rand() < 0.1:
                cancellations.append(cancellation)
            else:
                try:
                    self.vega.submit_transaction(
                        key_name=self.key_name,
                        wallet_name=self.wallet_name,
                        transaction=cancellation,
                        transaction_type="order_cancellation",
                    )
                except HTTPError:
                    continue
        stop_orders_submissions = []
        for _ in range(15):
            stop_orders_submission = self.create_fuzzed_stop_orders_submission(
                vega_state
            )
            if stop_orders_submission is None:
                continue
            if self.random_state.rand() < 0.1:
                stop_orders_submissions.append(stop_orders_submission)
            else:
                try:
                    self.vega.submit_transaction(
                        key_name=self.key_name,
                        wallet_name=self.wallet_name,
                        transaction=stop_orders_submission,
                        transaction_type="stop_orders_submission",
                    )
                except HTTPError:
                    continue
        try:
            self.vega.submit_instructions(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                submissions=submissions,
                amendments=amendments,
                cancellations=cancellations,
                stop_orders_submission=stop_orders_submissions,
            )
        except HTTPError:
            pass
        try:
            self.fuzz_isolated_margin_state()
        except HTTPError:
            pass

    def fuzz_isolated_margin_state(self):
        if self.random_state.random() > 0.95:
            try:
                self.vega.update_margin_mode(
                    key_name=self.key_name,
                    wallet_name=self.wallet_name,
                    market_id=self.market_id,
                    margin_mode=self.random_state.choice(
                        ["MODE_CROSS_MARGIN", "MODE_ISOLATED_MARGIN"]
                    ),
                    margin_factor=self.random_state.random(),
                )
            except HTTPError:
                pass

    def create_fuzzed_cancellation(self, vega_state):
        order_id = self._select_order_id()

        return self.vega.build_order_cancellation(
            order_id=order_id,
            # market_id=self.market_id,
        )

    def create_fuzzed_amendment(self, vega_state):
        order_id = self._select_order_id()
        try:
            order_amendment = fuzzers.fuzz_order_amendment(
                vega=self.vega, rs=self.random_state, bias=1.0
            )
            if order_id is not None:
                setattr(order_amendment, "order_id", order_id)
            return order_amendment
        except builders.exceptions.VegaProtoValueError as e:
            return None

    def create_fuzzed_submission(self, vega_state):
        try:
            return fuzzers.fuzz_order_submission(
                vega=self.vega, rs=self.random_state, bias=1.0
            )
        except builders.exceptions.VegaProtoValueError:
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
        except builders.exceptions.VegaProtoValueError:
            return None

    def create_fuzzed_stop_orders_setup(self, vega_state):
        try:
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
        except builders.exceptions.VegaProtoValueError:
            return None

    def _select_order_id(self):
        if self.live_orders != {}:
            order_key = self.random_state.choice(list(self.live_orders.keys()))
            order = self.live_orders.get(order_key)
            return order.id if order is not None else None
        else:
            return None


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
                    fill_or_kill=False,
                    side=self.side,
                    volume=size,
                    wait=False,
                )
            except Exception as e:
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
        probability_cancel: float = 0.01,
    ):
        super().__init__(key_name, tag, wallet_name, state_update_freq)

        self.market_name = market_name
        self.asset_name = asset_name

        self.commitment_factor_min = commitment_factor_min
        self.commitment_factor_max = commitment_factor_max
        self.probability_cancel = probability_cancel
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
        if self.random_state.random() < self.probability_cancel:
            self.vega.cancel_liquidity(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                market_id=self.market_id,
            )
            return

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
            except (HTTPError, builders.exceptions.VegaProtoValueError):
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
        except (HTTPError, builders.exceptions.VegaProtoValueError):
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


class PerpProductOptions(NamedTuple):
    funding_payment_frequency_in_seconds: Optional[int]
    margin_funding_factor: Optional[float]
    interest_rate: Optional[float]
    clamp_lower_bound: Optional[float]
    clamp_upper_bound: Optional[float]


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
        perp_settlement_data_generator: Optional[Iterable[float]] = None,
        perp_sample_settlement_every_n_steps: int = 10,
        perp_options: Optional[PerpProductOptions] = None,
        perp_close_on_finalise: bool = True,
        fuzz_market_configuration: bool = False,
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

        if self.market_config.is_perp() and perp_settlement_data_generator == None:
            raise ValueError(
                "'perp_settlement_data_generator' must be supplied when 'market_config'"
                " indicates a perp market"
            )

        self.settlement_price = settlement_price
        self.needs_to_update_markets = False
        self.stake_key = stake_key
        self.perp_options = perp_options
        self.perp_close_at_settlement_price = perp_close_on_finalise
        self.current_step = 0
        self.prev_perp_settlement_data = None
        self.curr_perp_settlement_data = None
        self.perp_settlement_data_generator = perp_settlement_data_generator
        self.perp_sample_settlement_every_n_steps = perp_sample_settlement_every_n_steps

        self.fuzz_market_configuration = fuzz_market_configuration

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
                asset=self.vega.find_asset_id(symbol="VOTE", enabled=True),
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

    def _set_product_variables(self, mkt_config: MarketConfig):
        if mkt_config.is_future():
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
        if mkt_config.is_perp():
            mkt_config.set("instrument.perpetual.settlement_asset", self.asset_id)
            mkt_config.set("instrument.perpetual.quote_name", self.asset_name)
            mkt_config.set("instrument.perpetual.number_decimal_places", self.asset_dp)
            mkt_config.set(
                "instrument.perpetual.settlement_key",
                self.vega.wallet.public_key(
                    wallet_name=self.termination_wallet_name,
                    name=self._get_termination_key_name(),
                ),
            )
            if self.perp_options != None:
                if self.perp_options.funding_payment_frequency_in_seconds != None:
                    mkt_config.set(
                        "instrument.perpetual.funding_payment_frequency_in_seconds"
                    )
                if self.perp_options.margin_funding_factor != None:
                    mkt_config.set(
                        "instrument.perpetual.margin_funding_factor",
                        self.perp_options.margin_funding_factor,
                    )
                if self.perp_options.interest_rate != None:
                    mkt_config.set(
                        "instrument.perpetual.interest_rate",
                        self.perp_options.interest_rate,
                    )
                if self.perp_options.clamp_lower_bound != None:
                    mkt_config.set(
                        "instrument.perpetual.clamp_lower_bound",
                        self.perp_options.clamp_lower_bound,
                    )
                if self.perp_options.clamp_upper_bound != None:
                    mkt_config.set(
                        "instrument.perpetual.clamp_upper_bound",
                        self.perp_options.clamp_upper_bound,
                    )

    def _fuzz_market_variables(self, mkt_config: MarketConfig):
        # Fuzz price and position decimals
        mkt_config.decimal_places = self.random_state.randint(0, 5)
        mkt_config.position_decimal_places = self.random_state.randint(-5, 5)
        # Fuzz price monitoring parameters
        mkt_config.price_monitoring_parameters.triggers = [
            {
                "horizon": int(self.random_state.lognormal(mean=8, sigma=0.5)),
                "probability": self.random_state.uniform(0.9, 1),
                "auction_extension": int(
                    self.random_state.lognormal(mean=5, sigma=0.8)
                ),
            }
            for _ in range(self.random_state.randint(5))
        ]
        # Fuzz liquidity monitoring parameters
        mkt_config.liquidity_monitoring_parameters.target_stake_parameters.time_window = self.random_state.randint(
            0, 3600
        )
        mkt_config.liquidity_monitoring_parameters.target_stake_parameters.scaling_factor = self.random_state.uniform(
            0, 1
        )
        mkt_config.liquidity_monitoring_parameters.triggering_ratio = (
            self.random_state.uniform(0, 1)
        )
        mkt_config.liquidity_monitoring_parameters.auction_extension = (
            self.random_state.randint(0, 300)
        )
        # Fuzz risk model parameters
        mkt_config.log_normal.params.mu = self.random_state.uniform(-1e-6, 1e-6)
        mkt_config.log_normal.params.r = self.random_state.uniform(-1, 1)
        mkt_config.log_normal.params.sigma = self.random_state.uniform(-1e-3, 50)
        mkt_config.log_normal.risk_aversion_parameter = self.random_state.uniform(
            1e-8, 0.1
        )
        mkt_config.log_normal.tau = self.random_state.uniform(1e-8, 1)
        # Fuzz liquidity sla parameters
        mkt_config.liquidity_sla_parameters.price_range = self.random_state.uniform(
            0, 20
        )
        mkt_config.liquidity_sla_parameters.commitment_min_time_fraction = (
            self.random_state.uniform(0, 1)
        )
        mkt_config.liquidity_sla_parameters.performance_hysteresis_epochs = (
            self.random_state.randint(0, 366)
        )
        mkt_config.liquidity_sla_parameters.sla_competition_factor = (
            self.random_state.uniform(0, 1)
        )
        # Fuzz liquidity fee settings
        mkt_config.liquidity_fee_settings.method = self.random_state.choice(
            vega_protos.markets.LiquidityFeeSettings.Method.values()
        )
        mkt_config.liquidity_fee_settings.fee_constant = (
            self.random_state.uniform(0, 1)
            if mkt_config.liquidity_fee_settings.method
            == vega_protos.markets.LiquidityFeeSettings.Method.METHOD_CONSTANT
            else None
        )
        # Fuzz liquidation strategy
        mkt_config.liquidation_strategy.disposal_time_step = self.random_state.randint(
            1, 3600
        )
        mkt_config.liquidation_strategy.disposal_fraction = self.random_state.uniform(
            0, 1
        )
        mkt_config.liquidation_strategy.full_disposal_size = (
            self.random_state.lognormal(mean=5, sigma=1)
        )
        mkt_config.liquidation_strategy.max_fraction_consumed = (
            self.random_state.uniform(0, 1)
        )
        # Fuzz mark price configuration
        mkt_config.mark_price_configuration.decay_weight = self.random_state.uniform(
            0, 1
        )
        mkt_config.mark_price_configuration.decay_power = self.random_state.randint(
            1, 3
        )
        mkt_config.mark_price_configuration.cash_amount = self.random_state.randint(
            0, 10000
        )
        mkt_config.mark_price_configuration.composite_price_type = (
            self.random_state.choice(vega_protos.markets.CompositePriceType.values())
        )
        mkt_config.mark_price_configuration.source_weights = (
            self.random_state.randint(0, 100, size=3)
            if mkt_config.mark_price_configuration.composite_price_type
            == vega_protos.markets.CompositePriceType.COMPOSITE_PRICE_TYPE_WEIGHTED
            else None
        )
        mkt_config.mark_price_configuration.source_staleness_tolerance = (
            self.random_state.randint(0, 100, size=3)
            if mkt_config.mark_price_configuration.composite_price_type
            == vega_protos.markets.CompositePriceType.COMPOSITE_PRICE_TYPE_WEIGHTED
            else None
        )

    def _create_latest_market(self, parent_market_id: Optional[str] = None):
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                # Add market information and asset information to market config
                mkt_config = copy.deepcopy(self.market_config)
                mkt_config.set("instrument.name", self._get_market_name())
                mkt_config.set("instrument.code", self._get_market_code())
                self._set_product_variables(mkt_config)

                # If final attempt don't fuzz configuration so we get a sensible market
                if (attempt != max_attempts - 1) and (self.fuzz_market_configuration):
                    self._fuzz_market_variables(mkt_config)

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
                self.market_id = self.vega.find_market_id(
                    name=self._get_market_name(), raise_on_missing=True
                )
                self.market_config = mkt_config
                return

            except (
                HTTPError,
                ProposalNotAcceptedError,
                builders.exceptions.VegaProtoValueError,
            ):
                continue
        logging.info("Unable to successfully propose fuzzed market.")
        self.latest_key_idx += -1
        self.needs_to_update_markets = False

    def finalise(self):
        if self.settlement_price is not None:
            if self.market_config.is_future():
                self.vega.submit_termination_and_settlement_data(
                    self._get_termination_key_name(),
                    self.settlement_price,
                    self.market_id,
                    self.termination_wallet_name,
                )
                self.vega.wait_for_total_catchup()
            if self.perp_close_at_settlement_price and self.market_config.is_perp():
                self.vega.update_market_state(
                    market_id=self.market_id,
                    proposal_key=self.key_name,
                    wallet_name=self.wallet_name,
                    market_state=MarketStateUpdateType.Terminate,
                    price=self.settlement_price,
                )
                self.vega.wait_for_total_catchup()

    def step(self, vega_state) -> None:
        self.current_step += 1
        if self.needs_to_update_markets:
            self.vega.submit_termination_and_settlement_data(
                self.old_termination_key,
                self.vega.market_data_from_feed(self.old_market_id).last_traded_price,
                self.market_id,
                self.termination_wallet_name,
            )

            self.market_id = self.vega.find_market_id(
                name=self._get_market_name(), raise_on_missing=True
            )
            for agents in self.market_agents.values():
                for agent in agents:
                    agent.market_id = self.market_id
                    agent.market_name = self._get_market_name()
            self.needs_to_update_markets = False

        # current successor market implementation requires both markets to be futures markets
        if (
            not self.market_config.is_perp()
            and self.random_state.random() < self.successor_probability
        ):
            self.old_market_id = self.market_id
            self.old_termination_key = self._get_termination_key_name()
            self.latest_key_idx += 1

            self.vega.create_key(
                wallet_name=self.termination_wallet_name,
                name=self._get_termination_key_name(),
            )

            self.needs_to_update_markets = True
            self._create_latest_market(parent_market_id=self.market_id)

        # submit perp settlement data
        if self.market_config.is_perp():
            self.prev_perp_settlement_data = self.curr_perp_settlement_data
            self.curr_perp_settlement_data = next(self.perp_settlement_data_generator)

            if (self.current_step - 1) % self.perp_sample_settlement_every_n_steps == 0:
                self.vega.submit_settlement_data(
                    settlement_key=self._get_termination_key_name(),
                    wallet_name=self.termination_wallet_name,
                    settlement_price=self.curr_perp_settlement_data,
                    market_id=self.market_id,
                )


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
                asset=self.vega.find_asset_id(symbol="VOTE", enabled=True),
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
                except (
                    HTTPError,
                    ProposalNotAcceptedError,
                    builders.exceptions.VegaProtoValueError,
                ):
                    continue
            logging.info(
                "All fuzzed UpdateReferralProgram proposals failed, submitting sensible"
                " proposal."
            )
            try:
                self._sensible_proposal()
            except ProposalNotAcceptedError:
                logging.warning("Sensible UpdateReferralProgram failed.")

    def _sensible_proposal(self):
        # Updating program requires method to get the current blockchain time. Ensure
        # datanode is synced before requesting the current blockchain time.
        self.vega.wait_for_datanode_sync()
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
                asset=self.vega.find_asset_id(symbol="VOTE", enabled=True),
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
                except (
                    HTTPError,
                    ProposalNotAcceptedError,
                    builders.exceptions.VegaProtoValueError,
                ):
                    continue
            logging.info(
                "All fuzzed UpdateVolumeDiscountProgram proposals failed, submitting sensible"
                " proposal."
            )
            try:
                # Updating program requires method to get the current blockchain time. Ensure
                # datanode is synced before requesting the current blockchain time.
                self.vega.wait_for_datanode_sync()
                self._sensible_proposal()
            except ProposalNotAcceptedError:
                logging.warning("Sensible UpdateVolumeDiscountProgram proposal failed.")

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
                fuzzed_transfer = fuzzers.fuzz_transfer(
                    vega=self.vega, rs=self.random_state, bias=self.validity_bias
                )
                # Overwrite fields which should not be fuzzed
                fuzzed_transfer.asset = self.asset_id
                fuzzed_transfer.from_account_type = (
                    vega_protos.vega.ACCOUNT_TYPE_GENERAL
                )
                self.vega.wallet.submit_transaction(
                    transaction=fuzzed_transfer,
                    key_name=self.key_name,
                    transaction_type="transfer",
                    wallet_name=self.wallet_name,
                )

            except (HTTPError, builders.exceptions.VegaProtoValueError):
                continue


class FuzzyGovernanceTransferAgent(StateAgentWithWallet):
    NAME_BASE = "fuzzy_governance_transfer_agent"

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

        self.proposals = 0
        self.accepted_proposals = 0

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
                asset=self.vega.find_asset_id(symbol="VOTE", enabled=True),
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
                fuzzed_new_transfer_configuration = (
                    fuzzers.fuzz_new_transfer_configuration(
                        vega=self.vega, rs=self.random_state, bias=self.validity_bias
                    )
                )
                # Overwrite fields which should not be fuzzed
                fuzzed_new_transfer_configuration.asset = self.asset_id
                new_transfer = builders.governance.new_transfer(
                    changes=fuzzed_new_transfer_configuration,
                )
                blockchain_time = self.vega.get_blockchain_time(in_seconds=True)
                closing = datetime.fromtimestamp(int(blockchain_time + 50))
                enactment = datetime.fromtimestamp(int(blockchain_time + 50))
                terms = builders.governance.proposal_terms(
                    closing_timestamp=closing,
                    enactment_timestamp=enactment,
                    new_transfer=new_transfer,
                    for_batch_proposal=True,
                )
                terms = builders.governance.batch_proposal_submission_terms(
                    closing_timestamp=closing, changes=[terms]
                )
                rationale = builders.governance.proposal_rational(
                    description="fuzzed-proposal",
                    title="fuzzed-proposal",
                )
                proposal_submission = (
                    builders.commands.commands.batch_proposal_submission(
                        reference=str(uuid4()), terms=terms, rationale=rationale
                    )
                )
                self.proposals += 1
                self.vega.submit_proposal(
                    key_name=self.key_name,
                    proposal_submission=proposal_submission,
                    approve_proposal=True,
                    wallet_name=self.wallet_name,
                )
                self.accepted_proposals += 1
                break
            except (
                HTTPError,
                ProposalNotAcceptedError,
                builders.exceptions.VegaProtoValueError,
            ):
                continue

    def finalise(self):
        logging.debug(
            f"Agent {self.name()} proposed"
            f" {self.accepted_proposals}/{self.proposals} valid governance transfer"
            " proposals."
        )
