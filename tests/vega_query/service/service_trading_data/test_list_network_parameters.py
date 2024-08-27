import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_list_network_parameters(
    tds: TradingDataService,
):
    for network_parameter in tds.list_network_parameters(max_pages=1):
        assert isinstance(network_parameter, protos.vega.vega.NetworkParameter)
