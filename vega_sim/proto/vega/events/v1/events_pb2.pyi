from vega import assets_pb2 as _assets_pb2
from vega.commands.v1 import commands_pb2 as _commands_pb2
from vega.commands.v1 import data_pb2 as _data_pb2
from vega.commands.v1 import validator_commands_pb2 as _validator_commands_pb2
from vega import governance_pb2 as _governance_pb2
from vega import markets_pb2 as _markets_pb2
from vega import oracle_pb2 as _oracle_pb2
from vega import vega_pb2 as _vega_pb2
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

class ProtocolUpgradeProposalStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROTOCOL_UPGRADE_PROPOSAL_STATUS_UNSPECIFIED: _ClassVar[
        ProtocolUpgradeProposalStatus
    ]
    PROTOCOL_UPGRADE_PROPOSAL_STATUS_PENDING: _ClassVar[ProtocolUpgradeProposalStatus]
    PROTOCOL_UPGRADE_PROPOSAL_STATUS_APPROVED: _ClassVar[ProtocolUpgradeProposalStatus]
    PROTOCOL_UPGRADE_PROPOSAL_STATUS_REJECTED: _ClassVar[ProtocolUpgradeProposalStatus]

class BusEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BUS_EVENT_TYPE_UNSPECIFIED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_ALL: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_TIME_UPDATE: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_LEDGER_MOVEMENTS: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_POSITION_RESOLUTION: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_ORDER: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_ACCOUNT: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_PARTY: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_TRADE: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_MARGIN_LEVELS: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_PROPOSAL: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_VOTE: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_MARKET_DATA: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_NODE_SIGNATURE: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_LOSS_SOCIALIZATION: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_SETTLE_POSITION: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_SETTLE_DISTRESSED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_MARKET_CREATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_ASSET: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_MARKET_TICK: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_WITHDRAWAL: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_DEPOSIT: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_AUCTION: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_RISK_FACTOR: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_NETWORK_PARAMETER: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_LIQUIDITY_PROVISION: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_MARKET_UPDATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_ORACLE_SPEC: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_ORACLE_DATA: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_DELEGATION_BALANCE: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_VALIDATOR_SCORE: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_EPOCH_UPDATE: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_VALIDATOR_UPDATE: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_STAKE_LINKING: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_REWARD_PAYOUT_EVENT: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_CHECKPOINT: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_STREAM_START: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_KEY_ROTATION: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_STATE_VAR: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_NETWORK_LIMITS: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_TRANSFER: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_VALIDATOR_RANKING: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_ERC20_MULTI_SIG_SIGNER_EVENT: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_ERC20_MULTI_SIG_SET_THRESHOLD: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_ERC20_MULTI_SIG_SIGNER_ADDED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_ERC20_MULTI_SIG_SIGNER_REMOVED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_POSITION_STATE: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_ETHEREUM_KEY_ROTATION: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_PROTOCOL_UPGRADE_PROPOSAL: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_BEGIN_BLOCK: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_END_BLOCK: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_PROTOCOL_UPGRADE_STARTED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_SETTLE_MARKET: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_TRANSACTION_RESULT: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_SNAPSHOT_TAKEN: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_PROTOCOL_UPGRADE_DATA_NODE_READY: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_DISTRESSED_ORDERS_CLOSED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_EXPIRED_ORDERS: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_DISTRESSED_POSITIONS: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_SPOT_LIQUIDITY_PROVISION: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_STOP_ORDER: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_FUNDING_PERIOD: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_FUNDING_PERIOD_DATA_POINT: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_TEAM_CREATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_TEAM_UPDATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_REFEREE_SWITCHED_TEAM: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_REFEREE_JOINED_TEAM: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_REFERRAL_PROGRAM_STARTED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_REFERRAL_PROGRAM_UPDATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_REFERRAL_PROGRAM_ENDED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_REFERRAL_SET_CREATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_REFEREE_JOINED_REFERRAL_SET: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_PARTY_ACTIVITY_STREAK: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_VOLUME_DISCOUNT_PROGRAM_STARTED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_VOLUME_DISCOUNT_PROGRAM_UPDATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_VOLUME_DISCOUNT_PROGRAM_ENDED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_REFERRAL_SET_STATS_UPDATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_VESTING_STATS_UPDATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_VOLUME_DISCOUNT_STATS_UPDATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_FEES_STATS_UPDATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_FUNDING_PAYMENTS: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_PAID_LIQUIDITY_FEES_STATS_UPDATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_VESTING_SUMMARY: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_TRANSFER_FEES_PAID: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_TRANSFER_FEES_DISCOUNT_UPDATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_PARTY_MARGIN_MODE_UPDATED: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_MARKET: _ClassVar[BusEventType]
    BUS_EVENT_TYPE_TX_ERROR: _ClassVar[BusEventType]

PROTOCOL_UPGRADE_PROPOSAL_STATUS_UNSPECIFIED: ProtocolUpgradeProposalStatus
PROTOCOL_UPGRADE_PROPOSAL_STATUS_PENDING: ProtocolUpgradeProposalStatus
PROTOCOL_UPGRADE_PROPOSAL_STATUS_APPROVED: ProtocolUpgradeProposalStatus
PROTOCOL_UPGRADE_PROPOSAL_STATUS_REJECTED: ProtocolUpgradeProposalStatus
BUS_EVENT_TYPE_UNSPECIFIED: BusEventType
BUS_EVENT_TYPE_ALL: BusEventType
BUS_EVENT_TYPE_TIME_UPDATE: BusEventType
BUS_EVENT_TYPE_LEDGER_MOVEMENTS: BusEventType
BUS_EVENT_TYPE_POSITION_RESOLUTION: BusEventType
BUS_EVENT_TYPE_ORDER: BusEventType
BUS_EVENT_TYPE_ACCOUNT: BusEventType
BUS_EVENT_TYPE_PARTY: BusEventType
BUS_EVENT_TYPE_TRADE: BusEventType
BUS_EVENT_TYPE_MARGIN_LEVELS: BusEventType
BUS_EVENT_TYPE_PROPOSAL: BusEventType
BUS_EVENT_TYPE_VOTE: BusEventType
BUS_EVENT_TYPE_MARKET_DATA: BusEventType
BUS_EVENT_TYPE_NODE_SIGNATURE: BusEventType
BUS_EVENT_TYPE_LOSS_SOCIALIZATION: BusEventType
BUS_EVENT_TYPE_SETTLE_POSITION: BusEventType
BUS_EVENT_TYPE_SETTLE_DISTRESSED: BusEventType
BUS_EVENT_TYPE_MARKET_CREATED: BusEventType
BUS_EVENT_TYPE_ASSET: BusEventType
BUS_EVENT_TYPE_MARKET_TICK: BusEventType
BUS_EVENT_TYPE_WITHDRAWAL: BusEventType
BUS_EVENT_TYPE_DEPOSIT: BusEventType
BUS_EVENT_TYPE_AUCTION: BusEventType
BUS_EVENT_TYPE_RISK_FACTOR: BusEventType
BUS_EVENT_TYPE_NETWORK_PARAMETER: BusEventType
BUS_EVENT_TYPE_LIQUIDITY_PROVISION: BusEventType
BUS_EVENT_TYPE_MARKET_UPDATED: BusEventType
BUS_EVENT_TYPE_ORACLE_SPEC: BusEventType
BUS_EVENT_TYPE_ORACLE_DATA: BusEventType
BUS_EVENT_TYPE_DELEGATION_BALANCE: BusEventType
BUS_EVENT_TYPE_VALIDATOR_SCORE: BusEventType
BUS_EVENT_TYPE_EPOCH_UPDATE: BusEventType
BUS_EVENT_TYPE_VALIDATOR_UPDATE: BusEventType
BUS_EVENT_TYPE_STAKE_LINKING: BusEventType
BUS_EVENT_TYPE_REWARD_PAYOUT_EVENT: BusEventType
BUS_EVENT_TYPE_CHECKPOINT: BusEventType
BUS_EVENT_TYPE_STREAM_START: BusEventType
BUS_EVENT_TYPE_KEY_ROTATION: BusEventType
BUS_EVENT_TYPE_STATE_VAR: BusEventType
BUS_EVENT_TYPE_NETWORK_LIMITS: BusEventType
BUS_EVENT_TYPE_TRANSFER: BusEventType
BUS_EVENT_TYPE_VALIDATOR_RANKING: BusEventType
BUS_EVENT_TYPE_ERC20_MULTI_SIG_SIGNER_EVENT: BusEventType
BUS_EVENT_TYPE_ERC20_MULTI_SIG_SET_THRESHOLD: BusEventType
BUS_EVENT_TYPE_ERC20_MULTI_SIG_SIGNER_ADDED: BusEventType
BUS_EVENT_TYPE_ERC20_MULTI_SIG_SIGNER_REMOVED: BusEventType
BUS_EVENT_TYPE_POSITION_STATE: BusEventType
BUS_EVENT_TYPE_ETHEREUM_KEY_ROTATION: BusEventType
BUS_EVENT_TYPE_PROTOCOL_UPGRADE_PROPOSAL: BusEventType
BUS_EVENT_TYPE_BEGIN_BLOCK: BusEventType
BUS_EVENT_TYPE_END_BLOCK: BusEventType
BUS_EVENT_TYPE_PROTOCOL_UPGRADE_STARTED: BusEventType
BUS_EVENT_TYPE_SETTLE_MARKET: BusEventType
BUS_EVENT_TYPE_TRANSACTION_RESULT: BusEventType
BUS_EVENT_TYPE_SNAPSHOT_TAKEN: BusEventType
BUS_EVENT_TYPE_PROTOCOL_UPGRADE_DATA_NODE_READY: BusEventType
BUS_EVENT_TYPE_DISTRESSED_ORDERS_CLOSED: BusEventType
BUS_EVENT_TYPE_EXPIRED_ORDERS: BusEventType
BUS_EVENT_TYPE_DISTRESSED_POSITIONS: BusEventType
BUS_EVENT_TYPE_SPOT_LIQUIDITY_PROVISION: BusEventType
BUS_EVENT_TYPE_STOP_ORDER: BusEventType
BUS_EVENT_TYPE_FUNDING_PERIOD: BusEventType
BUS_EVENT_TYPE_FUNDING_PERIOD_DATA_POINT: BusEventType
BUS_EVENT_TYPE_TEAM_CREATED: BusEventType
BUS_EVENT_TYPE_TEAM_UPDATED: BusEventType
BUS_EVENT_TYPE_REFEREE_SWITCHED_TEAM: BusEventType
BUS_EVENT_TYPE_REFEREE_JOINED_TEAM: BusEventType
BUS_EVENT_TYPE_REFERRAL_PROGRAM_STARTED: BusEventType
BUS_EVENT_TYPE_REFERRAL_PROGRAM_UPDATED: BusEventType
BUS_EVENT_TYPE_REFERRAL_PROGRAM_ENDED: BusEventType
BUS_EVENT_TYPE_REFERRAL_SET_CREATED: BusEventType
BUS_EVENT_TYPE_REFEREE_JOINED_REFERRAL_SET: BusEventType
BUS_EVENT_TYPE_PARTY_ACTIVITY_STREAK: BusEventType
BUS_EVENT_TYPE_VOLUME_DISCOUNT_PROGRAM_STARTED: BusEventType
BUS_EVENT_TYPE_VOLUME_DISCOUNT_PROGRAM_UPDATED: BusEventType
BUS_EVENT_TYPE_VOLUME_DISCOUNT_PROGRAM_ENDED: BusEventType
BUS_EVENT_TYPE_REFERRAL_SET_STATS_UPDATED: BusEventType
BUS_EVENT_TYPE_VESTING_STATS_UPDATED: BusEventType
BUS_EVENT_TYPE_VOLUME_DISCOUNT_STATS_UPDATED: BusEventType
BUS_EVENT_TYPE_FEES_STATS_UPDATED: BusEventType
BUS_EVENT_TYPE_FUNDING_PAYMENTS: BusEventType
BUS_EVENT_TYPE_PAID_LIQUIDITY_FEES_STATS_UPDATED: BusEventType
BUS_EVENT_TYPE_VESTING_SUMMARY: BusEventType
BUS_EVENT_TYPE_TRANSFER_FEES_PAID: BusEventType
BUS_EVENT_TYPE_TRANSFER_FEES_DISCOUNT_UPDATED: BusEventType
BUS_EVENT_TYPE_PARTY_MARGIN_MODE_UPDATED: BusEventType
BUS_EVENT_TYPE_MARKET: BusEventType
BUS_EVENT_TYPE_TX_ERROR: BusEventType

