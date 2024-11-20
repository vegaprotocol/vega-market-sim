from tianshou.data import Collector
from tianshou.policy import MultiAgentPolicyManager,DQNPolicy
from tianshou.env import DummyVectorEnv, PettingZooEnv
from pettingzoo.utils.conversions import parallel_to_aec_wrapper
import torch
import matplotlib.pyplot as plt

import CAC_environment as pz
from CAC_configs import agent_configs, get_agents,common_params_dict

# Define the function to test the saved model
def test_model(policy,env,n_ep=20):
    # Create a test collector for testing
    test_env = DummyVectorEnv([lambda: env])
    test_collector = Collector(policy, test_env, exploration_noise=not True)

    # Collect results from test episodes
    results = test_collector.collect(n_episode=n_ep)
    test_collector.reset()

    # Compute different reward metrics
    rewards = results['rews'].sum(axis=0)/n_ep
    #print(results['lens'])

    # Print or save the computed reward metrics
    return rewards

def main_test(model_file='dqn_model_saved.pth',n_ep=5,n_iter=10,print_original=False):
    model_path = "./models/"+model_file

    # Load model
    base_env=pz.MultiAgentVegaEnv(
    agents=agent_configs,
    is_test=print_original,
    **common_params_dict
    )
    party_list=[agent_config.party for agent_config in agent_configs]
    env = PettingZooEnv(parallel_to_aec_wrapper(base_env))
    agents = get_agents(base_env)
    policy = MultiAgentPolicyManager(agents, env)

    try:
        agent_state_dicts = torch.load(model_path)['model']
        for agent_name, agent_state_dict in agent_state_dicts.items():
                # print(agent_state_dict)
                policy.policies[agent_name].load_state_dict(agent_state_dict)       
        print("Pre-trained models loaded")
    except: pass

    # Run the testing function
    rew,index=[],[]
    for _ in range(n_iter):
        print("----------Test Iter %d----------" % (_+1))
        result=test_model(policy=policy,env=env,n_ep=n_ep)
        print(['Party %s: %.3f' % (party_list[i],result[i]) for i in range(len(result))])
        rew.append(result)
        index.append(_)

    if env is not None:
            env.close()

    # visualisation
    for i in range(len(result)):
        data=[row[i] for row in rew]
        print(data)
        plt.plot(index,data,label="Party %s" % party_list[i])
    plt.legend()
    plt.savefig("./models/figures/"+model_file[:-4]+'_test.png')
    plt.show()

if __name__ == "__main__":
    main_test(model_file='training_DATE08-26_TIME01-43.pth',n_ep=1,n_iter=20,
              print_original=True)