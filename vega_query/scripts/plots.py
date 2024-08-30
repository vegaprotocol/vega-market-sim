import os
import logging
import datetime
from pathlib import Path
import matplotlib.pyplot as plt

import vega_query.visualisations as vis
import vega_protos.protos as protos
from vega_query.service.service import Service
from vega_query.service.networks.constants import Network
from vega_query.scripts.parser import PARSER

if __name__ == "__main__":
    # Enrich parser with script specific options
    plotting = PARSER.add_argument_group("Plotting options")
    plotting.add_argument(
        "--monitoring",
        action="store_true",
        default=False,
        help="Specify whether to create the price monitoring analysis plot.",
    )
    plotting.add_argument(
        "--liquidations",
        action="store_true",
        default=False,
        help="Specify whether to create the liquidations analysis plot.",
    )
    plotting.add_argument(
        "--funding",
        action="store_true",
        default=False,
        help="Specify whether to create the funding analysis plot.",
    )
    plotting.add_argument(
        "--tight",
        action="store_true",
        default=False,
        help="Specify whether to plot all bounds or just the tightest bounds.",
    )
    args = PARSER.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

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

    # Request required data from network
    network_timestamp = service.api.data.get_vega_time()
    end_timestamp = (
        network_timestamp
        if args.end_time is None
        else int(args.end_time.timestamp() * 1e9)
    )
    start_timestamp = (
        network_timestamp - int(1 * 60 * 60 * 1e9)
        if args.start_time is None
        else int(args.start_time.timestamp() * 1e9)
    )
    market = service.utils.market.find_market([args.market])
    if market.tradable_instrument.instrument.spot != protos.vega.markets.Spot():
        asset = service.utils.market.find_quote_asset([args.market])
    if market.tradable_instrument.instrument.future != protos.vega.markets.Future():
        asset = service.utils.market.find_settlement_asset([args.market])
    if (
        market.tradable_instrument.instrument.perpetual
        != protos.vega.markets.Perpetual()
    ):
        asset = service.utils.market.find_settlement_asset([args.market])

    market_data_history = service.api.data.get_market_data_history_by_id(
        market_id=market.id,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        max_pages=args.pages,
    )
    trades = None
    aggregated_balance_history = None
    if args.liquidations:
        trades = service.api.data.list_trades(
            market_ids=[market.id],
            date_range_start_timestamp=start_timestamp,
            date_range_end_timestamp=end_timestamp,
        )
        aggregated_balance_history = service.api.data.list_balance_changes(
            party_ids=["network"],
            market_ids=[market.id],
            account_types=[protos.vega.vega.AccountType.ACCOUNT_TYPE_INSURANCE],
            date_range_start_timestamp=start_timestamp,
            date_range_end_timestamp=end_timestamp,
        )
    funding_periods = None
    funding_period_data_points = None
    if args.funding:
        funding_periods = service.api.data.list_funding_periods(
            market_id=market.id,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )
        funding_period_data_points = service.api.data.list_funding_period_data_points(
            market_id=market.id,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )

    # Build figures and optionally save or show
    if args.save:
        if not os.path.exists("plots"):
            os.makedirs("plots")
    if args.monitoring:
        fig_m = vis.plot.price_monitoring_analysis(
            market, market_data_history, tightest_bounds=args.tight
        )
        if args.save:
            fig_m.savefig(f"plots/{datetime.datetime.now()}-monitoring.png")
    if args.liquidations:
        fig_l = vis.plot.liquidation_analysis(
            asset,
            market,
            trades,
            market_data_history,
            aggregated_balance_history,
        )
        if args.save:
            fig_l.savefig(f"plots/{datetime.datetime.now()}-liquidations.png")
    if args.funding:
        fig_f = vis.plot.funding_analysis(
            asset,
            market,
            market_data_history,
            funding_periods,
            funding_period_data_points,
        )
        if args.save:
            fig_f.savefig(f"plots/{datetime.datetime.now()}-funding.png")
    if args.show:
        plt.show()
