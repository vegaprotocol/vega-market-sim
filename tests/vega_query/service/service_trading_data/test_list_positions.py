import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, markets, parties

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_list_positions(tds: TradingDataService):
    tds.list_positions(max_pages=1)


@pytest.mark.vega_query
def test_list_positions_market_id(tds: TradingDataService, markets):
    market_id_filter = markets[0]
    for position in tds.list_positions(market_id=market_id_filter, max_pages=1):
        assert position.market_id == market_id_filter


@pytest.mark.vega_query
def test_list_positions_party_id(tds: TradingDataService, parties):
    party_id_filter = parties[0]
    for position in tds.list_positions(party_id=party_id_filter, max_pages=1):
        assert position.party_id == party_id_filter
