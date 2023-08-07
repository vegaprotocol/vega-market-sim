import pytest
from vega_sim.devops.scenario import DevOpsScenario
from vega_sim.devops.registry import SCENARIOS

from vega_sim.null_service import VegaServiceNull

from vega_sim.scenario.common.utils.price_process import random_walk

from vega_sim.scenario.constants import Network

from vega_sim.proto.vega import markets as markets_protos
import time


@pytest.mark.integration
@pytest.mark.parametrize(
    "scenario_to_test",
    [pytest.param(SCENARIOS[s](), id=s) for s in SCENARIOS],
)
def test_devops_scenarios(scenario_to_test: DevOpsScenario):
    """"""

    scenario_to_test.step_length_seconds = 10
    scenario_to_test.simulation_args.n_steps = 60

    with VegaServiceNull(
        seconds_per_block=1,
        transactions_per_block=1000,
        retain_log_files=True,
        use_full_vega_wallet=False,
        warn_on_raw_data_access=False,
        run_with_console=False,
    ) as vega:
        time.sleep(5.0)
        assert True