class VestingBalancesSummary(_message.Message):
    __slots__ = ("epoch_seq", "parties_vesting_summary")
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    PARTIES_VESTING_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    epoch_seq: int
    parties_vesting_summary: _containers.RepeatedCompositeFieldContainer[
        PartyVestingSummary
    ]
    def __init__(
        self,
        epoch_seq: _Optional[int] = ...,
        parties_vesting_summary: _Optional[
            _Iterable[_Union[PartyVestingSummary, _Mapping]]
        ] = ...,
    ) -> None: ...

class PartyVestingSummary(_message.Message):
    __slots__ = ("party", "party_locked_balances", "party_vesting_balances")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    PARTY_LOCKED_BALANCES_FIELD_NUMBER: _ClassVar[int]
    PARTY_VESTING_BALANCES_FIELD_NUMBER: _ClassVar[int]
    party: str
    party_locked_balances: _containers.RepeatedCompositeFieldContainer[
        PartyLockedBalance
    ]
    party_vesting_balances: _containers.RepeatedCompositeFieldContainer[
        PartyVestingBalance
    ]
    def __init__(
        self,
        party: _Optional[str] = ...,
        party_locked_balances: _Optional[
            _Iterable[_Union[PartyLockedBalance, _Mapping]]
        ] = ...,
        party_vesting_balances: _Optional[
            _Iterable[_Union[PartyVestingBalance, _Mapping]]
        ] = ...,
    ) -> None: ...

class PartyLockedBalance(_message.Message):
    __slots__ = ("asset", "until_epoch", "balance")
    ASSET_FIELD_NUMBER: _ClassVar[int]
    UNTIL_EPOCH_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    asset: str
    until_epoch: int
    balance: str
    def __init__(
        self,
        asset: _Optional[str] = ...,
        until_epoch: _Optional[int] = ...,
        balance: _Optional[str] = ...,
    ) -> None: ...

class PartyVestingBalance(_message.Message):
    __slots__ = ("asset", "balance")
    ASSET_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    asset: str
    balance: str
    def __init__(
        self, asset: _Optional[str] = ..., balance: _Optional[str] = ...
    ) -> None: ...

class VolumeDiscountStatsUpdated(_message.Message):
    __slots__ = ("at_epoch", "stats")
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    at_epoch: int
    stats: _containers.RepeatedCompositeFieldContainer[PartyVolumeDiscountStats]
    def __init__(
        self,
        at_epoch: _Optional[int] = ...,
        stats: _Optional[_Iterable[_Union[PartyVolumeDiscountStats, _Mapping]]] = ...,
    ) -> None: ...

class PartyVolumeDiscountStats(_message.Message):
    __slots__ = ("party_id", "discount_factor", "running_volume")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    RUNNING_VOLUME_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    discount_factor: str
    running_volume: str
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        discount_factor: _Optional[str] = ...,
        running_volume: _Optional[str] = ...,
    ) -> None: ...

class VestingStatsUpdated(_message.Message):
    __slots__ = ("at_epoch", "stats")
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    at_epoch: int
    stats: _containers.RepeatedCompositeFieldContainer[PartyVestingStats]
    def __init__(
        self,
        at_epoch: _Optional[int] = ...,
        stats: _Optional[_Iterable[_Union[PartyVestingStats, _Mapping]]] = ...,
    ) -> None: ...

class PartyVestingStats(_message.Message):
    __slots__ = ("party_id", "reward_bonus_multiplier", "quantum_balance")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    REWARD_BONUS_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    QUANTUM_BALANCE_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    reward_bonus_multiplier: str
    quantum_balance: str
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        reward_bonus_multiplier: _Optional[str] = ...,
        quantum_balance: _Optional[str] = ...,
    ) -> None: ...

class FeesStats(_message.Message):
    __slots__ = (
        "market",
        "asset",
        "epoch_seq",
        "total_rewards_received",
        "referrer_rewards_generated",
        "referees_discount_applied",
        "volume_discount_applied",
        "total_maker_fees_received",
        "maker_fees_generated",
        "total_fees_paid_and_received",
    )
    MARKET_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REWARDS_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    REFERRER_REWARDS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    REFEREES_DISCOUNT_APPLIED_FIELD_NUMBER: _ClassVar[int]
    VOLUME_DISCOUNT_APPLIED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_MAKER_FEES_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    MAKER_FEES_GENERATED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FEES_PAID_AND_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    market: str
    asset: str
    epoch_seq: int
    total_rewards_received: _containers.RepeatedCompositeFieldContainer[PartyAmount]
    referrer_rewards_generated: _containers.RepeatedCompositeFieldContainer[
        ReferrerRewardsGenerated
    ]
    referees_discount_applied: _containers.RepeatedCompositeFieldContainer[PartyAmount]
    volume_discount_applied: _containers.RepeatedCompositeFieldContainer[PartyAmount]
    total_maker_fees_received: _containers.RepeatedCompositeFieldContainer[PartyAmount]
    maker_fees_generated: _containers.RepeatedCompositeFieldContainer[
        MakerFeesGenerated
    ]
    total_fees_paid_and_received: _containers.RepeatedCompositeFieldContainer[
        PartyAmount
    ]
    def __init__(
        self,
        market: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        epoch_seq: _Optional[int] = ...,
        total_rewards_received: _Optional[
            _Iterable[_Union[PartyAmount, _Mapping]]
        ] = ...,
        referrer_rewards_generated: _Optional[
            _Iterable[_Union[ReferrerRewardsGenerated, _Mapping]]
        ] = ...,
        referees_discount_applied: _Optional[
            _Iterable[_Union[PartyAmount, _Mapping]]
        ] = ...,
        volume_discount_applied: _Optional[
            _Iterable[_Union[PartyAmount, _Mapping]]
        ] = ...,
        total_maker_fees_received: _Optional[
            _Iterable[_Union[PartyAmount, _Mapping]]
        ] = ...,
        maker_fees_generated: _Optional[
            _Iterable[_Union[MakerFeesGenerated, _Mapping]]
        ] = ...,
        total_fees_paid_and_received: _Optional[
            _Iterable[_Union[PartyAmount, _Mapping]]
        ] = ...,
    ) -> None: ...

class ReferrerRewardsGenerated(_message.Message):
    __slots__ = ("referrer", "generated_reward")
    REFERRER_FIELD_NUMBER: _ClassVar[int]
    GENERATED_REWARD_FIELD_NUMBER: _ClassVar[int]
    referrer: str
    generated_reward: _containers.RepeatedCompositeFieldContainer[PartyAmount]
    def __init__(
        self,
        referrer: _Optional[str] = ...,
        generated_reward: _Optional[_Iterable[_Union[PartyAmount, _Mapping]]] = ...,
    ) -> None: ...

class MakerFeesGenerated(_message.Message):
    __slots__ = ("taker", "maker_fees_paid")
    TAKER_FIELD_NUMBER: _ClassVar[int]
    MAKER_FEES_PAID_FIELD_NUMBER: _ClassVar[int]
    taker: str
    maker_fees_paid: _containers.RepeatedCompositeFieldContainer[PartyAmount]
    def __init__(
        self,
        taker: _Optional[str] = ...,
        maker_fees_paid: _Optional[_Iterable[_Union[PartyAmount, _Mapping]]] = ...,
    ) -> None: ...

class PartyAmount(_message.Message):
    __slots__ = ("party", "amount", "quantum_amount")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    QUANTUM_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    party: str
    amount: str
    quantum_amount: str
    def __init__(
        self,
        party: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        quantum_amount: _Optional[str] = ...,
    ) -> None: ...

class PartyActivityStreak(_message.Message):
    __slots__ = (
        "party",
        "active_for",
        "inactive_for",
        "is_active",
        "reward_distribution_activity_multiplier",
        "reward_vesting_activity_multiplier",
        "epoch",
        "traded_volume",
        "open_volume",
    )
    PARTY_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FOR_FIELD_NUMBER: _ClassVar[int]
    INACTIVE_FOR_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    REWARD_DISTRIBUTION_ACTIVITY_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    REWARD_VESTING_ACTIVITY_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    TRADED_VOLUME_FIELD_NUMBER: _ClassVar[int]
    OPEN_VOLUME_FIELD_NUMBER: _ClassVar[int]
    party: str
    active_for: int
    inactive_for: int
    is_active: bool
    reward_distribution_activity_multiplier: str
    reward_vesting_activity_multiplier: str
    epoch: int
    traded_volume: str
    open_volume: str
    def __init__(
        self,
        party: _Optional[str] = ...,
        active_for: _Optional[int] = ...,
        inactive_for: _Optional[int] = ...,
        is_active: bool = ...,
        reward_distribution_activity_multiplier: _Optional[str] = ...,
        reward_vesting_activity_multiplier: _Optional[str] = ...,
        epoch: _Optional[int] = ...,
        traded_volume: _Optional[str] = ...,
        open_volume: _Optional[str] = ...,
    ) -> None: ...

class FundingPeriod(_message.Message):
    __slots__ = (
        "market_id",
        "seq",
        "start",
        "end",
        "funding_payment",
        "funding_rate",
        "internal_twap",
        "external_twap",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    FUNDING_PAYMENT_FIELD_NUMBER: _ClassVar[int]
    FUNDING_RATE_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_TWAP_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_TWAP_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    seq: int
    start: int
    end: int
    funding_payment: str
    funding_rate: str
    internal_twap: str
    external_twap: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        seq: _Optional[int] = ...,
        start: _Optional[int] = ...,
        end: _Optional[int] = ...,
        funding_payment: _Optional[str] = ...,
        funding_rate: _Optional[str] = ...,
        internal_twap: _Optional[str] = ...,
        external_twap: _Optional[str] = ...,
    ) -> None: ...

class FundingPayment(_message.Message):
    __slots__ = ("party_id", "amount")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    amount: str
    def __init__(
        self, party_id: _Optional[str] = ..., amount: _Optional[str] = ...
    ) -> None: ...

class FundingPayments(_message.Message):
    __slots__ = ("market_id", "seq", "payments")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    PAYMENTS_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    seq: int
    payments: _containers.RepeatedCompositeFieldContainer[FundingPayment]
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        seq: _Optional[int] = ...,
        payments: _Optional[_Iterable[_Union[FundingPayment, _Mapping]]] = ...,
    ) -> None: ...

class FundingPeriodDataPoint(_message.Message):
    __slots__ = ("market_id", "seq", "data_point_type", "price", "timestamp", "twap")

    class Source(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SOURCE_UNSPECIFIED: _ClassVar[FundingPeriodDataPoint.Source]
        SOURCE_EXTERNAL: _ClassVar[FundingPeriodDataPoint.Source]
        SOURCE_INTERNAL: _ClassVar[FundingPeriodDataPoint.Source]
    SOURCE_UNSPECIFIED: FundingPeriodDataPoint.Source
    SOURCE_EXTERNAL: FundingPeriodDataPoint.Source
    SOURCE_INTERNAL: FundingPeriodDataPoint.Source
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    DATA_POINT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TWAP_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    seq: int
    data_point_type: FundingPeriodDataPoint.Source
    price: str
    timestamp: int
    twap: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        seq: _Optional[int] = ...,
        data_point_type: _Optional[_Union[FundingPeriodDataPoint.Source, str]] = ...,
        price: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
        twap: _Optional[str] = ...,
    ) -> None: ...

