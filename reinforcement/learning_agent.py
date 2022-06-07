from dataclasses import dataclass
import numpy as np
from collections import namedtuple
from typing import List
from vega_sim.api.helpers import num_from_padded_int

from vega_sim.environment import VegaState
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import markets as markets_protos

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Send selling/buying MOs to hit LP orders
WALLET = WalletConfig("learner", "learner")


@dataclass
class MarketState:
    position: float
    margin_balance: float
    general_balance: float
    market_in_auction: bool
    market_active: bool
    bid_prices: List[float]
    ask_prices: List[float]
    bid_volumes: List[float]
    ask_volumes: List[float]
    trading_fee: float


@dataclass
class Action:
    buy: bool
    sell: bool
    volume: float


class LearningAgent(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
    ):
        super().__init__(wallet_name=wallet_name, wallet_pass=wallet_pass)
        self.base_wallet_name = wallet_name

    def set_market_tag(self, tag: str):
        self.tag = tag
        self.wallet_name = self.base_wallet_name + str(tag)

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
        self.tdai_id = self.vega.find_asset_id(symbol=f"tDAI{self.tag}")
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=self.tdai_id,
            amount=100000,
        )
        self.vega.forward("10s")

    def state(self, vega: VegaServiceNull) -> MarketState:
        position = self.vega.positions_by_market(self.wallet_name, self.market_id)
        position = (
            num_from_padded_int(
                position[0].open_volume, vega.market_pos_decimals[self.market_id]
            )
            if position
            else 0
        )
        account = self.vega.party_account(
            wallet_name=self.wallet_name,
            asset_id=self.tdai_id,
            market_id=self.market_id,
        )
        book_state = self.vega.market_depth(self.market_id, num_levels=5)
        market_info = vega.market_info(market_id=self.market_id)
        return MarketState(
            position=position,
            margin_balance=account.margin,
            general_balance=account.general,
            market_active=market_info.state == markets_protos.Market.State.STATE_ACTIVE,
            market_in_auction=market_info.trading_mode
            == markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS,
            bid_prices=[level.price for level in book_state.buys],
            ask_prices=[level.price for level in book_state.sells],
            bid_volumes=[level.volume for level in book_state.buys],
            ask_volumes=[level.volume for level in book_state.sells],
            trading_fee=0,
        )

    def step(self, vega_state: VegaState):
        learning_state = self.state(self.vega)
        self.latest_action = self._step(learning_state)
        self.latest_state = learning_state

        if self.latest_action.buy or self.latest_action.sell:
            self.vega.submit_market_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                side="SIDE_BUY" if self.latest_action.buy else "SIDE_SELL",
                volume=self.latest_action.volume,
                wait=False,
                fill_or_kill=False,
            )

    def _step(self, vega_state: MarketState) -> Action:
        choice = np.random.choice([0, 1, 2])

        return Action(buy=choice == 0, sell=choice == 1, volume=1)
