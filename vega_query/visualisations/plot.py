from typing import List

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import vega_protos.protos as protos
from vega_query.visualisations.overlay import *
from vega_query.utils import timestamp_to_datetime


def price_monitoring_analysis(
    market: protos.vega.markets.Market,
    market_data_history: List[protos.vega.vega.MarketData],
    tightest_bounds: bool = True,
) -> Figure:
    fig = plt.figure(tight_layout=True, figsize=(15, 8))
    gs = fig.add_gridspec(1, 1)

    ax0l = fig.add_subplot(gs[:, :])
    ax0r: Axes = ax0l.twinx()
    overlay_last_traded_price(ax0l, market_data_history, market.decimal_places)
    overlay_indicative_price(ax0l, market_data_history, market.decimal_places)
    overlay_price_bounds(
        ax0l,
        market_data_history,
        market.decimal_places,
        tightest_bounds=tightest_bounds,
    )
    overlay_trading_mode(ax0r, market_data_history)
    overlay_auction_starts(ax0r, market_data_history)
    overlay_auction_ends(ax0r, market_data_history)

    ax0l.set_xlim(
        right=timestamp_to_datetime(market_data_history[0].timestamp, nano=True),
    )

    ax0l.set_title(
        f"Price Monitoring: {market.tradable_instrument.instrument.code}",
        loc="left",
    )
    ax0l.set_ylabel("price")
    ax0r.set_yticks([])
    leg = ax0l.legend(loc="upper left", framealpha=1)
    leg.remove()
    ax0r.legend(loc="upper right", framealpha=1)
    ax0r.add_artist(leg)

    return fig


def liquidation_analysis(
    asset: protos.vega.assets.Asset,
    market: protos.vega.markets.Market,
    trades: List[protos.vega.vega.Trade],
    market_data_history: List[protos.vega.vega.MarketData],
    aggregated_balance_history: List[
        protos.data_node.api.v2.trading_data.AggregatedBalance
    ],
) -> Figure:
    fig = plt.figure(tight_layout=True, figsize=(15, 8))
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 2, 2])

    ax0l = fig.add_subplot(gs[:, 0])
    ax0r: Axes = ax0l.twinx()
    if market_data_history is not None:
        overlay_mark_price(ax0l, market_data_history, market.decimal_places)
        overlay_trading_mode(ax0r, market_data_history)
        overlay_auction_starts(ax0r, market_data_history)
        overlay_auction_ends(ax0r, market_data_history)
    ax0l.set_ylabel("price")
    ax0r.set_yticks([])

    ax1l = fig.add_subplot(gs[0, 1])
    ax1l.sharex(ax0l)
    ax1l.axhline(0, alpha=0.5, color="k", linewidth=1)
    ax1l.ticklabel_format(axis="y", style="sci", scilimits=(3, 3))
    overlay_network_liquidations(ax1l, trades, market.position_decimal_places)
    ax1l.legend(loc="upper left", framealpha=1)
    ax1l.set_ylabel("closeout volume")

    ax2l = fig.add_subplot(gs[1, 1])
    ax2l.sharex(ax0l)
    ax2l.axhline(0, alpha=0.5, color="k", linewidth=1)
    ax2l.ticklabel_format(axis="y", style="sci", scilimits=(3, 3))
    overlay_position(ax2l, trades, market.position_decimal_places, "network")
    ax2l.set_ylabel("network position")

    ax3l = fig.add_subplot(gs[2, 1])
    ax3l.sharex(ax0l)
    ax3l.ticklabel_format(axis="y", style="scientific", scilimits=(6, 6))
    overlay_balance(ax3l, aggregated_balance_history, asset.details.decimals)
    ax3l.set_ylabel("insurance pool")
    ax3l.set_xlim(
        right=timestamp_to_datetime(market_data_history[0].timestamp, nano=True),
    )

    leg = ax0l.legend(loc="upper left", framealpha=1)
    leg.remove()
    ax0r.legend(loc="upper right", framealpha=1)
    ax0r.add_artist(leg)

    ax0l.set_title(
        f"Liquidation analysis: {market.tradable_instrument.instrument.code}",
        loc="left",
    )

    return fig


def funding_analysis(
    asset: protos.vega.assets.Asset,
    market: protos.vega.markets.Market,
    market_data_history: List[protos.vega.vega.MarketData],
    funding_periods: List[protos.vega.events.v1.events.FundingPeriod],
    funding_period_data_points: List[
        protos.vega.events.v1.events.FundingPeriodDataPoint
    ],
) -> Figure:
    fig = plt.figure(tight_layout=True, figsize=(15, 8))
    gs = fig.add_gridspec(4, 1, height_ratios=[1, 3, 3, 2])

    ax0l = fig.add_subplot(gs[0, 0])
    ax0r: Axes = ax0l.twinx()
    overlay_period_funding_rate(ax0l, funding_periods=funding_periods, color="r")
    overlay_trading_mode(ax0r, market_data_history)
    overlay_funding_period_start(ax0r, funding_periods)
    leg = ax0l.legend(loc="upper left", framealpha=1)
    leg.remove()
    ax0r.add_artist(leg)
    ax0l.axhline(0, alpha=0.5, color="k", linewidth=1)
    ax0l.set_ylabel("funding rate")
    ax0r.set_yticks([])

    ax1l = fig.add_subplot(gs[1, 0])
    ax1r: Axes = ax1l.twinx()
    ax1l.sharex(ax0l)
    overlay_internal_twap(ax1l, market_data_history, asset.details.decimals)
    overlay_funding_period_data_points(
        ax1l,
        funding_period_data_points,
        asset.details.decimals,
        external=False,
    )
    overlay_trading_mode(ax1r, market_data_history)
    overlay_funding_period_start(ax1r, funding_periods)
    leg = ax1l.legend(loc="upper left", framealpha=1)
    leg.remove()
    ax1r.add_artist(leg)
    ax1l.set_ylabel(f"{asset.details.symbol}")
    ax1r.set_yticks([])
    ax2l = fig.add_subplot(gs[2, 0])
    ax2r: Axes = ax2l.twinx()
    ax2l.sharex(ax0l)
    overlay_external_twap(ax2l, market_data_history, asset.details.decimals)
    overlay_funding_period_data_points(
        ax2l,
        funding_period_data_points,
        asset.details.decimals,
        internal=False,
    )
    overlay_trading_mode(ax2r, market_data_history)
    overlay_funding_period_start(ax2r, funding_periods)
    leg = ax2l.legend(loc="upper left", framealpha=1)
    leg.remove()
    ax2r.add_artist(leg)
    ax2l.set_ylabel(f"{asset.details.symbol}")
    ax2r.set_yticks([])
    ax3l = fig.add_subplot(gs[3, 0])
    ax3r: Axes = ax3l.twinx()
    ax3l.sharex(ax0l)
    overlay_twap_difference(ax3l, market_data_history=market_data_history, color="y")
    overlay_trading_mode(ax3r, market_data_history)
    overlay_funding_period_start(ax3r, funding_periods)
    leg = ax3l.legend(loc="upper left", framealpha=1)
    leg.remove()
    ax3r.add_artist(leg)
    ax3l.set_ylabel(f"difference [%]")
    ax3r.set_yticks([])
    ax3l.set_xlabel(f"datetime")
    ax3l.set_xlim(
        right=timestamp_to_datetime(market_data_history[0].timestamp, nano=True),
    )
    ax3l.axhline(0, alpha=0.5, color="k", linewidth=1)

    ax0l.set_title(
        f"Funding analysis: {market.tradable_instrument.instrument.code}",
        loc="left",
    )

    return fig
