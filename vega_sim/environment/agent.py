from abc import ABC
from dataclasses import dataclass
from typing import Any, Tuple, Dict, Optional, List, Union

from vega_sim.null_service import VegaServiceNull
from vega_sim.network_service import VegaServiceNetwork


@dataclass
class VegaState:
    network_state: Tuple
    market_state: Dict[str, Any]
    time: int


class Agent(ABC):
    NAME_BASE = "base_agent"

    def __init__(self, tag: Optional[str] = None):
        self.tag = tag

    def step(self, vega: Union[VegaServiceNull, VegaServiceNetwork]):
        pass

    def initialise(
        self,
        vega: VegaServiceNull,
        create_key: bool = False,
        mint_key: bool = False,
    ):
        self.vega = vega

    def finalise(self):
        pass

    def _update_state(self, current_step: int):
        pass

    def name(self) -> str:
        return self.NAME_BASE + (f"_{self.tag}" if self.tag else "")

    @classmethod
    def name_from_tag(cls, tag: Optional[str] = None) -> str:
        return cls.NAME_BASE + (f"_{tag}" if tag is not None else "")


class AgentWithWallet(Agent):
    def __init__(
        self,
        key_name: str,
        tag: Optional[str] = None,
        wallet_name: Optional[str] = None,
        state_update_freq: Optional[int] = None,
    ):
        """Agent for use in environments as specified in environment.py.
        To extend, the crucial function to implement is the step function which will
        be called on each timestep in the simulation.

        Additionally, the initialise function can be added to. This function is called
        once before the main simulation and can be used to creat assets, set up markets,
        faucet assets to the agent etc.

        Args:
            key_name:
                str, Name of key in wallet for agent to use.
            wallet_pass:
                str, The password which this agent uses to log in to the wallet
            tag:
                str, optional, additional tag to add to agent's wallet name
            wallet_name:
                str, optional, The name to use for this agent's wallet
        """
        super().__init__(tag=tag)
        self.wallet_name = wallet_name
        self.key_name = key_name

        self.state_update_freq = state_update_freq

    def step(self):
        pass

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = False,
    ):
        super().initialise(vega=vega)
        if create_key:
            self.vega.create_key(
                wallet_name=self.wallet_name,
                name=self.key_name,
            )
            self._public_key = vega.wallet.public_key(
                name=self.key_name, wallet_name=self.wallet_name
            )


class StateAgentWithWallet(AgentWithWallet):
    def step(self, vega_state: VegaState):
        super().step()


class StateAgent(Agent):
    def step(self, vega_state: VegaState):
        super().step()
