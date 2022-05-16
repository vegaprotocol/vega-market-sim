from collections import namedtuple
import random
from typing import Callable, List, Optional


from vega_sim.environment.agent import Agent, StateAgent, VegaState
from vega_sim.null_service import VegaServiceNull
from vega_sim.service import VegaService


MarketState = namedtuple("MarketState", ["state"])


class MarketEnvironment:
    def __init__(
        self,
        agents: List[Agent],
        n_steps: int,
        step_length: str = "1s",
        random_agent_ordering: bool = True,
        run_with_console: bool = False,
    ):
        self.agents = agents
        self.n_steps = n_steps
        self.step_length = step_length
        self.random_agent_ordering = random_agent_ordering
        self.run_with_console = run_with_console

    def run(self) -> None:
        with VegaServiceNull(run_wallet_with_console=self.run_with_console) as vega:
            for agent in self.agents:
                agent.initialise(vega=vega)
            for _ in range(self.n_steps):
                self.step(vega)

    def step(self, vega: VegaService) -> None:
        for agent in (
            sorted(self.agents, key=lambda _: random.random())
            if self.random_agent_ordering
            else self.agents
        ):
            agent.step(vega)
        # vega.forward(self.step_length)


class MarketEnvironmentWithState(MarketEnvironment):
    @staticmethod
    def _default_state_extraction(vega: VegaService) -> VegaState:
        market_state = {}
        for market_id in vega.all_markets():
            market_info = vega.market_info(market_id=market_id)
            market_state[market_id] = MarketState(state=market_info.state)

        return VegaState(network_state=(), market_state=market_state)

    def __init__(
        self,
        agents: List[StateAgent],
        n_steps: int,
        step_length: str = "1s",
        random_agent_ordering: bool = True,
        state_func: Optional[Callable[[VegaService], VegaState]] = None,
        run_with_console: bool = False,
    ):
        super().__init__(
            agents=agents,
            n_steps=n_steps,
            step_length=step_length,
            random_agent_ordering=random_agent_ordering,
            run_with_console=run_with_console,
        )
        self.state_func = (
            state_func if state_func is not None else self._default_state_extraction
        )

    def step(self, vega: VegaService) -> None:
        state = self.state_func(vega)
        for agent in (
            sorted(self.agents, key=lambda _: random.random())
            if self.random_agent_ordering
            else self.agents
        ):
            agent.step(state)
