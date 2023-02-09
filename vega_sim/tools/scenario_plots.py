from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import vega_sim.proto.vega as vega_protos
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.markers import MarkerStyle

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


def plot_run_outputs(run_name: Optional[str] = None) -> Figure:
    order_df = load_order_book_df(run_name=run_name)
    trades_df = load_trades_df(run_name=run_name)
    data_df = load_market_data_df(run_name=run_name)
    accounts_df = load_accounts_df(run_name=run_name)

    mid_df = order_df[order_df.level == 0].groupby("time")[["price"]].sum() / 2

    fig = plt.figure(layout="tight", figsize=(8, 10))

    ax = plt.subplot(411)
    ax2 = plt.subplot(423)
    ax3 = plt.subplot(424)
    ax4 = plt.subplot(425)
    ax5 = plt.subplot(426)
    ax6 = plt.subplot(427)
    ax7 = plt.subplot(428)

    plot_trading_summary(ax, trades_df, order_df, mid_df)
    plot_total_traded_volume(ax2, trades_df)
    plot_spread(ax3, order_book_df=order_df)
    plot_open_interest(ax4, data_df)
    plot_open_notional(ax5, market_data_df=data_df, price_df=mid_df)
    plot_margin_totals(ax6, accounts_df=accounts_df)
    plot_target_stake(ax7, market_data_df=data_df)

    return fig


if __name__ == "__main__":
    fig = plot_run_outputs()
    fig.savefig("output.jpg")
