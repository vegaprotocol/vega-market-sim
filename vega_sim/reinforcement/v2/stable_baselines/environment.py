import logging

import gymnasium as gym
from gymnasium import spaces

from vega_sim.reinforcement.v2.agents.puppets import (
    MarketOrderAction,
    AgentType,
    Side,
)
from vega_sim.reinforcement.v2.learning_environment import Environment
from vega_sim.reinforcement.v2.rewards import Reward
from vega_sim.reinforcement.v2.stable_baselines.states import (
    price_state_with_fees_obs_space,
)
from vega_sim.reinforcement.v2.states import PriceStateWithFees, State
from vega_sim.scenario.registry import CurveMarketMaker

logger = logging.getLogger(__name__)


class SingleAgentVegaEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        action_type: str = "market",
        state_type: State = PriceStateWithFees,
        num_levels_state: int = 5,
        trade_volume: float = 1,
        steps_per_trading_session: int = 1000,
    ):
        super().__init__()
        self.num_levels_state = num_levels_state
        self.state_type = state_type
        self.action_type = action_type
        self.trade_volume = trade_volume
        self.steps_per_trading_session = steps_per_trading_session
        self.current_step = 0
        self.learner_name = "learner_1"

        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = self._get_action_space(action_type=action_type)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = self._get_observation_space(self.state_type)

        scenario = CurveMarketMaker(
            market_decimal=3,
            asset_decimal=5,
            market_position_decimal=2,
            initial_price=1000.0,
            lp_commitamount=100000,
            initial_asset_mint=1e8,
            step_length_seconds=1,
            block_length_seconds=1,
            buy_intensity=5,
            sell_intensity=5,
            market_name="ETH",
            num_steps=self.steps_per_trading_session * 2,
            random_agent_ordering=False,
            sigma=100,
            asset_name="DAI",
        )

        self.env = Environment(
            agents={self.learner_name: AgentType.MARKET_ORDER},
            agent_to_reward={self.learner_name: Reward.PNL},
            agent_to_state={self.learner_name: PriceStateWithFees},
            scenario=scenario,
        )

    def _get_action_space(self, action_type: str) -> spaces.Space:
        if action_type == "market":
            return spaces.Discrete(3)
        else:
            raise Exception(f"Action type {action_type} is not implemented")

    def _get_observation_space(self, state_type: State) -> spaces.Space:
        if state_type == PriceStateWithFees:
            return price_state_with_fees_obs_space(num_levels=self.num_levels_state)

    def step(self, action):
        step_res = self.env.step(
            {
                self.learner_name: MarketOrderAction(
                    side=Side(action), volume=self.trade_volume
                )
            }
        )[self.learner_name]
        self.current_step += 1

        return (
            step_res.observation.to_array(),
            step_res.reward,
            self.current_step >= self.steps_per_trading_session,
            False,
            {},
        )

    def reset(self):
        self.env.reset()
        step_res = self.env.step(
            {self.learner_name: MarketOrderAction(side=Side.NONE, volume=0)}
        )[self.learner_name]

        self.current_step = 0
        return step_res.observation.to_array(), {}

    def render(self, mode="human"):
        pass

    def close(self):
        self.env.stop()
