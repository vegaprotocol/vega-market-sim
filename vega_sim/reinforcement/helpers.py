from typing import List, Callable, Any
import torch
import torch.nn as nn
import numpy as np


def apply_funcs(value, funcs: List[Callable[..., Any]]):
    """
    composition of functions applied to value
    """
    res = value
    for f in funcs:
        res = f(res)
    return res


def to_torch(arr: np.array, dtype: torch.dtype = torch.float, device: str = "cpu"):
    return torch.tensor(arr, dtype=dtype, device=device)


def toggle(m: nn.Module, to: bool):
    """
    freezes or unfreezes a model's parameters
    """
    for p in m.parameters():
        p.requires_grad_(to)


def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
