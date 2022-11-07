import grpc
import pytest
from concurrent.futures import ThreadPoolExecutor
from vega_sim.grpc.client import (
    VegaCoreClient,
    VegaTradingDataClient,
    VegaTradingDataClientV2,
)
from vega_sim.null_service import find_free_port

import vega_sim.proto.data_node.api.v1 as data_node_protos
import vega_sim.proto.data_node.api.v2 as data_node_protos_v2
import vega_sim.proto.vega as vega_protos
from vega_sim.api.data_raw import (
    MarketAccount,
    all_market_accounts,
    all_markets,
    asset_info,
    get_trades,
    infrastructure_fee_accounts,
    liquidity_provisions,
    market_accounts,
    market_data,
    market_info,
    order_status,
    positions_by_market,
    order_subscription,
    margin_levels,
)
from vega_sim.proto.data_node.api.v1.trading_data_pb2_grpc import (
    TradingDataServiceServicer,
    add_TradingDataServiceServicer_to_server,
)
from vega_sim.proto.data_node.api.v2.trading_data_pb2_grpc import (
    TradingDataServiceServicer as TradingDataServiceServicerV2,
    add_TradingDataServiceServicer_to_server as add_TradingDataServiceServicer_v2_to_server,
)
from vega_sim.proto.vega.api.v1.core_pb2_grpc import (
    CoreServiceServicer,
    add_CoreServiceServicer_to_server,
)

import vega_sim.proto.vega.events.v1.events_pb2 as events_protos


@pytest.fixture
def trading_data_servicer_and_port():
    server = grpc.server(ThreadPoolExecutor(1))
    port = find_free_port()
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    class MockTradingDataServicer(TradingDataServiceServicer):
        pass

    return server, port, MockTradingDataServicer


@pytest.fixture
def trading_data_v2_servicer_and_port():
    server = grpc.server(ThreadPoolExecutor(1))
    port = find_free_port()
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    class MockTradingDataServicer(TradingDataServiceServicerV2):
        pass

    return server, port, MockTradingDataServicer


@pytest.fixture
def core_servicer_and_port():
    server = grpc.server(ThreadPoolExecutor(1))
    port = find_free_port()
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    class MockCoreServicer(CoreServiceServicer):
        pass

    return server, port, MockCoreServicer


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
            id="ins",
            asset="asset1",
            market_id="market1",
            type=vega_protos.vega.ACCOUNT_TYPE_INSURANCE,
        ),
        vega_protos.vega.Account(
            id="liq",
            asset="asset1",
            market_id="market1",
            type=vega_protos.vega.ACCOUNT_TYPE_FEES_LIQUIDITY,
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


def test_liquidity_provisions(trading_data_servicer_and_port):
    def LiquidityProvisions(self, request, context):
        return data_node_protos.trading_data.LiquidityProvisionsResponse(
            liquidity_provisions=[
                vega_protos.vega.LiquidityProvision(
                    market_id=request.market, party_id=request.party
                )
            ]
        )

    server, port, mock_servicer = trading_data_servicer_and_port
    mock_servicer.LiquidityProvisions = LiquidityProvisions

    add_TradingDataServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClient(f"localhost:{port}")
    res = liquidity_provisions(
        market_id="MARKET", party_id="PARTY", data_client=data_client
    )

    assert res[0].market_id == "MARKET"


def test_order_subscription(core_servicer_and_port):
    def ObserveEventBus(self, request, context):
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
        for order_chunk in [orders[:3], orders[3:6], orders[6:]]:
            yield vega_protos.api.v1.core.ObserveEventBusResponse(
                events=[events_protos.BusEvent(order=order) for order in order_chunk]
            )

    server, port, mock_servicer = core_servicer_and_port
    mock_servicer.ObserveEventBus = ObserveEventBus

    add_CoreServiceServicer_to_server(mock_servicer(), server)

    data_client = VegaCoreClient(f"localhost:{port}")

    queue = order_subscription(
        data_client=data_client,
    )

    batch_one = next(queue)
    batch_two = next(queue)
    batch_three = next(queue)

    assert len(batch_one.events) == 3
    assert len(batch_two.events) == 3
    assert len(batch_three.events) == 1


def test_market_limits(trading_data_v2_servicer_and_port):
    expected = vega_protos.vega.MarginLevels(
        maintenance_margin="100",
        search_level="150",
        initial_margin="200",
        collateral_release_level="300",
        party_id="party",
        market_id="market",
        asset="asset",
        timestamp=1251825938592,
    )

    def ListMarginLevels(self, request, context):
        return data_node_protos_v2.trading_data.ListMarginLevelsResponse(
            margin_levels=data_node_protos_v2.trading_data.MarginConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.MarginEdge(
                        cursor="cursor",
                        node=expected,
                    )
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListMarginLevels = ListMarginLevels

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    res = margin_levels(party_id="party", market_id="market", data_client=data_client)

    assert res == [expected]


def test_get_trades(trading_data_v2_servicer_and_port):
    expected = vega_protos.vega.Trade(
        id="t1",
        market_id="m1",
        price="100",
        size=10,
        buyer="b1",
        seller="s1",
        aggressor=vega_protos.vega.SIDE_BUY,
        buy_order="bo1",
        sell_order="so1",
        timestamp=100,
        type=vega_protos.vega.Trade.TYPE_DEFAULT,
        buyer_fee=vega_protos.vega.Fee(
            maker_fee="100", infrastructure_fee="12", liquidity_fee="14"
        ),
        seller_fee=vega_protos.vega.Fee(
            maker_fee="200", infrastructure_fee="122", liquidity_fee="144"
        ),
        buyer_auction_batch=100,
        seller_auction_batch=96,
    )

    def ListTrades(self, request, context):
        return data_node_protos_v2.trading_data.ListTradesResponse(
            trades=data_node_protos_v2.trading_data.TradeConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.TradeEdge(
                        cursor="cursor",
                        node=expected,
                    )
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListTrades = ListTrades

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    res = get_trades(party_id="party", market_id="market", data_client=data_client)

    assert res == [expected]
