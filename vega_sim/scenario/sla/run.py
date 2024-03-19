import os
import logging
import pathlib
import datetime
import argparse


from vega_sim.null_service import VegaServiceNull, Ports
from vega_sim.scenario.constants import Network
from vega_sim.scenario.sla.scenario import SLAScenario
from vega_sim.scenario.sla.registry import REGISTRY

from vegapy.service.service import Service
from vegapy.service.networks.constants import Network
import vegapy.visualisations as vis
import vegapy.protobuf.protos as protos


def _run(
    scenario: SLAScenario,
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
            service = Service(
                network=Network.NETWORK_LOCAL,
                network_config=pathlib.Path(
                    f"{vega.log_dir}/vegahome/config/wallet-service/networks/local.toml"
                ),
            )
            fig = vis.plots.sla.create(
                service=service, market_code=scenario.market_config.instrument.code
            )
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            output_dir = output_dir + f"/{datetime.datetime.now()}"
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            fig.savefig(f"{output_dir}/sla_analysis.png")

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
