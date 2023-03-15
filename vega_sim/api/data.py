import logging
from collections import namedtuple
from dataclasses import dataclass
from typing import (
    DefaultDict,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Callable,
    TypeVar,
    Union,
)
import datetime
import vega_sim.api.data_raw as data_raw
import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v2 as data_node_protos_v2
import vega_sim.proto.vega as vega_protos
import vega_sim.proto.vega.events.v1.events_pb2 as events_protos
from vega_sim.api.helpers import num_from_padded_int


class MissingAssetError(Exception):
    pass


class MissingMarketError(Exception):
    pass


logger = logging.Logger(__name__)

T = TypeVar("T")
S = TypeVar("S")

PartyMarketAccount = namedtuple("PartyMarketAccount", ["general", "margin", "bond"])
AccountData = namedtuple(
    "AccountData", ["owner", "balance", "asset", "market_id", "type"]
)
RiskFactor = namedtuple("RiskFactors", ["market_id", "short", "long"])
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
        "loss_socialisation_amount",
    ],
)
Transfer = namedtuple(
    "Transfer",
    [
        "id",
        "party_from",
        "from_account_type",
        "party_to",
        "to_account_type",
        "asset",
        "amount",
        "reference",
        "status",
        "timestamp",
        "reason",
        "one_off",
        "recurring",
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
class DecimalSpec:
    position_decimals: Optional[int] = None
    price_decimals: Optional[int] = None
    asset_decimals: Optional[int] = None


@dataclass
class LedgerEntry:
    from_account: vega_protos.vega.AccountDetails
    to_account: vega_protos.vega.AccountDetails
    amount: str
    transfer_type: vega_protos.vega.TransferType
    timestamp: int


@dataclass
class AggregatedLedgerEntry:
    timestamp: int
    quantity: float
    transfer_type: vega_protos.vega.TransferType
    asset_id: str
    from_account_type: vega_protos.vega.AccountType
    to_account_type: vega_protos.vega.AccountType
    from_account_party_id: str
    to_account_party_id: str
    from_account_market_id: str
    to_account_market_id: str


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


@dataclass(frozen=True)
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


def _ledger_entry_from_proto(
    ledger_entry,
    asset_decimals: int,
) -> LedgerEntry:
    return LedgerEntry(
        from_account=ledger_entry.from_account,
        to_account=ledger_entry.to_account,
        amount=num_from_padded_int(ledger_entry.amount, asset_decimals),
        transfer_type=ledger_entry.type,
        timestamp=ledger_entry.timestamp,
    )


def _aggregated_ledger_entry_from_proto(
    ledger_entry: data_node_protos_v2.trading_data.AggregatedLedgerEntry,
    decimal_spec: DecimalSpec,
) -> AggregatedLedgerEntry:
    return AggregatedLedgerEntry(
        timestamp=ledger_entry.timestamp,
        quantity=num_from_padded_int(
            ledger_entry.quantity, decimal_spec.asset_decimals
        ),
        transfer_type=ledger_entry.transfer_type,
        asset_id=ledger_entry.asset_id,
        from_account_type=ledger_entry.from_account_type,
        to_account_type=ledger_entry.to_account_type,
        from_account_party_id=ledger_entry.from_account_party_id,
        to_account_party_id=ledger_entry.to_account_party_id,
        from_account_market_id=ledger_entry.from_account_market_id,
        to_account_market_id=ledger_entry.to_account_market_id,
    )


def _trade_from_proto(
    trade: vega_protos.vega.Trade,
    decimal_spec: DecimalSpec,
) -> Trade:
    return Trade(
        id=trade.id,
        market_id=trade.market_id,
        price=num_from_padded_int(trade.price, decimal_spec.price_decimals),
        size=num_from_padded_int(trade.size, decimal_spec.position_decimals),
        buyer=trade.buyer,
        seller=trade.seller,
        aggressor=trade.aggressor,
        buy_order=trade.buy_order,
        sell_order=trade.sell_order,
        timestamp=trade.timestamp,
        trade_type=trade.type,
        buyer_fee=Fee(
            maker_fee=num_from_padded_int(
                trade.buyer_fee.maker_fee, decimal_spec.asset_decimals
            ),
            infrastructure_fee=num_from_padded_int(
                trade.buyer_fee.infrastructure_fee, decimal_spec.asset_decimals
            ),
            liquidity_fee=num_from_padded_int(
                trade.buyer_fee.liquidity_fee, decimal_spec.asset_decimals
            ),
        ),
        seller_fee=Fee(
            maker_fee=num_from_padded_int(
                trade.seller_fee.maker_fee, decimal_spec.asset_decimals
            ),
            infrastructure_fee=num_from_padded_int(
                trade.seller_fee.infrastructure_fee, decimal_spec.asset_decimals
            ),
            liquidity_fee=num_from_padded_int(
                trade.seller_fee.liquidity_fee, decimal_spec.asset_decimals
            ),
        ),
        buyer_auction_batch=trade.buyer_auction_batch,
        seller_auction_batch=trade.seller_auction_batch,
    )


def _margin_level_from_proto(
    margin_level: vega_protos.vega.MarginLevels, decimal_spec: DecimalSpec
) -> MarginLevels:
    return MarginLevels(
        maintenance_margin=num_from_padded_int(
            margin_level.maintenance_margin, decimal_spec.asset_decimals
        ),
        search_level=num_from_padded_int(
            margin_level.search_level, decimal_spec.asset_decimals
        ),
        initial_margin=num_from_padded_int(
            margin_level.initial_margin, decimal_spec.asset_decimals
        ),
        collateral_release_level=num_from_padded_int(
            margin_level.collateral_release_level, decimal_spec.asset_decimals
        ),
        party_id=margin_level.party_id,
        market_id=margin_level.market_id,
        asset=margin_level.asset,
        timestamp=margin_level.timestamp,
    )


def _order_from_proto(
    order: vega_protos.vega.Order,
    decimal_spec: DecimalSpec,
) -> Order:
    return Order(
        id=order.id,
        price=num_from_padded_int(order.price, decimal_spec.price_decimals),
        size=num_from_padded_int(order.size, decimal_spec.position_decimals),
        reference=order.reference,
        side=order.side,
        status=order.status,
        remaining=num_from_padded_int(order.remaining, decimal_spec.position_decimals),
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
    decimal_spec: DecimalSpec,
) -> Position:
    return Position(
        party_id=position.party_id,
        market_id=position.market_id,
        open_volume=num_from_padded_int(
            position.open_volume, decimal_spec.position_decimals
        ),
        realised_pnl=num_from_padded_int(
            position.realised_pnl, decimal_spec.asset_decimals
        ),
        unrealised_pnl=num_from_padded_int(
            position.unrealised_pnl, decimal_spec.asset_decimals
        ),
        average_entry_price=num_from_padded_int(
            position.average_entry_price, decimal_spec.price_decimals
        ),
        loss_socialisation_amount=num_from_padded_int(
            position.loss_socialisation_amount,
            decimal_spec.asset_decimals,
        ),
        updated_at=position.updated_at,
    )


def _transfer_from_proto(
    transfer: vega_protos.vega.Transfer, decimal_spec: DecimalSpec
) -> Transfer:
    return Transfer(
        id=transfer.id,
        party_from=getattr(transfer, "from"),
        from_account_type=transfer.from_account_type,
        party_to=transfer.to,
        to_account_type=transfer.to_account_type,
        asset=transfer.asset,
        amount=num_from_padded_int(transfer.amount, decimal_spec.asset_decimals),
        reference=transfer.reference,
        status=transfer.status,
        timestamp=transfer.timestamp,
        reason=transfer.reason,
        one_off=transfer.one_off,
        recurring=transfer.recurring,
    )


def positions_by_market(
    data_client: vac.VegaTradingDataClientV2,
    pub_key: str,
    market_id: Optional[str] = None,
    market_price_decimals_map: Optional[Dict[str, int]] = None,
    market_position_decimals_map: Optional[Dict[str, int]] = None,
    market_to_asset_map: Optional[Dict[str, str]] = None,
    asset_decimals_map: Optional[Dict[str, int]] = None,
) -> Union[Dict[str, Position], Position]:
    """Output positions of a party."""

    raw_positions = data_raw.positions_by_market(
        pub_key=pub_key, market_id=market_id, data_client=data_client
    )
    if len(raw_positions) == 0:
        logging.debug(
            f"No positions to return for pub_key={pub_key}, market_id={market_id}"
        )
        return None

    positions = {}
    for pos in raw_positions:
        market_info = None

        # Update maps if value does not exist for current market id
        if pos.market_id not in market_price_decimals_map:
            if market_info is None:
                market_info = data_raw.market_info(
                    market_id=pos.market_id, data_client=data_client
                )
            market_price_decimals_map[pos.market_id] = int(market_info.decimal_places)
        if pos.market_id not in market_position_decimals_map:
            if market_info is None:
                market_info = data_raw.market_info(
                    market_id=pos.market_id, data_client=data_client
                )
            market_position_decimals_map[pos.market_id] = int(
                market_info.position_decimal_places
            )
        if pos.market_id not in market_to_asset_map:
            if market_info is None:
                market_info = data_raw.market_info(
                    market_id=pos.market_id, data_client=data_client
                )
            market_to_asset_map[
                pos.market_id
            ] = market_info.tradable_instrument.instrument.future.settlement_asset

        # Update maps if value does not exist for current asset id
        if market_to_asset_map[pos.market_id] not in asset_decimals_map:
            asset_info = data_raw.asset_info(
                asset_id=market_to_asset_map[pos.market_id],
                data_client=data_client,
            )
            asset_decimals_map[pos.market_id] = int(asset_info.details.decimals)

        # Convert raw proto into a market-sim Position object
        positions[pos.market_id] = _position_from_proto(
            position=pos,
            decimal_spec=DecimalSpec(
                price_decimals=market_price_decimals_map[pos.market_id],
                position_decimals=market_position_decimals_map[pos.market_id],
                asset_decimals=asset_decimals_map[market_to_asset_map[pos.market_id]],
            ),
        )

    if market_id is None:
        return positions
    else:
        return positions[market_id]


def list_accounts(
    data_client: vac.VegaTradingDataClientV2,
    pub_key: Optional[str] = None,
    asset_id: Optional[str] = None,
    market_id: Optional[str] = None,
    asset_decimals_map: Optional[Dict[str, int]] = None,
) -> List[AccountData]:
    """Output money in general accounts/margin accounts/bond accounts (if exists)
    of a party."""
    accounts = data_raw.list_accounts(
        data_client=data_client,
        party_id=pub_key,
        asset_id=asset_id,
        market_id=market_id,
    )

    asset_decimals_map = {} if asset_decimals_map is None else asset_decimals_map
    output_accounts = []
    for account in accounts:
        if account.asset not in asset_decimals_map:
            asset_decimals_map[account.asset] = get_asset_decimals(
                asset_id=account.asset,
                data_client=data_client,
            )

        output_accounts.append(
            AccountData(
                owner=account.owner,
                balance=num_from_padded_int(
                    int(account.balance), asset_decimals_map.setdefault(account.asset)
                ),
                asset=account.asset,
                type=account.type,
                market_id=account.market_id,
            )
        )
    return output_accounts


def party_account(
    pub_key: str,
    asset_id: str,
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
    asset_dp: Optional[int] = None,
) -> PartyMarketAccount:
    """Output money in general accounts/margin accounts/bond accounts (if exists)
    of a party."""
    accounts = data_raw.list_accounts(
        data_client=data_client,
        party_id=pub_key,
        asset_id=asset_id,
    )

    asset_dp = (
        asset_dp if asset_dp is not None else get_asset_decimals(asset_id, data_client)
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

    return PartyMarketAccount(general, margin, bond)


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
    res = data_raw.market_info(
        market_id=market_id, data_client=data_client
    ).decimal_places
    return res


def market_position_decimals(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
) -> int:
    """Returns the number of decimal places a specified market uses for position units.

    Args:
        market_id:
            str, The ID of the market requested
        data_client:
            VegaTradingDataClientV2,
    Returns:
        int, The number of decimal places the market uses for positions
    """
    return data_raw.market_info(
        market_id=market_id, data_client=data_client
    ).position_decimal_places


def get_asset_decimals(
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
    market_data: Optional[vega_protos.vega.MarketData] = None,
) -> Tuple[float, float]:
    """
    Output the best static bid price and best static ask price in current market.
    """
    mkt_data = (
        market_data
        if market_data is not None
        else data_raw.market_data(market_id=market_id, data_client=data_client)
    )
    mkt_price_dp = (
        price_decimals
        if price_decimals is not None
        else market_price_decimals(market_id=market_id, data_client=data_client)
    )

    return (
        num_from_padded_int(mkt_data.best_static_bid_price, mkt_price_dp),
        num_from_padded_int(mkt_data.best_static_offer_price, mkt_price_dp),
    )


def price_bounds(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
    price_decimals: Optional[int] = None,
    market_data: Optional[vega_protos.vega.MarketData] = None,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Output the tightest price bounds in current market.
    """
    mkt_data = (
        market_data
        if market_data is not None
        else data_raw.market_data(market_id=market_id, data_client=data_client)
    )
    mkt_price_dp = (
        price_decimals
        if price_decimals is not None
        else market_price_decimals(market_id=market_id, data_client=data_client)
    )

    lower_bounds = [
        price_monitoring_bound.min_valid_price
        for price_monitoring_bound in mkt_data.price_monitoring_bounds
    ]
    upper_bounds = [
        price_monitoring_bound.max_valid_price
        for price_monitoring_bound in mkt_data.price_monitoring_bounds
    ]

    return (
        num_from_padded_int(max(lower_bounds), mkt_price_dp) if lower_bounds else None,
        num_from_padded_int(min(upper_bounds), mkt_price_dp) if upper_bounds else None,
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
            decimal_spec=DecimalSpec(
                price_decimals=mkt_price_dp[order.market_id],
                position_decimals=mkt_pos_dp[order.market_id],
            ),
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
            DecimalSpec(
                price_decimals=mkt_price_dp[order.market_id],
                position_decimals=mkt_pos_dp[order.market_id],
            ),
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
    accounts = data_raw.list_accounts(
        asset_id=None, market_id=market_id, data_client=data_client
    )
    acct = {account.type: account for account in accounts}[account_type]

    asset_dp = get_asset_decimals(asset_id=acct.asset, data_client=data_client)
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
            asset_dp[margin.asset] = get_asset_decimals(
                asset_id=margin.asset, data_client=data_client
            )
        res_margins.append(
            _margin_level_from_proto(
                margin, DecimalSpec(asset_decimals=asset_dp[margin.asset])
            )
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
            market_asset_decimals_map[trade.market_id] = get_asset_decimals(
                asset_id=data_raw.market_info(
                    market_id=market_id, data_client=data_client
                ).tradable_instrument.instrument.future.settlement_asset,
                data_client=data_client,
            )
        res_trades.append(
            _trade_from_proto(
                trade,
                DecimalSpec(
                    price_decimals=market_price_decimals_map[trade.market_id],
                    position_decimals=market_position_decimals_map[trade.market_id],
                    asset_decimals=market_asset_decimals_map[trade.market_id],
                ),
            )
        )
    return res_trades


def ping(data_client: vac.VegaTradingDataClientV2):
    return data_client.Ping(data_node_protos_v2.trading_data.PingRequest())


def list_transfers(
    data_client: vac.VegaTradingDataClientV2,
    party_id: Optional[str] = None,
    direction: data_node_protos_v2.trading_data.TransferDirection = None,
) -> List[Transfer]:
    """Returns a list of processed transfers.

    Args:
        data_client (vac.VegaTradingDataClientV2):
            An instantiated gRPC trading data client
        party_id (Optional[str], optional):
            Public key for the specified party. Defaults to None.
        direction (Optional[data_node_protos_v2.trading_data.TransferDirection], optional):
            Direction of transfers to return. Defaults to None.

    Returns:
        List[Transfer]:
            A list of processed Transfer objects for the specified party and direction.
    """

    transfers = data_raw.list_transfers(
        data_client=data_client,
        party_id=party_id,
        direction=direction,
    )

    asset_dp = {}
    res_transfers = []

    for transfer in transfers:
        if transfer.status == events_protos.Transfer.Status.STATUS_REJECTED:
            continue

        if transfer.asset not in asset_dp:
            asset_dp[transfer.asset] = get_asset_decimals(
                asset_id=transfer.asset, data_client=data_client
            )
        res_transfers.append(
            _transfer_from_proto(
                transfer=transfer,
                decimal_spec=DecimalSpec(asset_decimals=asset_dp[transfer.asset]),
            )
        )

    return res_transfers


def _stream_handler(
    stream_item: vega_protos.api.v1.core.ObserveEventBusResponse,
    extraction_fn: Callable[[vega_protos.events.v1.events.BusEvent], T],
    conversion_fn: Callable[[T, int, int, int], S],
    mkt_pos_dp: Optional[Dict[str, int]] = None,
    mkt_price_dp: Optional[Dict[str, int]] = None,
    mkt_to_asset: Optional[Dict[str, str]] = None,
    asset_dp: Optional[Dict[str, int]] = None,
) -> S:
    mkt_pos_dp = mkt_pos_dp if mkt_pos_dp is not None else {}
    mkt_price_dp = mkt_price_dp if mkt_price_dp is not None else {}
    mkt_to_asset = mkt_to_asset if mkt_to_asset is not None else {}
    asset_dp = asset_dp if asset_dp is not None else {}

    event = extraction_fn(stream_item)

    market_id = getattr(event, "market_id", None)
    asset_decimals = asset_dp.get(getattr(event, "asset", mkt_to_asset.get(market_id)))

    return conversion_fn(
        event,
        DecimalSpec(
            price_decimals=mkt_price_dp[market_id] if market_id is not None else None,
            position_decimals=mkt_pos_dp[market_id] if market_id is not None else None,
            asset_decimals=asset_decimals,
        ),
    )


def get_liquidity_fee_shares(
    data_client: vac.VegaTradingDataClientV2,
    market_id: str,
    party_id: Optional[str] = None,
    market_data: Optional[vega_protos.vega.MarketData] = None,
) -> Union[Dict, float]:
    """Gets the current liquidity fee share for each party or a specified party.

    Args:
        data_client (vac.VegaTradingDataClientV2):
            An instantiated gRPC data client
        market_id (str):
            Id of market to get liquidity fee shares from.
        party_id (Optional[str], optional):
            Id of party to get liquidity fee shares for. Defaults to None.
        market_data (Optional[vega_protos.markets.MarketData]):
            Market data to use. If not passed, loads from data node
    """

    market_data = (
        market_data
        if market_data is not None
        else data_raw.market_data(data_client=data_client, market_id=market_id)
    )

    # Calculate share of fees for each LP
    shares = {
        lp.party: float(lp.equity_like_share) * float(lp.average_score)
        for lp in market_data.liquidity_provider_fee_share
    }
    total_shares = sum(shares.values())

    # Scale share of fees for each LP pro rata
    if total_shares != 0:
        pro_rata_shares = {key: val / total_shares for key, val in shares.items()}
    else:
        pro_rata_shares = {key: 1 / len(shares) for key, val in shares.items()}

    if party_id is None:
        return pro_rata_shares
    else:
        return pro_rata_shares[party_id]


def list_ledger_entries(
    data_client: vac.VegaTradingDataClientV2,
    close_on_account_filters: bool = False,
    asset_id: Optional[str] = None,
    from_party_ids: Optional[List[str]] = None,
    to_party_ids: Optional[List[str]] = None,
    from_account_types: Optional[list[vega_protos.vega.AccountType]] = None,
    from_market_ids: Optional[List[str]] = None,
    to_market_ids: Optional[List[str]] = None,
    to_account_types: Optional[list[vega_protos.vega.AccountType]] = None,
    transfer_types: Optional[list[vega_protos.vega.TransferType]] = None,
    from_datetime: Optional[datetime.datetime] = None,
    to_datetime: Optional[datetime.datetime] = None,
    asset_decimals_map: Optional[Dict[str, int]] = None,
) -> List[AggregatedLedgerEntry]:
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
        List[AggregatedLedgerEntry]
            A list of all transfers matching the requested criteria
    """
    raw_ledger_entries = data_raw.list_ledger_entries(
        data_client=data_client,
        close_on_account_filters=close_on_account_filters,
        asset_id=asset_id,
        from_party_ids=from_party_ids,
        to_party_ids=to_party_ids,
        from_account_types=from_account_types,
        from_market_ids=from_market_ids,
        to_market_ids=to_market_ids,
        transfer_types=transfer_types,
        from_datetime=from_datetime,
        to_datetime=to_datetime,
        to_account_types=to_account_types,
    )

    asset_decimals_map = {} if asset_decimals_map is None else asset_decimals_map
    ledger_entries = []
    for entry in raw_ledger_entries:
        if entry.asset_id not in asset_decimals_map:
            asset_decimals_map[entry.asset_id] = get_asset_decimals(
                asset_id=entry.asset_id,
                data_client=data_client,
            )
        ledger_entries.append(
            _aggregated_ledger_entry_from_proto(
                entry, DecimalSpec(asset_decimals=asset_decimals_map[entry.asset_id])
            )
        )
    return ledger_entries


def trades_subscription_handler(
    stream: Iterable[vega_protos.api.v1.core.ObserveEventBusResponse],
    mkt_pos_dp: Optional[Dict[str, int]] = None,
    mkt_price_dp: Optional[Dict[str, int]] = None,
    mkt_to_asset: Optional[Dict[str, str]] = None,
    asset_dp: Optional[Dict[str, int]] = None,
) -> Trade:
    """Subscribe to a stream of Order updates from the data-node.
    The stream of orders returned from this function is an iterable which
    does not end and will continue to tick another order update whenever
    one is received.

    Returns:
        Iterable[Trade], Infinite iterable of trade updates
    """
    return _stream_handler(
        stream_item=stream,
        extraction_fn=lambda evt: evt.trade,
        conversion_fn=_trade_from_proto,
        mkt_pos_dp=mkt_pos_dp,
        mkt_price_dp=mkt_price_dp,
        mkt_to_asset=mkt_to_asset,
        asset_dp=asset_dp,
    )


def order_subscription_handler(
    stream: Iterable[vega_protos.api.v1.core.ObserveEventBusResponse],
    mkt_pos_dp: Optional[Dict[str, int]] = None,
    mkt_price_dp: Optional[Dict[str, int]] = None,
    mkt_to_asset: Optional[Dict[str, str]] = None,
    asset_dp: Optional[Dict[str, int]] = None,
) -> Order:
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
    return _stream_handler(
        stream_item=stream,
        extraction_fn=lambda evt: evt.order,
        conversion_fn=_order_from_proto,
        mkt_pos_dp=mkt_pos_dp,
        mkt_price_dp=mkt_price_dp,
        mkt_to_asset=mkt_to_asset,
        asset_dp=asset_dp,
    )


def transfer_subscription_handler(
    stream: Iterable[vega_protos.api.v1.core.ObserveEventBusResponse],
    mkt_pos_dp: Optional[Dict[str, int]] = None,
    mkt_price_dp: Optional[Dict[str, int]] = None,
    mkt_to_asset: Optional[Dict[str, str]] = None,
    asset_dp: Optional[Dict[str, int]] = None,
) -> Transfer:
    return _stream_handler(
        stream_item=stream,
        extraction_fn=lambda evt: evt.transfer,
        conversion_fn=_transfer_from_proto,
        mkt_pos_dp=mkt_pos_dp,
        mkt_price_dp=mkt_price_dp,
        mkt_to_asset=mkt_to_asset,
        asset_dp=asset_dp,
    )


def ledger_entries_subscription_handler(
    stream_item: vega_protos.api.v1.core.ObserveEventBusResponse,
    asset_dp: Optional[Dict[str, int]] = None,
) -> Iterable[LedgerEntry]:
    ledger_entries = []
    for ledger_movement in stream_item.ledger_movements.ledger_movements:
        for ledger_entry in ledger_movement.entries:
            asset_id = ledger_entry.from_account.asset_id
            ledger_entries.append(
                _ledger_entry_from_proto(
                    ledger_entry,
                    asset_decimals=asset_dp[asset_id],
                )
            )
    return ledger_entries


def get_risk_factors(
    data_client: vac.VegaTradingDataClientV2,
    market_id: str,
):
    raw_risk_factors = data_raw.get_risk_factors(
        data_client=data_client, market_id=market_id
    )
    return RiskFactor(
        market_id=market_id,
        short=float(raw_risk_factors.risk_factor.short),
        long=float(raw_risk_factors.risk_factor.long),
    )
