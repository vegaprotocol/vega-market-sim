import torch
import torch.nn as nn
import numpy as np
from functools import partial

from torch.distributions.normal import Normal


def lognorm_sample(mu: torch.Tensor, sigma: torch.Tensor):
    z = mu + sigma * torch.randn_like(sigma)
    sample = torch.exp(z)
    return z, sample

def lognorm_logprob(z: torch.Tensor, mu: torch.Tensor, sigma: torch.Tensor):
    """
    It's a change of measure: calculate the expected value of the log-density of the lognormal by changing the measure to the law of the normal .
    """
    normal = Normal(loc = mu, scale = sigma)
    logprob = normal.log_prob(z) - z

    return logprob


def reg_policy(z: torch.Tensor, mu: torch.Tensor, sigma: torch.Tensor):
    """
    Regularisation term for the policy: D_KL(N(policy_parameters), N(0,1))

    """
    normal_policy = Normal(loc=mu, scale=sigma)
    normal_ref = Normal(loc=torch.zeros_like(mu), scale=torch.ones_like(sigma))

    d_kl = normal_policy.log_prob(z) - normal_ref.log_prob(z)
    return d_kl
