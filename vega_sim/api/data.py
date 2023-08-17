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
from collections import defaultdict


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


@dataclass
class IcebergOrder:
    peak_size: float
    minimum_visible_size: float
    reserved_remaining: float


@dataclass
class Order:
    price: float
    size: float
    id: str
    reference: str
    side: vega_protos.vega.Side
    status: vega_protos.vega.Order.Status
    remaining: float
    time_in_force: vega_protos.vega.Order.TimeInForce
    order_type: vega_protos.vega.Order.Type
    created_at: int
    expires_at: int
    party_id: str
    market_id: str
    updated_at: int
    version: int
    iceberg_order: Optional[IcebergOrder]


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
class LiquidationPrice:
    open_volume_only: float
    including_buy_orders: float
    including_sell_orders: float


@dataclass
class MarginEstimate:
    best_case: MarginLevels
    worst_case: MarginLevels


@dataclass
class LiquidationEstimate:
    best_case: LiquidationPrice
    worst_case: LiquidationPrice


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
    maker_fee_volume_discount: float
    infrastructure_fee_volume_discount: float
    liquidity_fee_volume_discount: float
    maker_fee_referrer_discount: float
    infrastructure_fee_referrer_discount: float
    liquidity_fee_referrer_discount: float


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


@dataclass(frozen=True)
class MarketData:
    mark_price: float
    best_bid_price: float
    best_bid_volume: float
    best_offer_price: float
    best_offer_volume: float
    best_static_bid_price: float
    best_static_bid_volume: float
    best_static_offer_price: float
    best_static_offer_volume: float
    mid_price: float
    static_mid_price: float
    market_id: str
    timestamp: str
    open_interest: float
    auction_end: str
    auction_start: str
    indicative_price: float
    indicative_volume: float
    market_trading_mode: str
    trigger: str
    extension_trigger: str
    target_stake: float
    supplied_stake: float
    market_value_proxy: float
    price_monitoring_bounds: list
    liquidity_provider_fee_share: list
    market_state: str
    next_mark_to_market: float
    last_traded_price: float


@dataclass(frozen=True)
class PriceMonitoringBounds:
    min_valid_price: float
    max_valid_price: float
    trigger: str
    reference_price: float


@dataclass(frozen=True)
class LiquidityProviderFeeShare:
    party: str
    equity_like_share: float
    average_entry_valuation: float
    average_score: float


@dataclass(frozen=True)
class ReferralSet:
    id: str
    referrer: str
    created_at: int
    updated_at: int


@dataclass(frozen=True)
class ReferralSetReferee:
    referral_set_id: str
    referee: str
    joined_at: int
    at_epoch: int


@dataclass(frozen=True)
class VolumeDiscountStats:
    at_epoch: int
    party_id: str
    discount_factor: float
    running_volume: float


@dataclass(frozen=True)
class BenefitTier:
    minimum_running_notional_taker_volume: float
    minimum_epochs: int
    referral_reward_factor: float
    referral_discount_factor: float


@dataclass(frozen=True)
class StakingTier:
    minimum_staked_tokens: int
    referral_reward_multiplier: float


@dataclass(frozen=True)
class ReferralProgram:
    version: int
    id: str
    benefit_tiers: List[BenefitTier]
    end_of_program_timestamp: int
    window_length: int
    staking_tiers: List[StakingTier]
    ended_at: int


@dataclass(frozen=True)
class VolumeBenefitTier:
    minimum_running_notional_taker_volume: float
    volume_discount_factor: float


