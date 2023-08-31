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
    initial_fund: float = 1e5
    reward_type: Optional[Reward] = None
    terminal_reward_type: Optional[Reward] = None
    hidden_layers: int = 1
    hidden_units:int = 16
    learning_rate: float= 0.001
    target_update_freq: int = 10
    volume_multiplier: float = 1.0


class MultiAgentVegaEnv(ParallelEnv):
    """Custom Environment that follows gym interface."""

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        agents: List[AgentConfig],
        num_levels_state: int = 5,
        steps_per_trading_session: int = 1000,
        sigma=100,
        q_upper=15,
        q_lower=-15,
        initial_price=1000.0,
        lp_commitamount=1e5,
        initial_asset_mint=2e5,
        buy_intensity=10,
        sell_intensity=10,
        is_test=False,
        max_action=10,
    ):
        super().__init__()
        self.is_test= is_test
        self.num_levels_state = num_levels_state
        self.agent_configs = agents
        self.steps_per_trading_session = steps_per_trading_session
        self.current_step = 0
        self.max_action=max_action
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
        if self.is_test: print(self.action_spaces)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_spaces = {
            str(i): self._get_observation_space(state_type=agent_config.state_type)
            for (i, agent_config) in enumerate(self.agent_configs)
        }

        self._fund_list = [agent_config.initial_fund for agent_config in self.agent_configs]

        scenario = CurveMarketMaker(
            market_decimal=3,
            asset_decimal=5,
            market_position_decimal=2,
            initial_price=initial_price,
            lp_commitamount=lp_commitamount,
            initial_asset_mint=initial_asset_mint,
            step_length_seconds=1,
            block_length_seconds=1,
            buy_intensity=buy_intensity,
            sell_intensity=sell_intensity,
            market_name="ETH",
            num_steps=self.steps_per_trading_session * 2,
            random_agent_ordering=False,
            sigma=sigma,
            asset_name="DAI",
            q_upper=q_upper,
            q_lower=q_lower,
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
            fund_list=self._fund_list,
        )
        self.agents = list(self.learner_names.keys())
        self.possible_agents = self.agents

    def _get_action_space(self, action_type: ActionType) -> spaces.Space:
        if action_type == ActionType.AT_TOUCH_ONE_SIDE:
            return spaces.Box(low=-self.max_action,high=self.max_action)
        else:
            self.num_actions_side =0
            raise Exception(f"Action type {action_type} is not implemented")
        

    def _get_observation_space(self, state_type: Type[State]) -> spaces.Space:
        if state_type == PriceStateWithFees:
            return price_state_with_fees_obs_space(num_levels=self.num_levels_state)
        if state_type == PositionOnly:
            return position_state_with_fees_obs_space()

    def _convert_one_dimensional_action(self, one_dim_action):
        action_type = 0 if one_dim_action<0 else 1
        trade_volume = abs(one_dim_action)
        return (action_type, trade_volume)

    def _action_conversion(self, agent, one_dim_action):
        action = self._convert_one_dimensional_action(one_dim_action)
        agent_config = self.agent_configs[int(agent)]
        action_type, trade_volume = action

        if agent_config.action_type == ActionType.AT_TOUCH_ONE_SIDE:
            return AGENT_TYPE_TO_ACTION[AgentType.AT_TOUCH](
                side=ForcedSide(action_type), volume=trade_volume*agent_config.volume_multiplier
            )
        else:
            raise Exception(
                f"Action type {agent_config.action_type} is not implemented"
            )



    def step(self, actions):
        step_res = self.env.step(
            {
                self.learner_names[agent]: self._action_conversion(
                    one_dim_action=action, agent=agent
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
            if self.is_test==True: self.record_dict[agent_name]+=average_reward
            self.latest_observations[agent_id] = step_res[agent_name].observation.to_array()
            self.latest_terminations[str(agent_id)] = is_terminal
            self.latest_truncations[str(agent_id)] = False
            self.latest_infos[str(agent_id)] = {}
        
        if is_terminal and self.is_test:
            print(self.record_dict)


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
        # if self.is_test: print(self.current_step)
        self.current_step = 0
        if self.is_test: self.record_dict={agent_name:0 for agent_id, agent_name in self.learner_names.items()}
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


class RewardEva():
    def __init__(self,rewards,print_out=False):
        self.rewards=rewards
        if print_out:
            print(rewards.sum(axis=0)/len(rewards))

    def diff(self):
        return self.rewards[:,0]-self.rewards[:,-1]

    def ave(self):
        count=len(self.rewards[0])
        return self.rewards.sum(axis=1)/count
    
    def cartel(self):
        return self.rewards[:,0]
    
    def ind(self):
        return self.rewards[:,-1]


if __name__ == "__main__":
    import numpy as np
    rewards=np.array([[1,2,3],[4,5,6]])
    RewardEva(rewards=rewards,print_out=True)
    '''
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
    '''