class StopOrderEvent(_message.Message):
    __slots__ = ("submission", "stop_order")
    SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    STOP_ORDER_FIELD_NUMBER: _ClassVar[int]
    submission: _commands_pb2.OrderSubmission
    stop_order: _vega_pb2.StopOrder
    def __init__(
        self,
        submission: _Optional[_Union[_commands_pb2.OrderSubmission, _Mapping]] = ...,
        stop_order: _Optional[_Union[_vega_pb2.StopOrder, _Mapping]] = ...,
    ) -> None: ...

class ERC20MultiSigSignerAdded(_message.Message):
    __slots__ = (
        "signature_id",
        "validator_id",
        "timestamp",
        "new_signer",
        "submitter",
        "nonce",
        "epoch_seq",
    )
    SIGNATURE_ID_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    NEW_SIGNER_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    signature_id: str
    validator_id: str
    timestamp: int
    new_signer: str
    submitter: str
    nonce: str
    epoch_seq: str
    def __init__(
        self,
        signature_id: _Optional[str] = ...,
        validator_id: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
        new_signer: _Optional[str] = ...,
        submitter: _Optional[str] = ...,
        nonce: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
    ) -> None: ...

class ERC20MultiSigSignerRemovedSubmitter(_message.Message):
    __slots__ = ("signature_id", "submitter")
    SIGNATURE_ID_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_FIELD_NUMBER: _ClassVar[int]
    signature_id: str
    submitter: str
    def __init__(
        self, signature_id: _Optional[str] = ..., submitter: _Optional[str] = ...
    ) -> None: ...

class ERC20MultiSigSignerRemoved(_message.Message):
    __slots__ = (
        "signature_submitters",
        "validator_id",
        "timestamp",
        "old_signer",
        "nonce",
        "epoch_seq",
    )
    SIGNATURE_SUBMITTERS_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    OLD_SIGNER_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    signature_submitters: _containers.RepeatedCompositeFieldContainer[
        ERC20MultiSigSignerRemovedSubmitter
    ]
    validator_id: str
    timestamp: int
    old_signer: str
    nonce: str
    epoch_seq: str
    def __init__(
        self,
        signature_submitters: _Optional[
            _Iterable[_Union[ERC20MultiSigSignerRemovedSubmitter, _Mapping]]
        ] = ...,
        validator_id: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
        old_signer: _Optional[str] = ...,
        nonce: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
    ) -> None: ...

class Transfer(_message.Message):
    __slots__ = (
        "id",
        "from_account_type",
        "to",
        "to_account_type",
        "asset",
        "amount",
        "reference",
        "status",
        "timestamp",
        "reason",
        "game_id",
        "one_off",
        "recurring",
        "one_off_governance",
        "recurring_governance",
    )

    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[Transfer.Status]
        STATUS_PENDING: _ClassVar[Transfer.Status]
        STATUS_DONE: _ClassVar[Transfer.Status]
        STATUS_REJECTED: _ClassVar[Transfer.Status]
        STATUS_STOPPED: _ClassVar[Transfer.Status]
        STATUS_CANCELLED: _ClassVar[Transfer.Status]
    STATUS_UNSPECIFIED: Transfer.Status
    STATUS_PENDING: Transfer.Status
    STATUS_DONE: Transfer.Status
    STATUS_REJECTED: Transfer.Status
    STATUS_STOPPED: Transfer.Status
    STATUS_CANCELLED: Transfer.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    FROM_ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    TO_ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    GAME_ID_FIELD_NUMBER: _ClassVar[int]
    ONE_OFF_FIELD_NUMBER: _ClassVar[int]
    RECURRING_FIELD_NUMBER: _ClassVar[int]
    ONE_OFF_GOVERNANCE_FIELD_NUMBER: _ClassVar[int]
    RECURRING_GOVERNANCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    from_account_type: _vega_pb2.AccountType
    to: str
    to_account_type: _vega_pb2.AccountType
    asset: str
    amount: str
    reference: str
    status: Transfer.Status
    timestamp: int
    reason: str
    game_id: str
    one_off: OneOffTransfer
    recurring: RecurringTransfer
    one_off_governance: OneOffGovernanceTransfer
    recurring_governance: RecurringGovernanceTransfer
    def __init__(
        self,
        id: _Optional[str] = ...,
        from_account_type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
        to: _Optional[str] = ...,
        to_account_type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
        asset: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        reference: _Optional[str] = ...,
        status: _Optional[_Union[Transfer.Status, str]] = ...,
        timestamp: _Optional[int] = ...,
        reason: _Optional[str] = ...,
        game_id: _Optional[str] = ...,
        one_off: _Optional[_Union[OneOffTransfer, _Mapping]] = ...,
        recurring: _Optional[_Union[RecurringTransfer, _Mapping]] = ...,
        one_off_governance: _Optional[_Union[OneOffGovernanceTransfer, _Mapping]] = ...,
        recurring_governance: _Optional[
            _Union[RecurringGovernanceTransfer, _Mapping]
        ] = ...,
        **kwargs
    ) -> None: ...

class OneOffGovernanceTransfer(_message.Message):
    __slots__ = ("deliver_on",)
    DELIVER_ON_FIELD_NUMBER: _ClassVar[int]
    deliver_on: int
    def __init__(self, deliver_on: _Optional[int] = ...) -> None: ...

class OneOffTransfer(_message.Message):
    __slots__ = ("deliver_on",)
    DELIVER_ON_FIELD_NUMBER: _ClassVar[int]
    deliver_on: int
    def __init__(self, deliver_on: _Optional[int] = ...) -> None: ...

class RecurringTransfer(_message.Message):
    __slots__ = ("start_epoch", "end_epoch", "factor", "dispatch_strategy")
    START_EPOCH_FIELD_NUMBER: _ClassVar[int]
    END_EPOCH_FIELD_NUMBER: _ClassVar[int]
    FACTOR_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    start_epoch: int
    end_epoch: int
    factor: str
    dispatch_strategy: _vega_pb2.DispatchStrategy
    def __init__(
        self,
        start_epoch: _Optional[int] = ...,
        end_epoch: _Optional[int] = ...,
        factor: _Optional[str] = ...,
        dispatch_strategy: _Optional[
            _Union[_vega_pb2.DispatchStrategy, _Mapping]
        ] = ...,
    ) -> None: ...

class RecurringGovernanceTransfer(_message.Message):
    __slots__ = ("start_epoch", "end_epoch", "dispatch_strategy")
    START_EPOCH_FIELD_NUMBER: _ClassVar[int]
    END_EPOCH_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    start_epoch: int
    end_epoch: int
    dispatch_strategy: _vega_pb2.DispatchStrategy
    def __init__(
        self,
        start_epoch: _Optional[int] = ...,
        end_epoch: _Optional[int] = ...,
        dispatch_strategy: _Optional[
            _Union[_vega_pb2.DispatchStrategy, _Mapping]
        ] = ...,
    ) -> None: ...

class StakeLinking(_message.Message):
    __slots__ = (
        "id",
        "type",
        "ts",
        "party",
        "amount",
        "status",
        "finalized_at",
        "tx_hash",
        "block_height",
        "block_time",
        "log_index",
        "ethereum_address",
    )

    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[StakeLinking.Type]
        TYPE_LINK: _ClassVar[StakeLinking.Type]
        TYPE_UNLINK: _ClassVar[StakeLinking.Type]
    TYPE_UNSPECIFIED: StakeLinking.Type
    TYPE_LINK: StakeLinking.Type
    TYPE_UNLINK: StakeLinking.Type

    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[StakeLinking.Status]
        STATUS_PENDING: _ClassVar[StakeLinking.Status]
        STATUS_ACCEPTED: _ClassVar[StakeLinking.Status]
        STATUS_REJECTED: _ClassVar[StakeLinking.Status]
    STATUS_UNSPECIFIED: StakeLinking.Status
    STATUS_PENDING: StakeLinking.Status
    STATUS_ACCEPTED: StakeLinking.Status
    STATUS_REJECTED: StakeLinking.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TS_FIELD_NUMBER: _ClassVar[int]
    PARTY_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    FINALIZED_AT_FIELD_NUMBER: _ClassVar[int]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: StakeLinking.Type
    ts: int
    party: str
    amount: str
    status: StakeLinking.Status
    finalized_at: int
    tx_hash: str
    block_height: int
    block_time: int
    log_index: int
    ethereum_address: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        type: _Optional[_Union[StakeLinking.Type, str]] = ...,
        ts: _Optional[int] = ...,
        party: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        status: _Optional[_Union[StakeLinking.Status, str]] = ...,
        finalized_at: _Optional[int] = ...,
        tx_hash: _Optional[str] = ...,
        block_height: _Optional[int] = ...,
        block_time: _Optional[int] = ...,
        log_index: _Optional[int] = ...,
        ethereum_address: _Optional[str] = ...,
    ) -> None: ...

class ERC20MultiSigSignerEvent(_message.Message):
    __slots__ = (
        "id",
        "type",
        "signer",
        "nonce",
        "block_time",
        "tx_hash",
        "log_index",
        "block_number",
    )

    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[ERC20MultiSigSignerEvent.Type]
        TYPE_ADDED: _ClassVar[ERC20MultiSigSignerEvent.Type]
        TYPE_REMOVED: _ClassVar[ERC20MultiSigSignerEvent.Type]
    TYPE_UNSPECIFIED: ERC20MultiSigSignerEvent.Type
    TYPE_ADDED: ERC20MultiSigSignerEvent.Type
    TYPE_REMOVED: ERC20MultiSigSignerEvent.Type
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SIGNER_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    BLOCK_NUMBER_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: ERC20MultiSigSignerEvent.Type
    signer: str
    nonce: str
    block_time: int
    tx_hash: str
    log_index: int
    block_number: int
    def __init__(
        self,
        id: _Optional[str] = ...,
        type: _Optional[_Union[ERC20MultiSigSignerEvent.Type, str]] = ...,
        signer: _Optional[str] = ...,
        nonce: _Optional[str] = ...,
        block_time: _Optional[int] = ...,
        tx_hash: _Optional[str] = ...,
        log_index: _Optional[int] = ...,
        block_number: _Optional[int] = ...,
    ) -> None: ...

