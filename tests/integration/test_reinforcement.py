import pytest

import vega_sim.reinforcement.run_rl_agent as rl


@pytest.mark.integration
def test_rl_run():
    # Simply testing that it doesn't error
    rl._run(1)
