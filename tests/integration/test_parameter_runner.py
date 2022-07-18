from tempfile import TemporaryDirectory
import pytest

import vega_sim.parameter_test.parameter.experiment as experiment
from vega_sim.parameter_test.parameter.configs import CONFIGS


@pytest.mark.integration
@pytest.mark.parametrize("experiment_to_run", CONFIGS)
def test_parameter_runner(experiment_to_run: experiment.SingleParameterExperiment):
    with TemporaryDirectory() as temp_dir:
        experiment_to_run.runs_per_scenario = (
            1  # Likely only need to test the one run per scenario
        )
        results = experiment.run_single_parameter_experiment(experiment_to_run)
        experiment.output_logs(
            results,
            experiment_to_run.parameter_to_vary,
            experiment=experiment_to_run,
            result_folder=temp_dir,
        )
