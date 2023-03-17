from dataclasses import dataclass


@dataclass(frozen=True)
class SimpleState:
    balance: float
    position: float
    best_bid: float
    best_ask: float
