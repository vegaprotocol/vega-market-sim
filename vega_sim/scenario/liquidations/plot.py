import argparse
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from vega_sim.tools.scenario_plots import price_series_plot, liquidation_plot


def init_liquidation_analysis_figure() -> Figure:
    fig = plt.figure(figsize=[11.69, 8.27])
    fig.suptitle(
        f"Liquidation Analysis",
        fontsize=18,
        fontweight="bold",
        color=(0.2, 0.2, 0.2),
    )
    fig.tight_layout()

    gs = GridSpec(
        nrows=1,
        ncols=2,
        hspace=0.3,
    )
    return fig, gs


if __name__ == "__main__":
    fig: Figure = None
    (fig, gs) = init_liquidation_analysis_figure()

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--run")
    args = parser.parse_args()

    # Slot 1 - Market Depth Plot
    price_series_plot(
        run_name=args.run,
        fig=fig,
        ss=gs[0, 0],
        overlay_mid=True,
        overlay_bounds=True,
        overlay_auctions=True,
    )
    # Slot 2 - Liquidation Plots
    liquidation_plot(run_name=args.run, fig=fig, ss=gs[0, 1])

    axes = fig.get_axes()
    axes[0].sharex(axes[-1])

    plt.show()
