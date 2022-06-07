from typing import List, Tuple
from reinforcement.learning_agent import Action
from .learning_agent import MarketState

from functools import partial

def states_to_sarsa(
    states: List[Tuple[MarketState, Action]]
) -> List[Tuple[MarketState, Action, float, MarketState, Action]]:
    res = []
    for i in range(len(states) - 1):
        pres = states[i]
        next = states[i + 1]
        reward = (next[0].general_balance + next[0].margin_balance) - (
            pres[0].general_balance + pres[0].margin_balance
        )
        res.append((pres[0], pres[1], reward, next[0], next[1]))
    return res



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
