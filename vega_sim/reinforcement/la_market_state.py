from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

from vega_sim.environment.agent import Agent

@dataclass
class AbstractAction:
    pass


@dataclass
class LAMarketState:
    step: int
    position: float
    margin_balance: float
    general_balance: float
    market_in_auction: bool
    bid_prices: List[float]
    ask_prices: List[float]
    bid_volumes: List[float]
    ask_volumes: List[float]
    trading_fee: float
    next_price: float

    def to_array(self):
        l = (
            [
                self.step,
                self.position,
                self.margin_balance,
                self.general_balance,
                int(self.market_in_auction),
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




def states_to_sarsa(
    states: List[Tuple[LAMarketState, AbstractAction]],
    inventory_penalty: float = 0.0,
) -> List[Tuple[LAMarketState, AbstractAction, float, LAMarketState, AbstractAction]]:
    res = []
    for i in range(len(states) - 1):
        pres_state = states[i]
        next_state = states[i + 1]

        if next_state[0].margin_balance + next_state[0].general_balance <= 0:
            reward = -1e12
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
            (next_state[0].general_balance + next_state[0].margin_balance)
            - (pres_state[0].general_balance + pres_state[0].margin_balance)
            if next_state is not np.nan
            else 0
        )
        reward -= inventory_penalty * pres_state[0].position * pres_state[0].position
        res.append((pres_state[0], pres_state[1], reward, next_state[0], next_state[1]))
    return res
