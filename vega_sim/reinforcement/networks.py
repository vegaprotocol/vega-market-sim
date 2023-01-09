import torch
import torch.nn as nn
from typing import List


class Softmax(nn.Softmax):
    def __init__(self):
        super().__init__()
        self.activation = nn.Softmax(dim=-1)

    def forward(self, x):
        return self.activation(x)


class Threshold(nn.Module):
    def __init__(self, threshold):
        super().__init__()
        self.threshold = threshold

    def forward(self, x):
        return nn.LogSigmoid()(x) + self.threshold


class FFN(nn.Module):
    def __init__(
        self, sizes, activation=nn.ReLU, output_activation=nn.Identity, batch_norm=False
    ):
        super().__init__()

        layers = []
        for j in range(1, len(sizes)):
            layers.append(nn.Linear(sizes[j - 1], sizes[j]))
            if j < (len(sizes) - 1):
                layers.append(activation())
            else:
                layers.append(output_activation())

        self.net = nn.Sequential(*layers)

    def forward(self, *args):
        x = torch.cat(args, -1)
        return self.net(x)


class FFN_fix_fol_Q(nn.Module):
    """
    Specific class for Q-func of trader
    """

    def __init__(
        self,
        state_dim: int,
    ):
        """
        I create as many sub-networks as possible discrete actions that the agent can take.
        The input of each network is the continuous part of the action (i.e. the volume).
        The output of each network is the q-func applied to the state, the volume and that particular discrete action
        """
        super().__init__()

        self.ffn_sell = FFN(
            sizes=[state_dim, 4096, 1], activation=nn.ReLU
        )  # +action_cont_dim is for the volume
        self.ffn_buy = FFN(
            sizes=[state_dim, 4096, 1], activation=nn.ReLU
        )  # +action_cont_dim is for the volume
        self.ffn_do_nothing = FFN(sizes=[state_dim, 4096, 1], activation=nn.ReLU)

    def forward(self, state: torch.Tensor):
        output = []
        output.append(self.ffn_sell(state))
        output.append(self.ffn_buy(state))
        output.append(self.ffn_do_nothing(state))
        return torch.cat(output, -1)


class FFN_Q(nn.Module):
    """
    Specific class for Q-func of trader
    """

    def __init__(
        self,
        state_dim: int,
    ):
        """
        I create as many sub-networks as possible discrete actions that the agent can take.
        The input of each network is the continuous part of the action (i.e. the volume).
        The output of each network is the q-func applied to the state, the volume and that particular discrete action
        """
        super().__init__()

        self.ffn_sell = FFN(
            sizes=[state_dim + 1, 32, 1], activation=nn.Tanh
        )  # +action_cont_dim is for the volume
        self.ffn_buy = FFN(
            sizes=[state_dim + 1, 32, 1], activation=nn.Tanh
        )  # +action_cont_dim is for the volume
        self.ffn_do_nothing = FFN(sizes=[state_dim, 32, 1], activation=nn.Tanh)

    def forward(
        self, state: torch.Tensor, volume_sell: torch.Tensor, volume_buy: torch.Tensor
    ):
        if volume_sell.dim() == 1:
            volume_sell = volume_sell.unsqueeze(1)
        if volume_buy.dim() == 1:
            volume_buy = volume_buy.unsqueeze(1)
        output = []
        output.append(self.ffn_sell(state, volume_sell))
        output.append(self.ffn_buy(state, volume_buy))
        output.append(self.ffn_do_nothing(state))
        return torch.cat(output, -1)


class FFN_Params_Normal(nn.Module):
    def __init__(
        self,
        n_in: int,
        n_distr: int,
        hidden_sizes: List[int],
    ):

        super().__init__()
        self.net = FFN(
            sizes=[n_in] + hidden_sizes, activation=nn.Tanh, output_activation=nn.Tanh
        )
        self.net_mu = nn.Linear(hidden_sizes[-1], n_distr)
        self.net_sigma = nn.Sequential(
            nn.Linear(hidden_sizes[-1], n_distr), nn.Softplus()
        )

    def forward(self, *args):
        x = torch.cat(args, -1)
        y = self.net(x)
        mu = self.net_mu(y)
        sigma = self.net_sigma(y)
        return mu, sigma


@torch.no_grad()
def init_weights(m):
    if isinstance(m, nn.Linear):
        m.weight.fill_(0.0)
        m.bias.fill_(0.0)
