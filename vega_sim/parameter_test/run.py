import argparse
import logging

import vega_sim.parameter_test.parameter.experiment as experiment
from vega_sim.parameter_test.parameter.configs import CONFIGS


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    config_map = {c.name: c for c in CONFIGS}

    experiment_to_run = config_map[args.config]
    results = experiment.run_single_parameter_experiment(experiment_to_run)
    experiment.output_logs(
        results, experiment_to_run.parameter_to_vary, experiment=experiment_to_run
    )
