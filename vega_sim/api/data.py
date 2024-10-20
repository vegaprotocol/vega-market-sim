from __future__ import annotations

import logging
import string
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
import vega_protos.protos.data_node.api.v2 as data_node_protos_v2
import vega_protos.protos.vega as vega_protos
import vega_protos.protos.vega.events.v1.events_pb2 as events_protos
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
RiskFactor = namedtuple("RiskFactors", ["market_id", "short", "long"])
OrderBook = namedtuple("OrderBook", ["bids", "asks"])
PriceLevel = namedtuple("PriceLevel", ["price", "number_of_orders", "volume"])


@dataclass(frozen=True)
class AccountData:
    owner: str
    balance: float
    asset: str
    market_id: str
    type: vega_protos.vega.AccountType

    @property
    def account_id(self):
        return f"{self.owner}-{self.type}-{self.market_id}-{self.asset}"


@dataclass(frozen=True)
class IcebergOrder:
    peak_size: float
    minimum_visible_size: float
    reserved_remaining: float


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class MarginLevels:
    maintenance_margin: float
    search_level: float
    initial_margin: float
    collateral_release_level: float
    party_id: str
    market_id: str
    asset: str
    timestamp: datetime.datetime
    margin_mode: vega_protos.vega.MarginMode
    margin_factor: Optional[float] = None


# TODO: Implement class and add to _transfer_from_proto
@dataclass(frozen=True)
class OneOffTransfer:
    pass


# TODO: Implement class and add to _transfer_from_proto
@dataclass(frozen=True)
class RecurringTransfer:
    pass


# TODO: Implement class and add to _transfer_from_proto
@dataclass(frozen=True)
class OneOffGovernanceTransfer:
    pass


# TODO: Implement class and add to _transfer_from_proto
@dataclass(frozen=True)
class RecurringGovernanceTransfer:
    pass


@dataclass(frozen=True)
class Transfer:
    id: str
    party_from: str
    from_account_type: vega_protos.vega.AccountType
    party_to: str
    to_account_type: vega_protos.vega.AccountType
    asset: str
    amount: float
    reference: str
    status: vega_protos.vega.Transfer.Status
    timestamp: datetime.datetime
    reason: Optional[str] = None
    one_off: Optional[OneOffTransfer] = None
    recurring: Optional[RecurringTransfer] = None
    one_off_governance: Optional[OneOffGovernanceTransfer] = None
    recurring_governance: Optional[RecurringGovernanceTransfer] = None


@dataclass(frozen=True)
class TransferFees:
    transfer_id: str
    amount: float
    epoch: int


@dataclass(frozen=True)
class TransferNode:
    transfer: Transfer
    fees: TransferFees


@dataclass(frozen=True)
class LiquidationPrice:
    open_volume_only: float
    including_buy_orders: float
    including_sell_orders: float


@dataclass(frozen=True)
class MarginEstimate:
    best_case: MarginLevels
    worst_case: MarginLevels


@dataclass(frozen=True)
class CollateralIncreaseEstimate:
    best_case: float
    worst_case: float


@dataclass(frozen=True)
class LiquidationEstimate:
    best_case: LiquidationPrice
    worst_case: LiquidationPrice


@dataclass
class DecimalSpec:
    position_decimals: Optional[int] = None
    price_decimals: Optional[int] = None
    asset_decimals: Optional[int] = None


@dataclass(frozen=True)
class LedgerEntry:
    from_account: vega_protos.vega.AccountDetails
    to_account: vega_protos.vega.AccountDetails
    amount: str
    transfer_type: vega_protos.vega.TransferType
    timestamp: int


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class MarketDepth:
    buys: List[PriceLevel]
    sells: List[PriceLevel]


@dataclass(frozen=True)
class OrdersBySide:
    bids: List[Order]
    asks: List[Order]


@dataclass(frozen=True)
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
    timestamp: datetime.datetime
    open_interest: float
    auction_end: Optional[datetime.datetime]
    auction_start: Optional[datetime.datetime]
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
    liquidity_sla: List[LiquidityProviderSLA]
    market_state: str
    next_mark_to_market: datetime.datetime
    last_traded_price: float
    product_data: ProductData


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
class LiquidityProviderSLA:
    party: str
    current_epoch_fraction_of_time_on_book: float
    last_epoch_fraction_of_time_on_book: float
    last_epoch_fee_penalty: float
    last_epoch_bond_penalty: float
    hysteresis_period_fee_penalties: List[float]
    required_liquidity: float
    notional_volume_buys: float
    notional_volume_sells: float


@dataclass(frozen=True)
class PerpetualData:
    start_time: datetime.datetime
    funding_payment: Optional[float]
    funding_rate: Optional[float]
    internal_twap: Optional[float]
    external_twap: Optional[float]


@dataclass(frozen=True)
class ProductData:
    perpetual_data: None | PerpetualData


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
class ReferralSetStats:
    at_epoch: int
    referral_set_running_notional_taker_volume: float
    party_id: str
    discount_factor: float
    reward_factor: float
    epoch_notional_taker_volume: float


@dataclass(frozen=True)
class PartyAmount:
    party: str
    amount: float


@dataclass(frozen=True)
class ReferrerRewardsGenerated:
    referrer: str
    generated_reward: List[PartyAmount]


@dataclass(frozen=True)
class MakerFeesGenerated:
    taker: float
    maker_fees_paid: List[PartyAmount]


@dataclass(frozen=True)
class NetworkParameter:
    key: str
    value: str


@dataclass(frozen=True)
class Position:
    market_id: str
    party_id: str
    open_volume: float
    realised_pnl: float
    unrealised_pnl: float
    average_entry_price: float
    updated_at: datetime.datetime
    loss_socialisation_amount: float
    position_status: vega_protos.vega.PositionStatus


def _network_parameter_from_proto(network_parameter: vega_protos.vega.NetworkParameter):
    return NetworkParameter(key=network_parameter.key, value=network_parameter.value)


def _funding_period_from_proto(
    funding_period: vega_protos.events.v1.events.FundingPeriod,
    decimal_spec: DecimalSpec,
) -> FundingPeriod:
    start_time = datetime.datetime.fromtimestamp(
        funding_period.start / 1e9, tz=datetime.timezone.utc
    )
    end_time = None
    if funding_period.HasField("end"):
        end_time = datetime.datetime.fromtimestamp(
            funding_period.end / 1e9, tz=datetime.timezone.utc
        )

    return FundingPeriod(
        start_time=start_time,
        end_time=end_time,
        funding_payment=(
            None
            if not funding_period.funding_payment
            else num_from_padded_int(
                funding_period.funding_payment, decimal_spec.asset_decimals
            )
        ),
        funding_rate=(
            None
            if not funding_period.funding_rate
            else float(funding_period.funding_rate)
        ),
        internal_twap=(
            None
            if not funding_period.internal_twap
            else num_from_padded_int(
                funding_period.internal_twap, decimal_spec.asset_decimals
            )
        ),
        external_twap=(
            None
            if not funding_period.external_twap
            else num_from_padded_int(
                funding_period.external_twap, decimal_spec.asset_decimals
            )
        ),
    )