@dataclass(frozen=True)
class VolumeDiscountProgram:
    version: int
    id: str
    benefit_tiers: List[VolumeBenefitTier]
    end_of_program_timestamp: str
    window_length: int
    ended_at: int


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
            maker_fee_volume_discount=num_from_padded_int(
                trade.buyer_fee.maker_fee_volume_discount, decimal_spec.asset_decimals
            ),
            infrastructure_fee_volume_discount=num_from_padded_int(
                trade.buyer_fee.infrastructure_fee_volume_discount,
                decimal_spec.asset_decimals,
            ),
            liquidity_fee_volume_discount=num_from_padded_int(
                trade.buyer_fee.liquidity_fee_volume_discount,
                decimal_spec.asset_decimals,
            ),
            maker_fee_referrer_discount=num_from_padded_int(
                trade.buyer_fee.maker_fee_referrer_discount, decimal_spec.asset_decimals
            ),
            infrastructure_fee_referrer_discount=num_from_padded_int(
                trade.buyer_fee.infrastructure_fee_referrer_discount,
                decimal_spec.asset_decimals,
            ),
            liquidity_fee_referrer_discount=num_from_padded_int(
                trade.buyer_fee.liquidity_fee_referrer_discount,
                decimal_spec.asset_decimals,
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
            maker_fee_volume_discount=num_from_padded_int(
                trade.seller_fee.maker_fee_volume_discount, decimal_spec.asset_decimals
            ),
            infrastructure_fee_volume_discount=num_from_padded_int(
                trade.seller_fee.infrastructure_fee_volume_discount,
                decimal_spec.asset_decimals,
            ),
            liquidity_fee_volume_discount=num_from_padded_int(
                trade.seller_fee.liquidity_fee_volume_discount,
                decimal_spec.asset_decimals,
            ),
            maker_fee_referrer_discount=num_from_padded_int(
                trade.seller_fee.maker_fee_referrer_discount,
                decimal_spec.asset_decimals,
            ),
            infrastructure_fee_referrer_discount=num_from_padded_int(
                trade.seller_fee.infrastructure_fee_referrer_discount,
                decimal_spec.asset_decimals,
            ),
            liquidity_fee_referrer_discount=num_from_padded_int(
                trade.seller_fee.liquidity_fee_referrer_discount,
                decimal_spec.asset_decimals,
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


def _iceberg_order_from_proto(
    iceberg_order: vega_protos.vega.IcebergOrder,
    decimal_spec: DecimalSpec,
) -> IcebergOrder:
    return IcebergOrder(
        peak_size=num_from_padded_int(
            iceberg_order.peak_size, decimal_spec.position_decimals
        ),
        minimum_visible_size=num_from_padded_int(
            iceberg_order.minimum_visible_size, decimal_spec.position_decimals
        ),
        reserved_remaining=num_from_padded_int(
            iceberg_order.reserved_remaining, decimal_spec.position_decimals
        ),
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
        iceberg_order=_iceberg_order_from_proto(order.iceberg_order, decimal_spec)
        if order.HasField("iceberg_order")
        else None,
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


def _margin_estimate_from_proto(
    margin_estimate: data_node_protos_v2.trading_data.MarginEstimate,
    decimal_spec: DecimalSpec,
) -> MarginEstimate:
    return MarginEstimate(
        best_case=_margin_level_from_proto(
            margin_level=margin_estimate.best_case, decimal_spec=decimal_spec
        ),
        worst_case=_margin_level_from_proto(
            margin_level=margin_estimate.worst_case, decimal_spec=decimal_spec
        ),
    )


def _liquidation_estimate_from_proto(
    liquidation_estimate: data_node_protos_v2.trading_data.LiquidationEstimate,
):
    return LiquidationEstimate(
        best_case=_liquidation_price_from_proto(liquidation_estimate.best_case),
        worst_case=_liquidation_price_from_proto(liquidation_estimate.worst_case),
    )


def _liquidation_price_from_proto(
    liquidation_price: data_node_protos_v2.trading_data.LiquidationPrice,
):
    return LiquidationPrice(
        open_volume_only=float(liquidation_price.open_volume_only),
        including_buy_orders=float(liquidation_price.including_buy_orders),
        including_sell_orders=float(liquidation_price.including_sell_orders),
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


def _market_data_from_proto(
    market_data: vega_protos.vega.MarketData,
    decimal_spec: DecimalSpec,
):
    return MarketData(
        mark_price=num_from_padded_int(
            market_data.mark_price, decimal_spec.price_decimals
        ),
        best_bid_price=num_from_padded_int(
            market_data.best_bid_price, decimal_spec.price_decimals
        ),
        best_bid_volume=num_from_padded_int(
            market_data.best_bid_volume, decimal_spec.position_decimals
        ),
        best_offer_price=num_from_padded_int(
            market_data.best_offer_price, decimal_spec.price_decimals
        ),
        best_offer_volume=num_from_padded_int(
            market_data.best_offer_volume, decimal_spec.position_decimals
        ),
        best_static_bid_price=num_from_padded_int(
            market_data.best_static_bid_price, decimal_spec.price_decimals
        ),
        best_static_bid_volume=num_from_padded_int(
            market_data.best_static_bid_price, decimal_spec.position_decimals
        ),
        best_static_offer_price=num_from_padded_int(
            market_data.best_static_offer_price, decimal_spec.price_decimals
        ),
        best_static_offer_volume=num_from_padded_int(
            market_data.best_static_offer_volume, decimal_spec.position_decimals
        ),
        mid_price=num_from_padded_int(
            market_data.mid_price, decimal_spec.price_decimals
        ),
        static_mid_price=num_from_padded_int(
            market_data.static_mid_price, decimal_spec.price_decimals
        ),
        market_id=market_data.market,
        timestamp=market_data.timestamp,
        open_interest=market_data.open_interest,
        auction_end=market_data.auction_end,
        auction_start=market_data.auction_start,
        indicative_price=num_from_padded_int(
            market_data.indicative_price, decimal_spec.price_decimals
        ),
        indicative_volume=num_from_padded_int(
            market_data.indicative_volume, decimal_spec.price_decimals
        ),
        market_trading_mode=market_data.market_trading_mode,
        trigger=market_data.trigger,
        extension_trigger=market_data.extension_trigger,
        target_stake=num_from_padded_int(
            market_data.target_stake, decimal_spec.asset_decimals
        ),
        supplied_stake=num_from_padded_int(
            market_data.supplied_stake, decimal_spec.asset_decimals
        ),
        market_value_proxy=num_from_padded_int(
            market_data.market_value_proxy, decimal_spec.asset_decimals
        ),
        price_monitoring_bounds=_price_monitoring_bounds_from_proto(
            market_data.price_monitoring_bounds, decimal_spec.price_decimals
        ),
        liquidity_provider_fee_share=_liquidity_provider_fee_share_from_proto(
            market_data.liquidity_provider_fee_share,
            decimal_spec.asset_decimals,
        ),
        market_state=market_data.market_state,
        next_mark_to_market=market_data.next_mark_to_market,
        last_traded_price=num_from_padded_int(
            market_data.last_traded_price, decimal_spec.price_decimals
        ),
    )


def _price_monitoring_bounds_from_proto(
    price_monitoring_bounds,
    price_decimals: int,
) -> List[PriceMonitoringBounds]:
    return [
        PriceMonitoringBounds(
            min_valid_price=num_from_padded_int(
                individual_bound.min_valid_price,
                price_decimals,
            ),
            max_valid_price=num_from_padded_int(
                individual_bound.max_valid_price,
                price_decimals,
            ),
            trigger=individual_bound.trigger,
            reference_price=num_from_padded_int(
                individual_bound.reference_price,
                price_decimals,
            ),
        )
        for individual_bound in price_monitoring_bounds
    ]


def _liquidity_provider_fee_share_from_proto(
    liquidity_provider_fee_share,
    asset_decimals,
) -> List[PriceMonitoringBounds]:
    return [
        LiquidityProviderFeeShare(
            party=individual_liquidity_provider_fee_share.party,
            equity_like_share=float(
                individual_liquidity_provider_fee_share.equity_like_share
            ),
            average_entry_valuation=num_from_padded_int(
                float(individual_liquidity_provider_fee_share.average_entry_valuation),
                asset_decimals,
            ),
            average_score=float(
                individual_liquidity_provider_fee_share.equity_like_share
            ),
        )
        for individual_liquidity_provider_fee_share in liquidity_provider_fee_share
    ]


def _referral_set_from_proto(
    referral_set,
) -> ReferralSet:
    return ReferralSet(
        id=referral_set.id,
        referrer=referral_set.referrer,
        created_at=referral_set.created_at,
        updated_at=referral_set.updated_at,
    )


def _referral_set_referee_from_proto(
    referral_set_referee,
) -> ReferralSetReferee:
    return ReferralSetReferee(
        referral_set_id=referral_set_referee.referral_set_id,
        referee=referral_set_referee.referee,
        joined_at=referral_set_referee.joined_at,
        at_epoch=referral_set_referee.at_epoch,
    )


def _benefit_tier_from_proto(benefit_tier) -> BenefitTier:
    return BenefitTier(
        minimum_running_notional_taker_volume=float(
            benefit_tier.minimum_running_notional_taker_volume
        ),
        minimum_epochs=int(benefit_tier.minimum_epochs),
        referral_reward_factor=float(benefit_tier.referral_reward_factor),
        referral_discount_factor=float(benefit_tier.referral_discount_factor),
    )


def _staking_tier_from_proto(staking_tier) -> StakingTier:
    return StakingTier(
        minimum_staked_tokens=float(staking_tier.minimum_staked_tokens),
        referral_reward_multiplier=float(staking_tier.referral_reward_multiplier),
    )


def _referral_program_from_proto(referral_program) -> ReferralProgram:
    return ReferralProgram(
        version=referral_program.version,
        id=referral_program.id,
        benefit_tiers=[
            _benefit_tier_from_proto(benefit_tier)
            for benefit_tier in referral_program.benefit_tiers
        ],
        staking_tiers=[
            _staking_tier_from_proto(staking_tier)
            for staking_tier in referral_program.staking_tiers
        ],
        end_of_program_timestamp=referral_program.end_of_program_timestamp,
        window_length=referral_program.window_length,
        ended_at=referral_program.ended_at,
    )


def _volume_benefit_tier_from_proto(volume_benefit_tier) -> VolumeBenefitTier:
    return VolumeBenefitTier(
        minimum_running_notional_taker_volume=float(
            volume_benefit_tier.minimum_running_notional_taker_volume
        ),
        volume_discount_factor=float(volume_benefit_tier.volume_discount_factor),
    )


def _volume_discount_program_from_proto(
    volume_discount_program,
) -> VolumeDiscountProgram:
    return VolumeDiscountProgram(
        version=int(volume_discount_program.version),
        id=str(volume_discount_program.id),
        benefit_tiers=[
            _volume_benefit_tier_from_proto(volume_benefit_tier)
            for volume_benefit_tier in volume_discount_program.benefit_tiers
        ],
        end_of_program_timestamp=int(volume_discount_program.end_of_program_timestamp),
        window_length=int(volume_discount_program.window_length),
        ended_at=int(volume_discount_program.ended_at),
    )


def _volume_discount_stats_from_proto(volume_discount_stats) -> VolumeDiscountStats:
    return VolumeDiscountStats(
        at_epoch=int(volume_discount_stats.at_epoch),
        party_id=str(volume_discount_stats.party_id),
        discount_factor=float(volume_discount_stats.discount_factor),
        running_volume=float(volume_discount_stats.running_volume),
    )


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
    enabled: bool = True,
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
            if (enabled) and (asset.status != vega_protos.assets.Asset.STATUS_ENABLED):
                continue
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
        (
            bids.append(order)
            if order.side == vega_protos.vega.SIDE_BUY
            else asks.append(order)
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
    start: Optional[datetime.datetime] = None,
    end: Optional[datetime.datetime] = None,
) -> List[Trade]:
    base_trades = data_raw.get_trades(
        data_client=data_client,
        party_id=party_id,
        market_id=market_id,
        order_id=order_id,
        start=start,
        end=end,
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

    market_id = getattr(event, "market_id", getattr(event, "market", None))

    # Check market creation event observed
    if (market_id is not None) and (
        (market_id not in mkt_pos_dp)
        or (market_id not in mkt_price_dp)
        or (market_id not in mkt_to_asset)
    ):
        return

    asset_id = getattr(
        event,
        "asset",
        mkt_to_asset[market_id] if market_id is not None else None,
    )

    # Check asset creation event observed
    if (asset_id is not None) and (asset_id not in asset_dp):
        return

    return conversion_fn(
        event,
        DecimalSpec(
            price_decimals=mkt_price_dp[market_id] if market_id is not None else None,
            position_decimals=mkt_pos_dp[market_id] if market_id is not None else None,
            asset_decimals=asset_dp[asset_id],
        ),
    )


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


def market_data_subscription_handler(
    stream_item: vega_protos.api.v1.core.ObserveEventBusResponse,
    mkt_pos_dp: Optional[Dict[str, int]] = None,
    mkt_price_dp: Optional[Dict[str, int]] = None,
    mkt_to_asset: Optional[Dict[str, str]] = None,
    asset_dp: Optional[Dict[str, int]] = None,
):
    return _stream_handler(
        stream_item=stream_item,
        extraction_fn=lambda evt: evt.market_data,
        conversion_fn=_market_data_from_proto,
        mkt_pos_dp=mkt_pos_dp,
        mkt_price_dp=mkt_price_dp,
        mkt_to_asset=mkt_to_asset,
        asset_dp=asset_dp,
    )


def get_latest_market_data(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
    market_price_decimals_map: Optional[Dict[str, int]] = None,
    market_position_decimals_map: Optional[Dict[str, int]] = None,
    market_to_asset_map: Optional[Dict[str, str]] = None,
    asset_decimals_map: Optional[Dict[str, int]] = None,
) -> MarketData:
    # Get latest market data
    market_data = data_raw.get_latest_market_data(
        market_id=market_id, data_client=data_client
    )

    market_price_decimals_map = (
        market_price_decimals_map if market_price_decimals_map is not None else {}
    )
    market_position_decimals_map = (
        market_position_decimals_map if market_position_decimals_map is not None else {}
    )
    market_to_asset_map = market_to_asset_map if market_to_asset_map is not None else {}
    asset_decimals_map = asset_decimals_map if asset_decimals_map is not None else {}

    if market_id not in market_price_decimals_map:
        market_price_decimals_map[market_id] = market_price_decimals(
            market_id=market_id, data_client=data_client
        )
    if market_id not in market_position_decimals_map:
        market_position_decimals_map[market_id] = market_position_decimals(
            market_id=market_id, data_client=data_client
        )
    if market_id not in market_to_asset_map:
        market_to_asset_map[market_id] = data_raw.market_info(
            market_id=market_id, data_client=data_client
        ).tradable_instrument.instrument.future.settlement_asset
    if market_to_asset_map[market_id] not in asset_decimals_map:
        asset_decimals_map[market_to_asset_map[market_id]] = get_asset_decimals(
            asset_id=market_to_asset_map[market_id],
            data_client=data_client,
        )
    # Convert from proto
    return _market_data_from_proto(
        market_data=market_data,
        decimal_spec=DecimalSpec(
            price_decimals=market_price_decimals_map[market_data.market],
            position_decimals=market_position_decimals_map[market_data.market],
            asset_decimals=asset_decimals_map[market_to_asset_map[market_data.market]],
        ),
    )


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


def estimate_position(
    data_client: vac.VegaTradingDataClientV2,
    market_id: str,
    open_volume: int,
    orders: Optional[List[Tuple[str, str, int, bool]]] = None,
    collateral_available: Optional[str] = None,
    asset_decimals: Optional[Dict[str, int]] = {},
) -> Tuple[MarginEstimate, LiquidationEstimate,]:
    if orders is not None:
        proto_orders = [
            data_node_protos_v2.trading_data.OrderInfo(
                side=order[0],
                price=order[1],
                remaining=order[2],
                is_market_order=order[3],
            )
            for order in orders
        ]

    margin_estimate, liquidation_estimate = data_raw.estimate_position(
        data_client=data_client,
        market_id=market_id,
        open_volume=open_volume,
        orders=proto_orders if orders is not None else None,
        collateral_available=collateral_available,
    )

    if margin_estimate.best_case.asset not in asset_decimals:
        asset_decimals[margin_estimate.best_case.asset] = get_asset_decimals(
            asset_id=margin_estimate.best_case.market_id, data_client=data_client
        )

    converted_margin_estimate = _margin_estimate_from_proto(
        margin_estimate=margin_estimate,
        decimal_spec=DecimalSpec(
            asset_decimals=asset_decimals[margin_estimate.best_case.asset]
        ),
    )

    converted_liquidation_estimate = _liquidation_estimate_from_proto(
        liquidation_estimate=liquidation_estimate,
    )

    return converted_margin_estimate, converted_liquidation_estimate


def get_stake(
    data_client: vac.trading_data_grpc_v2, party_id: str, asset_decimals: int
):
    return num_from_padded_int(
        data_raw.get_stake(data_client=data_client, party_id=party_id),
        decimals=asset_decimals,
    )


def get_asset(
    data_client: vac.trading_data_grpc_v2,
    asset_id: str,
):
    return data_raw.asset_info(data_client=data_client, asset_id=asset_id)


def list_referral_sets(
    data_client: vac.trading_data_grpc_v2,
    referral_set_id: Optional[str] = None,
    referrer: Optional[str] = None,
    referee: Optional[str] = None,
) -> Dict[str, ReferralSet]:
    response: List[
        data_node_protos_v2.trading_data.ReferralSet
    ] = data_raw.list_referral_sets(
        data_client=data_client,
        referral_set_id=referral_set_id,
        referrer=referrer,
        referee=referee,
    )
    referral_sets = {}
    for referral_set in response:
        referral_sets[referral_set.id] = _referral_set_from_proto(referral_set)
    return referral_sets


def list_referral_set_referees(
    data_client: vac.trading_data_grpc_v2,
    referral_set_id: Optional[str] = None,
    referrer: Optional[str] = None,
    referee: Optional[str] = None,
) -> Dict[str, Dict[str, ReferralSetReferee]]:
    response: List[
        data_node_protos_v2.trading_data.ReferralSetReferee
    ] = data_raw.list_referral_set_referees(
        data_client=data_client,
        referral_set_id=referral_set_id,
        referrer=referrer,
        referee=referee,
    )
    referral_set_referees = defaultdict(dict)
    for referral_set_referee in response:
        referral_set_referees[referral_set_referee.referral_set_id][
            referral_set_referee.referee
        ] = _referral_set_referee_from_proto(referral_set_referee)
    return referral_set_referees


def get_current_referral_program(
    data_client: vac.trading_data_grpc_v2,
) -> ReferralProgram:
    response = data_raw.get_current_referral_program(data_client=data_client)
    return _referral_program_from_proto(referral_program=response)


def get_current_volume_discount_program(
    data_client: vac.trading_data_grpc_v2,
) -> VolumeDiscountProgram:
    response = data_raw.get_current_volume_discount_program(data_client=data_client)
    return _volume_discount_program_from_proto(volume_discount_program=response)


def get_volume_discount_stats(
    data_client: vac.trading_data_grpc_v2,
    at_epoch: Optional[int] = None,
    party_id: Optional[str] = None,
) -> List[VolumeDiscountStats]:
    response = data_raw.get_volume_discount_stats(
        data_client=data_client, at_epoch=at_epoch, party_id=party_id
    )
    return [
        _volume_discount_stats_from_proto(volume_discount_stats=volume_discount_stats)
        for volume_discount_stats in response
    ]
