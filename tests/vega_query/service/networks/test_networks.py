import pytest

from vega_query.service.networks.constants import Network
from vega_query.service.service_trading_data import TradingDataService


@pytest.mark.vega_query
@pytest.mark.parametrize(
    "network",
    [
        Network.NETWORK_MAINNET,
        Network.NETWORK_TESTNET,
        Network.NETWORK_STAGNET,
    ],
)
def test_network_public(network: Network):
    assert network.config.exists()


@pytest.mark.vega_query
@pytest.mark.parametrize(
    "network",
    [
        Network.NETWORK_LOCAL,
    ],
)
def test_network_local(network: Network):
    assert network.config is None
