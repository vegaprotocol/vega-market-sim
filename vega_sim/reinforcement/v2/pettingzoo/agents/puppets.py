import traceback
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from logging import getLogger

import vega_sim.proto.vega as vega_protos
from vega_sim.scenario.common.agents import StateAgentWithWallet, VegaService, VegaState
from vega_sim.service import PeggedOrder

logger = getLogger(__name__)


class Side(Enum):
    SELL = 0
    NONE = 1
    BUY = 2


class ForcedSide(Enum):
    SELL = 0
    BUY = 1


@dataclass
class Action:
    pass


@dataclass
class MarketOrderAction(Action):
    side: Side
    volume: float


@dataclass
class AtTouchOrderAction(Action):
    side: ForcedSide
    volume: float


@dataclass
class NoAction(Action):
    pass


class AgentType(Enum):
    MARKET_ORDER = auto()
    AT_TOUCH = auto()


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


class AtTouchPuppet(Puppet):
    def initialise(self, vega: VegaService, create_wallet: bool = True):
        super().initialise(vega, create_wallet)
        self.market_id = self.vega.find_market_id(name=self.market_name)

    def step(self, vega_state: VegaState):
        if self.action is not None and self.action is not NoAction:
            try:
                self.vega.cancel_order(
                    trading_key=self.key_name, market_id=self.market_id
                )
                self.vega.submit_order(
                    trading_key=self.key_name,
                    market_id=self.market_id,
                    side=(
                        "SIDE_BUY"
                        if self.action.side == ForcedSide.BUY
                        else "SIDE_SELL"
                    ),
                    volume=self.action.volume,
                    time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
                    order_type=vega_protos.vega.Order.Type.TYPE_LIMIT,
                    pegged_order=PeggedOrder(
                        reference=(
                            vega_protos.vega.PeggedReference.PEGGED_REFERENCE_BEST_BID
                            if self.action.side == ForcedSide.BUY
                            else vega_protos.vega.PeggedReference.PEGGED_REFERENCE_BEST_ASK
                        ),
                        offset=0,
                    ),
                    wait=False,
                )
            except:
                logger.exception(traceback.format_exc())


AGENT_TYPE_TO_AGENT = {
    AgentType.MARKET_ORDER: MarketOrderPuppet,
    AgentType.AT_TOUCH: AtTouchPuppet,
}
AGENT_TYPE_TO_ACTION = {
    AgentType.MARKET_ORDER: MarketOrderAction,
    AgentType.AT_TOUCH: AtTouchOrderAction,
}
