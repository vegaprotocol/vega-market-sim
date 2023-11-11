from unittest.mock import MagicMock, patch

import pytest
import vega_sim.proto.data_node.api.v2 as data_node_protos_v2
import vega_sim.proto.vega as vega_protos
import vega_sim.proto.vega.events.v1.events_pb2 as events_protos
from tests.vega_sim.api.test_data_raw import (
    core_servicer_and_port,
    trading_data_servicer_and_port,
    trading_data_v2_servicer_and_port,
)
from vega_sim.local_data_cache import (
    _queue_forwarder,
)
from vega_sim.grpc.client import (
    VegaCoreClient,
)
from queue import Queue

from vega_sim.proto.vega.api.v1.core_pb2_grpc import add_CoreServiceServicer_to_server


@patch("vega_sim.api.data.market_position_decimals")
@patch("vega_sim.api.data.market_price_decimals")
def test_order_subscription(mkt_price_mock, mkt_pos_mock, core_servicer_and_port):
    mkt_pos_mock.return_value = 2
    mkt_price_mock.return_value = 2
    orders = [
        vega_protos.vega.Order(
            id="id1",
            market_id="market",
            status=vega_protos.vega.Order.Status.STATUS_ACTIVE,
            reference="ref1",
            side=vega_protos.vega.SIDE_BUY,
            price="10100",
            size=101,
            remaining=101,
            time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
            type=vega_protos.vega.Order.Type.TYPE_LIMIT,
            created_at=1653266950,
            expires_at=1653276950,
            party_id="party1",
            updated_at=1653266950,
            version=1,
        ),
        vega_protos.vega.Order(
            id="id2",
            market_id="market",
            status=vega_protos.vega.Order.Status.STATUS_CANCELLED,
            reference="ref1",
            side=vega_protos.vega.SIDE_BUY,
            price="10100",
            size=101,
            remaining=101,
            time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
            type=vega_protos.vega.Order.Type.TYPE_LIMIT,
            created_at=1653266950,
            expires_at=1653276950,
            party_id="party1",
            updated_at=1653266950,
            version=1,
        ),
        vega_protos.vega.Order(
            id="id3",
            market_id="market",
            status=vega_protos.vega.Order.Status.STATUS_FILLED,
            reference="ref1",
            side=vega_protos.vega.SIDE_BUY,
            price="10100",
            size=101,
            remaining=0,
            time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
            type=vega_protos.vega.Order.Type.TYPE_LIMIT,
            created_at=1653266950,
            expires_at=1653276950,
            party_id="party1",
            updated_at=1653266950,
            version=1,
        ),
        vega_protos.vega.Order(
            id="id4",
            market_id="market",
            status=vega_protos.vega.Order.Status.STATUS_ACTIVE,
            reference="ref1",
            side=vega_protos.vega.SIDE_BUY,
            price="10110",
            size=101,
            remaining=101,
            time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
            type=vega_protos.vega.Order.Type.TYPE_LIMIT,
            created_at=1653266950,
            expires_at=1653276950,
            party_id="party1",
            updated_at=1653266950,
            version=1,
        ),
        vega_protos.vega.Order(
            id="id5",
            market_id="market",
            status=vega_protos.vega.Order.Status.STATUS_ACTIVE,
            reference="ref1",
            side=vega_protos.vega.SIDE_BUY,
            price="10100",
            size=101,
            remaining=101,
            time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
            type=vega_protos.vega.Order.Type.TYPE_LIMIT,
            created_at=1653266950,
            expires_at=1653276950,
            party_id="party2",
            updated_at=1653266950,
            version=1,
        ),
        vega_protos.vega.Order(
            id="id6",
            market_id="market",
            status=vega_protos.vega.Order.Status.STATUS_ACTIVE,
            reference="ref1",
            side=vega_protos.vega.SIDE_SELL,
            price="10400",
            size=111,
            remaining=121,
            time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
            type=vega_protos.vega.Order.Type.TYPE_LIMIT,
            created_at=1653266950,
            expires_at=1653276950,
            party_id="party1",
            updated_at=1653266950,
            version=1,
        ),
        vega_protos.vega.Order(
            id="id7",
            market_id="market",
            status=vega_protos.vega.Order.Status.STATUS_ACTIVE,
            reference="ref1",
            side=vega_protos.vega.SIDE_SELL,
            price="10100",
            size=101,
            remaining=101,
            time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
            type=vega_protos.vega.Order.Type.TYPE_LIMIT,
            created_at=1653266950,
            expires_at=1653276950,
            party_id="party1",
            updated_at=1653266950,
            version=1,
        ),
    ]

    def ObserveEventBus(self, request, context):
        for order_chunk in [orders[:3], orders[3:6], orders[6:]]:
            yield vega_protos.api.v1.core.ObserveEventBusResponse(
                events=[
                    events_protos.BusEvent(
                        order=order, type=events_protos.BUS_EVENT_TYPE_ORDER
                    )
                    for order in order_chunk
                ]
            )

    server, port, mock_servicer = core_servicer_and_port
    mock_servicer.ObserveEventBus = ObserveEventBus

    add_CoreServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaCoreClient(f"localhost:{port}")

    queue = Queue()
    _queue_forwarder(
        data_client=data_client,
        stream_registry=[
            (
                (events_protos.BUS_EVENT_TYPE_ORDER,),
                lambda evt: evt.order,
            ),
        ],
        sink=queue,
    )
    for order in orders:
        assert order.id == queue.get().id


