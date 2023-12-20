from tianshou.utils.net.common import Net
from tianshou.utils.net.discrete import Actor, Critic
from tianshou.policy import DiscreteSACPolicy
from typing import Optional, Tuple, Dict, Any
import torch
import environment_updated as pz


common_params_dict = {
    'trade_volume_levels': 11, 
    'sigma': 100,
    'q_upper': 20,
    'q_lower': -20,
    'initial_price': 1000.0,
    'lp_commitamount': 1e5, # the greater, the smaller the impact that agents' actions have on the market price, 1e5~1e10
    'initial_asset_mint': 2e5,
    'buy_intensity': 10,
    'sell_intensity': 10,
    'steps_per_trading_session':1000,
}

agent_configs = [
    # Cartel Agents
    pz.AgentConfig(
        action_type=pz.ActionType.AT_TOUCH_ONE_SIDE,
        state_type=pz.PriceStateWithFees,
        reward_type=pz.Reward.PNL,
        terminal_reward_type=pz.Reward.SQ_INVENTORY_PENALTY,
        party="A",
        hidden_layers=3,
        hidden_units=64,
        learning_rate=0.001, # normal range 0.01~0.001
        target_update_freq=100,
        initial_fund=5e5,
    ),
    pz.AgentConfig(
        action_type=pz.ActionType.AT_TOUCH_ONE_SIDE,
        state_type=pz.PriceStateWithFees,
        reward_type=pz.Reward.PNL,
        terminal_reward_type=pz.Reward.SQ_INVENTORY_PENALTY,
        party="A",
        hidden_layers=3,
        hidden_units=64,
        learning_rate=0.001,
        target_update_freq=100,
        initial_fund=5e5,
    ),
    # Inidividual Agents
    pz.AgentConfig(
        action_type=pz.ActionType.AT_TOUCH_ONE_SIDE,
        state_type=pz.PriceStateWithFees,
        reward_type=pz.Reward.PNL,
        terminal_reward_type=pz.Reward.SQ_INVENTORY_PENALTY,
        party="B",
        hidden_layers=3,
        hidden_units=64,
        learning_rate=0.001,
        target_update_freq=100,
        initial_fund=5e5,
    ),
    # Less-intelligent Agents
    pz.AgentConfig(
        action_type=pz.ActionType.AT_TOUCH_ONE_SIDE,
        state_type=pz.PriceStateWithFees,
        reward_type=pz.Reward.PNL,
        terminal_reward_type=pz.Reward.SQ_INVENTORY_PENALTY,
        party="SL", # short for Sacrificial Lamb
        hidden_layers=1,
        hidden_units=16,
        learning_rate=0.001,
        target_update_freq=5,
        initial_fund=5e3,
    ),
]

def get_agents(env: pz.MultiAgentVegaEnv):
    agents = []
    for (i, agent_config) in enumerate(env.agent_configs):
        agent=env.agents[i]
        state_shape=(
                env.observation_spaces[agent].shape[0]
                if len(env.observation_spaces[agent].shape) > 0
                else 1
        )
        num_actions_side = env.action_spaces[agent][0].n
        num_actions_trade_volume = env.action_spaces[agent][1].n
        total_actions = num_actions_side * num_actions_trade_volume

        actor_net = Net(
            state_shape,
            total_actions,
            hidden_sizes=[agent_config.hidden_units * 2**(i%2) for i in range(agent_config.hidden_layers)],
        )
        critic_net=Net(
            state_shape,
            total_actions,
            hidden_sizes=[agent_config.hidden_units * 2**(i%2) for i in range(agent_config.hidden_layers)],
        )

        # Actor Network
        actor = Actor(preprocess_net=actor_net,action_shape=total_actions)
        
        # Twin Critic Networks
        critic1 = Critic(preprocess_net=critic_net)
        critic2 = Critic(preprocess_net=critic_net)

        optim_policy = torch.optim.Adam(actor.parameters(), lr=agent_config.learning_rate)
        optim_critic1 = torch.optim.Adam(critic1.parameters(), lr=agent_config.learning_rate)
        optim_critic2 = torch.optim.Adam(critic2.parameters(), lr=agent_config.learning_rate)

        policy = DiscreteSACPolicy(
            actor=actor, critic1=critic1, critic2=critic2,
            actor_optim=optim_policy, critic1_optim=optim_critic1, critic2_optim=optim_critic2,
            gamma=0.95, tau=0.005,
            reward_normalization=True
        )

        agents.append(policy)
        if i==0:
            print("Actor Net")
            print(actor)
            print("Critic Net")
            print(critic1)

    return agents