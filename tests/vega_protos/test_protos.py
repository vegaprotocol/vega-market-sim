import pytest

import vega_protos as protos

@pytest.integration.vega_protos
def test_data_node_attributes():
    protos.data_node.api.v2.trading_data

@pytest.mark.vega_protos
def test_vega_attributes():
    protos.vega.assets
    protos.vega.chain_events
    protos.vega.data_source
    protos.vega.governance
    protos.vega.markets
    protos.vega.oracle
    protos.vega.vega
