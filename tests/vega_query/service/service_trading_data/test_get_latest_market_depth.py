import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, markets

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_get_latest_market_depth(tds: TradingDataService, markets):
    market_id_filter = markets[0]
    market_depth = tds.get_latest_market_depth(market_id=market_id_filter)
    assert market_depth.market_id == market_id_filter
