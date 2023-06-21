import pytest
from vega_sim.null_service import VegaServiceNull, Ports


# Testing that you can specify ports using port_config
# in the same process ok
@pytest.mark.integration
def test_port_config():
    expected_data_node_rest_port = 2222
    expected_wallet_port = 1111

    with VegaServiceNull(
        run_with_console=False,
        port_config={
            Ports.DATA_NODE_REST: expected_data_node_rest_port,
            Ports.WALLET: expected_wallet_port
        }
    ) as vega:
      assert vega.wallet_port == expected_wallet_port
      assert vega.data_node_rest_port == expected_data_node_rest_port
      assert isinstance(vega.data_node_grpc_port, int)
      assert isinstance(vega.data_node_postgres_port, int)
      assert isinstance(vega.faucet_port, int)
      assert isinstance(vega.vega_node_port, int)
      assert isinstance(vega.vega_node_grpc_port, int)
      assert isinstance(vega.vega_node_rest_port, int)
      assert isinstance(vega.console_port, int)
