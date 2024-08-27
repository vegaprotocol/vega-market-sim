import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_get_vega_time(tds: TradingDataService):
    timestamp = tds.get_vega_time()
    assert isinstance(timestamp, int)
    assert timestamp > 0
