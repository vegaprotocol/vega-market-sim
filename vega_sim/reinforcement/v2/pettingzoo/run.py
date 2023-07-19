import os

import torch
from torch.utils.tensorboard import SummaryWriter
from pettingzoo.utils.conversions import parallel_to_aec_wrapper
from tianshou.data import Collector, VectorReplayBuffer
from tianshou.env import DummyVectorEnv, PettingZooEnv
from tianshou.policy import BasePolicy, DQNPolicy, MultiAgentPolicyManager, RandomPolicy
from tianshou.trainer import offpolicy_trainer
from tianshou.utils import TensorboardLogger
from tianshou.utils.net.common import Net

import vega_sim.reinforcement.v2.pettingzoo.environment as pz


def get_agents(env: pz.MultiAgentVegaEnv):
    agents = []
    for agent in env.agents:
        model = Net(
            action_shape=env.action_spaces[agent].n,
            state_shape=(
                env.observation_spaces[agent].shape[0]
                if len(env.observation_spaces[agent].shape) > 0
                else 1
            ),
            hidden_sizes=[10],
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
                # reward_type=pz.Reward.PNL,
                # terminal_reward_type=pz.Reward.SQ_INVENTORY_PENALTY,
            ),
            pz.AgentConfig(
                action_type=pz.ActionType.AT_TOUCH_ONE_SIDE,
                state_type=pz.PriceStateWithFees,
                # reward_type=pz.Reward.PNL,
                # terminal_reward_type=pz.Reward.SQ_INVENTORY_PENALTY,
            ),
        ]
        base_env = pz.MultiAgentVegaEnv(
            agents=agent_configs,
            steps_per_trading_session=200,
            unified_reward=pz.Reward.UNIFIED_PNL,
        )

        # Step 2: Wrap the environment for Tianshou interfacing
        # env.reset()
        env = PettingZooEnv(parallel_to_aec_wrapper(base_env))
        # Step 3: Define policies for each agent
        agents = get_agents(base_env)
        policy = MultiAgentPolicyManager(agents, env)

        # Step 4: Convert the env to vector format
        train_env = DummyVectorEnv([lambda: env])
        test_env = DummyVectorEnv([lambda: env])

        # Step 5: Construct the Collector, which interfaces the policies with the vectorised environment
        train_collector = Collector(
            policy, train_env, VectorReplayBuffer(100, 1), exploration_noise=True
        )
        test_collector = Collector(policy, test_env, exploration_noise=True)

        # Step 6: Execute the environment with the agents playing for 1 episode, and render a frame every 0.1 seconds
        train_collector.collect(n_episode=10)

        def save_best_fn(policy):
            pass

        # def stop_fn(mean_rewards):
        #     return mean_rewards >= 100

        def train_fn(epoch, env_step):
            for p in policy.policies.values():
                p.set_eps(0.1)

        def test_fn(epoch, env_step):
            for p in policy.policies.values():
                p.set_eps(0.05)

        def reward_fn(rewards):
            return rewards.sum(axis=1)

        # ======== tensorboard logging setup =========
        log_path = os.path.join(
            "./",
            "tianshou",
            "dqn",
        )
        writer = SummaryWriter(log_path)
        logger = TensorboardLogger(writer)

        # trainer
        result = offpolicy_trainer(
            policy,
            train_collector,
            test_collector,
            max_epoch=300,
            step_per_epoch=600,
            step_per_collect=50,
            episode_per_test=3,
            batch_size=64,
            train_fn=train_fn,
            test_fn=test_fn,
            reward_metric=reward_fn,
            # stop_fn=stop_fn,
            save_best_fn=save_best_fn,
            update_per_step=0.1,
            logger=logger,
            test_in_train=False,
        )
    finally:
        if env is not None:
            env.close()
