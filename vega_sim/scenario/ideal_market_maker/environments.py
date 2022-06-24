from typing import Any, Callable, List, Optional

from vega_sim.environment.agent import Agent, StateAgent, VegaState
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull
from vega_sim.service import VegaService


class MarketEnvironment(MarketEnvironmentWithState):
    def __init__(
        self,
        base_agents: List[StateAgent],
        n_steps: int = 180,
        random_agent_ordering: bool = False,
        state_func: Optional[Callable[[VegaService], VegaState]] = None,
        transactions_per_block: int = 1,
        step_length_seconds: Optional[int] = None,
        vega_service: Optional[VegaServiceNull] = None,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, List[Agent]], Any]
        ] = None,
        state_extraction_freq: int = 10,
        block_length_seconds: int = 1,
    ):
        super().__init__(
            agents=base_agents,
            n_steps=n_steps,
            random_agent_ordering=random_agent_ordering,
            transactions_per_block=transactions_per_block,
            step_length_seconds=step_length_seconds,
            vega_service=vega_service,
            state_extraction_fn=state_extraction_fn,
            state_extraction_freq=state_extraction_freq,
            state_func=state_func,
            block_length_seconds=block_length_seconds,
        )
        self._base_agents = base_agents

    def step(self, vega: VegaService):
        state = self.state_func(vega)

        # Agent must step in order
        #   agents = [market_maker, tradingbot, randomtrader,
        #    auctionpass1, auctionpass2]

        self.agents[0].AvoidCrossedOrder()

        try:
            self.agents[2].step_amendprice(state)
        except Exception as e:
            print(e)
        self.agents[0].step(state)

        try:
            self.agents[2].num_post_at_bid = self.agents[0].num_bidhit
            self.agents[2].num_post_at_ask = self.agents[0].num_askhit
            self.agents[1].num_buyMO = self.agents[0].num_buyMO
            self.agents[1].num_sellMO = self.agents[0].num_sellMO
        except Exception as e:
            print(e)

        try:
            self.agents[2].step_limitorders(state)
            self.agents[1].step_buy(state)
            self.agents[2].step_limitorderask(state)
        except Exception as e:
            print(e)

        try:
            self.agents[1].step_sell(state)
            self.agents[2].step_limitorderbid(state)
        except Exception as e:
            print(e)

        try:
            self.agents[0].logdata()
        except Exception as e:
            print(e)
