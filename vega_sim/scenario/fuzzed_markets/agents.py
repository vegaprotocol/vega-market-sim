from vega_sim.environment.agent import StateAgentWithWallet
from typing import Optional
from vega_sim.null_service import VegaServiceNull
from numpy import array
from numpy.random import RandomState
from vega_sim.proto.vega import markets as markets_protos


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

        submissions = [self.create_fuzzed_submission() for _ in range(20)]
        amendments = [self.create_fuzzed_amendment() for _ in range(10)]
        cancellations = [self.create_fuzzed_cancellation() for _ in range(1)]

        self.vega.submit_instructions(
            key_name=self.key_name,
            wallet_name=self.wallet_name,
            submissions=submissions,
            amendments=amendments,
            cancellations=cancellations,
        )

    def create_fuzzed_cancellation(self):
        order_id = self._select_order_id()

        return self.vega.create_order_cancellation(
            order_id=order_id,
            market_id=self.market_id,
        )

    def create_fuzzed_amendment(self):
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
                (
                    self.vega.get_blockchain_time()
                    + self.random_state.normal(loc=60, scale=60)
                )
                * 1e9
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

    def create_fuzzed_submission(self):
        return self.vega.create_order_submission(
            market_id=self.market_id,
            side=self.random_state.choice(
                a=["SIDE_UNSPECIFIED", "SIDE_BUY", "SIDE_SELL"],
            ),
            size=self.random_state.poisson(lam=10),
            order_type=self.random_state.choice(
                a=["TYPE_UNSPECIFIED", "TYPE_MARKET", "TYPE_LIMIT"]
            ),
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
                a=[None, self.random_state.normal(loc=self.curr_price, scale=10)]
            ),
            expires_at=int(
                (
                    self.vega.get_blockchain_time()
                    + self.random_state.normal(loc=60, scale=60)
                )
                * 1e9
            ),
            pegged_reference=self.random_state.choice(
                a=[
                    "PEGGED_REFERENCE_UNSPECIFIED",
                    "PEGGED_REFERENCE_MID",
                    "PEGGED_REFERENCE_BEST_BID",
                    "PEGGED_REFERENCE_BEST_ASK",
                ]
            ),
            pegged_offset=self.random_state.normal(loc=0, scale=10),
        )

    def _select_order_id(self):
        if self.live_orders != {}:
            order_key = self.random_state.choice(list(self.live_orders.keys()))
            self.live_orders[order_key].id
        else:
            return None


class DegenerateTrader(StateAgentWithWallet):
    NAME_BASE = "degenerate_trader"

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
    ):
        super().__init__(key_name, tag, wallet_name, state_update_freq)

        self.market_name = market_name
        self.asset_name = asset_name

        self.size_factor = size_factor
        self.side = side
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

    def step(self, vega_state):
        if (
            vega_state.market_state[self.market_id].trading_mode
            != markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS
        ):
            return
        if self.random_state.rand() > 0.05:
            return

        midprice = vega_state.market_state[self.market_id].midprice

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
            return

        if account.general > 0:
            add_to_margin = (
                account.general + account.margin
            ) * self.size_factor - account.margin
            add_to_margin = add_to_margin if add_to_margin > 0 else 0

            risk_factors = self.vega.get_risk_factors(market_id=self.market_id)
            risk_factor = (
                risk_factors.long if self.side == "SIDE_BUY" else risk_factors.short
            )

            size = add_to_margin / (midprice * risk_factor)

            self.vega.submit_market_order(
                trading_key=self.key_name,
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                side=self.side,
                volume=size,
                wait=False,
            )


class DegenerateLiquidityProvider(StateAgentWithWallet):
    NAME_BASE = "degenerate_liquidity_provider"

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
    ):
        super().__init__(key_name, tag, wallet_name, state_update_freq)

        self.market_name = market_name
        self.asset_name = asset_name

        self.commitment_factor = commitment_factor
        self.random_state = random_state if random_state is not None else RandomState()
        self.initial_asset_mint = initial_asset_mint

        self.commitment_amount = 0

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
        if self.random_state.rand() > 0.05:
            return

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

        if self.commitment_amount < self.commitment_factor * (total_balance):
            self.commitment_amount = self.commitment_factor * (total_balance)

            self.vega.submit_simple_liquidity(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                market_id=self.market_id,
                fee=0.0001,
                commitment_amount=self.commitment_amount,
                reference_buy="PEGGED_REFERENCE_BEST_BID",
                reference_sell="PEGGED_REFERENCE_BEST_ASK",
                delta_buy=0,
                delta_sell=0,
            )
