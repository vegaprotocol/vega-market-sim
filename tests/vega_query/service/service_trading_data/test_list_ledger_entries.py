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

import datetime


@pytest.mark.vega_query
def test_list_ledger_entries_from_party_ids(tds: TradingDataService, parties):
    from_party_ids_filter = [parties[1]]
    for ledger_entry in tds.list_ledger_entries(
        from_party_ids=from_party_ids_filter,
        max_pages=1,
    ):
        assert ledger_entry.from_account_party_id == from_party_ids_filter[0]


@pytest.mark.vega_query
def test_list_ledger_entries_to_party_ids(tds: TradingDataService, parties):
    to_party_ids_filter = [parties[1]]
    for ledger_entry in tds.list_ledger_entries(
        to_party_ids=to_party_ids_filter,
        max_pages=1,
    ):
        assert ledger_entry.to_account_party_id == to_party_ids_filter[0]


@pytest.mark.vega_query
def test_list_ledger_entries_close_on_accounts_filter(tds: TradingDataService, parties):
    from_party_ids_filter = [parties[0]]
    to_party_ids_filter = [parties[1]]
    for ledger_entry in tds.list_ledger_entries(
        close_on_account_filters=True,
        from_party_ids=from_party_ids_filter,
        to_party_ids=to_party_ids_filter,
        max_pages=1,
    ):
        assert (ledger_entry.from_account_party_id == from_party_ids_filter[0]) and (
            ledger_entry.to_account_party_id == to_party_ids_filter[0]
        )


@pytest.mark.vega_query
def test_list_ledger_entries_date_range_start_timestamp(
    tds: TradingDataService, parties, start_timestamp
):
    from_party_ids_filter = [parties[0]]
    for ledger_entry in tds.list_ledger_entries(
        from_party_ids=from_party_ids_filter,
        date_range_start_timestamp=start_timestamp,
        max_pages=1,
    ):
        assert ledger_entry.timestamp > start_timestamp


@pytest.mark.vega_query
def test_list_ledger_entries_date_range_end_timestamp(
    tds: TradingDataService, parties, end_timestamp
):
    from_party_ids_filter = [parties[0]]
    for ledger_entry in tds.list_ledger_entries(
        from_party_ids=from_party_ids_filter,
        date_range_end_timestamp=end_timestamp,
        max_pages=1,
    ):
        assert ledger_entry.timestamp < end_timestamp
