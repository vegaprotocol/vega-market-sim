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

from vega_sim.reinforcement.networks import (
    Softmax,
    FFN,
    FFN_Params_Normal,
    FFN_Q,
)
from vega_sim.reinforcement.helpers import apply_funcs, to_torch, toggle
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

        l = (
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
        arr = np.nan_to_num(np.array(l))
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
    def __init__(
        self,
        device: str,
        discount_factor: float,
        logfile: str,
        num_levels: int,
        wallet_name: str,
        wallet_pass: str,
    ):
        super().__init__(wallet_name=wallet_name, wallet_pass=wallet_pass)
        self.base_wallet_name = wallet_name

        self.price_process = None
        self.step_num = 0

        self.device = device
        self.discount_factor = discount_factor

        self.memory = defaultdict(list)
        self.memory_capacity = 10000

        # Dimensions of state and action
        self.num_levels = num_levels
        state_dim = 7 + 4 * self.num_levels  # from MarketState
        action_discrete_dim = 3
        # Q func
        self.q_func = FFN_Q(
            state_dim=state_dim,
        )
        self.optimizer_q = torch.optim.RMSprop(self.q_func.parameters(), lr=0.001)
        # policy
        self.policy_volume = FFN_Params_Normal(
            n_in=state_dim,
            n_distr=2,
            hidden_sizes=[32],
        )
        self.policy_discr = FFN(
            sizes=[state_dim, 32, action_discrete_dim],
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
        self.logfile = logfile

    def set_market_tag(self, tag: str):
        self.tag = tag
        self.wallet_name = self.base_wallet_name + str(tag)

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

    def _update_memory(
        self, state: MarketState, action: Action, reward: float, next_state: MarketState
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

    def update_memory(self, states: List[Tuple[MarketState, Action]]):
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

    def step(self, vega_state: VegaState, random: bool = False):
        learning_state = self.state(self.vega)
        if learning_state.margin_balance + learning_state.general_balance <= 0:
            return 0
        else:
            self.latest_action = self._step(learning_state, random)
            self.latest_state = learning_state

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

            self.step_num += 1

    def _step(self, vega_state: MarketState, random: bool = False) -> Action:
        if random:
            # random policy
            choice = np.random.choice([0, 1, 2])
            volume = 1
        else:
            # learned policy
            state = vega_state.to_array().reshape(1, -1)  # adding batch_dimension
            state = torch.from_numpy(state).float()  # .to(self.device)

            with torch.no_grad():
                soft_action = self.sample_action(state=state, sim=True)
            choice = int(soft_action.c.item())
            if choice == 0:  # choice = 0 --> sell
                volume = soft_action.volume_sell.item()
            elif choice == 1:  # choice = 1 --> buy
                volume = soft_action.volume_buy.item()
            else:
                volume = 0  # choice=2, hence do nothing, hence volume is irrelevant
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
        probs = self.policy_discr(state)
        mu, sigma = self.policy_volume(state)
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

        return SoftAction(
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
            for i, (
                batch_state,
                batch_action_discrete,
                batch_action_volume,
                batch_reward,
                batch_next_state,
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
            with open(self.logfile, "a") as f:
                f.write(
                    "policy evaluation... Epoch {} / {}. Loss={:.4f}\n".format(
                        epoch, n_epochs, loss.item()
                    )
                )
            pbar.update(1)
        return 0

    def v_func(self, state, n_mc=50):
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
            + 0.5 * reg.reshape(n_mc, batch_size, -1).mean(0).mean()
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
            with open(self.logfile, "a") as f:
                f.write(
                    "policy improvement... Epoch {} / {}. KL_div={:.4f}\n".format(
                        epoch, n_epochs, d_kl.item()
                    )
                )
            pbar.update(1)

        # update the coefficients for the next run
        self.coefH_discr = max(self.coefH_discr * 0.99, 0.1)
        self.coefH_cont = max(self.coefH_cont * 0.99, 0.1)

        return 0

    def save(self, results_dir: str):
        filename = os.path.join(results_dir, "agent.pth.tar")
        d = {
            "losses": self.losses,
            "q": self.q_func.state_dict(),
            "policy_discr": self.policy_discr.state_dict(),
            "policy_volume": self.policy_volume.state_dict(),
        }
        torch.save(d, filename)

    def load(self, results_dir: str):
        filename = os.path.join(results_dir, "agent.pth.tar")
        d = torch.load(filename, map_location="cpu")
        self.q_func.load_state_dict(d["q"])
        self.policy_discr.load_state_dict(d["policy_discr"])
        self.policy_volume.load_state_dict(d["policy_volume"])
