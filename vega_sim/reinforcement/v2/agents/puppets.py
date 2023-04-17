import traceback
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from logging import getLogger

from vega_sim.scenario.common.agents import StateAgentWithWallet, VegaService, VegaState

logger = getLogger(__name__)


class Side(Enum):
    SELL = 0
    NONE = 1
    BUY = 2


@dataclass
class Action:
    pass


@dataclass
class MarketOrderAction(Action):
    side: Side
    volume: float


@dataclass
class NoAction(Action):
    pass


class AgentType(Enum):
    MARKET_ORDER = auto()


class Puppet(StateAgentWithWallet):
    def __init__(
        self,
        key_name: str,
        market_name: str,
        tag: Optional[str] = None,
        wallet_name: Optional[str] = None,
    ):
        """A puppet agent.

        When an action is set using set_next_action, the agent will take that
        action next time its step function is called (and will forget it after that).

        These are useful for learning agents who can act separately and insert their
        actions into the main scenario.

        Args:
            key_name:
                str, The name to use for this agent's key
            tag:
                str, optional, additional tag to add to agent's wallet name
            wallet_name:
                str, optional, Name of wallet for agent to use.
        """
        super().__init__(wallet_name=wallet_name, tag=tag, key_name=key_name)
        self.action: Optional[Action] = None
        self.market_name = market_name

    def set_next_action(self, action: Action):
        self.action = action


class MarketOrderPuppet(Puppet):
    def initialise(self, vega: VegaService, create_wallet: bool = True):
        super().initialise(vega, create_wallet)
        self.market_id = self.vega.find_market_id(name=self.market_name)

    def step(self, vega_state: VegaState):
        if (
            self.action is not None
            and self.action is not NoAction
            and self.action.side != Side.NONE
        ):
            try:
                self.vega.submit_market_order(
                    trading_key=self.key_name,
                    market_id=self.market_id,
                    side=("SIDE_BUY" if self.action.side == Side.BUY else "SIDE_SELL"),
                    volume=self.action.volume,
                    wait=False,
                )
            except:
                logger.exception(traceback.format_exc())


AGENT_TYPE_TO_AGENT = {AgentType.MARKET_ORDER: MarketOrderPuppet}
AGENT_TYPE_TO_ACTION = {AgentType.MARKET_ORDER: MarketOrderAction}
