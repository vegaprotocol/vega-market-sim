import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, parties

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_list_parties(tds: TradingDataService):
    tds.list_parties(max_pages=1)


@pytest.mark.vega_query
def test_list_parties_party_id(tds: TradingDataService, parties):
    party_id_filter = parties[0]
    for party in tds.list_parties(party_id=party_id_filter, max_pages=1):
        assert party.id == party_id_filter
