from typing import List
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from vega_query.service.service import Service
import vega_protos.protos as protos
from vega_query.utils import timestamp_to_datetime, duration_str_to_int
from vega_query.visualisations.overlay import *

from vega_query.service.networks.constants import Network


def __party_defaults(
    market_data_history: List[protos.vega.vega.MarketData],
    amms: List[protos.vega.events.v1.events.AMM],
) -> List[str]:
    unique_ids = set()
    for market_data in market_data_history:
        for lp in market_data.liquidity_provider_sla:
            unique_ids.add(lp.party)
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
        market.market_timestamps.proposed if start_timestamp is None else None
    )
    end_timestamp = network_timestamp if end_timestamp is None else None

    # Get market specific information
    market_data_history = service.api.data.get_market_data_history_by_id(
        market_id=market.id,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )

    # Set unique colors for each party and request party specific information
    amms = service.api.data.list_amms()
    if party_ids is None:
        party_ids = __party_defaults(market_data_history, amms)
    party_colors = __party_colors(party_ids)
    rewards = []
    ledger_entries = []
    for party_id in party_ids:
        ledger_entries.extend(
            service.api.data.list_ledger_entries(
                close_on_account_filters=False,
                from_party_ids=[party_id],
                to_party_ids=[party_id],
                transfer_types=[
                    protos.vega.vega.TransferType.TRANSFER_TYPE_SLA_PENALTY_LP_FEE_APPLY,
                    protos.vega.vega.TransferType.TRANSFER_TYPE_LIQUIDITY_FEE_NET_DISTRIBUTE,
                    protos.vega.vega.TransferType.TRANSFER_TYPE_SLA_PERFORMANCE_BONUS_DISTRIBUTE,
                    protos.vega.vega.TransferType.TRANSFER_TYPE_LIQUIDITY_FEE_UNPAID_COLLECT,
                ],
                date_range_start_timestamp=start_timestamp,
                date_range_end_timestamp=end_timestamp,
            )
        )
        rewards.extend(service.api.data.list_rewards(party_id=party_id))

    # TODO: Tidy plotting section
    fig = plt.figure(figsize=(15, 8))
    gs = fig.add_gridspec(len(party_ids), 3)
    ymin = ymax = 0
    axes: List[Axes] = []
    axi0 = fig.add_subplot(gs[:, 0])
    axes.append(axi0)
    colors = []
    for i, party_id in enumerate(party_ids):
        overlay_current_epoch_fraction_of_time_on_book(
            ax=axi0,
            market=market,
            market_data_history=market_data_history,
            party_ids=[party_id],
            color=party_colors[party_id],
        )
        colors.append(axi0.get_lines()[-1].get_color())
        axi1 = fig.add_subplot(gs[i, 1])
        axi1.set_title(
            f"LP fee distribution breakdown: {party_id[:7]}",
            color=party_colors[party_id],
            loc="left",
        )
        overlay_sla_ledger_entries(
            axi1,
            ledger_entries=ledger_entries,
            asset_decimals=asset.details.decimals,
            party_id=party_id,
            interval=epoch_length,
        )
        axi1.legend(framealpha=1)
        axes.append(axi1)
        ymin = min(ymin, axi1.get_ylim()[0])
        ymax = max(ymax, axi1.get_ylim()[1])
        axi1.set_xlabel(f"datetime")
        axi1.set_ylabel(f"{asset.details.symbol}")
    axi2 = fig.add_subplot(gs[:, 2])
    overlay_stacked_rewards(
        axi2,
        rewards=rewards,
        asset_decimal=asset.details.decimals,
        reward_type_filter=protos.vega.vega.AccountType.ACCOUNT_TYPE_REWARD_LP_RECEIVED_FEES,
        party_color_map=party_colors,
    )
    axi2.set_ylabel(f"{asset.details.symbol}")
    axi2.set_xlabel("datetime")
    axi2.legend(framealpha=1)
    unique_labels = {}
    lines, labels = axi0.get_legend_handles_labels()
    for line, label in zip(lines, labels):
        if label not in unique_labels:
            unique_labels[label] = line
    axi0.legend(unique_labels.values(), unique_labels.keys(), framealpha=1)
    for ax in axes[1:]:
        ax.set_ylim(ymin, ymax)
    for ax in axes[0:]:
        ax.sharex(axes[0])
    axes[0].set_title("Fraction on Book", loc="left")
    st = fig.suptitle("Liquidity Analysis: LP Fee Distribution", ha="left")
    fig.tight_layout()
    st.set_position(xy=[axi0.get_position().x0, st.get_position()[1]])

    return fig


if __name__ == "__main__":

    from scripts.parser import PARSER

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
            timestamp_to_datetime(args.start_time, nano=True)
            if args.start_time is not None
            else None
        ),
        end_timestamp=(
            timestamp_to_datetime(args.end_time, nano=True)
            if args.end_time is not None
            else None
        ),
    )
    plt.show()
