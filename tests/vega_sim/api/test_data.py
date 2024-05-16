from unittest.mock import MagicMock, patch

import pytest
import datetime
import vega_python_protos.protos.data_node.api.v2 as data_node_protos_v2
import vega_python_protos.protos.vega as vega_protos
import vega_python_protos.protos.vega.events.v1.events_pb2 as events_protos
from tests.vega_sim.api.test_data_raw import (
    core_servicer_and_port,
    trading_data_servicer_and_port,
    trading_data_v2_servicer_and_port,
)
from vega_sim.api.data import (
    PartyMarketAccount,
    Fee,
    MarginLevels,
    MissingAssetError,
    Order,
    Transfer,
    OrdersBySide,
    Trade,
    AggregatedLedgerEntry,
    MarginEstimate,
    LiquidationEstimate,
    LiquidationPrice,
    ReferralSet,
    ReferralSetReferee,
    ReferralSetStats,
    PartyAmount,
    ReferrerRewardsGenerated,
    MakerFeesGenerated,
    FeesStats,
    Team,
    TeamReferee,
    TeamRefereeHistory,
    StopOrderEvent,
    OrderSubmission,
    PeggedOrder,
    IcebergOpts,
    StopOrder,
    NetworkParameter,
    AMM,
    ConcentratedLiquidityParameters,
    get_asset_decimals,
    find_asset_id,
    get_trades,
    margin_levels,
    market_position_decimals,
    market_price_decimals,
    open_orders_by_market,
    party_account,
    list_transfers,
    list_ledger_entries,
    estimate_position,
    list_referral_sets,
    list_referral_set_referees,
    get_referral_set_stats,
    get_fees_stats,
    list_teams,
    list_team_referees,
    list_team_referee_history,
    list_stop_orders,
    list_network_parameters,
    list_funding_periods,
    list_amms,
    FundingPeriod,
)
from vega_sim.grpc.client import (
    VegaTradingDataClientV2,
)

from vega_python_protos.protos.data_node.api.v2.trading_data_pb2_grpc import (
    add_TradingDataServiceServicer_to_server as add_TradingDataServiceServicer_v2_to_server,
)


