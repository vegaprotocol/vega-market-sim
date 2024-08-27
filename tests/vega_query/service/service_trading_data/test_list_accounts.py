import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, markets, assets, parties

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_list_accounts(tds: TradingDataService):
    tds.list_accounts(max_pages=1)


@pytest.mark.vega_query
def test_list_accounts_asset_id(tds: TradingDataService, assets):
    asset_filter = assets[0]
    for account in tds.list_accounts(asset_id=asset_filter, max_pages=1):
        assert account.asset == asset_filter


@pytest.mark.vega_query
def test_list_accounts_party_ids(tds: TradingDataService, parties):
    party_ids_filter = parties[:1]
    for account in tds.list_accounts(party_ids=party_ids_filter, max_pages=1):
        assert account.owner in party_ids_filter


@pytest.mark.vega_query
def test_list_accounts_market_ids(tds: TradingDataService, markets):
    market_id_filters = markets[:1]
    for account in tds.list_accounts(market_ids=market_id_filters, max_pages=1):
        assert account.market_id in market_id_filters


@pytest.mark.vega_query
def test_list_accounts_account_types(tds: TradingDataService):
    account_types_filter = protos.vega.vega.AccountType.values()[:1]
    for account in tds.list_accounts(account_types=account_types_filter, max_pages=1):
        assert account.type in account_types_filter
