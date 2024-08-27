import pytest
from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import (
    tds,
    markets,
    parties,
    orders,
    start_timestamp,
    end_timestamp,
)

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_list_trades(tds: TradingDataService):
    tds.list_trades(max_pages=1)


@pytest.mark.vega_query
def test_list_trades_market_ids(tds: TradingDataService, markets):
    market_ids_filter = markets[:2]
    for trade in tds.list_trades(market_ids=market_ids_filter, max_pages=1):
        assert trade.market_id in market_ids_filter


@pytest.mark.vega_query
def test_list_trades_order_ids(tds: TradingDataService, orders):
    market_ids_filter = [order.market_id for order in orders[:2]]
    order_ids_filter = [order.id for order in orders[:2]]
    for trade in tds.list_trades(
        market_ids=market_ids_filter, order_ids=order_ids_filter, max_pages=1
    ):
        assert (trade.buy_order in order_ids_filter) or (
            trade.sell_order in order_ids_filter
        )


@pytest.mark.vega_query
def test_list_trades_party_ids(tds: TradingDataService, parties):
    party_ids_filter = parties[:2]
    for trade in tds.list_trades(party_ids=party_ids_filter, max_pages=1):
        assert (trade.buyer in party_ids_filter) or (trade.seller in party_ids_filter)


@pytest.mark.vega_query
def test_list_trades_date_range_start_timestamp(
    tds: TradingDataService, start_timestamp
):
    for trade in tds.list_trades(
        date_range_start_timestamp=start_timestamp, max_pages=1
    ):
        assert trade.timestamp > start_timestamp


@pytest.mark.vega_query
def test_list_trades_date_range_end_timestamp(tds: TradingDataService, end_timestamp):
    for trade in tds.list_trades(date_range_end_timestamp=end_timestamp, max_pages=1):
        assert trade.timestamp < end_timestamp
