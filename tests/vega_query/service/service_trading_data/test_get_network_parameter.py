import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, network_parameters

import vega_protos.protos as protos
from typing import List


@pytest.mark.vega_query
def test_get_network_parameter(
    tds: TradingDataService,
    network_parameters: List[protos.vega.vega.NetworkParameter],
):
    for network_parameter in network_parameters:
        assert (
            network_parameter.value
            == tds.get_network_parameter(key=network_parameter.key).value
        )
