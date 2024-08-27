import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, markets, parties

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_list_all_positions(tds: TradingDataService):
    tds.list_all_positions(max_pages=1)


@pytest.mark.vega_query
def test_list_all_positions_party_id(tds: TradingDataService, parties):
    party_ids_filter = parties[:2]
    for position in tds.list_all_positions(party_ids=party_ids_filter, max_pages=1):
        assert position.party_id in party_ids_filter


@pytest.mark.vega_query
def test_list_all_positions_market_id(tds: TradingDataService, markets):
    market_ids_filter = markets[:2]
    for position in tds.list_all_positions(market_ids=market_ids_filter, max_pages=1):
        assert position.market_id in market_ids_filter
