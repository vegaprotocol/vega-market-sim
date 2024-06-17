import os
import logging
import pathlib
import datetime
import argparse


from vega_sim.null_service import VegaServiceNull, Ports
from vega_sim.scenario.constants import Network
from vega_sim.scenario.amm.scenario import AMMScenario
from vega_sim.scenario.amm.registry import REGISTRY

from vegapy.service.service import Service
from vegapy.service.networks.constants import Network

# import vegapy.visualisations as vis
import vega_python_protos as protos


def _run(
    scenario: AMMScenario,
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

        if output:
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            output_dir = output_dir + f"/{datetime.datetime.now()}"
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)

        # # Use vegapy package to produce plots
        # service = Service(
        #     network=Network.NETWORK_LOCAL,
        #     network_config=pathlib.Path(
        #         f"{vega.log_dir}/vegahome/config/wallet-service/networks/local.toml"
        #     ),
        # )
        # markets = service.api.data.list_markets(include_settled=True)

        # date_range_end_timestamp = service.api.data.get_vega_time()
        # for market in markets:
        #     date_range_start_timestamp = market.market_timestamps.pending

        #     is_spot = (
        #         market.tradable_instrument.instrument.spot != protos.vega.markets.Spot()
        #     )
        #     is_future = (
        #         market.tradable_instrument.instrument.future
        #         != protos.vega.markets.Future()
        #     )
        #     is_perpetual = (
        #         market.tradable_instrument.instrument.perpetual
        #         != protos.vega.markets.Perpetual()
        #     )

        #     if is_spot:
        #         market_asset = market.tradable_instrument.instrument.spot.quote_asset
        #     if is_future:
        #         market_asset = (
        #             market.tradable_instrument.instrument.future.settlement_asset
        #         )
        #     if is_perpetual:
        #         market_asset = (
        #             market.tradable_instrument.instrument.perpetual.settlement_asset
        #         )

        #     asset = service.api.data.get_asset(market_asset)
        #     trades = service.api.data.list_trades(
        #         market_ids=[market.id],
        #         date_range_start_timestamp=date_range_start_timestamp,
        #     )
        #     market_data_history = service.api.data.get_market_data_history_by_id(
        #         market.id,
        #         start_timestamp=date_range_start_timestamp,
        #     )
        #     aggregated_balance_history = service.api.data.list_balance_changes(
        #         asset_id=asset.id,
        #         market_ids=[market.id],
        #         party_ids=["network"],
        #         account_types=[protos.vega.vega.AccountType.ACCOUNT_TYPE_INSURANCE],
        #         date_range_start_timestamp=date_range_start_timestamp,
        #         date_range_end_timestamp=date_range_end_timestamp,
        #     )
        #     # Update figures
        #     if output:
        #         market_output_dir = f"{output_dir}/{market.tradable_instrument.instrument.code.replace('/', '')}"
        #         if not os.path.exists(market_output_dir):
        #             os.mkdir(market_output_dir)
        #         vis.plot.price_monitoring_analysis(market, market_data_history).savefig(
        #             f"{market_output_dir}/price_monitoring_analysis.png"
        #         )
        #         if not is_spot:
        #             vis.plot.liquidation_analysis(
        #                 asset,
        #                 market,
        #                 trades,
        #                 market_data_history,
        #                 aggregated_balance_history,
        #             ).savefig(f"{market_output_dir}/liquidation_analysis.png")
        #         if is_perpetual:
        #             funding_periods = service.api.data.list_funding_periods(
        #                 market_id=market.id,
        #                 start_timestamp=date_range_start_timestamp,
        #             )
        #             funding_period_data_points = (
        #                 service.api.data.list_funding_period_data_points(
        #                     market.id,
        #                     start_timestamp=date_range_start_timestamp,
        #                 )
        #             )
        #             vis.plot.funding_analysis(
        #                 asset,
        #                 market,
        #                 market_data_history,
        #                 funding_periods,
        #                 funding_period_data_points,
        #             ).savefig(f"{market_output_dir}/funding_analysis.png")

        if pause:
            input("Waiting after run finished.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--market", required=True, type=str)
    parser.add_argument("-s", "--steps", default=600, type=int)
    parser.add_argument("-p", "--pause", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-o", "--output", action="store_true")
    parser.add_argument("-c", "--console", action="store_true")
    parser.add_argument("-w", "--wallet", action="store_true")
    parser.add_argument("--core-metrics-port", default=2723, type=int)
    parser.add_argument("--data-node-metrics-port", default=3651, type=int)
    args = parser.parse_args()

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
