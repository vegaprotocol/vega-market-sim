from dataclasses import dataclass
import numpy as np
from collections import namedtuple
from typing import Callable, List, Optional, Tuple, TypeVar


import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v1 as data_node_protos
import vega_sim.proto.vega as vega_protos
import vega_sim.api.data_raw as data_raw
from vega_sim.api.helpers import num_from_padded_int


class MissingAssetError(Exception):
    pass


T = TypeVar("T")
S = TypeVar("S")

AccountData = namedtuple("AccountData", ["general", "margin", "bond"])
OrderBook = namedtuple("OrderBook", ["bids", "asks"])
Order = namedtuple(
    "Order",
    [
        "price",
        "size",
        "id",
        "reference",
        "side",
        "status",
        "remaining",
        "time_in_force",
        "order_type",
        "created_at",
        "expires_at",
        "party_id",
        "updated_at",
        "version",
    ],
)


@dataclass
class OrdersBySide:
    bids: List[Order]
    asks: List[Order]


def _unroll_pagination(
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


def _order_from_proto(
    order: vega_protos.vega.Order, price_decimals: int, position_decimals: int
) -> Order:
    return Order(
        id=order.id,
        price=num_from_padded_int(order.price, price_decimals),
        size=num_from_padded_int(order.size, position_decimals),
        reference=order.reference,
        side=order.side,
        status=order.status,
        remaining=num_from_padded_int(order.remaining, position_decimals),
        time_in_force=order.time_in_force,
        order_type=order.type,
        created_at=order.created_at,
        expires_at=order.expires_at,
        party_id=order.party_id,
        updated_at=order.updated_at,
        version=order.version,
    )


def party_account(
    pub_key: str,
    asset_id: str,
    market_id: str,
    data_client: vac.VegaTradingDataClient,
    asset_dp: Optional[int] = None,
) -> AccountData:
    """Output money in general accounts/margin accounts/bond accounts (if exists)
    of a party."""
    account_req = data_node_protos.trading_data.PartyAccountsRequest(
        party_id=pub_key,
        asset=asset_id,
    )
    accounts = data_client.PartyAccounts(account_req).accounts

    asset_dp = (
        asset_dp if asset_dp is not None else asset_decimals(asset_id, data_client)
    )

    general, margin, bond = np.nan, np.nan, np.nan
    for account in accounts:
        if account.market_id and account.market_id != market_id:
            # The 'general' account type has no market ID, so we have to pull
            # all markets then filter down here
            continue
        if account.type == vega_protos.vega.ACCOUNT_TYPE_GENERAL:
            general = num_from_padded_int(float(account.balance), asset_dp)
        if account.type == vega_protos.vega.ACCOUNT_TYPE_MARGIN:
            margin = num_from_padded_int(float(account.balance), asset_dp)
        if account.type == vega_protos.vega.ACCOUNT_TYPE_BOND:
            bond = num_from_padded_int(float(account.balance), asset_dp)

    return AccountData(general, margin, bond)


def find_asset_id(
    symbol: str, data_client: vac.VegaTradingDataClient, raise_on_missing: bool = False
) -> str:
    """Looks up the Asset ID of a given asset name

    Args:
        symbol:
            str, The symbol of the asset to look up
        data_client:
            VegaTradingDataClient, the gRPC data client
        raise_on_missing:
            bool, whether to raise an Error or silently return
                if the asset does not exist

    Returns:
        str, the ID of the asset
    """
    asset_request = data_node_protos.trading_data.AssetsRequest()
    assets = data_client.Assets(asset_request).assets
    # Find settlement asset
    for asset in assets:
        if asset.details.symbol == symbol:
            return asset.id
    if raise_on_missing:
        raise MissingAssetError(
            f"{symbol} asset not found on specified Vega network, "
            + "please propose and create this asset first"
        )


def market_price_decimals(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> int:
    """Returns the number of decimal places a specified market uses for price units.

    Args:
        market_id:
            str, The ID of the market requested
        data_client:
            VegaTradingDataClient, an instantiated gRPC data client

    Returns:
        int, The number of decimal places the market uses
    """
    return data_raw.market_info(
        market_id=market_id, data_client=data_client
    ).decimal_places


def market_position_decimals(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> int:
    """Returns the number of decimal places a specified market uses for position units.

    Args:
        market_id:
            str, The ID of the market requested
        data_client:
            VegaTradingDataClient, an instantiated gRPC data client

    Returns:
        int, The number of decimal places the market uses for positions
    """
    return data_raw.market_info(
        market_id=market_id, data_client=data_client
    ).position_decimal_places


def asset_decimals(
    asset_id: str,
    data_client: vac.VegaTradingDataClient,
) -> int:
    """Returns the number of decimal places a specified asset uses for price.

    Args:
        asset_id:
            str, The ID of the asset requested
        data_client:
            VegaTradingDataClient, an instantiated gRPC data client

    Returns:
        int, The number of decimal places the asset uses
    """
    return data_raw.asset_info(
        asset_id=asset_id, data_client=data_client
    ).details.decimals


def best_prices(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
    price_decimals: Optional[int] = None,
) -> Tuple[float, float]:
    """
    Output the best static bid price and best static ask price in current market.
    """
    mkt_data = data_raw.market_data(market_id=market_id, data_client=data_client)
    mkt_price_dp = (
        price_decimals
        if price_decimals is not None
        else market_price_decimals(market_id=market_id, data_client=data_client)
    )

    return num_from_padded_int(
        mkt_data.best_static_bid_price, mkt_price_dp
    ), num_from_padded_int(mkt_data.best_static_ask_price, mkt_price_dp)


def open_orders_by_market(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
    price_decimals: Optional[int] = None,
    position_decimals: Optional[int] = None,
) -> OrdersBySide:
    """
    Output all active limit orders in current market.

    Args:
        market_id:
            str, ID for the market to load
        data_client:
            VegaTradingDataClient, instantiated gRPC client

    Returns:
        OrdersBySide, Live orders segregated by side
    """
    orders = _unroll_pagination(
        data_node_protos.trading_data.OrdersByMarketRequest(market_id=market_id),
        lambda x: data_client.OrdersByMarket(x).orders,
    )

    mkt_price_dp = (
        price_decimals
        if price_decimals is not None
        else market_price_decimals(market_id=market_id, data_client=data_client)
    )
    mkt_pos_dp = (
        position_decimals
        if position_decimals is not None
        else market_position_decimals(market_id=market_id, data_client=data_client)
    )

    bids = []
    asks = []
    for order in orders:
        if order.status != vega_protos.vega.Order.Status.STATUS_ACTIVE:
            continue
        converted_order = _order_from_proto(
            order, price_decimals=mkt_price_dp, position_decimals=mkt_pos_dp
        )
        bids.append(
            converted_order
        ) if converted_order.side == vega_protos.vega.SIDE_BUY else asks.append(
            converted_order
        )

    return OrdersBySide(bids, asks)


def order_book_by_market(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> OrderBook:
    """
    Output state of order book for a given market.
    """

    orders = _unroll_pagination(
        data_node_protos.trading_data.OrdersByMarketRequest(market_id=market_id),
        lambda x: data_client.OrdersByMarket(x).orders,
    )

    mkt_price_dp = market_price_decimals(market_id=market_id, data_client=data_client)
    mkt_pos_dp = market_position_decimals(market_id=market_id, data_client=data_client)

    bids = {}
    asks = {}

    for order in orders:
        if order.status == vega_protos.vega.Order.Status.STATUS_ACTIVE:
            if order.side == vega_protos.vega.Side.SIDE_BUY:
                price = num_from_padded_int(order.price, mkt_price_dp)
                volume = num_from_padded_int(order.remaining, mkt_pos_dp)
                bids[price] = bids.get(price, 0) + volume
            else:
                price = num_from_padded_int(order.price, mkt_price_dp)
                volume = num_from_padded_int(order.remaining, mkt_pos_dp)
                asks[price] = bids.get(price, 0) + volume

    return OrderBook(bids, asks)


def order_status_by_reference(
    reference: str,
    data_client: vac.VegaTradingDataClient,
    price_decimals: Optional[int] = None,
    position_decimals: Optional[int] = None,
) -> Optional[vega_protos.vega.Order]:
    """Loads information about a specific order identified by the reference.
    Optionally return historic order versions.

    Args:
        reference:
            str, the order reference as specified by Vega when originally placed
                or assigned by Vega
        data_client:
            VegaTradingDataClient, an instantiated gRPC trading data client
        price_decimals:
            int, the decimal precision used when specifying prices on the market
        position_decimals:
            int, the decimal precision used when specifying positions on the market

    Returns:
        Optional[vega.Order], the requested Order object or None if nothing found
    """
    return _order_from_proto(
        data_raw.order_status_by_reference(
            reference=reference, data_client=data_client
        ),
        price_decimals=price_decimals,
        position_decimals=position_decimals,
    )


def market_account(
    market_id: str,
    account_type: vega_protos.vega.AccountType,
    data_client: vac.VegaTradingDataClient,
) -> float:
    """
    Returns the current asset value in the Market's fee account

    Args:
        market_id:
            str, The ID of the market to check
        account_type:
            vega.AccountType, the account type to check for

    Returns:
        float, the current balance in the market's fee asset
    """
    accounts = data_raw.all_market_accounts(
        asset_id=None, market_id=market_id, data_client=data_client
    )
    acct = accounts[account_type]

    asset_dp = asset_decimals(asset_id=acct.asset, data_client=data_client)
    return num_from_padded_int(
        acct.balance,
        asset_dp,
    )
