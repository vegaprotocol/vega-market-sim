import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple
import os


from vega_sim.reinforcement.learning_agent import MarketState, Action, states_to_sarsa


def action_to_vector(action: Action):
    if action.sell:
        output = 0
    elif action.buy:
        output = 1
    else:
        output = 2
    return output


def plot_simulation(
    simulation: List[Tuple[MarketState, Action]], results_dir: str, tag: int
):
    """Plot the states of a learning_agent in the simulation"""
    sars = states_to_sarsa(simulation)
    reward = np.array([_sars[2] for _sars in sars])
    next_price = np.array([_sars[0].next_price for _sars in sars])
    best_bid = np.array([_sars[0].bid_prices[0] for _sars in sars])
    best_ask = np.array([_sars[0].ask_prices[0] for _sars in sars])
    position = np.array([_sars[0].position for _sars in sars])
    margin_balance = np.array([_sars[0].margin_balance for _sars in sars])
    general_balance = np.array([_sars[0].general_balance for _sars in sars])

    total_balance = np.array(
        [_sars[0].margin_balance + _sars[0].general_balance for _sars in sars]
    )
    action_discr = np.array([action_to_vector(_sars[1]) for _sars in sars])
    action_volume = np.array([_sars[1].volume for _sars in sars])
    t = np.linspace(1, len(action_volume), len(action_volume))

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))
    fig = plt.figure(figsize=(12, 12))
    spec = fig.add_gridspec(3, 2)

    ax0 = fig.add_subplot(spec[0, 0])
    ax0.plot(best_bid, label="best bid")
    ax0.plot(best_ask, label="best ask")
    ax0.plot(next_price, label="next_price")
    ax0.legend()

    ax1 = fig.add_subplot(spec[0, 1])
    ax1.plot(position, label="position")
    ax1.legend()

    ax2 = fig.add_subplot(spec[1, 0])
    ax2.plot(margin_balance, label="margin balance")
    ax2.plot(general_balance, label="general balance")
    ax2.plot(total_balance, label="total balance")
    ax2.set_yscale("log")
    ax2.legend()

    ax3 = fig.add_subplot(spec[1, 1])
    scatter = ax3.scatter(t, action_volume, c=action_discr)
    # produce a legend with the unique colors from the scatter
    handles, labels = scatter.legend_elements()
    labels = ["sell", "buy", "do nothing"]
    ax3.legend(*(handles, labels), title="Type of action")
    ax3.set_ylabel("volume")

    ax4 = fig.add_subplot(spec[2, :])
    ax4.plot(reward.cumsum(), label="cumulative reward")
    ax4.legend()
    fig.savefig(os.path.join(results_dir, "sim{}.pdf".format(tag)))
    plt.close()
    return 0
