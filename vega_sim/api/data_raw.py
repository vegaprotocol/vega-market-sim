from __future__ import annotations

from collections import namedtuple
from typing import Callable, Dict, Iterable, List, Optional, TypeVar, Union

import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v2 as data_node_protos_v2
import vega_sim.proto.vega as vega_protos
import vega_sim.proto.vega.events.v1.events_pb2 as events_protos

MarketAccount = namedtuple("MarketAccount", ["insurance", "liquidity_fee"])

T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")


def unroll_v2_pagination(
    base_request: S,
    request_func: Callable[[S], T],
    extraction_func: Callable[[S], List[U]],
) -> List[T]:
    base_request.pagination.CopyFrom(data_node_protos_v2.trading_data.Pagination())
    response = request_func(base_request)
    full_list = extraction_func(response)
    while response.page_info.has_next_page:
        base_request.pagination.after = response.page_info.end_cursor
        response = request_func(base_request)
        curr_list = extraction_func(response)
        full_list.extend(curr_list)
    return full_list


def positions_by_market(
    pub_key: str,
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> List[vega_protos.vega.Position]:
    """Output positions of a party."""
    return unroll_v2_pagination(
        base_request=data_node_protos_v2.trading_data.ListPositionsRequest(
            party_id=pub_key,
            market_id=market_id,
        ),
        request_func=lambda x: data_client.ListPositions(x).positions,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


def all_markets(
    data_client: vac.VegaTradingDataClientV2,
) -> List[vega_protos.markets.Market]:
    """
    Output market info.
    """
    return unroll_v2_pagination(
        base_request=data_node_protos_v2.trading_data.ListMarketsRequest(),
        request_func=lambda x: data_client.ListMarkets(x).markets,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


def market_info(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> vega_protos.markets.Market:
    """
    Output market info.
    """
    return data_client.GetMarket(
        data_node_protos_v2.trading_data.GetMarketRequest(market_id=market_id)
    ).market


def list_assets(data_client: vac.VegaTradingDataClientV2):
    return unroll_v2_pagination(
        base_request=data_node_protos_v2.trading_data.ListAssetsRequest(),
        request_func=lambda x: data_client.ListAssets(x).assets,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


def asset_info(
    asset_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> vac.vega.assets.Asset:
    """Returns information on a given asset selected by its ID

    Args:
        asset_id:
            str, The ID of the asset requested
        data_client:
            VegaTradingDataClientV2, an instantiated gRPC data client

    Returns:
        vega.assets.Asset, Object containing data about the requested asset
    """
    return data_client.GetAsset(
        data_node_protos_v2.trading_data.GetAssetRequest(asset_id=asset_id)
    ).asset


def all_market_accounts(
    asset_id: str,
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> Dict[vega_protos.vega.AccountType, MarketAccount]:
    """
    Output liquidity fee account/ insurance pool in the market
    """

    account_filter = data_node_protos_v2.trading_data.AccountFilter(
        asset_id=asset_id,
        market_ids=[market_id],
    )

    accounts = unroll_v2_pagination(
        base_request=data_node_protos_v2.trading_data.ListAccountsRequest(
            filter=account_filter
        ),
        request_func=lambda x: data_client.ListAccounts(x).accounts,
        extraction_func=lambda res: [i.account for i in res.edges],
    )

    return {account.type: account for account in accounts}


def market_accounts(
    asset_id: str,
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> MarketAccount:
    """
    Output liquidity fee account/ insurance pool in the market
    """
    account_type_map = all_market_accounts(
        asset_id=asset_id, market_id=market_id, data_client=data_client
    )
    return MarketAccount(
        account_type_map[vega_protos.vega.ACCOUNT_TYPE_INSURANCE],
        account_type_map[vega_protos.vega.ACCOUNT_TYPE_FEES_LIQUIDITY],
    )


def party_accounts(
    asset_id: str,
    party_id: str,
    data_client: vac.VegaTradingDataClientV2,
):

    account_filter = data_node_protos_v2.trading_data.AccountFilter(
        asset_id=asset_id,
        party_ids=[party_id],
    )

    return unroll_v2_pagination(
        base_request=data_node_protos_v2.trading_data.ListAccountsRequest(
            filter=account_filter
        ),
        request_func=lambda x: data_client.ListAccounts(x).accounts,
        extraction_func=lambda res: [i.account for i in res.edges],
    )


def market_data(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> vega_protos.vega.MarketData:
    """
    Output market info.
    """
    return data_client.GetLatestMarketData(
        data_node_protos_v2.trading_data.GetLatestMarketDataRequest(market_id=market_id)
    ).market_data


def infrastructure_fee_accounts(
    asset_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> List[vega_protos.vega.Account]:
    """
    Output infrastructure fee accounts
    """

    account_filter = data_node_protos_v2.trading_data.AccountFilter(
        asset_id=asset_id,
        account_types=[
            vega_protos.vega.AccountType.ACCOUNT_TYPE_FEES_INFRASTRUCTURE,
        ],
    )

    return unroll_v2_pagination(
        base_request=data_node_protos_v2.trading_data.ListAccountsRequest(
            filter=account_filter
        ),
        request_func=lambda x: data_client.ListAccounts(x).accounts,
        extraction_func=lambda res: [i.account for i in res.edges],
    )


def list_orders(
    data_client: vac.VegaTradingDataClientV2,
    market_id: str = None,
    party_id: str = None,
    reference: str = None,
    live_only: bool = True,
) -> List[vega_protos.vega.Orders]:
    """Gets a list of Orders for the specified market and party.

    Function queries the datanode for a response of orders for the specified market_id
    and party_id and state (defaults to live orders only). The function then unrolls
    pagination and returns a list of Orders.

    Args:
        data_client (vac.VegaTradingDataClientV2):
            An instantiated gRPC trading_data_client_V2.
        market_id (str):
            Id for market to return orders from.
        party_id (str):
            Id for party to return orders from.
        live_only (bool, optional):
            Whether to only return live orders. Defaults to True.

    Returns:
        _type_: _description_
    """

    request = data_node_protos_v2.trading_data.ListOrdersRequest(live_only=live_only)

    for attr, val in [
        ("market_id", market_id),
        ("party_id", party_id),
        ("reference", reference),
    ]:
        if val is not None:
            setattr(request, attr, val)

    return unroll_v2_pagination(
        base_request=request,
        request_func=lambda x: data_client.ListOrders(x).orders,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


def order_status(
    order_id: str, data_client: vac.VegaTradingDataClientV2, version: int = 0
) -> Optional[vega_protos.vega.Order]:
    """Loads information about a specific order identified by the ID.
    Optionally return historic order versions.

    Args:
        order_id:
            str, the order identifier as specified by Vega when originally placed
        data_client:
            VegaTradingDataClientV2, an instantiated gRPC trading data client
        version:
            int, Optional, Version of the order:
                - Set `version` to 0 for most recent version of the order
                - Set `1` for original version of the order
                - Set `2` for first amendment, `3` for second amendment, etc
    Returns:
        Optional[vega.Order], the requested Order object or None if nothing found
    """
    return data_client.GetOrder(
        data_node_protos_v2.trading_data.GetOrderRequest(
            order_id=order_id, version=version
        )
    ).order


def market_depth(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
    max_depth: Optional[int] = None,
) -> Optional[vega_protos.vega.MarketDepth]:
    return data_client.GetLatestMarketDepth(
        data_node_protos_v2.trading_data.GetLatestMarketDepthRequest(
            market_id=market_id, max_depth=max_depth
        )
    )


def liquidity_provisions(
    data_client: vac.VegaTradingDataClientV2,
    market_id: Optional[str] = None,
    party_id: Optional[str] = None,
) -> Optional[List[vega_protos.vega.LiquidityProvision]]:
    """Loads the current liquidity provision(s) for a given market and/or party.

    Args:
        data_client:
            VegaTradingDataClientV2, an instantiated gRPC trading data client
        market_id:
            Optional[str], the ID of the market from which to pull liquidity provisions
        party_id:
            Optional[str], the ID of the party from which to pull liquidity provisions

    Returns:
        List[LiquidityProvision], list of liquidity provisions (if any exist)
    """
    return unroll_v2_pagination(
        base_request=data_node_protos_v2.trading_data.ListLiquidityProvisionsRequest(
            market_id=market_id,
            party_id=party_id,
        ),
        request_func=lambda x: data_client.ListLiquidityProvisions(
            x
        ).liquidity_provisions,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


def order_subscription(
    data_client: vac.VegaCoreClient,
    market_id: Optional[str] = None,
    party_id: Optional[str] = None,
) -> Iterable[vega_protos.api.v1.core.ObserveEventBusResponse]:
    """Subscribe to a stream of Order updates from the data-node.
    The stream of orders returned from this function is an iterable which
    does not end and will continue to tick another order update whenever
    one is received.

    Args:
        market_id:
            Optional[str], If provided, only update orders from this market
        party_id:
            Optional[str], If provided, only update orders from this party
    Returns:
        Iterable[List[vega.Order]], Infinite iterable of lists of order updates
    """
    return data_client.ObserveEventBus(
        iter(
            [
                vega_protos.api.v1.core.ObserveEventBusRequest(
                    type=[events_protos.BUS_EVENT_TYPE_ORDER]
                )
            ]
        )
    )


def margin_levels(
    data_client: vac.VegaTradingDataClientV2,
    party_id: str,
    market_id: Optional[str] = None,
) -> List[vega_protos.vega.MarginLevels]:
    return unroll_v2_pagination(
        data_node_protos_v2.trading_data.ListMarginLevelsRequest(
            market_id=market_id, party_id=party_id
        ),
        request_func=lambda x: data_client.ListMarginLevels(x).margin_levels,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


def get_trades(
    data_client: vac.VegaTradingDataClientV2,
    market_id: str,
    party_id: Optional[str] = None,
    order_id: Optional[str] = None,
) -> List[vega_protos.vega.Trade]:
    return unroll_v2_pagination(
        data_node_protos_v2.trading_data.ListTradesRequest(
            market_id=market_id, party_id=party_id, order_id=order_id
        ),
        request_func=lambda x: data_client.ListTrades(x).trades,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


def get_network_parameter(
    data_client: vac.VegaTradingDataClientV2,
    key: str,
) -> Union[str, int, float]:
    """Returns the value of the specified network parameter.

    Args:
        data_client (vac.VegaTradingDataClientV2):
            Instantiated gRPC client
        key (str):
            The key identifying the network parameter.

    Returns:
        Any:
            The value of the specified network parameter.
    """
    return data_client.GetNetworkParameter(
        data_node_protos_v2.trading_data.GetNetworkParameterRequest(key=key),
    ).network_parameter
