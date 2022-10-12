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
    FFN_Q,
)
from vega_sim.reinforcement.helpers import apply_funcs, to_torch, toggle
from vega_sim.reinforcement.la_market_state import LAMarketState, states_to_sarsa

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
class Action(AbstractAction):
    buy: bool
    sell: bool
    volume: float


@dataclass
class SoftActionWithVol:
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


class LearningAgentWithVol(LearningAgent):
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
        inventory_penalty: float = 0.05,
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

        # Dimensions of state and action
        self.num_levels = num_levels
        self.state_dim = 6 + 4 * self.num_levels  # from MarketState
        action_discrete_dim = 3

        # NN and optimizer for Q func
        self.q_func = FFN_Q(
            state_dim=self.state_dim,
        )
        self.optimizer_q = torch.optim.RMSprop(self.q_func.parameters(), lr=0.001)

        # NN for policy and its optimizer
        self.policy_discr = FFN(
            sizes=[self.state_dim, 1024, 1024, 1024, action_discrete_dim],
            activation=nn.Tanh,
            output_activation=Softmax,
        )  # this network decides whether to buy/sell/do nothing

        # NN for volume
        self.policy_volume = FFN_Params_Normal(
            n_in=self.state_dim,
            n_distr=2,
            hidden_sizes=[32],
        )

        # And the optimizer needs to include this too
        self.optimizer_pol = torch.optim.RMSprop(
            list(self.policy_volume.parameters())
            + list(self.policy_discr.parameters()),
            lr=0.001,
        )

    def move_to_device(self):
        self.q_func.to(self.device)
        self.policy_volume.to(self.device)
        self.policy_discr.to(self.device)

    def move_to_cpu(self):
        self.q_func.to("cpu")
        self.policy_volume.to("cpu")
        self.policy_discr.to("cpu")

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

        self.memory["action_volume"].append([action.volume])
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
        dataset_action_volume = apply_funcs(
            value=self.memory["action_volume"], funcs=(np.array, to_torch_device)
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
                dataset_action_volume,
                dataset_reward,
                dataset_next_state,
            )
        )
        dataloader = torch.utils.data.DataLoader(
            dataset, batch_size=batch_size, shuffle=True
        )
        return dataloader

    def empty_action(self) -> AbstractAction:
        return Action(True, True, 0.0)

    def step(self, vega_state: VegaState):
        learning_state = self.state(self.vega)
        self.step_num += 1
        self.latest_action = self._step(learning_state)
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
                    volume=self.latest_action.volume,
                    wait=False,
                    fill_or_kill=False,
                )
            except Exception as e:
                print(e)

    def _step(self, vega_state: LAMarketState) -> Action:
        # learned policy
        state = vega_state.to_array().reshape(1, -1)  # adding batch_dimension
        state = torch.from_numpy(state).float()  # .to(self.device)

        with torch.no_grad():
            soft_action = self.sample_action(state=state, sim=True)
        choice = int(soft_action.c.item())
        if choice == 0:  # choice = 0 --> sell
            volume = soft_action.volume_sell.item() * 10 ** (-self.position_decimals)
        elif choice == 1:  # choice = 1 --> buy
            volume = soft_action.volume_buy.item() * 10 ** (-self.position_decimals)
        else:
            volume = 0  # choice=2, hence do nothing, hence volume is irrelevant
        return Action(buy=choice == 0, sell=choice == 1, volume=volume)

    def _step_heuristic(self, vega_state: LAMarketState) -> Action:
        volume = 0.0
        if (
            vega_state.position <= 0
            and vega_state.ask_prices[0] < vega_state.next_price
        ):
            choice = 0  # buy
            volume = 0.01
        elif (
            vega_state.position >= 0
            and vega_state.bid_prices[0] > vega_state.next_price
        ):
            choice = 1  # sell
            volume = 0.01
        else:
            choice = 2  # do nothing

        return Action(buy=choice == 0, sell=choice == 1, volume=volume)

    def sample_action(
        self, state: torch.Tensor, sim: bool = True, evaluate: bool = False
    ):
        """
        Sample an action.

        Returns
        -------
        z_sell: torch.Tensor
            samples from N(0,1) used to sample volume_sell from a lognormal
        z_buy: torch.Tensor
            samples from N(0,1) used to sample volume_buy from a lognormal
        mu: torch.Tensor
            Tensor of shape (batch_size,2). Each column is mu_{sell} and mu_{buy} of lognormal
        sigma: torch.Tensor
            Tensor of shape (batch_size, 2). Each column is sigma_{sell} and sigma_{buy} of lognormal
        c: torch.Tensor
            if sim = False, c is a tensor of shape (batch_size, 3) returning the probs of {sell, buy, do nothign}
            if sim = True, c is a tensor of shape (batch_size, 1) returning the sampled action from {sell, buy, do nothing} (i.e. c is filled with values from {0,1,2})
        mu: torch.Tensor
            Tensor of shape
        sigma: torch.Tensor
            Tensor of shape
        volume_sell: torch.Tensor
            Tensor of shape
        volume_buy: torch.Tensor
            Tensor of shape
        """
        probs = self.policy_discr(
            state
        )  # this is the FFN returning probabilities for the 3 actions
        mu, sigma = self.policy_volume(
            state
        )  # this is the FFN returning statistics for volume distribution
        z_sell, volume_sell = lognorm_sample(mu=mu[:, 0], sigma=sigma[:, 0])
        z_buy, volume_buy = lognorm_sample(mu=mu[:, 1], sigma=sigma[:, 1])
        if sim:
            # We are simulating, hence we sample from discr action
            m = Categorical(probs)
            c = m.sample()
        else:
            c = probs
        if evaluate:
            c = torch.max(probs, 1, keepdim=True)[1]

        return SoftActionWithVol(
            z_sell=z_sell,
            z_buy=z_buy,
            c=c,
            mu=mu,
            sigma=sigma,
            volume_sell=volume_sell,
            volume_buy=volume_buy,
        )

    def policy_eval(
        self,
        batch_size: int,
        n_epochs: int,
    ):
        toggle(self.policy_discr, to=False)
        toggle(self.policy_volume, to=False)
        toggle(self.q_func, to=True)

        dataloader = self.create_dataloader(batch_size=batch_size)

        pbar = tqdm(total=n_epochs)
        for epoch in range(n_epochs):
            for (
                i,
                (
                    batch_state,
                    batch_action_discrete,
                    batch_action_volume,
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
                # differentiate between sell and buy volumes for the q_func
                volume_sell = batch_action_volume.clone()
                volume_sell[batch_action_discrete.ne(0)] = 0
                volume_buy = batch_action_volume.clone()
                volume_buy[batch_action_discrete.ne(1)] = 0

                pred = torch.gather(
                    self.q_func(batch_state, volume_sell, volume_buy),
                    dim=1,
                    index=batch_action_discrete,
                )

                with torch.no_grad():
                    v = self.v_func(batch_next_state)
                    target = (
                        batch_reward
                        + (1 - next_state_terminal.mean(1, keepdim=True))
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

    def v_func(self, state, n_mc=1000):
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
        batch_size = state.shape[0]
        # MONTE CARLO to approximate expectations
        state_mc = state.repeat(n_mc, 1)
        soft_action = self.sample_action(state_mc, sim=False)
        z_sell, z_buy, c, mu, sigma, volume_sell, volume_buy = soft_action.unravel()

        q = self.q_func(state_mc, volume_sell, volume_buy)
        v = c[:, 0] * (
            q[:, 0]
            - self.coefH_discr * torch.log(c[:, 0])
            - self.coefH_cont
            * lognorm_logprob(z=z_sell, mu=mu[:, 0], sigma=sigma[:, 0])
        )
        v += c[:, 1] * (
            q[:, 1]
            - self.coefH_discr * torch.log(c[:, 1])
            - self.coefH_cont * lognorm_logprob(z=z_buy, mu=mu[:, 1], sigma=sigma[:, 1])
        )
        v += c[:, 2] * (q[:, 2] - self.coefH_discr * torch.log(c[:, 2]))
        v = v.reshape(n_mc, batch_size, -1).mean(0)  # average of Monte Carlo samples
        self.q_func.train()
        return v

    def D_KL(self, state, n_mc):
        """
        KL divergence between pi(.|x) and the unnormalised density exp(Q(x,.)),
        where pi(.|x) is a LogNormal distribution
        """
        batch_size = state.shape[0]
        # MONTE CARLO to approximate expectations
        state_mc = state.repeat(n_mc, 1)
        soft_action = self.sample_action(state_mc, sim=False)
        z_sell, z_buy, c, mu, sigma, volume_sell, volume_buy = soft_action.unravel()

        q = self.q_func(state_mc, volume_sell, volume_buy)
        d_kl = c[:, 0] * (
            self.coefH_discr * torch.log(c[:, 0])
            + self.coefH_cont
            * lognorm_logprob(z=z_sell, mu=mu[:, 0], sigma=sigma[:, 0])
            - q[:, 0]
        )
        d_kl += c[:, 1] * (
            self.coefH_discr * torch.log(c[:, 1])
            + self.coefH_cont * lognorm_logprob(z=z_buy, mu=mu[:, 1], sigma=sigma[:, 1])
            - q[:, 1]
        )
        d_kl += c[:, 2] * (self.coefH_discr * torch.log(c[:, 2]) - q[:, 2])

        # regularisation. Since the action space is not compact, then Q(x,a) could potentially explode.
        # To avoid this, I force the parameters of the lognormal not to be very far away from (0,1)
        reg = c[:, 0] * reg_policy(z_sell, mu=mu[:, 0], sigma=sigma[:, 0])
        reg += c[:, 1] * reg_policy(z_buy, mu=mu[:, 1], sigma=sigma[:, 1])

        d_kl = (
            d_kl.reshape(n_mc, batch_size, -1).mean(0).mean()
            + 0.5 * self.coefH_cont * reg.reshape(n_mc, batch_size, -1).mean(0).mean()
        )  # Average of Monte Carlo samples. Doing one extra unnecessary step for clarity

        return d_kl

    def policy_improvement(self, batch_size: int, n_epochs: int):
        toggle(self.policy_discr, to=True)
        toggle(self.policy_volume, to=True)
        toggle(self.q_func, to=False)

        dataloader = self.create_dataloader(batch_size=batch_size)

        pbar = tqdm(total=n_epochs)
        for epoch in range(n_epochs):
            for i, (batch_state, _, _, _, _) in enumerate(dataloader):
                self.optimizer_pol.zero_grad()
                d_kl = self.D_KL(batch_state, n_mc=100).mean()
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
        self.coefH_discr = max(self.coefH_discr * 0.99, 0.05)
        self.coefH_cont = max(self.coefH_cont * 0.99, 0.05)
        self.lerningIteration += 1
        return 0

    def save(self, results_dir: str):
        filename = os.path.join(results_dir, "agent.pth.tar")
        d = {
            "losses": self.losses,
            "q": self.q_func.state_dict(),
            "policy_discr": self.policy_discr.state_dict(),
            "policy_volume": self.policy_volume.state_dict(),
            "iteration": self.lerningIteration,
            "coefH_discr": self.coefH_discr,
            "coefH_cont": self.coefH_cont,
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
        self.policy_volume.load_state_dict(d["policy_volume"])
        self.lerningIteration = d["iteration"]
        self.coefH_discr = d["coefH_discr"]
        self.coefH_cont = d["coefH_cont"]

        filename_for_memory = os.path.join(results_dir, "memory.pickle")
        with open(filename_for_memory, "rb") as f:
            memory = pickle.load(f)
        self.memory = memory