class ERC20MultiSigThresholdSetEvent(_message.Message):
    __slots__ = (
        "id",
        "new_threshold",
        "nonce",
        "block_time",
        "tx_hash",
        "log_index",
        "block_number",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    NEW_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    BLOCK_NUMBER_FIELD_NUMBER: _ClassVar[int]
    id: str
    new_threshold: int
    nonce: str
    block_time: int
    tx_hash: str
    log_index: int
    block_number: int
    def __init__(
        self,
        id: _Optional[str] = ...,
        new_threshold: _Optional[int] = ...,
        nonce: _Optional[str] = ...,
        block_time: _Optional[int] = ...,
        tx_hash: _Optional[str] = ...,
        log_index: _Optional[int] = ...,
        block_number: _Optional[int] = ...,
    ) -> None: ...

class CheckpointEvent(_message.Message):
    __slots__ = ("hash", "block_hash", "block_height")
    HASH_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HASH_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    hash: str
    block_hash: str
    block_height: int
    def __init__(
        self,
        hash: _Optional[str] = ...,
        block_hash: _Optional[str] = ...,
        block_height: _Optional[int] = ...,
    ) -> None: ...

class StreamStartEvent(_message.Message):
    __slots__ = ("chain_id",)
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    chain_id: str
    def __init__(self, chain_id: _Optional[str] = ...) -> None: ...

class RewardPayoutEvent(_message.Message):
    __slots__ = (
        "party",
        "epoch_seq",
        "asset",
        "amount",
        "percent_of_total_reward",
        "timestamp",
        "reward_type",
        "locked_until_epoch",
        "quantum_amount",
        "game_id",
    )
    PARTY_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PERCENT_OF_TOTAL_REWARD_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REWARD_TYPE_FIELD_NUMBER: _ClassVar[int]
    LOCKED_UNTIL_EPOCH_FIELD_NUMBER: _ClassVar[int]
    QUANTUM_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    GAME_ID_FIELD_NUMBER: _ClassVar[int]
    party: str
    epoch_seq: str
    asset: str
    amount: str
    percent_of_total_reward: str
    timestamp: int
    reward_type: str
    locked_until_epoch: str
    quantum_amount: str
    game_id: str
    def __init__(
        self,
        party: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        percent_of_total_reward: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
        reward_type: _Optional[str] = ...,
        locked_until_epoch: _Optional[str] = ...,
        quantum_amount: _Optional[str] = ...,
        game_id: _Optional[str] = ...,
    ) -> None: ...

class ValidatorScoreEvent(_message.Message):
    __slots__ = (
        "node_id",
        "epoch_seq",
        "validator_score",
        "normalised_score",
        "validator_performance",
        "raw_validator_score",
        "validator_status",
        "multisig_score",
    )
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_SCORE_FIELD_NUMBER: _ClassVar[int]
    NORMALISED_SCORE_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_PERFORMANCE_FIELD_NUMBER: _ClassVar[int]
    RAW_VALIDATOR_SCORE_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_STATUS_FIELD_NUMBER: _ClassVar[int]
    MULTISIG_SCORE_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    epoch_seq: str
    validator_score: str
    normalised_score: str
    validator_performance: str
    raw_validator_score: str
    validator_status: str
    multisig_score: str
    def __init__(
        self,
        node_id: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
        validator_score: _Optional[str] = ...,
        normalised_score: _Optional[str] = ...,
        validator_performance: _Optional[str] = ...,
        raw_validator_score: _Optional[str] = ...,
        validator_status: _Optional[str] = ...,
        multisig_score: _Optional[str] = ...,
    ) -> None: ...

class DelegationBalanceEvent(_message.Message):
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

class MarketEvent(_message.Message):
    __slots__ = ("market_id", "payload")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    payload: str
    def __init__(
        self, market_id: _Optional[str] = ..., payload: _Optional[str] = ...
    ) -> None: ...

class TransferFees(_message.Message):
    __slots__ = ("transfer_id", "amount", "epoch", "discount_applied")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_APPLIED_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    amount: str
    epoch: int
    discount_applied: str
    def __init__(
        self,
        transfer_id: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        epoch: _Optional[int] = ...,
        discount_applied: _Optional[str] = ...,
    ) -> None: ...

class TransferFeesDiscount(_message.Message):
    __slots__ = ("party", "asset", "amount", "epoch")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    party: str
    asset: str
    amount: str
    epoch: int
    def __init__(
        self,
        party: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        epoch: _Optional[int] = ...,
    ) -> None: ...

class TransactionResult(_message.Message):
    __slots__ = (
        "party_id",
        "status",
        "hash",
        "order_submission",
        "order_amendment",
        "order_cancellation",
        "proposal",
        "vote_submission",
        "liquidity_provision_submission",
        "withdraw_submission",
        "delegate_submission",
        "undelegate_submission",
        "liquidity_provision_cancellation",
        "liquidity_provision_amendment",
        "transfer",
        "cancel_transfer",
        "announce_node",
        "oracle_data_submission",
        "protocol_upgrade_proposal",
        "issue_signatures",
        "batch_market_instructions",
        "key_rotate_submission",
        "ethereum_key_rotate_submission",
        "stop_order_submission",
        "stop_order_cancellation",
        "create_referral_set",
        "update_referral_set",
        "apply_referral_code",
        "update_margin_mode",
        "join_team",
        "batch_proposal",
        "success",
        "failure",
    )

    class SuccessDetails(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...

    class FailureDetails(_message.Message):
        __slots__ = ("error",)
        ERROR_FIELD_NUMBER: _ClassVar[int]
        error: str
        def __init__(self, error: _Optional[str] = ...) -> None: ...
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    ORDER_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    ORDER_AMENDMENT_FIELD_NUMBER: _ClassVar[int]
    ORDER_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    VOTE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISION_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    WITHDRAW_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    DELEGATE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    UNDELEGATE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISION_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISION_AMENDMENT_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_FIELD_NUMBER: _ClassVar[int]
    CANCEL_TRANSFER_FIELD_NUMBER: _ClassVar[int]
    ANNOUNCE_NODE_FIELD_NUMBER: _ClassVar[int]
    ORACLE_DATA_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_UPGRADE_PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    ISSUE_SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    BATCH_MARKET_INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    KEY_ROTATE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_KEY_ROTATE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    STOP_ORDER_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    STOP_ORDER_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    CREATE_REFERRAL_SET_FIELD_NUMBER: _ClassVar[int]
    UPDATE_REFERRAL_SET_FIELD_NUMBER: _ClassVar[int]
    APPLY_REFERRAL_CODE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MARGIN_MODE_FIELD_NUMBER: _ClassVar[int]
    JOIN_TEAM_FIELD_NUMBER: _ClassVar[int]
    BATCH_PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FAILURE_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    status: bool
    hash: str
    order_submission: _commands_pb2.OrderSubmission
    order_amendment: _commands_pb2.OrderAmendment
    order_cancellation: _commands_pb2.OrderCancellation
    proposal: _commands_pb2.ProposalSubmission
    vote_submission: _commands_pb2.VoteSubmission
    liquidity_provision_submission: _commands_pb2.LiquidityProvisionSubmission
    withdraw_submission: _commands_pb2.WithdrawSubmission
    delegate_submission: _commands_pb2.DelegateSubmission
    undelegate_submission: _commands_pb2.UndelegateSubmission
    liquidity_provision_cancellation: _commands_pb2.LiquidityProvisionCancellation
    liquidity_provision_amendment: _commands_pb2.LiquidityProvisionAmendment
    transfer: _commands_pb2.Transfer
    cancel_transfer: _commands_pb2.CancelTransfer
    announce_node: _validator_commands_pb2.AnnounceNode
    oracle_data_submission: _data_pb2.OracleDataSubmission
    protocol_upgrade_proposal: _validator_commands_pb2.ProtocolUpgradeProposal
    issue_signatures: _commands_pb2.IssueSignatures
    batch_market_instructions: _commands_pb2.BatchMarketInstructions
    key_rotate_submission: _validator_commands_pb2.KeyRotateSubmission
    ethereum_key_rotate_submission: _validator_commands_pb2.EthereumKeyRotateSubmission
    stop_order_submission: _commands_pb2.StopOrdersSubmission
    stop_order_cancellation: _commands_pb2.StopOrdersCancellation
    create_referral_set: _commands_pb2.CreateReferralSet
    update_referral_set: _commands_pb2.UpdateReferralSet
    apply_referral_code: _commands_pb2.ApplyReferralCode
    update_margin_mode: _commands_pb2.UpdateMarginMode
    join_team: _commands_pb2.JoinTeam
    batch_proposal: _commands_pb2.BatchProposalSubmission
    success: TransactionResult.SuccessDetails
    failure: TransactionResult.FailureDetails
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        status: bool = ...,
        hash: _Optional[str] = ...,
        order_submission: _Optional[
            _Union[_commands_pb2.OrderSubmission, _Mapping]
        ] = ...,
        order_amendment: _Optional[
            _Union[_commands_pb2.OrderAmendment, _Mapping]
        ] = ...,
        order_cancellation: _Optional[
            _Union[_commands_pb2.OrderCancellation, _Mapping]
        ] = ...,
        proposal: _Optional[_Union[_commands_pb2.ProposalSubmission, _Mapping]] = ...,
        vote_submission: _Optional[
            _Union[_commands_pb2.VoteSubmission, _Mapping]
        ] = ...,
        liquidity_provision_submission: _Optional[
            _Union[_commands_pb2.LiquidityProvisionSubmission, _Mapping]
        ] = ...,
        withdraw_submission: _Optional[
            _Union[_commands_pb2.WithdrawSubmission, _Mapping]
        ] = ...,
        delegate_submission: _Optional[
            _Union[_commands_pb2.DelegateSubmission, _Mapping]
        ] = ...,
        undelegate_submission: _Optional[
            _Union[_commands_pb2.UndelegateSubmission, _Mapping]
        ] = ...,
        liquidity_provision_cancellation: _Optional[
            _Union[_commands_pb2.LiquidityProvisionCancellation, _Mapping]
        ] = ...,
        liquidity_provision_amendment: _Optional[
            _Union[_commands_pb2.LiquidityProvisionAmendment, _Mapping]
        ] = ...,
        transfer: _Optional[_Union[_commands_pb2.Transfer, _Mapping]] = ...,
        cancel_transfer: _Optional[
            _Union[_commands_pb2.CancelTransfer, _Mapping]
        ] = ...,
        announce_node: _Optional[
            _Union[_validator_commands_pb2.AnnounceNode, _Mapping]
        ] = ...,
        oracle_data_submission: _Optional[
            _Union[_data_pb2.OracleDataSubmission, _Mapping]
        ] = ...,
        protocol_upgrade_proposal: _Optional[
            _Union[_validator_commands_pb2.ProtocolUpgradeProposal, _Mapping]
        ] = ...,
        issue_signatures: _Optional[
            _Union[_commands_pb2.IssueSignatures, _Mapping]
        ] = ...,
        batch_market_instructions: _Optional[
            _Union[_commands_pb2.BatchMarketInstructions, _Mapping]
        ] = ...,
        key_rotate_submission: _Optional[
            _Union[_validator_commands_pb2.KeyRotateSubmission, _Mapping]
        ] = ...,
        ethereum_key_rotate_submission: _Optional[
            _Union[_validator_commands_pb2.EthereumKeyRotateSubmission, _Mapping]
        ] = ...,
        stop_order_submission: _Optional[
            _Union[_commands_pb2.StopOrdersSubmission, _Mapping]
        ] = ...,
        stop_order_cancellation: _Optional[
            _Union[_commands_pb2.StopOrdersCancellation, _Mapping]
        ] = ...,
        create_referral_set: _Optional[
            _Union[_commands_pb2.CreateReferralSet, _Mapping]
        ] = ...,
        update_referral_set: _Optional[
            _Union[_commands_pb2.UpdateReferralSet, _Mapping]
        ] = ...,
        apply_referral_code: _Optional[
            _Union[_commands_pb2.ApplyReferralCode, _Mapping]
        ] = ...,
        update_margin_mode: _Optional[
            _Union[_commands_pb2.UpdateMarginMode, _Mapping]
        ] = ...,
        join_team: _Optional[_Union[_commands_pb2.JoinTeam, _Mapping]] = ...,
        batch_proposal: _Optional[
            _Union[_commands_pb2.BatchProposalSubmission, _Mapping]
        ] = ...,
        success: _Optional[_Union[TransactionResult.SuccessDetails, _Mapping]] = ...,
        failure: _Optional[_Union[TransactionResult.FailureDetails, _Mapping]] = ...,
    ) -> None: ...

class TxErrorEvent(_message.Message):
    __slots__ = (
        "party_id",
        "err_msg",
        "order_submission",
        "order_amendment",
        "order_cancellation",
        "proposal",
        "vote_submission",
        "liquidity_provision_submission",
        "withdraw_submission",
        "delegate_submission",
        "undelegate_submission",
        "liquidity_provision_cancellation",
        "liquidity_provision_amendment",
        "transfer",
        "cancel_transfer",
        "announce_node",
        "oracle_data_submission",
        "protocol_upgrade_proposal",
        "issue_signatures",
        "batch_market_instructions",
    )
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    ERR_MSG_FIELD_NUMBER: _ClassVar[int]
    ORDER_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    ORDER_AMENDMENT_FIELD_NUMBER: _ClassVar[int]
    ORDER_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    VOTE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISION_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    WITHDRAW_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    DELEGATE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    UNDELEGATE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISION_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISION_AMENDMENT_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_FIELD_NUMBER: _ClassVar[int]
    CANCEL_TRANSFER_FIELD_NUMBER: _ClassVar[int]
    ANNOUNCE_NODE_FIELD_NUMBER: _ClassVar[int]
    ORACLE_DATA_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_UPGRADE_PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    ISSUE_SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    BATCH_MARKET_INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    err_msg: str
    order_submission: _commands_pb2.OrderSubmission
    order_amendment: _commands_pb2.OrderAmendment
    order_cancellation: _commands_pb2.OrderCancellation
    proposal: _commands_pb2.ProposalSubmission
    vote_submission: _commands_pb2.VoteSubmission
    liquidity_provision_submission: _commands_pb2.LiquidityProvisionSubmission
    withdraw_submission: _commands_pb2.WithdrawSubmission
    delegate_submission: _commands_pb2.DelegateSubmission
    undelegate_submission: _commands_pb2.UndelegateSubmission
    liquidity_provision_cancellation: _commands_pb2.LiquidityProvisionCancellation
    liquidity_provision_amendment: _commands_pb2.LiquidityProvisionAmendment
    transfer: _commands_pb2.Transfer
    cancel_transfer: _commands_pb2.CancelTransfer
    announce_node: _validator_commands_pb2.AnnounceNode
    oracle_data_submission: _data_pb2.OracleDataSubmission
    protocol_upgrade_proposal: _validator_commands_pb2.ProtocolUpgradeProposal
    issue_signatures: _commands_pb2.IssueSignatures
    batch_market_instructions: _commands_pb2.BatchMarketInstructions
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        err_msg: _Optional[str] = ...,
        order_submission: _Optional[
            _Union[_commands_pb2.OrderSubmission, _Mapping]
        ] = ...,
        order_amendment: _Optional[
            _Union[_commands_pb2.OrderAmendment, _Mapping]
        ] = ...,
        order_cancellation: _Optional[
            _Union[_commands_pb2.OrderCancellation, _Mapping]
        ] = ...,
        proposal: _Optional[_Union[_commands_pb2.ProposalSubmission, _Mapping]] = ...,
        vote_submission: _Optional[
            _Union[_commands_pb2.VoteSubmission, _Mapping]
        ] = ...,
        liquidity_provision_submission: _Optional[
            _Union[_commands_pb2.LiquidityProvisionSubmission, _Mapping]
        ] = ...,
        withdraw_submission: _Optional[
            _Union[_commands_pb2.WithdrawSubmission, _Mapping]
        ] = ...,
        delegate_submission: _Optional[
            _Union[_commands_pb2.DelegateSubmission, _Mapping]
        ] = ...,
        undelegate_submission: _Optional[
            _Union[_commands_pb2.UndelegateSubmission, _Mapping]
        ] = ...,
        liquidity_provision_cancellation: _Optional[
            _Union[_commands_pb2.LiquidityProvisionCancellation, _Mapping]
        ] = ...,
        liquidity_provision_amendment: _Optional[
            _Union[_commands_pb2.LiquidityProvisionAmendment, _Mapping]
        ] = ...,
        transfer: _Optional[_Union[_commands_pb2.Transfer, _Mapping]] = ...,
        cancel_transfer: _Optional[
            _Union[_commands_pb2.CancelTransfer, _Mapping]
        ] = ...,
        announce_node: _Optional[
            _Union[_validator_commands_pb2.AnnounceNode, _Mapping]
        ] = ...,
        oracle_data_submission: _Optional[
            _Union[_data_pb2.OracleDataSubmission, _Mapping]
        ] = ...,
        protocol_upgrade_proposal: _Optional[
            _Union[_validator_commands_pb2.ProtocolUpgradeProposal, _Mapping]
        ] = ...,
        issue_signatures: _Optional[
            _Union[_commands_pb2.IssueSignatures, _Mapping]
        ] = ...,
        batch_market_instructions: _Optional[
            _Union[_commands_pb2.BatchMarketInstructions, _Mapping]
        ] = ...,
    ) -> None: ...