def _maker_fees_generated_from_proto(
    maker_fees_generated: vega_protos.events.v1.events.MakerFeesGenerated,
    decimal_spec: DecimalSpec,
):
    return MakerFeesGenerated(
        taker=maker_fees_generated.taker,
        maker_fees_paid=[
            _party_amount_from_proto(party_amount, decimal_spec)
            for party_amount in maker_fees_generated.maker_fees_paid
        ],
    )


@dataclass(frozen=True)
class FeesStats:
    market: str
    asset: str
    epoch_seq: int
    total_rewards_received: List[PartyAmount]
    referrer_rewards_generated: List[ReferrerRewardsGenerated]
    referees_discount_applied: List[PartyAmount]
    volume_discount_applied: List[PartyAmount]
    total_maker_fees_received: List[PartyAmount]
    maker_fees_generated: List[MakerFeesGenerated]


@dataclass(frozen=True)
class VolumeDiscountStats:
    at_epoch: int
    party_id: str
    discount_factor: float
    running_volume: float
    discount_factors: DiscountFactors


@dataclass(frozen=True)
class BenefitTier:
    minimum_running_notional_taker_volume: float
    minimum_epochs: int
    referral_reward_factor: float
    referral_discount_factor: float
    referral_reward_factors: RewardFactors
    referral_discount_factors: DiscountFactors


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
    volume_discount_factors: DiscountFactors


@dataclass(frozen=True)
class VolumeDiscountProgram:
    version: int
    id: str
    benefit_tiers: List[VolumeBenefitTier]
    end_of_program_timestamp: str
    window_length: int
    ended_at: int


@dataclass(frozen=True)
class Team:
    team_id: str
    referrer: str
    name: str
    team_url: str
    avatar_url: str
    created_at: int
    closed: bool
    created_at_epoch: int


@dataclass(frozen=True)
class TeamReferee:
    team_id: str
    referee: str
    joined_at: int
    joined_at_epoch: int


@dataclass(frozen=True)
class TeamRefereeHistory:
    team_id: str
    joined_at: int
    joined_at_epoch: int


@dataclass(frozen=True)
class PeggedOrder:
    reference: vega_protos.vega.PeggedReference
    offset: float


@dataclass(frozen=True)
class IcebergOpts:
    peak_size: float
    minimum_visible_size: float


@dataclass(frozen=True)
class OrderSubmission:
    market_id: str
    size: float
    side: vega_protos.vega.Side
    time_in_force: vega_protos.Order.TimeInForce
    type: vega_protos.Order.Type
    reference: str
    post_only: bool
    reduce_only: bool
    price: Optional[float] = None
    expires_at: Optional[datetime.datetime] = None
    pegged_order: Optional[PeggedOrder] = None
    iceberg_opts: Optional[IcebergOpts] = None


@dataclass(frozen=True)
class StopOrder:
    id: str
    trigger_direction: vega_protos.vega.StopOrder.TriggerDirection
    status: vega_protos.vega.StopOrder.Status
    created_at: datetime.datetime
    updated_at: datetime.datetime
    order_id: str
    party_id: str
    market_id: str
    rejection_reason: vega_protos.vega.StopOrder.RejectionReason
    price: Optional[float] = None
    trailing_percent_offset: Optional[float] = None
    oco_link_id: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None
    expiry_strategy: Optional[vega_protos.vega.StopOrder.ExpiryStrategy] = None


@dataclass(frozen=True)
class Asset:
    id: str
    details: AssetDetails
    status: vega_protos.assets.Asset.Status


@dataclass(frozen=True)
class AssetDetails:
    name: str
    symbol: str
    decimals: int
    quantum: float
    builtin_asset: Optional[BuiltinAsset] = None
    erc20: Optional[ERC20] = None


@dataclass(frozen=True)
class BuiltinAsset:
    max_faucet_amount_mint: float


@dataclass(frozen=True)
class ERC20:
    contract_address: str
    lifetime_limit: float
    withdraw_threshold: float


@dataclass(frozen=True)
class RewardFactors:
    infrastructure_reward_factor: float
    liquidity_reward_factor: float
    maker_reward_factor: float


@dataclass(frozen=True)
class DiscountFactors:
    infrastructure_discount_factor: float
    liquidity_discount_factor: float
    maker_discount_factor: float


def _asset_from_proto(asset: vega_protos.assets.Asset, decimal_spec: DecimalSpec):
    return Asset(
        id=asset.id,
        details=_asset_details_from_proto(asset.details, decimal_spec=decimal_spec),
        status=asset.status,
    )


def _asset_details_from_proto(
    asset_details: vega_protos.assets.AssetDetails, decimal_spec: DecimalSpec
) -> AssetDetails:
    return AssetDetails(
        name=asset_details.name,
        symbol=asset_details.symbol,
        decimals=asset_details.decimals,
        quantum=asset_details.quantum,
        builtin_asset=(
            _builtin_asset_from_proto(
                builtin_asset=asset_details.builtin_asset, decimal_spec=decimal_spec
            )
            if asset_details.builtin_asset is not None
            else None
        ),
        erc20=(
            _erc20_from_proto(erc20=asset_details.erc20, decimal_spec=decimal_spec)
            if asset_details.erc20 is not None
            else None
        ),
    )


def _builtin_asset_from_proto(
    builtin_asset: vega_protos.assets.BuiltinAsset, decimal_spec: DecimalSpec
) -> BuiltinAsset:
    return BuiltinAsset(
        max_faucet_amount_mint=num_from_padded_int(
            to_convert=builtin_asset.max_faucet_amount_mint,
            decimals=decimal_spec.asset_decimals,
        )
    )


def _erc20_from_proto(
    erc20: vega_protos.assets.ERC20, decimal_spec: DecimalSpec
) -> ERC20:
    return ERC20(
        contract_address=erc20.contract_address,
        lifetime_limit=num_from_padded_int(
            to_convert=erc20.lifetime_limit, decimals=decimal_spec.asset_decimals
        ),
        withdraw_threshold=num_from_padded_int(
            to_convert=erc20.withdraw_threshold, decimals=decimal_spec.asset_decimals
        ),
    )


@dataclass(frozen=True)
class StopOrderEvent:
    submission: OrderSubmission
    stop_order: StopOrder


@dataclass(frozen=True)
class FundingPeriod:
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime]
    internal_twap: Optional[float]
    external_twap: Optional[float]
    funding_payment: Optional[float]
    funding_rate: Optional[float]


@dataclass(frozen=True)
class PartyMarginMode:
    market_id: str
    party_id: str
    margin_mode: vega_protos.vega.MarginMode
    at_epoch: int
    margin_factor: Optional[float]
    min_theoretical_margin_factor: Optional[float]
    max_theoretical_leverage: Optional[float]


