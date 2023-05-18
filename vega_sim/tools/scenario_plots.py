import os
import ast

import pandas as pd
import matplotlib.pyplot as plt
import vega_sim.proto.vega as vega_protos

from typing import Optional
from collections import defaultdict
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.markers import MarkerStyle
from matplotlib.gridspec import GridSpec, SubplotSpec, GridSpecFromSubplotSpec

from vega_sim.scenario.fuzzed_markets.agents import (
    FuzzingAgent,
    FuzzyLiquidityProvider,
    DegenerateTrader,
    DegenerateLiquidityProvider,
)

from vega_sim.proto.vega import markets

import numpy as np


TRADING_MODE_COLORS = {
    0: (200 / 255, 200 / 255, 200 / 255),
    1: (204 / 255, 255 / 255, 15 / 2553),
    2: (255 / 255, 204 / 255, 153 / 255),
    3: (153 / 255, 204 / 255, 244 / 255),
    4: (255 / 255, 133 / 255, 133 / 255),
    5: (255 / 255, 204 / 255, 255 / 255),
}


"""
Thoughts for plots
    - Total LP Margin positions
    - Market State
"""

from vega_sim.tools.scenario_output import (
    load_accounts_df,
    load_market_data_df,
    load_order_book_df,
    load_trades_df,
    load_fuzzing_df,
    load_agents_df,
)


def _set_xticks(ax, index, freq: int = 60):
    xaxis_ticks = index[0:-1:freq]
    labels = [dt.strftime("%H:%M:%S") for dt in xaxis_ticks.to_pydatetime()]
    ax.set_xticks(
        xaxis_ticks,
        labels=labels,
        rotation=45,
    )


def _order_book_df_to_heatmap_df(order_book_df: pd.DataFrame) -> pd.DataFrame:
    book_data_df = order_book_df.reset_index()[["time", "price", "volume"]].copy()

    min_pr = order_book_df.price.min()
    max_pr = order_book_df.price.max()
    int_range = pd.interval_range(start=min_pr, end=max_pr, freq=0.1)
    book_data_df["interval"] = pd.cut(book_data_df.price, bins=int_range)
    book_data_df = (
        book_data_df.groupby(["time", "interval"])[["volume"]].sum().sort_index()
    )
    idx = pd.MultiIndex.from_product(
        [
            book_data_df.index.get_level_values(0).unique(),
            book_data_df.index.get_level_values(1).unique(),
        ],
        names=["time", "interval"],
    )

    return (
        book_data_df.reindex(idx, fill_value=0)
        .sort_index(ascending=[True, False])
        .unstack(level=-1)
        .transpose()
        .sort_index(ascending=False)
        .values
    )


def plot_trading_summary(
    ax: Axes,
    trade_df: pd.DataFrame,
    order_book_df: pd.DataFrame,
    price_df: pd.DataFrame,
) -> None:
    if any(df.empty for df in (trade_df, order_book_df, price_df)):
        return
    buys = trade_df[trade_df.aggressor == 1]
    sells = trade_df[trade_df.aggressor == 2]

    heatmap_df = _order_book_df_to_heatmap_df(order_book_df=order_book_df)

    ax.set_title("Trading Summary")

    ax.imshow(
        heatmap_df,
        interpolation="none",
        aspect="auto",
        extent=(
            int(price_df.index[0].value / 1e9),
            int(price_df.index[-1].value / 1e9),
            order_book_df.price.min(),
            order_book_df.price.max(),
        ),
    )
    x_ticks = [t.value / 1e9 for t in price_df.index]
    ax.plot(x_ticks, price_df["price"])
    ax.scatter(
        buys["seen_at"], buys["price"], marker=MarkerStyle("x").scaled(0.5), c="red"
    )
    ax.scatter(
        sells["seen_at"], sells["price"], marker=MarkerStyle("s").scaled(0.5), c="blue"
    )
    ax.set_xticks(
        x_ticks[0:-1:60],
        labels=[
            dt.strftime("%H:%M:%S") for dt in price_df.index.to_pydatetime()[0:-1:60]
        ],
        rotation=45,
    )


def plot_total_traded_volume(ax: Axes, trades_df: pd.DataFrame) -> None:
    if trades_df.empty:
        return
    ax.set_title("Traded Volume")
    traded = trades_df.groupby(level=0)["size"].sum().cumsum()

    _set_xticks(ax, traded.index)

    ax.plot(traded)


