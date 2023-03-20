import logging
import argparse

from vega_sim.null_service import VegaServiceNull

from vega_sim.scenario.constants import Network
from vega_sim.scenario.fuzzed_markets.scenario import FuzzingScenario

from vega_sim.tools.scenario_plots import fuzz_plots, plot_run_outputs


def output_summary(output):
    pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--steps",
        default=2 * 60 * 12,
        type=int,
    )
    args = parser.parse_args()

    scenario = FuzzingScenario(
        num_steps=args.steps,
        step_length_seconds=30,
        block_length_seconds=1,
        transactions_per_block=4096,
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
            output_data=True,
        )

    fuzz_figs = fuzz_plots()
    for key, fig in fuzz_figs.items():
        fig.savefig(f"fuzz-{key}.jpg")

    trading_figs = plot_run_outputs()
    for key, fig in trading_figs.items():
        fig.savefig(f"trading-{key}.jpg")

