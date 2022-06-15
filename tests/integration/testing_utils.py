import pytest

from vega_sim.null_service import VegaServiceNull


@pytest.fixture
def vega_service():
    with VegaServiceNull(warn_on_raw_data_access=False) as vega:
        yield vega
