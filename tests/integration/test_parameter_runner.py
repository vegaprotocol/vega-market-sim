from tempfile import TemporaryDirectory
import pytest

import vega_sim.parameter_test.parameter.experiment as experiment
from vega_sim.parameter_test.parameter.configs import CONFIGS
from vega_sim.scenario.common.utils.price_process import random_walk


@pytest.mark.integration
@pytest.mark.parametrize(
    "experiment_to_run",
    [pytest.param(c, id=c.name) for c in CONFIGS],
)
def test_parameter_runner(experiment_to_run: experiment.SingleParameterExperiment):
    with TemporaryDirectory() as temp_dir:
        experiment_to_run.runs_per_scenario = (
            1  # Likely only need to test the one run per scenario
        )
        experiment_to_run.scenario.num_steps = 60
        experiment_to_run.scenario.price_process_fn = lambda: random_walk(
            num_steps=experiment_to_run.scenario.num_steps,
            starting_price=1000,
            sigma=0.1,
        )

        results = experiment.run_single_parameter_experiment(experiment_to_run)
        experiment.output_logs(
            results,
            experiment_to_run.parameter_to_vary,
            experiment=experiment_to_run,
            result_folder=temp_dir,
        )
