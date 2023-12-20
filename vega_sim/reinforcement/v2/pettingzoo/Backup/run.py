import os

import torch
import numpy as np
from torch.utils.tensorboard import SummaryWriter
from pettingzoo.utils.conversions import parallel_to_aec_wrapper
from tianshou.data import Collector, VectorReplayBuffer
from tianshou.env import DummyVectorEnv, PettingZooEnv
from tianshou.policy import BasePolicy, DQNPolicy, MultiAgentPolicyManager, RandomPolicy
from tianshou.trainer import offpolicy_trainer
from tianshou.utils import TensorboardLogger
from tianshou.utils.net.common import Net

import environment as pz


def get_agents(env: pz.MultiAgentVegaEnv,hidden_layers=3, hidden_units=64):
    agents = []
    for agent in env.agents:
        model = Net(
            action_shape=env.action_spaces[agent].n,
            state_shape=(
                env.observation_spaces[agent].shape[0]
                if len(env.observation_spaces[agent].shape) > 0
                else 1
            ),
            hidden_sizes=[hidden_units for i in range(hidden_layers)],
        )
        optim = torch.optim.Adam(model.parameters())

        agents.append(DQNPolicy(model, optim))

    return agents


if __name__ == "__main__":
    env = None
    # Step 1: Load the PettingZoo environment
    try:
        agent_configs = [
            pz.AgentConfig(
                action_type=pz.ActionType.AT_TOUCH_ONE_SIDE,
                state_type=pz.PriceStateWithFees,
                reward_type=pz.Reward.PNL,
                terminal_reward_type=pz.Reward.SQ_INVENTORY_PENALTY,
                party="A",
            ),
            pz.AgentConfig(
                action_type=pz.ActionType.AT_TOUCH_ONE_SIDE,
                state_type=pz.PriceStateWithFees,
                reward_type=pz.Reward.PNL,
                terminal_reward_type=pz.Reward.SQ_INVENTORY_PENALTY,
                party="A",
            ),
            pz.AgentConfig(
                action_type=pz.ActionType.AT_TOUCH_ONE_SIDE,
                state_type=pz.PriceStateWithFees,
                reward_type=pz.Reward.PNL,
                terminal_reward_type=pz.Reward.SQ_INVENTORY_PENALTY,
                party="A",
            ),
            pz.AgentConfig(
                action_type=pz.ActionType.AT_TOUCH_ONE_SIDE,
                state_type=pz.PriceStateWithFees,
                reward_type=pz.Reward.PNL,
                terminal_reward_type=pz.Reward.SQ_INVENTORY_PENALTY,
                party="B",
            ),
        ]
        base_env = pz.MultiAgentVegaEnv(
            agents=agent_configs,
            steps_per_trading_session=750,
            trade_volume=5,
        )

        #env.reset()
        env = PettingZooEnv(parallel_to_aec_wrapper(base_env))

        # ======== tensorboard logging setup =========
        log_path = os.path.join(
            "./",
            "tianshou",
            "dqn",
        )
        writer = SummaryWriter(log_path)
        logger = TensorboardLogger(writer)

        agents = get_agents(base_env,hidden_layers=3,hidden_units=64)
        policy = MultiAgentPolicyManager(agents, env)

        # Step 4: Convert the env to vector format
        train_env = DummyVectorEnv([lambda: env])
        test_env = DummyVectorEnv([lambda: env])

        # Step 5: Construct the Collector, which interfaces the policies with the vectorised environment
        train_collector = Collector(
            policy, train_env, VectorReplayBuffer(120, 1), exploration_noise=True
        )
        test_collector = Collector(policy, test_env, exploration_noise=True)

        # Step 6: Execute the environment with the agents playing for 1 episode, and render a frame every 0.1 seconds
        train_collector.collect(n_episode=15)

        def epsilon_decay(step,EPS_START=0.75,EPS_DECAY=0.005):
            return EPS_START * np.exp(-EPS_DECAY * step)

        def save_best_fn(policy):
            agent_state_dicts = {agent_name: agent_policy.state_dict() for agent_name, agent_policy in policy.policies.items()}
            torch.save(agent_state_dicts, model_path)
            print("Model Updated")

        def stop_fn(mean_rewards):
             return mean_rewards >= 100
        
        def train_fn(epoch, env_step):
            eps = epsilon_decay(env_step)
            for p in policy.policies.values():
                p.set_eps(eps)

        def test_fn(epoch, env_step):
            eps = epsilon_decay(env_step)  # or set to a smaller constant value for testing
            for p in policy.policies.values():
                p.set_eps(eps)

        def reward_diff(rewards):
            # modified 
            return rewards[:,0]-rewards[:,3]
        
        def reward_ave(rewards):
            return rewards.sum(axis=1)
        
        def reward_single(rewards,agent="cartel"):
            #print(rewards)
            return rewards[:,0] if agent=='cartel' else rewards[:,3]
        

        # trainer
        model_path = "./dqn_model.pth"

        if os.path.exists(model_path):
            agent_state_dicts = torch.load(model_path)
            for agent_name, agent_state_dict in agent_state_dicts.items():
                policy.policies[agent_name].load_state_dict(agent_state_dict)
            print(agent_state_dicts.keys)
            print("Pre-trained models loaded")
        
        result = offpolicy_trainer(
            policy,
            train_collector,
            test_collector,
            max_epoch=200,
            step_per_epoch=1000,
            step_per_collect=10,
            episode_per_test=5,
            batch_size=64,
            train_fn=train_fn,
            test_fn=test_fn,
            reward_metric=lambda x: reward_single(x,agent='cartel'),
            # stop_fn=stop_fn,
            save_best_fn=save_best_fn,
            update_per_step=0.05,
            logger=logger,
            test_in_train=True,
        )
        
    finally:
        if env is not None:
            env.close()