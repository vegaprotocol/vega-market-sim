
from typing import Any, Callable, List, Optional

from vega_sim.environment.agent import Agent, StateAgent, VegaState
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull
from vega_sim.service import VegaService


class MarketEnvironmentforMMsim(MarketEnvironmentWithState):
    def __init__(
        self,
        agents: List[StateAgent],
        n_steps: int = 180,
        random_agent_ordering: bool = False,
        state_func: Optional[Callable[[VegaService], VegaState]] = None,
        transactions_per_block: int = 1,
        block_length_seconds: int = 1,
        vega_service: Optional[VegaServiceNull] = None,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, List[Agent]], Any]
        ] = None,
        state_extraction_freq: int = 10,       
    ):
        super().__init__(
            agents = agents,
            n_steps = n_steps,
            random_agent_ordering = random_agent_ordering,
            transactions_per_block = transactions_per_block,
            block_length_seconds = block_length_seconds,
            vega_service = vega_service,
            state_extraction_fn = state_extraction_fn,
            state_extraction_freq = state_extraction_freq,
            state_func = state_func,
        )

    def step(self, vega: VegaService):
        state = self.state_func(vega)

        # Agent must step in order
        #   agents = [market_maker, tradingbot, randomtrader, auctionpass1, auctionpass2]
        self.agents[0].AvoidCrossedOrder()
        self.agents[2].step_amendprice(state)
        self.agents[0].step(state)

        self.agents[2].num_post_at_bid = self.agents[0].num_bidhit
        self.agents[2].num_post_at_ask = self.agents[0].num_askhit
        self.agents[1].num_buyMO = self.agents[0].num_buyMO
        self.agents[1].num_sellMO = self.agents[0].num_sellMO       

        self.agents[2].step_limitorders(state)
        self.agents[1].step_buy(state)
        self.agents[2].step_limitorderask(state)

        self.agents[1].step_sell(state)
        self.agents[2].step_limitorderbid(state)

        self.agents[0].logdata()

        