class TimeUpdate(_message.Message):
    __slots__ = ("timestamp",)
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    def __init__(self, timestamp: _Optional[int] = ...) -> None: ...

class EpochEvent(_message.Message):
    __slots__ = ("seq", "action", "start_time", "expire_time", "end_time")
    SEQ_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    seq: int
    action: _vega_pb2.EpochAction
    start_time: int
    expire_time: int
    end_time: int
    def __init__(
        self,
        seq: _Optional[int] = ...,
        action: _Optional[_Union[_vega_pb2.EpochAction, str]] = ...,
        start_time: _Optional[int] = ...,
        expire_time: _Optional[int] = ...,
        end_time: _Optional[int] = ...,
    ) -> None: ...

class LedgerMovements(_message.Message):
    __slots__ = ("ledger_movements",)
    LEDGER_MOVEMENTS_FIELD_NUMBER: _ClassVar[int]
    ledger_movements: _containers.RepeatedCompositeFieldContainer[
        _vega_pb2.LedgerMovement
    ]
    def __init__(
        self,
        ledger_movements: _Optional[
            _Iterable[_Union[_vega_pb2.LedgerMovement, _Mapping]]
        ] = ...,
    ) -> None: ...

class PositionResolution(_message.Message):
    __slots__ = ("market_id", "distressed", "closed", "mark_price")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    DISTRESSED_FIELD_NUMBER: _ClassVar[int]
    CLOSED_FIELD_NUMBER: _ClassVar[int]
    MARK_PRICE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    distressed: int
    closed: int
    mark_price: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        distressed: _Optional[int] = ...,
        closed: _Optional[int] = ...,
        mark_price: _Optional[str] = ...,
    ) -> None: ...

class LossSocialization(_message.Message):
    __slots__ = ("market_id", "party_id", "amount")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    party_id: str
    amount: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        amount: _Optional[str] = ...,
    ) -> None: ...

class TradeSettlement(_message.Message):
    __slots__ = ("size", "price", "market_price")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    MARKET_PRICE_FIELD_NUMBER: _ClassVar[int]
    size: int
    price: str
    market_price: str
    def __init__(
        self,
        size: _Optional[int] = ...,
        price: _Optional[str] = ...,
        market_price: _Optional[str] = ...,
    ) -> None: ...

class SettlePosition(_message.Message):
    __slots__ = (
        "market_id",
        "party_id",
        "price",
        "trade_settlements",
        "position_factor",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    TRADE_SETTLEMENTS_FIELD_NUMBER: _ClassVar[int]
    POSITION_FACTOR_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    party_id: str
    price: str
    trade_settlements: _containers.RepeatedCompositeFieldContainer[TradeSettlement]
    position_factor: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        price: _Optional[str] = ...,
        trade_settlements: _Optional[
            _Iterable[_Union[TradeSettlement, _Mapping]]
        ] = ...,
        position_factor: _Optional[str] = ...,
    ) -> None: ...

class SettleMarket(_message.Message):
    __slots__ = ("market_id", "price", "position_factor")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FACTOR_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    price: str
    position_factor: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        price: _Optional[str] = ...,
        position_factor: _Optional[str] = ...,
    ) -> None: ...

class PositionStateEvent(_message.Message):
    __slots__ = (
        "party_id",
        "market_id",
        "size",
        "potential_buys",
        "potential_sells",
        "vw_buy_price",
        "vw_sell_price",
    )
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    POTENTIAL_BUYS_FIELD_NUMBER: _ClassVar[int]
    POTENTIAL_SELLS_FIELD_NUMBER: _ClassVar[int]
    VW_BUY_PRICE_FIELD_NUMBER: _ClassVar[int]
    VW_SELL_PRICE_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    market_id: str
    size: int
    potential_buys: int
    potential_sells: int
    vw_buy_price: str
    vw_sell_price: str
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        size: _Optional[int] = ...,
        potential_buys: _Optional[int] = ...,
        potential_sells: _Optional[int] = ...,
        vw_buy_price: _Optional[str] = ...,
        vw_sell_price: _Optional[str] = ...,
    ) -> None: ...

class SettleDistressed(_message.Message):
    __slots__ = ("market_id", "party_id", "margin", "price")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MARGIN_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    party_id: str
    margin: str
    price: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        margin: _Optional[str] = ...,
        price: _Optional[str] = ...,
    ) -> None: ...

class DistressedOrders(_message.Message):
    __slots__ = ("market_id", "parties")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    parties: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self, market_id: _Optional[str] = ..., parties: _Optional[_Iterable[str]] = ...
    ) -> None: ...

class DistressedPositions(_message.Message):
    __slots__ = ("market_id", "distressed_parties", "safe_parties")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    DISTRESSED_PARTIES_FIELD_NUMBER: _ClassVar[int]
    SAFE_PARTIES_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    distressed_parties: _containers.RepeatedScalarFieldContainer[str]
    safe_parties: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        distressed_parties: _Optional[_Iterable[str]] = ...,
        safe_parties: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class MarketTick(_message.Message):
    __slots__ = ("id", "time")
    ID_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    time: int
    def __init__(
        self, id: _Optional[str] = ..., time: _Optional[int] = ...
    ) -> None: ...

class AuctionEvent(_message.Message):
    __slots__ = (
        "market_id",
        "opening_auction",
        "leave",
        "start",
        "end",
        "trigger",
        "extension_trigger",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    OPENING_AUCTION_FIELD_NUMBER: _ClassVar[int]
    LEAVE_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_TRIGGER_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    opening_auction: bool
    leave: bool
    start: int
    end: int
    trigger: _vega_pb2.AuctionTrigger
    extension_trigger: _vega_pb2.AuctionTrigger
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        opening_auction: bool = ...,
        leave: bool = ...,
        start: _Optional[int] = ...,
        end: _Optional[int] = ...,
        trigger: _Optional[_Union[_vega_pb2.AuctionTrigger, str]] = ...,
        extension_trigger: _Optional[_Union[_vega_pb2.AuctionTrigger, str]] = ...,
    ) -> None: ...

class ValidatorUpdate(_message.Message):
    __slots__ = (
        "node_id",
        "vega_pub_key",
        "ethereum_address",
        "tm_pub_key",
        "info_url",
        "country",
        "name",
        "avatar_url",
        "vega_pub_key_index",
        "added",
        "from_epoch",
        "submitter_address",
        "epoch_seq",
    )
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    VEGA_PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TM_PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    INFO_URL_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    VEGA_PUB_KEY_INDEX_FIELD_NUMBER: _ClassVar[int]
    ADDED_FIELD_NUMBER: _ClassVar[int]
    FROM_EPOCH_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    vega_pub_key: str
    ethereum_address: str
    tm_pub_key: str
    info_url: str
    country: str
    name: str
    avatar_url: str
    vega_pub_key_index: int
    added: bool
    from_epoch: int
    submitter_address: str
    epoch_seq: int
    def __init__(
        self,
        node_id: _Optional[str] = ...,
        vega_pub_key: _Optional[str] = ...,
        ethereum_address: _Optional[str] = ...,
        tm_pub_key: _Optional[str] = ...,
        info_url: _Optional[str] = ...,
        country: _Optional[str] = ...,
        name: _Optional[str] = ...,
        avatar_url: _Optional[str] = ...,
        vega_pub_key_index: _Optional[int] = ...,
        added: bool = ...,
        from_epoch: _Optional[int] = ...,
        submitter_address: _Optional[str] = ...,
        epoch_seq: _Optional[int] = ...,
    ) -> None: ...

