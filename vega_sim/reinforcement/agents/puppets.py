from dataclasses import dataclass
from enum import Enum
from typing import Optional

from vega_sim.scenario.common.agents import StateAgentWithWallet, VegaState, VegaService


class Side(Enum):
    SELL = 0
    BUY = 1


@dataclass
class MarketOrderAction:
    side: Side
    volume: float


class MarketOrderPuppet(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        market_name: str,
        tag: Optional[str] = None,
        key_name: Optional[str] = None,
    ):
        """A puppet agent which places orders according to a specified
        MarketOrderAction.

        When an action is set using set_next_action, the agent will take that
        action next time its step function is called (and will forget it after that).

        These are useful for learning agents who can act separately and insert their
        actions into the main scenario.

        Args:
            wallet_name:
                str, The name to use for this agent's wallet
            wallet_pass:
                str, The password which this agent uses to log in to the wallet
            tag:
                str, optional, additional tag to add to agent's wallet name
            key_name:
                str, optional, Name of key in wallet for agent to use. Defaults
                to value in the environment variable "VEGA_DEFAULT_KEY_NAME".
        """
        super().__init__(
            wallet_name=wallet_name, wallet_pass=wallet_pass, tag=tag, key_name=key_name
        )
        self.action: Optional[MarketOrderAction] = None
        self.market_name = market_name

    def initialise(self, vega: VegaService, create_wallet: bool = True):
        super().initialise(vega, create_wallet)
        market_name = self.market_name + f"_{self.tag}"
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == market_name
        ][0]

    def step(self, vega_state: VegaState):
        if self.action is not None:
            self.vega.submit_market_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                side="BUY" if self.action.side == Side.BUY.value else "SELL",
                volume=self.action.volume,
                wait=False,
            )