def plot_open_interest(ax: Axes, market_data_df: pd.DataFrame):
    ax.set_title("Open Interest")

    _set_xticks(ax, market_data_df.index)
    ax.plot(market_data_df["open_interest"])


def plot_open_notional(
    ax: Axes,
    market_data_df: pd.DataFrame,
    price_df: pd.DataFrame,
) -> None:
    if any(df.empty for df in (market_data_df, price_df)):
        return
    ax.set_title("Open Notional $")

    _set_xticks(ax, market_data_df.index)
    ax.plot(market_data_df["open_interest"] * price_df["price"])


def plot_spread(ax: Axes, order_book_df: pd.DataFrame) -> None:
    if order_book_df.empty:
        return
    ax.set_title("10s Rolling Avg Spread")

    spread_df = (
        order_book_df[order_book_df.level == 0]
        .groupby(level=0)["price"]
        .diff()
        .dropna()
        .rolling(10)
        .mean()
    )

    _set_xticks(ax, spread_df.index)
    ax.plot(spread_df)


def plot_margin_totals(ax: Axes, accounts_df: pd.DataFrame) -> None:
    if accounts_df.empty:
        return
    ax.set_title("Total Margin Balance")
    grouped_df = (
        accounts_df[accounts_df.type == vega_protos.vega.ACCOUNT_TYPE_MARGIN]
        .groupby(level=0)[["balance"]]
        .sum()
        .iloc[1:]
    )
    _set_xticks(ax, grouped_df.index)
    ax.plot(grouped_df)


def plot_target_stake(ax: Axes, market_data_df: pd.DataFrame) -> None:
    if market_data_df.empty:
        return
    ax.set_title("Target Stake")

    _set_xticks(ax, market_data_df.index)
    ax.plot(market_data_df["target_stake"])


def plot_run_outputs(run_name: Optional[str] = None) -> list[Figure]:
    order_df = load_order_book_df(run_name=run_name)
    trades_df = load_trades_df(run_name=run_name)
    data_df = load_market_data_df(run_name=run_name)
    accounts_df = load_accounts_df(run_name=run_name)

    figs = {}

    for market_id in data_df["market_id"].unique():
        market_order_df = order_df[order_df["market_id"] == market_id]
        market_trades_df = trades_df[trades_df["market_id"] == market_id]
        market_data_df = data_df[data_df["market_id"] == market_id]
        market_accounts_df = accounts_df[accounts_df["market_id"] == market_id]

        market_mid_df = (
            market_order_df[market_order_df.level == 0].groupby("time")[["price"]].sum()
            / 2
        )

        fig = plt.figure(layout="tight", figsize=(8, 10))

        ax = plt.subplot(411)
        ax2 = plt.subplot(423)
        ax3 = plt.subplot(424)
        ax4 = plt.subplot(425)
        ax5 = plt.subplot(426)
        ax6 = plt.subplot(427)
        ax7 = plt.subplot(428)

        plot_trading_summary(ax, market_trades_df, market_order_df, market_mid_df)
        plot_total_traded_volume(ax2, market_trades_df)
        plot_spread(ax3, order_book_df=market_order_df)
        plot_open_interest(ax4, market_data_df)
        plot_open_notional(ax5, market_data_df=market_data_df, price_df=market_mid_df)
        plot_margin_totals(ax6, accounts_df=market_accounts_df)
        plot_target_stake(ax7, market_data_df=market_data_df)

        figs[market_id] = fig

    return figs


