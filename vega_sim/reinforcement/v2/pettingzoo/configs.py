import environment_updated as pz
from tianshou.utils.net.common import Net
from tianshou.policy import BasePolicy, DQNPolicy
from tianshou.data import Batch
from typing import Optional, Tuple, Dict, Any
import torch


common_params_dict = {
    'trade_volume_levels': 11, 
    'sigma': 100,
    'q_upper': 20,
    'q_lower': -20,
    'initial_price': 1000.0,
    'lp_commitamount': 1.5e5, # the greater, the greater the impact that agents' actions have on the market price, 1e5~1e10
    'initial_asset_mint': 2e5,
    'buy_intensity': 10,
    'sell_intensity': 10,
    'steps_per_trading_session':750,
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
        learning_rate=0.01, # normal range 0.01~0.001
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
        learning_rate=0.01,
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
        learning_rate=0.01,
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
        learning_rate=0.01,
        target_update_freq=5,
        initial_fund=5e3,
    ),
]

def get_agents(env: pz.MultiAgentVegaEnv):
    agents = []
    for (i, agent_config) in enumerate(env.agent_configs):
        agent=env.agents[i]
        num_actions_side = env.action_spaces[agent][0].n
        num_actions_trade_volume = env.action_spaces[agent][1].n
        total_actions = num_actions_side * num_actions_trade_volume

        model = Net(
            action_shape=total_actions,
            state_shape=(
                env.observation_spaces[agent].shape[0]
                if len(env.observation_spaces[agent].shape) > 0
                else 1
            ),
            hidden_sizes=[agent_config.hidden_units*2**(i%2) for i in range(agent_config.hidden_layers)],
        )
        optim = torch.optim.Adam(model.parameters(),lr=agent_config.learning_rate)
        if agent_config.party=="SL":
            scheduler = torch.optim.lr_scheduler.StepLR(optim, step_size=10, gamma=0.1)
        else:
            scheduler = torch.optim.lr_scheduler.StepLR(optim, step_size=5, gamma=0.8)
        agents.append(DQNPolicy(model, optim,
                                target_update_freq=agent_config.target_update_freq,reward_normalization=True,
                                is_double=True, discount_factor=0.9, estimation_step=3, lr_scheduler=scheduler))
        print(model)

    return agents