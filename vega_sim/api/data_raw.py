from __future__ import annotations

import datetime
import logging
from collections import namedtuple
from functools import wraps
from typing import Callable, Iterable, List, Optional, TypeVar, Union, Tuple

import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v2 as data_node_protos_v2
import vega_sim.proto.vega as vega_protos
import vega_sim.proto.vega.events.v1.events_pb2 as events_protos

logger = logging.getLogger(__name__)

MarketAccount = namedtuple("MarketAccount", ["insurance", "liquidity_fee"])

T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")


def _retry(num_retry_attempts: int = 3):
    """Automatically retries a function a certain number
    of times. Swallows any errors raised by earlier attempts
    and will raise the last one if still failing.
    """

    def retry_decorator(fn):
        @wraps(fn)
        def auto_retry_fn(*args, **kwargs):
            for i in range(num_retry_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if (i + 1) == num_retry_attempts:
                        raise e

        return auto_retry_fn

    return retry_decorator


def unroll_v2_pagination(
    base_request: S,
    request_func: Callable[[S], T],
    extraction_func: Callable[[S], List[U]],
) -> List[T]:
    base_request.pagination.CopyFrom(
        data_node_protos_v2.trading_data.Pagination(first=1000)
    )

    response = request_func(base_request)
    full_list = extraction_func(response)
    while response.page_info.has_next_page:
        base_request.pagination.after = response.page_info.end_cursor
        response = request_func(base_request)
        curr_list = extraction_func(response)
        full_list.extend(curr_list)
    return full_list


@_retry(3)
def positions_by_market(
    pub_key: str,
    data_client: vac.VegaTradingDataClientV2,
    market_id: Optional[str] = None,
) -> List[vega_protos.vega.Position]:
    """Output positions of a party."""

    base_request = data_node_protos_v2.trading_data.ListPositionsRequest(
        party_id=pub_key,
    )
    if market_id is not None:
        setattr(base_request, "market_id", market_id)

    return unroll_v2_pagination(
        base_request=base_request,
        request_func=lambda x: data_client.ListPositions(x).positions,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
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


@_retry(3)
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


@_retry(3)
def list_assets(data_client: vac.VegaTradingDataClientV2):
    return unroll_v2_pagination(
        base_request=data_node_protos_v2.trading_data.ListAssetsRequest(),
        request_func=lambda x: data_client.ListAssets(x).assets,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
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


@_retry(3)
def list_accounts(
    data_client: vac.VegaTradingDataClientV2,
    asset_id: Optional[str] = None,
    market_id: Optional[str] = None,
    party_id: Optional[str] = None,
) -> List[data_node_protos_v2.trading_data.AccountBalance]:
    """
    Output liquidity fee account/ insurance pool in the market
    """

    account_filter = data_node_protos_v2.trading_data.AccountFilter()
    if party_id is not None:
        account_filter.party_ids.extend([party_id])
    if asset_id is not None:
        account_filter.asset_id = asset_id
    if market_id is not None:
        account_filter.market_ids.extend([market_id])
    return unroll_v2_pagination(
        base_request=data_node_protos_v2.trading_data.ListAccountsRequest(
            filter=account_filter
        ),
        request_func=lambda x: data_client.ListAccounts(x).accounts,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
def market_accounts(
    asset_id: str,
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> MarketAccount:
    """
    Output liquidity fee account/ insurance pool in the market
    """
    accounts = list_accounts(
        asset_id=asset_id, market_id=market_id, data_client=data_client
    )
    account_type_map = {account.type: account for account in accounts}
    return MarketAccount(
        account_type_map[vega_protos.vega.ACCOUNT_TYPE_INSURANCE],
        account_type_map[vega_protos.vega.ACCOUNT_TYPE_FEES_LIQUIDITY],
    )


@_retry(3)
def get_latest_market_data(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> vega_protos.vega.MarketData:
    """
    Output market info.
    """
    return data_client.GetLatestMarketData(
        data_node_protos_v2.trading_data.GetLatestMarketDataRequest(market_id=market_id)
    ).market_data


@_retry(3)
def market_data_history(
    market_id: str,
    start: datetime.datetime,
    end: datetime.datetime,
    data_client: vac.VegaTradingDataClientV2,
) -> List[vega_protos.vega.MarketData]:
    """
    Output market data history.
    """

    return unroll_v2_pagination(
        base_request=data_node_protos_v2.trading_data.GetMarketDataHistoryByIDRequest(
            market_id=market_id,
            start_timestamp=int(start.timestamp() * 1e9),
            end_timestamp=int(end.timestamp() * 1e9),
        ),
        request_func=lambda x: data_client.GetMarketDataHistoryByID(x).market_data,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
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
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
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

    order_filter = data_node_protos_v2.trading_data.OrderFilter(live_only=live_only)

    if reference is not None:
        order_filter.reference = reference

    for attr, val in [
        ("market_ids", [market_id] if market_id is not None else None),
        ("party_ids", [party_id] if party_id is not None else None),
    ]:
        if val is not None:
            getattr(order_filter, attr).extend(val)

    request = data_node_protos_v2.trading_data.ListOrdersRequest(filter=order_filter)

    return unroll_v2_pagination(
        base_request=request,
        request_func=lambda x: data_client.ListOrders(x).orders,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
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


@_retry(3)
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


@_retry(3)
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
            market_id=market_id, party_id=party_id, live=True
        ),
        request_func=lambda x: data_client.ListLiquidityProvisions(
            x
        ).liquidity_provisions,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


def observe_event_bus(
    data_client: vac.VegaCoreClient,
    type: Optional[list],
    market_id: Optional[str] = None,
    party_id: Optional[str] = None,
) -> Iterable[vega_protos.api.v1.core.ObserveEventBusResponse]:
    """Subscribe to a stream of event updates from the data-node.
    The stream of events returned from this function is an iterable which
    does not end and will continue to tick another order update whenever
    one is received.

    Args:
        type:
            Optional[list], If provided only return events of these types
        market_id:
            Optional[str], If provided, only update events from this market
        party_id:
            Optional[str], If provided, only update events from this party
    Returns:
        Iterable[vega_protos.api.v1.core.ObserveEventBusResponse]:
            Infinite iterable of lists of events updates
    """

    request = vega_protos.api.v1.core.ObserveEventBusRequest(type=type)
    if market_id is not None:
        setattr(request, "market_id", market_id)
    if party_id is not None:
        setattr(request, "party_id", party_id)

    return data_client.ObserveEventBus(iter([request]))


@_retry(3)
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


@_retry(3)
def get_trades(
    data_client: vac.VegaTradingDataClientV2,
    market_id: str,
    party_id: Optional[str] = None,
    order_id: Optional[str] = None,
    start: Optional[datetime.datetime] = None,
    end: Optional[datetime.datetime] = None,
) -> List[vega_protos.vega.Trade]:
    return unroll_v2_pagination(
        data_node_protos_v2.trading_data.ListTradesRequest(
            market_ids=[market_id],
            party_ids=[party_id] if party_id is not None else None,
            order_ids=[order_id] if order_id is not None else None,
            date_range=data_node_protos_v2.trading_data.DateRange(
                start_timestamp=int(start.timestamp() * 1e9)
                if start is not None
                else None,
                end_timestamp=int(end.timestamp() * 1e9) if end is not None else None,
            ),
        ),
        request_func=lambda x: data_client.ListTrades(x).trades,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
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


@_retry(3)
def list_transfers(
    data_client: vac.VegaTradingDataClientV2,
    party_id: Optional[str] = None,
    direction: Optional[data_node_protos_v2.trading_data.TransferDirection] = None,
) -> List[events_protos.Transfer]:
    """Returns a list of raw transfers.

    Args:
        data_client (vac.VegaTradingDataClientV2):
            An instantiated gRPC trading data client
        party_id (Optional[str], optional):
            Public key for the specified party. Defaults to None.
        direction (Optional[data_node_protos_v2.trading_data.TransferDirection], optional):
            Direction of transfers to return. Defaults to None.

    Returns:
        List[events_protos.Transfer]:
            A list of Vega Transfer proto objects.
    """

    base_request = data_node_protos_v2.trading_data.ListTransfersRequest(
        pubkey=party_id, direction=direction
    )

    if party_id is not None:
        setattr(base_request, "pubkey", party_id)
    if direction is not None:
        setattr(base_request, "direction", direction)
    else:
        setattr(
            base_request,
            "direction",
            data_node_protos_v2.trading_data.TRANSFER_DIRECTION_TRANSFER_TO_OR_FROM,
        )

    return unroll_v2_pagination(
        base_request=base_request,
        request_func=lambda x: data_client.ListTransfers(x).transfers,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
def list_ledger_entries(
    data_client: vac.VegaTradingDataClientV2,
    close_on_account_filters: bool = False,
    asset_id: Optional[str] = None,
    from_party_ids: Optional[List[str]] = None,
    from_market_ids: Optional[List[str]] = None,
    from_account_types: Optional[List[vega_protos.vega.AccountType]] = None,
    to_party_ids: Optional[List[str]] = None,
    to_market_ids: Optional[List[str]] = None,
    to_account_types: Optional[List[vega_protos.vega.AccountType]] = None,
    transfer_types: Optional[List[vega_protos.vega.TransferType]] = None,
    from_datetime: Optional[datetime.datetime] = None,
    to_datetime: Optional[datetime.datetime] = None,
) -> List[data_node_protos_v2.trading_data.AggregatedLedgerEntry]:
    """Returns a list of ledger entries matching specific filters as provided.
    These detail every transfer of funds between accounts within the Vega system,
    including fee/rewards payments and transfers between user margin/general/bond
    accounts.

    Note: At least one of the from_*/to_* filters, or asset ID, must be specified.

    Args:
        data_client:
            vac.VegaTradingDataClientV2, An instantiated gRPC trading data client
        close_on_account_filters:
            bool, default False, Whether both 'from' and 'to' filters must both match
                a given transfer for inclusion. If False, entries matching either
                'from' or 'to' will also be included.
        asset_id:
            Optional[str], filter to only transfers of specific asset ID
        from_party_ids:
            Optional[List[str]], Only include transfers from specified parties
        from_market_ids:
            Optional[List[str]], Only include transfers from specified markets
        from_account_types:
            Optional[List[str]], Only include transfers from specified account types
        to_party_ids:
            Optional[List[str]], Only include transfers to specified parties
        to_market_ids:
            Optional[List[str]], Only include transfers to specified markets
        to_account_types:
            Optional[List[str]], Only include transfers to specified account types
        transfer_types:
            Optional[List[vega_protos.vega.AccountType]], Only include transfers
                of specified types
        from_datetime:
            Optional[datetime.datetime], Only include transfers occurring after
                this time
        to_datetime:
            Optional[datetime.datetime], Only include transfers occurring before
                this time
    Returns:
        List[data_node_protos_v2.trading_data.AggregatedLedgerEntry]
            A list of all transfers matching the requested criteria
    """
    if all(
        not x
        for x in [
            from_party_ids,
            to_party_ids,
            from_account_types,
            to_account_types,
            asset_id,
        ]
    ):
        raise Exception("Must specify at least one filter criterion")

    base_request = data_node_protos_v2.trading_data.ListLedgerEntriesRequest(
        filter=data_node_protos_v2.trading_data.LedgerEntryFilter(
            close_on_account_filters=close_on_account_filters,
            from_account_filter=data_node_protos_v2.trading_data.AccountFilter(
                asset_id=asset_id,
                party_ids=from_party_ids if from_party_ids is not None else [],
                market_ids=from_market_ids if from_market_ids is not None else [],
                account_types=(
                    from_account_types if from_account_types is not None else []
                ),
            ),
            to_account_filter=data_node_protos_v2.trading_data.AccountFilter(
                asset_id=asset_id,
                party_ids=to_party_ids if to_party_ids is not None else [],
                market_ids=to_market_ids if to_market_ids is not None else [],
                account_types=to_account_types if to_account_types is not None else [],
            ),
            transfer_types=transfer_types,
        ),
    )
    if from_datetime is not None or to_datetime is not None:
        base_request.date_range.CopyFrom(
            data_node_protos_v2.trading_data.DateRange(
                start_timestamp=(
                    from_datetime.timestamp() * 1e9
                    if from_datetime is not None
                    else None
                ),
                end_timestamp=(
                    to_datetime.timestamp() * 1e9 if to_datetime is not None else None
                ),
            )
        )

    return unroll_v2_pagination(
        base_request=base_request,
        request_func=lambda x: data_client.ListLedgerEntries(x).ledger_entries,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


def market_data_subscription(
    data_client: vac.VegaCoreClient,
    market_id: Optional[str] = None,
) -> Iterable[vega_protos.vega.MarketData]:
    data_stream = observe_event_bus(
        data_client=data_client,
        type=[events_protos.BUS_EVENT_TYPE_MARKET_DATA],
        market_id=market_id,
    )

    def _data_gen(
        data_stream: Iterable[vega_protos.api.v1.core.ObserveEventBusResponse],
    ) -> Iterable[vega_protos.vega.MarketData]:
        try:
            for market_data in data_stream:
                for market_data_event in market_data.events:
                    yield market_data_event.market_data
        except Exception:
            logger.info("Order subscription closed")
            return

    return _data_gen(data_stream=data_stream)


@_retry(3)
def get_risk_factors(
    data_client: vac.VegaTradingDataClientV2,
    market_id: str,
):
    return data_client.GetRiskFactors(
        data_node_protos_v2.trading_data.GetRiskFactorsRequest(market_id=market_id)
    )


@_retry(3)
def estimate_position(
    data_client: vac.VegaTradingDataClientV2,
    market_id: str,
    open_volume: int,
    orders: Optional[List[data_node_protos_v2.trading_data.OrderInfo]] = None,
    collateral_available: Optional[str] = None,
) -> Tuple[
    data_node_protos_v2.trading_data.MarginEstimate,
    data_node_protos_v2.trading_data.LiquidationEstimate,
]:
    base_request = data_node_protos_v2.trading_data.EstimatePositionRequest(
        market_id=market_id,
        open_volume=open_volume,
    )

    if orders is not None:
        [base_request.orders.append(order) for order in orders]
    if collateral_available is not None:
        setattr(base_request, "collateral_available", collateral_available)

    response = data_client.EstimatePosition(base_request)

    return response.margin, response.liquidation


@_retry(3)
def get_stake(data_client: vac.trading_data_grpc_v2, party_id: str = None):
    base_request = data_node_protos_v2.trading_data.GetStakeRequest(party_id=party_id)
    return data_client.GetStake(base_request).current_stake_available


@_retry(3)
def list_all_network_history_segments(data_client: vac.trading_data_grpc_v2):
    base_request = (
        data_node_protos_v2.trading_data.ListAllNetworkHistorySegmentsRequest()
    )
    return data_client.ListAllNetworkHistorySegments(base_request).segments


@_retry(3)
def list_referral_sets(
    data_client: vac.trading_data_grpc_v2,
    referral_set_id: Optional[str] = None,
    referrer: Optional[str] = None,
    referee: Optional[str] = None,
) -> List[data_node_protos_v2.trading_data.ReferralSet]:
    base_request = data_node_protos_v2.trading_data.ListReferralSetsRequest()
    if referral_set_id is not None:
        setattr(base_request, "referral_set_id", referral_set_id)
    if referrer is not None:
        setattr(base_request, "referrer", referrer)
    if referee is not None:
        setattr(base_request, "referee", referee)
    return unroll_v2_pagination(
        base_request=base_request,
        request_func=lambda x: data_client.ListReferralSets(x).referral_sets,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
def list_referral_set_referees(
    data_client: vac.trading_data_grpc_v2,
    referral_set_id: Optional[str] = None,
    referrer: Optional[str] = None,
    referee: Optional[str] = None,
) -> List[data_node_protos_v2.trading_data.ReferralSet]:
    base_request = data_node_protos_v2.trading_data.ListReferralSetRefereesRequest()
    if referral_set_id is not None:
        setattr(base_request, "referral_set_id", referral_set_id)
    if referrer is not None:
        setattr(base_request, "referrer", referrer)
    if referee is not None:
        setattr(base_request, "referee", referee)
    return unroll_v2_pagination(
        base_request=base_request,
        request_func=lambda x: data_client.ListReferralSetReferees(
            x
        ).referral_set_referees,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
def get_current_referral_program(data_client: vac.trading_data_grpc_v2):
    return data_client.GetCurrentReferralProgram(
        data_node_protos_v2.trading_data.GetCurrentReferralProgramRequest()
    ).current_referral_program


@_retry(3)
def get_referral_set_stats(
    data_client: vac.trading_data_grpc_v2,
    at_epoch: Optional[int] = None,
    referee: Optional[str] = None,
):
    base_request = data_node_protos_v2.trading_data.GetReferralSetStatsRequest()
    if at_epoch is not None:
        setattr(base_request, "at_epoch", at_epoch)
    if referee is not None:
        setattr(base_request, "referee", referee)
    return unroll_v2_pagination(
        base_request=base_request,
        request_func=lambda x: data_client.GetReferralSetStats(x).stats,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
def get_referral_fee_stats(
    data_client: vac.trading_data_grpc_v2,
    market_id: Optional[str] = None,
    asset_id: Optional[str] = None,
    epoch_seq: Optional[int] = None,
):
    base_request = data_node_protos_v2.trading_data.GetReferralFeeStatsRequest()
    if market_id is None and asset_id is None:
        raise ValueError("Neither 'market_id' or 'asset_id' set.")
    if market_id is not None:
        setattr(base_request, "market_id", market_id)
    if asset_id is not None:
        setattr(base_request, "asset_id", asset_id)
    if epoch_seq is not None:
        setattr(base_request, "epoch_seq", epoch_seq)
    return data_client.GetReferralFeeStats(base_request).fee_stats


@_retry(3)
def get_current_volume_discount_program(
    data_client: vac.trading_data_grpc_v2.TradingDataServiceStub,
):
    return data_client.GetCurrentVolumeDiscountProgram(
        data_node_protos_v2.trading_data.GetCurrentVolumeDiscountProgramRequest()
    ).current_volume_discount_program


@_retry(3)
def get_volume_discount_stats(
    data_client: vac.trading_data_grpc_v2,
    at_epoch: Optional[int] = None,
    party_id: Optional[str] = None,
) -> List[data_node_protos_v2.trading_data.ReferralSet]:
    base_request = data_node_protos_v2.trading_data.GetVolumeDiscountStatsRequest()
    if at_epoch is not None:
        setattr(base_request, "at_epoch", at_epoch)
    if party_id is not None:
        setattr(base_request, "party_id", party_id)
    return unroll_v2_pagination(
        base_request=base_request,
        request_func=lambda x: data_client.GetVolumeDiscountStats(x).stats,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
def list_teams(
    data_client: vac.trading_data_grpc_v2,
    team_id: Optional[str] = None,
    party_id: Optional[str] = None,
):
    base_request = data_node_protos_v2.trading_data.ListTeamsRequest()
    if team_id is not None:
        setattr(base_request, "team_id", team_id)
    if party_id is not None:
        setattr(base_request, "party_id", party_id)
    return unroll_v2_pagination(
        base_request=base_request,
        request_func=lambda x: data_client.ListTeams(x).teams,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
def list_team_referees(
    data_client: vac.trading_data_grpc_v2,
    team_id: Optional[str] = None,
):
    base_request = data_node_protos_v2.trading_data.ListTeamRefereesRequest()
    if team_id is not None:
        setattr(base_request, "team_id", team_id)
    return unroll_v2_pagination(
        base_request=base_request,
        request_func=lambda x: data_client.ListTeamReferees(x).team_referees,
        extraction_func=lambda res: [i.node for i in res.edges],
    )


@_retry(3)
def list_team_referee_history(
    data_client: vac.trading_data_grpc_v2,
    referee: Optional[str] = None,
):
    base_request = data_node_protos_v2.trading_data.ListTeamRefereeHistoryRequest()
    if referee is not None:
        setattr(base_request, "referee", referee)
    return unroll_v2_pagination(
        base_request=base_request,
        request_func=lambda x: data_client.ListTeamRefereeHistory(
            x
        ).team_referee_history,
        extraction_func=lambda res: [i.node for i in res.edges],
    )
