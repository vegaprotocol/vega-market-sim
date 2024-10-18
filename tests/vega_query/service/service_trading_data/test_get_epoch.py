import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, epoch

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_get_epoch(tds: TradingDataService):
    epoch = tds.get_epoch()
    assert isinstance(epoch, protos.vega.vega.Epoch)


@pytest.mark.vega_query
def test_get_epoch_id(tds: TradingDataService, epoch: protos.vega.vega.Epoch):
    id = epoch.seq
    epoch = tds.get_epoch(id=id)
    assert epoch.seq == id


@pytest.mark.vega_query
def test_get_epoch_block(tds: TradingDataService, epoch: protos.vega.vega.Epoch):
    block = epoch.timestamps.first_block
    epoch = tds.get_epoch(block=block)
    assert epoch.timestamps.first_block == block
