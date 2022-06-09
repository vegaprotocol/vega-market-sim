import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple
import os


from reinforcement.learning_agent import MarketState, Action, states_to_sarsa


def action_to_vector(action: Action):
    if action.sell:
        output = 0
    elif action.buy:
        output = 1
    else:
        output = 2
    return output

def plot_simulation(simulation: List[Tuple[MarketState, Action]],
    results_dir: str,
    tag: int):
    """Plot the states of a learning_agent in the simulation
    """
    sars = states_to_sarsa(simulation)
    reward = np.array([_sars[2] for _sars in sars])
    next_price = np.array([_sars[0].next_price for _sars in sars])
    best_bid = np.array([_sars[0].bid_prices[0] for _sars in sars])
    best_ask = np.array([_sars[0].ask_prices[0] for _sars in sars])
    position = np.array([_sars[0].position for _sars in sars])
    total_balance = np.array([_sars[0].margin_balance + _sars[0].general_balance
        for _sars in sars])
    action_discr = np.array([action_to_vector(_sars[1]) for _sars in sars]) 
    action_volume = np.array([_sars[1].volume for _sars in sars])
    t = np.linspace(1,len(action_volume), len(action_volume))

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(12,8))
    ax[0,0].plot(best_bid, label="best bid")
    ax[0,0].plot(best_ask, label="best ask")
    ax[0,0].plot(next_price, label="next_price")
    ax[0,0].legend()
    ax[0,1].plot(position, label="position")
    ax[0,1].legend()
    scatter = ax[1,0].scatter(t, action_volume, c=action_discr)
    # produce a legend with the unique colors from the scatter
    handles, labels = scatter.legend_elements()
    labels = ['sell', 'buy', 'do nothing']
    ax[1,0].legend(*(handles, labels), title="Type of action")
    ax[1,0].set_ylabel("volume")
    ax[1,1].plot(reward.cumsum(), label="cumulative reward")
    ax[1,1].legend()
    fig.savefig(os.path.join(results_dir, "sim{}.pdf".format(tag)))
    plt.close()
    return 0

