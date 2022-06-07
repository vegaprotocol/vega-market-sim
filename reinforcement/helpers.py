from typing import List, Tuple
from functools import partial
import torch
import torch.nn as nn
import numpy as np


def apply_funcs(value, *functions):
    """
    composition of functions applied to value
    """
    res = value
    for f in functions:
        res = f(res)
    return res

def to_torch(arr: np.array, dtype: torch.dtype = torch.float, device: str = 'cpu'):
    return torch.tensor(arr, dtype=dtype, device=device)
    

def toggle(m: nn.Module, to: bool):
    """
    freezes or unfreezes a model's parameters
    """
    for p in m.parameters():
        p.requires_grad_(to)
