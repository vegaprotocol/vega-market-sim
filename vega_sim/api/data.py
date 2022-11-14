import logging
from collections import namedtuple
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterable, List, Optional, Tuple, Any

import vega_sim.api.data_raw as data_raw
import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v2 as data_node_protos_v2
import vega_sim.proto.vega as vega_protos
from vega_sim.api.helpers import num_from_padded_int


class MissingAssetError(Exception):
    pass


class MissingMarketError(Exception):
    pass


logger = logging.Logger(__name__)


AccountData = namedtuple("AccountData", ["general", "margin", "bond"])
OrderBook = namedtuple("OrderBook", ["bids", "asks"])
PriceLevel = namedtuple("PriceLevel", ["price", "number_of_orders", "volume"])
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
        "market_id",
        "updated_at",
        "version",
    ],
)
Position = namedtuple(
    "Position",
    [
        "party_id",
        "market_id",
        "open_volume",
        "realised_pnl",
        "unrealised_pnl",
        "average_entry_price",
        "updated_at",
    ],
)

MarginLevels = namedtuple(
    "MarginLevels",
    [
        "maintenance_margin",
        "search_level",
        "initial_margin",
        "collateral_release_level",
        "party_id",
        "market_id",
        "asset",
        "timestamp",
    ],
)


@dataclass
class MarketDepth:
    buys: List[PriceLevel]
    sells: List[PriceLevel]


@dataclass
class OrdersBySide:
    bids: List[Order]
    asks: List[Order]


@dataclass
class Fee:
    maker_fee: float
    infrastructure_fee: float
    liquidity_fee: float


@dataclass
class Trade:
    id: str
    market_id: str
    price: float
    size: float
    buyer: str
    seller: str
    aggressor: vega_protos.vega.Side
    buy_order: str
    sell_order: str
    timestamp: int
    trade_type: vega_protos.vega.Trade.Type
    buyer_fee: Fee
    seller_fee: Fee
    buyer_auction_batch: int
    seller_auction_batch: int


def _trade_from_proto(
    trade: vega_protos.vega.Trade,
    price_decimals: int,
    position_decimals: int,
    asset_decimals: int,
) -> Trade:
    return Trade(
        id=trade.id,
        market_id=trade.market_id,
        price=num_from_padded_int(trade.price, price_decimals),
        size=num_from_padded_int(trade.size, position_decimals),
        buyer=trade.buyer,
        seller=trade.seller,
        aggressor=trade.aggressor,
        buy_order=trade.buy_order,
        sell_order=trade.sell_order,
        timestamp=trade.timestamp,
        trade_type=trade.type,
        buyer_fee=Fee(
            maker_fee=num_from_padded_int(trade.buyer_fee.maker_fee, asset_decimals),
            infrastructure_fee=num_from_padded_int(
                trade.buyer_fee.infrastructure_fee, asset_decimals
            ),
            liquidity_fee=num_from_padded_int(
                trade.buyer_fee.liquidity_fee, asset_decimals
            ),
        ),
        seller_fee=Fee(
            maker_fee=num_from_padded_int(trade.seller_fee.maker_fee, asset_decimals),
            infrastructure_fee=num_from_padded_int(
                trade.seller_fee.infrastructure_fee, asset_decimals
            ),
            liquidity_fee=num_from_padded_int(
                trade.seller_fee.liquidity_fee, asset_decimals
            ),
        ),
        buyer_auction_batch=trade.buyer_auction_batch,
        seller_auction_batch=trade.seller_auction_batch,
    )


def _margin_level_from_proto(
    margin_level: vega_protos.vega.MarginLevels, asset_decimals: int
) -> MarginLevels:
    return MarginLevels(
        maintenance_margin=num_from_padded_int(
            margin_level.maintenance_margin, asset_decimals
        ),
        search_level=num_from_padded_int(margin_level.search_level, asset_decimals),
        initial_margin=num_from_padded_int(margin_level.initial_margin, asset_decimals),
        collateral_release_level=num_from_padded_int(
            margin_level.collateral_release_level, asset_decimals
        ),
        party_id=margin_level.party_id,
        market_id=margin_level.market_id,
        asset=margin_level.asset,
        timestamp=margin_level.timestamp,
    )


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
        market_id=order.market_id,
    )


def _position_from_proto(
    position: vega_protos.vega.Position,
    position_decimals: int,
    asset_decimals: int,
    price_decimals: int,
) -> Position:
    return Position(
        party_id=position.party_id,
        market_id=position.market_id,
        open_volume=num_from_padded_int(position.open_volume, position_decimals),
        realised_pnl=num_from_padded_int(position.realised_pnl, asset_decimals),
        unrealised_pnl=num_from_padded_int(position.unrealised_pnl, asset_decimals),
        average_entry_price=num_from_padded_int(
            position.average_entry_price, price_decimals
        ),
        updated_at=position.updated_at,
    )


