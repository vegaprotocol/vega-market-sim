import grpc
from abc import ABC
from vega_sim.proto.data_node.api.v1 import trading_data_grpc
from vega_sim.proto.data_node.api.v2 import trading_data_grpc as trading_data_grpc_v2
from vega_sim.proto.vega.api.v1 import core_grpc, corestate_grpc


class GRPCClient(ABC):
    """
    A `GRPCClient` talks to a gRPC endpoint.
    """

    STUB_CLASS = None

    def __init__(self, url: str, channel=None) -> None:
        if url is None:
            raise Exception("Missing node URL")
        self.url = url

        if channel is None:
            # get a gRPC channel
            channel = grpc.insecure_channel(self.url)
            grpc.channel_ready_future(channel).result(timeout=10)

        self.channel = channel
        self._client = self.STUB_CLASS(self.channel)

    def __getattr__(self, funcname):
        return getattr(self._client, funcname)


class VegaTradingDataClient(GRPCClient):
    """
    The Vega Trading Data Client talks to a back-end node.
    """

    STUB_CLASS = trading_data_grpc.TradingDataServiceStub


class VegaTradingDataClientV2(GRPCClient):
    """
    The Vega Trading Data Client talks to a back-end node.
    """

    STUB_CLASS = trading_data_grpc_v2.TradingDataServiceStub


class VegaCoreClient(GRPCClient):
    """
    The Vega Core Client talks to a back-end node.
    """

    STUB_CLASS = core_grpc.CoreServiceStub


class VegaCoreStateClient(GRPCClient):
    """
    The Vega Core Client talks to a back-end node.
    """

    STUB_CLASS = corestate_grpc.CoreStateServiceStub
