import pytest


@pytest.mark.integration
def test_fuzz_run():
    # Simply testing that it doesn't error
    import vega_sim.scenario.fuzzed_markets.run_fuzz_test as fuzz

    fuzz._run(steps=100, output=True)
