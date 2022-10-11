from abc import abstractmethod
from dataclasses import dataclass
import numpy as np
from collections import namedtuple, defaultdict
from typing import List, Tuple

from functools import partial
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.distributions.categorical import Categorical

from vega_sim.reinforcement.networks import (
    Softmax,
    FFN,
    FFN_Params_Normal,
    FFN_Q,
)
from vega_sim.reinforcement.helpers import apply_funcs, to_torch, toggle
from vega_sim.reinforcement.la_market_state import LAMarketState
from vega_sim.reinforcement.la_market_state import AbstractAction
from vega_sim.reinforcement.la_market_state import states_to_sarsa

from vega_sim.reinforcement.distributions import (
    lognorm_sample,
    lognorm_logprob,
    reg_policy,
)

from vega_sim.api.helpers import num_from_padded_int

from vega_sim.environment.agent import Agent
from vega_sim.environment import VegaState
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import markets as markets_protos

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Send selling/buying MOs to hit LP orders
WALLET = WalletConfig("learner", "learner")


def state_fn(
    service: VegaServiceNull,
    agents: List[Agent],
    state_values=None,
) -> Tuple[LAMarketState, AbstractAction]:
    learner = [a for a in agents if isinstance(a, LearningAgent)][0]
    return (learner.latest_state, learner.latest_action)


class LearningAgent(StateAgentWithWallet):
    @abstractmethod
    def __init__(
        self,
        device: str,
        logfile_pol_imp: str,
        logfile_pol_eval: str,
        logfile_pnl: str,
        discount_factor: float,
        num_levels: int,
        wallet_name: str,
        wallet_pass: str,
        market_name: str,
        initial_balance: int,
        position_decimals: int,
        inventory_penalty: float = 0.0,
    ):
        super().__init__(wallet_name=wallet_name, wallet_pass=wallet_pass)

        self.step_num = 0
        self.latest_state = None
        self.latest_action = None
        self.device = device
        self.discount_factor = discount_factor
        self.initial_balance = initial_balance

        self.memory = defaultdict(list)
        self.memory_capacity = 100_000

        # Coefficients for regularisation
        self.coefH_discr = 1.0
        self.coefH_cont = 0.01
        # losses logger
        self.losses = defaultdict(list)
        # logfile
        self.logfile_pol_imp = logfile_pol_imp
        self.logfile_pol_eval = logfile_pol_eval
        self.logfile_pnl = logfile_pnl

        self.lerningIteration = 0
        self.market_name = market_name
        self.position_decimals = position_decimals
        self.inventory_penalty = inventory_penalty

    def set_market_tag(self, tag: str):
        self.tag = tag

    @abstractmethod
    def move_to_device(self):
        pass

    @abstractmethod
    def move_to_cpu(self):
        pass

    def initialise(self, vega: VegaServiceNull):
        # Initialise wallet
        super().initialise(vega=vega)
        self.step_num = 0
        market_name = self.market_name + f"_{self.tag}"

        # Get market id
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == market_name
        ][0]
        # Get asset id
        self.tdai_id = self.vega.find_asset_id(symbol=f"tDAI_{self.tag}")
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=self.tdai_id,
            amount=self.initial_balance,
        )
        self.vega.wait_fn(2)

    def _update_memory(
        self,
        state: LAMarketState,
        action: AbstractAction,
        reward: float,
        next_state: LAMarketState,
    ):
        pass

    def update_memory(self, states: List[Tuple[LAMarketState, AbstractAction]]):
        """
        Updates memory of the agent, and removes old tuples (s,a,r,s) if memory exceeds its capacity
        """
        for res in states_to_sarsa(states, inventory_penalty=self.inventory_penalty):
            self._update_memory(res[0], res[1], res[2], res[3])
        # remove old tuples if memory exceeds its capaciy
        for key, value in self.memory.items():
            if len(self.memory[key]) > self.memory_capacity:
                first_n = len(self.memory[key]) - self.memory_capacity
                del self.memory[key][:first_n]
        return 0

    def clear_memory(self):
        for key in self.memory.keys():
            self.memory[key].clear()

    @abstractmethod
    def create_dataloader(self, batch_size):
        """
        creates dataset and dataloader for training.
        """
        pass

    def state(self, vega: VegaServiceNull) -> LAMarketState:
        position = self.vega.positions_by_market(self.wallet_name, self.market_id)

        position = position[0].open_volume if position else 0
        account = self.vega.party_account(
            wallet_name=self.wallet_name,
            asset_id=self.tdai_id,
            market_id=self.market_id,
        )
        book_state = self.vega.market_depth(
            self.market_id, num_levels=self.num_levels
        )  # make num_levels as a parameter?

        market_info = vega.market_info(market_id=self.market_id)
        fee = (
            float(market_info.fees.factors.liquidity_fee)
            + float(market_info.fees.factors.maker_fee)
            + float(market_info.fees.factors.infrastructure_fee)
        )
        init_price = self.price_process[0]
        next_price = (
            self.price_process[self.step_num + 1]
            if self.price_process is not None
            and len(self.price_process) > self.step_num + 1
            else np.nan
        )
        next_price /= init_price
        bid_prices = [level.price / init_price for level in book_state.buys] + [
            0
        ] * max(0, self.num_levels - len(book_state.buys))
        ask_prices = [level.price / init_price for level in book_state.sells] + [
            0
        ] * max(0, self.num_levels - len(book_state.sells))

        return LAMarketState(
            step=self.step_num,
            position=position,
            full_balance=(account.margin + account.general) / self.initial_balance,
            market_in_auction=(
                not market_info.trading_mode
                == markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS
            ),
            bid_prices=bid_prices,
            ask_prices=ask_prices,
            bid_volumes=[level.volume for level in book_state.buys]
            + [0] * max(0, self.num_levels - len(book_state.buys)),
            ask_volumes=[level.volume for level in book_state.sells]
            + [0] * max(0, self.num_levels - len(book_state.sells)),
            trading_fee=fee,
            next_price=next_price,
        )

    @abstractmethod
    def empty_action(self) -> AbstractAction:
        pass

    def finalise(self):
        numTries = 3
        account = None
        for i in range(0, numTries):
            account = self.vega.party_account(
                wallet_name=self.wallet_name,
                asset_id=self.tdai_id,
                market_id=self.market_id,
            )
            self.latest_state = self.state(self.vega)
            if account.margin == 0:
                break
            self.vega.forward("1s")
            self.vega.wait_for_total_catchup()

        if account.margin > 0:
            print(
                "Market should be settled but there is still balance in margin account. What's up?"
            )

        self.latest_action = self.empty_action()
        self.step_num += 1
        # final_pnl = self.latest_state.full_balance - self.initial_balance
        final_pnl = self.latest_state.full_balance - 1.0
        with open(self.logfile_pnl, "a") as f:
            f.write("{},{:.8f}\n".format(self.lerningIteration, final_pnl))

        return super().finalise()

    @abstractmethod
    def step(self, vega_state: VegaState):
        pass

    @abstractmethod
    def save(self, results_dir: str):
        pass

    @abstractmethod
    def load(self, results_dir: str):
        pass
