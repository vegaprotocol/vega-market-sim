import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, amms

from typing import List

import vega_protos as protos


@pytest.mark.vega_query
def test_list_amms(tds: TradingDataService):
    for amm in tds.list_amms(max_pages=1):
        assert isinstance(amm, protos.vega.events.v1.events.AMM)


@pytest.mark.vega_query
def test_list_amms_market_id(
    tds: TradingDataService, amms: List[protos.vega.events.v1.events.AMM]
):
    market_id = amms[0].market_id if amms != [] else "0" * 64
    for amm in tds.list_amms(market_id=market_id, max_pages=1):
        assert amm.market_id == market_id


@pytest.mark.vega_query
def test_list_amms_party_id(tds: TradingDataService, amms):
    party_id = amms[0].party_id if amms != [] else "0" * 64
    for amm in tds.list_amms(party_id=party_id, max_pages=1):
        assert amm.party_id == party_id


@pytest.mark.vega_query
def test_list_amms(tds: TradingDataService, amms):
    market_id = amms[0].market_id if amms != [] else "0" * 64
    amms = tds.list_amms(market_id=market_id, max_pages=1)
    for amm in tds.list_amms(market_id=market_id, max_pages=1):
        assert amm.market_id == market_id
