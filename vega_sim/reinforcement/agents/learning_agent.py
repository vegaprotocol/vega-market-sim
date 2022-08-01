from abc import abstractmethod
from dataclasses import dataclass
import numpy as np
from collections import namedtuple
from typing import List, Tuple

import torch


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
    next_price: float

    def to_array(self):
        data = (
            [
                self.position,
                self.margin_balance,
                self.general_balance,
                int(self.market_in_auction),
                int(self.market_active),
                self.trading_fee,
                self.next_price,
            ]
            + self.bid_prices
            + self.ask_prices
            + self.bid_volumes
            + self.ask_volumes
        )
        arr = np.nan_to_num(np.array(data))
        return arr


@dataclass
class Action:
    buy: bool
    sell: bool
    volume: float


@dataclass
class SoftAction:
    z_sell: torch.Tensor  # sample from N(mu_sell, sigma_sell) to generate selling volume from lognormal
    z_buy: torch.Tensor  # sample from N(mu_buy, sigma_buy) to generate buying volume from lognormal
    c: torch.Tensor  # sell / buy / do nothing probabilities if training. If simulating, value in {0,1,2} indicating sampled action
    mu: torch.Tensor  # [mu_sell, mu_buy]
    sigma: torch.Tensor  # [sigma_sell, sigma_buy]
    volume_sell: torch.Tensor  # sampled volume sell
    volume_buy: torch.Tensor  # sampled volume buy

    def unravel(self):
        return (
            self.z_sell,
            self.z_buy,
            self.c,
            self.mu,
            self.sigma,
            self.volume_sell,
            self.volume_buy,
        )


def states_to_sarsa(
    states: List[Tuple[MarketState, Action]]
) -> List[Tuple[MarketState, Action, float, MarketState, Action]]:
    res = []
    for i in range(len(states)):
        pres_state = states[i]
        next_state = states[i + 1] if i < len(states) - 1 else np.nan  # None
        prev_state = states[i - 1] if i > 0 else np.nan  # None
        if pres_state[0].margin_balance + pres_state[0].general_balance <= 0:
            reward = -10
            res.append(
                (
                    pres_state[0],
                    pres_state[1],
                    reward,
                    next_state[0] if next_state is not np.nan else np.nan,
                    next_state[1] if next_state is not np.nan else np.nan,
                )
            )
            break
        reward = (
            (pres_state[0].general_balance + pres_state[0].margin_balance)
            - (prev_state[0].general_balance + prev_state[0].margin_balance)
            if prev_state is not np.nan
            else 0
        )
        if next_state is not np.nan:
            res.append(
                (pres_state[0], pres_state[1], reward, next_state[0], next_state[1])
            )
        else:
            res[-1] = (res[-1][0], res[-1][1], reward + res[-1][2], np.nan, np.nan)
    return res


class LearningAgent(StateAgentWithWallet):
    def __init__(self, wallet_name: str, wallet_pass: str, *args, **kwargs):
        super().__init__(wallet_name=wallet_name, wallet_pass=wallet_pass)
        self.base_wallet_name = wallet_name

    def set_market_tag(self, tag: str):
        self.tag = tag
        self.wallet_name = self.base_wallet_name + str(tag)

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet
        super().initialise(vega=vega)
        market_name = f"BTC:DAI_{self.tag}"
        self.step_num = 0

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
        self.vega.wait_fn(2)

    @abstractmethod
    def update_memory(self, states: List[Tuple[MarketState, Action]]):
        """
        Updates memory of the agent, and removes old tuples (s,a,r,s) if memory exceeds its capacity
        """
        pass

    @abstractmethod
    def clear_memory(self):
        pass

    @abstractmethod
    def create_dataloader(self, batch_size):
        """
        creates dataset and dataloader for training.
        """
        pass

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
        book_state = self.vega.market_depth(
            self.market_id, num_levels=self.num_levels
        )  # make num_levels as a parameter?
        market_info = vega.market_info(market_id=self.market_id)
        return MarketState(
            position=position,
            margin_balance=account.margin,
            general_balance=account.general,
            market_active=market_info.state == markets_protos.Market.State.STATE_ACTIVE,
            market_in_auction=market_info.trading_mode
            == markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS,
            bid_prices=[level.price for level in book_state.buys]
            + [0] * max(0, self.num_levels - len(book_state.buys)),
            ask_prices=[level.price for level in book_state.sells]
            + [0] * max(0, self.num_levels - len(book_state.sells)),
            bid_volumes=[level.volume for level in book_state.buys]
            + [0] * max(0, self.num_levels - len(book_state.buys)),
            ask_volumes=[level.volume for level in book_state.sells]
            + [0] * max(0, self.num_levels - len(book_state.sells)),
            trading_fee=0,
            next_price=self.price_process[self.step_num + 1]
            if self.price_process is not None
            and len(self.price_process) > self.step_num + 1
            else np.nan,
        )

    @abstractmethod
    def step(self, vega_state: VegaState, random: bool = False):
        pass

    def policy_eval(
        self,
        batch_size: int,
        n_epochs: int,
    ):
        pass

    def policy_improvement(self, batch_size: int, n_epochs: int):
        pass

    def save(self, results_dir: str):
        pass

    def load(self, results_dir: str):
        pass
