import grpc
from vega_sim.proto.data_node.api.v1 import trading_data_grpc
from vega_sim.proto.vega.api.v1 import core_grpc


class GRPCClient:
    """
    A `GRPCClient` talks to a gRPC endpoint.
    """

    def __init__(self, url: str, channel=None) -> None:
        if url is None:
            raise Exception("Missing node URL")
        self.url = url

        if channel is None:
            # get a gRPC channel
            channel = grpc.insecure_channel(self.url)
            grpc.channel_ready_future(channel).result(timeout=10)

        self.channel = channel


class VegaTradingDataClient(GRPCClient):
    """
    The Vega Trading Data Client talks to a back-end node.
    """

    def __init__(self, url: str, channel=None) -> None:
        super().__init__(url, channel=channel)
        self._tradingdata = trading_data_grpc.TradingDataServiceStub(self.channel)

    def __getattr__(self, funcname):
        return getattr(self._tradingdata, funcname)


class VegaCoreClient(GRPCClient):
    """
    The Vega Core Client talks to a back-end node.
    """

    def __init__(self, url: str, channel=None) -> None:
        super().__init__(url, channel=channel)
        self._core = core_grpc.CoreServiceStub(self.channel)

    def __getattr__(self, funcname):
        return getattr(self._core, funcname)
