import os

import logging
import argparse

from vega_sim.null_service import VegaServiceNull, Ports

from vega_sim.scenario.constants import Network
from vega_sim.scenario.fuzzed_markets.scenario import FuzzingScenario

from vega_sim.tools.scenario_plots import (
    fuzz_plots,
    plot_run_outputs,
    account_plots,
    plot_price_monitoring,
    reward_plots,
)

from matplotlib import pyplot as plt

logger = logging.getLogger(__name__)


def _run(
    steps: int = 2880,
    console: bool = False,
    output: bool = False,
    output_dir: str = "fuzz_plots",
    core_metrics_port: int = 2723,
    data_node_metrics_port: int = 3651,
):
    scenario = FuzzingScenario(
        num_steps=steps,
        # step_length_seconds=30,
        block_length_seconds=1,
        transactions_per_block=4096,
        output=output,
    )

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        seconds_per_block=scenario.block_length_seconds,
        transactions_per_block=scenario.transactions_per_block,
        retain_log_files=True,
        use_full_vega_wallet=False,
        run_with_console=console,
        port_config={
            Ports.METRICS: core_metrics_port,
            Ports.DATA_NODE_METRICS: data_node_metrics_port,
        },
    ) as vega:
        scenario.run_iteration(
            vega=vega,
            network=Network.NULLCHAIN,
            output_data=output,
            log_every_n_steps=100,
        )

    if output:
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        logger.info("plot 1")
        fuzz_figs = plot_price_monitoring()
        for key, fig in fuzz_figs.items():
            fig.savefig(f"{output_dir}/monitoring-{key}.jpg")
            plt.close(fig)

        logger.info("plot 2")
        fuzz_figs = fuzz_plots()
        for key, fig in fuzz_figs.items():
            fig.savefig(f"{output_dir}/fuzz-{key}.jpg")
            plt.close(fig)

        logger.info("plot 3")
        trading_figs = plot_run_outputs()
        for key, fig in trading_figs.items():
            fig.savefig(f"{output_dir}/trading-{key}.jpg")
            plt.close(fig)

        logger.info("plot 4")
        reward_fig = reward_plots()
        reward_fig.savefig(f"{output_dir}/rewards.jpg")
        plt.close(fig)

        logger.info("plot 5")
        account_fig = account_plots()
        account_fig.savefig(f"{output_dir}/accounts.jpg")
        plt.close(account_fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--steps",
        default=2 * 60 * 12,
        type=int,
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
    )
    parser.add_argument("--console", action="store_true")
    parser.add_argument("--core-metrics-port", default=2723, type=int)
    parser.add_argument("--data-node-metrics-port", default=3651, type=int)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    _run(
        steps=args.steps,
        console=args.console,
        output=True,
        core_metrics_port=args.core_metrics_port,
        data_node_metrics_port=args.data_node_metrics_port,
    )
