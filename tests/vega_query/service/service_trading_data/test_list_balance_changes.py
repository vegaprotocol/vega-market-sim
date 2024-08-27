import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import (
    tds,
    markets,
    parties,
    assets,
    start_timestamp,
    end_timestamp,
)

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_list_balance_changes_asset_id(
    tds: TradingDataService, assets, start_timestamp, end_timestamp
):
    asset_id_filter = assets[0]
    for aggregated_balance in tds.list_balance_changes(
        asset_id=asset_id_filter,
        date_range_start_timestamp=start_timestamp,
        date_range_end_timestamp=end_timestamp,
        max_pages=1,
    ):
        assert aggregated_balance.asset_id == asset_id_filter


@pytest.mark.vega_query
def test_list_balance_changes_party_ids(
    tds: TradingDataService, parties, start_timestamp, end_timestamp
):
    party_ids_filter = parties[:2]
    for aggregated_balance in tds.list_balance_changes(
        party_ids=party_ids_filter,
        date_range_start_timestamp=start_timestamp,
        date_range_end_timestamp=end_timestamp,
        max_pages=1,
    ):
        assert aggregated_balance.party_id in party_ids_filter


@pytest.mark.vega_query
def test_list_balance_changes_market_ids(
    tds: TradingDataService, markets, start_timestamp, end_timestamp
):
    market_ids_filter = markets[:1]
    for aggregated_balance in tds.list_balance_changes(
        market_ids=market_ids_filter,
        date_range_start_timestamp=start_timestamp,
        date_range_end_timestamp=end_timestamp,
        max_pages=1,
    ):
        assert aggregated_balance.market_id in market_ids_filter


@pytest.mark.vega_query
@pytest.mark.parametrize("account_type", protos.vega.vega.AccountType.values())
def test_list_balance_changes_account_types(
    tds: TradingDataService, account_type, start_timestamp, end_timestamp
):
    for aggregated_balance in tds.list_balance_changes(
        account_types=[account_type],
        date_range_start_timestamp=start_timestamp,
        date_range_end_timestamp=end_timestamp,
        max_pages=1,
    ):
        assert aggregated_balance.account_type == account_type


@pytest.mark.vega_query
def test_list_balance_changes_start_timestamp(
    tds: TradingDataService,
    start_timestamp,
    markets,
):
    market_ids_filter = markets[:1]
    for aggregated_balance in tds.list_balance_changes(
        market_ids=market_ids_filter,
        date_range_start_timestamp=start_timestamp,
        max_pages=1,
    ):
        assert aggregated_balance.timestamp > start_timestamp


@pytest.mark.vega_query
def test_list_balance_changes_end_timestamp(
    tds: TradingDataService,
    start_timestamp,
    end_timestamp,
    markets,
):
    market_ids_filter = markets[:1]
    for aggregated_balance in tds.list_balance_changes(
        market_ids=market_ids_filter,
        date_range_start_timestamp=start_timestamp,
        date_range_end_timestamp=end_timestamp,
        max_pages=1,
    ):
        assert aggregated_balance.timestamp < end_timestamp
