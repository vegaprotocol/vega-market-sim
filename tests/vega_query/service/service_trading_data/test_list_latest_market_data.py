import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_get_latest_market_data(tds: TradingDataService):
    markets_data = tds.list_latest_market_data()