def test_party_account(trading_data_v2_servicer_and_port):
    def ListAccounts(self, request, context):
        return data_node_protos_v2.trading_data.ListAccountsResponse(
            accounts=data_node_protos_v2.trading_data.AccountsConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.AccountEdge(
                        cursor="cursor",
                        node=data_node_protos_v2.trading_data.AccountBalance(
                            balance="1051",
                            type=vega_protos.vega.ACCOUNT_TYPE_BOND,
                            market_id="MARK_ID",
                        ),
                    ),
                    data_node_protos_v2.trading_data.AccountEdge(
                        cursor="cursor",
                        node=data_node_protos_v2.trading_data.AccountBalance(
                            balance="2041",
                            type=vega_protos.vega.ACCOUNT_TYPE_FEES_INFRASTRUCTURE,
                        ),
                    ),
                    data_node_protos_v2.trading_data.AccountEdge(
                        cursor="cursor",
                        node=data_node_protos_v2.trading_data.AccountBalance(
                            balance="5235",
                            type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
                        ),
                    ),
                    data_node_protos_v2.trading_data.AccountEdge(
                        cursor="cursor",
                        node=data_node_protos_v2.trading_data.AccountBalance(
                            balance="6423",
                            type=vega_protos.vega.ACCOUNT_TYPE_MARGIN,
                            market_id="MARK_ID",
                        ),
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListAccounts = ListAccounts

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    res = party_account(
        "PUB_KEY",
        asset_id="a1",
        market_id="MARK_ID",
        data_client=data_client,
        asset_dp=2,
    )

    assert res == PartyMarketAccount(52.35, 64.23, 10.51)

    with patch("vega_sim.api.data.get_asset_decimals", lambda asset_id, data_client: 2):
        res2 = party_account(
            "PUB_KEY",
            asset_id="a1",
            market_id="MARK_ID",
            data_client=data_client,
        )
        assert res2 == res


def test_find_asset_id(trading_data_v2_servicer_and_port):
    def ListAssets(self, request, context):
        return data_node_protos_v2.trading_data.ListAssetsResponse(
            assets=data_node_protos_v2.trading_data.AssetsConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.AssetEdge(
                        cursor="cursor",
                        node=vega_protos.assets.Asset(
                            id="asset1_id",
                            details=vega_protos.assets.AssetDetails(
                                name="asset1", symbol="A1", decimals=5
                            ),
                            status="STATUS_ENABLED",
                        ),
                    ),
                    data_node_protos_v2.trading_data.AssetEdge(
                        cursor="cursor",
                        node=vega_protos.assets.Asset(
                            id="asset2_id",
                            details=vega_protos.assets.AssetDetails(
                                name="asset2", symbol="A2", decimals=5
                            ),
                            status="STATUS_ENABLED",
                        ),
                    ),
                    data_node_protos_v2.trading_data.AssetEdge(
                        cursor="cursor",
                        node=vega_protos.assets.Asset(
                            id="asset3_id",
                            details=vega_protos.assets.AssetDetails(
                                name="asset3", symbol="A3", decimals=5
                            ),
                            status="STATUS_ENABLED",
                        ),
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListAssets = ListAssets

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    res = find_asset_id(symbol="A2", enabled=True, data_client=data_client)
    assert res == "asset2_id"

    with pytest.raises(MissingAssetError):
        find_asset_id(
            symbol="A4", enabled=True, data_client=data_client, raise_on_missing=True
        )

    empty_res = find_asset_id(
        symbol="A4", data_client=data_client, enabled=True, raise_on_missing=False
    )
    assert empty_res is None


@patch("vega_sim.api.data_raw.market_info")
def test_market_price_decimals(mkt_info_mock):
    asset_mock = MagicMock()
    asset_mock.decimal_places = 2
    mkt_info_mock.return_value = asset_mock

    assert market_price_decimals("MKT", None) == 2


@patch("vega_sim.api.data_raw.market_info")
def test_market_position_decimals(mkt_info_mock):
    asset_mock = MagicMock()
    asset_mock.position_decimal_places = 2
    mkt_info_mock.return_value = asset_mock

    assert market_position_decimals("MKT", None) == 2


@patch("vega_sim.api.data_raw.asset_info")
def test_asset_decimals(mkt_info_mock):
    asset_mock = MagicMock()
    asset_mock.details.decimals = 3
    mkt_info_mock.return_value = asset_mock

    assert get_asset_decimals("ASSET", None) == 3


def test_open_orders_by_market(trading_data_v2_servicer_and_port):
    def ListOrders(self, request, context):
        return data_node_protos_v2.trading_data.ListOrdersResponse(
            orders=data_node_protos_v2.trading_data.OrderConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.OrderEdge(
                        cursor="cursor",
                        node=vega_protos.vega.Order(
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
                    ),
                    data_node_protos_v2.trading_data.OrderEdge(
                        cursor="cursor",
                        node=vega_protos.vega.Order(
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
                    ),
                    data_node_protos_v2.trading_data.OrderEdge(
                        cursor="cursor",
                        node=vega_protos.vega.Order(
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
                    ),
                    data_node_protos_v2.trading_data.OrderEdge(
                        cursor="cursor",
                        node=vega_protos.vega.Order(
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
                    ),
                    data_node_protos_v2.trading_data.OrderEdge(
                        cursor="cursor",
                        node=vega_protos.vega.Order(
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
                    ),
                    data_node_protos_v2.trading_data.OrderEdge(
                        cursor="cursor",
                        node=vega_protos.vega.Order(
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
                    ),
                    data_node_protos_v2.trading_data.OrderEdge(
                        cursor="cursor",
                        node=vega_protos.vega.Order(
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
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListOrders = ListOrders

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")

    res = open_orders_by_market(
        market_id="MARK1",
        data_client=data_client,
        price_decimals=2,
        position_decimals=1,
    )

    assert res == OrdersBySide(
        bids=[
            Order(
                id="id1",
                market_id="market",
                status=vega_protos.vega.Order.Status.STATUS_ACTIVE,
                reference="ref1",
                side=vega_protos.vega.SIDE_BUY,
                price=101,
                size=10.1,
                remaining=10.1,
                time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
                order_type=vega_protos.vega.Order.Type.TYPE_LIMIT,
                created_at=1653266950,
                expires_at=1653276950,
                party_id="party1",
                updated_at=1653266950,
                iceberg_order=None,
                version=1,
            ),
            Order(
                id="id4",
                market_id="market",
                status=vega_protos.vega.Order.Status.STATUS_ACTIVE,
                reference="ref1",
                side=vega_protos.vega.SIDE_BUY,
                price=101.10,
                size=10.1,
                remaining=10.1,
                time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
                order_type=vega_protos.vega.Order.Type.TYPE_LIMIT,
                created_at=1653266950,
                expires_at=1653276950,
                party_id="party1",
                updated_at=1653266950,
                iceberg_order=None,
                version=1,
            ),
            Order(
                id="id5",
                market_id="market",
                status=vega_protos.vega.Order.Status.STATUS_ACTIVE,
                reference="ref1",
                side=vega_protos.vega.SIDE_BUY,
                price=101.00,
                size=10.1,
                remaining=10.1,
                time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
                order_type=vega_protos.vega.Order.Type.TYPE_LIMIT,
                created_at=1653266950,
                expires_at=1653276950,
                party_id="party2",
                updated_at=1653266950,
                iceberg_order=None,
                version=1,
            ),
        ],
        asks=[
            Order(
                id="id6",
                market_id="market",
                status=vega_protos.vega.Order.Status.STATUS_ACTIVE,
                reference="ref1",
                side=vega_protos.vega.SIDE_SELL,
                price=104.00,
                size=11.1,
                remaining=12.1,
                time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
                order_type=vega_protos.vega.Order.Type.TYPE_LIMIT,
                created_at=1653266950,
                expires_at=1653276950,
                party_id="party1",
                updated_at=1653266950,
                iceberg_order=None,
                version=1,
            ),
            Order(
                id="id7",
                market_id="market",
                status=vega_protos.vega.Order.Status.STATUS_ACTIVE,
                reference="ref1",
                side=vega_protos.vega.SIDE_SELL,
                price=101.00,
                size=10.1,
                remaining=10.1,
                time_in_force=vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
                order_type=vega_protos.vega.Order.Type.TYPE_LIMIT,
                created_at=1653266950,
                expires_at=1653276950,
                party_id="party1",
                updated_at=1653266950,
                iceberg_order=None,
                version=1,
            ),
        ],
    )


@patch("vega_sim.api.data.get_asset_decimals")
def test_market_limits(mk_asset_decimals, trading_data_v2_servicer_and_port):
    expected = [
        MarginLevels(
            maintenance_margin=10,
            search_level=15,
            initial_margin=20,
            collateral_release_level=30,
            party_id="party",
            market_id="market",
            asset="asset",
            timestamp=datetime.datetime(
                1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            margin_mode=vega_protos.vega.MarginMode.MARGIN_MODE_ISOLATED_MARGIN,
        )
    ]

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
                        node=vega_protos.vega.MarginLevels(
                            maintenance_margin="100",
                            search_level="150",
                            initial_margin="200",
                            collateral_release_level="300",
                            party_id="party",
                            market_id="market",
                            asset="asset",
                            timestamp=0,
                            margin_mode=vega_protos.vega.MarginMode.MARGIN_MODE_ISOLATED_MARGIN,
                        ),
                    )
                ],
            )
        )

    mk_asset_decimals.return_value = 1
    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListMarginLevels = ListMarginLevels

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    res = margin_levels(
        party_id="party",
        market_id="market",
        data_client=data_client,
    )

    assert res == expected


@patch("vega_sim.api.data.get_asset_decimals")
@patch("vega_sim.api.data.market_price_decimals")
@patch("vega_sim.api.data.market_position_decimals")
@patch("vega_sim.api.data_raw.market_info")
def test_get_trades(
    mk_mkt_info,
    mk_pos_decimals,
    mk_price_decimals,
    mk_asset_decimals,
    trading_data_v2_servicer_and_port,
):
    expected = [
        Trade(
            id="t1",
            market_id="m1",
            price=10,
            size=10,
            buyer="b1",
            seller="s1",
            aggressor=vega_protos.vega.SIDE_BUY,
            buy_order="bo1",
            sell_order="so1",
            timestamp=100,
            trade_type=vega_protos.vega.Trade.TYPE_DEFAULT,
            buyer_fee=Fee(
                maker_fee=10,
                infrastructure_fee=1.2,
                liquidity_fee=1.4,
                maker_fee_referrer_discount=0,
                maker_fee_volume_discount=0,
                infrastructure_fee_referrer_discount=0,
                infrastructure_fee_volume_discount=0,
                liquidity_fee_referrer_discount=0,
                liquidity_fee_volume_discount=0,
            ),
            seller_fee=Fee(
                maker_fee=20,
                infrastructure_fee=12.2,
                liquidity_fee=14.4,
                maker_fee_referrer_discount=0,
                maker_fee_volume_discount=0,
                infrastructure_fee_referrer_discount=0,
                infrastructure_fee_volume_discount=0,
                liquidity_fee_referrer_discount=0,
                liquidity_fee_volume_discount=0,
            ),
            buyer_auction_batch=100,
            seller_auction_batch=96,
        )
    ]

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
                        node=vega_protos.vega.Trade(
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
                                maker_fee="100",
                                infrastructure_fee="12",
                                liquidity_fee="14",
                                maker_fee_referrer_discount="0",
                                maker_fee_volume_discount="0",
                                infrastructure_fee_referrer_discount="0",
                                infrastructure_fee_volume_discount="0",
                                liquidity_fee_referrer_discount="0",
                                liquidity_fee_volume_discount="0",
                            ),
                            seller_fee=vega_protos.vega.Fee(
                                maker_fee="200",
                                infrastructure_fee="122",
                                liquidity_fee="144",
                                maker_fee_referrer_discount="0",
                                maker_fee_volume_discount="0",
                                infrastructure_fee_referrer_discount="0",
                                infrastructure_fee_volume_discount="0",
                                liquidity_fee_referrer_discount="0",
                                liquidity_fee_volume_discount="0",
                            ),
                            buyer_auction_batch=100,
                            seller_auction_batch=96,
                        ),
                    )
                ],
            )
        )

    mk_asset_decimals.return_value = 1
    mk_pos_decimals.return_value = 0
    mk_price_decimals.return_value = 1

    mk_mkt = MagicMock()
    mk_mkt_info.return_value = mk_mkt
    mk_mkt.tradable_instrument.instrument.future.settlement_asset = "a1"

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListTrades = ListTrades

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    res = get_trades(
        party_id="party",
        market_id="market",
        data_client=data_client,
    )

    assert res == expected


@patch("vega_sim.api.data.get_asset_decimals")
def test_list_transfers(
    mk_asset_decimals,
    trading_data_v2_servicer_and_port,
):
    expected = Transfer(
        id="id1",
        party_from="party1",
        from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
        party_to="party2",
        to_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
        asset="asset1",
        amount=1000.0,
        reference="reference",
        status=events_protos.Transfer.Status.STATUS_DONE,
        timestamp=000000000,
        reason="reason",
        one_off=events_protos.OneOffTransfer(deliver_on=000000000),
        recurring=events_protos.RecurringTransfer(),
    )

    node = data_node_protos_v2.trading_data.TransferNode(
        transfer=events_protos.Transfer(
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
        )
    )
    setattr(node.transfer, "from", "party1")

    def ListTransfers(self, request, context):
        return data_node_protos_v2.trading_data.ListTransfersResponse(
            transfers=data_node_protos_v2.trading_data.TransferConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.TransferEdge(
                        cursor="cursor",
                        node=node,
                    )
                ],
            )
        )

    mk_asset_decimals.return_value = 2

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListTransfers = ListTransfers

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    res = list_transfers(
        data_client=data_client,
        party_id="party2",
        direction=data_node_protos_v2.trading_data.TRANSFER_DIRECTION_TRANSFER_TO_OR_FROM,
    )

    assert res == [expected]


def test_list_ledger_entries(trading_data_v2_servicer_and_port):
    expected = data_node_protos_v2.trading_data.AggregatedLedgerEntry(
        timestamp=10000000, quantity="540", asset_id="asset1"
    )

    def ListLedgerEntries(self, request, context):
        return data_node_protos_v2.trading_data.ListLedgerEntriesResponse(
            ledger_entries=data_node_protos_v2.trading_data.AggregatedLedgerEntriesConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.AggregatedLedgerEntriesEdge(
                        cursor="cursor",
                        node=expected,
                    )
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListLedgerEntries = ListLedgerEntries

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    res = list_ledger_entries(
        data_client=data_client, asset_id="asset1", asset_decimals_map={"asset1": 1}
    )

    assert res == [
        AggregatedLedgerEntry(
            timestamp=10000000,
            quantity=54,
            asset_id="asset1",
            transfer_type=0,
            from_account_type=0,
            to_account_type=0,
            from_account_market_id="",
            from_account_party_id="",
            to_account_market_id="",
            to_account_party_id="",
        )
    ]
    res2 = list_ledger_entries(
        data_client=data_client, asset_id="asset1", asset_decimals_map={"asset1": 2}
    )

    assert res2 == [
        AggregatedLedgerEntry(
            timestamp=10000000,
            quantity=5.4,
            asset_id="asset1",
            transfer_type=0,
            from_account_type=0,
            to_account_type=0,
            from_account_market_id="",
            from_account_party_id="",
            to_account_market_id="",
            to_account_party_id="",
        )
    ]


def test_estimate_position(trading_data_v2_servicer_and_port):
    expected_market_id = "market"

    expected_margin = MarginEstimate(
        best_case=MarginLevels(
            maintenance_margin=10,
            search_level=20,
            initial_margin=30,
            collateral_release_level=40,
            party_id="party",
            market_id=expected_market_id,
            asset="asset",
            timestamp=datetime.datetime(
                1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            margin_mode=vega_protos.vega.MarginMode.MARGIN_MODE_ISOLATED_MARGIN,
        ),
        worst_case=MarginLevels(
            maintenance_margin=10,
            search_level=20,
            initial_margin=30,
            collateral_release_level=40,
            party_id="party",
            market_id=expected_market_id,
            asset="asset",
            timestamp=datetime.datetime(
                1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            margin_mode=vega_protos.vega.MarginMode.MARGIN_MODE_ISOLATED_MARGIN,
        ),
    )
    expected_liquidation = LiquidationEstimate(
        best_case=LiquidationPrice(
            open_volume_only=1000.00,
            including_buy_orders=2000.00,
            including_sell_orders=3000.00,
        ),
        worst_case=LiquidationPrice(
            open_volume_only=1000.00,
            including_buy_orders=2000.00,
            including_sell_orders=3000.00,
        ),
    )

    def EstimatePosition(self, request, context):
        return data_node_protos_v2.trading_data.EstimatePositionResponse(
            margin=data_node_protos_v2.trading_data.MarginEstimate(
                best_case=vega_protos.vega.MarginLevels(
                    maintenance_margin="100",
                    search_level="200",
                    initial_margin="300",
                    collateral_release_level="400",
                    party_id="party",
                    market_id=request.market_id,
                    asset="asset",
                    timestamp=0,
                    margin_mode=vega_protos.vega.MarginMode.MARGIN_MODE_ISOLATED_MARGIN,
                ),
                worst_case=vega_protos.vega.MarginLevels(
                    maintenance_margin="100",
                    search_level="200",
                    initial_margin="300",
                    collateral_release_level="400",
                    party_id="party",
                    market_id=request.market_id,
                    asset="asset",
                    timestamp=0,
                    margin_mode=vega_protos.vega.MarginMode.MARGIN_MODE_ISOLATED_MARGIN,
                ),
            ),
            liquidation=data_node_protos_v2.trading_data.LiquidationEstimate(
                best_case=data_node_protos_v2.trading_data.LiquidationPrice(
                    open_volume_only="10000",
                    including_buy_orders="20000",
                    including_sell_orders="30000",
                ),
                worst_case=data_node_protos_v2.trading_data.LiquidationPrice(
                    open_volume_only="10000",
                    including_buy_orders="20000",
                    including_sell_orders="30000",
                ),
            ),
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.EstimatePosition = EstimatePosition

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    margin, collateral_increase_estimate, liquidation = estimate_position(
        data_client=data_client,
        market_id=expected_market_id,
        open_volume=1,
        average_entry_price=100,
        margin_account_balance=10000,
        general_account_balance=10000,
        order_margin_account_balance=10000,
        margin_mode=vega_protos.vega.MarginMode.MARGIN_MODE_ISOLATED_MARGIN,
        orders=[(vega_protos.vega.SIDE_BUY, "500.00", 1, False)],
        margin_factor=0.5,
        asset_decimals={"asset": 1},
    )

    assert margin == expected_margin
    assert collateral_increase_estimate == collateral_increase_estimate
    assert liquidation == expected_liquidation


def test_list_referral_sets(trading_data_v2_servicer_and_port):
    def ListReferralSets(self, request, context):
        return data_node_protos_v2.trading_data.ListReferralSetsResponse(
            referral_sets=data_node_protos_v2.trading_data.ReferralSetConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.ReferralSetEdge(
                        cursor="cursor",
                        node=data_node_protos_v2.trading_data.ReferralSet(
                            id=request.referral_set_id,
                            referrer=request.referrer,
                            created_at=123456789,
                            updated_at=123456789,
                        ),
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListReferralSets = ListReferralSets

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")

    assert list_referral_sets(data_client=data_client, referral_set_id="id") == {
        "id": ReferralSet(
            id="id", referrer="", created_at=123456789, updated_at=123456789
        )
    }
    assert list_referral_sets(data_client=data_client, referral_set_id="id") == {
        "id": ReferralSet(
            id="id", referrer="", created_at=123456789, updated_at=123456789
        )
    }


def test_list_referral_set_referees(trading_data_v2_servicer_and_port):
    def ListReferralSetReferees(self, request, context):
        return data_node_protos_v2.trading_data.ListReferralSetRefereesResponse(
            referral_set_referees=data_node_protos_v2.trading_data.ReferralSetRefereeConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.ReferralSetRefereeEdge(
                        cursor="cursor",
                        node=data_node_protos_v2.trading_data.ReferralSetReferee(
                            referral_set_id=request.referral_set_id,
                            referee=request.referee,
                            joined_at=123456789,
                            at_epoch=1,
                        ),
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListReferralSetReferees = ListReferralSetReferees

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    assert list_referral_set_referees(
        data_client=data_client, referral_set_id="id"
    ) == {
        "id": {
            "": ReferralSetReferee(
                referral_set_id="id",
                referee="",
                joined_at=123456789,
                at_epoch=1,
            )
        }
    }


def test_get_referral_set_stats(trading_data_v2_servicer_and_port):
    def GetReferralSetStats(self, request, context):
        return data_node_protos_v2.trading_data.GetReferralSetStatsResponse(
            stats=data_node_protos_v2.trading_data.ReferralSetStatsConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.ReferralSetStatsEdge(
                        cursor="cursor",
                        node=data_node_protos_v2.trading_data.ReferralSetStats(
                            at_epoch=request.at_epoch,
                            referral_set_running_notional_taker_volume="1000",
                            party_id=request.referee,
                            discount_factor="0.1",
                            reward_factor="0.1",
                            epoch_notional_taker_volume="1000",
                        ),
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.GetReferralSetStats = GetReferralSetStats

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    assert get_referral_set_stats(data_client=data_client, at_epoch=1) == [
        ReferralSetStats(
            at_epoch=1,
            referral_set_running_notional_taker_volume=1000.0,
            party_id="",
            discount_factor=0.1,
            reward_factor=0.1,
            epoch_notional_taker_volume=1000.0,
        )
    ]
    assert get_referral_set_stats(data_client=data_client, referee="referee") == [
        ReferralSetStats(
            at_epoch=0,
            referral_set_running_notional_taker_volume=1000.0,
            party_id="referee",
            discount_factor=0.1,
            reward_factor=0.1,
            epoch_notional_taker_volume=1000.0,
        )
    ]


def test_get_fees_stats(trading_data_v2_servicer_and_port):
    def GetFeesStats(self, request, context):
        return data_node_protos_v2.trading_data.GetFeesStatsResponse(
            fees_stats=vega_protos.events.v1.events.FeesStats(
                market=request.market_id,
                asset=request.asset_id,
                epoch_seq=1,
                total_rewards_received=[
                    vega_protos.events.v1.events.PartyAmount(
                        party="referrer1", amount="1000"
                    )
                ],
                referrer_rewards_generated=[
                    vega_protos.events.v1.events.ReferrerRewardsGenerated(
                        referrer="referrer1",
                        generated_reward=[
                            vega_protos.events.v1.events.PartyAmount(
                                party="referee1", amount="1000"
                            )
                        ],
                    )
                ],
                referees_discount_applied=[
                    vega_protos.events.v1.events.PartyAmount(
                        party="referrer1", amount="1000"
                    )
                ],
                volume_discount_applied=[
                    vega_protos.events.v1.events.PartyAmount(
                        party="referrer1", amount="1000"
                    )
                ],
                total_maker_fees_received=[
                    vega_protos.events.v1.events.PartyAmount(
                        party="referrer1", amount="1000"
                    )
                ],
                maker_fees_generated=[
                    vega_protos.events.v1.events.MakerFeesGenerated(
                        taker="taker1",
                        maker_fees_paid=[
                            vega_protos.events.v1.events.PartyAmount(
                                party="referrer1", amount="1000"
                            )
                        ],
                    )
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.GetFeesStats = GetFeesStats

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    assert get_fees_stats(
        data_client=data_client,
        market_id="market_id",
        asset_decimals={"": 1},
    ) == FeesStats(
        market="market_id",
        asset="",
        epoch_seq=1,
        total_rewards_received=[PartyAmount(party="referrer1", amount=100.0)],
        referrer_rewards_generated=[
            ReferrerRewardsGenerated(
                referrer="referrer1",
                generated_reward=[PartyAmount(party="referee1", amount=100.0)],
            )
        ],
        referees_discount_applied=[PartyAmount(party="referrer1", amount=100.0)],
        volume_discount_applied=[PartyAmount(party="referrer1", amount=100.0)],
        total_maker_fees_received=[PartyAmount(party="referrer1", amount=100.0)],
        maker_fees_generated=[
            MakerFeesGenerated(
                taker="taker1",
                maker_fees_paid=[PartyAmount(party="referrer1", amount=100.0)],
            )
        ],
    )
    assert get_fees_stats(
        data_client=data_client,
        asset_id="asset",
        asset_decimals={"asset": 1},
    ) == FeesStats(
        market="",
        asset="asset",
        epoch_seq=1,
        total_rewards_received=[PartyAmount(party="referrer1", amount=100.0)],
        referrer_rewards_generated=[
            ReferrerRewardsGenerated(
                referrer="referrer1",
                generated_reward=[PartyAmount(party="referee1", amount=100.0)],
            )
        ],
        referees_discount_applied=[PartyAmount(party="referrer1", amount=100.0)],
        volume_discount_applied=[PartyAmount(party="referrer1", amount=100.0)],
        total_maker_fees_received=[PartyAmount(party="referrer1", amount=100.0)],
        maker_fees_generated=[
            MakerFeesGenerated(
                taker="taker1",
                maker_fees_paid=[PartyAmount(party="referrer1", amount=100.0)],
            )
        ],
    )


def test_list_teams(trading_data_v2_servicer_and_port):
    def ListTeams(self, request, context):
        return data_node_protos_v2.trading_data.ListTeamsResponse(
            teams=data_node_protos_v2.trading_data.TeamConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.TeamEdge(
                        cursor="cursor",
                        node=data_node_protos_v2.trading_data.Team(
                            team_id=request.team_id,
                            referrer="referrer",
                            name="name",
                            team_url="team_url",
                            avatar_url="avatar_url",
                            created_at=123456789,
                            closed=False,
                            created_at_epoch=1,
                        ),
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListTeams = ListTeams

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    assert list_teams(data_client=data_client, team_id="id") == {
        "id": Team(
            team_id="id",
            referrer="referrer",
            name="name",
            team_url="team_url",
            avatar_url="avatar_url",
            created_at=123456789,
            closed=False,
            created_at_epoch=1,
        )
    }


def test_list_team_referees(trading_data_v2_servicer_and_port):
    def ListTeamReferees(self, request, context):
        return data_node_protos_v2.trading_data.ListTeamRefereesResponse(
            team_referees=data_node_protos_v2.trading_data.TeamRefereeConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.TeamRefereeEdge(
                        cursor="cursor",
                        node=data_node_protos_v2.trading_data.TeamReferee(
                            team_id=request.team_id,
                            referee="referee",
                            joined_at=123456789,
                            joined_at_epoch=1,
                        ),
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListTeamReferees = ListTeamReferees

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    assert list_team_referees(data_client=data_client, team_id="id") == [
        TeamReferee(
            team_id="id",
            referee="referee",
            joined_at=123456789,
            joined_at_epoch=1,
        )
    ]


def test_list_team_referee_history(trading_data_v2_servicer_and_port):
    def ListTeamRefereeHistory(self, request, context):
        return data_node_protos_v2.trading_data.ListTeamRefereeHistoryResponse(
            team_referee_history=data_node_protos_v2.trading_data.TeamRefereeHistoryConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.TeamRefereeHistoryEdge(
                        cursor="cursor",
                        node=data_node_protos_v2.trading_data.TeamRefereeHistory(
                            team_id="id",
                            joined_at=123456789,
                            joined_at_epoch=1,
                        ),
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListTeamRefereeHistory = ListTeamRefereeHistory

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    assert list_team_referee_history(data_client=data_client, referee="id") == [
        TeamRefereeHistory(
            team_id="id",
            joined_at=123456789,
            joined_at_epoch=1,
        )
    ]


def test_list_stop_orders(trading_data_v2_servicer_and_port):
    def ListStopOrders(self, request, context):
        return data_node_protos_v2.trading_data.ListStopOrdersResponse(
            orders=data_node_protos_v2.trading_data.StopOrderConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.StopOrderEdge(
                        cursor="cursor",
                        node=vega_protos.events.v1.events.StopOrderEvent(
                            submission=vega_protos.commands.v1.commands.OrderSubmission(
                                market_id="market_id",
                                price="30",
                                size=10000,
                                side=vega_protos.vega.SIDE_BUY,
                                time_in_force=vega_protos.vega.Order.TIME_IN_FORCE_IOC,
                                type=vega_protos.vega.Order.TYPE_LIMIT,
                                reference="reference",
                                pegged_order=vega_protos.vega.PeggedOrder(
                                    reference=vega_protos.vega.PEGGED_REFERENCE_MID,
                                    offset="1",
                                ),
                                post_only=True,
                                reduce_only=True,
                                iceberg_opts=vega_protos.commands.v1.commands.IcebergOpts(
                                    peak_size=1000,
                                    minimum_visible_size=100,
                                ),
                            ),
                            stop_order=vega_protos.vega.StopOrder(
                                id="id",
                                oco_link_id="oco_link_id",
                                expires_at=1672531200000000000,
                                expiry_strategy=vega_protos.vega.StopOrder.EXPIRY_STRATEGY_CANCELS,
                                trigger_direction=vega_protos.vega.StopOrder.TRIGGER_DIRECTION_RISES_ABOVE,
                                status=vega_protos.vega.StopOrder.STATUS_PENDING,
                                created_at=1672531200000000000,
                                updated_at=1672531200000000000,
                                order_id="order_id",
                                party_id="party_id",
                                market_id="market_id",
                                rejection_reason=vega_protos.vega.StopOrder.REJECTION_REASON_TRADING_NOT_ALLOWED,
                                price="1000",
                                trailing_percent_offset=None,
                            ),
                        ),
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListStopOrders = ListStopOrders

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    stop_orders = list_stop_orders(
        data_client=data_client,
        market_price_decimals_map={"market_id": 0},
        market_position_decimals_map={"market_id": 2},
    )

    expected_expiry = datetime.datetime.fromtimestamp(1672531200)
    assert stop_orders == [
        StopOrderEvent(
            submission=OrderSubmission(
                market_id="market_id",
                price=30.0,
                size=100.0,
                side=vega_protos.vega.SIDE_BUY,
                time_in_force=vega_protos.vega.Order.TIME_IN_FORCE_IOC,
                type=vega_protos.vega.Order.TYPE_LIMIT,
                reference="reference",
                pegged_order=PeggedOrder(
                    reference=vega_protos.vega.PEGGED_REFERENCE_MID,
                    offset=1.0,
                ),
                post_only=True,
                reduce_only=True,
                iceberg_opts=IcebergOpts(
                    peak_size=10.0,
                    minimum_visible_size=1.0,
                ),
            ),
            stop_order=StopOrder(
                id="id",
                oco_link_id="oco_link_id",
                expires_at=expected_expiry,
                expiry_strategy=vega_protos.vega.StopOrder.EXPIRY_STRATEGY_CANCELS,
                trigger_direction=vega_protos.vega.StopOrder.TRIGGER_DIRECTION_RISES_ABOVE,
                status=vega_protos.vega.StopOrder.STATUS_PENDING,
                created_at=expected_expiry,
                updated_at=expected_expiry,
                order_id="order_id",
                party_id="party_id",
                market_id="market_id",
                rejection_reason=vega_protos.vega.StopOrder.REJECTION_REASON_TRADING_NOT_ALLOWED,
                price=1000.0,
            ),
        )
    ]


def test_list_network_parameters(trading_data_v2_servicer_and_port):
    def ListNetworkParameters(self, request, context):
        return data_node_protos_v2.trading_data.ListNetworkParametersResponse(
            network_parameters=data_node_protos_v2.trading_data.NetworkParameterConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.NetworkParameterEdge(
                        cursor="cursor",
                        node=vega_protos.vega.NetworkParameter(
                            key="key_a",
                            value="value_a",
                        ),
                    ),
                    data_node_protos_v2.trading_data.NetworkParameterEdge(
                        cursor="cursor",
                        node=vega_protos.vega.NetworkParameter(
                            key="key_b",
                            value="value_b",
                        ),
                    ),
                    data_node_protos_v2.trading_data.NetworkParameterEdge(
                        cursor="cursor",
                        node=vega_protos.vega.NetworkParameter(
                            key="key_c",
                            value="value_c",
                        ),
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListNetworkParameters = ListNetworkParameters

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    network_parameters = list_network_parameters(
        data_client=data_client,
    )
    assert network_parameters == [
        NetworkParameter("key_a", "value_a"),
        NetworkParameter("key_b", "value_b"),
        NetworkParameter("key_c", "value_c"),
    ]


def test_list_funding_periods(trading_data_v2_servicer_and_port):
    def ListFundingPeriods(self, request, context):
        return data_node_protos_v2.trading_data.ListFundingPeriodsResponse(
            funding_periods=data_node_protos_v2.trading_data.FundingPeriodConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.FundingPeriodEdge(
                        cursor="cursor",
                        node=vega_protos.events.v1.events.FundingPeriod(
                            market_id=request.market_id,
                            start=1708589798000000000,
                            end=1708618598000000000,
                            internal_twap="3200000",
                            external_twap="3316791",
                            funding_payment="-115133",
                            funding_rate="-0.0347121660665384",
                        ),
                    ),
                    data_node_protos_v2.trading_data.FundingPeriodEdge(
                        cursor="cursor",
                        node=vega_protos.events.v1.events.FundingPeriod(
                            market_id=request.market_id,
                            start=1708618598000000000,
                            end=None,
                            internal_twap="3200000",
                            external_twap=None,
                            funding_payment=None,
                            funding_rate=None,
                        ),
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListFundingPeriods = ListFundingPeriods

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    market_id = "mkt_id"
    funding_periods = list_funding_periods(
        market_id=market_id,
        data_client=data_client,
        market_to_asset_map={market_id: "asset_id"},
        asset_decimals_map={"asset_id": 6},
    )
    # Thu Feb 22 2024 16:16:38 GMT+0000
    assert funding_periods == [
        FundingPeriod(
            start_time=datetime.datetime(
                year=2024,
                month=2,
                day=22,
                hour=8,
                minute=16,
                second=38,
                tzinfo=datetime.timezone.utc,
            ),
            end_time=datetime.datetime(
                year=2024,
                month=2,
                day=22,
                hour=16,
                minute=16,
                second=38,
                tzinfo=datetime.timezone.utc,
            ),
            internal_twap=3.2,
            external_twap=3.316791,
            funding_payment=-0.115133,
            funding_rate=-0.0347121660665384,
        ),
        FundingPeriod(
            start_time=datetime.datetime(
                year=2024,
                month=2,
                day=22,
                hour=16,
                minute=16,
                second=38,
                tzinfo=datetime.timezone.utc,
            ),
            end_time=None,
            internal_twap=3.2,
            external_twap=None,
            funding_payment=None,
            funding_rate=None,
        ),
    ]


def test_list_amms(trading_data_v2_servicer_and_port):
    def ListAMMs(self, request, context):
        return data_node_protos_v2.trading_data.ListAMMsResponse(
            amms=data_node_protos_v2.trading_data.AMMConnection(
                page_info=data_node_protos_v2.trading_data.PageInfo(
                    has_next_page=False,
                    has_previous_page=False,
                    start_cursor="",
                    end_cursor="",
                ),
                edges=[
                    data_node_protos_v2.trading_data.AMMEdge(
                        cursor="cursor",
                        node=events_protos.AMM(
                            id="id",
                            party_id="party_id",
                            market_id="market_id",
                            amm_party_id="amm_party_id",
                            commitment="10000",
                            parameters=events_protos.AMM.ConcentratedLiquidityParameters(
                                base="20000",
                                lower_bound="10000",
                                upper_bound="30000",
                                leverage_at_lower_bound="10",
                                leverage_at_upper_bound="10",
                            ),
                            status=events_protos.AMM.Status.STATUS_ACTIVE,
                            status_reason=events_protos.AMM.StatusReason.STATUS_REASON_UNSPECIFIED,
                        ),
                    ),
                ],
            )
        )

    server, port, mock_servicer = trading_data_v2_servicer_and_port
    mock_servicer.ListAMMs = ListAMMs

    add_TradingDataServiceServicer_v2_to_server(mock_servicer(), server)

    data_client = VegaTradingDataClientV2(f"localhost:{port}")
    assert list_amms(
        data_client=data_client,
        price_decimals_map={"market_id": 1},
        asset_decimals_map={"asset_id": 1},
        market_to_asset_map={"market_id": "asset_id"},
        party_id="party_id",
    ) == [
        AMM(
            id="id",
            party_id="party_id",
            market_id="market_id",
            amm_party_id="amm_party_id",
            commitment=1000,
            parameters=ConcentratedLiquidityParameters(
                base=2000,
                lower_bound=1000,
                upper_bound=3000,
                leverage_at_lower_bound=10,
                leverage_at_upper_bound=10,
            ),
            status=events_protos.AMM.Status.STATUS_ACTIVE,
            status_reason=events_protos.AMM.StatusReason.STATUS_REASON_UNSPECIFIED,
        )
    ]
