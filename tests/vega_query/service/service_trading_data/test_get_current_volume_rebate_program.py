import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_get_latest_volume_rebate_program(tds: TradingDataService):
    program = tds.get_current_volume_rebate_program()
    if program is not None:
        assert isinstance(
            program, protos.data_node.api.v2.trading_data.VolumeRebateProgram
        )
