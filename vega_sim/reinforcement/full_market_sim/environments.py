from vega_sim.reinforcement.learning_agent import LearningAgent

from vega_sim.scenario.ideal_market_maker.environments import MarketEnvironment
from vega_sim.service import VegaService


class RLMarketEnvironment(MarketEnvironment):
    def add_learning_agent(self, agent: LearningAgent):
        self.learning_agent = agent
        self.agents = self._base_agents + [agent]

    def step(self, vega: VegaService):
        super().step(vega=vega)

        state = self.state_func(vega)
        # Learning agent
        self.learning_agent.step(state, random=False)
