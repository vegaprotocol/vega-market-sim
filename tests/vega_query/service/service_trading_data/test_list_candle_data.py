import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, markets, start_timestamp, end_timestamp

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_list_candle_data(tds: TradingDataService, markets: str):
    candle_id = tds.list_candle_intervals(market_id=markets[0])[-1].candle_id
    for candle in tds.list_candle_data(candle_id=candle_id, max_pages=1):
        assert isinstance(candle, protos.data_node.api.v2.trading_data.Candle)


@pytest.mark.vega_query
def test_list_candle_data_from_timestamp(
    tds: TradingDataService, markets: str, start_timestamp: int
):
    candle_intervals = tds.list_candle_intervals(market_id=markets[0])
    candle_id = [
        candle.candle_id for candle in candle_intervals if candle.interval == "1 minute"
    ][0]
    for candle in tds.list_candle_data(
        candle_id=candle_id, from_timestamp=start_timestamp, max_pages=1
    ):
        assert candle.start > (start_timestamp - 60 * 1e9)


@pytest.mark.vega_query
def test_list_candle_data_to_timestamp(
    tds: TradingDataService, markets: str, end_timestamp: int
):
    candle_intervals = tds.list_candle_intervals(market_id=markets[0])
    candle_id = [
        candle.candle_id for candle in candle_intervals if candle.interval == "1 minute"
    ][0]
    for candle in tds.list_candle_data(
        candle_id=candle_id, to_timestamp=end_timestamp, max_pages=1
    ):
        assert candle.start < end_timestamp
