from typing import List, Tuple
from reinforcement.learning_agent import Action
from .learning_agent import MarketState


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
