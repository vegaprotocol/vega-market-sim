from dataclasses import dataclass
import numpy as np
from collections import namedtuple, defaultdict
from typing import List, Tuple
import os
from functools import partial
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.distributions.categorical import Categorical
from vega_sim.reinforcement.agents.learning_agent import AbstractAction, LearningAgent

import pickle

from vega_sim.reinforcement.networks import (
    Softmax,
    FFN,
    FFN_Params_Normal,
    FFN_fix_fol_Q,
)
from vega_sim.reinforcement.helpers import apply_funcs, to_torch, toggle
from vega_sim.reinforcement.la_market_state import LAMarketState

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


@dataclass
class Action:
    buy: bool
    sell: bool


@dataclass
class SoftActionFixVol:
    c: torch.Tensor  # sell / buy / do nothing probabilities if training. If simulating, value in {0,1,2} indicating sampled action

    def unravel(self):
        return self.c


class LearningAgentHeuristic(LearningAgent):
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
        inventory_penalty: float = 1.0,
    ):
        super().__init__(
            device=device,
            logfile_pol_imp=logfile_pol_imp,
            logfile_pol_eval=logfile_pol_eval,
            logfile_pnl=logfile_pnl,
            discount_factor=discount_factor,
            num_levels=num_levels,
            wallet_name=wallet_name,
            wallet_pass=wallet_pass,
            market_name=market_name,
            initial_balance=initial_balance,
            position_decimals=position_decimals,
            inventory_penalty=inventory_penalty,
        )
        self.volume = 10 ** (-self.position_decimals)

        # Dimensions of state and action
        self.num_levels = num_levels
        self.state_dim = 6 + 4 * self.num_levels  # from MarketState
        action_discrete_dim = 3

        # NN for Q-fun and its optimizer
        self.q_func = FFN_fix_fol_Q(state_dim=self.state_dim)
        self.optimizer_q = torch.optim.RMSprop(self.q_func.parameters(), lr=0.01)

        self.policy_discr = FFN(
            sizes=[self.state_dim, 1024, 512, action_discrete_dim],
            activation=nn.Tanh,
            output_activation=Softmax,
        )  # this network decides whether to buy/sell/do nothing
        self.optimizer_pol = torch.optim.RMSprop(
            list(self.policy_discr.parameters()), lr=0.001
        )

    def move_to_device(self):
        self.q_func.to(self.device)

    def move_to_cpu(self):
        self.q_func.to("cpu")

    def _update_memory(
        self,
        state: LAMarketState,
        action: Action,
        reward: float,
        next_state: LAMarketState,
    ):
        """
        Ensure what is the input?
        """
        self.memory["state"].append(state.to_array())
        # action_discrete = 0 if sell
        # action_discrete = 1 if buy
        # action_discrete = 2 if they do not do anything
        if action.sell:
            self.memory["action_discrete"].append([0])
        elif action.buy:
            self.memory["action_discrete"].append([1])
        else:
            self.memory["action_discrete"].append([2])

        self.memory["reward"].append([reward])
        if next_state is not np.nan:
            self.memory["next_state"].append(next_state.to_array())
        else:
            self.memory["next_state"].append(np.nan * np.ones_like(state.to_array()))

        return 0

    def create_dataloader(self, batch_size):
        """
        creates dataset and dataloader for training.
        """
        to_torch_device = partial(to_torch, device=self.device)
        dataset_state = apply_funcs(
            value=self.memory["state"], funcs=(np.stack, to_torch_device)
        )
        dataset_action_discrete = apply_funcs(
            value=self.memory["action_discrete"],
            funcs=(np.array, partial(to_torch, dtype=torch.int64, device=self.device)),
        )
        dataset_reward = apply_funcs(
            value=self.memory["reward"], funcs=(np.array, to_torch_device)
        )
        dataset_next_state = apply_funcs(
            value=self.memory["next_state"], funcs=(np.stack, to_torch_device)
        )

        dataset = torch.utils.data.TensorDataset(
            *(
                dataset_state,
                dataset_action_discrete,
                dataset_reward,
                dataset_next_state,
            )
        )
        dataloader = torch.utils.data.DataLoader(
            dataset, batch_size=batch_size, shuffle=True
        )
        return dataloader

    def empty_action(self) -> AbstractAction:
        return Action(False, False)

    def step(self, vega_state: VegaState):
        learning_state = self.state(self.vega)
        self.step_num += 1
        self.latest_action = self._step_heuristic(learning_state)
        self.latest_state = learning_state

        if learning_state.full_balance <= 0:
            return
        if learning_state.market_in_auction:
            return

        if self.latest_action.buy or self.latest_action.sell:
            try:
                self.vega.submit_market_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    side="SIDE_BUY" if self.latest_action.buy else "SIDE_SELL",
                    volume=self.volume,
                    wait=False,
                    fill_or_kill=False,
                )
            except Exception as e:
                print(e)

    def _step_heuristic(self, vega_state: LAMarketState) -> Action:
        if (
            vega_state.position <= 0
            and vega_state.ask_prices[0] < vega_state.next_price
        ):
            choice = 0  # buy
        elif (
            vega_state.position >= 0
            and vega_state.bid_prices[0] > vega_state.next_price
        ):
            choice = 1  # sell
        else:
            choice = 2  # do nothing

        return Action(buy=choice == 0, sell=choice == 1)

    def sample_action(
        self,
        state: torch.Tensor,
        sim: bool = True,
        evaluate: bool = False,
    ):
        """
        Sample an action.

        Returns
        -------
        c is a tensor of shape (batch_size, 1) returning the sampled action from {sell, buy, do nothing} (i.e. c is filled with values from {0,1,2})
        """
        probs = self.policy_discr(state)
        if sim:
            m = Categorical(probs)
            c = m.sample()
        else:
            c = probs
        if evaluate:
            c = torch.max(probs, 1, keepdim=True)[1]
        return SoftActionFixVol(c)

    def D_KL(self, state):
        """
        KL divergence between pi(.|x) and the unnormalised density exp(Q(x,.)),
        where pi(.|x) is a LogNormal distribution
        """
        c = self.sample_action(state).unravel().reshape((state.shape[0], 1))

        q = self.q_func(state, c)
        probs = self.policy_discr(state)
        d_kl = probs[0] * (self.coefH_discr * torch.log(probs[0]) - q[0])
        d_kl += probs[1] * (self.coefH_discr * torch.log(probs[1]) - q[1])
        d_kl += probs[2] * (self.coefH_discr * torch.log(probs[2]) - q[2])

        d_kl = (
            d_kl.mean()
        )  # Average of Monte Carlo samples. Doing one extra unnecessary step for clarity
        return d_kl

    def policy_improvement(self, batch_size: int, n_epochs: int):
        toggle(self.policy_discr, to=True)
        toggle(self.q_func, to=False)

        dataloader = self.create_dataloader(batch_size=batch_size)

        pbar = tqdm(total=n_epochs)
        for epoch in range(n_epochs):
            for i, (batch_state, _, _, _) in enumerate(dataloader):
                self.optimizer_pol.zero_grad()
                d_kl = self.D_KL(batch_state).mean()
                d_kl.backward()
                # nn.utils.clip_grad_norm_(self.policy_volume.parameters(), max_norm=1.)
                self.optimizer_pol.step()
            self.losses["d_kl"].append(d_kl.item())
            with open(self.logfile_pol_imp, "a") as f:
                f.write(
                    "{},{:.4f}\n".format(
                        epoch + n_epochs * self.lerningIteration, d_kl.item()
                    )
                )
            pbar.update(1)

        # update the coefficients for the next run
        self.coefH_discr = max(self.coefH_discr * 0.99, 1e-10)
        self.coefH_cont = max(self.coefH_cont * 0.99, 1e-10)
        self.lerningIteration += 1
        return 0

    def policy_eval(
        self,
        batch_size: int,
        n_epochs: int,
    ):
        toggle(self.q_func, to=True)

        dataloader = self.create_dataloader(batch_size=batch_size)

        pbar = tqdm(total=n_epochs)
        for epoch in range(n_epochs):
            for (
                i,
                (
                    batch_state,
                    batch_action_discrete,
                    batch_reward,
                    batch_next_state,
                ),
            ) in enumerate(dataloader):
                next_state_terminal = torch.isnan(
                    batch_next_state
                ).float()  # shape (batch_size, dim_state)
                batch_next_state[next_state_terminal.eq(True)] = batch_state[
                    next_state_terminal.eq(True)
                ]
                self.optimizer_q.zero_grad()

                pred = self.q_func(batch_state, batch_action_discrete)

                with torch.no_grad():
                    v = self.v_func(batch_next_state)
                    target = (
                        batch_reward
                        + (1 - next_state_terminal.float().mean(1, keepdim=True))
                        * self.discount_factor
                        * v
                    )
                loss = torch.pow(pred - target, 2).mean()
                loss.backward()
                self.optimizer_q.step()
            self.losses["q"].append(loss.item())
            # logging loss
            with open(self.logfile_pol_eval, "a") as f:
                f.write(
                    "{},{:.2e},{:.3f},{:.3f}\n".format(
                        epoch + self.lerningIteration * n_epochs,
                        loss.item(),
                        self.coefH_discr,
                        self.coefH_cont,
                    )
                )
            pbar.update(1)

        return 0

    def v_func(self, state):
        """
        v(x) = E[q(x,A)] = E[q(x,A)|C=0]p(C=0) + E[q(x,A)|C=1]p(C=1) + E[q(x)|C=2]p(C=2)

        if C==0 --> sell,
        if C==1 --> buy,
        if C==2 --> does nothing,
        Parameters
        ----------
        state: torch.Tensor
            State. Tensor of shape (batch_size,
        n_mc: torch.Tensor
            Number of Monte Carlo samples to calculate
        """

        c = self.sample_action(state).unravel().reshape((state.shape[0], 1))
        q = self.q_func(state, c)

        probs = self.policy_discr(state)
        v = probs[0] * (q[0] - self.coefH_discr * torch.log(probs[0]))
        v += probs[1] * (q[1] - self.coefH_discr * torch.log(probs[1]))
        v += probs[2] * (q[2] - self.coefH_discr * torch.log(probs[2]))
        self.q_func.train()
        return v

    def save(self, results_dir: str):
        filename = os.path.join(results_dir, "agent.pth.tar")
        d = {
            "losses": self.losses,
            "q": self.q_func.state_dict(),
            "policy_discr": self.policy_discr.state_dict(),
            "iteration": self.lerningIteration,
            "coefH_discr": self.coefH_discr,
        }
        torch.save(d, filename)

        filename_for_memory = os.path.join(results_dir, "memory.pickle")
        with open(filename_for_memory, "wb") as f:
            pickle.dump(self.memory, f)

    def load(self, results_dir: str):
        filename = os.path.join(results_dir, "agent.pth.tar")
        d = torch.load(filename, map_location="cpu")
        self.q_func.load_state_dict(d["q"])
        self.policy_discr.load_state_dict(d["policy_discr"])

        self.lerningIteration = d["iteration"]
        self.coefH_discr = d["coefH_discr"]

        filename_for_memory = os.path.join(results_dir, "memory.pickle")
        with open(filename_for_memory, "rb") as f:
            memory = pickle.load(f)
        self.memory = memory
