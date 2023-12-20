import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Type
from copy import deepcopy

from gymnasium import spaces
from pettingzoo.utils.env import AgentID, ParallelEnv
from pettingzoo.test import api_test

from vega_sim.reinforcement.v2.agents.puppets import (
    AGENT_TYPE_TO_ACTION,
    AgentType,
    ForcedSide,
    Side,
)
from vega_sim.reinforcement.v2.learning_environment import Environment
from vega_sim.reinforcement.v2.rewards import REWARD_ENUM_TO_CLASS, Reward
from vega_sim.reinforcement.v2.stable_baselines.states import (
    position_state_with_fees_obs_space,
    price_state_with_fees_obs_space,
)
from vega_sim.reinforcement.v2.states import PositionOnly, PriceStateWithFees, State
from vega_sim.scenario.registry import CurveMarketMaker

logger = logging.getLogger(__name__)


class ActionType(Enum):
    MARKET = "market"
    AT_TOUCH_ONE_SIDE = "at_touch_one_side"


ACTION_TO_AGENT = {
    ActionType.MARKET: AgentType.MARKET_ORDER,
    ActionType.AT_TOUCH_ONE_SIDE: AgentType.AT_TOUCH,
}


@dataclass
class AgentConfig:
    action_type: ActionType
    state_type: Type[State]
    party: str  # Added party attribute here
    reward_type: Optional[Reward] = None
    terminal_reward_type: Optional[Reward] = None


class MultiAgentVegaEnv(ParallelEnv):
    """Custom Environment that follows gym interface."""

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        agents: List[AgentConfig],
        num_levels_state: int = 5,
        trade_volume: float = 1,
        steps_per_trading_session: int = 1000,
    ):
        super().__init__()
        self.num_levels_state = num_levels_state
        self.agent_configs = agents
        self.trade_volume = trade_volume
        self.steps_per_trading_session = steps_per_trading_session
        self.current_step = 0
        self.learner_names = {
            str(i): f"learner_{i}" for i in range(len(self.agent_configs))
        }

        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_spaces = {
            str(i): self._get_action_space(action_type=agent_config.action_type)
            for (i, agent_config) in enumerate(self.agent_configs)
        }
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_spaces = {
            str(i): self._get_observation_space(state_type=agent_config.state_type)
            for (i, agent_config) in enumerate(self.agent_configs)
        }

        scenario = CurveMarketMaker(
            market_decimal=3,
            asset_decimal=5,
            market_position_decimal=2,
            initial_price=1000.0,
            lp_commitamount=1e4,
            initial_asset_mint=12e4,
            step_length_seconds=1,
            block_length_seconds=1,
            buy_intensity=10,
            sell_intensity=10,
            market_name="ETH",
            num_steps=self.steps_per_trading_session * 2,
            random_agent_ordering=False,
            sigma=8,
            asset_name="DAI",
            q_upper=15,
            q_lower=-15,
        )

        self.env = Environment(
            agents={
                learner_name: ACTION_TO_AGENT[self.agent_configs[int(i)].action_type]
                for (i, learner_name) in self.learner_names.items()
            },
            agent_to_reward=(
                {
                    learner_name: self.agent_configs[int(i)].reward_type
                    for (i, learner_name) in self.learner_names.items()
                }
            ),
            agent_to_state={
                learner_name: self.agent_configs[int(i)].state_type
                for (i, learner_name) in self.learner_names.items()
            },
            scenario=scenario,
        )
        self.agents = list(self.learner_names.keys())
        self.possible_agents = self.agents

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

    def _action_conversion(self, agent, action):
        agent_config = self.agent_configs[int(agent)]
        if agent_config.action_type == ActionType.MARKET:
            return AGENT_TYPE_TO_ACTION[AgentType.MARKET_ORDER](
                side=Side(action), volume=self.trade_volume
            )
        elif agent_config.action_type == ActionType.AT_TOUCH_ONE_SIDE:
            return AGENT_TYPE_TO_ACTION[AgentType.AT_TOUCH](
                side=ForcedSide(action), volume=self.trade_volume
            )
        else:
            raise Exception(
                f"Action type {agent_config.action_type} is not implemented"
            )

    def step(self, actions):
        step_res = self.env.step(
            {
                self.learner_names[agent]: self._action_conversion(
                    action=action, agent=agent
                )
                for (agent, action) in actions.items()
            }
        )
        self.current_step += 1

        is_terminal = self.current_step >= self.steps_per_trading_session

        self.latest_observations = {}
        self.latest_rewards = {}
        self.latest_terminations = {}
        self.latest_truncations = {}
        self.latest_infos = {}

        # First pass: Calculate total reward and count for each party
        party_rewards = {}
        party_counts = {}
        for agent_id, agent_name in self.learner_names.items():
            agent_step_res = step_res[agent_name]
            reward = agent_step_res.reward
            if (
                is_terminal
                and self.agent_configs[int(agent_id)].terminal_reward_type is not None
            ):
                terminal_reward = REWARD_ENUM_TO_CLASS[
                    self.agent_configs[int(agent_id)].terminal_reward_type
                ](
                    agent_key=agent_name,
                    asset_id=self.env._asset_id,
                    market_id=self.env._market_id,
                )
                reward += self.env.calculate_reward(terminal_reward)
            
            party = self.agent_configs[int(agent_id)].party
            party_rewards[party] = party_rewards.get(party, 0) + reward
            party_counts[party] = party_counts.get(party, 0) + 1


        # Second pass: Assign average reward to agents in each party
        for agent_id, agent_name in self.learner_names.items():
            party = self.agent_configs[int(agent_id)].party
            average_reward = party_rewards[party] / party_counts[party]
            
            self.latest_rewards[str(agent_id)] = average_reward
            # for debugging
            #print(str(agent_id),average_reward)
            self.latest_observations[agent_id] = step_res[agent_name].observation.to_array()
            self.latest_terminations[str(agent_id)] = is_terminal
            self.latest_truncations[str(agent_id)] = False
            self.latest_infos[str(agent_id)] = {}


        return (
            self.latest_observations,
            self.latest_rewards,
            self.latest_terminations,
            self.latest_truncations,
            self.latest_infos,
        )

    def reset(self, seed=None, options=None):
        self.env.reset()
        step_res = self.env.step(
            {learner_name: None for learner_name in self.learner_names.values()}
        )

        self.current_step = 0
        return {
            i: step_res[name].observation.to_array()
            for (i, name) in self.learner_names.items()
        }, {i: {} for i in self.learner_names.keys()}

    def render(self, mode="human"):
        pass

    def close(self):
        self.env.stop()

    def action_space(self, agent: AgentID):
        return self.action_spaces[agent]

    def observation_space(self, agent: AgentID):
        return self.observation_spaces[agent]

