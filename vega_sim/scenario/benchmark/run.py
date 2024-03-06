import os
import logging
import pathlib
import datetime
import argparse


from vega_sim.null_service import VegaServiceNull, Ports
from vega_sim.scenario.constants import Network
from vega_sim.scenario.benchmark.scenario import BenchmarkScenario
from vega_sim.scenario.benchmark.registry import REGISTRY

from vegapy.service.service import Service
from vegapy.service.networks.constants import Network
import vegapy.visualisations as vis
import vegapy.protobuf.protos as protos

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-m", "--market", required=True, type=str)
PARSER.add_argument("-s", "--steps", default=600, type=int)
PARSER.add_argument("-p", "--pause", action="store_true")
PARSER.add_argument("-d", "--debug", action="store_true")
PARSER.add_argument("-o", "--output", action="store_true")
PARSER.add_argument("-c", "--console", action="store_true")
PARSER.add_argument("-w", "--wallet", action="store_true")
PARSER.add_argument("--core-metrics-port", default=2723, type=int)
PARSER.add_argument("--data-node-metrics-port", default=3651, type=int)


def _run(
    scenario: BenchmarkScenario,
    pause: bool = False,
    console: bool = False,
    output: bool = False,
    wallet: bool = False,
    output_dir: str = "plots",
    core_metrics_port: int = 2723,
    data_node_metrics_port: int = 3651,
):

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        seconds_per_block=scenario.block_length_seconds,
        transactions_per_block=scenario.transactions_per_block,
        retain_log_files=True,
        use_full_vega_wallet=wallet,
        run_with_console=console,
        port_config={
            Ports.METRICS: core_metrics_port,
            Ports.DATA_NODE_METRICS: data_node_metrics_port,
        },
    ) as vega:
        scenario.run_iteration(
            vega=vega,
            log_every_n_steps=100,
            output_data=False,
            run_with_snitch=False,
        )

        # Use vegapy package to produce plots
        service = Service(
            network=Network.NETWORK_LOCAL,
            network_config=pathlib.Path(
                f"{vega.log_dir}/vegahome/config/wallet-service/networks/local.toml"
            ),
        )
        # Request data from datanode
        market = service.api.data.list_markets(include_settled=True)[0]

        future_settlement_asset = (
            market.tradable_instrument.instrument.future.settlement_asset
        )
        perpetual_settlement_asset = (
            market.tradable_instrument.instrument.perpetual.settlement_asset
        )
        if future_settlement_asset != "":
            settlement_asset = future_settlement_asset
        if perpetual_settlement_asset != "":
            settlement_asset = perpetual_settlement_asset

        asset = service.api.data.get_asset(settlement_asset)
        trades = service.api.data.list_trades(
            market_ids=[market.id],
            date_range_start_timestamp=market.market_timestamps.pending,
        )
        market_data_history = service.api.data.get_market_data_history_by_id(
            market.id,
            start_timestamp=market.market_timestamps.pending,
        )
        aggregated_balance_history = service.api.data.list_balance_changes(
            asset_id=asset.id,
            market_ids=[market.id],
            party_ids=["network"],
            account_types=[protos.vega.vega.AccountType.ACCOUNT_TYPE_INSURANCE],
            date_range_start_timestamp=market.market_timestamps.pending,
        )
        # Initialise figures
        fig1 = None
        fig2 = None
        fig3 = None
        # Update figures
        fig1 = vis.plot.price_monitoring_analysis(market, market_data_history)
        fig2 = vis.plot.liquidation_analysis(
            asset, market, trades, market_data_history, aggregated_balance_history
        )
        if perpetual_settlement_asset != "":
            funding_periods = service.api.data.list_funding_periods(
                market_id=market.id,
                start_timestamp=market.market_timestamps.pending,
            )
            funding_period_data_points = (
                service.api.data.list_funding_period_data_points(
                    market.id, start_timestamp=market.market_timestamps.pending
                )
            )
            fig3 = vis.plot.funding_analysis(
                asset,
                market,
                market_data_history,
                funding_periods,
                funding_period_data_points,
            )

        if pause:
            input("Waiting after run finished.")

    if output:
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_dir = output_dir + f"/{datetime.datetime.now()}"
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        if fig1 is not None:
            fig1.savefig(f"{output_dir}/price_monitoring_analysis.png")
        if fig2 is not None:
            fig2.savefig(f"{output_dir}/liquidation_analysis.png")
        if fig3 is not None:
            fig3.savefig(f"{output_dir}/funding_analysis.png")


if __name__ == "__main__":

    args = PARSER.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if args.market not in REGISTRY:
        raise ValueError(f"Market {args.market} not found")
    scenario = REGISTRY[args.market].num_steps = args.steps

    _run(
        scenario=REGISTRY[args.market],
        wallet=args.wallet,
        console=args.console,
        pause=args.pause,
        output=args.output,
        core_metrics_port=args.core_metrics_port,
        data_node_metrics_port=args.data_node_metrics_port,
    )
