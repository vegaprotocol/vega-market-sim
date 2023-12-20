from tianshou.utils.net.common import Net
from tianshou.utils.net.continuous import ActorProb, Critic, Actor
from tianshou.policy import SACPolicy
from tianshou.exploration import GaussianNoise
from typing import Optional, Tuple, Dict, Any
import torch
import CAC_environment as pz


max_action=1
common_params_dict = {
    'sigma': 100,
    'q_upper': 20,
    'q_lower': -20,
    'initial_price': 1000.0,
    'lp_commitamount': 1e5, # the greater, the smaller the impact that agents' actions have on the market price, 1e5~1e10
    'initial_asset_mint': 2e5,
    'buy_intensity': 10,
    'sell_intensity': 10,
    'steps_per_trading_session':1000,
    'max_action' : max_action
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
        initial_fund=1e4,
        volume_multiplier=10,
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
        initial_fund=1e4,
        volume_multiplier=10,
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
        initial_fund=1e4,
        volume_multiplier=10,
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
        initial_fund=1e4,
        volume_multiplier=10, # pettingzoo requites identical action spaces? possible to find one that support different action spaces?
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
        action_shape = env.action_spaces[agent].shape[0]
        hidden_sizes=[agent_config.hidden_units // 2**(i) for i in range(agent_config.hidden_layers)]

        if agent_config.party=='SL':
            actor_net = Net(
            state_shape,
            hidden_sizes[0],
            hidden_sizes=[16],
            )
            critic_net=Net(
            state_shape+action_shape,
            hidden_sizes[0],
            hidden_sizes=[16],
            )
        else:
            actor_net = Net(
            state_shape,
            hidden_sizes[0],
            hidden_sizes=[128],
            )
            critic_net=Net(
            state_shape+action_shape,
            hidden_sizes[0],
            hidden_sizes=[128,96],
            )

        # Actor Network
        actor = ActorProb(preprocess_net=actor_net,action_shape=action_shape, conditioned_sigma=True,
                          max_action=max_action, hidden_sizes=hidden_sizes,unbounded=False)
        
        # Twin Critic Networks
        critic1 = Critic(preprocess_net=critic_net,hidden_sizes=hidden_sizes)
        critic2 = Critic(preprocess_net=critic_net,hidden_sizes=hidden_sizes)

        optim_policy = torch.optim.Adam(actor.parameters(), lr=agent_config.learning_rate)
        optim_critic1 = torch.optim.Adam(critic1.parameters(), lr=agent_config.learning_rate)
        optim_critic2 = torch.optim.Adam(critic2.parameters(), lr=agent_config.learning_rate)

        policy = SACPolicy(
            actor=actor, critic1=critic1, critic2=critic2,
            actor_optim=optim_policy, critic1_optim=optim_critic1, critic2_optim=optim_critic2,
            gamma=0.95, tau=0.01, alpha=0.2, deterministic_eval= False,
            reward_normalization=True, action_space=env.action_spaces[agent],
            lr_scheduler=None,  action_scaling=True, exploration_noise=GaussianNoise(mu=0,sigma=1/5),
            action_bound_method='clip',
        )

        agents.append(policy)
        if i==0 or i==len(env.agent_configs)-1:
            print("Actor Net")
            print(actor)
            print("Critic Net")
            print(critic1)

    return agents