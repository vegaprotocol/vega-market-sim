from vega import markets_pb2 as _markets_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class Side(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIDE_UNSPECIFIED: _ClassVar[Side]
    SIDE_BUY: _ClassVar[Side]
    SIDE_SELL: _ClassVar[Side]

class Interval(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INTERVAL_UNSPECIFIED: _ClassVar[Interval]
    INTERVAL_BLOCK: _ClassVar[Interval]
    INTERVAL_I1M: _ClassVar[Interval]
    INTERVAL_I5M: _ClassVar[Interval]
    INTERVAL_I15M: _ClassVar[Interval]
    INTERVAL_I30M: _ClassVar[Interval]
    INTERVAL_I1H: _ClassVar[Interval]
    INTERVAL_I4H: _ClassVar[Interval]
    INTERVAL_I6H: _ClassVar[Interval]
    INTERVAL_I8H: _ClassVar[Interval]
    INTERVAL_I12H: _ClassVar[Interval]
    INTERVAL_I1D: _ClassVar[Interval]
    INTERVAL_I7D: _ClassVar[Interval]

class PositionStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    POSITION_STATUS_UNSPECIFIED: _ClassVar[PositionStatus]
    POSITION_STATUS_ORDERS_CLOSED: _ClassVar[PositionStatus]
    POSITION_STATUS_CLOSED_OUT: _ClassVar[PositionStatus]
    POSITION_STATUS_DISTRESSED: _ClassVar[PositionStatus]

class AuctionTrigger(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUCTION_TRIGGER_UNSPECIFIED: _ClassVar[AuctionTrigger]
    AUCTION_TRIGGER_BATCH: _ClassVar[AuctionTrigger]
    AUCTION_TRIGGER_OPENING: _ClassVar[AuctionTrigger]
    AUCTION_TRIGGER_PRICE: _ClassVar[AuctionTrigger]
    AUCTION_TRIGGER_LIQUIDITY: _ClassVar[AuctionTrigger]
    AUCTION_TRIGGER_LIQUIDITY_TARGET_NOT_MET: _ClassVar[AuctionTrigger]
    AUCTION_TRIGGER_UNABLE_TO_DEPLOY_LP_ORDERS: _ClassVar[AuctionTrigger]
    AUCTION_TRIGGER_GOVERNANCE_SUSPENSION: _ClassVar[AuctionTrigger]
    AUCTION_TRIGGER_LONG_BLOCK: _ClassVar[AuctionTrigger]
    AUCTION_TRIGGER_PROTOCOL_AUTOMATED_PURCHASE: _ClassVar[AuctionTrigger]

class PeggedReference(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PEGGED_REFERENCE_UNSPECIFIED: _ClassVar[PeggedReference]
    PEGGED_REFERENCE_MID: _ClassVar[PeggedReference]
    PEGGED_REFERENCE_BEST_BID: _ClassVar[PeggedReference]
    PEGGED_REFERENCE_BEST_ASK: _ClassVar[PeggedReference]

class OrderError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_ERROR_UNSPECIFIED: _ClassVar[OrderError]
    ORDER_ERROR_INVALID_MARKET_ID: _ClassVar[OrderError]
    ORDER_ERROR_INVALID_ORDER_ID: _ClassVar[OrderError]
    ORDER_ERROR_OUT_OF_SEQUENCE: _ClassVar[OrderError]
    ORDER_ERROR_INVALID_REMAINING_SIZE: _ClassVar[OrderError]
    ORDER_ERROR_TIME_FAILURE: _ClassVar[OrderError]
    ORDER_ERROR_REMOVAL_FAILURE: _ClassVar[OrderError]
    ORDER_ERROR_INVALID_EXPIRATION_DATETIME: _ClassVar[OrderError]
    ORDER_ERROR_INVALID_ORDER_REFERENCE: _ClassVar[OrderError]
    ORDER_ERROR_EDIT_NOT_ALLOWED: _ClassVar[OrderError]
    ORDER_ERROR_AMEND_FAILURE: _ClassVar[OrderError]
    ORDER_ERROR_NOT_FOUND: _ClassVar[OrderError]
    ORDER_ERROR_INVALID_PARTY_ID: _ClassVar[OrderError]
    ORDER_ERROR_MARKET_CLOSED: _ClassVar[OrderError]
    ORDER_ERROR_MARGIN_CHECK_FAILED: _ClassVar[OrderError]
    ORDER_ERROR_MISSING_GENERAL_ACCOUNT: _ClassVar[OrderError]
    ORDER_ERROR_INTERNAL_ERROR: _ClassVar[OrderError]
    ORDER_ERROR_INVALID_SIZE: _ClassVar[OrderError]
    ORDER_ERROR_INVALID_PERSISTENCE: _ClassVar[OrderError]
    ORDER_ERROR_INVALID_TYPE: _ClassVar[OrderError]
    ORDER_ERROR_SELF_TRADING: _ClassVar[OrderError]
    ORDER_ERROR_INSUFFICIENT_FUNDS_TO_PAY_FEES: _ClassVar[OrderError]
    ORDER_ERROR_INCORRECT_MARKET_TYPE: _ClassVar[OrderError]
    ORDER_ERROR_INVALID_TIME_IN_FORCE: _ClassVar[OrderError]
    ORDER_ERROR_CANNOT_SEND_GFN_ORDER_DURING_AN_AUCTION: _ClassVar[OrderError]
    ORDER_ERROR_CANNOT_SEND_GFA_ORDER_DURING_CONTINUOUS_TRADING: _ClassVar[OrderError]
    ORDER_ERROR_CANNOT_AMEND_TO_GTT_WITHOUT_EXPIRYAT: _ClassVar[OrderError]
    ORDER_ERROR_EXPIRYAT_BEFORE_CREATEDAT: _ClassVar[OrderError]
    ORDER_ERROR_CANNOT_HAVE_GTC_AND_EXPIRYAT: _ClassVar[OrderError]
    ORDER_ERROR_CANNOT_AMEND_TO_FOK_OR_IOC: _ClassVar[OrderError]
    ORDER_ERROR_CANNOT_AMEND_TO_GFA_OR_GFN: _ClassVar[OrderError]
    ORDER_ERROR_CANNOT_AMEND_FROM_GFA_OR_GFN: _ClassVar[OrderError]
    ORDER_ERROR_CANNOT_SEND_IOC_ORDER_DURING_AUCTION: _ClassVar[OrderError]
    ORDER_ERROR_CANNOT_SEND_FOK_ORDER_DURING_AUCTION: _ClassVar[OrderError]
    ORDER_ERROR_MUST_BE_LIMIT_ORDER: _ClassVar[OrderError]
    ORDER_ERROR_MUST_BE_GTT_OR_GTC: _ClassVar[OrderError]
    ORDER_ERROR_WITHOUT_REFERENCE_PRICE: _ClassVar[OrderError]
    ORDER_ERROR_BUY_CANNOT_REFERENCE_BEST_ASK_PRICE: _ClassVar[OrderError]
    ORDER_ERROR_OFFSET_MUST_BE_GREATER_OR_EQUAL_TO_ZERO: _ClassVar[OrderError]
    ORDER_ERROR_SELL_CANNOT_REFERENCE_BEST_BID_PRICE: _ClassVar[OrderError]
    ORDER_ERROR_OFFSET_MUST_BE_GREATER_THAN_ZERO: _ClassVar[OrderError]
    ORDER_ERROR_INSUFFICIENT_ASSET_BALANCE: _ClassVar[OrderError]
    ORDER_ERROR_CANNOT_AMEND_PEGGED_ORDER_DETAILS_ON_NON_PEGGED_ORDER: _ClassVar[
        OrderError
    ]
    ORDER_ERROR_UNABLE_TO_REPRICE_PEGGED_ORDER: _ClassVar[OrderError]
    ORDER_ERROR_UNABLE_TO_AMEND_PRICE_ON_PEGGED_ORDER: _ClassVar[OrderError]
    ORDER_ERROR_NON_PERSISTENT_ORDER_OUT_OF_PRICE_BOUNDS: _ClassVar[OrderError]
    ORDER_ERROR_TOO_MANY_PEGGED_ORDERS: _ClassVar[OrderError]
    ORDER_ERROR_POST_ONLY_ORDER_WOULD_TRADE: _ClassVar[OrderError]
    ORDER_ERROR_REDUCE_ONLY_ORDER_WOULD_NOT_REDUCE_POSITION: _ClassVar[OrderError]
    ORDER_ERROR_ISOLATED_MARGIN_CHECK_FAILED: _ClassVar[OrderError]
    ORDER_ERROR_PEGGED_ORDERS_NOT_ALLOWED_IN_ISOLATED_MARGIN_MODE: _ClassVar[OrderError]
    ORDER_ERROR_PRICE_NOT_IN_TICK_SIZE: _ClassVar[OrderError]
    ORDER_ERROR_PRICE_MUST_BE_LESS_THAN_OR_EQUAL_TO_MAX_PRICE: _ClassVar[OrderError]
    ORDER_ERROR_SELL_ORDER_NOT_ALLOWED: _ClassVar[OrderError]

class ChainStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHAIN_STATUS_UNSPECIFIED: _ClassVar[ChainStatus]
    CHAIN_STATUS_DISCONNECTED: _ClassVar[ChainStatus]
    CHAIN_STATUS_REPLAYING: _ClassVar[ChainStatus]
    CHAIN_STATUS_CONNECTED: _ClassVar[ChainStatus]

class AccountType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACCOUNT_TYPE_UNSPECIFIED: _ClassVar[AccountType]
    ACCOUNT_TYPE_INSURANCE: _ClassVar[AccountType]
    ACCOUNT_TYPE_SETTLEMENT: _ClassVar[AccountType]
    ACCOUNT_TYPE_MARGIN: _ClassVar[AccountType]
    ACCOUNT_TYPE_GENERAL: _ClassVar[AccountType]
    ACCOUNT_TYPE_FEES_INFRASTRUCTURE: _ClassVar[AccountType]
    ACCOUNT_TYPE_FEES_LIQUIDITY: _ClassVar[AccountType]
    ACCOUNT_TYPE_FEES_MAKER: _ClassVar[AccountType]
    ACCOUNT_TYPE_BOND: _ClassVar[AccountType]
    ACCOUNT_TYPE_EXTERNAL: _ClassVar[AccountType]
    ACCOUNT_TYPE_GLOBAL_INSURANCE: _ClassVar[AccountType]
    ACCOUNT_TYPE_GLOBAL_REWARD: _ClassVar[AccountType]
    ACCOUNT_TYPE_PENDING_TRANSFERS: _ClassVar[AccountType]
    ACCOUNT_TYPE_REWARD_MAKER_PAID_FEES: _ClassVar[AccountType]
    ACCOUNT_TYPE_REWARD_MAKER_RECEIVED_FEES: _ClassVar[AccountType]
    ACCOUNT_TYPE_REWARD_LP_RECEIVED_FEES: _ClassVar[AccountType]
    ACCOUNT_TYPE_REWARD_MARKET_PROPOSERS: _ClassVar[AccountType]
    ACCOUNT_TYPE_HOLDING: _ClassVar[AccountType]
    ACCOUNT_TYPE_LP_LIQUIDITY_FEES: _ClassVar[AccountType]
    ACCOUNT_TYPE_LIQUIDITY_FEES_BONUS_DISTRIBUTION: _ClassVar[AccountType]
    ACCOUNT_TYPE_NETWORK_TREASURY: _ClassVar[AccountType]
    ACCOUNT_TYPE_VESTING_REWARDS: _ClassVar[AccountType]
    ACCOUNT_TYPE_VESTED_REWARDS: _ClassVar[AccountType]
    ACCOUNT_TYPE_REWARD_RELATIVE_RETURN: _ClassVar[AccountType]
    ACCOUNT_TYPE_REWARD_RETURN_VOLATILITY: _ClassVar[AccountType]
    ACCOUNT_TYPE_REWARD_VALIDATOR_RANKING: _ClassVar[AccountType]
    ACCOUNT_TYPE_PENDING_FEE_REFERRAL_REWARD: _ClassVar[AccountType]
    ACCOUNT_TYPE_ORDER_MARGIN: _ClassVar[AccountType]
    ACCOUNT_TYPE_REWARD_REALISED_RETURN: _ClassVar[AccountType]
    ACCOUNT_TYPE_BUY_BACK_FEES: _ClassVar[AccountType]
    ACCOUNT_TYPE_REWARD_AVERAGE_NOTIONAL: _ClassVar[AccountType]
    ACCOUNT_TYPE_REWARD_ELIGIBLE_ENTITIES: _ClassVar[AccountType]

class TransferType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRANSFER_TYPE_UNSPECIFIED: _ClassVar[TransferType]
    TRANSFER_TYPE_LOSS: _ClassVar[TransferType]
    TRANSFER_TYPE_WIN: _ClassVar[TransferType]
    TRANSFER_TYPE_MTM_LOSS: _ClassVar[TransferType]
    TRANSFER_TYPE_MTM_WIN: _ClassVar[TransferType]
    TRANSFER_TYPE_MARGIN_LOW: _ClassVar[TransferType]
    TRANSFER_TYPE_MARGIN_HIGH: _ClassVar[TransferType]
    TRANSFER_TYPE_MARGIN_CONFISCATED: _ClassVar[TransferType]
    TRANSFER_TYPE_MAKER_FEE_PAY: _ClassVar[TransferType]
    TRANSFER_TYPE_MAKER_FEE_RECEIVE: _ClassVar[TransferType]
    TRANSFER_TYPE_INFRASTRUCTURE_FEE_PAY: _ClassVar[TransferType]
    TRANSFER_TYPE_INFRASTRUCTURE_FEE_DISTRIBUTE: _ClassVar[TransferType]
    TRANSFER_TYPE_LIQUIDITY_FEE_PAY: _ClassVar[TransferType]
    TRANSFER_TYPE_LIQUIDITY_FEE_DISTRIBUTE: _ClassVar[TransferType]
    TRANSFER_TYPE_BOND_LOW: _ClassVar[TransferType]
    TRANSFER_TYPE_BOND_HIGH: _ClassVar[TransferType]
    TRANSFER_TYPE_WITHDRAW: _ClassVar[TransferType]
    TRANSFER_TYPE_DEPOSIT: _ClassVar[TransferType]
    TRANSFER_TYPE_BOND_SLASHING: _ClassVar[TransferType]
    TRANSFER_TYPE_REWARD_PAYOUT: _ClassVar[TransferType]
    TRANSFER_TYPE_TRANSFER_FUNDS_SEND: _ClassVar[TransferType]
    TRANSFER_TYPE_TRANSFER_FUNDS_DISTRIBUTE: _ClassVar[TransferType]
    TRANSFER_TYPE_CLEAR_ACCOUNT: _ClassVar[TransferType]
    TRANSFER_TYPE_CHECKPOINT_BALANCE_RESTORE: _ClassVar[TransferType]
    TRANSFER_TYPE_SPOT: _ClassVar[TransferType]
    TRANSFER_TYPE_HOLDING_LOCK: _ClassVar[TransferType]
    TRANSFER_TYPE_HOLDING_RELEASE: _ClassVar[TransferType]
    TRANSFER_TYPE_SUCCESSOR_INSURANCE_FRACTION: _ClassVar[TransferType]
    TRANSFER_TYPE_LIQUIDITY_FEE_ALLOCATE: _ClassVar[TransferType]
    TRANSFER_TYPE_LIQUIDITY_FEE_NET_DISTRIBUTE: _ClassVar[TransferType]
    TRANSFER_TYPE_SLA_PENALTY_BOND_APPLY: _ClassVar[TransferType]
    TRANSFER_TYPE_SLA_PENALTY_LP_FEE_APPLY: _ClassVar[TransferType]
    TRANSFER_TYPE_LIQUIDITY_FEE_UNPAID_COLLECT: _ClassVar[TransferType]
    TRANSFER_TYPE_SLA_PERFORMANCE_BONUS_DISTRIBUTE: _ClassVar[TransferType]
    TRANSFER_TYPE_PERPETUALS_FUNDING_LOSS: _ClassVar[TransferType]
    TRANSFER_TYPE_PERPETUALS_FUNDING_WIN: _ClassVar[TransferType]
    TRANSFER_TYPE_REWARDS_VESTED: _ClassVar[TransferType]
    TRANSFER_TYPE_FEE_REFERRER_REWARD_PAY: _ClassVar[TransferType]
    TRANSFER_TYPE_FEE_REFERRER_REWARD_DISTRIBUTE: _ClassVar[TransferType]
    TRANSFER_TYPE_ORDER_MARGIN_LOW: _ClassVar[TransferType]
    TRANSFER_TYPE_ORDER_MARGIN_HIGH: _ClassVar[TransferType]
    TRANSFER_TYPE_ISOLATED_MARGIN_LOW: _ClassVar[TransferType]
    TRANSFER_TYPE_ISOLATED_MARGIN_HIGH: _ClassVar[TransferType]
    TRANSFER_TYPE_AMM_LOW: _ClassVar[TransferType]
    TRANSFER_TYPE_AMM_HIGH: _ClassVar[TransferType]
    TRANSFER_TYPE_AMM_RELEASE: _ClassVar[TransferType]
    TRANSFER_TYPE_TREASURY_FEE_PAY: _ClassVar[TransferType]
    TRANSFER_TYPE_BUY_BACK_FEE_PAY: _ClassVar[TransferType]
    TRANSFER_TYPE_HIGH_MAKER_FEE_REBATE_PAY: _ClassVar[TransferType]
    TRANSFER_TYPE_HIGH_MAKER_FEE_REBATE_RECEIVE: _ClassVar[TransferType]

class DispatchMetric(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DISPATCH_METRIC_UNSPECIFIED: _ClassVar[DispatchMetric]
    DISPATCH_METRIC_MAKER_FEES_PAID: _ClassVar[DispatchMetric]
    DISPATCH_METRIC_MAKER_FEES_RECEIVED: _ClassVar[DispatchMetric]
    DISPATCH_METRIC_LP_FEES_RECEIVED: _ClassVar[DispatchMetric]
    DISPATCH_METRIC_MARKET_VALUE: _ClassVar[DispatchMetric]
    DISPATCH_METRIC_RELATIVE_RETURN: _ClassVar[DispatchMetric]
    DISPATCH_METRIC_RETURN_VOLATILITY: _ClassVar[DispatchMetric]
    DISPATCH_METRIC_VALIDATOR_RANKING: _ClassVar[DispatchMetric]
    DISPATCH_METRIC_REALISED_RETURN: _ClassVar[DispatchMetric]
    DISPATCH_METRIC_AVERAGE_NOTIONAL: _ClassVar[DispatchMetric]
    DISPATCH_METRIC_ELIGIBLE_ENTITIES: _ClassVar[DispatchMetric]

class EntityScope(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ENTITY_SCOPE_UNSPECIFIED: _ClassVar[EntityScope]
    ENTITY_SCOPE_INDIVIDUALS: _ClassVar[EntityScope]
    ENTITY_SCOPE_TEAMS: _ClassVar[EntityScope]

class IndividualScope(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INDIVIDUAL_SCOPE_UNSPECIFIED: _ClassVar[IndividualScope]
    INDIVIDUAL_SCOPE_ALL: _ClassVar[IndividualScope]
    INDIVIDUAL_SCOPE_IN_TEAM: _ClassVar[IndividualScope]
    INDIVIDUAL_SCOPE_NOT_IN_TEAM: _ClassVar[IndividualScope]
    INDIVIDUAL_SCOPE_AMM: _ClassVar[IndividualScope]

class DistributionStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DISTRIBUTION_STRATEGY_UNSPECIFIED: _ClassVar[DistributionStrategy]
    DISTRIBUTION_STRATEGY_PRO_RATA: _ClassVar[DistributionStrategy]
    DISTRIBUTION_STRATEGY_RANK: _ClassVar[DistributionStrategy]
    DISTRIBUTION_STRATEGY_RANK_LOTTERY: _ClassVar[DistributionStrategy]

class NodeStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NODE_STATUS_UNSPECIFIED: _ClassVar[NodeStatus]
    NODE_STATUS_VALIDATOR: _ClassVar[NodeStatus]
    NODE_STATUS_NON_VALIDATOR: _ClassVar[NodeStatus]

class EpochAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EPOCH_ACTION_UNSPECIFIED: _ClassVar[EpochAction]
    EPOCH_ACTION_START: _ClassVar[EpochAction]
    EPOCH_ACTION_END: _ClassVar[EpochAction]

class ValidatorNodeStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VALIDATOR_NODE_STATUS_UNSPECIFIED: _ClassVar[ValidatorNodeStatus]
    VALIDATOR_NODE_STATUS_TENDERMINT: _ClassVar[ValidatorNodeStatus]
    VALIDATOR_NODE_STATUS_ERSATZ: _ClassVar[ValidatorNodeStatus]
    VALIDATOR_NODE_STATUS_PENDING: _ClassVar[ValidatorNodeStatus]

class MarginMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MARGIN_MODE_UNSPECIFIED: _ClassVar[MarginMode]
    MARGIN_MODE_CROSS_MARGIN: _ClassVar[MarginMode]
    MARGIN_MODE_ISOLATED_MARGIN: _ClassVar[MarginMode]

SIDE_UNSPECIFIED: Side
SIDE_BUY: Side
SIDE_SELL: Side
INTERVAL_UNSPECIFIED: Interval
INTERVAL_BLOCK: Interval
INTERVAL_I1M: Interval
INTERVAL_I5M: Interval
INTERVAL_I15M: Interval
INTERVAL_I30M: Interval
INTERVAL_I1H: Interval
INTERVAL_I4H: Interval
INTERVAL_I6H: Interval
INTERVAL_I8H: Interval
INTERVAL_I12H: Interval
INTERVAL_I1D: Interval
INTERVAL_I7D: Interval
POSITION_STATUS_UNSPECIFIED: PositionStatus
POSITION_STATUS_ORDERS_CLOSED: PositionStatus
POSITION_STATUS_CLOSED_OUT: PositionStatus
POSITION_STATUS_DISTRESSED: PositionStatus
AUCTION_TRIGGER_UNSPECIFIED: AuctionTrigger
AUCTION_TRIGGER_BATCH: AuctionTrigger
AUCTION_TRIGGER_OPENING: AuctionTrigger
AUCTION_TRIGGER_PRICE: AuctionTrigger
AUCTION_TRIGGER_LIQUIDITY: AuctionTrigger
AUCTION_TRIGGER_LIQUIDITY_TARGET_NOT_MET: AuctionTrigger
AUCTION_TRIGGER_UNABLE_TO_DEPLOY_LP_ORDERS: AuctionTrigger
AUCTION_TRIGGER_GOVERNANCE_SUSPENSION: AuctionTrigger
AUCTION_TRIGGER_LONG_BLOCK: AuctionTrigger
AUCTION_TRIGGER_PROTOCOL_AUTOMATED_PURCHASE: AuctionTrigger
PEGGED_REFERENCE_UNSPECIFIED: PeggedReference
PEGGED_REFERENCE_MID: PeggedReference
PEGGED_REFERENCE_BEST_BID: PeggedReference
PEGGED_REFERENCE_BEST_ASK: PeggedReference
ORDER_ERROR_UNSPECIFIED: OrderError
ORDER_ERROR_INVALID_MARKET_ID: OrderError
ORDER_ERROR_INVALID_ORDER_ID: OrderError
ORDER_ERROR_OUT_OF_SEQUENCE: OrderError
ORDER_ERROR_INVALID_REMAINING_SIZE: OrderError
ORDER_ERROR_TIME_FAILURE: OrderError
ORDER_ERROR_REMOVAL_FAILURE: OrderError
ORDER_ERROR_INVALID_EXPIRATION_DATETIME: OrderError
ORDER_ERROR_INVALID_ORDER_REFERENCE: OrderError
ORDER_ERROR_EDIT_NOT_ALLOWED: OrderError
ORDER_ERROR_AMEND_FAILURE: OrderError
ORDER_ERROR_NOT_FOUND: OrderError
ORDER_ERROR_INVALID_PARTY_ID: OrderError
ORDER_ERROR_MARKET_CLOSED: OrderError
ORDER_ERROR_MARGIN_CHECK_FAILED: OrderError
ORDER_ERROR_MISSING_GENERAL_ACCOUNT: OrderError
ORDER_ERROR_INTERNAL_ERROR: OrderError
ORDER_ERROR_INVALID_SIZE: OrderError
ORDER_ERROR_INVALID_PERSISTENCE: OrderError
ORDER_ERROR_INVALID_TYPE: OrderError
ORDER_ERROR_SELF_TRADING: OrderError
ORDER_ERROR_INSUFFICIENT_FUNDS_TO_PAY_FEES: OrderError
ORDER_ERROR_INCORRECT_MARKET_TYPE: OrderError
ORDER_ERROR_INVALID_TIME_IN_FORCE: OrderError
ORDER_ERROR_CANNOT_SEND_GFN_ORDER_DURING_AN_AUCTION: OrderError
ORDER_ERROR_CANNOT_SEND_GFA_ORDER_DURING_CONTINUOUS_TRADING: OrderError
ORDER_ERROR_CANNOT_AMEND_TO_GTT_WITHOUT_EXPIRYAT: OrderError
ORDER_ERROR_EXPIRYAT_BEFORE_CREATEDAT: OrderError
ORDER_ERROR_CANNOT_HAVE_GTC_AND_EXPIRYAT: OrderError
ORDER_ERROR_CANNOT_AMEND_TO_FOK_OR_IOC: OrderError
ORDER_ERROR_CANNOT_AMEND_TO_GFA_OR_GFN: OrderError
ORDER_ERROR_CANNOT_AMEND_FROM_GFA_OR_GFN: OrderError
ORDER_ERROR_CANNOT_SEND_IOC_ORDER_DURING_AUCTION: OrderError
ORDER_ERROR_CANNOT_SEND_FOK_ORDER_DURING_AUCTION: OrderError
ORDER_ERROR_MUST_BE_LIMIT_ORDER: OrderError
ORDER_ERROR_MUST_BE_GTT_OR_GTC: OrderError
ORDER_ERROR_WITHOUT_REFERENCE_PRICE: OrderError
ORDER_ERROR_BUY_CANNOT_REFERENCE_BEST_ASK_PRICE: OrderError
ORDER_ERROR_OFFSET_MUST_BE_GREATER_OR_EQUAL_TO_ZERO: OrderError
ORDER_ERROR_SELL_CANNOT_REFERENCE_BEST_BID_PRICE: OrderError
ORDER_ERROR_OFFSET_MUST_BE_GREATER_THAN_ZERO: OrderError
ORDER_ERROR_INSUFFICIENT_ASSET_BALANCE: OrderError
ORDER_ERROR_CANNOT_AMEND_PEGGED_ORDER_DETAILS_ON_NON_PEGGED_ORDER: OrderError
ORDER_ERROR_UNABLE_TO_REPRICE_PEGGED_ORDER: OrderError
ORDER_ERROR_UNABLE_TO_AMEND_PRICE_ON_PEGGED_ORDER: OrderError
ORDER_ERROR_NON_PERSISTENT_ORDER_OUT_OF_PRICE_BOUNDS: OrderError
ORDER_ERROR_TOO_MANY_PEGGED_ORDERS: OrderError
ORDER_ERROR_POST_ONLY_ORDER_WOULD_TRADE: OrderError
ORDER_ERROR_REDUCE_ONLY_ORDER_WOULD_NOT_REDUCE_POSITION: OrderError
ORDER_ERROR_ISOLATED_MARGIN_CHECK_FAILED: OrderError
ORDER_ERROR_PEGGED_ORDERS_NOT_ALLOWED_IN_ISOLATED_MARGIN_MODE: OrderError
ORDER_ERROR_PRICE_NOT_IN_TICK_SIZE: OrderError
ORDER_ERROR_PRICE_MUST_BE_LESS_THAN_OR_EQUAL_TO_MAX_PRICE: OrderError
ORDER_ERROR_SELL_ORDER_NOT_ALLOWED: OrderError
CHAIN_STATUS_UNSPECIFIED: ChainStatus
CHAIN_STATUS_DISCONNECTED: ChainStatus
CHAIN_STATUS_REPLAYING: ChainStatus
CHAIN_STATUS_CONNECTED: ChainStatus
ACCOUNT_TYPE_UNSPECIFIED: AccountType
ACCOUNT_TYPE_INSURANCE: AccountType
ACCOUNT_TYPE_SETTLEMENT: AccountType
ACCOUNT_TYPE_MARGIN: AccountType
ACCOUNT_TYPE_GENERAL: AccountType
ACCOUNT_TYPE_FEES_INFRASTRUCTURE: AccountType
ACCOUNT_TYPE_FEES_LIQUIDITY: AccountType
ACCOUNT_TYPE_FEES_MAKER: AccountType
ACCOUNT_TYPE_BOND: AccountType
ACCOUNT_TYPE_EXTERNAL: AccountType
ACCOUNT_TYPE_GLOBAL_INSURANCE: AccountType
ACCOUNT_TYPE_GLOBAL_REWARD: AccountType
ACCOUNT_TYPE_PENDING_TRANSFERS: AccountType
ACCOUNT_TYPE_REWARD_MAKER_PAID_FEES: AccountType
ACCOUNT_TYPE_REWARD_MAKER_RECEIVED_FEES: AccountType
ACCOUNT_TYPE_REWARD_LP_RECEIVED_FEES: AccountType
ACCOUNT_TYPE_REWARD_MARKET_PROPOSERS: AccountType
ACCOUNT_TYPE_HOLDING: AccountType
ACCOUNT_TYPE_LP_LIQUIDITY_FEES: AccountType
ACCOUNT_TYPE_LIQUIDITY_FEES_BONUS_DISTRIBUTION: AccountType
ACCOUNT_TYPE_NETWORK_TREASURY: AccountType
ACCOUNT_TYPE_VESTING_REWARDS: AccountType
ACCOUNT_TYPE_VESTED_REWARDS: AccountType
ACCOUNT_TYPE_REWARD_RELATIVE_RETURN: AccountType
ACCOUNT_TYPE_REWARD_RETURN_VOLATILITY: AccountType
ACCOUNT_TYPE_REWARD_VALIDATOR_RANKING: AccountType
ACCOUNT_TYPE_PENDING_FEE_REFERRAL_REWARD: AccountType
ACCOUNT_TYPE_ORDER_MARGIN: AccountType
ACCOUNT_TYPE_REWARD_REALISED_RETURN: AccountType
ACCOUNT_TYPE_BUY_BACK_FEES: AccountType
ACCOUNT_TYPE_REWARD_AVERAGE_NOTIONAL: AccountType
ACCOUNT_TYPE_REWARD_ELIGIBLE_ENTITIES: AccountType
TRANSFER_TYPE_UNSPECIFIED: TransferType
TRANSFER_TYPE_LOSS: TransferType
TRANSFER_TYPE_WIN: TransferType
TRANSFER_TYPE_MTM_LOSS: TransferType
TRANSFER_TYPE_MTM_WIN: TransferType
TRANSFER_TYPE_MARGIN_LOW: TransferType
TRANSFER_TYPE_MARGIN_HIGH: TransferType
TRANSFER_TYPE_MARGIN_CONFISCATED: TransferType
TRANSFER_TYPE_MAKER_FEE_PAY: TransferType
TRANSFER_TYPE_MAKER_FEE_RECEIVE: TransferType
TRANSFER_TYPE_INFRASTRUCTURE_FEE_PAY: TransferType
TRANSFER_TYPE_INFRASTRUCTURE_FEE_DISTRIBUTE: TransferType
TRANSFER_TYPE_LIQUIDITY_FEE_PAY: TransferType
TRANSFER_TYPE_LIQUIDITY_FEE_DISTRIBUTE: TransferType
TRANSFER_TYPE_BOND_LOW: TransferType
TRANSFER_TYPE_BOND_HIGH: TransferType
TRANSFER_TYPE_WITHDRAW: TransferType
TRANSFER_TYPE_DEPOSIT: TransferType
TRANSFER_TYPE_BOND_SLASHING: TransferType
TRANSFER_TYPE_REWARD_PAYOUT: TransferType
TRANSFER_TYPE_TRANSFER_FUNDS_SEND: TransferType
TRANSFER_TYPE_TRANSFER_FUNDS_DISTRIBUTE: TransferType
TRANSFER_TYPE_CLEAR_ACCOUNT: TransferType
TRANSFER_TYPE_CHECKPOINT_BALANCE_RESTORE: TransferType
TRANSFER_TYPE_SPOT: TransferType
TRANSFER_TYPE_HOLDING_LOCK: TransferType
TRANSFER_TYPE_HOLDING_RELEASE: TransferType
TRANSFER_TYPE_SUCCESSOR_INSURANCE_FRACTION: TransferType
TRANSFER_TYPE_LIQUIDITY_FEE_ALLOCATE: TransferType
TRANSFER_TYPE_LIQUIDITY_FEE_NET_DISTRIBUTE: TransferType
TRANSFER_TYPE_SLA_PENALTY_BOND_APPLY: TransferType
TRANSFER_TYPE_SLA_PENALTY_LP_FEE_APPLY: TransferType
TRANSFER_TYPE_LIQUIDITY_FEE_UNPAID_COLLECT: TransferType
TRANSFER_TYPE_SLA_PERFORMANCE_BONUS_DISTRIBUTE: TransferType
TRANSFER_TYPE_PERPETUALS_FUNDING_LOSS: TransferType
TRANSFER_TYPE_PERPETUALS_FUNDING_WIN: TransferType
TRANSFER_TYPE_REWARDS_VESTED: TransferType
TRANSFER_TYPE_FEE_REFERRER_REWARD_PAY: TransferType
TRANSFER_TYPE_FEE_REFERRER_REWARD_DISTRIBUTE: TransferType
TRANSFER_TYPE_ORDER_MARGIN_LOW: TransferType
TRANSFER_TYPE_ORDER_MARGIN_HIGH: TransferType
TRANSFER_TYPE_ISOLATED_MARGIN_LOW: TransferType
TRANSFER_TYPE_ISOLATED_MARGIN_HIGH: TransferType
TRANSFER_TYPE_AMM_LOW: TransferType
TRANSFER_TYPE_AMM_HIGH: TransferType
TRANSFER_TYPE_AMM_RELEASE: TransferType
TRANSFER_TYPE_TREASURY_FEE_PAY: TransferType
TRANSFER_TYPE_BUY_BACK_FEE_PAY: TransferType
TRANSFER_TYPE_HIGH_MAKER_FEE_REBATE_PAY: TransferType
TRANSFER_TYPE_HIGH_MAKER_FEE_REBATE_RECEIVE: TransferType
DISPATCH_METRIC_UNSPECIFIED: DispatchMetric
DISPATCH_METRIC_MAKER_FEES_PAID: DispatchMetric
DISPATCH_METRIC_MAKER_FEES_RECEIVED: DispatchMetric
DISPATCH_METRIC_LP_FEES_RECEIVED: DispatchMetric
DISPATCH_METRIC_MARKET_VALUE: DispatchMetric
DISPATCH_METRIC_RELATIVE_RETURN: DispatchMetric
DISPATCH_METRIC_RETURN_VOLATILITY: DispatchMetric
DISPATCH_METRIC_VALIDATOR_RANKING: DispatchMetric
DISPATCH_METRIC_REALISED_RETURN: DispatchMetric
DISPATCH_METRIC_AVERAGE_NOTIONAL: DispatchMetric
DISPATCH_METRIC_ELIGIBLE_ENTITIES: DispatchMetric
ENTITY_SCOPE_UNSPECIFIED: EntityScope
ENTITY_SCOPE_INDIVIDUALS: EntityScope
ENTITY_SCOPE_TEAMS: EntityScope
INDIVIDUAL_SCOPE_UNSPECIFIED: IndividualScope
INDIVIDUAL_SCOPE_ALL: IndividualScope
INDIVIDUAL_SCOPE_IN_TEAM: IndividualScope
INDIVIDUAL_SCOPE_NOT_IN_TEAM: IndividualScope
INDIVIDUAL_SCOPE_AMM: IndividualScope
DISTRIBUTION_STRATEGY_UNSPECIFIED: DistributionStrategy
DISTRIBUTION_STRATEGY_PRO_RATA: DistributionStrategy
DISTRIBUTION_STRATEGY_RANK: DistributionStrategy
DISTRIBUTION_STRATEGY_RANK_LOTTERY: DistributionStrategy
NODE_STATUS_UNSPECIFIED: NodeStatus
NODE_STATUS_VALIDATOR: NodeStatus
NODE_STATUS_NON_VALIDATOR: NodeStatus
EPOCH_ACTION_UNSPECIFIED: EpochAction
EPOCH_ACTION_START: EpochAction
EPOCH_ACTION_END: EpochAction
VALIDATOR_NODE_STATUS_UNSPECIFIED: ValidatorNodeStatus
VALIDATOR_NODE_STATUS_TENDERMINT: ValidatorNodeStatus
VALIDATOR_NODE_STATUS_ERSATZ: ValidatorNodeStatus
VALIDATOR_NODE_STATUS_PENDING: ValidatorNodeStatus
MARGIN_MODE_UNSPECIFIED: MarginMode
MARGIN_MODE_CROSS_MARGIN: MarginMode
MARGIN_MODE_ISOLATED_MARGIN: MarginMode

class PartyProfile(_message.Message):
    __slots__ = ("party_id", "alias", "metadata", "derived_keys")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    DERIVED_KEYS_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    alias: str
    metadata: _containers.RepeatedCompositeFieldContainer[Metadata]
    derived_keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        alias: _Optional[str] = ...,
        metadata: _Optional[_Iterable[_Union[Metadata, _Mapping]]] = ...,
        derived_keys: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class Metadata(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(
        self, key: _Optional[str] = ..., value: _Optional[str] = ...
    ) -> None: ...

class StopOrder(_message.Message):
    __slots__ = (
        "id",
        "oco_link_id",
        "expires_at",
        "expiry_strategy",
        "trigger_direction",
        "status",
        "created_at",
        "updated_at",
        "order_id",
        "party_id",
        "market_id",
        "rejection_reason",
        "size_override_setting",
        "size_override_value",
        "price",
        "trailing_percent_offset",
    )

    class SizeOverrideSetting(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SIZE_OVERRIDE_SETTING_UNSPECIFIED: _ClassVar[StopOrder.SizeOverrideSetting]
        SIZE_OVERRIDE_SETTING_NONE: _ClassVar[StopOrder.SizeOverrideSetting]
        SIZE_OVERRIDE_SETTING_POSITION: _ClassVar[StopOrder.SizeOverrideSetting]

    SIZE_OVERRIDE_SETTING_UNSPECIFIED: StopOrder.SizeOverrideSetting
    SIZE_OVERRIDE_SETTING_NONE: StopOrder.SizeOverrideSetting
    SIZE_OVERRIDE_SETTING_POSITION: StopOrder.SizeOverrideSetting

    class ExpiryStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        EXPIRY_STRATEGY_UNSPECIFIED: _ClassVar[StopOrder.ExpiryStrategy]
        EXPIRY_STRATEGY_CANCELS: _ClassVar[StopOrder.ExpiryStrategy]
        EXPIRY_STRATEGY_SUBMIT: _ClassVar[StopOrder.ExpiryStrategy]

    EXPIRY_STRATEGY_UNSPECIFIED: StopOrder.ExpiryStrategy
    EXPIRY_STRATEGY_CANCELS: StopOrder.ExpiryStrategy
    EXPIRY_STRATEGY_SUBMIT: StopOrder.ExpiryStrategy

    class TriggerDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRIGGER_DIRECTION_UNSPECIFIED: _ClassVar[StopOrder.TriggerDirection]
        TRIGGER_DIRECTION_RISES_ABOVE: _ClassVar[StopOrder.TriggerDirection]
        TRIGGER_DIRECTION_FALLS_BELOW: _ClassVar[StopOrder.TriggerDirection]

    TRIGGER_DIRECTION_UNSPECIFIED: StopOrder.TriggerDirection
    TRIGGER_DIRECTION_RISES_ABOVE: StopOrder.TriggerDirection
    TRIGGER_DIRECTION_FALLS_BELOW: StopOrder.TriggerDirection

    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[StopOrder.Status]
        STATUS_PENDING: _ClassVar[StopOrder.Status]
        STATUS_CANCELLED: _ClassVar[StopOrder.Status]
        STATUS_STOPPED: _ClassVar[StopOrder.Status]
        STATUS_TRIGGERED: _ClassVar[StopOrder.Status]
        STATUS_EXPIRED: _ClassVar[StopOrder.Status]
        STATUS_REJECTED: _ClassVar[StopOrder.Status]

    STATUS_UNSPECIFIED: StopOrder.Status
    STATUS_PENDING: StopOrder.Status
    STATUS_CANCELLED: StopOrder.Status
    STATUS_STOPPED: StopOrder.Status
    STATUS_TRIGGERED: StopOrder.Status
    STATUS_EXPIRED: StopOrder.Status
    STATUS_REJECTED: StopOrder.Status

    class RejectionReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REJECTION_REASON_UNSPECIFIED: _ClassVar[StopOrder.RejectionReason]
        REJECTION_REASON_TRADING_NOT_ALLOWED: _ClassVar[StopOrder.RejectionReason]
        REJECTION_REASON_EXPIRY_IN_THE_PAST: _ClassVar[StopOrder.RejectionReason]
        REJECTION_REASON_MUST_BE_REDUCE_ONLY: _ClassVar[StopOrder.RejectionReason]
        REJECTION_REASON_MAX_STOP_ORDERS_PER_PARTY_REACHED: _ClassVar[
            StopOrder.RejectionReason
        ]
        REJECTION_REASON_STOP_ORDER_NOT_ALLOWED_WITHOUT_A_POSITION: _ClassVar[
            StopOrder.RejectionReason
        ]
        REJECTION_REASON_STOP_ORDER_NOT_CLOSING_THE_POSITION: _ClassVar[
            StopOrder.RejectionReason
        ]
        REJECTION_REASON_STOP_ORDER_LINKED_PERCENTAGE_INVALID: _ClassVar[
            StopOrder.RejectionReason
        ]
        REJECTION_REASON_STOP_ORDER_NOT_ALLOWED_DURING_OPENING_AUCTION: _ClassVar[
            StopOrder.RejectionReason
        ]
        REJECTION_REASON_STOP_ORDER_CANNOT_MATCH_OCO_EXPIRY_TIMES: _ClassVar[
            StopOrder.RejectionReason
        ]
        REJECTION_REASON_STOP_ORDER_SIZE_OVERRIDE_UNSUPPORTED_FOR_SPOT: _ClassVar[
            StopOrder.RejectionReason
        ]
        REJECTION_REASON_SELL_ORDER_NOT_ALLOWED: _ClassVar[StopOrder.RejectionReason]

    REJECTION_REASON_UNSPECIFIED: StopOrder.RejectionReason
    REJECTION_REASON_TRADING_NOT_ALLOWED: StopOrder.RejectionReason
    REJECTION_REASON_EXPIRY_IN_THE_PAST: StopOrder.RejectionReason
    REJECTION_REASON_MUST_BE_REDUCE_ONLY: StopOrder.RejectionReason
    REJECTION_REASON_MAX_STOP_ORDERS_PER_PARTY_REACHED: StopOrder.RejectionReason
    REJECTION_REASON_STOP_ORDER_NOT_ALLOWED_WITHOUT_A_POSITION: (
        StopOrder.RejectionReason
    )
    REJECTION_REASON_STOP_ORDER_NOT_CLOSING_THE_POSITION: StopOrder.RejectionReason
    REJECTION_REASON_STOP_ORDER_LINKED_PERCENTAGE_INVALID: StopOrder.RejectionReason
    REJECTION_REASON_STOP_ORDER_NOT_ALLOWED_DURING_OPENING_AUCTION: (
        StopOrder.RejectionReason
    )
    REJECTION_REASON_STOP_ORDER_CANNOT_MATCH_OCO_EXPIRY_TIMES: StopOrder.RejectionReason
    REJECTION_REASON_STOP_ORDER_SIZE_OVERRIDE_UNSUPPORTED_FOR_SPOT: (
        StopOrder.RejectionReason
    )
    REJECTION_REASON_SELL_ORDER_NOT_ALLOWED: StopOrder.RejectionReason

    class SizeOverrideValue(_message.Message):
        __slots__ = ("percentage",)
        PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
        percentage: str
        def __init__(self, percentage: _Optional[str] = ...) -> None: ...

    ID_FIELD_NUMBER: _ClassVar[int]
    OCO_LINK_ID_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    REJECTION_REASON_FIELD_NUMBER: _ClassVar[int]
    SIZE_OVERRIDE_SETTING_FIELD_NUMBER: _ClassVar[int]
    SIZE_OVERRIDE_VALUE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    TRAILING_PERCENT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    id: str
    oco_link_id: str
    expires_at: int
    expiry_strategy: StopOrder.ExpiryStrategy
    trigger_direction: StopOrder.TriggerDirection
    status: StopOrder.Status
    created_at: int
    updated_at: int
    order_id: str
    party_id: str
    market_id: str
    rejection_reason: StopOrder.RejectionReason
    size_override_setting: StopOrder.SizeOverrideSetting
    size_override_value: StopOrder.SizeOverrideValue
    price: str
    trailing_percent_offset: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        oco_link_id: _Optional[str] = ...,
        expires_at: _Optional[int] = ...,
        expiry_strategy: _Optional[_Union[StopOrder.ExpiryStrategy, str]] = ...,
        trigger_direction: _Optional[_Union[StopOrder.TriggerDirection, str]] = ...,
        status: _Optional[_Union[StopOrder.Status, str]] = ...,
        created_at: _Optional[int] = ...,
        updated_at: _Optional[int] = ...,
        order_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        rejection_reason: _Optional[_Union[StopOrder.RejectionReason, str]] = ...,
        size_override_setting: _Optional[
            _Union[StopOrder.SizeOverrideSetting, str]
        ] = ...,
        size_override_value: _Optional[
            _Union[StopOrder.SizeOverrideValue, _Mapping]
        ] = ...,
        price: _Optional[str] = ...,
        trailing_percent_offset: _Optional[str] = ...,
    ) -> None: ...

class Party(_message.Message):
    __slots__ = ("id", "alias", "metadata")
    ID_FIELD_NUMBER: _ClassVar[int]
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    alias: str
    metadata: _containers.RepeatedCompositeFieldContainer[Metadata]
    def __init__(
        self,
        id: _Optional[str] = ...,
        alias: _Optional[str] = ...,
        metadata: _Optional[_Iterable[_Union[Metadata, _Mapping]]] = ...,
    ) -> None: ...

class RiskFactor(_message.Message):
    __slots__ = ("market", "short", "long")
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SHORT_FIELD_NUMBER: _ClassVar[int]
    LONG_FIELD_NUMBER: _ClassVar[int]
    market: str
    short: str
    long: str
    def __init__(
        self,
        market: _Optional[str] = ...,
        short: _Optional[str] = ...,
        long: _Optional[str] = ...,
    ) -> None: ...

class PeggedOrder(_message.Message):
    __slots__ = ("reference", "offset")
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    reference: PeggedReference
    offset: str
    def __init__(
        self,
        reference: _Optional[_Union[PeggedReference, str]] = ...,
        offset: _Optional[str] = ...,
    ) -> None: ...

class IcebergOrder(_message.Message):
    __slots__ = ("peak_size", "minimum_visible_size", "reserved_remaining")
    PEAK_SIZE_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_VISIBLE_SIZE_FIELD_NUMBER: _ClassVar[int]
    RESERVED_REMAINING_FIELD_NUMBER: _ClassVar[int]
    peak_size: int
    minimum_visible_size: int
    reserved_remaining: int
    def __init__(
        self,
        peak_size: _Optional[int] = ...,
        minimum_visible_size: _Optional[int] = ...,
        reserved_remaining: _Optional[int] = ...,
    ) -> None: ...

class Order(_message.Message):
    __slots__ = (
        "id",
        "market_id",
        "party_id",
        "side",
        "price",
        "size",
        "remaining",
        "time_in_force",
        "type",
        "created_at",
        "status",
        "expires_at",
        "reference",
        "reason",
        "updated_at",
        "version",
        "batch_id",
        "pegged_order",
        "liquidity_provision_id",
        "post_only",
        "reduce_only",
        "iceberg_order",
    )

    class TimeInForce(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TIME_IN_FORCE_UNSPECIFIED: _ClassVar[Order.TimeInForce]
        TIME_IN_FORCE_GTC: _ClassVar[Order.TimeInForce]
        TIME_IN_FORCE_GTT: _ClassVar[Order.TimeInForce]
        TIME_IN_FORCE_IOC: _ClassVar[Order.TimeInForce]
        TIME_IN_FORCE_FOK: _ClassVar[Order.TimeInForce]
        TIME_IN_FORCE_GFA: _ClassVar[Order.TimeInForce]
        TIME_IN_FORCE_GFN: _ClassVar[Order.TimeInForce]

    TIME_IN_FORCE_UNSPECIFIED: Order.TimeInForce
    TIME_IN_FORCE_GTC: Order.TimeInForce
    TIME_IN_FORCE_GTT: Order.TimeInForce
    TIME_IN_FORCE_IOC: Order.TimeInForce
    TIME_IN_FORCE_FOK: Order.TimeInForce
    TIME_IN_FORCE_GFA: Order.TimeInForce
    TIME_IN_FORCE_GFN: Order.TimeInForce

    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[Order.Type]
        TYPE_LIMIT: _ClassVar[Order.Type]
        TYPE_MARKET: _ClassVar[Order.Type]
        TYPE_NETWORK: _ClassVar[Order.Type]

    TYPE_UNSPECIFIED: Order.Type
    TYPE_LIMIT: Order.Type
    TYPE_MARKET: Order.Type
    TYPE_NETWORK: Order.Type

    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[Order.Status]
        STATUS_ACTIVE: _ClassVar[Order.Status]
        STATUS_EXPIRED: _ClassVar[Order.Status]
        STATUS_CANCELLED: _ClassVar[Order.Status]
        STATUS_STOPPED: _ClassVar[Order.Status]
        STATUS_FILLED: _ClassVar[Order.Status]
        STATUS_REJECTED: _ClassVar[Order.Status]
        STATUS_PARTIALLY_FILLED: _ClassVar[Order.Status]
        STATUS_PARKED: _ClassVar[Order.Status]

    STATUS_UNSPECIFIED: Order.Status
    STATUS_ACTIVE: Order.Status
    STATUS_EXPIRED: Order.Status
    STATUS_CANCELLED: Order.Status
    STATUS_STOPPED: Order.Status
    STATUS_FILLED: Order.Status
    STATUS_REJECTED: Order.Status
    STATUS_PARTIALLY_FILLED: Order.Status
    STATUS_PARKED: Order.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    REMAINING_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    PEGGED_ORDER_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISION_ID_FIELD_NUMBER: _ClassVar[int]
    POST_ONLY_FIELD_NUMBER: _ClassVar[int]
    REDUCE_ONLY_FIELD_NUMBER: _ClassVar[int]
    ICEBERG_ORDER_FIELD_NUMBER: _ClassVar[int]
    id: str
    market_id: str
    party_id: str
    side: Side
    price: str
    size: int
    remaining: int
    time_in_force: Order.TimeInForce
    type: Order.Type
    created_at: int
    status: Order.Status
    expires_at: int
    reference: str
    reason: OrderError
    updated_at: int
    version: int
    batch_id: int
    pegged_order: PeggedOrder
    liquidity_provision_id: str
    post_only: bool
    reduce_only: bool
    iceberg_order: IcebergOrder
    def __init__(
        self,
        id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        side: _Optional[_Union[Side, str]] = ...,
        price: _Optional[str] = ...,
        size: _Optional[int] = ...,
        remaining: _Optional[int] = ...,
        time_in_force: _Optional[_Union[Order.TimeInForce, str]] = ...,
        type: _Optional[_Union[Order.Type, str]] = ...,
        created_at: _Optional[int] = ...,
        status: _Optional[_Union[Order.Status, str]] = ...,
        expires_at: _Optional[int] = ...,
        reference: _Optional[str] = ...,
        reason: _Optional[_Union[OrderError, str]] = ...,
        updated_at: _Optional[int] = ...,
        version: _Optional[int] = ...,
        batch_id: _Optional[int] = ...,
        pegged_order: _Optional[_Union[PeggedOrder, _Mapping]] = ...,
        liquidity_provision_id: _Optional[str] = ...,
        post_only: bool = ...,
        reduce_only: bool = ...,
        iceberg_order: _Optional[_Union[IcebergOrder, _Mapping]] = ...,
    ) -> None: ...

class OrderCancellationConfirmation(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: Order
    def __init__(self, order: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class OrderConfirmation(_message.Message):
    __slots__ = ("order", "trades", "passive_orders_affected")
    ORDER_FIELD_NUMBER: _ClassVar[int]
    TRADES_FIELD_NUMBER: _ClassVar[int]
    PASSIVE_ORDERS_AFFECTED_FIELD_NUMBER: _ClassVar[int]
    order: Order
    trades: _containers.RepeatedCompositeFieldContainer[Trade]
    passive_orders_affected: _containers.RepeatedCompositeFieldContainer[Order]
    def __init__(
        self,
        order: _Optional[_Union[Order, _Mapping]] = ...,
        trades: _Optional[_Iterable[_Union[Trade, _Mapping]]] = ...,
        passive_orders_affected: _Optional[_Iterable[_Union[Order, _Mapping]]] = ...,
    ) -> None: ...

class AuctionIndicativeState(_message.Message):
    __slots__ = (
        "market_id",
        "indicative_price",
        "indicative_volume",
        "auction_start",
        "auction_end",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    INDICATIVE_PRICE_FIELD_NUMBER: _ClassVar[int]
    INDICATIVE_VOLUME_FIELD_NUMBER: _ClassVar[int]
    AUCTION_START_FIELD_NUMBER: _ClassVar[int]
    AUCTION_END_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    indicative_price: str
    indicative_volume: int
    auction_start: int
    auction_end: int
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        indicative_price: _Optional[str] = ...,
        indicative_volume: _Optional[int] = ...,
        auction_start: _Optional[int] = ...,
        auction_end: _Optional[int] = ...,
    ) -> None: ...

class Trade(_message.Message):
    __slots__ = (
        "id",
        "market_id",
        "price",
        "size",
        "buyer",
        "seller",
        "aggressor",
        "buy_order",
        "sell_order",
        "timestamp",
        "type",
        "buyer_fee",
        "seller_fee",
        "buyer_auction_batch",
        "seller_auction_batch",
        "asset_price",
    )

    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[Trade.Type]
        TYPE_DEFAULT: _ClassVar[Trade.Type]
        TYPE_NETWORK_CLOSE_OUT_GOOD: _ClassVar[Trade.Type]
        TYPE_NETWORK_CLOSE_OUT_BAD: _ClassVar[Trade.Type]

    TYPE_UNSPECIFIED: Trade.Type
    TYPE_DEFAULT: Trade.Type
    TYPE_NETWORK_CLOSE_OUT_GOOD: Trade.Type
    TYPE_NETWORK_CLOSE_OUT_BAD: Trade.Type
    ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    BUYER_FIELD_NUMBER: _ClassVar[int]
    SELLER_FIELD_NUMBER: _ClassVar[int]
    AGGRESSOR_FIELD_NUMBER: _ClassVar[int]
    BUY_ORDER_FIELD_NUMBER: _ClassVar[int]
    SELL_ORDER_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    BUYER_FEE_FIELD_NUMBER: _ClassVar[int]
    SELLER_FEE_FIELD_NUMBER: _ClassVar[int]
    BUYER_AUCTION_BATCH_FIELD_NUMBER: _ClassVar[int]
    SELLER_AUCTION_BATCH_FIELD_NUMBER: _ClassVar[int]
    ASSET_PRICE_FIELD_NUMBER: _ClassVar[int]
    id: str
    market_id: str
    price: str
    size: int
    buyer: str
    seller: str
    aggressor: Side
    buy_order: str
    sell_order: str
    timestamp: int
    type: Trade.Type
    buyer_fee: Fee
    seller_fee: Fee
    buyer_auction_batch: int
    seller_auction_batch: int
    asset_price: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        price: _Optional[str] = ...,
        size: _Optional[int] = ...,
        buyer: _Optional[str] = ...,
        seller: _Optional[str] = ...,
        aggressor: _Optional[_Union[Side, str]] = ...,
        buy_order: _Optional[str] = ...,
        sell_order: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
        type: _Optional[_Union[Trade.Type, str]] = ...,
        buyer_fee: _Optional[_Union[Fee, _Mapping]] = ...,
        seller_fee: _Optional[_Union[Fee, _Mapping]] = ...,
        buyer_auction_batch: _Optional[int] = ...,
        seller_auction_batch: _Optional[int] = ...,
        asset_price: _Optional[str] = ...,
    ) -> None: ...

class Fee(_message.Message):
    __slots__ = (
        "maker_fee",
        "infrastructure_fee",
        "liquidity_fee",
        "maker_fee_volume_discount",
        "infrastructure_fee_volume_discount",
        "liquidity_fee_volume_discount",
        "maker_fee_referrer_discount",
        "infrastructure_fee_referrer_discount",
        "liquidity_fee_referrer_discount",
        "treasury_fee",
        "buy_back_fee",
        "high_volume_maker_fee",
    )
    MAKER_FEE_FIELD_NUMBER: _ClassVar[int]
    INFRASTRUCTURE_FEE_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_FEE_FIELD_NUMBER: _ClassVar[int]
    MAKER_FEE_VOLUME_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    INFRASTRUCTURE_FEE_VOLUME_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_FEE_VOLUME_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    MAKER_FEE_REFERRER_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    INFRASTRUCTURE_FEE_REFERRER_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_FEE_REFERRER_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    TREASURY_FEE_FIELD_NUMBER: _ClassVar[int]
    BUY_BACK_FEE_FIELD_NUMBER: _ClassVar[int]
    HIGH_VOLUME_MAKER_FEE_FIELD_NUMBER: _ClassVar[int]
    maker_fee: str
    infrastructure_fee: str
    liquidity_fee: str
    maker_fee_volume_discount: str
    infrastructure_fee_volume_discount: str
    liquidity_fee_volume_discount: str
    maker_fee_referrer_discount: str
    infrastructure_fee_referrer_discount: str
    liquidity_fee_referrer_discount: str
    treasury_fee: str
    buy_back_fee: str
    high_volume_maker_fee: str
    def __init__(
        self,
        maker_fee: _Optional[str] = ...,
        infrastructure_fee: _Optional[str] = ...,
        liquidity_fee: _Optional[str] = ...,
        maker_fee_volume_discount: _Optional[str] = ...,
        infrastructure_fee_volume_discount: _Optional[str] = ...,
        liquidity_fee_volume_discount: _Optional[str] = ...,
        maker_fee_referrer_discount: _Optional[str] = ...,
        infrastructure_fee_referrer_discount: _Optional[str] = ...,
        liquidity_fee_referrer_discount: _Optional[str] = ...,
        treasury_fee: _Optional[str] = ...,
        buy_back_fee: _Optional[str] = ...,
        high_volume_maker_fee: _Optional[str] = ...,
    ) -> None: ...

class TradeSet(_message.Message):
    __slots__ = ("trades",)
    TRADES_FIELD_NUMBER: _ClassVar[int]
    trades: _containers.RepeatedCompositeFieldContainer[Trade]
    def __init__(
        self, trades: _Optional[_Iterable[_Union[Trade, _Mapping]]] = ...
    ) -> None: ...

class Candle(_message.Message):
    __slots__ = (
        "timestamp",
        "datetime",
        "high",
        "low",
        "open",
        "close",
        "volume",
        "interval",
        "notional",
    )
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DATETIME_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    NOTIONAL_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    datetime: str
    high: str
    low: str
    open: str
    close: str
    volume: int
    interval: Interval
    notional: int
    def __init__(
        self,
        timestamp: _Optional[int] = ...,
        datetime: _Optional[str] = ...,
        high: _Optional[str] = ...,
        low: _Optional[str] = ...,
        open: _Optional[str] = ...,
        close: _Optional[str] = ...,
        volume: _Optional[int] = ...,
        interval: _Optional[_Union[Interval, str]] = ...,
        notional: _Optional[int] = ...,
    ) -> None: ...

class PriceLevel(_message.Message):
    __slots__ = (
        "price",
        "number_of_orders",
        "volume",
        "amm_volume",
        "amm_volume_estimated",
    )
    PRICE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_ORDERS_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    AMM_VOLUME_FIELD_NUMBER: _ClassVar[int]
    AMM_VOLUME_ESTIMATED_FIELD_NUMBER: _ClassVar[int]
    price: str
    number_of_orders: int
    volume: int
    amm_volume: int
    amm_volume_estimated: int
    def __init__(
        self,
        price: _Optional[str] = ...,
        number_of_orders: _Optional[int] = ...,
        volume: _Optional[int] = ...,
        amm_volume: _Optional[int] = ...,
        amm_volume_estimated: _Optional[int] = ...,
    ) -> None: ...

class MarketDepth(_message.Message):
    __slots__ = ("market_id", "buy", "sell", "sequence_number")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    BUY_FIELD_NUMBER: _ClassVar[int]
    SELL_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    buy: _containers.RepeatedCompositeFieldContainer[PriceLevel]
    sell: _containers.RepeatedCompositeFieldContainer[PriceLevel]
    sequence_number: int
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        buy: _Optional[_Iterable[_Union[PriceLevel, _Mapping]]] = ...,
        sell: _Optional[_Iterable[_Union[PriceLevel, _Mapping]]] = ...,
        sequence_number: _Optional[int] = ...,
    ) -> None: ...

class MarketDepthUpdate(_message.Message):
    __slots__ = (
        "market_id",
        "buy",
        "sell",
        "sequence_number",
        "previous_sequence_number",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    BUY_FIELD_NUMBER: _ClassVar[int]
    SELL_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    buy: _containers.RepeatedCompositeFieldContainer[PriceLevel]
    sell: _containers.RepeatedCompositeFieldContainer[PriceLevel]
    sequence_number: int
    previous_sequence_number: int
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        buy: _Optional[_Iterable[_Union[PriceLevel, _Mapping]]] = ...,
        sell: _Optional[_Iterable[_Union[PriceLevel, _Mapping]]] = ...,
        sequence_number: _Optional[int] = ...,
        previous_sequence_number: _Optional[int] = ...,
    ) -> None: ...

class Position(_message.Message):
    __slots__ = (
        "market_id",
        "party_id",
        "open_volume",
        "realised_pnl",
        "unrealised_pnl",
        "average_entry_price",
        "updated_at",
        "loss_socialisation_amount",
        "position_status",
        "taker_fees_paid",
        "maker_fees_received",
        "fees_paid",
        "taker_fees_paid_since",
        "maker_fees_received_since",
        "fees_paid_since",
        "funding_payment_amount",
        "funding_payment_amount_since",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    OPEN_VOLUME_FIELD_NUMBER: _ClassVar[int]
    REALISED_PNL_FIELD_NUMBER: _ClassVar[int]
    UNREALISED_PNL_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_ENTRY_PRICE_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    LOSS_SOCIALISATION_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    POSITION_STATUS_FIELD_NUMBER: _ClassVar[int]
    TAKER_FEES_PAID_FIELD_NUMBER: _ClassVar[int]
    MAKER_FEES_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    FEES_PAID_FIELD_NUMBER: _ClassVar[int]
    TAKER_FEES_PAID_SINCE_FIELD_NUMBER: _ClassVar[int]
    MAKER_FEES_RECEIVED_SINCE_FIELD_NUMBER: _ClassVar[int]
    FEES_PAID_SINCE_FIELD_NUMBER: _ClassVar[int]
    FUNDING_PAYMENT_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    FUNDING_PAYMENT_AMOUNT_SINCE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    party_id: str
    open_volume: int
    realised_pnl: str
    unrealised_pnl: str
    average_entry_price: str
    updated_at: int
    loss_socialisation_amount: str
    position_status: PositionStatus
    taker_fees_paid: str
    maker_fees_received: str
    fees_paid: str
    taker_fees_paid_since: str
    maker_fees_received_since: str
    fees_paid_since: str
    funding_payment_amount: str
    funding_payment_amount_since: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        open_volume: _Optional[int] = ...,
        realised_pnl: _Optional[str] = ...,
        unrealised_pnl: _Optional[str] = ...,
        average_entry_price: _Optional[str] = ...,
        updated_at: _Optional[int] = ...,
        loss_socialisation_amount: _Optional[str] = ...,
        position_status: _Optional[_Union[PositionStatus, str]] = ...,
        taker_fees_paid: _Optional[str] = ...,
        maker_fees_received: _Optional[str] = ...,
        fees_paid: _Optional[str] = ...,
        taker_fees_paid_since: _Optional[str] = ...,
        maker_fees_received_since: _Optional[str] = ...,
        fees_paid_since: _Optional[str] = ...,
        funding_payment_amount: _Optional[str] = ...,
        funding_payment_amount_since: _Optional[str] = ...,
    ) -> None: ...

class PositionTrade(_message.Message):
    __slots__ = ("volume", "price")
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    volume: int
    price: str
    def __init__(
        self, volume: _Optional[int] = ..., price: _Optional[str] = ...
    ) -> None: ...

class Deposit(_message.Message):
    __slots__ = (
        "id",
        "status",
        "party_id",
        "asset",
        "amount",
        "tx_hash",
        "credited_timestamp",
        "created_timestamp",
    )

    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[Deposit.Status]
        STATUS_OPEN: _ClassVar[Deposit.Status]
        STATUS_CANCELLED: _ClassVar[Deposit.Status]
        STATUS_FINALIZED: _ClassVar[Deposit.Status]
        STATUS_DUPLICATE_REJECTED: _ClassVar[Deposit.Status]

    STATUS_UNSPECIFIED: Deposit.Status
    STATUS_OPEN: Deposit.Status
    STATUS_CANCELLED: Deposit.Status
    STATUS_FINALIZED: Deposit.Status
    STATUS_DUPLICATE_REJECTED: Deposit.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    CREDITED_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CREATED_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: Deposit.Status
    party_id: str
    asset: str
    amount: str
    tx_hash: str
    credited_timestamp: int
    created_timestamp: int
    def __init__(
        self,
        id: _Optional[str] = ...,
        status: _Optional[_Union[Deposit.Status, str]] = ...,
        party_id: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        tx_hash: _Optional[str] = ...,
        credited_timestamp: _Optional[int] = ...,
        created_timestamp: _Optional[int] = ...,
    ) -> None: ...

class Withdrawal(_message.Message):
    __slots__ = (
        "id",
        "party_id",
        "amount",
        "asset",
        "status",
        "ref",
        "tx_hash",
        "created_timestamp",
        "withdrawn_timestamp",
        "ext",
    )

    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[Withdrawal.Status]
        STATUS_OPEN: _ClassVar[Withdrawal.Status]
        STATUS_REJECTED: _ClassVar[Withdrawal.Status]
        STATUS_FINALIZED: _ClassVar[Withdrawal.Status]

    STATUS_UNSPECIFIED: Withdrawal.Status
    STATUS_OPEN: Withdrawal.Status
    STATUS_REJECTED: Withdrawal.Status
    STATUS_FINALIZED: Withdrawal.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    CREATED_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWN_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    id: str
    party_id: str
    amount: str
    asset: str
    status: Withdrawal.Status
    ref: str
    tx_hash: str
    created_timestamp: int
    withdrawn_timestamp: int
    ext: WithdrawExt
    def __init__(
        self,
        id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        status: _Optional[_Union[Withdrawal.Status, str]] = ...,
        ref: _Optional[str] = ...,
        tx_hash: _Optional[str] = ...,
        created_timestamp: _Optional[int] = ...,
        withdrawn_timestamp: _Optional[int] = ...,
        ext: _Optional[_Union[WithdrawExt, _Mapping]] = ...,
    ) -> None: ...

class WithdrawExt(_message.Message):
    __slots__ = ("erc20",)
    ERC20_FIELD_NUMBER: _ClassVar[int]
    erc20: Erc20WithdrawExt
    def __init__(
        self, erc20: _Optional[_Union[Erc20WithdrawExt, _Mapping]] = ...
    ) -> None: ...

class Erc20WithdrawExt(_message.Message):
    __slots__ = ("receiver_address",)
    RECEIVER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    receiver_address: str
    def __init__(self, receiver_address: _Optional[str] = ...) -> None: ...

class Account(_message.Message):
    __slots__ = ("id", "owner", "balance", "asset", "market_id", "type")
    ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    owner: str
    balance: str
    asset: str
    market_id: str
    type: AccountType
    def __init__(
        self,
        id: _Optional[str] = ...,
        owner: _Optional[str] = ...,
        balance: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        type: _Optional[_Union[AccountType, str]] = ...,
    ) -> None: ...

class FinancialAmount(_message.Message):
    __slots__ = ("amount", "asset")
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    amount: str
    asset: str
    def __init__(
        self, amount: _Optional[str] = ..., asset: _Optional[str] = ...
    ) -> None: ...

class Transfer(_message.Message):
    __slots__ = ("owner", "amount", "type", "min_amount", "market_id")
    OWNER_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MIN_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    owner: str
    amount: FinancialAmount
    type: TransferType
    min_amount: str
    market_id: str
    def __init__(
        self,
        owner: _Optional[str] = ...,
        amount: _Optional[_Union[FinancialAmount, _Mapping]] = ...,
        type: _Optional[_Union[TransferType, str]] = ...,
        min_amount: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
    ) -> None: ...

class DispatchStrategy(_message.Message):
    __slots__ = (
        "asset_for_metric",
        "metric",
        "markets",
        "entity_scope",
        "individual_scope",
        "team_scope",
        "n_top_performers",
        "staking_requirement",
        "notional_time_weighted_average_position_requirement",
        "window_length",
        "lock_period",
        "distribution_strategy",
        "rank_table",
        "cap_reward_fee_multiple",
        "transfer_interval",
        "target_notional_volume",
        "eligible_keys",
    )
    ASSET_FOR_METRIC_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    MARKETS_FIELD_NUMBER: _ClassVar[int]
    ENTITY_SCOPE_FIELD_NUMBER: _ClassVar[int]
    INDIVIDUAL_SCOPE_FIELD_NUMBER: _ClassVar[int]
    TEAM_SCOPE_FIELD_NUMBER: _ClassVar[int]
    N_TOP_PERFORMERS_FIELD_NUMBER: _ClassVar[int]
    STAKING_REQUIREMENT_FIELD_NUMBER: _ClassVar[int]
    NOTIONAL_TIME_WEIGHTED_AVERAGE_POSITION_REQUIREMENT_FIELD_NUMBER: _ClassVar[int]
    WINDOW_LENGTH_FIELD_NUMBER: _ClassVar[int]
    LOCK_PERIOD_FIELD_NUMBER: _ClassVar[int]
    DISTRIBUTION_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    RANK_TABLE_FIELD_NUMBER: _ClassVar[int]
    CAP_REWARD_FEE_MULTIPLE_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    TARGET_NOTIONAL_VOLUME_FIELD_NUMBER: _ClassVar[int]
    ELIGIBLE_KEYS_FIELD_NUMBER: _ClassVar[int]
    asset_for_metric: str
    metric: DispatchMetric
    markets: _containers.RepeatedScalarFieldContainer[str]
    entity_scope: EntityScope
    individual_scope: IndividualScope
    team_scope: _containers.RepeatedScalarFieldContainer[str]
    n_top_performers: str
    staking_requirement: str
    notional_time_weighted_average_position_requirement: str
    window_length: int
    lock_period: int
    distribution_strategy: DistributionStrategy
    rank_table: _containers.RepeatedCompositeFieldContainer[Rank]
    cap_reward_fee_multiple: str
    transfer_interval: int
    target_notional_volume: str
    eligible_keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        asset_for_metric: _Optional[str] = ...,
        metric: _Optional[_Union[DispatchMetric, str]] = ...,
        markets: _Optional[_Iterable[str]] = ...,
        entity_scope: _Optional[_Union[EntityScope, str]] = ...,
        individual_scope: _Optional[_Union[IndividualScope, str]] = ...,
        team_scope: _Optional[_Iterable[str]] = ...,
        n_top_performers: _Optional[str] = ...,
        staking_requirement: _Optional[str] = ...,
        notional_time_weighted_average_position_requirement: _Optional[str] = ...,
        window_length: _Optional[int] = ...,
        lock_period: _Optional[int] = ...,
        distribution_strategy: _Optional[_Union[DistributionStrategy, str]] = ...,
        rank_table: _Optional[_Iterable[_Union[Rank, _Mapping]]] = ...,
        cap_reward_fee_multiple: _Optional[str] = ...,
        transfer_interval: _Optional[int] = ...,
        target_notional_volume: _Optional[str] = ...,
        eligible_keys: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class Rank(_message.Message):
    __slots__ = ("start_rank", "share_ratio")
    START_RANK_FIELD_NUMBER: _ClassVar[int]
    SHARE_RATIO_FIELD_NUMBER: _ClassVar[int]
    start_rank: int
    share_ratio: int
    def __init__(
        self, start_rank: _Optional[int] = ..., share_ratio: _Optional[int] = ...
    ) -> None: ...

class TransferRequest(_message.Message):
    __slots__ = ("from_account", "to_account", "amount", "min_amount", "asset", "type")
    FROM_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    TO_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    MIN_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    from_account: _containers.RepeatedCompositeFieldContainer[Account]
    to_account: _containers.RepeatedCompositeFieldContainer[Account]
    amount: str
    min_amount: str
    asset: str
    type: TransferType
    def __init__(
        self,
        from_account: _Optional[_Iterable[_Union[Account, _Mapping]]] = ...,
        to_account: _Optional[_Iterable[_Union[Account, _Mapping]]] = ...,
        amount: _Optional[str] = ...,
        min_amount: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        type: _Optional[_Union[TransferType, str]] = ...,
    ) -> None: ...

class AccountDetails(_message.Message):
    __slots__ = ("asset_id", "type", "owner", "market_id")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    type: AccountType
    owner: str
    market_id: str
    def __init__(
        self,
        asset_id: _Optional[str] = ...,
        type: _Optional[_Union[AccountType, str]] = ...,
        owner: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
    ) -> None: ...

class LedgerEntry(_message.Message):
    __slots__ = (
        "from_account",
        "to_account",
        "amount",
        "type",
        "timestamp",
        "from_account_balance",
        "to_account_balance",
        "transfer_id",
    )
    FROM_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    TO_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FROM_ACCOUNT_BALANCE_FIELD_NUMBER: _ClassVar[int]
    TO_ACCOUNT_BALANCE_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    from_account: AccountDetails
    to_account: AccountDetails
    amount: str
    type: TransferType
    timestamp: int
    from_account_balance: str
    to_account_balance: str
    transfer_id: str
    def __init__(
        self,
        from_account: _Optional[_Union[AccountDetails, _Mapping]] = ...,
        to_account: _Optional[_Union[AccountDetails, _Mapping]] = ...,
        amount: _Optional[str] = ...,
        type: _Optional[_Union[TransferType, str]] = ...,
        timestamp: _Optional[int] = ...,
        from_account_balance: _Optional[str] = ...,
        to_account_balance: _Optional[str] = ...,
        transfer_id: _Optional[str] = ...,
    ) -> None: ...

class PostTransferBalance(_message.Message):
    __slots__ = ("account", "balance")
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    account: AccountDetails
    balance: str
    def __init__(
        self,
        account: _Optional[_Union[AccountDetails, _Mapping]] = ...,
        balance: _Optional[str] = ...,
    ) -> None: ...

class LedgerMovement(_message.Message):
    __slots__ = ("entries", "balances")
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    BALANCES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[LedgerEntry]
    balances: _containers.RepeatedCompositeFieldContainer[PostTransferBalance]
    def __init__(
        self,
        entries: _Optional[_Iterable[_Union[LedgerEntry, _Mapping]]] = ...,
        balances: _Optional[_Iterable[_Union[PostTransferBalance, _Mapping]]] = ...,
    ) -> None: ...

class MarginLevels(_message.Message):
    __slots__ = (
        "maintenance_margin",
        "search_level",
        "initial_margin",
        "collateral_release_level",
        "party_id",
        "market_id",
        "asset",
        "timestamp",
        "order_margin",
        "margin_mode",
        "margin_factor",
    )
    MAINTENANCE_MARGIN_FIELD_NUMBER: _ClassVar[int]
    SEARCH_LEVEL_FIELD_NUMBER: _ClassVar[int]
    INITIAL_MARGIN_FIELD_NUMBER: _ClassVar[int]
    COLLATERAL_RELEASE_LEVEL_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ORDER_MARGIN_FIELD_NUMBER: _ClassVar[int]
    MARGIN_MODE_FIELD_NUMBER: _ClassVar[int]
    MARGIN_FACTOR_FIELD_NUMBER: _ClassVar[int]
    maintenance_margin: str
    search_level: str
    initial_margin: str
    collateral_release_level: str
    party_id: str
    market_id: str
    asset: str
    timestamp: int
    order_margin: str
    margin_mode: MarginMode
    margin_factor: str
    def __init__(
        self,
        maintenance_margin: _Optional[str] = ...,
        search_level: _Optional[str] = ...,
        initial_margin: _Optional[str] = ...,
        collateral_release_level: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
        order_margin: _Optional[str] = ...,
        margin_mode: _Optional[_Union[MarginMode, str]] = ...,
        margin_factor: _Optional[str] = ...,
    ) -> None: ...

class PerpetualData(_message.Message):
    __slots__ = (
        "funding_payment",
        "funding_rate",
        "internal_twap",
        "external_twap",
        "seq_num",
        "start_time",
        "internal_composite_price",
        "next_internal_composite_price_calc",
        "internal_composite_price_type",
        "underlying_index_price",
        "internal_composite_price_state",
    )
    FUNDING_PAYMENT_FIELD_NUMBER: _ClassVar[int]
    FUNDING_RATE_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_TWAP_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_TWAP_FIELD_NUMBER: _ClassVar[int]
    SEQ_NUM_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_COMPOSITE_PRICE_FIELD_NUMBER: _ClassVar[int]
    NEXT_INTERNAL_COMPOSITE_PRICE_CALC_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_COMPOSITE_PRICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    UNDERLYING_INDEX_PRICE_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_COMPOSITE_PRICE_STATE_FIELD_NUMBER: _ClassVar[int]
    funding_payment: str
    funding_rate: str
    internal_twap: str
    external_twap: str
    seq_num: int
    start_time: int
    internal_composite_price: str
    next_internal_composite_price_calc: int
    internal_composite_price_type: _markets_pb2.CompositePriceType
    underlying_index_price: str
    internal_composite_price_state: CompositePriceState
    def __init__(
        self,
        funding_payment: _Optional[str] = ...,
        funding_rate: _Optional[str] = ...,
        internal_twap: _Optional[str] = ...,
        external_twap: _Optional[str] = ...,
        seq_num: _Optional[int] = ...,
        start_time: _Optional[int] = ...,
        internal_composite_price: _Optional[str] = ...,
        next_internal_composite_price_calc: _Optional[int] = ...,
        internal_composite_price_type: _Optional[
            _Union[_markets_pb2.CompositePriceType, str]
        ] = ...,
        underlying_index_price: _Optional[str] = ...,
        internal_composite_price_state: _Optional[
            _Union[CompositePriceState, _Mapping]
        ] = ...,
    ) -> None: ...

class ProductData(_message.Message):
    __slots__ = ("perpetual_data",)
    PERPETUAL_DATA_FIELD_NUMBER: _ClassVar[int]
    perpetual_data: PerpetualData
    def __init__(
        self, perpetual_data: _Optional[_Union[PerpetualData, _Mapping]] = ...
    ) -> None: ...

class ProtocolAutomatedPurchaseData(_message.Message):
    __slots__ = ("id", "order_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    order_id: str
    def __init__(
        self, id: _Optional[str] = ..., order_id: _Optional[str] = ...
    ) -> None: ...

class MarketData(_message.Message):
    __slots__ = (
        "mark_price",
        "best_bid_price",
        "best_bid_volume",
        "best_offer_price",
        "best_offer_volume",
        "best_static_bid_price",
        "best_static_bid_volume",
        "best_static_offer_price",
        "best_static_offer_volume",
        "mid_price",
        "static_mid_price",
        "market",
        "timestamp",
        "open_interest",
        "auction_end",
        "auction_start",
        "indicative_price",
        "indicative_volume",
        "market_trading_mode",
        "trigger",
        "extension_trigger",
        "target_stake",
        "supplied_stake",
        "price_monitoring_bounds",
        "market_value_proxy",
        "liquidity_provider_fee_share",
        "market_state",
        "next_mark_to_market",
        "last_traded_price",
        "market_growth",
        "product_data",
        "liquidity_provider_sla",
        "next_network_closeout",
        "mark_price_type",
        "mark_price_state",
        "active_protocol_automated_purchase",
    )
    MARK_PRICE_FIELD_NUMBER: _ClassVar[int]
    BEST_BID_PRICE_FIELD_NUMBER: _ClassVar[int]
    BEST_BID_VOLUME_FIELD_NUMBER: _ClassVar[int]
    BEST_OFFER_PRICE_FIELD_NUMBER: _ClassVar[int]
    BEST_OFFER_VOLUME_FIELD_NUMBER: _ClassVar[int]
    BEST_STATIC_BID_PRICE_FIELD_NUMBER: _ClassVar[int]
    BEST_STATIC_BID_VOLUME_FIELD_NUMBER: _ClassVar[int]
    BEST_STATIC_OFFER_PRICE_FIELD_NUMBER: _ClassVar[int]
    BEST_STATIC_OFFER_VOLUME_FIELD_NUMBER: _ClassVar[int]
    MID_PRICE_FIELD_NUMBER: _ClassVar[int]
    STATIC_MID_PRICE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    OPEN_INTEREST_FIELD_NUMBER: _ClassVar[int]
    AUCTION_END_FIELD_NUMBER: _ClassVar[int]
    AUCTION_START_FIELD_NUMBER: _ClassVar[int]
    INDICATIVE_PRICE_FIELD_NUMBER: _ClassVar[int]
    INDICATIVE_VOLUME_FIELD_NUMBER: _ClassVar[int]
    MARKET_TRADING_MODE_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_TRIGGER_FIELD_NUMBER: _ClassVar[int]
    TARGET_STAKE_FIELD_NUMBER: _ClassVar[int]
    SUPPLIED_STAKE_FIELD_NUMBER: _ClassVar[int]
    PRICE_MONITORING_BOUNDS_FIELD_NUMBER: _ClassVar[int]
    MARKET_VALUE_PROXY_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVIDER_FEE_SHARE_FIELD_NUMBER: _ClassVar[int]
    MARKET_STATE_FIELD_NUMBER: _ClassVar[int]
    NEXT_MARK_TO_MARKET_FIELD_NUMBER: _ClassVar[int]
    LAST_TRADED_PRICE_FIELD_NUMBER: _ClassVar[int]
    MARKET_GROWTH_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_DATA_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVIDER_SLA_FIELD_NUMBER: _ClassVar[int]
    NEXT_NETWORK_CLOSEOUT_FIELD_NUMBER: _ClassVar[int]
    MARK_PRICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MARK_PRICE_STATE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_PROTOCOL_AUTOMATED_PURCHASE_FIELD_NUMBER: _ClassVar[int]
    mark_price: str
    best_bid_price: str
    best_bid_volume: int
    best_offer_price: str
    best_offer_volume: int
    best_static_bid_price: str
    best_static_bid_volume: int
    best_static_offer_price: str
    best_static_offer_volume: int
    mid_price: str
    static_mid_price: str
    market: str
    timestamp: int
    open_interest: int
    auction_end: int
    auction_start: int
    indicative_price: str
    indicative_volume: int
    market_trading_mode: _markets_pb2.Market.TradingMode
    trigger: AuctionTrigger
    extension_trigger: AuctionTrigger
    target_stake: str
    supplied_stake: str
    price_monitoring_bounds: _containers.RepeatedCompositeFieldContainer[
        PriceMonitoringBounds
    ]
    market_value_proxy: str
    liquidity_provider_fee_share: _containers.RepeatedCompositeFieldContainer[
        LiquidityProviderFeeShare
    ]
    market_state: _markets_pb2.Market.State
    next_mark_to_market: int
    last_traded_price: str
    market_growth: str
    product_data: ProductData
    liquidity_provider_sla: _containers.RepeatedCompositeFieldContainer[
        LiquidityProviderSLA
    ]
    next_network_closeout: int
    mark_price_type: _markets_pb2.CompositePriceType
    mark_price_state: CompositePriceState
    active_protocol_automated_purchase: ProtocolAutomatedPurchaseData
    def __init__(
        self,
        mark_price: _Optional[str] = ...,
        best_bid_price: _Optional[str] = ...,
        best_bid_volume: _Optional[int] = ...,
        best_offer_price: _Optional[str] = ...,
        best_offer_volume: _Optional[int] = ...,
        best_static_bid_price: _Optional[str] = ...,
        best_static_bid_volume: _Optional[int] = ...,
        best_static_offer_price: _Optional[str] = ...,
        best_static_offer_volume: _Optional[int] = ...,
        mid_price: _Optional[str] = ...,
        static_mid_price: _Optional[str] = ...,
        market: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
        open_interest: _Optional[int] = ...,
        auction_end: _Optional[int] = ...,
        auction_start: _Optional[int] = ...,
        indicative_price: _Optional[str] = ...,
        indicative_volume: _Optional[int] = ...,
        market_trading_mode: _Optional[
            _Union[_markets_pb2.Market.TradingMode, str]
        ] = ...,
        trigger: _Optional[_Union[AuctionTrigger, str]] = ...,
        extension_trigger: _Optional[_Union[AuctionTrigger, str]] = ...,
        target_stake: _Optional[str] = ...,
        supplied_stake: _Optional[str] = ...,
        price_monitoring_bounds: _Optional[
            _Iterable[_Union[PriceMonitoringBounds, _Mapping]]
        ] = ...,
        market_value_proxy: _Optional[str] = ...,
        liquidity_provider_fee_share: _Optional[
            _Iterable[_Union[LiquidityProviderFeeShare, _Mapping]]
        ] = ...,
        market_state: _Optional[_Union[_markets_pb2.Market.State, str]] = ...,
        next_mark_to_market: _Optional[int] = ...,
        last_traded_price: _Optional[str] = ...,
        market_growth: _Optional[str] = ...,
        product_data: _Optional[_Union[ProductData, _Mapping]] = ...,
        liquidity_provider_sla: _Optional[
            _Iterable[_Union[LiquidityProviderSLA, _Mapping]]
        ] = ...,
        next_network_closeout: _Optional[int] = ...,
        mark_price_type: _Optional[_Union[_markets_pb2.CompositePriceType, str]] = ...,
        mark_price_state: _Optional[_Union[CompositePriceState, _Mapping]] = ...,
        active_protocol_automated_purchase: _Optional[
            _Union[ProtocolAutomatedPurchaseData, _Mapping]
        ] = ...,
    ) -> None: ...

class CompositePriceSource(_message.Message):
    __slots__ = ("price_source", "price", "last_updated")
    PRICE_SOURCE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    price_source: str
    price: str
    last_updated: int
    def __init__(
        self,
        price_source: _Optional[str] = ...,
        price: _Optional[str] = ...,
        last_updated: _Optional[int] = ...,
    ) -> None: ...

class CompositePriceState(_message.Message):
    __slots__ = ("price_sources",)
    PRICE_SOURCES_FIELD_NUMBER: _ClassVar[int]
    price_sources: _containers.RepeatedCompositeFieldContainer[CompositePriceSource]
    def __init__(
        self,
        price_sources: _Optional[
            _Iterable[_Union[CompositePriceSource, _Mapping]]
        ] = ...,
    ) -> None: ...

class LiquidityProviderFeeShare(_message.Message):
    __slots__ = (
        "party",
        "equity_like_share",
        "average_entry_valuation",
        "average_score",
        "virtual_stake",
    )
    PARTY_FIELD_NUMBER: _ClassVar[int]
    EQUITY_LIKE_SHARE_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_ENTRY_VALUATION_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_SCORE_FIELD_NUMBER: _ClassVar[int]
    VIRTUAL_STAKE_FIELD_NUMBER: _ClassVar[int]
    party: str
    equity_like_share: str
    average_entry_valuation: str
    average_score: str
    virtual_stake: str
    def __init__(
        self,
        party: _Optional[str] = ...,
        equity_like_share: _Optional[str] = ...,
        average_entry_valuation: _Optional[str] = ...,
        average_score: _Optional[str] = ...,
        virtual_stake: _Optional[str] = ...,
    ) -> None: ...

class LiquidityProviderSLA(_message.Message):
    __slots__ = (
        "party",
        "current_epoch_fraction_of_time_on_book",
        "last_epoch_fraction_of_time_on_book",
        "last_epoch_fee_penalty",
        "last_epoch_bond_penalty",
        "hysteresis_period_fee_penalties",
        "required_liquidity",
        "notional_volume_buys",
        "notional_volume_sells",
    )
    PARTY_FIELD_NUMBER: _ClassVar[int]
    CURRENT_EPOCH_FRACTION_OF_TIME_ON_BOOK_FIELD_NUMBER: _ClassVar[int]
    LAST_EPOCH_FRACTION_OF_TIME_ON_BOOK_FIELD_NUMBER: _ClassVar[int]
    LAST_EPOCH_FEE_PENALTY_FIELD_NUMBER: _ClassVar[int]
    LAST_EPOCH_BOND_PENALTY_FIELD_NUMBER: _ClassVar[int]
    HYSTERESIS_PERIOD_FEE_PENALTIES_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_LIQUIDITY_FIELD_NUMBER: _ClassVar[int]
    NOTIONAL_VOLUME_BUYS_FIELD_NUMBER: _ClassVar[int]
    NOTIONAL_VOLUME_SELLS_FIELD_NUMBER: _ClassVar[int]
    party: str
    current_epoch_fraction_of_time_on_book: str
    last_epoch_fraction_of_time_on_book: str
    last_epoch_fee_penalty: str
    last_epoch_bond_penalty: str
    hysteresis_period_fee_penalties: _containers.RepeatedScalarFieldContainer[str]
    required_liquidity: str
    notional_volume_buys: str
    notional_volume_sells: str
    def __init__(
        self,
        party: _Optional[str] = ...,
        current_epoch_fraction_of_time_on_book: _Optional[str] = ...,
        last_epoch_fraction_of_time_on_book: _Optional[str] = ...,
        last_epoch_fee_penalty: _Optional[str] = ...,
        last_epoch_bond_penalty: _Optional[str] = ...,
        hysteresis_period_fee_penalties: _Optional[_Iterable[str]] = ...,
        required_liquidity: _Optional[str] = ...,
        notional_volume_buys: _Optional[str] = ...,
        notional_volume_sells: _Optional[str] = ...,
    ) -> None: ...

class PriceMonitoringBounds(_message.Message):
    __slots__ = (
        "min_valid_price",
        "max_valid_price",
        "trigger",
        "reference_price",
        "active",
    )
    MIN_VALID_PRICE_FIELD_NUMBER: _ClassVar[int]
    MAX_VALID_PRICE_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_PRICE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    min_valid_price: str
    max_valid_price: str
    trigger: _markets_pb2.PriceMonitoringTrigger
    reference_price: str
    active: bool
    def __init__(
        self,
        min_valid_price: _Optional[str] = ...,
        max_valid_price: _Optional[str] = ...,
        trigger: _Optional[_Union[_markets_pb2.PriceMonitoringTrigger, _Mapping]] = ...,
        reference_price: _Optional[str] = ...,
        active: bool = ...,
    ) -> None: ...

class ErrorDetail(_message.Message):
    __slots__ = ("code", "message", "inner")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    INNER_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    inner: str
    def __init__(
        self,
        code: _Optional[int] = ...,
        message: _Optional[str] = ...,
        inner: _Optional[str] = ...,
    ) -> None: ...

class NetworkParameter(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(
        self, key: _Optional[str] = ..., value: _Optional[str] = ...
    ) -> None: ...

class NetworkLimits(_message.Message):
    __slots__ = (
        "can_propose_market",
        "can_propose_asset",
        "propose_market_enabled",
        "propose_asset_enabled",
        "genesis_loaded",
        "propose_market_enabled_from",
        "propose_asset_enabled_from",
        "can_propose_spot_market",
        "can_propose_perpetual_market",
        "can_use_amm",
    )
    CAN_PROPOSE_MARKET_FIELD_NUMBER: _ClassVar[int]
    CAN_PROPOSE_ASSET_FIELD_NUMBER: _ClassVar[int]
    PROPOSE_MARKET_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROPOSE_ASSET_ENABLED_FIELD_NUMBER: _ClassVar[int]
    GENESIS_LOADED_FIELD_NUMBER: _ClassVar[int]
    PROPOSE_MARKET_ENABLED_FROM_FIELD_NUMBER: _ClassVar[int]
    PROPOSE_ASSET_ENABLED_FROM_FIELD_NUMBER: _ClassVar[int]
    CAN_PROPOSE_SPOT_MARKET_FIELD_NUMBER: _ClassVar[int]
    CAN_PROPOSE_PERPETUAL_MARKET_FIELD_NUMBER: _ClassVar[int]
    CAN_USE_AMM_FIELD_NUMBER: _ClassVar[int]
    can_propose_market: bool
    can_propose_asset: bool
    propose_market_enabled: bool
    propose_asset_enabled: bool
    genesis_loaded: bool
    propose_market_enabled_from: int
    propose_asset_enabled_from: int
    can_propose_spot_market: bool
    can_propose_perpetual_market: bool
    can_use_amm: bool
    def __init__(
        self,
        can_propose_market: bool = ...,
        can_propose_asset: bool = ...,
        propose_market_enabled: bool = ...,
        propose_asset_enabled: bool = ...,
        genesis_loaded: bool = ...,
        propose_market_enabled_from: _Optional[int] = ...,
        propose_asset_enabled_from: _Optional[int] = ...,
        can_propose_spot_market: bool = ...,
        can_propose_perpetual_market: bool = ...,
        can_use_amm: bool = ...,
    ) -> None: ...

class LiquidityOrder(_message.Message):
    __slots__ = ("reference", "proportion", "offset")
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    PROPORTION_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    reference: PeggedReference
    proportion: int
    offset: str
    def __init__(
        self,
        reference: _Optional[_Union[PeggedReference, str]] = ...,
        proportion: _Optional[int] = ...,
        offset: _Optional[str] = ...,
    ) -> None: ...

class LiquidityOrderReference(_message.Message):
    __slots__ = ("order_id", "liquidity_order")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_ORDER_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    liquidity_order: LiquidityOrder
    def __init__(
        self,
        order_id: _Optional[str] = ...,
        liquidity_order: _Optional[_Union[LiquidityOrder, _Mapping]] = ...,
    ) -> None: ...

class LiquidityProvision(_message.Message):
    __slots__ = (
        "id",
        "party_id",
        "created_at",
        "updated_at",
        "market_id",
        "commitment_amount",
        "fee",
        "sells",
        "buys",
        "version",
        "status",
        "reference",
    )

    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[LiquidityProvision.Status]
        STATUS_ACTIVE: _ClassVar[LiquidityProvision.Status]
        STATUS_STOPPED: _ClassVar[LiquidityProvision.Status]
        STATUS_CANCELLED: _ClassVar[LiquidityProvision.Status]
        STATUS_REJECTED: _ClassVar[LiquidityProvision.Status]
        STATUS_UNDEPLOYED: _ClassVar[LiquidityProvision.Status]
        STATUS_PENDING: _ClassVar[LiquidityProvision.Status]

    STATUS_UNSPECIFIED: LiquidityProvision.Status
    STATUS_ACTIVE: LiquidityProvision.Status
    STATUS_STOPPED: LiquidityProvision.Status
    STATUS_CANCELLED: LiquidityProvision.Status
    STATUS_REJECTED: LiquidityProvision.Status
    STATUS_UNDEPLOYED: LiquidityProvision.Status
    STATUS_PENDING: LiquidityProvision.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    FEE_FIELD_NUMBER: _ClassVar[int]
    SELLS_FIELD_NUMBER: _ClassVar[int]
    BUYS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    party_id: str
    created_at: int
    updated_at: int
    market_id: str
    commitment_amount: str
    fee: str
    sells: _containers.RepeatedCompositeFieldContainer[LiquidityOrderReference]
    buys: _containers.RepeatedCompositeFieldContainer[LiquidityOrderReference]
    version: int
    status: LiquidityProvision.Status
    reference: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        created_at: _Optional[int] = ...,
        updated_at: _Optional[int] = ...,
        market_id: _Optional[str] = ...,
        commitment_amount: _Optional[str] = ...,
        fee: _Optional[str] = ...,
        sells: _Optional[_Iterable[_Union[LiquidityOrderReference, _Mapping]]] = ...,
        buys: _Optional[_Iterable[_Union[LiquidityOrderReference, _Mapping]]] = ...,
        version: _Optional[int] = ...,
        status: _Optional[_Union[LiquidityProvision.Status, str]] = ...,
        reference: _Optional[str] = ...,
    ) -> None: ...

class EthereumL2Config(_message.Message):
    __slots__ = ("network_id", "chain_id", "confirmations", "name", "block_interval")
    NETWORK_ID_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIRMATIONS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BLOCK_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    network_id: str
    chain_id: str
    confirmations: int
    name: str
    block_interval: int
    def __init__(
        self,
        network_id: _Optional[str] = ...,
        chain_id: _Optional[str] = ...,
        confirmations: _Optional[int] = ...,
        name: _Optional[str] = ...,
        block_interval: _Optional[int] = ...,
    ) -> None: ...

class EthereumL2Configs(_message.Message):
    __slots__ = ("configs",)
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    configs: _containers.RepeatedCompositeFieldContainer[EthereumL2Config]
    def __init__(
        self, configs: _Optional[_Iterable[_Union[EthereumL2Config, _Mapping]]] = ...
    ) -> None: ...

class EthereumConfig(_message.Message):
    __slots__ = (
        "network_id",
        "chain_id",
        "collateral_bridge_contract",
        "confirmations",
        "staking_bridge_contract",
        "token_vesting_contract",
        "multisig_control_contract",
        "block_time",
    )
    NETWORK_ID_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    COLLATERAL_BRIDGE_CONTRACT_FIELD_NUMBER: _ClassVar[int]
    CONFIRMATIONS_FIELD_NUMBER: _ClassVar[int]
    STAKING_BRIDGE_CONTRACT_FIELD_NUMBER: _ClassVar[int]
    TOKEN_VESTING_CONTRACT_FIELD_NUMBER: _ClassVar[int]
    MULTISIG_CONTROL_CONTRACT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    network_id: str
    chain_id: str
    collateral_bridge_contract: EthereumContractConfig
    confirmations: int
    staking_bridge_contract: EthereumContractConfig
    token_vesting_contract: EthereumContractConfig
    multisig_control_contract: EthereumContractConfig
    block_time: str
    def __init__(
        self,
        network_id: _Optional[str] = ...,
        chain_id: _Optional[str] = ...,
        collateral_bridge_contract: _Optional[
            _Union[EthereumContractConfig, _Mapping]
        ] = ...,
        confirmations: _Optional[int] = ...,
        staking_bridge_contract: _Optional[
            _Union[EthereumContractConfig, _Mapping]
        ] = ...,
        token_vesting_contract: _Optional[
            _Union[EthereumContractConfig, _Mapping]
        ] = ...,
        multisig_control_contract: _Optional[
            _Union[EthereumContractConfig, _Mapping]
        ] = ...,
        block_time: _Optional[str] = ...,
    ) -> None: ...

class EVMBridgeConfig(_message.Message):
    __slots__ = (
        "network_id",
        "chain_id",
        "collateral_bridge_contract",
        "confirmations",
        "multisig_control_contract",
        "block_time",
        "name",
    )
    NETWORK_ID_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    COLLATERAL_BRIDGE_CONTRACT_FIELD_NUMBER: _ClassVar[int]
    CONFIRMATIONS_FIELD_NUMBER: _ClassVar[int]
    MULTISIG_CONTROL_CONTRACT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    network_id: str
    chain_id: str
    collateral_bridge_contract: EthereumContractConfig
    confirmations: int
    multisig_control_contract: EthereumContractConfig
    block_time: str
    name: str
    def __init__(
        self,
        network_id: _Optional[str] = ...,
        chain_id: _Optional[str] = ...,
        collateral_bridge_contract: _Optional[
            _Union[EthereumContractConfig, _Mapping]
        ] = ...,
        confirmations: _Optional[int] = ...,
        multisig_control_contract: _Optional[
            _Union[EthereumContractConfig, _Mapping]
        ] = ...,
        block_time: _Optional[str] = ...,
        name: _Optional[str] = ...,
    ) -> None: ...

class EVMBridgeConfigs(_message.Message):
    __slots__ = ("configs",)
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    configs: _containers.RepeatedCompositeFieldContainer[EVMBridgeConfig]
    def __init__(
        self, configs: _Optional[_Iterable[_Union[EVMBridgeConfig, _Mapping]]] = ...
    ) -> None: ...

class EthereumContractConfig(_message.Message):
    __slots__ = ("address", "deployment_block_height")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    address: str
    deployment_block_height: int
    def __init__(
        self,
        address: _Optional[str] = ...,
        deployment_block_height: _Optional[int] = ...,
    ) -> None: ...

class EpochTimestamps(_message.Message):
    __slots__ = ("start_time", "expiry_time", "end_time", "first_block", "last_block")
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    FIRST_BLOCK_FIELD_NUMBER: _ClassVar[int]
    LAST_BLOCK_FIELD_NUMBER: _ClassVar[int]
    start_time: int
    expiry_time: int
    end_time: int
    first_block: int
    last_block: int
    def __init__(
        self,
        start_time: _Optional[int] = ...,
        expiry_time: _Optional[int] = ...,
        end_time: _Optional[int] = ...,
        first_block: _Optional[int] = ...,
        last_block: _Optional[int] = ...,
    ) -> None: ...

class Epoch(_message.Message):
    __slots__ = ("seq", "timestamps", "validators", "delegations")
    SEQ_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    VALIDATORS_FIELD_NUMBER: _ClassVar[int]
    DELEGATIONS_FIELD_NUMBER: _ClassVar[int]
    seq: int
    timestamps: EpochTimestamps
    validators: _containers.RepeatedCompositeFieldContainer[Node]
    delegations: _containers.RepeatedCompositeFieldContainer[Delegation]
    def __init__(
        self,
        seq: _Optional[int] = ...,
        timestamps: _Optional[_Union[EpochTimestamps, _Mapping]] = ...,
        validators: _Optional[_Iterable[_Union[Node, _Mapping]]] = ...,
        delegations: _Optional[_Iterable[_Union[Delegation, _Mapping]]] = ...,
    ) -> None: ...

class EpochParticipation(_message.Message):
    __slots__ = ("epoch", "offline", "online", "total_rewards")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REWARDS_FIELD_NUMBER: _ClassVar[int]
    epoch: Epoch
    offline: int
    online: int
    total_rewards: float
    def __init__(
        self,
        epoch: _Optional[_Union[Epoch, _Mapping]] = ...,
        offline: _Optional[int] = ...,
        online: _Optional[int] = ...,
        total_rewards: _Optional[float] = ...,
    ) -> None: ...

class EpochData(_message.Message):
    __slots__ = ("total", "offline", "online")
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    total: int
    offline: int
    online: int
    def __init__(
        self,
        total: _Optional[int] = ...,
        offline: _Optional[int] = ...,
        online: _Optional[int] = ...,
    ) -> None: ...

class RankingScore(_message.Message):
    __slots__ = (
        "stake_score",
        "performance_score",
        "previous_status",
        "status",
        "voting_power",
        "ranking_score",
    )
    STAKE_SCORE_FIELD_NUMBER: _ClassVar[int]
    PERFORMANCE_SCORE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VOTING_POWER_FIELD_NUMBER: _ClassVar[int]
    RANKING_SCORE_FIELD_NUMBER: _ClassVar[int]
    stake_score: str
    performance_score: str
    previous_status: ValidatorNodeStatus
    status: ValidatorNodeStatus
    voting_power: int
    ranking_score: str
    def __init__(
        self,
        stake_score: _Optional[str] = ...,
        performance_score: _Optional[str] = ...,
        previous_status: _Optional[_Union[ValidatorNodeStatus, str]] = ...,
        status: _Optional[_Union[ValidatorNodeStatus, str]] = ...,
        voting_power: _Optional[int] = ...,
        ranking_score: _Optional[str] = ...,
    ) -> None: ...

class RewardScore(_message.Message):
    __slots__ = (
        "raw_validator_score",
        "performance_score",
        "multisig_score",
        "validator_score",
        "normalised_score",
        "validator_status",
    )
    RAW_VALIDATOR_SCORE_FIELD_NUMBER: _ClassVar[int]
    PERFORMANCE_SCORE_FIELD_NUMBER: _ClassVar[int]
    MULTISIG_SCORE_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_SCORE_FIELD_NUMBER: _ClassVar[int]
    NORMALISED_SCORE_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_STATUS_FIELD_NUMBER: _ClassVar[int]
    raw_validator_score: str
    performance_score: str
    multisig_score: str
    validator_score: str
    normalised_score: str
    validator_status: ValidatorNodeStatus
    def __init__(
        self,
        raw_validator_score: _Optional[str] = ...,
        performance_score: _Optional[str] = ...,
        multisig_score: _Optional[str] = ...,
        validator_score: _Optional[str] = ...,
        normalised_score: _Optional[str] = ...,
        validator_status: _Optional[_Union[ValidatorNodeStatus, str]] = ...,
    ) -> None: ...

class Node(_message.Message):
    __slots__ = (
        "id",
        "pub_key",
        "tm_pub_key",
        "ethereum_address",
        "info_url",
        "location",
        "staked_by_operator",
        "staked_by_delegates",
        "staked_total",
        "max_intended_stake",
        "pending_stake",
        "epoch_data",
        "status",
        "delegations",
        "reward_score",
        "ranking_score",
        "name",
        "avatar_url",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    TM_PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    INFO_URL_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    STAKED_BY_OPERATOR_FIELD_NUMBER: _ClassVar[int]
    STAKED_BY_DELEGATES_FIELD_NUMBER: _ClassVar[int]
    STAKED_TOTAL_FIELD_NUMBER: _ClassVar[int]
    MAX_INTENDED_STAKE_FIELD_NUMBER: _ClassVar[int]
    PENDING_STAKE_FIELD_NUMBER: _ClassVar[int]
    EPOCH_DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DELEGATIONS_FIELD_NUMBER: _ClassVar[int]
    REWARD_SCORE_FIELD_NUMBER: _ClassVar[int]
    RANKING_SCORE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    id: str
    pub_key: str
    tm_pub_key: str
    ethereum_address: str
    info_url: str
    location: str
    staked_by_operator: str
    staked_by_delegates: str
    staked_total: str
    max_intended_stake: str
    pending_stake: str
    epoch_data: EpochData
    status: NodeStatus
    delegations: _containers.RepeatedCompositeFieldContainer[Delegation]
    reward_score: RewardScore
    ranking_score: RankingScore
    name: str
    avatar_url: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        pub_key: _Optional[str] = ...,
        tm_pub_key: _Optional[str] = ...,
        ethereum_address: _Optional[str] = ...,
        info_url: _Optional[str] = ...,
        location: _Optional[str] = ...,
        staked_by_operator: _Optional[str] = ...,
        staked_by_delegates: _Optional[str] = ...,
        staked_total: _Optional[str] = ...,
        max_intended_stake: _Optional[str] = ...,
        pending_stake: _Optional[str] = ...,
        epoch_data: _Optional[_Union[EpochData, _Mapping]] = ...,
        status: _Optional[_Union[NodeStatus, str]] = ...,
        delegations: _Optional[_Iterable[_Union[Delegation, _Mapping]]] = ...,
        reward_score: _Optional[_Union[RewardScore, _Mapping]] = ...,
        ranking_score: _Optional[_Union[RankingScore, _Mapping]] = ...,
        name: _Optional[str] = ...,
        avatar_url: _Optional[str] = ...,
    ) -> None: ...

class NodeSet(_message.Message):
    __slots__ = ("total", "inactive", "promoted", "demoted", "maximum")
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    INACTIVE_FIELD_NUMBER: _ClassVar[int]
    PROMOTED_FIELD_NUMBER: _ClassVar[int]
    DEMOTED_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_FIELD_NUMBER: _ClassVar[int]
    total: int
    inactive: int
    promoted: _containers.RepeatedScalarFieldContainer[str]
    demoted: _containers.RepeatedScalarFieldContainer[str]
    maximum: int
    def __init__(
        self,
        total: _Optional[int] = ...,
        inactive: _Optional[int] = ...,
        promoted: _Optional[_Iterable[str]] = ...,
        demoted: _Optional[_Iterable[str]] = ...,
        maximum: _Optional[int] = ...,
    ) -> None: ...

class NodeData(_message.Message):
    __slots__ = (
        "staked_total",
        "total_nodes",
        "inactive_nodes",
        "tendermint_nodes",
        "ersatz_nodes",
        "pending_nodes",
        "uptime",
    )
    STAKED_TOTAL_FIELD_NUMBER: _ClassVar[int]
    TOTAL_NODES_FIELD_NUMBER: _ClassVar[int]
    INACTIVE_NODES_FIELD_NUMBER: _ClassVar[int]
    TENDERMINT_NODES_FIELD_NUMBER: _ClassVar[int]
    ERSATZ_NODES_FIELD_NUMBER: _ClassVar[int]
    PENDING_NODES_FIELD_NUMBER: _ClassVar[int]
    UPTIME_FIELD_NUMBER: _ClassVar[int]
    staked_total: str
    total_nodes: int
    inactive_nodes: int
    tendermint_nodes: NodeSet
    ersatz_nodes: NodeSet
    pending_nodes: NodeSet
    uptime: float
    def __init__(
        self,
        staked_total: _Optional[str] = ...,
        total_nodes: _Optional[int] = ...,
        inactive_nodes: _Optional[int] = ...,
        tendermint_nodes: _Optional[_Union[NodeSet, _Mapping]] = ...,
        ersatz_nodes: _Optional[_Union[NodeSet, _Mapping]] = ...,
        pending_nodes: _Optional[_Union[NodeSet, _Mapping]] = ...,
        uptime: _Optional[float] = ...,
    ) -> None: ...

class Delegation(_message.Message):
    __slots__ = ("party", "node_id", "amount", "epoch_seq")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    party: str
    node_id: str
    amount: str
    epoch_seq: str
    def __init__(
        self,
        party: _Optional[str] = ...,
        node_id: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
    ) -> None: ...

class Reward(_message.Message):
    __slots__ = (
        "asset_id",
        "party_id",
        "epoch",
        "amount",
        "percentage_of_total",
        "received_at",
        "market_id",
        "reward_type",
        "locked_until_epoch",
        "quantum_amount",
        "game_id",
        "team_id",
    )
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_OF_TOTAL_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_AT_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    REWARD_TYPE_FIELD_NUMBER: _ClassVar[int]
    LOCKED_UNTIL_EPOCH_FIELD_NUMBER: _ClassVar[int]
    QUANTUM_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    GAME_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    party_id: str
    epoch: int
    amount: str
    percentage_of_total: str
    received_at: int
    market_id: str
    reward_type: str
    locked_until_epoch: int
    quantum_amount: str
    game_id: str
    team_id: str
    def __init__(
        self,
        asset_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        epoch: _Optional[int] = ...,
        amount: _Optional[str] = ...,
        percentage_of_total: _Optional[str] = ...,
        received_at: _Optional[int] = ...,
        market_id: _Optional[str] = ...,
        reward_type: _Optional[str] = ...,
        locked_until_epoch: _Optional[int] = ...,
        quantum_amount: _Optional[str] = ...,
        game_id: _Optional[str] = ...,
        team_id: _Optional[str] = ...,
    ) -> None: ...

class RewardSummary(_message.Message):
    __slots__ = ("asset_id", "party_id", "amount")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    party_id: str
    amount: str
    def __init__(
        self,
        asset_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        amount: _Optional[str] = ...,
    ) -> None: ...

class EpochRewardSummary(_message.Message):
    __slots__ = ("epoch", "asset_id", "market_id", "reward_type", "amount")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    REWARD_TYPE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    epoch: int
    asset_id: str
    market_id: str
    reward_type: str
    amount: str
    def __init__(
        self,
        epoch: _Optional[int] = ...,
        asset_id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        reward_type: _Optional[str] = ...,
        amount: _Optional[str] = ...,
    ) -> None: ...

class StateValueProposal(_message.Message):
    __slots__ = ("state_var_id", "event_id", "kvb")
    STATE_VAR_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    KVB_FIELD_NUMBER: _ClassVar[int]
    state_var_id: str
    event_id: str
    kvb: _containers.RepeatedCompositeFieldContainer[KeyValueBundle]
    def __init__(
        self,
        state_var_id: _Optional[str] = ...,
        event_id: _Optional[str] = ...,
        kvb: _Optional[_Iterable[_Union[KeyValueBundle, _Mapping]]] = ...,
    ) -> None: ...

class KeyValueBundle(_message.Message):
    __slots__ = ("key", "tolerance", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    tolerance: str
    value: StateVarValue
    def __init__(
        self,
        key: _Optional[str] = ...,
        tolerance: _Optional[str] = ...,
        value: _Optional[_Union[StateVarValue, _Mapping]] = ...,
    ) -> None: ...

class StateVarValue(_message.Message):
    __slots__ = ("scalar_val", "vector_val", "matrix_val")
    SCALAR_VAL_FIELD_NUMBER: _ClassVar[int]
    VECTOR_VAL_FIELD_NUMBER: _ClassVar[int]
    MATRIX_VAL_FIELD_NUMBER: _ClassVar[int]
    scalar_val: ScalarValue
    vector_val: VectorValue
    matrix_val: MatrixValue
    def __init__(
        self,
        scalar_val: _Optional[_Union[ScalarValue, _Mapping]] = ...,
        vector_val: _Optional[_Union[VectorValue, _Mapping]] = ...,
        matrix_val: _Optional[_Union[MatrixValue, _Mapping]] = ...,
    ) -> None: ...

class ScalarValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class VectorValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, value: _Optional[_Iterable[str]] = ...) -> None: ...

class MatrixValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedCompositeFieldContainer[VectorValue]
    def __init__(
        self, value: _Optional[_Iterable[_Union[VectorValue, _Mapping]]] = ...
    ) -> None: ...

class ReferralProgram(_message.Message):
    __slots__ = (
        "version",
        "id",
        "benefit_tiers",
        "end_of_program_timestamp",
        "window_length",
        "staking_tiers",
    )
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    BENEFIT_TIERS_FIELD_NUMBER: _ClassVar[int]
    END_OF_PROGRAM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WINDOW_LENGTH_FIELD_NUMBER: _ClassVar[int]
    STAKING_TIERS_FIELD_NUMBER: _ClassVar[int]
    version: int
    id: str
    benefit_tiers: _containers.RepeatedCompositeFieldContainer[BenefitTier]
    end_of_program_timestamp: int
    window_length: int
    staking_tiers: _containers.RepeatedCompositeFieldContainer[StakingTier]
    def __init__(
        self,
        version: _Optional[int] = ...,
        id: _Optional[str] = ...,
        benefit_tiers: _Optional[_Iterable[_Union[BenefitTier, _Mapping]]] = ...,
        end_of_program_timestamp: _Optional[int] = ...,
        window_length: _Optional[int] = ...,
        staking_tiers: _Optional[_Iterable[_Union[StakingTier, _Mapping]]] = ...,
    ) -> None: ...

class VolumeBenefitTier(_message.Message):
    __slots__ = (
        "minimum_running_notional_taker_volume",
        "volume_discount_factor",
        "volume_discount_factors",
        "tier_number",
    )
    MINIMUM_RUNNING_NOTIONAL_TAKER_VOLUME_FIELD_NUMBER: _ClassVar[int]
    VOLUME_DISCOUNT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    VOLUME_DISCOUNT_FACTORS_FIELD_NUMBER: _ClassVar[int]
    TIER_NUMBER_FIELD_NUMBER: _ClassVar[int]
    minimum_running_notional_taker_volume: str
    volume_discount_factor: str
    volume_discount_factors: DiscountFactors
    tier_number: int
    def __init__(
        self,
        minimum_running_notional_taker_volume: _Optional[str] = ...,
        volume_discount_factor: _Optional[str] = ...,
        volume_discount_factors: _Optional[_Union[DiscountFactors, _Mapping]] = ...,
        tier_number: _Optional[int] = ...,
    ) -> None: ...

class BenefitTier(_message.Message):
    __slots__ = (
        "minimum_running_notional_taker_volume",
        "minimum_epochs",
        "referral_reward_factor",
        "referral_discount_factor",
        "referral_reward_factors",
        "referral_discount_factors",
        "tier_number",
    )
    MINIMUM_RUNNING_NOTIONAL_TAKER_VOLUME_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_EPOCHS_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_REWARD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_DISCOUNT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_REWARD_FACTORS_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_DISCOUNT_FACTORS_FIELD_NUMBER: _ClassVar[int]
    TIER_NUMBER_FIELD_NUMBER: _ClassVar[int]
    minimum_running_notional_taker_volume: str
    minimum_epochs: str
    referral_reward_factor: str
    referral_discount_factor: str
    referral_reward_factors: RewardFactors
    referral_discount_factors: DiscountFactors
    tier_number: int
    def __init__(
        self,
        minimum_running_notional_taker_volume: _Optional[str] = ...,
        minimum_epochs: _Optional[str] = ...,
        referral_reward_factor: _Optional[str] = ...,
        referral_discount_factor: _Optional[str] = ...,
        referral_reward_factors: _Optional[_Union[RewardFactors, _Mapping]] = ...,
        referral_discount_factors: _Optional[_Union[DiscountFactors, _Mapping]] = ...,
        tier_number: _Optional[int] = ...,
    ) -> None: ...

class RewardFactors(_message.Message):
    __slots__ = (
        "infrastructure_reward_factor",
        "liquidity_reward_factor",
        "maker_reward_factor",
    )
    INFRASTRUCTURE_REWARD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_REWARD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    MAKER_REWARD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    infrastructure_reward_factor: str
    liquidity_reward_factor: str
    maker_reward_factor: str
    def __init__(
        self,
        infrastructure_reward_factor: _Optional[str] = ...,
        liquidity_reward_factor: _Optional[str] = ...,
        maker_reward_factor: _Optional[str] = ...,
    ) -> None: ...

class DiscountFactors(_message.Message):
    __slots__ = (
        "infrastructure_discount_factor",
        "liquidity_discount_factor",
        "maker_discount_factor",
    )
    INFRASTRUCTURE_DISCOUNT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_DISCOUNT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    MAKER_DISCOUNT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    infrastructure_discount_factor: str
    liquidity_discount_factor: str
    maker_discount_factor: str
    def __init__(
        self,
        infrastructure_discount_factor: _Optional[str] = ...,
        liquidity_discount_factor: _Optional[str] = ...,
        maker_discount_factor: _Optional[str] = ...,
    ) -> None: ...

class VestingBenefitTiers(_message.Message):
    __slots__ = ("tiers",)
    TIERS_FIELD_NUMBER: _ClassVar[int]
    tiers: _containers.RepeatedCompositeFieldContainer[VestingBenefitTier]
    def __init__(
        self, tiers: _Optional[_Iterable[_Union[VestingBenefitTier, _Mapping]]] = ...
    ) -> None: ...

class VestingBenefitTier(_message.Message):
    __slots__ = ("minimum_quantum_balance", "reward_multiplier")
    MINIMUM_QUANTUM_BALANCE_FIELD_NUMBER: _ClassVar[int]
    REWARD_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    minimum_quantum_balance: str
    reward_multiplier: str
    def __init__(
        self,
        minimum_quantum_balance: _Optional[str] = ...,
        reward_multiplier: _Optional[str] = ...,
    ) -> None: ...

class StakingTier(_message.Message):
    __slots__ = ("minimum_staked_tokens", "referral_reward_multiplier")
    MINIMUM_STAKED_TOKENS_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_REWARD_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    minimum_staked_tokens: str
    referral_reward_multiplier: str
    def __init__(
        self,
        minimum_staked_tokens: _Optional[str] = ...,
        referral_reward_multiplier: _Optional[str] = ...,
    ) -> None: ...

class VolumeDiscountProgram(_message.Message):
    __slots__ = (
        "version",
        "id",
        "benefit_tiers",
        "end_of_program_timestamp",
        "window_length",
    )
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    BENEFIT_TIERS_FIELD_NUMBER: _ClassVar[int]
    END_OF_PROGRAM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WINDOW_LENGTH_FIELD_NUMBER: _ClassVar[int]
    version: int
    id: str
    benefit_tiers: _containers.RepeatedCompositeFieldContainer[VolumeBenefitTier]
    end_of_program_timestamp: int
    window_length: int
    def __init__(
        self,
        version: _Optional[int] = ...,
        id: _Optional[str] = ...,
        benefit_tiers: _Optional[_Iterable[_Union[VolumeBenefitTier, _Mapping]]] = ...,
        end_of_program_timestamp: _Optional[int] = ...,
        window_length: _Optional[int] = ...,
    ) -> None: ...

class ActivityStreakBenefitTiers(_message.Message):
    __slots__ = ("tiers",)
    TIERS_FIELD_NUMBER: _ClassVar[int]
    tiers: _containers.RepeatedCompositeFieldContainer[ActivityStreakBenefitTier]
    def __init__(
        self,
        tiers: _Optional[_Iterable[_Union[ActivityStreakBenefitTier, _Mapping]]] = ...,
    ) -> None: ...

class ActivityStreakBenefitTier(_message.Message):
    __slots__ = ("minimum_activity_streak", "reward_multiplier", "vesting_multiplier")
    MINIMUM_ACTIVITY_STREAK_FIELD_NUMBER: _ClassVar[int]
    REWARD_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    VESTING_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    minimum_activity_streak: int
    reward_multiplier: str
    vesting_multiplier: str
    def __init__(
        self,
        minimum_activity_streak: _Optional[int] = ...,
        reward_multiplier: _Optional[str] = ...,
        vesting_multiplier: _Optional[str] = ...,
    ) -> None: ...

class LongBlockAuction(_message.Message):
    __slots__ = ("threshold", "duration")
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    threshold: str
    duration: str
    def __init__(
        self, threshold: _Optional[str] = ..., duration: _Optional[str] = ...
    ) -> None: ...

class LongBlockAuctionDurationTable(_message.Message):
    __slots__ = ("threshold_and_duration",)
    THRESHOLD_AND_DURATION_FIELD_NUMBER: _ClassVar[int]
    threshold_and_duration: _containers.RepeatedCompositeFieldContainer[
        LongBlockAuction
    ]
    def __init__(
        self,
        threshold_and_duration: _Optional[
            _Iterable[_Union[LongBlockAuction, _Mapping]]
        ] = ...,
    ) -> None: ...

class VolumeRebateBenefitTier(_message.Message):
    __slots__ = (
        "minimum_party_maker_volume_fraction",
        "additional_maker_rebate",
        "tier_number",
    )
    MINIMUM_PARTY_MAKER_VOLUME_FRACTION_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_MAKER_REBATE_FIELD_NUMBER: _ClassVar[int]
    TIER_NUMBER_FIELD_NUMBER: _ClassVar[int]
    minimum_party_maker_volume_fraction: str
    additional_maker_rebate: str
    tier_number: int
    def __init__(
        self,
        minimum_party_maker_volume_fraction: _Optional[str] = ...,
        additional_maker_rebate: _Optional[str] = ...,
        tier_number: _Optional[int] = ...,
    ) -> None: ...

class VolumeRebateProgram(_message.Message):
    __slots__ = (
        "version",
        "id",
        "benefit_tiers",
        "end_of_program_timestamp",
        "window_length",
    )
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    BENEFIT_TIERS_FIELD_NUMBER: _ClassVar[int]
    END_OF_PROGRAM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WINDOW_LENGTH_FIELD_NUMBER: _ClassVar[int]
    version: int
    id: str
    benefit_tiers: _containers.RepeatedCompositeFieldContainer[VolumeRebateBenefitTier]
    end_of_program_timestamp: int
    window_length: int
    def __init__(
        self,
        version: _Optional[int] = ...,
        id: _Optional[str] = ...,
        benefit_tiers: _Optional[
            _Iterable[_Union[VolumeRebateBenefitTier, _Mapping]]
        ] = ...,
        end_of_program_timestamp: _Optional[int] = ...,
        window_length: _Optional[int] = ...,
    ) -> None: ...
