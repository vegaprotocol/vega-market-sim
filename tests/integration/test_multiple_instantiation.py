import pytest
from vega_sim.null_service import VegaServiceNull


# Simply testing that multiple Vegas start
# in the same process ok
@pytest.mark.integration
def test_multiple_instantiation():
    with VegaServiceNull(
        run_with_console=False,
        start_live_feeds=False,
    ) as _:
        pass
    with VegaServiceNull(
        run_with_console=False,
        start_live_feeds=False,
    ) as _:
        pass
    with VegaServiceNull(
        run_with_console=False,
        start_live_feeds=False,
    ) as _:
        pass
    with VegaServiceNull(
        run_with_console=False,
        start_live_feeds=False,
    ) as _:
        with VegaServiceNull(
            run_with_console=False,
            start_live_feeds=False,
        ) as _:
            pass
