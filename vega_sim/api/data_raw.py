from __future__ import annotations

from collections import namedtuple
from typing import Callable, Dict, Iterable, List, Optional, TypeVar

import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v1 as data_node_protos
import vega_sim.proto.data_node.api.v2 as data_node_protos_v2
import vega_sim.proto.vega as vega_protos
import vega_sim.proto.vega.events.v1.events_pb2 as events_protos

MarketAccount = namedtuple("MarketAccount", ["insurance", "liquidity_fee"])

T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")


def unroll_pagination(
    base_request: S, extraction_func: Callable[[S], List[T]], step_size: int = 50
) -> List[T]:
    skip = 0
    base_request.pagination.CopyFrom(
        data_node_protos.trading_data.Pagination(skip=skip, limit=step_size)
    )
    curr_list = extraction_func(base_request)
    full_list = curr_list
    while len(curr_list) == step_size:
        skip += step_size
        base_request.pagination.skip = skip
        curr_list = extraction_func(base_request)
        full_list.extend(curr_list)
    return full_list


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
    data_client: vac.VegaTradingDataClient,
) -> List[vega_protos.vega.Position]:
    """Output positions of a party."""
    positions_req = data_node_protos.trading_data.PositionsByPartyRequest(
        party_id=pub_key,
        market_id=market_id,
    )
    return data_client.PositionsByParty(positions_req).positions


def all_markets(
    data_client: vac.VegaTradingDataClient,
) -> List[vega_protos.markets.Market]:
    """
    Output market info.
    """
    market_req = data_node_protos.trading_data.MarketsRequest()
    return data_client.Markets(market_req).markets


def market_info(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> vega_protos.markets.Market:
    """
    Output market info.
    """
    market_req = data_node_protos.trading_data.MarketByIDRequest(market_id=market_id)
    return data_client.MarketByID(market_req).market


def asset_info(
    asset_id: str,
    data_client: vac.VegaTradingDataClient,
) -> vac.vega.assets.Asset:
    """Returns information on a given asset selected by its ID

    Args:
        asset_id:
            str, The ID of the asset requested
        data_client:
            VegaTradingDataClient, an instantiated gRPC data client

    Returns:
        vega.assets.Asset, Object containing data about the requested asset
    """
    return data_client.AssetByID(
        data_node_protos.trading_data.AssetByIDRequest(id=asset_id)
    ).asset


def all_market_accounts(
    asset_id: str,
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> Dict[vega_protos.vega.AccountType, MarketAccount]:
    """
    Output liquidity fee account/ insurance pool in the market
    """
    accounts = data_client.MarketAccounts(
        data_node_protos.trading_data.MarketAccountsRequest(
            asset=asset_id, market_id=market_id
        )
    ).accounts

    return {account.type: account for account in accounts}


def market_accounts(
    asset_id: str,
    market_id: str,
    data_client: vac.VegaTradingDataClient,
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


def market_data(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> vega_protos.vega.MarketData:
    """
    Output market info.
    """
    market_req = data_node_protos.trading_data.MarketDataByIDRequest(
        market_id=market_id
    )
    return data_client.MarketDataByID(market_req).market_data


def infrastructure_fee_accounts(
    asset_id: str,
    data_client: vac.VegaTradingDataClient,
) -> List[vega_protos.vega.Account]:
    """
    Output infrastructure fee accounts
    """
    return data_client.FeeInfrastructureAccounts(
        data_node_protos.trading_data.FeeInfrastructureAccountsRequest(asset=asset_id)
    ).accounts


def order_status(
    order_id: str, data_client: vac.VegaTradingDataClient, version: int = 0
) -> Optional[vega_protos.vega.Order]:
    """Loads information about a specific order identified by the ID.
    Optionally return historic order versions.

    Args:
        order_id:
            str, the order identifier as specified by Vega when originally placed
        data_client:
            VegaTradingDataClient, an instantiated gRPC trading data client
        version:
            int, Optional, Version of the order:
                - Set `version` to 0 for most recent version of the order
                - Set `1` for original version of the order
                - Set `2` for first amendment, `3` for second amendment, etc
    Returns:
        Optional[vega.Order], the requested Order object or None if nothing found
    """
    return data_client.OrderByID(
        data_node_protos.trading_data.OrderByIDRequest(
            order_id=order_id, version=version
        )
    ).order


def order_status_by_reference(
    reference: str, data_client: vac.VegaTradingDataClient
) -> Optional[vega_protos.vega.Order]:
    """Loads information about a specific order identified by the reference.
    Optionally return historic order versions.

    Args:
        reference:
            str, the order reference as specified by Vega when originally placed
                or assigned by Vega
        data_client:
            VegaTradingDataClient, an instantiated gRPC trading data client
    Returns:
        Optional[vega.Order], the requested Order object or None if nothing found
    """
    return data_client.OrderByReference(
        data_node_protos.trading_data.OrderByReferenceRequest(reference=reference)
    ).order


def market_depth(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
    max_depth: Optional[int] = None,
) -> Optional[vega_protos.vega.MarketDepth]:
    return data_client.MarketDepth(
        data_node_protos.trading_data.MarketDepthRequest(
            market_id=market_id, max_depth=max_depth
        )
    )


def liquidity_provisions(
    data_client: vac.VegaTradingDataClient,
    market_id: Optional[str] = None,
    party_id: Optional[str] = None,
) -> Optional[List[vega_protos.vega.LiquidityProvision]]:
    """Loads the current liquidity provision(s) for a given market and/or party.

    Args:
        data_client:
            VegaTradingDataClient, an instantiated gRPC trading data client
        market_id:
            Optional[str], the ID of the market from which to pull liquidity provisions
        party_id:
            Optional[str], the ID of the party from which to pull liquidity provisions

    Returns:
        List[LiquidityProvision], list of liquidity provisions (if any exist)
    """
    return data_client.LiquidityProvisions(
        data_node_protos.trading_data.LiquidityProvisionsRequest(
            market=market_id,
            party=party_id,
        )
    ).liquidity_provisions


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
