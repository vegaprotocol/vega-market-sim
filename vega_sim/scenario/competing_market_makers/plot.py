import argparse

from vega_sim.tools.scenario_plots import plot_account_by_party

import vega_sim.proto.vega as vega_protos


import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec


def init_liquidation_analysis_figure() -> Figure:
    fig = plt.figure(figsize=[11.69, 8.27])
    fig.suptitle(
        f"Tau Scaling Analysis",
        fontsize=18,
        fontweight="bold",
        color=(0.2, 0.2, 0.2),
    )
    fig.tight_layout()

    gs = GridSpec(
        nrows=2,
        ncols=1,
        hspace=0.3,
    )
    return fig, gs


if __name__ == "__main__":
    fig: Figure = None
    (fig, gs) = init_liquidation_analysis_figure()

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--runs", nargs="+")
    args = parser.parse_args()

    plot_account_by_party(
        run_name=args.runs[0],
        fig=fig,
        ss=gs[0, 0],
        account_type=vega_protos.vega.ACCOUNT_TYPE_LP_LIQUIDITY_FEES,
    )
    plot_account_by_party(
        run_name=args.runs[1],
        fig=fig,
        ss=gs[1, 0],
        account_type=vega_protos.vega.ACCOUNT_TYPE_LP_LIQUIDITY_FEES,
    )
    axes = fig.get_axes()
    for ax in axes:
        ax.set_ylim(bottom=0, top=6000)
    axes[0].set_title(
        "market.liquidity.probabilityOfTrading.tau.scaling=1",
        loc="left",
        fontsize=12,
        color=(0.3, 0.3, 0.3),
    )
    axes[1].set_title(
        "market.liquidity.probabilityOfTrading.tau.scaling=10",
        loc="left",
        fontsize=12,
        color=(0.3, 0.3, 0.3),
    )

    plt.show()