def _party_margin_mode_from_proto(
    party_margin_mode: data_node_protos_v2.trading_data.PartyMarginMode,
) -> PartyMarginMode:
    return PartyMarginMode(
        market_id=party_margin_mode.market_id,
        party_id=party_margin_mode.party_id,
        margin_mode=party_margin_mode.margin_mode,
        at_epoch=int(party_margin_mode.at_epoch),
        margin_factor=(
            float(party_margin_mode.margin_factor)
            if party_margin_mode.margin_factor != ""
            else None
        ),
        min_theoretical_margin_factor=(
            float(party_margin_mode.min_theoretical_margin_factor)
            if party_margin_mode.min_theoretical_margin_factor != ""
            else None
        ),
        max_theoretical_leverage=(
            float(party_margin_mode.max_theoretical_leverage)
            if party_margin_mode.max_theoretical_leverage != ""
            else None
        ),
    )


def _pegged_order_from_proto(pegged_order, decimal_spec: DecimalSpec) -> PeggedOrder:
    return PeggedOrder(
        reference=pegged_order.reference,
        offset=num_from_padded_int(pegged_order.offset, decimal_spec.price_decimals),
    )


def _iceberg_opts_from_proto(iceberg_opts, decimal_spec: DecimalSpec) -> IcebergOpts:
    return IcebergOpts(
        peak_size=num_from_padded_int(
            iceberg_opts.peak_size, decimal_spec.position_decimals
        ),
        minimum_visible_size=num_from_padded_int(
            iceberg_opts.minimum_visible_size, decimal_spec.position_decimals
        ),
    )


def _order_submission_from_proto(
    order_submission: vega_protos.commands.OrderSubmission,
    decimal_spec: DecimalSpec,
) -> OrderSubmission:
    return OrderSubmission(
        market_id=order_submission.market_id,
        price=num_from_padded_int(order_submission.price, decimal_spec.price_decimals),
        size=num_from_padded_int(order_submission.size, decimal_spec.position_decimals),
        side=order_submission.side,
        time_in_force=order_submission.time_in_force,
        expires_at=(
            datetime.datetime.fromtimestamp(order_submission.expires_at / 1e9)
            if order_submission.expires_at != 0
            else None
        ),
        type=order_submission.type,
        reference=order_submission.reference,
        pegged_order=_pegged_order_from_proto(
            order_submission.pegged_order, decimal_spec
        ),
        post_only=order_submission.post_only,
        reduce_only=order_submission.reduce_only,
        iceberg_opts=_iceberg_opts_from_proto(
            order_submission.iceberg_opts, decimal_spec
        ),
    )


def _stop_order_from_proto(
    stop_order: vega_protos.vega.StopOrder, decimal_spec: DecimalSpec
) -> StopOrder:
    return StopOrder(
        id=stop_order.id,
        oco_link_id=stop_order.oco_link_id,
        expires_at=(
            datetime.datetime.fromtimestamp(stop_order.expires_at / 1e9)
            if stop_order.expires_at != 0
            else None
        ),
        expiry_strategy=stop_order.expiry_strategy,
        trigger_direction=stop_order.trigger_direction,
        status=stop_order.status,
        created_at=(
            datetime.datetime.fromtimestamp(stop_order.created_at / 1e9)
            if stop_order.created_at != 0
            else None
        ),
        updated_at=(
            datetime.datetime.fromtimestamp(stop_order.updated_at / 1e9)
            if stop_order.updated_at != 0
            else None
        ),
        order_id=stop_order.order_id,
        party_id=stop_order.party_id,
        market_id=stop_order.market_id,
        rejection_reason=stop_order.rejection_reason,
        price=(
            num_from_padded_int(stop_order.price, decimal_spec.price_decimals)
            if stop_order.price is not None
            else None
        ),
        trailing_percent_offset=(
            float(stop_order.trailing_percent_offset)
            if stop_order.trailing_percent_offset != ""
            else None
        ),
    )


def _stop_order_event_from_proto(
    stop_order_event: vega_protos.events.StopOrderEvent, decimal_spec: DecimalSpec
) -> StopOrderEvent:
    return StopOrderEvent(
        submission=_order_submission_from_proto(
            stop_order_event.submission, decimal_spec
        ),
        stop_order=_stop_order_from_proto(stop_order_event.stop_order, decimal_spec),
    )


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
        timestamp=datetime.datetime.fromtimestamp(
            int(margin_level.timestamp / 1e9),
            tz=datetime.timezone.utc,
        ),
        margin_mode=margin_level.margin_mode,
        margin_factor=(
            float(margin_level.margin_factor)
            if margin_level.margin_factor != ""
            else None
        ),
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
        iceberg_order=(
            _iceberg_order_from_proto(order.iceberg_order, decimal_spec)
            if order.HasField("iceberg_order")
            else None
        ),
    )