def plot_trading_mode(
    fig: Figure, data_df: pd.DataFrame, ss: Optional[SubplotSpec] = None
):
    """Plots the proportion of time spent in different trading modes of a market.

    Args:
        fig (Figure):
            The Figure object to which the subplots will be added.
        data_df (pd.DataFrame):
            The DataFrame containing market data, including the trading mode of the
            market at each time step.
        gs (Optional[SubplotSpec]):
            An optional SubplotSpec object defining the placement of the subplots. If
            not specified, a default GridSpec with two rows and one column will be used.

    The function adds two subplots to the Figure object fig. The top subplot shows a
    step plot with a fill between each step representing the trading mode at the current
    time step. The bottom subplot shows a stacked area plot of the same information,
    with each area representing the proportion of time spent in a particular trading
    mode. The legend in the bottom subplot shows the name of each trading mode.

    TRADING_MODE_COLORS is a dictionary that maps each trading mode to a color used in
    the plots.
    """

    if ss is None:
        gs = GridSpec(
            nrows=2,
            ncols=1,
            height_ratios=[1, 5],
            hspace=0.1,
        )
    else:
        gs = GridSpecFromSubplotSpec(
            subplot_spec=ss,
            nrows=2,
            ncols=1,
            height_ratios=[1, 5],
            hspace=0.1,
        )
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[1, 0])

    ax0.set_title(
        "Trading Mode Analysis", loc="left", fontsize=12, color=(0.3, 0.3, 0.3)
    )
    names = []
    for name, value in markets.Market.TradingMode.items():
        names.append(name)
        series = (data_df["market_trading_mode"] == value).astype(int)
        ax0.fill_between(
            series.index,
            series,
            step="post",
            alpha=1,
            color=TRADING_MODE_COLORS[value],
            linewidth=0,
        )

        data_df = data_df.merge(
            (data_df["market_trading_mode"] == value).cumsum().rename(name),
            left_index=True,
            right_index=True,
        )
    data_df = data_df[names].divide(data_df[names].sum(axis=1), axis=0)

    ax1.stackplot(
        data_df.index,
        *[data_df[name].values for name in names],
        colors=TRADING_MODE_COLORS.values(),
    )

    ax0.get_xaxis().set_visible(False)
    ax0.get_yaxis().set_visible(False)

    ax1.set_ylabel("PROPORTION OF TIME IN MODE")
    ax1.legend(labels=names, loc="lower right")


def plot_price_comparison(
    fig: Figure,
    data_df: pd.DataFrame,
    fuzzing_df: pd.DataFrame,
    ss: Optional[SubplotSpec],
):
    """Plots the external price and mark price along with their respective volatilities.

    Args:
        fig (Figure):
            Figure object to plot the data on.
        fuzzing_df (pd.DataFrame):
            DataFrame containing fuzzing data.
        data_df (pd.DataFrame):
            DataFrame containing market data.
        ss (Optional[SubplotSpec]):
            SubplotSpec object representing the position of the subplot on the figure.
    """
    if ss is None:
        gs = GridSpec(
            nrows=1,
            ncols=1,
        )
    else:
        gs = GridSpecFromSubplotSpec(
            subplot_spec=ss,
            nrows=1,
            ncols=1,
        )
    ax0 = fig.add_subplot(gs[0, 0])

    ax0.set_title("Price Analysis", loc="left", fontsize=12, color=(0.3, 0.3, 0.3))

    external_price_series = fuzzing_df["external_price"].replace(0, np.nan)
    mark_price_series = data_df["mark_price"].replace(0, np.nan)

    ax0.plot(mark_price_series)
    ax0.set_ylim(ax0.get_ylim())
    ax0.plot(external_price_series, linewidth=0.8, alpha=0.8)

    ep_volatility = external_price_series.var() / (
        external_price_series.size + 0.000001
    )
    mp_volatility = mark_price_series.var() / mark_price_series.size

    ax0.text(
        x=0.1,
        y=0.1,
        s=(
            f"external-price volatility = {round(ep_volatility, 1)}\nmark-price"
            f" volatility = {round(mp_volatility, 1)}"
        ),
        fontsize=8,
        bbox=dict(facecolor="white", alpha=1),
        transform=ax0.transAxes,
    )

    ax0.set_ylabel("PRICE")
    ax0.legend(labels=["external price", "mark price"])


