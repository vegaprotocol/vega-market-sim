from threading import Thread
from typing import Any, Callable
import grpc
import pytest
from concurrent.futures import ThreadPoolExecutor
from vega_sim.grpc.client import VegaTradingDataClient
from vega_sim.null_service import find_free_port

import vega_sim.proto.data_node.api.v1 as data_node_protos
import vega_sim.proto.vega as vega_protos
from vega_sim.api.data_raw import (
    MarketAccount,
    all_market_accounts,
    all_markets,
    asset_info,
    infrastructure_fee_accounts,
    market_accounts,
    market_data,
    market_info,
    order_status,
    positions_by_market,
    order_status_by_reference,
)
from vega_sim.proto.data_node.api.v1.trading_data_pb2_grpc import (
    TradingDataServiceServicer,
    add_TradingDataServiceServicer_to_server,
)


@pytest.fixture
def trading_data_servicer_and_port():
    server = grpc.server(ThreadPoolExecutor(1))
    port = find_free_port()
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    class MockTradingDataServicer(TradingDataServiceServicer):
        pass

    return server, port, MockTradingDataServicer


def test_positions_by_market(trading_data_servicer_and_port):
    def PositionsByParty(self, request, context):
        return data_node_protos.trading_data.PositionsByPartyResponse(
            positions=[
                vega_protos.vega.Position(
                    market_id=request.market_id,
                    party_id=request.party_id,
                    open_volume=1,
                    realised_pnl="100",
                ),
                vega_protos.vega.Position(
                    market_id=request.market_id,
                    party_id=request.party_id,
                    open_volume=2,
                    realised_pnl="200",
                ),
                vega_protos.vega.Position(
                    market_id=request.market_id,
                    party_id=request.party_id,
                    open_volume=3,
                    realised_pnl="300",
                ),
            ]
        )

    server, port, mock_servicer = trading_data_servicer_and_port
    mock_servicer.PositionsByParty = PositionsByParty

    add_TradingDataServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClient(f"localhost:{port}")
    res = positions_by_market("PUB_KEY", market_id="MARK_ID", data_client=data_client)

    assert len(res) == 3
    assert res[0].market_id == "MARK_ID"
    assert res[0].party_id == "PUB_KEY"


def test_all_markets(trading_data_servicer_and_port):
    def AllMarkets(self, request, context):
        return data_node_protos.trading_data.MarketsResponse(
            markets=[
                vega_protos.markets.Market(
                    id="foobar",
                    decimal_places=5,
                    trading_mode=vega_protos.markets.Market.TradingMode.TRADING_MODE_CONTINUOUS,
                    state=vega_protos.markets.Market.State.STATE_ACTIVE,
                ),
                vega_protos.markets.Market(
                    id="foobar2",
                    decimal_places=5,
                    trading_mode=vega_protos.markets.Market.TradingMode.TRADING_MODE_CONTINUOUS,
                    state=vega_protos.markets.Market.State.STATE_SUSPENDED,
                ),
            ]
        )

    server, port, mock_servicer = trading_data_servicer_and_port
    mock_servicer.Markets = AllMarkets

    add_TradingDataServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClient(f"localhost:{port}")
    res = all_markets(data_client=data_client)
    market_map = {m.id: m for m in res}

    assert len(res) == 2
    assert set(m.id for m in res) == {"foobar", "foobar2"}
    assert market_map["foobar"].state == vega_protos.markets.Market.State.STATE_ACTIVE
    assert (
        market_map["foobar2"].state == vega_protos.markets.Market.State.STATE_SUSPENDED
    )


def test_market_info(trading_data_servicer_and_port):
    def MarketByID(self, request, context):
        return data_node_protos.trading_data.MarketByIDResponse(
            market=vega_protos.markets.Market(
                id=request.market_id,
                decimal_places=5,
                trading_mode=vega_protos.markets.Market.TradingMode.TRADING_MODE_CONTINUOUS,
                state=vega_protos.markets.Market.State.STATE_ACTIVE,
            )
        )

    server, port, mock_servicer = trading_data_servicer_and_port
    mock_servicer.MarketByID = MarketByID

    add_TradingDataServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClient(f"localhost:{port}")
    res = market_info(market_id="foobar", data_client=data_client)

    assert res.id == "foobar"
    assert res.state == vega_protos.markets.Market.State.STATE_ACTIVE


def test_asset_info(trading_data_servicer_and_port):
    def AssetByID(self, request, context):
        return data_node_protos.trading_data.AssetByIDResponse(
            asset=vega_protos.assets.Asset(id=request.id)
        )

    server, port, mock_servicer = trading_data_servicer_and_port
    mock_servicer.AssetByID = AssetByID

    add_TradingDataServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClient(f"localhost:{port}")
    res = asset_info(asset_id="foobar", data_client=data_client)

    assert res.id == "foobar"