class ValidatorRankingEvent(_message.Message):
    __slots__ = (
        "node_id",
        "stake_score",
        "performance_score",
        "ranking_score",
        "previous_status",
        "next_status",
        "epoch_seq",
        "tm_voting_power",
    )
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    STAKE_SCORE_FIELD_NUMBER: _ClassVar[int]
    PERFORMANCE_SCORE_FIELD_NUMBER: _ClassVar[int]
    RANKING_SCORE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_STATUS_FIELD_NUMBER: _ClassVar[int]
    NEXT_STATUS_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    TM_VOTING_POWER_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    stake_score: str
    performance_score: str
    ranking_score: str
    previous_status: str
    next_status: str
    epoch_seq: str
    tm_voting_power: int
    def __init__(
        self,
        node_id: _Optional[str] = ...,
        stake_score: _Optional[str] = ...,
        performance_score: _Optional[str] = ...,
        ranking_score: _Optional[str] = ...,
        previous_status: _Optional[str] = ...,
        next_status: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
        tm_voting_power: _Optional[int] = ...,
    ) -> None: ...

class KeyRotation(_message.Message):
    __slots__ = ("node_id", "old_pub_key", "new_pub_key", "block_height")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    OLD_PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    NEW_PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    old_pub_key: str
    new_pub_key: str
    block_height: int
    def __init__(
        self,
        node_id: _Optional[str] = ...,
        old_pub_key: _Optional[str] = ...,
        new_pub_key: _Optional[str] = ...,
        block_height: _Optional[int] = ...,
    ) -> None: ...

class EthereumKeyRotation(_message.Message):
    __slots__ = ("node_id", "old_address", "new_address", "block_height")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    OLD_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NEW_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    old_address: str
    new_address: str
    block_height: int
    def __init__(
        self,
        node_id: _Optional[str] = ...,
        old_address: _Optional[str] = ...,
        new_address: _Optional[str] = ...,
        block_height: _Optional[int] = ...,
    ) -> None: ...

class ProtocolUpgradeEvent(_message.Message):
    __slots__ = ("upgrade_block_height", "vega_release_tag", "approvers", "status")
    UPGRADE_BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    VEGA_RELEASE_TAG_FIELD_NUMBER: _ClassVar[int]
    APPROVERS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    upgrade_block_height: int
    vega_release_tag: str
    approvers: _containers.RepeatedScalarFieldContainer[str]
    status: ProtocolUpgradeProposalStatus
    def __init__(
        self,
        upgrade_block_height: _Optional[int] = ...,
        vega_release_tag: _Optional[str] = ...,
        approvers: _Optional[_Iterable[str]] = ...,
        status: _Optional[_Union[ProtocolUpgradeProposalStatus, str]] = ...,
    ) -> None: ...

class StateVar(_message.Message):
    __slots__ = ("id", "event_id", "state")
    ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    event_id: str
    state: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        event_id: _Optional[str] = ...,
        state: _Optional[str] = ...,
    ) -> None: ...

class BeginBlock(_message.Message):
    __slots__ = ("height", "timestamp", "hash")
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    height: int
    timestamp: int
    hash: str
    def __init__(
        self,
        height: _Optional[int] = ...,
        timestamp: _Optional[int] = ...,
        hash: _Optional[str] = ...,
    ) -> None: ...

class EndBlock(_message.Message):
    __slots__ = ("height",)
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    height: int
    def __init__(self, height: _Optional[int] = ...) -> None: ...

class ProtocolUpgradeStarted(_message.Message):
    __slots__ = ("last_block_height",)
    LAST_BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    last_block_height: int
    def __init__(self, last_block_height: _Optional[int] = ...) -> None: ...

class ProtocolUpgradeDataNodeReady(_message.Message):
    __slots__ = ("last_block_height",)
    LAST_BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    last_block_height: int
    def __init__(self, last_block_height: _Optional[int] = ...) -> None: ...

class CoreSnapshotData(_message.Message):
    __slots__ = ("block_height", "block_hash", "core_version", "protocol_upgrade_block")
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HASH_FIELD_NUMBER: _ClassVar[int]
    CORE_VERSION_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_UPGRADE_BLOCK_FIELD_NUMBER: _ClassVar[int]
    block_height: int
    block_hash: str
    core_version: str
    protocol_upgrade_block: bool
    def __init__(
        self,
        block_height: _Optional[int] = ...,
        block_hash: _Optional[str] = ...,
        core_version: _Optional[str] = ...,
        protocol_upgrade_block: bool = ...,
    ) -> None: ...

class ExpiredOrders(_message.Message):
    __slots__ = ("market_id", "order_ids")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_IDS_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    order_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        order_ids: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class TeamCreated(_message.Message):
    __slots__ = (
        "team_id",
        "referrer",
        "name",
        "team_url",
        "avatar_url",
        "created_at",
        "closed",
        "at_epoch",
    )
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    REFERRER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEAM_URL_FIELD_NUMBER: _ClassVar[int]
    AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CLOSED_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    referrer: str
    name: str
    team_url: str
    avatar_url: str
    created_at: int
    closed: bool
    at_epoch: int
    def __init__(
        self,
        team_id: _Optional[str] = ...,
        referrer: _Optional[str] = ...,
        name: _Optional[str] = ...,
        team_url: _Optional[str] = ...,
        avatar_url: _Optional[str] = ...,
        created_at: _Optional[int] = ...,
        closed: bool = ...,
        at_epoch: _Optional[int] = ...,
    ) -> None: ...

class TeamUpdated(_message.Message):
    __slots__ = ("team_id", "name", "team_url", "avatar_url", "closed")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEAM_URL_FIELD_NUMBER: _ClassVar[int]
    AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    CLOSED_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    name: str
    team_url: str
    avatar_url: str
    closed: bool
    def __init__(
        self,
        team_id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        team_url: _Optional[str] = ...,
        avatar_url: _Optional[str] = ...,
        closed: bool = ...,
    ) -> None: ...

class RefereeSwitchedTeam(_message.Message):
    __slots__ = ("from_team_id", "to_team_id", "referee", "switched_at", "at_epoch")
    FROM_TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    TO_TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    REFEREE_FIELD_NUMBER: _ClassVar[int]
    SWITCHED_AT_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    from_team_id: str
    to_team_id: str
    referee: str
    switched_at: int
    at_epoch: int
    def __init__(
        self,
        from_team_id: _Optional[str] = ...,
        to_team_id: _Optional[str] = ...,
        referee: _Optional[str] = ...,
        switched_at: _Optional[int] = ...,
        at_epoch: _Optional[int] = ...,
    ) -> None: ...

class RefereeJoinedTeam(_message.Message):
    __slots__ = ("team_id", "referee", "joined_at", "at_epoch")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    REFEREE_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    referee: str
    joined_at: int
    at_epoch: int
    def __init__(
        self,
        team_id: _Optional[str] = ...,
        referee: _Optional[str] = ...,
        joined_at: _Optional[int] = ...,
        at_epoch: _Optional[int] = ...,
    ) -> None: ...

class ReferralSetCreated(_message.Message):
    __slots__ = ("set_id", "referrer", "created_at", "updated_at")
    SET_ID_FIELD_NUMBER: _ClassVar[int]
    REFERRER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    set_id: str
    referrer: str
    created_at: int
    updated_at: int
    def __init__(
        self,
        set_id: _Optional[str] = ...,
        referrer: _Optional[str] = ...,
        created_at: _Optional[int] = ...,
        updated_at: _Optional[int] = ...,
    ) -> None: ...

class ReferralSetStatsUpdated(_message.Message):
    __slots__ = (
        "set_id",
        "at_epoch",
        "referral_set_running_notional_taker_volume",
        "referees_stats",
        "reward_factor",
        "rewards_multiplier",
        "rewards_factor_multiplier",
        "was_eligible",
        "referrer_taker_volume",
    )
    SET_ID_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_SET_RUNNING_NOTIONAL_TAKER_VOLUME_FIELD_NUMBER: _ClassVar[int]
    REFEREES_STATS_FIELD_NUMBER: _ClassVar[int]
    REWARD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    REWARDS_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    REWARDS_FACTOR_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    WAS_ELIGIBLE_FIELD_NUMBER: _ClassVar[int]
    REFERRER_TAKER_VOLUME_FIELD_NUMBER: _ClassVar[int]
    set_id: str
    at_epoch: int
    referral_set_running_notional_taker_volume: str
    referees_stats: _containers.RepeatedCompositeFieldContainer[RefereeStats]
    reward_factor: str
    rewards_multiplier: str
    rewards_factor_multiplier: str
    was_eligible: bool
    referrer_taker_volume: str
    def __init__(
        self,
        set_id: _Optional[str] = ...,
        at_epoch: _Optional[int] = ...,
        referral_set_running_notional_taker_volume: _Optional[str] = ...,
        referees_stats: _Optional[_Iterable[_Union[RefereeStats, _Mapping]]] = ...,
        reward_factor: _Optional[str] = ...,
        rewards_multiplier: _Optional[str] = ...,
        rewards_factor_multiplier: _Optional[str] = ...,
        was_eligible: bool = ...,
        referrer_taker_volume: _Optional[str] = ...,
    ) -> None: ...

class RefereeStats(_message.Message):
    __slots__ = ("party_id", "discount_factor", "epoch_notional_taker_volume")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    EPOCH_NOTIONAL_TAKER_VOLUME_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    discount_factor: str
    epoch_notional_taker_volume: str
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        discount_factor: _Optional[str] = ...,
        epoch_notional_taker_volume: _Optional[str] = ...,
    ) -> None: ...

class RefereeJoinedReferralSet(_message.Message):
    __slots__ = ("set_id", "referee", "joined_at", "at_epoch")
    SET_ID_FIELD_NUMBER: _ClassVar[int]
    REFEREE_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    set_id: str
    referee: str
    joined_at: int
    at_epoch: int
    def __init__(
        self,
        set_id: _Optional[str] = ...,
        referee: _Optional[str] = ...,
        joined_at: _Optional[int] = ...,
        at_epoch: _Optional[int] = ...,
    ) -> None: ...

class ReferralProgramStarted(_message.Message):
    __slots__ = ("program", "started_at", "at_epoch")
    PROGRAM_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    program: _vega_pb2.ReferralProgram
    started_at: int
    at_epoch: int
    def __init__(
        self,
        program: _Optional[_Union[_vega_pb2.ReferralProgram, _Mapping]] = ...,
        started_at: _Optional[int] = ...,
        at_epoch: _Optional[int] = ...,
    ) -> None: ...

class ReferralProgramUpdated(_message.Message):
    __slots__ = ("program", "updated_at", "at_epoch")
    PROGRAM_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    program: _vega_pb2.ReferralProgram
    updated_at: int
    at_epoch: int
    def __init__(
        self,
        program: _Optional[_Union[_vega_pb2.ReferralProgram, _Mapping]] = ...,
        updated_at: _Optional[int] = ...,
        at_epoch: _Optional[int] = ...,
    ) -> None: ...

class ReferralProgramEnded(_message.Message):
    __slots__ = ("version", "id", "ended_at", "at_epoch")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    version: int
    id: str
    ended_at: int
    at_epoch: int
    def __init__(
        self,
        version: _Optional[int] = ...,
        id: _Optional[str] = ...,
        ended_at: _Optional[int] = ...,
        at_epoch: _Optional[int] = ...,
    ) -> None: ...