def positions_by_market(
    pub_key: str,
    market_id: str,
    position_decimals: int,
    asset_decimals: int,
    price_decimals: int,
    data_client: vac.VegaTradingDataClientV2,
) -> List[Position]:
    """Output positions of a party."""
    return [
        _position_from_proto(
            pos,
            position_decimals=position_decimals,
            asset_decimals=asset_decimals,
            price_decimals=price_decimals,
        )
        for pos in data_raw.positions_by_market(
            pub_key=pub_key, market_id=market_id, data_client=data_client
        )
    ]


def party_account(
    pub_key: str,
    asset_id: str,
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
    asset_dp: Optional[int] = None,
) -> AccountData:
    """Output money in general accounts/margin accounts/bond accounts (if exists)
    of a party."""
    accounts = data_raw.party_accounts(
        data_client=data_client,
        party_id=pub_key,
        asset_id=asset_id,
    )

    asset_dp = (
        asset_dp if asset_dp is not None else asset_decimals(asset_id, data_client)
    )

    general, margin, bond = 0, 0, 0  # np.nan, np.nan, np.nan
    for account in accounts:
        if (
            account.market_id
            and account.market_id != "!"
            and account.market_id != market_id
        ):
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


def find_market_id(
    name: str, data_client: vac.VegaTradingDataClientV2, raise_on_missing: bool = False
) -> str:
    """Looks up the Market ID of a given market name

    Args:
        symbol:
            str, The symbol of the asset to look up
        data_client:
            VegaTradingDataClientV2, the gRPC data client
        raise_on_missing:
            bool, whether to raise an Error or silently return
                if the asset does not exist

    Returns:
        str, the ID of the asset
    """
    markets = data_raw.all_markets(data_client=data_client)

    acceptable_states = [
        vega_protos.markets.Market.STATE_PENDING,
        vega_protos.markets.Market.STATE_ACTIVE,
        vega_protos.markets.Market.STATE_SUSPENDED,
    ]

    market_ids = {}

    for market in markets:

        if market.tradable_instrument.instrument.name == name:
            if market.state in acceptable_states:
                market_ids[market.id] = market.market_timestamps.pending

    if len(market_ids) > 0:
        return max(market_ids, key=market_ids.get)

    if raise_on_missing:
        raise MissingMarketError(
            f"{name} market not found on specified Vega network, "
            + "please propose and create this market first"
        )


def find_asset_id(
    symbol: str,
    data_client: vac.VegaTradingDataClientV2,
    raise_on_missing: bool = False,
) -> str:
    """Looks up the Asset ID of a given asset name

    Args:
        symbol:
            str, The symbol of the asset to look up
        data_client:
            VegaTradingDataClientV2, the gRPC data client
        raise_on_missing:
            bool, whether to raise an Error or silently return
                if the asset does not exist

    Returns:
        str, the ID of the asset
    """
    assets = data_raw.list_assets(data_client=data_client)
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
    data_client: vac.VegaTradingDataClientV2,
) -> int:
    """Returns the number of decimal places a specified market uses for price units.

    Args:
        market_id:
            str, The ID of the market requested
        data_client:
            VegaTradingDataClientV2, an instantiated gRPC data client

    Returns:
        int, The number of decimal places the market uses
    """
    return data_raw.market_info(
        market_id=market_id, data_client=data_client
    ).decimal_places


