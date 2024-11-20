import os

import torch
import pickle
import numpy as np
from datetime import datetime
from torch.utils.tensorboard import SummaryWriter
from pettingzoo.utils.conversions import parallel_to_aec_wrapper
from tianshou.data import Collector, VectorReplayBuffer
from tianshou.policy import MultiAgentPolicyManager,DQNPolicy
from tianshou.env import DummyVectorEnv, PettingZooEnv
from tianshou.trainer import offpolicy_trainer
from tianshou.utils import TensorboardLogger


import environment_updated as pz
from AC_configs import agent_configs,get_agents, common_params_dict

def train(max_epoch=200,step_per_epoch=500,step_per_collect=2,episode_per_test=9,batch_size=64,update_per_step=0.05,
          n_replay=120,n_train_collector_init=20,
          trade_volume_levels=11,sigma=100,q_upper=15,q_lower=-15,
          initial_price=1000.0,lp_commitamount=1e5,initial_asset_mint=2e5,
          buy_intensity=10,sell_intensity=10,
          steps_per_trading_session=500,
          load_model=False,model_name='dqn_model_training.pth',resume=False):
    env = None
    # Step 1: Load the PettingZoo environment
    try:
        #env.reset()
        base_env = pz.MultiAgentVegaEnv(
            agents=agent_configs,
            steps_per_trading_session=steps_per_trading_session,
            trade_volume_levels=trade_volume_levels,
            sigma=sigma,
            q_upper=q_upper,
            q_lower=q_lower,
            initial_price=initial_price,
            lp_commitamount=lp_commitamount,
            initial_asset_mint=initial_asset_mint,
            buy_intensity=buy_intensity,
            sell_intensity=sell_intensity,
        )
        env = PettingZooEnv(parallel_to_aec_wrapper(base_env))

        # ======== tensorboard logging setup =========
        log_path = os.path.join(
            "./",
            "tianshou",
            "dqn",
        )
        writer = SummaryWriter(log_path)
        logger = TensorboardLogger(writer)

        agents = get_agents(base_env)
        policy = MultiAgentPolicyManager(agents, env)

        # Step 4: Convert the env to vector format
        train_env = DummyVectorEnv([lambda: env])
        test_env = DummyVectorEnv([lambda: env])

        # Step 5: Construct the Collector, which interfaces the policies with the vectorised environment
        train_collector = Collector(
            policy, train_env, VectorReplayBuffer(n_replay, 1), exploration_noise=True
        )
        test_collector = Collector(policy, test_env, exploration_noise=True)
        
        date_time = datetime.now().strftime("DATE%m-%d_TIME%H-%M")
        save_path = f"./models/training_{date_time}.pth"

        def save_best_fn(policy):
            agent_state_dicts = {agent_name: agent_policy.state_dict() for agent_name, agent_policy in policy.policies.items()}
            optim_state_dicts = {agent_name: {'actor_optim': agent_policy.actor_optim.state_dict(), 'critic1_optim': agent_policy.critic1_optim.state_dict(), 'critic2_optim': agent_policy.critic2_optim.state_dict()} for agent_name, agent_policy in policy.policies.items()}
            torch.save(
                {
                    "model": agent_state_dicts,
                    "optim": optim_state_dicts,
                },
                save_path,
            )
            print("Model Updated: Saved to", save_path)

        def save_checkpoint_fn(epoch, env_step, gradient_step):
            ckpt_path = './models/checkpoint.pth'
            agent_state_dicts = {agent_name: agent_policy.state_dict() for agent_name, agent_policy in policy.policies.items()}
            optim_state_dicts = {agent_name: {'actor_optim': agent_policy.actor_optim.state_dict(), 'critic1_optim': agent_policy.critic1_optim.state_dict(), 'critic2_optim': agent_policy.critic2_optim.state_dict()} for agent_name, agent_policy in policy.policies.items()}
            torch.save(
                {
                    "model": agent_state_dicts,
                    "optim": optim_state_dicts,
                },
                ckpt_path,
            )
            buffer_path = './models/train_buffer.pkl'
            pickle.dump(train_collector.buffer, open(buffer_path, "wb"))
            return ckpt_path

        
        # pre-trained model loading 
        if load_model:
            ckpt_path = "./models/"+model_name
            buffer_path = './models/train_buffer.pkl'
        else: ckpt_path =None
        try:
            load=torch.load(ckpt_path)
            print('Check point loaded')
            agent_state_dicts = load["model"]
            optim_state_dicts = load["optim"]
            for agent_name, agent_state_dict in agent_state_dicts.items():
                policy.policies[agent_name].load_state_dict(agent_state_dict)
            print("Pre-trained models loaded")
            for agent_name, optim_state_dict in optim_state_dicts.items():
                agent_policy = policy.policies[agent_name]
                agent_policy.actor_optim.load_state_dict(optim_state_dict['actor_optim'])
                agent_policy.critic1_optim.load_state_dict(optim_state_dict['critic1_optim'])
                agent_policy.critic2_optim.load_state_dict(optim_state_dict['critic2_optim'])
            print("Optim loaded")
            train_collector.buffer = pickle.load(open(buffer_path, "rb"))
            print("Successfully restore buffer.")
        except: 
            print("New model applied")
        
        def train_fn(epoch, env_step):
            pass

        def test_fn(epoch, env_step):
            pass
        
        if resume==False: train_collector.collect(n_episode=n_train_collector_init)
        reward_fn=lambda rewards: pz.RewardEva(rewards=rewards,print_out=True).ave()
        result = offpolicy_trainer(
            policy,
            train_collector,
            test_collector,
            max_epoch=max_epoch,
            step_per_epoch=step_per_epoch,
            step_per_collect=step_per_collect,
            episode_per_test=episode_per_test,
            batch_size=batch_size,
            update_per_step=update_per_step,
            train_fn=train_fn,
            test_fn=test_fn,
            reward_metric=reward_fn, 
            # stop_fn=stop_fn,
            save_best_fn=save_best_fn,
            logger=logger,
            test_in_train=True,
            save_checkpoint_fn=save_checkpoint_fn,
            resume_from_log=resume,
        )
        
    finally:
        if env is not None:
            env.close()

if __name__ == "__main__":

    train(max_epoch=300,
          step_per_epoch=1000,step_per_collect=5,episode_per_test=4,
          batch_size=128,update_per_step=0.01, n_replay=10000,n_train_collector_init=25,
          load_model=True,model_name='checkpoint.pth', resume=True,
          **common_params_dict
        )
    '''
    train(max_epoch=10,
          step_per_epoch=100,step_per_collect=5,episode_per_test=1,
          batch_size=10,update_per_step=0.05, n_replay=100,n_train_collector_init=1,
          load_model=True,model_name='checkpoint.pth', resume=True,
          **common_params_dict)
    '''