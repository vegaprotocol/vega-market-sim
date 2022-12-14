from typing import Any, Callable, List, Optional

from vega_sim.environment.agent import Agent, StateAgent, VegaState
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull
from vega_sim.service import VegaService
from vega_sim.scenario.ideal_market_maker.agents import (
    OptimalMarketMaker,
    LimitOrderTrader,
    MarketOrderTrader,
    OptimalLiquidityProvider,
    InformedTrader,
)


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
        self.num_agents = len(base_agents)

        self.mm_agent = self.agents[OptimalMarketMaker.name_from_tag()]
        self.lo_agent = self.agents[LimitOrderTrader.name_from_tag()]
        self.mo_agent = self.agents[MarketOrderTrader.name_from_tag()]
        self.olp_agent = self.agents[OptimalLiquidityProvider.name_from_tag()]

    def step(self, vega: VegaService):
        state = self.state_func(vega)
        self.mm_agent.AvoidCrossedOrder()
        self.lo_agent.step_amendprice(state)
        self.mm_agent.step(state)

        if self.olp_agent:
            for lp_agent in self.olp_agent:
                lp_agent.step(state)

        # Pass trading info
        self.lo_agent.num_post_at_bid = self.agents[0].num_bidhit
        self.lo_agent.num_post_at_ask = self.agents[0].num_askhit
        self.mo_agent.num_buyMO = self.agents[0].num_buyMO
        self.mo_agent.num_sellMO = self.agents[0].num_sellMO

        self.lo_agent.step_limitorders(state)
        self.mo_agent.step_buy(state)
        self.lo_agent.step_limitorderask(state)
        self.mo_agent.step_sell(state)
        self.lo_agent.step_limitorderbid(state)