def plot_degen_close_outs(
    fig: Figure,
    accounts_df: pd.DataFrame,
    fuzzing_df: pd.DataFrame,
    ss: Optional[SubplotSpec] = None,
):
    """Plots the number of close outs of degen traders and degen liquidity providers.

    Args:
        fig (matplotlib.figure.Figure):
            The figure object to plot onto.
        accounts_df (pandas.DataFrame):
            A dataframe containing the accounts data.
        fuzzing_df (pandas.DataFrame):
            A dataframe containing the fuzzing data.
        ss (Optional[matplotlib.gridspec.SubplotSpec]):
            A subplot specification for the plot. Default is None.
    """
    if ss is None:
        gs = GridSpec(
            nrows=2,
            ncols=1,
            height_ratios=[1, 1],
            hspace=0.15,
        )
    else:
        gs = GridSpecFromSubplotSpec(
            subplot_spec=ss,
            nrows=2,
            ncols=1,
            height_ratios=[1, 1],
            hspace=0.15,
        )

    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[1, 0])

    ax0.set_title("Close Out Analysis", loc="left", fontsize=12, color=(0.3, 0.3, 0.3))

    insurance_pool_ds = accounts_df["balance"][
        (accounts_df["party_id"] == "network") & (accounts_df["type"] == 1)
    ]
    trader_close_outs_ds = fuzzing_df["trader_close_outs"]
    liquidity_provider_close_outs_ds = fuzzing_df["liquidity_provider_close_outs"]

    ax0r = ax0.twinx()

    ln0 = ax0r.plot(
        insurance_pool_ds.index,
        insurance_pool_ds.values,
        "b.-",
        markersize=1,
        label="insurance pool",
    )
    ln1 = ax0.plot(
        trader_close_outs_ds.index,
        trader_close_outs_ds.values,
        "r.-",
        markersize=1,
        label="degen trader close outs",
    )

    lns = ln0 + ln1
    ax0.legend(handles=lns, labels=[ln.get_label() for ln in lns], loc="upper left")

    ax0.set_ylabel("NB CLOSE OUTS")
    ax0r.set_ylabel("INSURANCE POOL", position="right")
    ax0r.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

    ax0.get_xaxis().set_visible(False)

    ax1r = ax1.twinx()

    ln3 = ax1r.plot(
        insurance_pool_ds.index,
        insurance_pool_ds.values,
        "b.-",
        markersize=1,
        label="insurance pool",
    )
    ln4 = ax1.plot(
        liquidity_provider_close_outs_ds.index,
        liquidity_provider_close_outs_ds.values,
        "r.-",
        markersize=1,
        label="degen LP close outs",
    )

    lns = ln3 + ln4
    ax1.legend(handles=lns, labels=[ln.get_label() for ln in lns], loc="upper left")

    ax1.set_ylabel("NB CLOSE OUTS")
    ax1r.set_ylabel("INSURANCE POOL", position="right")
    ax1r.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))


def fuzz_plots(run_name: Optional[str] = None) -> Figure:
    data_df = load_market_data_df(run_name=run_name)
    accounts_df = load_accounts_df(run_name=run_name)
    fuzzing_df = load_fuzzing_df(run_name=run_name)

    markets = data_df.market_id.unique()

    figs = {}
    for market_id in markets:
        market_data_df = data_df[data_df["market_id"] == market_id]
        market_accounts_df = accounts_df[accounts_df["market_id"] == market_id]
        market_fuzzing_df = fuzzing_df[fuzzing_df["market_id"] == market_id]

        fig = plt.figure(figsize=[8, 10])
        fig.suptitle(
            f"Fuzz Testing Plots",
            fontsize=18,
            fontweight="bold",
            color=(0.2, 0.2, 0.2),
        )
        fig.tight_layout()

        plt.rcParams.update({"font.size": 8})

        gs = GridSpec(nrows=3, ncols=1, height_ratios=[2, 2, 3], hspace=0.3)

        plot_trading_mode(fig, ss=gs[0, 0], data_df=market_data_df)
        plot_price_comparison(
            fig,
            ss=gs[1, 0],
            data_df=market_data_df,
            fuzzing_df=market_fuzzing_df,
        )
        plot_degen_close_outs(
            fig,
            ss=gs[2, 0],
            accounts_df=market_accounts_df,
            fuzzing_df=market_fuzzing_df,
        )

        figs[market_id] = fig

    return figs


def account_plots(run_name: Optional[str] = None, agent_types: Optional[list] = None):
    accounts_df = load_accounts_df(run_name=run_name)
    agents_df = load_agents_df(run_name=run_name)

    fig = plt.figure(figsize=[8, 10])
    fig.suptitle(
        f"Agent Account Plots",
        fontsize=18,
        fontweight="bold",
        color=(0.2, 0.2, 0.2),
    )
    fig.tight_layout()

    plt.rcParams.update({"font.size": 8})

    agent_types = [
        FuzzingAgent,
        FuzzyLiquidityProvider,
        DegenerateTrader,
        DegenerateLiquidityProvider,
    ]

    gs = GridSpec(nrows=len(agent_types), ncols=1, hspace=0.5)

    axs: list[plt.Axes] = []

    for i, agent_type in enumerate(agent_types):
        axs.append(fig.add_subplot(gs[i, 0]))

        axs[i].set_title(
            f"Total Account Balance: {agent_type.__name__}",
            loc="left",
            fontsize=12,
            color=(0.3, 0.3, 0.3),
        )

        agent_keys = agents_df["agent_key"][
            agents_df["agent_type"] == agent_type.__name__
        ].to_list()
        for key in agent_keys:
            totals = (
                accounts_df[accounts_df["party_id"] == key]["balance"]
                .groupby(level=0)
                .sum()
            )
            axs[i].plot(totals)
        axs[i].autoscale(enable=True, axis="y")

    return fig


