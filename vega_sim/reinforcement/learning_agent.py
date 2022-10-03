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

from vega_sim.environment import VegaState
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import markets as markets_protos

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Send selling/buying MOs to hit LP orders
WALLET = WalletConfig("learner", "learner")



class LearningAgent(StateAgentWithWallet):
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
        exploitation: float, # set this to 0 for full exploration and 1 for full exploitation
    ):
        super().__init__(wallet_name=wallet_name, wallet_pass=wallet_pass)

        self.step_num = 0
        self.device = device
        self.discount_factor = discount_factor
        self.initial_balance=initial_balance

        self.memory = defaultdict(list)
        self.memory_capacity = 10000

        # Dimensions of state and action
        self.num_levels = num_levels
        self.state_dim = 7 + 4 * self.num_levels  # from MarketState
        action_discrete_dim = 3
        # Q func
        self.q_func = FFN_Q(
            state_dim=self.state_dim,
        )
        self.optimizer_q = torch.optim.RMSprop(self.q_func.parameters(), lr=0.001)
        # policy
        self.policy_volume = FFN_Params_Normal(
            n_in=self.state_dim,
            n_distr=2,
            hidden_sizes=[4096],
        )
        self.policy_discr = FFN(
            sizes=[self.state_dim, 32, action_discrete_dim],
            activation=nn.Tanh,
            output_activation=Softmax,
        )  # this network decides whether to buy/sell/do nothing
        self.optimizer_pol = torch.optim.RMSprop(
            list(self.policy_volume.parameters())
            + list(self.policy_discr.parameters()),
            lr=0.001,
        )

        # Coefficients for regularisation
        self.coefH_discr = 5.0
        self.coefH_cont = 0.5
        # losses logger
        self.losses = defaultdict(list)
        # logfile
        self.logfile_pol_imp = logfile_pol_imp
        with open(self.logfile_pol_imp, "w") as f:
                f.write("iteration,loss\n")
        self.logfile_pol_eval = logfile_pol_eval
        with open(self.logfile_pol_eval, "w") as f:
                f.write("iteration,loss\n")
        self.logfile_pnl = logfile_pnl
        with open(self.logfile_pnl, "w") as f:
                f.write("iteration,pnl\n")
        
        
        self.lerningIteration = 0
        self.market_name = market_name
        self.position_decimals = position_decimals
        if exploitation < 0 or exploitation > 1:
            raise Exception("Need 0.0 <= exploitation <= 1.0")
        self.exploitation = exploitation
        
    def set_market_tag(self, tag: str):
        self.tag = tag
        #self.wallet_name = self.base_wallet_name + str(tag)

    def move_to_device(self):
        self.q_func.to(self.device)
        self.policy_volume.to(self.device)
        self.policy_discr.to(self.device)

    def move_to_cpu(self):
        self.q_func.to("cpu")
        self.policy_volume.to("cpu")
        self.policy_discr.to("cpu")

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
        for res in states_to_sarsa(states):
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

    def create_dataloader(self, batch_size):
        """
        creates dataset and dataloader for training.
        """
        pass

    def state(self, vega: VegaServiceNull) -> LAMarketState:
        position = self.vega.positions_by_market(self.wallet_name, self.market_id)
        
        position = (
            position[0].open_volume if position else 0
        )
        account = self.vega.party_account(
            wallet_name=self.wallet_name,
            asset_id=self.tdai_id,
            market_id=self.market_id,
        )
        book_state = self.vega.market_depth(
            self.market_id, num_levels=self.num_levels
        )  # make num_levels as a parameter?

        # ext_price=self.price_process[self.step_num]
        # bid_prices=[level.price for level in book_state.buys] + [0] * max(0, self.num_levels - len(book_state.buys))
        # ask_prices=[level.price for level in book_state.sells] + [0] * max(0, self.num_levels - len(book_state.sells))
        # # if (bid_prices[0] > 0 and bid_prices[0] >= ext_price) or (ask_prices[0] > 0 and ask_prices[0] <= ext_price):
        #     print("best_buy "+str(bid_prices[0])+" ext price "+str(ext_price)+" best ask "+str(ask_prices[0]) )

        market_info = vega.market_info(market_id=self.market_id)
        return LAMarketState(
            step=self.step_num,
            position=position,
            margin_balance=account.margin,
            general_balance=account.general,
            market_in_auction=(not market_info.trading_mode
            == markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS),
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

    def empty_action(self) -> AbstractAction:
        pass

    def finalise(self):
        learning_state = self.state(self.vega)
        self.latest_action = self.empty_action()
        self.latest_state = learning_state
        self.step_num += 1
        final_pnl = learning_state.general_balance + learning_state.margin_balance - self.initial_balance
        if learning_state.margin_balance > 0:
            print("Market should be settled but there is still balance in margin account. What's up?")
        with open(self.logfile_pnl, "a") as f:
                f.write(
                    "{},{:.5f}\n".format(self.lerningIteration, final_pnl)
                )

        return super().finalise()

    
    def step(self, vega_state: VegaState):
        pass
    
    def save(self, results_dir: str):
        pass

    def load(self, results_dir: str):
        pass
