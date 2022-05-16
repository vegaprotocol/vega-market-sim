from abc import ABC
from dataclasses import dataclass
from typing import Any, Tuple, Dict

from vega_sim.service import VegaService


@dataclass
class VegaState:
    network_state: Tuple
    market_state: Dict[str, Any]


class Agent(ABC):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
    ):
        self.wallet_name = wallet_name
        self.wallet_pass = wallet_pass

    def step(self, vega: VegaService):
        pass

    def initialise(self, vega: VegaService):
        self.vega = vega
        self.vega.create_wallet(name=self.wallet_name, passphrase=self.wallet_pass)


class StateAgent(Agent):
    def step(self, vega_state: VegaState):
        pass
