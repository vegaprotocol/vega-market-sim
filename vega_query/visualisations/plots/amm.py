from typing import List
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from vega_query.service.service import Service
import vega_protos.protos as protos
from vega_query.utils import padded_int_to_float
from vega_query.utils import timestamp_to_datetime, duration_str_to_int
from vega_query.visualisations.overlay import *

from vega_query.service.networks.constants import Network


def __party_defaults(
    amms: List[protos.vega.events.v1.events.AMM],
) -> List[str]:
    unique_ids = set()
    for amm in amms:
        unique_ids.add(amm.amm_party_id)
    return list(unique_ids)


def __party_colors(party_ids: List[str]) -> Dict[str, str]:
    color_cycler = iter(plt.rcParams["axes.prop_cycle"])
    party_colors = {}
    for party_id in party_ids:
        party_colors[party_id] = next(color_cycler)["color"]
    return party_colors


def create(
    service: Service,
    market_code: str,
    party_ids: Optional[List[str]] = None,
    start_timestamp: Optional[int] = None,
    end_timestamp: Optional[int] = None,
):

    # Get market, asset, and network parameter information
    market = service.utils.market.find_market([market_code])
    asset = service.utils.market.find_asset([market_code])
    epoch_length = duration_str_to_int(
        service.api.data.get_network_parameter(key="validators.epoch.length").value
    )

    # Default timestamps for getting data if required
    network_timestamp = service.api.data.get_vega_time()
    start_timestamp = (
        market.market_timestamps.proposed if start_timestamp is None else start_timestamp
    )
    end_timestamp = network_timestamp if end_timestamp is None else end_timestamp

    # Get market specific information
    market_data_history = service.api.data.get_market_data_history_by_id(
        market_id=market.id,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )

    # Set unique colors for each party and request party specific information
    amms = service.api.data.list_amms(market_id=market.id)
    if party_ids is None:
        # party_ids = __party_defaults_old(market_data_history=market_data_history)
        party_ids = __party_defaults(amms=amms)
        # party_ids = __party_defaults(amms=amms) + __party_defaults_old(
        #     market_data_history=market_data_history
        # )

        print(party_ids)

    party_colors = __party_colors(party_ids)

    fig = plt.figure(figsize=(15, 8))
    gs = fig.add_gridspec(2, 2)
    ymin = ymax = 0
    axes: List[Axes] = []

    axn0l = fig.add_subplot(gs[:, 0])
    axn0r: Axes = axn0l.twinx()
    if market_data_history is not None:
        overlay_mark_price(axn0l, market_data_history, market.decimal_places)
        overlay_trading_mode(axn0r, market_data_history)
        overlay_auction_starts(axn0r, market_data_history)
        overlay_auction_ends(axn0r, market_data_history)

    axn0l.set_ylabel("USDT")
    axn0l.set_title(
        "Market Price: Ornstein–Uhlenbeck ($\\theta=0.01$, $\\sigma=0.5$)",
        loc="left",
    )

    axn0r.set_yticks([])
    leg = axn0l.legend(loc="upper left", framealpha=1)
    leg.remove()
    axn0r.legend(loc="upper right", framealpha=1)
    axn0r.add_artist(leg)

    ax11 = fig.add_subplot(gs[0, 1])
    ax11.set_title("AMM: Position", loc="left")
    ax11.set_ylabel("Open Volume")

    ax11.sharex(axn0l)
    axes.append(ax11)
    ax21 = fig.add_subplot(gs[1, 1])
    ax21.set_title("AMM: Aggregated Account Balances [USDT]", loc="left")
    ax21.set_ylabel("$\\Delta$ USDT")
    ax21.sharex(axn0l)
    axes.append(ax21)

    for _, amm_party_id in enumerate(party_ids):

        parameters = [
            amm.parameters for amm in amms if amm.amm_party_id == amm_party_id
        ][0]
        axn0l.axhline(
            y=padded_int_to_float(parameters.base, market.decimal_places),
            color=party_colors[amm_party_id],
            linewidth=0.5,
        )

        # Reconstruct the AMMs position from trades
        trades = service.api.data.list_trades(
            party_ids=[amm_party_id],
            market_ids=[market.id],
            date_range_start_timestamp=start_timestamp,
            date_range_end_timestamp=end_timestamp,
        )
        overlay_position(
            ax=ax11,
            trades=trades,
            party_id=amm_party_id,
            size_decimals=market.position_decimal_places,
        )
        ax11.get_lines()[-1].set_label(amm_party_id[:7])

        # Reconstruct the AMMs aggregated balance from balance changes
        aggregated_balances = service.api.data.list_balance_changes(
            party_ids=[amm_party_id],
            date_range_start_timestamp=start_timestamp,
            date_range_end_timestamp=end_timestamp,
        )
        overlay_aggregated_balances(
            ax=ax21,
            aggregated_balances=aggregated_balances,
            asset_decimals=asset.details.decimals,
        )
        ax21.get_lines()[-1].set_label(amm_party_id[:7])

    ax11.legend()
    ax21.legend()
    return fig


if __name__ == "__main__":

    from vega_query.scripts.parser import PARSER

    args = PARSER.parse_args()

    # Instantiate service for specified network
    match args.network:
        case "mainnet":
            network = Network.NETWORK_MAINNET
        case "stagnet":
            network = Network.NETWORK_STAGNET
        case "testnet":
            network = Network.NETWORK_TESTNET
        case "local":
            network = Network.NETWORK_LOCAL
            if args.port is None:
                raise ValueError("A port (--port) must be specified for local network.")
        case _:
            network = Network.NETWORK_UNSPECIFIED
            if args.config is None:
                raise ValueError(
                    "A config path (--config) must be specified for unspecified network."
                )
    service = Service(
        network=network,
        network_config=args.config,
        port_data_node=args.port,
    )

    fig = create(
        service,
        market_code=args.market,
        start_timestamp=(
            int(args.start_time.timestamp() * 1e9)
            if args.start_time is not None
            else None
        ),
        end_timestamp=(
            int(args.end_time.timestamp() * 1e9) if args.end_time is not None else None
        ),
    )
    plt.show()
