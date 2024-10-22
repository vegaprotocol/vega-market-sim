import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, epoch, sets

from typing import List

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_get_referral_set_stats(tds: TradingDataService):
    for stat in tds.get_referral_set_stats():
        assert isinstance(stat, protos.data_node.api.v2.trading_data.ReferralSetStats)


def test_get_referral_set_stats_referral_set_id(
    tds: TradingDataService,
    sets: List[protos.data_node.api.v2.trading_data.ReferralSet],
):
    referrer_set_id = sets[0].id
    for stat in tds.get_referral_set_stats(referrer_set_id=referrer_set_id):
        assert isinstance(stat, protos.data_node.api.v2.trading_data.ReferralSetStats)


def test_get_referral_set_stats_at_epoch(
    tds: TradingDataService, epoch: protos.vega.vega.Epoch
):
    at_epoch = epoch.seq
    for stat in tds.get_referral_set_stats(at_epoch=at_epoch):
        assert stat.at_epoch == at_epoch


def test_get_referral_set_stats_referee(
    tds: TradingDataService,
    sets: List[protos.data_node.api.v2.trading_data.ReferralSet],
):
    referrer = sets[0].referrer
    for stat in tds.get_referral_set_stats(referee=referrer):
        assert stat.party_id == referrer