'''   
class CartelIndividualEnvWrapper:
    metadata = {'render.modes': []}
    def __init__(self, env, cartel_agents_count):
        super().__init__(env)
        self.env = env
        self.cartel_agents_count = cartel_agents_count

    def reset(self):
        obs, _ = self.env.reset()
        return self._split_observation(obs)

    def step(self, actions):
        # Combine actions into a single dictionary
        combined_actions = {str(i): act for i, act in enumerate(actions[:self.cartel_agents_count] + actions[self.cartel_agents_count:])}

        obs, rewards, dones, _, infos = self.env.step(combined_actions)

        split_obs = self._split_observation(obs)
        split_rewards = self._split_values(rewards)
        split_dones = self._split_values(dones)
        split_infos = self._split_values(infos, to_dict=True)

        return split_obs, split_rewards, split_dones, split_infos

    def render(self, mode="human"):
        self.env.render(mode)

    def close(self):
        self.env.close()

    def _split_observation(self, observation):
        cartel_obs = {k: v for i, (k, v) in enumerate(observation.items()) if i < self.cartel_agents_count}
        individual_obs = {k: v for i, (k, v) in enumerate(observation.items()) if i >= self.cartel_agents_count}
        return cartel_obs, individual_obs

    def _split_values(self, values, to_dict=False):
        cartel_values = {k: v for i, (k, v) in enumerate(values.items()) if i < self.cartel_agents_count}
        individual_values = {k: v for i, (k, v) in enumerate(values.items()) if i >= self.cartel_agents_count}
        if to_dict:
            return {'cartel': cartel_values, 'individual': individual_values}
        return cartel_values, individual_values
'''


if __name__ == "__main__":
    from pettingzoo.utils.conversions import parallel_to_aec_wrapper

    env = MultiAgentVegaEnv(
        agents=[
            AgentConfig(
                action_type=ActionType.AT_TOUCH_ONE_SIDE,
                state_type=PriceStateWithFees,
                reward_type=Reward.PNL,
                terminal_reward_type=Reward.SQ_INVENTORY_PENALTY,
            )
        ],
        steps_per_trading_session=200,
    )
    api_test(parallel_to_aec_wrapper(env), num_cycles=1, verbose_progress=True)