def test_all_market_accounts(trading_data_servicer_and_port):
    expected = {
        vega_protos.vega.ACCOUNT_TYPE_BOND: vega_protos.vega.Account(
            id="a1",
            asset="asset1",
            market_id="market1",
            type=vega_protos.vega.ACCOUNT_TYPE_BOND,
        ),
        vega_protos.vega.ACCOUNT_TYPE_GENERAL: vega_protos.vega.Account(
            id="a2",
            asset="asset1",
            market_id="market1",
            type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
        ),
    }

    def MarketAccounts(self, request, context):
        return data_node_protos.trading_data.MarketAccountsResponse(
            accounts=[
                vega_protos.vega.Account(
                    id="a1",
                    asset=request.asset,
                    market_id=request.market_id,
                    type=vega_protos.vega.ACCOUNT_TYPE_BOND,
                ),
                vega_protos.vega.Account(
                    id="a2",
                    asset=request.asset,
                    market_id=request.market_id,
                    type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
                ),
            ]
        )

    server, port, mock_servicer = trading_data_servicer_and_port
    mock_servicer.MarketAccounts = MarketAccounts

    add_TradingDataServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClient(f"localhost:{port}")
    res = all_market_accounts(
        market_id="market1", asset_id="asset1", data_client=data_client
    )

    assert res == expected


def test_market_accounts(trading_data_servicer_and_port):
    expected = MarketAccount(
        vega_protos.vega.Account(
            id="liq",
            asset="asset1",
            market_id="market1",
            type=vega_protos.vega.ACCOUNT_TYPE_FEES_LIQUIDITY,
        ),
        vega_protos.vega.Account(
            id="ins",
            asset="asset1",
            market_id="market1",
            type=vega_protos.vega.ACCOUNT_TYPE_INSURANCE,
        ),
    )

    def MarketAccounts(self, request, context):
        return data_node_protos.trading_data.MarketAccountsResponse(
            accounts=[
                vega_protos.vega.Account(
                    id="a1",
                    asset=request.asset,
                    market_id=request.market_id,
                    type=vega_protos.vega.ACCOUNT_TYPE_BOND,
                ),
                vega_protos.vega.Account(
                    id="a2",
                    asset=request.asset,
                    market_id=request.market_id,
                    type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
                ),
                vega_protos.vega.Account(
                    id="liq",
                    asset=request.asset,
                    market_id=request.market_id,
                    type=vega_protos.vega.ACCOUNT_TYPE_FEES_LIQUIDITY,
                ),
                vega_protos.vega.Account(
                    id="ins",
                    asset=request.asset,
                    market_id=request.market_id,
                    type=vega_protos.vega.ACCOUNT_TYPE_INSURANCE,
                ),
            ]
        )

    server, port, mock_servicer = trading_data_servicer_and_port
    mock_servicer.MarketAccounts = MarketAccounts

    add_TradingDataServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClient(f"localhost:{port}")
    res = market_accounts(
        market_id="market1", asset_id="asset1", data_client=data_client
    )

    assert res == expected


def test_market_data(trading_data_servicer_and_port):
    expected = vega_protos.vega.MarketData(mid_price="100", market="foobar")

    def MarketDataByID(self, request, context):
        return data_node_protos.trading_data.MarketDataByIDResponse(
            market_data=vega_protos.vega.MarketData(
                mid_price="100", market=request.market_id
            )
        )

    server, port, mock_servicer = trading_data_servicer_and_port
    mock_servicer.MarketDataByID = MarketDataByID

    add_TradingDataServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClient(f"localhost:{port}")
    res = market_data(market_id="foobar", data_client=data_client)

    assert res == expected


def test_infrastructure_fee_accounts(trading_data_servicer_and_port):
    expected = vega_protos.vega.Account(
        id="ins",
        asset="asset1",
        type=vega_protos.vega.ACCOUNT_TYPE_FEES_INFRASTRUCTURE,
    )

    def FeeInfrastructureAccounts(self, request, context):
        return data_node_protos.trading_data.FeeInfrastructureAccountsResponse(
            accounts=[
                vega_protos.vega.Account(
                    id="ins",
                    asset=request.asset,
                    type=vega_protos.vega.ACCOUNT_TYPE_FEES_INFRASTRUCTURE,
                )
            ]
        )

    server, port, mock_servicer = trading_data_servicer_and_port
    mock_servicer.FeeInfrastructureAccounts = FeeInfrastructureAccounts

    add_TradingDataServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClient(f"localhost:{port}")
    res = infrastructure_fee_accounts(asset_id="asset1", data_client=data_client)

    assert res[0] == expected


def test_order_status(trading_data_servicer_and_port):
    expected = vega_protos.vega.Order(id="foo")

    def OrderByID(self, request, context):
        return data_node_protos.trading_data.OrderByIDResponse(
            order=vega_protos.vega.Order(id=request.order_id)
        )

    server, port, mock_servicer = trading_data_servicer_and_port
    mock_servicer.OrderByID = OrderByID

    add_TradingDataServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClient(f"localhost:{port}")
    res = order_status(order_id="foo", data_client=data_client)

    assert res == expected


def test_order_status_by_reference(trading_data_servicer_and_port):
    expected = vega_protos.vega.Order(id="foo", reference="foo")

    def OrderByReference(self, request, context):
        return data_node_protos.trading_data.OrderByReferenceResponse(
            order=vega_protos.vega.Order(
                id=request.reference, reference=request.reference
            )
        )

    server, port, mock_servicer = trading_data_servicer_and_port
    mock_servicer.OrderByReference = OrderByReference

    add_TradingDataServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClient(f"localhost:{port}")
    res = order_status_by_reference(reference="foo", data_client=data_client)

    assert res == expected