@patch("vega_sim.api.data.get_asset_decimals")
def test_transfer_subscription(mk_asset_decimals, core_servicer_and_port):
    mk_asset_decimals.return_value = 1
    transfers = [
        events_protos.Transfer(
            id="id1",
            from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            to="party2",
            to_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            asset="asset1",
            amount="100000",
            reference="reference",
            status=events_protos.Transfer.Status.STATUS_DONE,
            timestamp=000000000,
            reason="reason",
            one_off=events_protos.OneOffTransfer(deliver_on=000000000),
            recurring=events_protos.RecurringTransfer(),
        ),
        events_protos.Transfer(
            id="id2",
            from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            to="party2",
            to_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            asset="asset1",
            amount="100000",
            reference="reference",
            status=events_protos.Transfer.Status.STATUS_DONE,
            timestamp=000000000,
            reason="reason",
            one_off=events_protos.OneOffTransfer(deliver_on=000000000),
            recurring=events_protos.RecurringTransfer(),
        ),
        events_protos.Transfer(
            id="id3",
            from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            to="party2",
            to_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            asset="asset1",
            amount="100000",
            reference="reference",
            status=events_protos.Transfer.Status.STATUS_DONE,
            timestamp=000000000,
            reason="reason",
            one_off=events_protos.OneOffTransfer(deliver_on=000000000),
            recurring=events_protos.RecurringTransfer(),
        ),
        events_protos.Transfer(
            id="id4",
            from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            to="party2",
            to_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            asset="asset1",
            amount="100000",
            reference="reference",
            status=events_protos.Transfer.Status.STATUS_DONE,
            timestamp=000000000,
            reason="reason",
            one_off=events_protos.OneOffTransfer(deliver_on=000000000),
            recurring=events_protos.RecurringTransfer(),
        ),
        events_protos.Transfer(
            id="id5",
            from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            to="party2",
            to_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            asset="asset1",
            amount="100000",
            reference="reference",
            status=events_protos.Transfer.Status.STATUS_DONE,
            timestamp=000000000,
            reason="reason",
            one_off=events_protos.OneOffTransfer(deliver_on=000000000),
            recurring=events_protos.RecurringTransfer(),
        ),
        events_protos.Transfer(
            id="id6",
            from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            to="party2",
            to_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            asset="asset1",
            amount="100000",
            reference="reference",
            status=events_protos.Transfer.Status.STATUS_DONE,
            timestamp=000000000,
            reason="reason",
            one_off=events_protos.OneOffTransfer(deliver_on=000000000),
            recurring=events_protos.RecurringTransfer(),
        ),
        events_protos.Transfer(
            id="id7",
            from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            to="party2",
            to_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
            asset="asset1",
            amount="100000",
            reference="reference",
            status=events_protos.Transfer.Status.STATUS_DONE,
            timestamp=000000000,
            reason="reason",
            one_off=events_protos.OneOffTransfer(deliver_on=000000000),
            recurring=events_protos.RecurringTransfer(),
        ),
    ]

    def ObserveEventBus(self, request, context):
        for transfer_chunk in [transfers[:3], transfers[3:6], transfers[6:]]:
            yield vega_protos.api.v1.core.ObserveEventBusResponse(
                events=[
                    events_protos.BusEvent(
                        transfer=transfer, type=events_protos.BUS_EVENT_TYPE_TRANSFER
                    )
                    for transfer in transfer_chunk
                ]
            )

    server, port, mock_servicer = core_servicer_and_port
    mock_servicer.ObserveEventBus = ObserveEventBus

    add_CoreServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaCoreClient(f"localhost:{port}")

    queue = Queue()
    _queue_forwarder(
        data_client=data_client,
        stream_registry=[
            (
                (events_protos.BUS_EVENT_TYPE_TRANSFER,),
                lambda evt: evt.transfer,
            ),
        ],
        sink=queue,
    )
    for transfer in transfers:
        assert transfer.id == queue.get().id


def test_network_parameter_subscription(core_servicer_and_port):
    network_parameters_t0 = [
        vega_protos.vega.NetworkParameter(key="key_a_t0", value="param_a_t0"),
        vega_protos.vega.NetworkParameter(key="key_b_t0", value="param_b_t0"),
    ]
    network_parameters_t1 = [
        vega_protos.vega.NetworkParameter(key="key_a_t1", value="param_a_t1"),
        vega_protos.vega.NetworkParameter(key="key_b_t1", value="param_b_t1"),
    ]
    network_parameters_t2 = [
        vega_protos.vega.NetworkParameter(key="key_a_t2", value="param_a_t2"),
        vega_protos.vega.NetworkParameter(key="key_b_t2", value="param_b_t2"),
    ]

    def ObserveEventBus(self, request, context):
        for network_parameters_chunk in [
            network_parameters_t0,
            network_parameters_t1,
            network_parameters_t2,
        ]:
            yield vega_protos.api.v1.core.ObserveEventBusResponse(
                events=[
                    events_protos.BusEvent(
                        network_parameter=network_parameter,
                        type=events_protos.BUS_EVENT_TYPE_NETWORK_PARAMETER,
                    )
                    for network_parameter in network_parameters_chunk
                ]
            )

    server, port, mock_servicer = core_servicer_and_port
    mock_servicer.ObserveEventBus = ObserveEventBus

    add_CoreServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaCoreClient(f"localhost:{port}")

    queue = Queue()
    _queue_forwarder(
        data_client=data_client,
        stream_registry=[
            (
                (events_protos.BUS_EVENT_TYPE_NETWORK_PARAMETER,),
                lambda evt: evt.network_parameter,
            ),
        ],
        sink=queue,
    )
    for network_parameter in (
        network_parameters_t0 + network_parameters_t1 + network_parameters_t2
    ):
        assert network_parameter == queue.get()