def _position_from_proto(
    position: vega_protos.vega.Position,
    decimal_spec: DecimalSpec,
) -> Position:
    return Position(
        market_id=position.market_id,
        party_id=position.party_id,
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
        updated_at=datetime.datetime.fromtimestamp(position.updated_at / 1e9),
        loss_socialisation_amount=num_from_padded_int(
            position.loss_socialisation_amount,
            decimal_spec.asset_decimals,
        ),
        position_status=position.position_status,
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


def _transfer_fees_from_proto(
    transfer_fees: vega_protos.events.v1.events.TransferFees, decimal_spec: DecimalSpec
) -> TransferFees:
    return TransferFees(
        transfer_id=transfer_fees.transfer_id,
        amount=num_from_padded_int(transfer_fees.amount, decimal_spec.asset_decimals),
        epoch=int(transfer_fees.epoch),
    )


def _transfer_node_from_proto(
    transfer_node: data_node_protos_v2.trading_data.TransferNode,
    decimal_spec: DecimalSpec,
):
    return TransferNode(
        transfer=_transfer_from_proto(
            transfer=transfer_node.transfer, decimal_spec=decimal_spec
        ),
        fees=_transfer_fees_from_proto(
            transfer_fees=transfer_node.fees, decimal_spec=decimal_spec
        ),
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


def _collateral_increase_estimate_from_proto(
    collateral_increase_estimate: data_node_protos_v2.trading_data.CollateralIncreaseEstimate,
    decimal_spec: DecimalSpec,
) -> CollateralIncreaseEstimate:
    return CollateralIncreaseEstimate(
        worst_case=num_from_padded_int(
            collateral_increase_estimate.worst_case,
            decimals=decimal_spec.asset_decimals,
        ),
        best_case=num_from_padded_int(
            collateral_increase_estimate.best_case, decimals=decimal_spec.asset_decimals
        ),
    )


def _liquidation_estimate_from_proto(
    liquidation_estimate: data_node_protos_v2.trading_data.LiquidationEstimate,
    decimal_spec: DecimalSpec,
):
    return LiquidationEstimate(
        best_case=_liquidation_price_from_proto(
            liquidation_estimate.best_case, decimal_spec=decimal_spec
        ),
        worst_case=_liquidation_price_from_proto(
            liquidation_estimate.worst_case, decimal_spec=decimal_spec
        ),
    )


def _liquidation_price_from_proto(
    liquidation_price: data_node_protos_v2.trading_data.LiquidationPrice,
    decimal_spec: DecimalSpec,
):
    return LiquidationPrice(
        open_volume_only=num_from_padded_int(
            liquidation_price.open_volume_only, decimals=decimal_spec.asset_decimals
        ),
        including_buy_orders=num_from_padded_int(
            liquidation_price.including_buy_orders, decimals=decimal_spec.asset_decimals
        ),
        including_sell_orders=num_from_padded_int(
            liquidation_price.including_sell_orders,
            decimals=decimal_spec.asset_decimals,
        ),
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

            settlement_asset_id = (
                market_info.tradable_instrument.instrument.future.settlement_asset
            )
            if not settlement_asset_id:
                settlement_asset_id = (
                    market_info.tradable_instrument.instrument.perpetual.settlement_asset
                )
            if not settlement_asset_id:
                settlement_asset_id = (
                    market_info.tradable_instrument.instrument.spot.quote_asset
                )

            market_to_asset_map[pos.market_id] = settlement_asset_id

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
) -> MarketData:
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
        timestamp=datetime.datetime.fromtimestamp(
            market_data.timestamp / 1e9, tz=datetime.timezone.utc
        ),
        open_interest=market_data.open_interest,
        auction_end=(
            None
            if market_data.auction_end == None
            else datetime.datetime.fromtimestamp(
                market_data.auction_end / 1e9, tz=datetime.timezone.utc
            )
        ),
        auction_start=(
            None
            if market_data.auction_start == None
            else datetime.datetime.fromtimestamp(
                market_data.auction_start / 1e9, tz=datetime.timezone.utc
            )
        ),
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
        liquidity_sla=_liquidity_sla_from_proto(
            market_data.liquidity_provider_sla, decimal_spec
        ),
        market_state=market_data.market_state,
        next_mark_to_market=datetime.datetime.fromtimestamp(
            market_data.next_mark_to_market / 1e9, tz=datetime.timezone.utc
        ),
        last_traded_price=num_from_padded_int(
            market_data.last_traded_price, decimal_spec.price_decimals
        ),
        product_data=_product_data_from_proto(market_data.product_data, decimal_spec),
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
) -> List[LiquidityProviderFeeShare]:
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


def _liquidity_sla_from_proto(
    liquidity_provider_sla: List[vega_protos.vega.LiquidityProviderSLA],
    decimal_spec: DecimalSpec,
) -> List[LiquidityProviderSLA]:
    decimals = decimal_spec.asset_decimals
    return [
        LiquidityProviderSLA(
            party=individual_liquidity_provider_sla.party,
            current_epoch_fraction_of_time_on_book=(
                0
                if individual_liquidity_provider_sla.current_epoch_fraction_of_time_on_book
                == ""
                else float(
                    individual_liquidity_provider_sla.current_epoch_fraction_of_time_on_book
                )
            ),
            last_epoch_fraction_of_time_on_book=(
                0
                if individual_liquidity_provider_sla.last_epoch_fraction_of_time_on_book
                == ""
                else float(
                    individual_liquidity_provider_sla.last_epoch_fraction_of_time_on_book
                )
            ),
            last_epoch_fee_penalty=(
                0
                if individual_liquidity_provider_sla.last_epoch_fee_penalty == ""
                else float(individual_liquidity_provider_sla.last_epoch_fee_penalty)
            ),
            last_epoch_bond_penalty=(
                0
                if individual_liquidity_provider_sla.last_epoch_bond_penalty == ""
                else float(individual_liquidity_provider_sla.last_epoch_bond_penalty)
            ),
            hysteresis_period_fee_penalties=[
                float(x)
                for x in individual_liquidity_provider_sla.hysteresis_period_fee_penalties
            ],
            required_liquidity=(
                0
                if individual_liquidity_provider_sla.required_liquidity == ""
                else num_from_padded_int(
                    float(individual_liquidity_provider_sla.required_liquidity),
                    decimals,
                )
            ),
            notional_volume_buys=(
                0
                if individual_liquidity_provider_sla.notional_volume_buys == ""
                else num_from_padded_int(
                    float(individual_liquidity_provider_sla.notional_volume_buys),
                    decimals,
                )
            ),
            notional_volume_sells=(
                0
                if individual_liquidity_provider_sla.notional_volume_sells == ""
                else num_from_padded_int(
                    float(individual_liquidity_provider_sla.notional_volume_sells),
                    decimals,
                )
            ),
        )
        for individual_liquidity_provider_sla in liquidity_provider_sla
    ]


def _product_data_from_proto(
    product_data: vega_protos.vega.ProductData, decimal_spec: DecimalSpec
) -> ProductData:
    data_field = product_data.WhichOneof("data")
    if data_field is None:
        return ProductData(perpetual_data=None)
    if data_field == "perpetual_data":
        data = getattr(product_data, data_field)
        perpetual_data = PerpetualData(
            start_time=datetime.datetime.fromtimestamp(
                data.start_time / 1e9, tz=datetime.timezone.utc
            ),
            funding_payment=(
                None
                if not data.funding_payment
                else num_from_padded_int(
                    data.funding_payment, decimal_spec.asset_decimals
                )
            ),
            funding_rate=None if not data.funding_rate else float(data.funding_rate),
            internal_twap=(
                None
                if not data.internal_twap
                else num_from_padded_int(
                    data.internal_twap, decimal_spec.asset_decimals
                )
            ),
            external_twap=(
                None
                if not data.external_twap
                else num_from_padded_int(
                    data.external_twap, decimal_spec.asset_decimals
                )
            ),
        )
        return ProductData(perpetual_data=perpetual_data)
    raise Exception(f"unsupported product data type '{data_field}'")


def _account_from_proto(account, decimal_spec: DecimalSpec) -> AccountData:
    return AccountData(
        owner=account.owner,
        balance=num_from_padded_int(int(account.balance), decimal_spec.asset_decimals),
        asset=account.asset,
        type=account.type,
        market_id=account.market_id if account.market_id != "!" else "",
    )


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


def _benefit_tier_from_proto(benefit_tier: vega_protos.vega.BenefitTier) -> BenefitTier:
    return BenefitTier(
        minimum_running_notional_taker_volume=float(
            benefit_tier.minimum_running_notional_taker_volume
        ),
        minimum_epochs=int(benefit_tier.minimum_epochs),
        referral_reward_factor=(
            float(benefit_tier.referral_reward_factor)
            if benefit_tier.referral_reward_factor != ""
            else None
        ),
        referral_discount_factor=(
            float(benefit_tier.referral_discount_factor)
            if benefit_tier.referral_discount_factor != ""
            else None
        ),
        referral_reward_factors=_reward_factors_from_proto(
            reward_factors=benefit_tier.referral_reward_factors
        ),
        referral_discount_factors=_discount_factors_from_proto(
            discount_factors=benefit_tier.referral_discount_factors
        ),
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


def _referral_set_stats_from_proto(
    referral_set_stats: data_node_protos_v2.trading_data.ReferralSetStats,
) -> ReferralSetStats:
    return ReferralSetStats(
        at_epoch=referral_set_stats.at_epoch,
        referral_set_running_notional_taker_volume=int(
            referral_set_stats.referral_set_running_notional_taker_volume
        ),
        party_id=referral_set_stats.party_id,
        discount_factor=float(referral_set_stats.discount_factor),
        reward_factor=float(referral_set_stats.reward_factor),
        epoch_notional_taker_volume=int(referral_set_stats.epoch_notional_taker_volume),
    )


def _party_amount_from_proto(
    party_amount: vega_protos.events.v1.events.PartyAmount,
    decimal_spec: DecimalSpec,
) -> PartyAmount:
    return PartyAmount(
        party=party_amount.party,
        amount=num_from_padded_int(party_amount.amount, decimal_spec.asset_decimals),
    )


def _referrer_rewards_generated_from_proto(
    referrer_rewards_generated: vega_protos.events.v1.events.ReferrerRewardsGenerated,
    decimal_spec: DecimalSpec,
) -> ReferrerRewardsGenerated:
    return ReferrerRewardsGenerated(
        referrer=referrer_rewards_generated.referrer,
        generated_reward=[
            _party_amount_from_proto(
                party_amount=generated_reward,
                decimal_spec=decimal_spec,
            )
            for generated_reward in referrer_rewards_generated.generated_reward
        ],
    )


def _fees_stats_from_proto(
    fee_stats: vega_protos.events.v1.events.FeesStats, decimal_spec: DecimalSpec
):
    return FeesStats(
        market=fee_stats.market,
        asset=fee_stats.asset,
        epoch_seq=fee_stats.epoch_seq,
        total_rewards_received=[
            _party_amount_from_proto(
                party_amount=party_amount, decimal_spec=decimal_spec
            )
            for party_amount in fee_stats.total_rewards_received
        ],
        referrer_rewards_generated=[
            _referrer_rewards_generated_from_proto(
                referrer_rewards_generated=referrer_rewards_generated,
                decimal_spec=decimal_spec,
            )
            for referrer_rewards_generated in fee_stats.referrer_rewards_generated
        ],
        referees_discount_applied=[
            _party_amount_from_proto(
                party_amount=party_amount, decimal_spec=decimal_spec
            )
            for party_amount in fee_stats.referees_discount_applied
        ],
        volume_discount_applied=[
            _party_amount_from_proto(
                party_amount=party_amount, decimal_spec=decimal_spec
            )
            for party_amount in fee_stats.volume_discount_applied
        ],
        total_maker_fees_received=[
            _party_amount_from_proto(
                party_amount=party_amount, decimal_spec=decimal_spec
            )
            for party_amount in fee_stats.total_maker_fees_received
        ],
        maker_fees_generated=[
            _maker_fees_generated_from_proto(
                maker_fees_generated=maker_fees_generated,
                decimal_spec=decimal_spec,
            )
            for maker_fees_generated in fee_stats.maker_fees_generated
        ],
    )


def _volume_benefit_tier_from_proto(
    volume_benefit_tier: vega_protos.vega.VolumeBenefitTier,
) -> VolumeBenefitTier:
    return VolumeBenefitTier(
        minimum_running_notional_taker_volume=float(
            volume_benefit_tier.minimum_running_notional_taker_volume
        ),
        volume_discount_factor=(
            float(volume_benefit_tier.volume_discount_factor)
            if volume_benefit_tier.volume_discount_factor != ""
            else None
        ),
        volume_discount_factors=_discount_factors_from_proto(
            volume_benefit_tier.volume_discount_factors
        ),
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


def _volume_discount_stats_from_proto(
    volume_discount_stats: data_node_protos_v2.trading_data.VolumeDiscountStats,
) -> VolumeDiscountStats:
    return VolumeDiscountStats(
        at_epoch=int(volume_discount_stats.at_epoch),
        party_id=str(volume_discount_stats.party_id),
        discount_factor=(
            float(volume_discount_stats.discount_factor)
            if volume_discount_stats.discount_factor != ""
            else None
        ),
        running_volume=float(volume_discount_stats.running_volume),
        discount_factors=_discount_factors_from_proto(
            volume_discount_stats.discount_factors
        ),
    )


def _team_from_proto(team: data_node_protos_v2.trading_data.Team) -> Team:
    return Team(
        team_id=team.team_id,
        referrer=team.referrer,
        name=team.name,
        team_url=team.team_url,
        avatar_url=team.avatar_url,
        created_at=team.created_at,
        closed=team.closed,
        created_at_epoch=team.created_at_epoch,
    )


def _team_referee_from_proto(
    team_referee: data_node_protos_v2.trading_data.TeamReferee,
) -> TeamReferee:
    return TeamReferee(
        team_id=team_referee.team_id,
        referee=team_referee.referee,
        joined_at=team_referee.joined_at,
        joined_at_epoch=team_referee.joined_at_epoch,
    )


def _team_referee_history_from_proto(
    team_referee_history: data_node_protos_v2.trading_data.TeamRefereeHistory,
) -> TeamRefereeHistory:
    return TeamRefereeHistory(
        team_id=team_referee_history.team_id,
        joined_at=team_referee_history.joined_at,
        joined_at_epoch=team_referee_history.joined_at_epoch,
    )


@dataclass(frozen=True)
class ConcentratedLiquidityParameters:
    base: float
    lower_bound: float
    upper_bound: float
    leverage_at_upper_bound: float
    leverage_at_lower_bound: float


def _concentrated_liquidity_parameters_from_proto(
    concentrated_liquidity_parameters: vega_protos.events.v1.events.AMM.ConcentratedLiquidityParameters,
    decimal_spec: DecimalSpec,
) -> ConcentratedLiquidityParameters:
    return ConcentratedLiquidityParameters(
        base=num_from_padded_int(
            concentrated_liquidity_parameters.base, decimal_spec.price_decimals
        ),
        lower_bound=num_from_padded_int(
            concentrated_liquidity_parameters.lower_bound, decimal_spec.price_decimals
        ),
        upper_bound=num_from_padded_int(
            concentrated_liquidity_parameters.upper_bound, decimal_spec.price_decimals
        ),
        leverage_at_upper_bound=float(
            concentrated_liquidity_parameters.leverage_at_upper_bound
        ),
        leverage_at_lower_bound=float(
            concentrated_liquidity_parameters.leverage_at_lower_bound
        ),
    )


@dataclass(frozen=True)
class AMM:
    id: str
    party_id: str
    market_id: str
    amm_party_id: str
    commitment: float
    parameters: vega_protos.events.v1.events.AMM.ConcentratedLiquidityParameters
    status: vega_protos.events.v1.events.AMM.Status
    status_reason: vega_protos.events.v1.events.AMM.StatusReason


def _amm_from_proto(
    amm: vega_protos.events.v1.events.AMM, decimal_spec: DecimalSpec
) -> AMM:
    return AMM(
        id=amm.id,
        party_id=amm.party_id,
        market_id=amm.market_id,
        amm_party_id=amm.amm_party_id,
        commitment=num_from_padded_int(amm.commitment, decimal_spec.asset_decimals),
        parameters=_concentrated_liquidity_parameters_from_proto(
            amm.parameters, decimal_spec
        ),
        status=amm.status,
        status_reason=amm.status_reason,
    )


def _reward_factors_from_proto(
    reward_factors: vega_protos.vega.RewardFactors,
) -> RewardFactors:
    return RewardFactors(
        infrastructure_reward_factor=float(reward_factors.infrastructure_reward_factor),
        liquidity_reward_factor=float(reward_factors.liquidity_reward_factor),
        maker_reward_factor=float(reward_factors.maker_reward_factor),
    )


def _discount_factors_from_proto(
    discount_factors: vega_protos.vega.DiscountFactors,
) -> DiscountFactors:
    return DiscountFactors(
        infrastructure_discount_factor=float(
            discount_factors.infrastructure_discount_factor
        ),
        liquidity_discount_factor=float(discount_factors.liquidity_discount_factor),
        maker_discount_factor=float(discount_factors.maker_discount_factor),
    )


def list_accounts(
    data_client: vac.VegaTradingDataClientV2,
    pub_key: Optional[str] = None,
    asset_id: Optional[str] = None,
    market_id: Optional[str] = None,
    account_types: Optional[vega_protos.vega.AccountType] = None,
    asset_decimals_map: Optional[Dict[str, int]] = None,
) -> List[AccountData]:
    """Output money in general accounts/margin accounts/bond accounts (if exists)
    of a party."""
    accounts = data_raw.list_accounts(
        data_client=data_client,
        party_id=pub_key,
        asset_id=asset_id,
        account_types=account_types,
        market_id=market_id,
    )

    asset_decimals_map = {} if asset_decimals_map is None else asset_decimals_map
    output_accounts = []
    for account in accounts:
        if not is_valid_vega_id(account.asset):
            continue

        if account.asset not in asset_decimals_map:
            asset_decimals_map[account.asset] = get_asset_decimals(
                asset_id=account.asset,
                data_client=data_client,
            )

        output_accounts.append(
            _account_from_proto(
                account, DecimalSpec(asset_decimals=asset_decimals_map[account.asset])
            )
        )
    return output_accounts


def is_valid_vega_id(resource_id: str) -> bool:
    return len(resource_id) == 64 and all(c in string.hexdigits for c in resource_id)


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

    return account_list_to_party_account(
        [
            account
            for account in accounts
            if account.market_id is None
            or account.market_id == ""
            or account.market_id == market_id
        ],
        asset_dp_conversion=asset_dp,
    )


def account_list_to_party_account(
    accounts: Union[
        List[data_node_protos_v2.trading_data.AccountBalance], List[AccountData]
    ],
    asset_dp_conversion: Optional[int] = None,
):
    general, margin, bond = 0, 0, 0  # np.nan, np.nan, np.nan
    for account in accounts:
        if account.type == vega_protos.vega.ACCOUNT_TYPE_GENERAL:
            general = (
                num_from_padded_int(float(account.balance), asset_dp_conversion)
                if asset_dp_conversion is not None
                else account.balance
            )
        if account.type == vega_protos.vega.ACCOUNT_TYPE_MARGIN:
            margin = (
                num_from_padded_int(float(account.balance), asset_dp_conversion)
                if asset_dp_conversion is not None
                else account.balance
            )
        if account.type == vega_protos.vega.ACCOUNT_TYPE_BOND:
            bond = (
                num_from_padded_int(float(account.balance), asset_dp_conversion)
                if asset_dp_conversion is not None
                else account.balance
            )

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
            market_info = data_raw.market_info(
                market_id=market_id, data_client=data_client
            )
            settlement_asset_id = (
                market_info.tradable_instrument.instrument.future.settlement_asset
            )
            if not settlement_asset_id:
                settlement_asset_id = (
                    market_info.tradable_instrument.instrument.perpetual.settlement_asset
                )

            market_asset_decimals_map[trade.market_id] = get_asset_decimals(
                asset_id=settlement_asset_id,
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
    direction: Optional[data_node_protos_v2.trading_data.TransferDirection] = None,
    is_reward: Optional[bool] = None,
    from_epoch: Optional[int] = None,
    to_epoch: Optional[int] = None,
    status: Optional[vega_protos.events.v1.events.Transfer.Status] = None,
    scope: Optional[data_node_protos_v2.trading_data.ListTransfersRequest.Scope] = None,
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

    transfer_nodes = data_raw.list_transfers(
        data_client=data_client,
        party_id=party_id,
        direction=direction,
        is_reward=is_reward,
        from_epoch=from_epoch,
        to_epoch=to_epoch,
        status=status,
        scope=scope,
    )

    asset_dp = {}
    res_transfers = []

    for transfer_node in transfer_nodes:
        transfer = transfer_node.transfer

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
    market_id = None if market_id == "!" else market_id

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


def accounts_subscription_handler(
    stream: Iterable[vega_protos.api.v1.core.ObserveEventBusResponse],
    mkt_pos_dp: Optional[Dict[str, int]] = None,
    mkt_price_dp: Optional[Dict[str, int]] = None,
    mkt_to_asset: Optional[Dict[str, str]] = None,
    asset_dp: Optional[Dict[str, int]] = None,
) -> Transfer:
    return _stream_handler(
        stream_item=stream,
        extraction_fn=lambda evt: evt.account,
        conversion_fn=_account_from_proto,
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


def network_parameter_handler(
    stream: Iterable[vega_protos.api.v1.core.ObserveEventBusResponse],
) -> Transfer:
    return _stream_handler(
        stream_item=stream,
        extraction_fn=lambda evt: evt.network_parameter,
        conversion_fn=_network_parameter_from_proto,
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
        market_info = data_raw.market_info(market_id=market_id, data_client=data_client)
        settlement_asset_id = (
            market_info.tradable_instrument.instrument.future.settlement_asset
        )
        if not settlement_asset_id:
            settlement_asset_id = (
                market_info.tradable_instrument.instrument.perpetual.settlement_asset
            )
        if not settlement_asset_id:
            settlement_asset_id = (
                market_info.tradable_instrument.instrument.spot.quote_asset
            )

        market_to_asset_map[market_id] = settlement_asset_id
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


def get_market_data_history(
    market_id: str,
    data_client: vac.VegaTradingDataClientV2,
    start: Optional[datetime.datetime] = None,
    end: Optional[datetime.datetime] = None,
    market_price_decimals_map: Optional[Dict[str, int]] = None,
    market_position_decimals_map: Optional[Dict[str, int]] = None,
    market_to_asset_map: Optional[Dict[str, str]] = None,
    asset_decimals_map: Optional[Dict[str, int]] = None,
) -> MarketData:
    # Get market data history
    market_data_history = data_raw.market_data_history(
        market_id=market_id, start=start, end=end, data_client=data_client
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
        market_info = data_raw.market_info(market_id=market_id, data_client=data_client)
        settlement_asset_id = (
            market_info.tradable_instrument.instrument.future.settlement_asset
        )
        if not settlement_asset_id:
            settlement_asset_id = (
                market_info.tradable_instrument.instrument.perpetual.settlement_asset
            )
        if not settlement_asset_id:
            settlement_asset_id = (
                market_info.tradable_instrument.instrument.spot.quote_asset
            )

        market_to_asset_map[market_id] = settlement_asset_id
    if market_to_asset_map[market_id] not in asset_decimals_map:
        asset_decimals_map[market_to_asset_map[market_id]] = get_asset_decimals(
            asset_id=market_to_asset_map[market_id],
            data_client=data_client,
        )
    # Convert from proto
    return [
        _market_data_from_proto(
            market_data=market_data,
            decimal_spec=DecimalSpec(
                price_decimals=market_price_decimals_map[market_data.market],
                position_decimals=market_position_decimals_map[market_data.market],
                asset_decimals=asset_decimals_map[
                    market_to_asset_map[market_data.market]
                ],
            ),
        )
        for market_data in market_data_history
    ]


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
    average_entry_price: int,
    margin_account_balance: int,
    general_account_balance: int,
    order_margin_account_balance: int,
    margin_mode: vega_protos.vega.MarginMode,
    orders: Optional[List[Tuple[str, str, int, bool]]] = None,
    margin_factor: Optional[float] = None,
    include_required_position_margin_in_available_collateral: bool = True,
    scale_liquidation_price_to_market_decimals: bool = False,
    asset_decimals: Optional[Dict[str, int]] = {},
) -> Tuple[
    MarginEstimate,
    LiquidationEstimate,
]:
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

    (
        margin_estimate,
        collateral_increase_estimate,
        liquidation_estimate,
    ) = data_raw.estimate_position(
        data_client=data_client,
        market_id=market_id,
        open_volume=open_volume,
        average_entry_price=average_entry_price,
        margin_account_balance=margin_account_balance,
        general_account_balance=general_account_balance,
        order_margin_account_balance=order_margin_account_balance,
        margin_mode=margin_mode,
        orders=proto_orders if orders is not None else None,
        margin_factor=margin_factor,
        include_required_position_margin_in_available_collateral=include_required_position_margin_in_available_collateral,
        scale_liquidation_price_to_market_decimals=scale_liquidation_price_to_market_decimals,
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

    converted_collateral_increase_estimate = _collateral_increase_estimate_from_proto(
        collateral_increase_estimate=collateral_increase_estimate,
        decimal_spec=DecimalSpec(
            asset_decimals=asset_decimals[margin_estimate.best_case.asset]
        ),
    )

    converted_liquidation_estimate = _liquidation_estimate_from_proto(
        liquidation_estimate=liquidation_estimate,
        decimal_spec=DecimalSpec(
            asset_decimals=asset_decimals[margin_estimate.best_case.asset]
        ),
    )

    return (
        converted_margin_estimate,
        converted_collateral_increase_estimate,
        converted_liquidation_estimate,
    )


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
) -> Asset:
    asset = data_raw.asset_info(data_client=data_client, asset_id=asset_id)
    return _asset_from_proto(
        asset, decimal_spec=DecimalSpec(asset_decimals=asset.details.decimals)
    )


def list_referral_sets(
    data_client: vac.trading_data_grpc_v2,
    referral_set_id: Optional[str] = None,
    referrer: Optional[str] = None,
    referee: Optional[str] = None,
) -> Dict[str, ReferralSet]:
    response: List[data_node_protos_v2.trading_data.ReferralSet] = (
        data_raw.list_referral_sets(
            data_client=data_client,
            referral_set_id=referral_set_id,
            referrer=referrer,
            referee=referee,
        )
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
    response: List[data_node_protos_v2.trading_data.ReferralSetReferee] = (
        data_raw.list_referral_set_referees(
            data_client=data_client,
            referral_set_id=referral_set_id,
            referrer=referrer,
            referee=referee,
        )
    )
    referral_set_referees = defaultdict(dict)
    for referral_set_referee in response:
        referral_set_referees[referral_set_referee.referral_set_id][
            referral_set_referee.referee
        ] = _referral_set_referee_from_proto(referral_set_referee)
    return referral_set_referees


def get_referral_set_stats(
    data_client: vac.trading_data_grpc_v2,
    at_epoch: Optional[int] = None,
    referee: Optional[str] = None,
) -> Dict[str, ReferralSetStats]:
    response = data_raw.get_referral_set_stats(
        data_client=data_client, at_epoch=at_epoch, referee=referee
    )
    return [
        _referral_set_stats_from_proto(referral_set_stats=referral_set_stats)
        for referral_set_stats in response
    ]


def get_fees_stats(
    data_client: vac.trading_data_grpc_v2,
    market_id: Optional[str] = None,
    asset_id: Optional[str] = None,
    epoch_seq: Optional[int] = None,
    party_id: Optional[str] = None,
    asset_decimals: Optional[Dict[str, int]] = {},
) -> List[FeesStats]:
    response = data_raw.get_fees_stats(
        data_client=data_client,
        market_id=market_id,
        asset_id=asset_id,
        epoch_seq=epoch_seq,
        party_id=party_id,
    )
    return _fees_stats_from_proto(
        fee_stats=response,
        decimal_spec=DecimalSpec(asset_decimals=asset_decimals[response.asset]),
    )


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


def dispatch_strategy(
    metric: vega_protos.vega.DispatchMetric,
    asset_for_metric: Optional[str] = None,
    markets: Optional[List[str]] = None,
    entity_scope: Optional[vega_protos.vega.EntityScope] = None,
    individual_scope: Optional[vega_protos.vega.IndividualScope] = None,
    team_scope: Optional[List[str]] = None,
    n_top_performers: Optional[float] = None,
    staking_requirement: Optional[float] = None,
    notional_time_weighted_average_position_requirement: Optional[float] = None,
    window_length: Optional[int] = None,
    lock_period: Optional[int] = None,
    distribution_strategy: Optional[vega_protos.vega.DistributionStrategy] = None,
    rank_table: Optional[List[vega_protos.vega.Rank]] = None,
    cap_reward_fee_multiple: Optional[float] = None,
    transfer_interval: Optional[int] = None,
) -> vega_protos.vega.DispatchStrategy:
    # Set defaults for mandatory fields
    if entity_scope is None:
        entity_scope = vega_protos.vega.ENTITY_SCOPE_INDIVIDUALS
    if individual_scope is None:
        individual_scope = vega_protos.vega.INDIVIDUAL_SCOPE_ALL
    if distribution_strategy is None:
        distribution_strategy = vega_protos.vega.DISTRIBUTION_STRATEGY_PRO_RATA
    if window_length is None:
        window_length = 1
    if lock_period is None:
        lock_period = 1

    # Set the mandatory (and conditionally mandatory) DispatchStrategy fields
    dispatch_strategy = vega_protos.vega.DispatchStrategy(
        asset_for_metric=(
            None
            if metric in [vega_protos.vega.DISPATCH_METRIC_VALIDATOR_RANKING]
            else asset_for_metric
        ),
        entity_scope=entity_scope,
        individual_scope=(
            individual_scope
            if entity_scope == vega_protos.vega.ENTITY_SCOPE_INDIVIDUALS
            else None
        ),
        window_length=(
            None
            if metric in [vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE]
            else window_length
        ),
        lock_period=lock_period,
        distribution_strategy=(
            None
            if metric in [vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE]
            else distribution_strategy
        ),
        n_top_performers=(
            str(n_top_performers)
            if entity_scope == vega_protos.vega.ENTITY_SCOPE_TEAMS
            else None
        ),
        cap_reward_fee_multiple=(
            str(cap_reward_fee_multiple)
            if cap_reward_fee_multiple is not None
            else None
        ),
        transfer_interval=transfer_interval,
    )
    # Set the optional DispatchStrategy fields
    if metric is not None:
        setattr(dispatch_strategy, "metric", metric)
    if staking_requirement is not None:
        setattr(dispatch_strategy, "staking_requirement", str(staking_requirement))
    if notional_time_weighted_average_position_requirement is not None:
        setattr(
            dispatch_strategy,
            "notional_time_weighted_average_position_requirement",
            str(notional_time_weighted_average_position_requirement),
        )
    if markets is not None:
        dispatch_strategy.markets.extend(markets)
    if team_scope is not None:
        dispatch_strategy.team_scope.extend(team_scope)
    if rank_table is not None:
        dispatch_strategy.rank_table.extend(rank_table)
    return dispatch_strategy


def list_teams(
    data_client: vac.trading_data_grpc_v2,
    team_id: Optional[str] = None,
    party_id: Optional[str] = None,
) -> Dict[str, Team]:
    response = data_raw.list_teams(
        data_client=data_client, team_id=team_id, party_id=party_id
    )
    return {team.team_id: _team_from_proto(team=team) for team in response}


def list_team_referees(
    data_client: vac.trading_data_grpc_v2,
    team_id: Optional[str] = None,
) -> List[TeamReferee]:
    response = data_raw.list_team_referees(data_client=data_client, team_id=team_id)
    return [
        _team_referee_from_proto(team_referee=team_referee) for team_referee in response
    ]


def list_team_referee_history(
    data_client: vac.trading_data_grpc_v2,
    referee: Optional[str] = None,
) -> List[TeamRefereeHistory]:
    response = data_raw.list_team_referee_history(
        data_client=data_client, referee=referee
    )
    return [
        _team_referee_history_from_proto(team_referee_history=team_referee_history)
        for team_referee_history in response
    ]


def list_stop_orders(
    data_client: vac.trading_data_grpc_v2,
    statuses: Optional[List[vega_protos.vega.StopOrder.Status]] = None,
    expiry_strategies: Optional[
        List[vega_protos.vega.StopOrder.ExpiryStrategies]
    ] = None,
    date_range: Optional[vega_protos.vega.DateRange] = None,
    party_ids: Optional[List[str]] = None,
    market_ids: Optional[List[str]] = None,
    live_only: Optional[bool] = None,
    market_price_decimals_map: Optional[Dict[str, int]] = None,
    market_position_decimals_map: Optional[Dict[str, int]] = None,
):
    response = data_raw.list_stop_orders(
        data_client=data_client,
        statuses=statuses,
        expiry_strategies=expiry_strategies,
        date_range=date_range,
        party_ids=party_ids,
        market_ids=market_ids,
        live_only=live_only,
    )
    return [
        _stop_order_event_from_proto(
            stop_order_event,
            DecimalSpec(
                price_decimals=market_price_decimals_map[
                    stop_order_event.submission.market_id
                ],
                position_decimals=market_position_decimals_map[
                    stop_order_event.submission.market_id
                ],
            ),
        )
        for stop_order_event in response
    ]


def list_network_parameters(
    data_client: vac.trading_data_grpc_v2,
) -> List[NetworkParameter]:
    response = data_raw.list_network_parameters(data_client=data_client)
    return [
        _network_parameter_from_proto(network_parameter=proto) for proto in response
    ]


def list_all_positions(
    data_client: vac.VegaTradingDataClientV2,
    party_ids: Optional[List[str]] = None,
    market_ids: Optional[List[str]] = None,
    market_price_decimals_map: Optional[Dict[str, int]] = None,
    market_position_decimals_map: Optional[Dict[str, int]] = None,
    market_to_asset_map: Optional[Dict[str, str]] = None,
    asset_decimals_map: Optional[Dict[str, int]] = None,
) -> List[vega_protos.vega.Position]:
    response = data_raw.list_all_positions(
        data_client=data_client, party_ids=party_ids, market_ids=market_ids
    )
    positions = []
    for position in response:
        positions.append(
            _position_from_proto(
                position=position,
                decimal_spec=DecimalSpec(
                    price_decimals=market_price_decimals_map[position.market_id],
                    position_decimals=market_position_decimals_map[position.market_id],
                    asset_decimals=asset_decimals_map[
                        market_to_asset_map[position.market_id]
                    ],
                ),
            )
        )
    return positions


def list_funding_periods(
    data_client: vac.trading_data_grpc_v2,
    market_id: str,
    start: Optional[datetime.datetime] = None,
    end: Optional[datetime.datetime] = None,
    market_to_asset_map: Optional[Dict[str, str]] = None,
    asset_decimals_map: Optional[Dict[str, int]] = None,
) -> List[FundingPeriod]:
    response = data_raw.list_funding_periods(
        data_client=data_client, market_id=market_id, start=start, end=end
    )
    decimal_spec = DecimalSpec(
        asset_decimals=asset_decimals_map[market_to_asset_map[market_id]],
    )
    return [
        _funding_period_from_proto(funding_period=proto, decimal_spec=decimal_spec)
        for proto in response
    ]


def list_party_margin_modes(
    data_client: vac.trading_data_grpc_v2,
    market_id: Optional[str] = None,
    party_id: Optional[str] = None,
):
    return [
        _party_margin_mode_from_proto(proto)
        for proto in data_raw.list_party_margin_modes(
            data_client=data_client, market_id=market_id, party_id=party_id
        )
    ]


def list_amms(
    data_client: vac.trading_data_grpc_v2,
    price_decimals_map: Dict[str, int],
    asset_decimals_map: Dict[str, int],
    market_to_asset_map: Dict[str, str],
    market_id: Optional[str] = None,
    party_id: Optional[str] = None,
    amm_party_id: Optional[str] = None,
    status: Optional[vega_protos.events.v1.events.AMM.Status.Value] = None,
) -> List[AMM]:
    amms = data_raw.list_amms(
        data_client=data_client,
        market_id=market_id,
        party_id=party_id,
        amm_party_id=amm_party_id,
        status=status,
    )
    return [
        _amm_from_proto(
            amm,
            DecimalSpec(
                price_decimals=price_decimals_map[amm.market_id],
                asset_decimals=asset_decimals_map[market_to_asset_map[amm.market_id]],
            ),
        )
        for amm in amms
    ]