class VolumeDiscountProgramStarted(_message.Message):
    __slots__ = ("program", "started_at", "at_epoch")
    PROGRAM_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    program: _vega_pb2.VolumeDiscountProgram
    started_at: int
    at_epoch: int
    def __init__(
        self,
        program: _Optional[_Union[_vega_pb2.VolumeDiscountProgram, _Mapping]] = ...,
        started_at: _Optional[int] = ...,
        at_epoch: _Optional[int] = ...,
    ) -> None: ...

class VolumeDiscountProgramUpdated(_message.Message):
    __slots__ = ("program", "updated_at", "at_epoch")
    PROGRAM_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    program: _vega_pb2.VolumeDiscountProgram
    updated_at: int
    at_epoch: int
    def __init__(
        self,
        program: _Optional[_Union[_vega_pb2.VolumeDiscountProgram, _Mapping]] = ...,
        updated_at: _Optional[int] = ...,
        at_epoch: _Optional[int] = ...,
    ) -> None: ...

class VolumeDiscountProgramEnded(_message.Message):
    __slots__ = ("version", "id", "ended_at", "at_epoch")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    version: int
    id: str
    ended_at: int
    at_epoch: int
    def __init__(
        self,
        version: _Optional[int] = ...,
        id: _Optional[str] = ...,
        ended_at: _Optional[int] = ...,
        at_epoch: _Optional[int] = ...,
    ) -> None: ...

class PaidLiquidityFeesStats(_message.Message):
    __slots__ = (
        "market",
        "asset",
        "epoch_seq",
        "total_fees_paid",
        "fees_paid_per_party",
    )
    MARKET_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FEES_PAID_FIELD_NUMBER: _ClassVar[int]
    FEES_PAID_PER_PARTY_FIELD_NUMBER: _ClassVar[int]
    market: str
    asset: str
    epoch_seq: int
    total_fees_paid: str
    fees_paid_per_party: _containers.RepeatedCompositeFieldContainer[PartyAmount]
    def __init__(
        self,
        market: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        epoch_seq: _Optional[int] = ...,
        total_fees_paid: _Optional[str] = ...,
        fees_paid_per_party: _Optional[_Iterable[_Union[PartyAmount, _Mapping]]] = ...,
    ) -> None: ...

class PartyMarginModeUpdated(_message.Message):
    __slots__ = (
        "market_id",
        "party_id",
        "margin_mode",
        "margin_factor",
        "min_theoretical_margin_factor",
        "max_theoretical_leverage",
        "at_epoch",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MARGIN_MODE_FIELD_NUMBER: _ClassVar[int]
    MARGIN_FACTOR_FIELD_NUMBER: _ClassVar[int]
    MIN_THEORETICAL_MARGIN_FACTOR_FIELD_NUMBER: _ClassVar[int]
    MAX_THEORETICAL_LEVERAGE_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    party_id: str
    margin_mode: _vega_pb2.MarginMode
    margin_factor: str
    min_theoretical_margin_factor: str
    max_theoretical_leverage: str
    at_epoch: int
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        margin_mode: _Optional[_Union[_vega_pb2.MarginMode, str]] = ...,
        margin_factor: _Optional[str] = ...,
        min_theoretical_margin_factor: _Optional[str] = ...,
        max_theoretical_leverage: _Optional[str] = ...,
        at_epoch: _Optional[int] = ...,
    ) -> None: ...