def market_position_decimals(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> int:
    """Returns the number of decimal places a specified market uses for position units.

    Args:
        market_id:
            str, The ID of the market requested
        data_client:
            VegaTradingDataClientV2, an instantiated gRPC data client

    Returns:
        int, The number of decimal places the market uses for positions
    """
    return data_raw.market_info(
        market_id=market_id, data_client=data_client
    ).position_decimal_places


def asset_decimals(
    asset_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> int:
    """Returns the number of decimal places a specified asset uses for price.

    Args:
        asset_id:
            str, The ID of the asset requested
        data_client:
            VegaTradingDataClientV2, an instantiated gRPC data client

    Returns:
        int, The number of decimal places the asset uses
    """
    return data_raw.asset_info(
        asset_id=asset_id, data_client=data_client
    ).details.decimals


def best_prices(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
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

    return (
        num_from_padded_int(mkt_data.best_static_bid_price, mkt_price_dp),
        num_from_padded_int(mkt_data.best_static_offer_price, mkt_price_dp),
    )


def open_orders_by_market(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
    price_decimals: Optional[int] = None,
    position_decimals: Optional[int] = None,
) -> OrdersBySide:
    """
    Output all active limit orders in current market.

    Args:
        market_id:
            str, ID for the market to load
        data_client:
            VegaTradingDataClientV2, instantiated gRPC client

    Returns:
        OrdersBySide, Live orders segregated by side
    """
    bids = []
    asks = []
    orders = all_orders(
        market_id=market_id,
        data_client=data_client,
        price_decimals=price_decimals,
        position_decimals=position_decimals,
        open_only=True,
    )
    for order in orders:
        bids.append(order) if order.side == vega_protos.vega.SIDE_BUY else asks.append(
            order
        )

    return OrdersBySide(bids, asks)


def list_orders(
    data_client: vac.VegaTradingDataClientV2,
    market_id: Optional[str] = None,
    party_id: Optional[str] = None,
    reference: Optional[str] = None,
    price_decimals: Optional[int] = None,
    position_decimals: Optional[int] = None,
    live_only: Optional[bool] = True,
) -> List[Order]:
    """Return a list of converted orders for the specified market, party, and reference.

    Args:
        data_client (vac.VegaTradingDataClientV2):
            An instantiated gRPC trading_data_client_v2.
        market_id (str):
            Id of market to return orders for.
        party_id (str):
            Id of party to return orders for.
        reference (str):
            References to return orders for.
        price_decimals (Optional[int], optional):
            Market price decimal places. Defaults to None.
        position_decimals (Optional[int], optional):
            Market position decimal places. Defaults to None.
        live_only (Optional[bool], optional):
            Whether to only return live orders. Defaults to True.

    Returns:
        List[Order]:
            A list of converted orders.
    """
    orders = data_raw.list_orders(
        data_client=data_client,
        party_id=party_id,
        market_id=market_id,
        reference=reference,
        live_only=live_only,
    )

    mkt_price_dp = (
        DefaultDict(lambda: price_decimals) if price_decimals is not None else {}
    )
    mkt_pos_dp = (
        DefaultDict(lambda: position_decimals) if position_decimals is not None else {}
    )

    output_orders = []
    for order in orders:
        if price_decimals is None and order.market_id not in mkt_price_dp:
            mkt_pos_dp[order.market_id] = market_position_decimals(
                market_id=order.market_id, data_client=data_client
            )
            mkt_price_dp[order.market_id] = market_price_decimals(
                market_id=order.market_id, data_client=data_client
            )

        converted_order = _order_from_proto(
            order,
            price_decimals=mkt_price_dp[order.market_id],
            position_decimals=mkt_pos_dp[order.market_id],
        )
        output_orders.append(converted_order)
    return output_orders


def all_orders(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
    price_decimals: Optional[int] = None,
    position_decimals: Optional[int] = None,
    open_only: bool = False,
) -> OrdersBySide:
    """
    Output all active limit orders in current market.

    Args:
        market_id:
            str, ID for the market to load
        data_client:
            VegaTradingDataClientV2, instantiated gRPC client
        open_only:
            bool, default False, whether to only return still
                open orders

    Returns:
        OrdersBySide, Live orders segregated by side
    """
    orders = data_raw.list_orders(
        market_id=market_id,
        data_client=data_client,
    )

    mkt_price_dp = (
        DefaultDict(lambda: price_decimals) if price_decimals is not None else {}
    )
    mkt_pos_dp = (
        DefaultDict(lambda: position_decimals) if position_decimals is not None else {}
    )

    output_orders = []
    for order in orders:
        if price_decimals is None and order.market_id not in mkt_price_dp:
            mkt_pos_dp[order.market_id] = market_position_decimals(
                market_id=order.market_id, data_client=data_client
            )
            mkt_price_dp[order.market_id] = market_price_decimals(
                market_id=order.market_id, data_client=data_client
            )

        if open_only and order.status != vega_protos.vega.Order.Status.STATUS_ACTIVE:
            continue
        converted_order = _order_from_proto(
            order,
            price_decimals=mkt_price_dp[order.market_id],
            position_decimals=mkt_pos_dp[order.market_id],
        )
        output_orders.append(converted_order)
    return output_orders


def order_book_by_market(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> OrderBook:
    """
    Output state of order book for a given market.
    """

    orders = data_raw.list_orders(
        market_id=market_id,
        data_client=data_client,
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


def market_account(
    market_id: str,
    account_type: vega_protos.vega.AccountType,
    data_client: vac.VegaTradingDataClientV2,
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


def market_depth(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
    max_depth: Optional[int] = None,
    price_decimals: Optional[int] = None,
    position_decimals: Optional[int] = None,
) -> Optional[MarketDepth]:
    mkt_depth = data_raw.market_depth(
        data_client=data_client,
        market_id=market_id,
        max_depth=max_depth,
    )
    if mkt_depth is None:
        return mkt_depth

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

    def _price_level_from_raw(level) -> PriceLevel:
        return PriceLevel(
            price=num_from_padded_int(
                level.price,
                mkt_price_dp,
            ),
            number_of_orders=level.number_of_orders,
            volume=num_from_padded_int(
                level.volume,
                mkt_pos_dp,
            ),
        )

    return MarketDepth(
        buys=[_price_level_from_raw(level) for level in mkt_depth.buy],
        sells=[_price_level_from_raw(level) for level in mkt_depth.sell],
    )


def order_subscription(
    data_client: vac.VegaCoreClient,
    trading_data_client: vac.VegaTradingDataClientV2,
    market_id: Optional[str] = None,
    party_id: Optional[str] = None,
) -> Iterable[Order]:
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
        Iterable[Order], Infinite iterable of order updates
    """

    order_stream = data_raw.order_subscription(
        data_client=data_client, market_id=market_id, party_id=party_id
    )

    def _order_gen(
        order_stream: Iterable[vega_protos.api.v1.core.ObserveEventBusResponse],
    ) -> Iterable[Order]:
        mkt_pos_dp = {}
        mkt_price_dp = {}
        try:
            for order_list in order_stream:
                for bus_event in order_list.events:
                    order = bus_event.order
                    if order.market_id not in mkt_pos_dp:
                        mkt_pos_dp[order.market_id] = market_position_decimals(
                            market_id=order.market_id, data_client=trading_data_client
                        )
                        mkt_price_dp[order.market_id] = market_price_decimals(
                            market_id=order.market_id, data_client=trading_data_client
                        )
                    yield _order_from_proto(
                        order,
                        mkt_price_dp[order.market_id],
                        mkt_pos_dp[order.market_id],
                    )
        except Exception as _:
            logger.info("Order subscription closed")
            return

    return _order_gen(order_stream=order_stream)


def has_liquidity_provision(
    data_client: vac.VegaTradingDataClientV2,
    market_id: str,
    party_id: str,
) -> bool:
    lip = data_raw.liquidity_provisions(
        data_client=data_client, market_id=market_id, party_id=party_id
    )
    return (
        lip
        and len(lip) > 0
        and lip[0].status
        in [
            vega_protos.vega.LiquidityProvision.Status.STATUS_ACTIVE,
            vega_protos.vega.LiquidityProvision.Status.STATUS_UNDEPLOYED,
            vega_protos.vega.LiquidityProvision.Status.STATUS_PENDING,
        ]
    )


def margin_levels(
    data_client: vac.VegaTradingDataClientV2,
    party_id: str,
    market_id: Optional[str] = None,
) -> List[MarginLevels]:
    asset_dp = {}
    margins = data_raw.margin_levels(
        data_client=data_client, party_id=party_id, market_id=market_id
    )
    res_margins = []
    for margin in margins:
        if margin.asset not in asset_dp:
            asset_dp[margin.asset] = asset_decimals(
                asset_id=margin.asset, data_client=data_client
            )
        res_margins.append(
            _margin_level_from_proto(margin, asset_decimals=asset_dp[margin.asset])
        )
    return res_margins


def get_trades(
    data_client: vac.VegaTradingDataClientV2,
    market_id: str,
    party_id: Optional[str] = None,
    order_id: Optional[str] = None,
    market_price_decimals_map: Optional[Dict[str, int]] = None,
    market_position_decimals_map: Optional[Dict[str, int]] = None,
    market_asset_decimals_map: Optional[Dict[str, int]] = None,
) -> List[Trade]:
    base_trades = data_raw.get_trades(
        data_client=data_client,
        party_id=party_id,
        market_id=market_id,
        order_id=order_id,
    )
    market_price_decimals_map = market_price_decimals_map or {}
    market_position_decimals_map = market_position_decimals_map or {}
    market_asset_decimals_map = market_asset_decimals_map or {}

    res_trades = []
    for trade in base_trades:
        if trade.market_id not in market_price_decimals_map:
            market_price_decimals_map[trade.market_id] = market_price_decimals(
                market_id=trade.market_id, data_client=data_client
            )
        if trade.market_id not in market_position_decimals_map:
            market_position_decimals_map[trade.market_id] = market_position_decimals(
                market_id=trade.market_id, data_client=data_client
            )
        if trade.market_id not in market_asset_decimals_map:
            market_asset_decimals_map[trade.market_id] = asset_decimals(
                asset_id=data_raw.market_info(
                    market_id=market_id, data_client=data_client
                ).tradable_instrument.instrument.future.settlement_asset,
                data_client=data_client,
            )
        res_trades.append(
            _trade_from_proto(
                trade,
                price_decimals=market_price_decimals_map[trade.market_id],
                position_decimals=market_position_decimals_map[trade.market_id],
                asset_decimals=market_asset_decimals_map[trade.market_id],
            )
        )
    return res_trades
