import pytest

import vega_sim.parameter_test.parameter.experiment as experiment
from vega_sim.parameter_test.parameter.configs import CONFIGS


@pytest.mark.integration
def test_parameter_runner():
    config_map = {c.name: c for c in CONFIGS}
    for key in config_map:
        experiment_to_run = config_map[key]
        results = experiment.run_single_parameter_experiment(experiment_to_run)
        experiment.output_logs(
            results, experiment_to_run.parameter_to_vary, experiment=experiment_to_run
        )
