import os
import pickle
from collections import namedtuple
from dataclasses import dataclass
from functools import partial
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from torch.distributions.categorical import Categorical
from tqdm import tqdm

from vega_sim.reinforcement.helpers import apply_funcs, to_torch, toggle
from vega_sim.reinforcement.networks import FFN, FFN_fix_fol_Q, Softmax
from vega_sim.reinforcement.v2.agents.learning_agent import TorchLearningAgent
from vega_sim.reinforcement.v2.agents.puppets import (
    MarketOrderAction,
    NoAction,
    Side,
    Action,
)
from vega_sim.reinforcement.v2.states import PriceStateWithFees

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Send selling/buying MOs to hit LP orders
WALLET = WalletConfig("learner", "learner")


class LearningAgentFixedVol(TorchLearningAgent):
    def __init__(
        self,
        device: str,
        logfile_pol_imp: str,
        logfile_pol_eval: str,
        logfile_pnl: str,
        discount_factor: float,
        num_levels: int,
        inventory_penalty: float = 1.0,
    ):
        super().__init__(
            device=device,
            logfile_pol_imp=logfile_pol_imp,
            logfile_pol_eval=logfile_pol_eval,
            logfile_pnl=logfile_pnl,
            discount_factor=discount_factor,
            inventory_penalty=inventory_penalty,
        )
        self.volume = 1

        # Dimensions of state and action
        self.num_levels = num_levels
        self.state_dim = 4 + 4 * self.num_levels  # from MarketState
        action_discrete_dim = 3

        # NN for Q-fun and its optimizer
        self.q_func = FFN_fix_fol_Q(state_dim=self.state_dim)
        self.optimizer_q = torch.optim.RMSprop(self.q_func.parameters(), lr=0.01)

        # NN for policy and its optimizer
        self.policy_discr = FFN(
            sizes=[self.state_dim, 4096, action_discrete_dim],
            activation=nn.ReLU,
            output_activation=Softmax,
        )  # this network decides whether to buy/sell/do nothing
        self.optimizer_pol = torch.optim.RMSprop(
            list(self.policy_discr.parameters()), lr=0.001
        )
        self.prev_state_action_reward = None

    def move_to_device(self):
        self.q_func.to(self.device)
        self.policy_discr.to(self.device)

    def move_to_cpu(self):
        self.q_func.to("cpu")
        self.policy_discr.to("cpu")

    def learning_step(self, results_dir: Optional[str] = None):
        # Policy evaluation + Policy improvement
        self.move_to_device()
        self.policy_eval(batch_size=20000, n_epochs=10)
        self.policy_improvement(batch_size=100_000, n_epochs=10)

        if results_dir is not None:
            # save in case environment chooses to crash
            self.save(results_dir)
        self.move_to_cpu()

    def _update_memory(
        self,
        state: PriceStateWithFees,
        action: Action,
        reward: float,
    ):
        """
        Ensure what is the input?
        """
        if (
            self.prev_state_action_reward is not None
            and self.prev_state_action_reward[1] is not NoAction
        ):
            prev_state, prev_action, prev_reward = self.prev_state_action_reward
            self.memory["state"].append(prev_state.to_array())
            # action_discrete = 0 if sell
            # action_discrete = 1 if buy
            # action_discrete = 2 if they do not do anything
            self.memory["action_discrete"].append([prev_action.side.value])

            self.memory["reward"].append([prev_reward])
            if state is not np.nan:
                self.memory["next_state"].append(state.to_array())
            else:
                self.memory["next_state"].append(
                    np.nan * np.ones_like(state.to_array())
                )

        self.prev_state_action_reward = (state, action, reward)

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

    def step(self, state: PriceStateWithFees):
        self.step_num += 1
        self.latest_action = self._step(state)
        self.latest_state = state

        if state.full_balance <= 0:
            return NoAction
        if state.market_in_auction:
            return NoAction
        return self.latest_action

    def _step(self, state: PriceStateWithFees) -> Action:
        # learned policy
        state = state.to_array().reshape(1, -1)  # adding batch_dimension
        state = torch.from_numpy(state).float()  # .to(self.device)

        with torch.no_grad():
            c = self.sample_action(state=state, sim=True)
        choice = int(c.item())

        return MarketOrderAction(side=Side(choice), volume=self.volume)

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
        c is a tensor of shape (batch_size, 1) returning the sampled action from {sell, buy, do nothing}
        (i.e. c is filled with values from {0,1,2})
        """

        probs = self.policy_discr(state)
        if sim:
            m = Categorical(probs)
            c = m.sample()
        else:
            c = probs
        if evaluate:
            c = torch.max(probs, 1, keepdim=True)[1]
        return c

    def policy_eval(
        self,
        batch_size: int,
        n_epochs: int,
    ):
        toggle(self.policy_discr, to=False)
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

                pred = torch.gather(
                    self.q_func(batch_state),
                    dim=1,
                    index=batch_action_discrete,
                )

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
                    "{},{:.2e},{:.2e},{:.2e}\n".format(
                        epoch + self.learningIteration * n_epochs,
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

        q = self.q_func(state)
        c = self.sample_action(
            state, sim=False
        )  # .unravel().reshape((state.shape[0], 1))

        v = c[:, 0] * (q[:, 0] - self.coefH_discr * torch.log(c[:, 0]))
        v += c[:, 1] * (q[:, 1] - self.coefH_discr * torch.log(c[:, 1]))
        v += c[:, 2] * (q[:, 2] - self.coefH_discr * torch.log(c[:, 2]))
        self.q_func.train()
        return v

    def D_KL(self, state):
        """
        KL divergence between pi(.|x) and the unnormalised density exp(Q(x,.)),
        where pi(.|x) is a LogNormal distribution
        """
        # c = self.sample_action(state).reshape((state.shape[0], 1))

        q = self.q_func(state)
        c = self.sample_action(
            state, sim=False
        )  # .unravel().reshape((state.shape[0], 1))

        d_kl = c[:, 0] * (self.coefH_discr * torch.log(c[:, 0]) - q[:, 0])
        d_kl += c[:, 1] * (self.coefH_discr * torch.log(c[:, 1]) - q[:, 1])
        d_kl += c[:, 2] * (self.coefH_discr * torch.log(c[:, 2]) - q[:, 2])

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
                        epoch + n_epochs * self.learningIteration, d_kl.item()
                    )
                )
            pbar.update(1)

        # update the coefficients for the next run
        self.coefH_discr = max(self.coefH_discr * 0.99, 1e-10)
        self.coefH_cont = max(self.coefH_cont * 0.99, 1e-10)
        self.learningIteration += 1
        return 0

    def save(self, results_dir: str):
        filename = os.path.join(results_dir, "agent.pth.tar")
        d = {
            "losses": self.losses,
            "q": self.q_func.state_dict(),
            "policy_discr": self.policy_discr.state_dict(),
            "iteration": self.learningIteration,
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

        self.learningIteration = d["iteration"]
        self.coefH_discr = d["coefH_discr"]

        filename_for_memory = os.path.join(results_dir, "memory.pickle")
        with open(filename_for_memory, "rb") as f:
            memory = pickle.load(f)
        self.memory = memory
