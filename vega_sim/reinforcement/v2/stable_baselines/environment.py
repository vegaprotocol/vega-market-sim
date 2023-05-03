import logging

import gymnasium as gym
from gymnasium import spaces
from typing import Type
from enum import Enum
from stable_baselines3.common.callbacks import BaseCallback

from vega_sim.reinforcement.v2.agents.puppets import (
    AgentType,
    ForcedSide,
    Side,
    AGENT_TYPE_TO_ACTION,
)
from vega_sim.reinforcement.v2.learning_environment import Environment
from vega_sim.reinforcement.v2.rewards import Reward
from vega_sim.reinforcement.v2.stable_baselines.states import (
    price_state_with_fees_obs_space,
    position_state_with_fees_obs_space,
)
from vega_sim.reinforcement.v2.states import PriceStateWithFees, State, PositionOnly
from vega_sim.scenario.registry import CurveMarketMaker


logger = logging.getLogger(__name__)


class ActionType(Enum):
    MARKET = "market"
    AT_TOUCH_ONE_SIDE = "at_touch_one_side"


ACTION_TO_AGENT = {
    ActionType.MARKET: AgentType.MARKET_ORDER,
    ActionType.AT_TOUCH_ONE_SIDE: AgentType.AT_TOUCH,
}


class ActionLoggerCallback(BaseCallback):
    pass


class SingleAgentVegaEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        action_type: ActionType = ActionType.MARKET,
        state_type: Type[State] = PriceStateWithFees,
        reward_type: Reward = Reward.PNL,
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
            agents={self.learner_name: ACTION_TO_AGENT[self.action_type]},
            agent_to_reward={self.learner_name: reward_type},
            agent_to_state={self.learner_name: state_type},
            scenario=scenario,
        )

    def _get_action_space(self, action_type: ActionType) -> spaces.Space:
        if action_type == ActionType.MARKET:
            return spaces.Discrete(3)
        elif action_type == ActionType.AT_TOUCH_ONE_SIDE:
            return spaces.Discrete(2)
        else:
            raise Exception(f"Action type {action_type} is not implemented")

    def _get_observation_space(self, state_type: Type[State]) -> spaces.Space:
        if state_type == PriceStateWithFees:
            return price_state_with_fees_obs_space(num_levels=self.num_levels_state)
        if state_type == PositionOnly:
            return position_state_with_fees_obs_space()

    def _action_conversion(self, action):
        if self.action_type == ActionType.MARKET:
            return AGENT_TYPE_TO_ACTION[AgentType.MARKET_ORDER](
                side=Side(action), volume=self.trade_volume
            )
        elif self.action_type == ActionType.AT_TOUCH_ONE_SIDE:
            return AGENT_TYPE_TO_ACTION[AgentType.AT_TOUCH](
                side=ForcedSide(action), volume=self.trade_volume
            )
        else:
            raise Exception(f"Action type {self.action_type} is not implemented")

    def step(self, action):
        step_res = self.env.step(
            {self.learner_name: self._action_conversion(action=action)}
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
        step_res = self.env.step({self.learner_name: None})[self.learner_name]

        self.current_step = 0
        return step_res.observation.to_array(), {}

    def render(self, mode="human"):
        pass

    def close(self):
        self.env.stop()
