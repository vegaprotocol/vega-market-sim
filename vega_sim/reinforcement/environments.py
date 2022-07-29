from typing import List
from vega_sim.environment.agent import Agent
from vega_sim.reinforcement.learning_agent import LearningAgent

from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.service import VegaService


class RLMarketEnvironment(MarketEnvironmentWithState):
    def __init__(self, agents: List[Agent], *args, **kwargs):
        super().__init__(agents, *args, **kwargs)
        self._base_agents = agents

    def add_learning_agent(self, agent: LearningAgent):
        self.learning_agent = agent
        self.agents = self._base_agents + [agent]

    def step(self, vega: VegaService):
        super().step(vega=vega)

        state = self.state_func(vega)
        # Learning agent
        self.learning_agent.step(state, random=False)
