from abc import ABC
from dataclasses import dataclass
from typing import Any, Tuple, Dict

from vega_sim.service import VegaService


@dataclass
class VegaState:
    network_state: Tuple
    market_state: Dict[str, Any]


class Agent(ABC):
    def step(self, vega: VegaService):
        pass

    def initialise(self, vega: VegaService):
        self.vega = vega

    def finalise(self):
        pass


class AgentWithWallet(Agent):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
    ):
        """Agent for use in environments as specified in environment.py.
        To extend, the crucial function to implement is the step function which will
        be called on each timestep in the simulation.

        Additionally, the initialise function can be added to. This function is called
        once before the main simulation and can be used to creat assets, set up markets,
        faucet assets to the agent etc.

        Args:
            wallet_name:
                str, The name to use for this agent's wallet
            wallet_pass:
                str, The password which this agent uses to log in to the wallet
        """
        super().__init__()
        self.wallet_name = wallet_name
        self.wallet_pass = wallet_pass

    def step(self, vega: VegaService):
        pass

    def initialise(self, vega: VegaService):
        super().initialise(vega=vega)
        self.vega.create_wallet(name=self.wallet_name, passphrase=self.wallet_pass)


class StateAgentWithWallet(AgentWithWallet):
    def step(self, vega_state: VegaState):
        pass


class StateAgent(Agent):
    def step(self, vega_state: VegaState):
        pass
