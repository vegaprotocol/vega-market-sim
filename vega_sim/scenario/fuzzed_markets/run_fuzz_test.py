import os

import logging
import argparse

from vega_sim.null_service import VegaServiceNull

from vega_sim.scenario.constants import Network
from vega_sim.scenario.fuzzed_markets.scenario import FuzzingScenario

from vega_sim.tools.scenario_plots import fuzz_plots, plot_run_outputs, account_plots


def _run(steps: int = 2880, output: bool = False):
    scenario = FuzzingScenario(
        num_steps=steps,
        step_length_seconds=30,
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
    ) as vega:
        scenario.run_iteration(
            vega=vega,
            network=Network.NULLCHAIN,
            output_data=output,
            log_every_n_steps=100,
        )

    if output:
        if not os.path.exists("fuzz_plots"):
            os.mkdir("fuzz_plots")

        fuzz_figs = fuzz_plots()
        for key, fig in fuzz_figs.items():
            fig.savefig(f"fuzz_plots/fuzz-{key}.jpg")

        trading_figs = plot_run_outputs()
        for key, fig in trading_figs.items():
            fig.savefig(f"fuzz_plots/trading-{key}.jpg")

        account_fig = account_plots()
        account_fig.savefig(f"fuzz_plots/accounts-{key}.jpg")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--steps",
        default=2 * 60 * 12,
        type=int,
    )
    args = parser.parse_args()

    _run(steps=args.steps, output=True)
