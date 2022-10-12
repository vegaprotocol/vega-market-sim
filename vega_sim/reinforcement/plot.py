import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Tuple
from scipy.stats import norm
import os


from vega_sim.reinforcement.la_market_state import LAMarketState, states_to_sarsa
from vega_sim.reinforcement.agents.learning_agent_MO_with_vol import Action


def action_to_vector(action: Action):
    if action.sell:
        output = 0
    elif action.buy:
        output = 1
    else:
        output = 2
    return output


def plot_simulation(
    simulation: List[Tuple[LAMarketState, Action]], results_dir: str, tag: int
):
    """Plot the states of a learning_agent in the simulation"""
    sars = states_to_sarsa(simulation)
    reward = np.array([_sars[2] for _sars in sars])
    next_price_list = [_sars[0].next_price for _sars in sars]
    next_price_list.insert(0, next_price_list[0])
    next_price = np.array(next_price_list)
    best_bid = np.array([_sars[0].bid_prices[0] for _sars in sars])
    best_bid[-1] = best_bid[-2]  # because at settlement it's `0` and messes up the plot
    best_ask = np.array([_sars[0].ask_prices[0] for _sars in sars])
    best_ask[-1] = best_ask[-2]  # because at settlement it's `0` and messes up the plot
    position = np.array([_sars[0].position for _sars in sars])

    total_balance = np.array([_sars[0].full_balance for _sars in sars])
    # action_discr = np.array([action_to_vector(_sars[1]) for _sars in sars])
    # action_volume = np.array([_sars[1].volume for _sars in sars])
    # t = np.linspace(1, len(action_volume), len(action_volume))

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))
    fig = plt.figure(figsize=(12, 12))
    spec = fig.add_gridspec(3, 2)

    ax0 = fig.add_subplot(spec[0, 0])
    ax0.plot(best_bid, label="best bid")
    ax0.plot(best_ask, label="best ask")
    ax0.plot(next_price, label="next_price")
    ax0.legend()

    ax1 = fig.add_subplot(spec[0, 1])
    ax1.plot(position, "x", label="position")
    ax1.legend()

    ax2 = fig.add_subplot(spec[1, 0])
    ax2.plot(total_balance, ".", label="total balance")
    ax2.set_yscale("log")
    ax2.legend()

    # ax3 = fig.add_subplot(spec[1, 1])
    # scatter = ax3.scatter(t, action_volume, c=action_discr)
    # produce a legend with the unique colors from the scatter
    # handles, labels = scatter.legend_elements()
    # labels = ["buy", "sell", "do nothing"]
    # ax3.legend(*(handles, labels), title="Type of action")
    # ax3.set_ylabel("volume")

    ax4 = fig.add_subplot(spec[2, :])
    ax4.plot(reward.cumsum(), label="cumulative reward")
    ax4.legend()
    fig.savefig(os.path.join(results_dir, "sim{}.pdf".format(tag)))
    plt.close()


def plot_learning(results_dir: str, logfile_pol_imp: str, logfile_pol_eval: str):

    data = pd.read_csv(logfile_pol_imp)
    plt.figure()
    plt.plot(data["iteration"], data["loss"])
    plt.ylabel("KL(policy|e^Q)")
    plt.xlabel("Iteration")
    plt.title("Policy improvement")

    plt.savefig(os.path.join(results_dir, "learn_pol_imp.pdf"))
    plt.close()

    data = pd.read_csv(logfile_pol_eval)
    plt.figure()
    plt.plot(data["iteration"], np.log(data["loss"]))
    plt.ylabel("log: Bellman error est")
    plt.xlabel("Iteration")
    plt.title("Q-function estimation")
    plt.savefig(os.path.join(results_dir, "learn_pol_eval.pdf"))
    plt.close()


def plot_pnl(results_dir: str, logfile_pnl: str):
    data = pd.read_csv(logfile_pnl)
    pnl = data["pnl"].to_numpy()
    plt.figure()
    n, bins, patches = plt.hist(x=pnl, bins=20, color="#0504aa", alpha=0.7, rwidth=0.85)
    plt.grid(axis="y", alpha=0.75)
    plt.xlabel("PnL")
    plt.ylabel("Frequency")
    conf = 0.975
    err_bar = norm.ppf(conf) * pnl.std() / len(pnl)
    text = str(pnl.mean() - err_bar) + " < PnL < " + str(pnl.mean() + err_bar)
    plt.title(text)
    maxfreq = n.max()
    # Set a clean upper y-axis limit.
    plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)
    plt.savefig(os.path.join(results_dir, "learn_pnl.pdf"))
    plt.close()
