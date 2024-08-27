import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, markets

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_list_markets(tds: TradingDataService):
    tds.list_markets(max_pages=1)


@pytest.mark.vega_query
def test_list_markets_include_settled(tds: TradingDataService):
    for market in tds.list_markets(include_settled=False, max_pages=1):
        assert market.state not in [protos.vega.markets.Market.State.STATE_SETTLED]
