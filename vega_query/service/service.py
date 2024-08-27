from typing import Optional
from pathlib import Path

from vega_query.service.utils.utils import Utils
from vega_query.service.networks.constants import Network
from vega_query.service.service_core import CoreService
from vega_query.service.service_trading_data import TradingDataService


class Service:
    def __init__(
        self,
        network: str,
        network_config: Optional[Path] = None,
        port_data_node: Optional[int] = None,
        port_core_node: Optional[int] = None,
    ):
        # Compartmentalise APIs
        class API:
            def __init__(
                self,
                network: Network,
            ):
                # TODO: Implement core service APIs
                self.__data = TradingDataService(
                    network, network_config, port_data_node
                )
                self.__core = CoreService()

            @property
            def data(self):
                return self.__data

            @property
            def core(self):
                return self.__core

        self.api = API(network=network)

        # Compartmentalise utility methods
        self.utils = Utils(core_service=self.api.core, data_service=self.api.data)


if __name__ == "__main__":
    service = Service(network="mainnet")
