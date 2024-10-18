import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, parties

from typing import List

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_get_volume_discount_stats(tds: TradingDataService):
    for stat in tds.get_volume_discount_stats():
        assert isinstance(
            stat, protos.data_node.api.v2.trading_data.VolumeDiscountStats
        )


@pytest.mark.vega_query
def test_get_volume_discount_stats_at_epoch(tds: TradingDataService):
    at_epoch = 0
    for stat in tds.get_volume_discount_stats(at_epoch=0):
        assert stat.at_epoch == at_epoch


@pytest.mark.vega_query
def test_get_volume_discount_stats_party_id(
    tds: TradingDataService, parties: List[str]
):
    party_id = parties[0]
    for stat in tds.get_volume_discount_stats(party_id=party_id):
        assert stat.party_id == party_id