def plot_price_monitoring(run_name: Optional[str] = None):
    data_df = load_market_data_df(run_name=run_name)

    market_ids = data_df.market_id.unique()

    figs = {}
    for market_id in market_ids:
        market_data_df = data_df[data_df["market_id"] == market_id]

        # Extract the tightest valid prices from the price monitoring valid_prices
        valid_prices = defaultdict(lambda: [])
        for index in market_data_df.index:
            all_bounds = ast.literal_eval(
                market_data_df.loc[index]["price_monitoring_bounds"]
            )
            valid_prices["datetime"].append(index)
            valid_prices["min_valid_price"].append(np.nan)
            valid_prices["max_valid_price"].append(np.nan)
            for _, individual_bound in enumerate(all_bounds):
                valid_prices["min_valid_price"][-1] = (
                    individual_bound[0]
                    if valid_prices["min_valid_price"][-1] is np.nan
                    else max(individual_bound[0], valid_prices["min_valid_price"][-1])
                )
                valid_prices["max_valid_price"][-1] = (
                    individual_bound[1]
                    if valid_prices["max_valid_price"][-1] is np.nan
                    else min(individual_bound[1], valid_prices["max_valid_price"][-1])
                )

        fig = plt.figure(figsize=[10, 7])
        fig.suptitle(
            f"Price Monitoring Analysis",
            fontsize=18,
            fontweight="bold",
            color=(0.2, 0.2, 0.2),
        )
        fig.tight_layout()
        plt.rcParams.update({"font.size": 8})

        gs = GridSpec(nrows=1, ncols=1, hspace=0.1)
        ax = fig.add_subplot(
            gs[0, 0],
        )
        twinax = ax.twinx()
        twinax.set_ylim(0, 1)

        # Plot period where auctions triggered (but not extended)
        series = (market_data_df["trigger"] == 3).astype(int) & (
            market_data_df["extension_trigger"] != 3
        ).astype(int)
        twinax.fill_between(
            series.index,
            series,
            step="post",
            alpha=0.1,
            color="r",
            linewidth=0,
            label="auction",
        )
        # Plot periods where auctions extended
        series = (market_data_df["extension_trigger"] == 3).astype(int)
        twinax.fill_between(
            series.index,
            series,
            step="post",
            alpha=0.1,
            color="orange",
            linewidth=0,
            label="extension",
        )

        ax.plot(
            valid_prices["datetime"],
            valid_prices["min_valid_price"],
            "r-",
            linewidth=0.5,
            alpha=0.4,
            label="valid price bounds",
        )
        ax.plot(
            valid_prices["datetime"],
            valid_prices["max_valid_price"],
            "r-",
            linewidth=0.5,
            alpha=0.4,
            label="_nolegend",
        )

        ax.plot(
            market_data_df.index,
            market_data_df["mark_price"].replace(0, np.nan),
            "b-",
            alpha=1.0,
            label="mark price",
        )
        ax.plot(
            market_data_df.index,
            market_data_df["mid_price"].replace(0, np.nan),
            "b-",
            alpha=0.4,
            label="mid price",
        )
        ax.plot(
            market_data_df.index,
            market_data_df["indicative_price"].replace(0, np.nan),
            "g-",
            alpha=1.0,
            label="indicative price",
        )

        ax.legend(loc="upper left")
        twinax.legend(loc="lower right")

        ax.set_xlabel("datetime")
        ax.set_ylabel("price")

        figs[market_id] = fig

    return figs


if __name__ == "__main__":
    dir = "test_plots"
    if not os.path.exists(dir):
        os.mkdir(dir)
    figs = fuzz_plots()
    for i, fig in enumerate(figs.values()):
        fig.savefig(f"{dir}/fuzz-{i}.jpg")
    figs = plot_run_outputs()
    for i, fig in enumerate(figs.values()):
        fig.savefig(f"{dir}/trading-{i}.jpg")
    figs = plot_price_monitoring()
    for i, fig in enumerate(figs.values()):
        fig.savefig(f"{dir}/monitoring-{i}.jpg")
    fig = account_plots()
    fig.savefig(f"{dir}/accounts.jpg")
