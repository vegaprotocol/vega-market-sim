import os
import ast

import itertools
import argparse

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import vega_sim.proto.vega as vega_protos

from typing import Optional, List
from collections import defaultdict
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.markers import MarkerStyle
from matplotlib.gridspec import GridSpec, SubplotSpec, GridSpecFromSubplotSpec

from vega_sim.scenario.fuzzed_markets.agents import (
    FuzzingAgent,
    FuzzyLiquidityProvider,
    RiskyMarketOrderTrader,
    RiskySimpleLiquidityProvider,
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
    6: (255 / 255, 0 / 255, 0 / 255),
}

TRANSFER_TYPE_MAP = {
    vega_protos.vega.TRANSFER_TYPE_LIQUIDITY_FEE_ALLOCATE: {
        "color": "b",
        "stack": False,
    },
    vega_protos.vega.TRANSFER_TYPE_LIQUIDITY_FEE_NET_DISTRIBUTE: {
        "color": "g",
        "stack": True,
    },
    vega_protos.vega.TRANSFER_TYPE_SLA_PENALTY_BOND_APPLY: {
        "color": "r",
        "stack": False,
    },
    vega_protos.vega.TRANSFER_TYPE_SLA_PENALTY_LP_FEE_APPLY: {
        "color": "r",
        "stack": True,
    },
    vega_protos.vega.TRANSFER_TYPE_LIQUIDITY_FEE_UNPAID_COLLECT: {
        "color": [1, 0.8, 0],
        "stack": True,
    },
    vega_protos.vega.TRANSFER_TYPE_SLA_PERFORMANCE_BONUS_DISTRIBUTE: {
        "color": "c",
        "stack": True,
    },
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
    load_market_chain,
    load_resource_df,
    load_assets_df,
    load_ledger_entries_df,
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


def _series_df_to_single_series(
    df: pd.DataFrame, market_series: List[str]
) -> pd.DataFrame:
    df_clone = df.copy().reset_index()
    df_clone["series_ix"] = df_clone.market_id.apply(lambda x: market_series.index(x))
    selector = df_clone.loc[df_clone.groupby("time").series_ix.idxmax()][
        ["time", "market_id"]
    ]

    return df_clone.merge(selector, on=["time", "market_id"]).set_index("time")


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

    market_chains = load_market_chain(run_name=run_name)
    if not market_chains:
        market_chains = {
            market_id: [market_id] for market_id in data_df["market_id"].unique()
        }

    figs = {}

    for market_id, market_children in market_chains.items():
        market_order_df = _series_df_to_single_series(
            order_df[order_df["market_id"].isin(market_children)],
            market_series=market_children,
        )
        market_trades_df = _series_df_to_single_series(
            trades_df[trades_df["market_id"].isin(market_children)],
            market_series=market_children,
        )
        market_data_df = _series_df_to_single_series(
            data_df[data_df["market_id"].isin(market_children)],
            market_series=market_children,
        )
        market_accounts_df = _series_df_to_single_series(
            accounts_df[accounts_df["market_id"].isin(market_children)],
            market_series=market_children,
        )

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

    ep_volatility = external_price_series.var() / external_price_series.size
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


def plot_risky_close_outs(
    fig: Figure,
    accounts_df: pd.DataFrame,
    fuzzing_df: pd.DataFrame,
    ss: Optional[SubplotSpec] = None,
):
    """Plots the number of close outs of risky traders and risky liquidity providers.

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
        label="risky trader close outs",
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
        label="risky LP close outs",
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

    market_chains = load_market_chain(run_name=run_name)
    if not market_chains:
        market_chains = {
            market_id: [market_id] for market_id in data_df["market_id"].unique()
        }

    figs = {}
    for market_id, market_children in market_chains.items():
        market_data_df = _series_df_to_single_series(
            data_df[data_df["market_id"].isin(market_children)],
            market_series=market_children,
        )
        market_accounts_df = _series_df_to_single_series(
            accounts_df[accounts_df["market_id"].isin(market_children)],
            market_series=market_children,
        )

        market_fuzzing_df = _series_df_to_single_series(
            fuzzing_df[fuzzing_df["market_id"].isin(market_children)],
            market_series=market_children,
        )

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
        plot_risky_close_outs(
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
        RiskyMarketOrderTrader,
        RiskySimpleLiquidityProvider,
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
    market_chains = load_market_chain(run_name=run_name)
    if not market_chains:
        market_chains = {
            market_id: [market_id] for market_id in data_df["market_id"].unique()
        }

    figs = {}
    for market_id, market_children in market_chains.items():
        market_data_df = _series_df_to_single_series(
            data_df[data_df["market_id"].isin(market_children)],
            market_series=market_children,
        )

        # Extract the tightest valid prices from the price monitoring valid_prices
        valid_prices = defaultdict(lambda: [])
        for index in market_data_df.index:
            all_bounds = list(
                itertools.chain(
                    *[
                        ast.literal_eval(
                            bounds[0] if isinstance(bounds, np.ndarray) else bounds
                        )
                        for bounds in market_data_df.loc[index][
                            ["price_monitoring_bounds"]
                        ].values
                    ]
                )
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


def resource_monitoring_plot(run_name: Optional[str] = None):
    resource_df = load_resource_df(
        run_name=run_name,
    )

    fig = plt.figure(figsize=[11.69, 8.27])
    fig.suptitle(
        f"Resource Monitoring",
        fontsize=18,
        fontweight="bold",
        color=(0.2, 0.2, 0.2),
    )
    fig.tight_layout()
    plt.rcParams.update({"font.size": 8})
    plt.rcParams.update({"axes.formatter.useoffset": False})

    gs = GridSpec(nrows=3, ncols=2, hspace=0.5, wspace=0.3)

    ax0 = fig.add_subplot(
        gs[0, :],
    )
    ax0.set_title("CPU Utilization")
    ax0.plot(resource_df.index, resource_df.vega_cpu_per, "r", label="vega")
    ax0.plot(resource_df.index, resource_df.datanode_cpu_per, "b", label="data-node")
    ax0.legend()
    ax0.set_xlabel("'vega' datetime")
    ax0.set_ylabel("CPU [%]")

    ax1 = fig.add_subplot(gs[1, 0], sharex=ax0)
    ax1.set_title("Memory - RSS (vega)")
    ax1.plot(resource_df.index, resource_df.vega_mem_rss / 1e9, "r", label="vega")
    ax1.legend()
    ax1.set_xlabel("'vega' datetime")
    ax1.set_ylabel("RSS [GB]")

    ax2 = fig.add_subplot(gs[1, 1], sharex=ax0)
    ax2.set_title("Memory - RSS (data-node)")
    ax2.plot(
        resource_df.index, resource_df.datanode_mem_rss / 1e9, "b", label="data-node"
    )
    ax2.legend()
    ax2.set_xlabel("'vega' datetime")
    ax2.set_ylabel("RSS [GB]")

    ax3 = fig.add_subplot(gs[2, 0], sharex=ax0)
    ax3.set_title("Memory - VMS (vega)")
    ax3.plot(resource_df.index, resource_df.vega_mem_vms / 1e9, "r", label="vega")
    ax3.legend()
    ax3.set_xlabel("'vega' datetime")
    ax3.set_ylabel("VMS [GB]")

    ax4 = fig.add_subplot(gs[2, 1], sharex=ax0)
    ax4.set_title("Memory - VMS (data-node)")
    ax4.plot(
        resource_df.index, resource_df.datanode_mem_vms / 1e9, "b", label="data-node"
    )
    ax4.legend()
    ax4.set_xlabel("'vega' datetime")
    ax4.set_ylabel("VMS [GB]")

    return fig


def reward_plots(run_name: Optional[str] = None):
    accounts_df = load_accounts_df(run_name=run_name)
    assets_df = load_assets_df(run_name=run_name)
    agents_df = load_agents_df(run_name=run_name).set_index("agent_key")

    joined_df = accounts_df.join(agents_df, on="party_id").join(assets_df, on="asset")

    datetime = joined_df.index.unique()

    fig = plt.figure(figsize=[11.69, 8.27])
    fig.suptitle(
        f"Agent Rewards Plots",
        fontsize=18,
        fontweight="bold",
        color=(0.2, 0.2, 0.2),
    )
    fig.tight_layout()

    plt.rcParams.update({"font.size": 8})

    gs = GridSpec(nrows=2, ncols=2, hspace=0.4)

    axs: list[plt.Axes] = []

    plots = [
        (
            0,
            0,
            vega_protos.vega.DispatchMetric.Name(
                vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_PAID
            ),
        ),
        (
            0,
            1,
            vega_protos.vega.DispatchMetric.Name(
                vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_RECEIVED
            ),
        ),
        (
            1,
            0,
            vega_protos.vega.DispatchMetric.Name(
                vega_protos.vega.DISPATCH_METRIC_LP_FEES_RECEIVED
            ),
        ),
        (
            1,
            1,
            vega_protos.vega.DispatchMetric.Name(
                vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE
            ),
        ),
    ]

    for plot in plots:
        axs.append(fig.add_subplot(gs[plot[0], plot[1]]))
        axs[-1].set_title(f"Asset: {plot[2]}")
        accounts_for_asset = joined_df[joined_df.symbol == str(plot[2])]
        grouped = accounts_for_asset.groupby(["agent_type", "time"])["balance"].sum()
        for index in grouped.index.get_level_values(0).unique():
            if index == "RewardFunder":
                continue
            series = grouped.loc[index]
            series = series.reindex(datetime, fill_value=0)
            axs[-1].plot(series.index, series.values, label=index)
        plt.xticks(rotation=45)
        axs[-1].legend()

    return fig


def sla_plot(run_name: Optional[str] = None):
    accounts_df = load_accounts_df(run_name=run_name)
    ledger_entries_df = load_ledger_entries_df(run_name=run_name)

    # Add a party of interest (poi) column to the ledger entries dataframe
    def determine_poi(row):
        if row["from_account_party_id"] not in ["network", None]:
            return row["from_account_party_id"]
        if row["to_account_party_id"] not in ["network", None]:
            return row["to_account_party_id"]
        return None

    ledger_entries_df["poi"] = ledger_entries_df.apply(determine_poi, axis=1)

    # Initialise the figure and subplots
    fig = plt.figure(figsize=[11.69, 8.27])
    fig.suptitle(
        f"SLA Analysis Plots",
        fontsize=18,
        fontweight="bold",
        color=(0.2, 0.2, 0.2),
    )
    fig.tight_layout()
    plt.rcParams.update({"font.size": 8})
    gs = GridSpec(nrows=3, ncols=2, hspace=0.4)
    fig.subplots_adjust(bottom=0.2)
    axs: list[plt.Axes] = []

    # Add a LP fee accounts plot
    axs.append(fig.add_subplot(gs[0, 0:2]))
    axs[-1].set_title(
        f"LP Liquidity Fee Account Balances",
        loc="left",
        fontsize=12,
        color=(0.3, 0.3, 0.3),
    )
    filtered_accounts_df = accounts_df[accounts_df["type"] == 19]
    for i, party_id in enumerate(ledger_entries_df["poi"].unique()):
        axs[-1].plot(
            filtered_accounts_df[filtered_accounts_df["party_id"] == party_id][
                "balance"
            ],
            label=f"LP {i+1}",
        )
    axs[-1].legend()
    axs[-1].set_ylabel("Amount [USD]")

    for i, party_id in enumerate(ledger_entries_df["poi"].unique()):
        filtered_ledger_entries_df = ledger_entries_df[
            ledger_entries_df["poi"] == party_id
        ]
        unique_times = filtered_ledger_entries_df["time"].unique()
        unique_transfer_types = list(TRANSFER_TYPE_MAP.keys())
        combinations = pd.DataFrame(
            [(a, b) for a in unique_times for b in unique_transfer_types],
            columns=["time", "transfer_type"],
        )
        merged_ledger_entries_df = pd.merge(
            combinations,
            filtered_ledger_entries_df,
            on=["time", "transfer_type"],
            how="left",
        ).fillna(0)
        # Condense transfers with identical timestamps + type
        merged_ledger_entries_df = merged_ledger_entries_df.groupby(
            ["time", "transfer_type"], as_index=False
        )["quantity"].sum()

        merged_ledger_entries_df.sort_values("time", ascending=True, inplace=True)
        merged_ledger_entries_df["cum_sum"] = merged_ledger_entries_df.groupby(
            "transfer_type"
        )["quantity"].cumsum()

        axs.append(fig.add_subplot(gs[1, i]))
        axs[-1].set_title(
            f"Bond account and penalties for LP {i+1}",
            loc="left",
            fontsize=12,
            color=(0.3, 0.3, 0.3),
        )
        accounts = accounts_df[
            (accounts_df["type"] == 9) & (accounts_df["party_id"] == party_id)
        ]
        axs[-1].plot(accounts.index, accounts["balance"], "g", label=f"Bond Account")
        axs[-1].step(
            merged_ledger_entries_df[merged_ledger_entries_df["transfer_type"] == 32][
                "time"
            ],
            merged_ledger_entries_df[merged_ledger_entries_df["transfer_type"] == 32][
                "cum_sum"
            ],
            "r",
            label=f"SLA Penalties",
        )
        axs[-1].legend()
        axs[-1].set_ylabel("Amount [USD]")

        axs.append(fig.add_subplot(gs[2, i]))
        axs[-1].set_title(
            f"Cumulative transfers for LP {i+1}",
            loc="left",
            fontsize=12,
            color=(0.3, 0.3, 0.3),
        )
        axs[-1].step(
            merged_ledger_entries_df.time.unique(),
            merged_ledger_entries_df[merged_ledger_entries_df["transfer_type"] == 30][
                "cum_sum"
            ],
            label=vega_protos.vega.TransferType.Name(30),
        )
        data = []
        labels = []
        colors = []
        for transfer_type in TRANSFER_TYPE_MAP:
            if TRANSFER_TYPE_MAP[transfer_type]["stack"] == True:
                data.append(
                    merged_ledger_entries_df[
                        merged_ledger_entries_df["transfer_type"] == transfer_type
                    ]["cum_sum"]
                )
                labels.append(vega_protos.vega.TransferType.Name(transfer_type))
                colors.append(TRANSFER_TYPE_MAP[transfer_type]["color"])
        axs[-1].stackplot(
            merged_ledger_entries_df.time.unique(),
            *data,
            labels=labels,
            colors=colors,
            step="pre",
        )
        axs[-1].legend(
            fontsize="9",
            loc="upper left",
            bbox_to_anchor=(-0.02, -0.15),
            fancybox=False,
            shadow=False,
        )
        axs[-1].set_ylabel("Amount [USD]")

    axs[0].get_shared_x_axes().join(*[ax for ax in axs[0:]])
    axs[1].get_shared_y_axes().join(*[axs[1], axs[3]])
    axs[2].get_shared_y_axes().join(*[axs[2], axs[4]])

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fuzzing", action="store_true")
    parser.add_argument("--trading", action="store_true")
    parser.add_argument("--monitoring", action="store_true")
    parser.add_argument("--accounts", action="store_true")
    parser.add_argument("--rewards", action="store_true")
    parser.add_argument("--resources", action="store_true")
    parser.add_argument("--sla", action="store_true")
    parser.add_argument("--all", action="store_true")

    parser.add_argument("--show", action="store_true")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    dir = "test_plots"
    if not os.path.exists(dir):
        os.mkdir(dir)

    if args.fuzzing or args.all:
        figs = fuzz_plots()
        for i, fig in enumerate(figs.values()):
            if args.save:
                fig.savefig(f"{dir}/fuzz-{i}.jpg")

    if args.trading or args.all:
        figs = plot_run_outputs()
        for i, fig in enumerate(figs.values()):
            if args.save:
                fig.savefig(f"{dir}/trading-{i}.jpg")

    if args.monitoring or args.all:
        figs = plot_price_monitoring()
        for i, fig in enumerate(figs.values()):
            if args.save:
                fig.savefig(f"{dir}/monitoring-{i}.jpg")

    if args.accounts or args.all:
        print("accounting")
        fig = account_plots()
        if args.save:
            fig.savefig(f"{dir}/accounts.jpg")

    if args.rewards or args.all:
        fig = reward_plots()
        if args.save:
            fig.savefig(f"{dir}/rewards.jpg")

    if args.resources or args.all:
        fig = resource_monitoring_plot()
        if args.save:
            fig.savefig(f"{dir}/resource_monitoring.jpg")

    if args.sla or args.all:
        fig = sla_plot()
        if args.save:
            fig.savefig(f"{dir}/sla.jpg")

    if args.show:
        plt.show()
