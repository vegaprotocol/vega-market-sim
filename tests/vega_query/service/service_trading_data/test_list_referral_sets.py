import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, sets

from typing import List

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_list_referral_sets(tds: TradingDataService):
    for set in tds.list_referral_sets():
        assert isinstance(set, protos.data_node.api.v2.trading_data.ReferralSet)


@pytest.mark.vega_query
def test_list_referral_sets_referral_set_id(
    tds: TradingDataService,
    sets: List[protos.data_node.api.v2.trading_data.ReferralSet],
):
    referral_set_id = sets[0].id
    for set in tds.list_referral_sets(referral_set_id=referral_set_id):
        assert set.id == referral_set_id


@pytest.mark.vega_query
def test_list_referral_sets_referrer(
    tds: TradingDataService,
    sets: List[protos.data_node.api.v2.trading_data.ReferralSet],
):
    referrer = sets[0].referrer
    for set in tds.list_referral_sets(referrer=referrer):
        assert set.referrer == referrer


@pytest.mark.vega_query
def test_list_referral_sets_referee(
    tds: TradingDataService,
    sets: List[protos.data_node.api.v2.trading_data.ReferralSet],
):
    referrer = sets[0].referrer
    for set in tds.list_referral_sets(referee=referrer):
        assert isinstance(set, protos.data_node.api.v2.trading_data.ReferralSet)
