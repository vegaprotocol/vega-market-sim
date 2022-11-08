# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from blockexplorer import blockexplorer_pb2 as blockexplorer_dot_blockexplorer__pb2


class BlockExplorerServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetTransaction = channel.unary_unary(
            "/blockexplorer.api.v1.BlockExplorerService/GetTransaction",
            request_serializer=blockexplorer_dot_blockexplorer__pb2.GetTransactionRequest.SerializeToString,
            response_deserializer=blockexplorer_dot_blockexplorer__pb2.GetTransactionResponse.FromString,
        )
        self.ListTransactions = channel.unary_unary(
            "/blockexplorer.api.v1.BlockExplorerService/ListTransactions",
            request_serializer=blockexplorer_dot_blockexplorer__pb2.ListTransactionsRequest.SerializeToString,
            response_deserializer=blockexplorer_dot_blockexplorer__pb2.ListTransactionsResponse.FromString,
        )


class BlockExplorerServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetTransaction(self, request, context):
        """Get transaction

        Get a transaction from the Vega blockchain
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def ListTransactions(self, request, context):
        """List transactions

        List transactions from the Vega blockchain
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_BlockExplorerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetTransaction": grpc.unary_unary_rpc_method_handler(
            servicer.GetTransaction,
            request_deserializer=blockexplorer_dot_blockexplorer__pb2.GetTransactionRequest.FromString,
            response_serializer=blockexplorer_dot_blockexplorer__pb2.GetTransactionResponse.SerializeToString,
        ),
        "ListTransactions": grpc.unary_unary_rpc_method_handler(
            servicer.ListTransactions,
            request_deserializer=blockexplorer_dot_blockexplorer__pb2.ListTransactionsRequest.FromString,
            response_serializer=blockexplorer_dot_blockexplorer__pb2.ListTransactionsResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "blockexplorer.api.v1.BlockExplorerService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class BlockExplorerService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetTransaction(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/blockexplorer.api.v1.BlockExplorerService/GetTransaction",
            blockexplorer_dot_blockexplorer__pb2.GetTransactionRequest.SerializeToString,
            blockexplorer_dot_blockexplorer__pb2.GetTransactionResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def ListTransactions(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/blockexplorer.api.v1.BlockExplorerService/ListTransactions",
            blockexplorer_dot_blockexplorer__pb2.ListTransactionsRequest.SerializeToString,
            blockexplorer_dot_blockexplorer__pb2.ListTransactionsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
