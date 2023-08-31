import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="We will enable it once job is stable in the Jenkins")
def test_rl_run():
    # Simply testing that it doesn't error
    import vega_sim.reinforcement.run_rl_agent as rl

    rl._run(3)
