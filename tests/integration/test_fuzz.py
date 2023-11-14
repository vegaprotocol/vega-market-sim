import pytest
import tempfile

import vega_sim.scenario.fuzzed_markets.run_fuzz_test as fuzz


@pytest.mark.integration
def test_fuzz_run():
    # Simply testing that it doesn't error
    with tempfile.TemporaryDirectory() as temp_dir:
        fuzz._run(
            steps=100, output=True, output_dir=temp_dir, perp_market_probability=0.0
        )


@pytest.mark.integration
def test_fuzz_run_perps():
    # Simply testing that it doesn't error
    with tempfile.TemporaryDirectory() as temp_dir:
        fuzz._run(
            steps=100, output=True, output_dir=temp_dir, perp_market_probability=1.0
        )
