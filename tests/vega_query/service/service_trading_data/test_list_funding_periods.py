import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import (
    logger,
    tds,
    perpetual_markets,
    start_timestamp,
    end_timestamp,
)

import vega_protos.protos as protos
import datetime


@pytest.mark.vega_query
def test_list_funding_periods_market_id(tds: TradingDataService, perpetual_markets):
    market_id_filter = perpetual_markets[0]
    for funding_period in tds.list_funding_periods(
        market_id=market_id_filter,
        max_pages=1,
    ):
        assert funding_period.market_id == market_id_filter


@pytest.mark.vega_query
def test_list_funding_period_data_points_start_timestamp(
    tds: TradingDataService, perpetual_markets, start_timestamp
):
    market_id_filter = perpetual_markets[0]
    for funding_period in tds.list_funding_periods(
        market_id=market_id_filter,
        start_timestamp=start_timestamp,
        max_pages=1,
    ):
        assert funding_period.start > start_timestamp


@pytest.mark.vega_query
def test_list_funding_period_data_points_end_timestamp(
    tds: TradingDataService, perpetual_markets, end_timestamp
):
    market_id_filter = perpetual_markets[0]
    for funding_period in tds.list_funding_periods(
        market_id=market_id_filter,
        end_timestamp=end_timestamp,
        max_pages=1,
    ):
        assert funding_period.start < end_timestamp