class BusEvent(_message.Message):
    __slots__ = (
        "id",
        "block",
        "type",
        "time_update",
        "ledger_movements",
        "position_resolution",
        "order",
        "account",
        "party",
        "trade",
        "margin_levels",
        "proposal",
        "vote",
        "market_data",
        "node_signature",
        "loss_socialization",
        "settle_position",
        "settle_distressed",
        "market_created",
        "asset",
        "market_tick",
        "withdrawal",
        "deposit",
        "auction",
        "risk_factor",
        "network_parameter",
        "liquidity_provision",
        "market_updated",
        "oracle_spec",
        "oracle_data",
        "delegation_balance",
        "validator_score",
        "epoch_event",
        "validator_update",
        "stake_linking",
        "reward_payout",
        "checkpoint",
        "key_rotation",
        "state_var",
        "network_limits",
        "transfer",
        "ranking_event",
        "erc20_multisig_signer_event",
        "erc20_multisig_set_threshold_event",
        "erc20_multisig_signer_added",
        "erc20_multisig_signer_removed",
        "position_state_event",
        "ethereum_key_rotation",
        "protocol_upgrade_event",
        "begin_block",
        "end_block",
        "protocol_upgrade_started",
        "settle_market",
        "transaction_result",
        "core_snapshot_event",
        "protocol_upgrade_data_node_ready",
        "distressed_orders",
        "expired_orders",
        "distressed_positions",
        "stop_order",
        "funding_period",
        "funding_period_data_point",
        "team_created",
        "team_updated",
        "referee_switched_team",
        "referee_joined_team",
        "referral_program_started",
        "referral_program_updated",
        "referral_program_ended",
        "referral_set_created",
        "referee_joined_referral_set",
        "party_activity_streak",
        "volume_discount_program_started",
        "volume_discount_program_updated",
        "volume_discount_program_ended",
        "referral_set_stats_updated",
        "vesting_stats_updated",
        "volume_discount_stats_updated",
        "fees_stats",
        "funding_payments",
        "paid_liquidity_fees_stats",
        "vesting_balances_summary",
        "transfer_fees",
        "transfer_fees_discount",
        "party_margin_mode_updated",
        "market",
        "tx_err_event",
        "version",
        "chain_id",
        "tx_hash",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TIME_UPDATE_FIELD_NUMBER: _ClassVar[int]
    LEDGER_MOVEMENTS_FIELD_NUMBER: _ClassVar[int]
    POSITION_RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    PARTY_FIELD_NUMBER: _ClassVar[int]
    TRADE_FIELD_NUMBER: _ClassVar[int]
    MARGIN_LEVELS_FIELD_NUMBER: _ClassVar[int]
    PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    VOTE_FIELD_NUMBER: _ClassVar[int]
    MARKET_DATA_FIELD_NUMBER: _ClassVar[int]
    NODE_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    LOSS_SOCIALIZATION_FIELD_NUMBER: _ClassVar[int]
    SETTLE_POSITION_FIELD_NUMBER: _ClassVar[int]
    SETTLE_DISTRESSED_FIELD_NUMBER: _ClassVar[int]
    MARKET_CREATED_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    MARKET_TICK_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWAL_FIELD_NUMBER: _ClassVar[int]
    DEPOSIT_FIELD_NUMBER: _ClassVar[int]
    AUCTION_FIELD_NUMBER: _ClassVar[int]
    RISK_FACTOR_FIELD_NUMBER: _ClassVar[int]
    NETWORK_PARAMETER_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISION_FIELD_NUMBER: _ClassVar[int]
    MARKET_UPDATED_FIELD_NUMBER: _ClassVar[int]
    ORACLE_SPEC_FIELD_NUMBER: _ClassVar[int]
    ORACLE_DATA_FIELD_NUMBER: _ClassVar[int]
    DELEGATION_BALANCE_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_SCORE_FIELD_NUMBER: _ClassVar[int]
    EPOCH_EVENT_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_UPDATE_FIELD_NUMBER: _ClassVar[int]
    STAKE_LINKING_FIELD_NUMBER: _ClassVar[int]
    REWARD_PAYOUT_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINT_FIELD_NUMBER: _ClassVar[int]
    KEY_ROTATION_FIELD_NUMBER: _ClassVar[int]
    STATE_VAR_FIELD_NUMBER: _ClassVar[int]
    NETWORK_LIMITS_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_FIELD_NUMBER: _ClassVar[int]
    RANKING_EVENT_FIELD_NUMBER: _ClassVar[int]
    ERC20_MULTISIG_SIGNER_EVENT_FIELD_NUMBER: _ClassVar[int]
    ERC20_MULTISIG_SET_THRESHOLD_EVENT_FIELD_NUMBER: _ClassVar[int]
    ERC20_MULTISIG_SIGNER_ADDED_FIELD_NUMBER: _ClassVar[int]
    ERC20_MULTISIG_SIGNER_REMOVED_FIELD_NUMBER: _ClassVar[int]
    POSITION_STATE_EVENT_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_KEY_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_UPGRADE_EVENT_FIELD_NUMBER: _ClassVar[int]
    BEGIN_BLOCK_FIELD_NUMBER: _ClassVar[int]
    END_BLOCK_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_UPGRADE_STARTED_FIELD_NUMBER: _ClassVar[int]
    SETTLE_MARKET_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_RESULT_FIELD_NUMBER: _ClassVar[int]
    CORE_SNAPSHOT_EVENT_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_UPGRADE_DATA_NODE_READY_FIELD_NUMBER: _ClassVar[int]
    DISTRESSED_ORDERS_FIELD_NUMBER: _ClassVar[int]
    EXPIRED_ORDERS_FIELD_NUMBER: _ClassVar[int]
    DISTRESSED_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    STOP_ORDER_FIELD_NUMBER: _ClassVar[int]
    FUNDING_PERIOD_FIELD_NUMBER: _ClassVar[int]
    FUNDING_PERIOD_DATA_POINT_FIELD_NUMBER: _ClassVar[int]
    TEAM_CREATED_FIELD_NUMBER: _ClassVar[int]
    TEAM_UPDATED_FIELD_NUMBER: _ClassVar[int]
    REFEREE_SWITCHED_TEAM_FIELD_NUMBER: _ClassVar[int]
    REFEREE_JOINED_TEAM_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_PROGRAM_STARTED_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_PROGRAM_UPDATED_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_PROGRAM_ENDED_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_SET_CREATED_FIELD_NUMBER: _ClassVar[int]
    REFEREE_JOINED_REFERRAL_SET_FIELD_NUMBER: _ClassVar[int]
    PARTY_ACTIVITY_STREAK_FIELD_NUMBER: _ClassVar[int]
    VOLUME_DISCOUNT_PROGRAM_STARTED_FIELD_NUMBER: _ClassVar[int]
    VOLUME_DISCOUNT_PROGRAM_UPDATED_FIELD_NUMBER: _ClassVar[int]
    VOLUME_DISCOUNT_PROGRAM_ENDED_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_SET_STATS_UPDATED_FIELD_NUMBER: _ClassVar[int]
    VESTING_STATS_UPDATED_FIELD_NUMBER: _ClassVar[int]
    VOLUME_DISCOUNT_STATS_UPDATED_FIELD_NUMBER: _ClassVar[int]
    FEES_STATS_FIELD_NUMBER: _ClassVar[int]
    FUNDING_PAYMENTS_FIELD_NUMBER: _ClassVar[int]
    PAID_LIQUIDITY_FEES_STATS_FIELD_NUMBER: _ClassVar[int]
    VESTING_BALANCES_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_FEES_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_FEES_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    PARTY_MARGIN_MODE_UPDATED_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    TX_ERR_EVENT_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    id: str
    block: str
    type: BusEventType
    time_update: TimeUpdate
    ledger_movements: LedgerMovements
    position_resolution: PositionResolution
    order: _vega_pb2.Order
    account: _vega_pb2.Account
    party: _vega_pb2.Party
    trade: _vega_pb2.Trade
    margin_levels: _vega_pb2.MarginLevels
    proposal: _governance_pb2.Proposal
    vote: _governance_pb2.Vote
    market_data: _vega_pb2.MarketData
    node_signature: _validator_commands_pb2.NodeSignature
    loss_socialization: LossSocialization
    settle_position: SettlePosition
    settle_distressed: SettleDistressed
    market_created: _markets_pb2.Market
    asset: _assets_pb2.Asset
    market_tick: MarketTick
    withdrawal: _vega_pb2.Withdrawal
    deposit: _vega_pb2.Deposit
    auction: AuctionEvent
    risk_factor: _vega_pb2.RiskFactor
    network_parameter: _vega_pb2.NetworkParameter
    liquidity_provision: _vega_pb2.LiquidityProvision
    market_updated: _markets_pb2.Market
    oracle_spec: _oracle_pb2.OracleSpec
    oracle_data: _oracle_pb2.OracleData
    delegation_balance: DelegationBalanceEvent
    validator_score: ValidatorScoreEvent
    epoch_event: EpochEvent
    validator_update: ValidatorUpdate
    stake_linking: StakeLinking
    reward_payout: RewardPayoutEvent
    checkpoint: CheckpointEvent
    key_rotation: KeyRotation
    state_var: StateVar
    network_limits: _vega_pb2.NetworkLimits
    transfer: Transfer
    ranking_event: ValidatorRankingEvent
    erc20_multisig_signer_event: ERC20MultiSigSignerEvent
    erc20_multisig_set_threshold_event: ERC20MultiSigThresholdSetEvent
    erc20_multisig_signer_added: ERC20MultiSigSignerAdded
    erc20_multisig_signer_removed: ERC20MultiSigSignerRemoved
    position_state_event: PositionStateEvent
    ethereum_key_rotation: EthereumKeyRotation
    protocol_upgrade_event: ProtocolUpgradeEvent
    begin_block: BeginBlock
    end_block: EndBlock
    protocol_upgrade_started: ProtocolUpgradeStarted
    settle_market: SettleMarket
    transaction_result: TransactionResult
    core_snapshot_event: CoreSnapshotData
    protocol_upgrade_data_node_ready: ProtocolUpgradeDataNodeReady
    distressed_orders: DistressedOrders
    expired_orders: ExpiredOrders
    distressed_positions: DistressedPositions
    stop_order: StopOrderEvent
    funding_period: FundingPeriod
    funding_period_data_point: FundingPeriodDataPoint
    team_created: TeamCreated
    team_updated: TeamUpdated
    referee_switched_team: RefereeSwitchedTeam
    referee_joined_team: RefereeJoinedTeam
    referral_program_started: ReferralProgramStarted
    referral_program_updated: ReferralProgramUpdated
    referral_program_ended: ReferralProgramEnded
    referral_set_created: ReferralSetCreated
    referee_joined_referral_set: RefereeJoinedReferralSet
    party_activity_streak: PartyActivityStreak
    volume_discount_program_started: VolumeDiscountProgramStarted
    volume_discount_program_updated: VolumeDiscountProgramUpdated
    volume_discount_program_ended: VolumeDiscountProgramEnded
    referral_set_stats_updated: ReferralSetStatsUpdated
    vesting_stats_updated: VestingStatsUpdated
    volume_discount_stats_updated: VolumeDiscountStatsUpdated
    fees_stats: FeesStats
    funding_payments: FundingPayments
    paid_liquidity_fees_stats: PaidLiquidityFeesStats
    vesting_balances_summary: VestingBalancesSummary
    transfer_fees: TransferFees
    transfer_fees_discount: TransferFeesDiscount
    party_margin_mode_updated: PartyMarginModeUpdated
    market: MarketEvent
    tx_err_event: TxErrorEvent
    version: int
    chain_id: str
    tx_hash: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        block: _Optional[str] = ...,
        type: _Optional[_Union[BusEventType, str]] = ...,
        time_update: _Optional[_Union[TimeUpdate, _Mapping]] = ...,
        ledger_movements: _Optional[_Union[LedgerMovements, _Mapping]] = ...,
        position_resolution: _Optional[_Union[PositionResolution, _Mapping]] = ...,
        order: _Optional[_Union[_vega_pb2.Order, _Mapping]] = ...,
        account: _Optional[_Union[_vega_pb2.Account, _Mapping]] = ...,
        party: _Optional[_Union[_vega_pb2.Party, _Mapping]] = ...,
        trade: _Optional[_Union[_vega_pb2.Trade, _Mapping]] = ...,
        margin_levels: _Optional[_Union[_vega_pb2.MarginLevels, _Mapping]] = ...,
        proposal: _Optional[_Union[_governance_pb2.Proposal, _Mapping]] = ...,
        vote: _Optional[_Union[_governance_pb2.Vote, _Mapping]] = ...,
        market_data: _Optional[_Union[_vega_pb2.MarketData, _Mapping]] = ...,
        node_signature: _Optional[
            _Union[_validator_commands_pb2.NodeSignature, _Mapping]
        ] = ...,
        loss_socialization: _Optional[_Union[LossSocialization, _Mapping]] = ...,
        settle_position: _Optional[_Union[SettlePosition, _Mapping]] = ...,
        settle_distressed: _Optional[_Union[SettleDistressed, _Mapping]] = ...,
        market_created: _Optional[_Union[_markets_pb2.Market, _Mapping]] = ...,
        asset: _Optional[_Union[_assets_pb2.Asset, _Mapping]] = ...,
        market_tick: _Optional[_Union[MarketTick, _Mapping]] = ...,
        withdrawal: _Optional[_Union[_vega_pb2.Withdrawal, _Mapping]] = ...,
        deposit: _Optional[_Union[_vega_pb2.Deposit, _Mapping]] = ...,
        auction: _Optional[_Union[AuctionEvent, _Mapping]] = ...,
        risk_factor: _Optional[_Union[_vega_pb2.RiskFactor, _Mapping]] = ...,
        network_parameter: _Optional[
            _Union[_vega_pb2.NetworkParameter, _Mapping]
        ] = ...,
        liquidity_provision: _Optional[
            _Union[_vega_pb2.LiquidityProvision, _Mapping]
        ] = ...,
        market_updated: _Optional[_Union[_markets_pb2.Market, _Mapping]] = ...,
        oracle_spec: _Optional[_Union[_oracle_pb2.OracleSpec, _Mapping]] = ...,
        oracle_data: _Optional[_Union[_oracle_pb2.OracleData, _Mapping]] = ...,
        delegation_balance: _Optional[_Union[DelegationBalanceEvent, _Mapping]] = ...,
        validator_score: _Optional[_Union[ValidatorScoreEvent, _Mapping]] = ...,
        epoch_event: _Optional[_Union[EpochEvent, _Mapping]] = ...,
        validator_update: _Optional[_Union[ValidatorUpdate, _Mapping]] = ...,
        stake_linking: _Optional[_Union[StakeLinking, _Mapping]] = ...,
        reward_payout: _Optional[_Union[RewardPayoutEvent, _Mapping]] = ...,
        checkpoint: _Optional[_Union[CheckpointEvent, _Mapping]] = ...,
        key_rotation: _Optional[_Union[KeyRotation, _Mapping]] = ...,
        state_var: _Optional[_Union[StateVar, _Mapping]] = ...,
        network_limits: _Optional[_Union[_vega_pb2.NetworkLimits, _Mapping]] = ...,
        transfer: _Optional[_Union[Transfer, _Mapping]] = ...,
        ranking_event: _Optional[_Union[ValidatorRankingEvent, _Mapping]] = ...,
        erc20_multisig_signer_event: _Optional[
            _Union[ERC20MultiSigSignerEvent, _Mapping]
        ] = ...,
        erc20_multisig_set_threshold_event: _Optional[
            _Union[ERC20MultiSigThresholdSetEvent, _Mapping]
        ] = ...,
        erc20_multisig_signer_added: _Optional[
            _Union[ERC20MultiSigSignerAdded, _Mapping]
        ] = ...,
        erc20_multisig_signer_removed: _Optional[
            _Union[ERC20MultiSigSignerRemoved, _Mapping]
        ] = ...,
        position_state_event: _Optional[_Union[PositionStateEvent, _Mapping]] = ...,
        ethereum_key_rotation: _Optional[_Union[EthereumKeyRotation, _Mapping]] = ...,
        protocol_upgrade_event: _Optional[_Union[ProtocolUpgradeEvent, _Mapping]] = ...,
        begin_block: _Optional[_Union[BeginBlock, _Mapping]] = ...,
        end_block: _Optional[_Union[EndBlock, _Mapping]] = ...,
        protocol_upgrade_started: _Optional[
            _Union[ProtocolUpgradeStarted, _Mapping]
        ] = ...,
        settle_market: _Optional[_Union[SettleMarket, _Mapping]] = ...,
        transaction_result: _Optional[_Union[TransactionResult, _Mapping]] = ...,
        core_snapshot_event: _Optional[_Union[CoreSnapshotData, _Mapping]] = ...,
        protocol_upgrade_data_node_ready: _Optional[
            _Union[ProtocolUpgradeDataNodeReady, _Mapping]
        ] = ...,
        distressed_orders: _Optional[_Union[DistressedOrders, _Mapping]] = ...,
        expired_orders: _Optional[_Union[ExpiredOrders, _Mapping]] = ...,
        distressed_positions: _Optional[_Union[DistressedPositions, _Mapping]] = ...,
        stop_order: _Optional[_Union[StopOrderEvent, _Mapping]] = ...,
        funding_period: _Optional[_Union[FundingPeriod, _Mapping]] = ...,
        funding_period_data_point: _Optional[
            _Union[FundingPeriodDataPoint, _Mapping]
        ] = ...,
        team_created: _Optional[_Union[TeamCreated, _Mapping]] = ...,
        team_updated: _Optional[_Union[TeamUpdated, _Mapping]] = ...,
        referee_switched_team: _Optional[_Union[RefereeSwitchedTeam, _Mapping]] = ...,
        referee_joined_team: _Optional[_Union[RefereeJoinedTeam, _Mapping]] = ...,
        referral_program_started: _Optional[
            _Union[ReferralProgramStarted, _Mapping]
        ] = ...,
        referral_program_updated: _Optional[
            _Union[ReferralProgramUpdated, _Mapping]
        ] = ...,
        referral_program_ended: _Optional[_Union[ReferralProgramEnded, _Mapping]] = ...,
        referral_set_created: _Optional[_Union[ReferralSetCreated, _Mapping]] = ...,
        referee_joined_referral_set: _Optional[
            _Union[RefereeJoinedReferralSet, _Mapping]
        ] = ...,
        party_activity_streak: _Optional[_Union[PartyActivityStreak, _Mapping]] = ...,
        volume_discount_program_started: _Optional[
            _Union[VolumeDiscountProgramStarted, _Mapping]
        ] = ...,
        volume_discount_program_updated: _Optional[
            _Union[VolumeDiscountProgramUpdated, _Mapping]
        ] = ...,
        volume_discount_program_ended: _Optional[
            _Union[VolumeDiscountProgramEnded, _Mapping]
        ] = ...,
        referral_set_stats_updated: _Optional[
            _Union[ReferralSetStatsUpdated, _Mapping]
        ] = ...,
        vesting_stats_updated: _Optional[_Union[VestingStatsUpdated, _Mapping]] = ...,
        volume_discount_stats_updated: _Optional[
            _Union[VolumeDiscountStatsUpdated, _Mapping]
        ] = ...,
        fees_stats: _Optional[_Union[FeesStats, _Mapping]] = ...,
        funding_payments: _Optional[_Union[FundingPayments, _Mapping]] = ...,
        paid_liquidity_fees_stats: _Optional[
            _Union[PaidLiquidityFeesStats, _Mapping]
        ] = ...,
        vesting_balances_summary: _Optional[
            _Union[VestingBalancesSummary, _Mapping]
        ] = ...,
        transfer_fees: _Optional[_Union[TransferFees, _Mapping]] = ...,
        transfer_fees_discount: _Optional[_Union[TransferFeesDiscount, _Mapping]] = ...,
        party_margin_mode_updated: _Optional[
            _Union[PartyMarginModeUpdated, _Mapping]
        ] = ...,
        market: _Optional[_Union[MarketEvent, _Mapping]] = ...,
        tx_err_event: _Optional[_Union[TxErrorEvent, _Mapping]] = ...,
        version: _Optional[int] = ...,
        chain_id: _Optional[str] = ...,
        tx_hash: _Optional[str] = ...,
    ) -> None: ...
