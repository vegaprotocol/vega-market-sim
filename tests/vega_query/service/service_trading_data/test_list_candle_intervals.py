import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, markets

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_list_candle_intervals(tds: TradingDataService, markets):
    market_id = markets[0]
    for interval_to_candle_id in tds.list_candle_intervals(market_id=market_id):
        assert isinstance(
            interval_to_candle_id,
            protos.data_node.api.v2.trading_data.IntervalToCandleId,
        )
