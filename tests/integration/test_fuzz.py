import pytest
import tempfile

from vega_sim.scenario.fuzzing.run import _run
from vega_sim.scenario.fuzzing.registry import REGISTRY


@pytest.mark.integration
def test_fuzz_run():
    # Simply testing that it doesn't error
    with tempfile.TemporaryDirectory() as temp_dir:
        scenario = REGISTRY["overnight"]
        scenario.num_steps = 20
        _run(
            scenario=scenario,
            wallet=False,
            console=False,
            pause=False,
            output=False,
            output_dir=temp_dir,
        )
