import pytest

from vega_query.service.networks.constants import Network
from vega_query.service.service_trading_data import TradingDataService


@pytest.mark.networks
@pytest.mark.vega_query
@pytest.mark.parametrize(
    "network",
    [
        Network.NETWORK_MAINNET,
        Network.NETWORK_TESTNET,
        Network.NETWORK_STAGNET,
    ],
)
def test_trading_data_service(network):
    tds = TradingDataService(network=network)
    tds.ping()
