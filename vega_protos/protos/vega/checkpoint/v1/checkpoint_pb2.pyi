from vega import assets_pb2 as _assets_pb2
from vega import chain_events_pb2 as _chain_events_pb2
from vega.events.v1 import events_pb2 as _events_pb2
from vega import governance_pb2 as _governance_pb2
from vega import markets_pb2 as _markets_pb2
from vega import vega_pb2 as _vega_pb2
from google.protobuf.internal import containers as _containers
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

class CheckpointState(_message.Message):
    __slots__ = ("hash", "state")
    HASH_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    hash: bytes
    state: bytes
    def __init__(
        self, hash: _Optional[bytes] = ..., state: _Optional[bytes] = ...
    ) -> None: ...

class Checkpoint(_message.Message):
    __slots__ = (
        "governance",
        "assets",
        "collateral",
        "network_parameters",
        "delegation",
        "epoch",
        "block",
        "rewards",
        "banking",
        "validators",
        "staking",
        "multisig_control",
        "market_tracker",
        "execution",
    )
    GOVERNANCE_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    COLLATERAL_FIELD_NUMBER: _ClassVar[int]
    NETWORK_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    DELEGATION_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    REWARDS_FIELD_NUMBER: _ClassVar[int]
    BANKING_FIELD_NUMBER: _ClassVar[int]
    VALIDATORS_FIELD_NUMBER: _ClassVar[int]
    STAKING_FIELD_NUMBER: _ClassVar[int]
    MULTISIG_CONTROL_FIELD_NUMBER: _ClassVar[int]
    MARKET_TRACKER_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_FIELD_NUMBER: _ClassVar[int]
    governance: bytes
    assets: bytes
    collateral: bytes
    network_parameters: bytes
    delegation: bytes
    epoch: bytes
    block: bytes
    rewards: bytes
    banking: bytes
    validators: bytes
    staking: bytes
    multisig_control: bytes
    market_tracker: bytes
    execution: bytes
    def __init__(
        self,
        governance: _Optional[bytes] = ...,
        assets: _Optional[bytes] = ...,
        collateral: _Optional[bytes] = ...,
        network_parameters: _Optional[bytes] = ...,
        delegation: _Optional[bytes] = ...,
        epoch: _Optional[bytes] = ...,
        block: _Optional[bytes] = ...,
        rewards: _Optional[bytes] = ...,
        banking: _Optional[bytes] = ...,
        validators: _Optional[bytes] = ...,
        staking: _Optional[bytes] = ...,
        multisig_control: _Optional[bytes] = ...,
        market_tracker: _Optional[bytes] = ...,
        execution: _Optional[bytes] = ...,
    ) -> None: ...

class AssetEntry(_message.Message):
    __slots__ = ("id", "asset_details")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_DETAILS_FIELD_NUMBER: _ClassVar[int]
    id: str
    asset_details: _assets_pb2.AssetDetails
    def __init__(
        self,
        id: _Optional[str] = ...,
        asset_details: _Optional[_Union[_assets_pb2.AssetDetails, _Mapping]] = ...,
    ) -> None: ...

class Assets(_message.Message):
    __slots__ = ("assets", "pending_listing_assets")
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    PENDING_LISTING_ASSETS_FIELD_NUMBER: _ClassVar[int]
    assets: _containers.RepeatedCompositeFieldContainer[AssetEntry]
    pending_listing_assets: _containers.RepeatedCompositeFieldContainer[AssetEntry]
    def __init__(
        self,
        assets: _Optional[_Iterable[_Union[AssetEntry, _Mapping]]] = ...,
        pending_listing_assets: _Optional[
            _Iterable[_Union[AssetEntry, _Mapping]]
        ] = ...,
    ) -> None: ...

class AssetBalance(_message.Message):
    __slots__ = ("party", "asset", "balance")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    party: str
    asset: str
    balance: str
    def __init__(
        self,
        party: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        balance: _Optional[str] = ...,
    ) -> None: ...

class Collateral(_message.Message):
    __slots__ = ("balances",)
    BALANCES_FIELD_NUMBER: _ClassVar[int]
    balances: _containers.RepeatedCompositeFieldContainer[AssetBalance]
    def __init__(
        self, balances: _Optional[_Iterable[_Union[AssetBalance, _Mapping]]] = ...
    ) -> None: ...

class NetParams(_message.Message):
    __slots__ = ("params",)
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    params: _containers.RepeatedCompositeFieldContainer[_vega_pb2.NetworkParameter]
    def __init__(
        self,
        params: _Optional[
            _Iterable[_Union[_vega_pb2.NetworkParameter, _Mapping]]
        ] = ...,
    ) -> None: ...

class Proposals(_message.Message):
    __slots__ = ("proposals",)
    PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    proposals: _containers.RepeatedCompositeFieldContainer[_governance_pb2.Proposal]
    def __init__(
        self,
        proposals: _Optional[
            _Iterable[_Union[_governance_pb2.Proposal, _Mapping]]
        ] = ...,
    ) -> None: ...

class DelegateEntry(_message.Message):
    __slots__ = ("party", "node", "amount", "undelegate", "epoch_seq")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    UNDELEGATE_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    party: str
    node: str
    amount: str
    undelegate: bool
    epoch_seq: int
    def __init__(
        self,
        party: _Optional[str] = ...,
        node: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        undelegate: bool = ...,
        epoch_seq: _Optional[int] = ...,
    ) -> None: ...

class Delegate(_message.Message):
    __slots__ = ("active", "pending", "auto_delegation")
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    AUTO_DELEGATION_FIELD_NUMBER: _ClassVar[int]
    active: _containers.RepeatedCompositeFieldContainer[DelegateEntry]
    pending: _containers.RepeatedCompositeFieldContainer[DelegateEntry]
    auto_delegation: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        active: _Optional[_Iterable[_Union[DelegateEntry, _Mapping]]] = ...,
        pending: _Optional[_Iterable[_Union[DelegateEntry, _Mapping]]] = ...,
        auto_delegation: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class Block(_message.Message):
    __slots__ = ("height",)
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    height: int
    def __init__(self, height: _Optional[int] = ...) -> None: ...

class Rewards(_message.Message):
    __slots__ = ("rewards",)
    REWARDS_FIELD_NUMBER: _ClassVar[int]
    rewards: _containers.RepeatedCompositeFieldContainer[RewardPayout]
    def __init__(
        self, rewards: _Optional[_Iterable[_Union[RewardPayout, _Mapping]]] = ...
    ) -> None: ...

class RewardPayout(_message.Message):
    __slots__ = ("payout_time", "rewards_payout")
    PAYOUT_TIME_FIELD_NUMBER: _ClassVar[int]
    REWARDS_PAYOUT_FIELD_NUMBER: _ClassVar[int]
    payout_time: int
    rewards_payout: _containers.RepeatedCompositeFieldContainer[PendingRewardPayout]
    def __init__(
        self,
        payout_time: _Optional[int] = ...,
        rewards_payout: _Optional[
            _Iterable[_Union[PendingRewardPayout, _Mapping]]
        ] = ...,
    ) -> None: ...

class PendingRewardPayout(_message.Message):
    __slots__ = (
        "from_account",
        "asset",
        "party_amount",
        "total_reward",
        "epoch_seq",
        "timestamp",
    )
    FROM_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    PARTY_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REWARD_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    from_account: str
    asset: str
    party_amount: _containers.RepeatedCompositeFieldContainer[PartyAmount]
    total_reward: str
    epoch_seq: str
    timestamp: int
    def __init__(
        self,
        from_account: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        party_amount: _Optional[_Iterable[_Union[PartyAmount, _Mapping]]] = ...,
        total_reward: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
    ) -> None: ...

class PartyAmount(_message.Message):
    __slots__ = ("party", "amount")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    party: str
    amount: str
    def __init__(
        self, party: _Optional[str] = ..., amount: _Optional[str] = ...
    ) -> None: ...

class PendingKeyRotation(_message.Message):
    __slots__ = (
        "relative_target_block_height",
        "node_id",
        "new_pub_key",
        "new_pub_key_index",
    )
    RELATIVE_TARGET_BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    NEW_PUB_KEY_INDEX_FIELD_NUMBER: _ClassVar[int]
    relative_target_block_height: int
    node_id: str
    new_pub_key: str
    new_pub_key_index: int
    def __init__(
        self,
        relative_target_block_height: _Optional[int] = ...,
        node_id: _Optional[str] = ...,
        new_pub_key: _Optional[str] = ...,
        new_pub_key_index: _Optional[int] = ...,
    ) -> None: ...

class PendingEthereumKeyRotation(_message.Message):
    __slots__ = ("relative_target_block_height", "node_id", "new_address")
    RELATIVE_TARGET_BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    relative_target_block_height: int
    node_id: str
    new_address: str
    def __init__(
        self,
        relative_target_block_height: _Optional[int] = ...,
        node_id: _Optional[str] = ...,
        new_address: _Optional[str] = ...,
    ) -> None: ...

class ScheduledTransfer(_message.Message):
    __slots__ = ("transfer", "account_type", "reference", "oneoff_transfer")
    TRANSFER_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    ONEOFF_TRANSFER_FIELD_NUMBER: _ClassVar[int]
    transfer: _vega_pb2.Transfer
    account_type: _vega_pb2.AccountType
    reference: str
    oneoff_transfer: _events_pb2.Transfer
    def __init__(
        self,
        transfer: _Optional[_Union[_vega_pb2.Transfer, _Mapping]] = ...,
        account_type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
        reference: _Optional[str] = ...,
        oneoff_transfer: _Optional[_Union[_events_pb2.Transfer, _Mapping]] = ...,
    ) -> None: ...

class ScheduledTransferAtTime(_message.Message):
    __slots__ = ("deliver_on", "transfers")
    DELIVER_ON_FIELD_NUMBER: _ClassVar[int]
    TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    deliver_on: int
    transfers: _containers.RepeatedCompositeFieldContainer[ScheduledTransfer]
    def __init__(
        self,
        deliver_on: _Optional[int] = ...,
        transfers: _Optional[_Iterable[_Union[ScheduledTransfer, _Mapping]]] = ...,
    ) -> None: ...

class RecurringTransfers(_message.Message):
    __slots__ = ("recurring_transfers", "next_metric_update")
    RECURRING_TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    NEXT_METRIC_UPDATE_FIELD_NUMBER: _ClassVar[int]
    recurring_transfers: _containers.RepeatedCompositeFieldContainer[
        _events_pb2.Transfer
    ]
    next_metric_update: int
    def __init__(
        self,
        recurring_transfers: _Optional[
            _Iterable[_Union[_events_pb2.Transfer, _Mapping]]
        ] = ...,
        next_metric_update: _Optional[int] = ...,
    ) -> None: ...

class GovernanceTransfer(_message.Message):
    __slots__ = ("id", "reference", "status", "timestamp", "config")
    ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    id: str
    reference: str
    status: _events_pb2.Transfer.Status
    timestamp: int
    config: _governance_pb2.NewTransferConfiguration
    def __init__(
        self,
        id: _Optional[str] = ...,
        reference: _Optional[str] = ...,
        status: _Optional[_Union[_events_pb2.Transfer.Status, str]] = ...,
        timestamp: _Optional[int] = ...,
        config: _Optional[
            _Union[_governance_pb2.NewTransferConfiguration, _Mapping]
        ] = ...,
    ) -> None: ...

class ScheduledGovernanceTransferAtTime(_message.Message):
    __slots__ = ("deliver_on", "transfers")
    DELIVER_ON_FIELD_NUMBER: _ClassVar[int]
    TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    deliver_on: int
    transfers: _containers.RepeatedCompositeFieldContainer[GovernanceTransfer]
    def __init__(
        self,
        deliver_on: _Optional[int] = ...,
        transfers: _Optional[_Iterable[_Union[GovernanceTransfer, _Mapping]]] = ...,
    ) -> None: ...

class Banking(_message.Message):
    __slots__ = (
        "transfers_at_time",
        "recurring_transfers",
        "primary_bridge_state",
        "asset_actions",
        "last_seen_primary_eth_block",
        "seen_refs",
        "governance_transfers_at_time",
        "recurring_governance_transfers",
        "secondary_bridge_state",
        "last_seen_secondary_eth_block",
    )
    TRANSFERS_AT_TIME_FIELD_NUMBER: _ClassVar[int]
    RECURRING_TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_BRIDGE_STATE_FIELD_NUMBER: _ClassVar[int]
    ASSET_ACTIONS_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_PRIMARY_ETH_BLOCK_FIELD_NUMBER: _ClassVar[int]
    SEEN_REFS_FIELD_NUMBER: _ClassVar[int]
    GOVERNANCE_TRANSFERS_AT_TIME_FIELD_NUMBER: _ClassVar[int]
    RECURRING_GOVERNANCE_TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_BRIDGE_STATE_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_SECONDARY_ETH_BLOCK_FIELD_NUMBER: _ClassVar[int]
    transfers_at_time: _containers.RepeatedCompositeFieldContainer[
        ScheduledTransferAtTime
    ]
    recurring_transfers: RecurringTransfers
    primary_bridge_state: BridgeState
    asset_actions: _containers.RepeatedCompositeFieldContainer[AssetAction]
    last_seen_primary_eth_block: int
    seen_refs: _containers.RepeatedScalarFieldContainer[str]
    governance_transfers_at_time: _containers.RepeatedCompositeFieldContainer[
        ScheduledGovernanceTransferAtTime
    ]
    recurring_governance_transfers: _containers.RepeatedCompositeFieldContainer[
        GovernanceTransfer
    ]
    secondary_bridge_state: BridgeState
    last_seen_secondary_eth_block: int
    def __init__(
        self,
        transfers_at_time: _Optional[
            _Iterable[_Union[ScheduledTransferAtTime, _Mapping]]
        ] = ...,
        recurring_transfers: _Optional[_Union[RecurringTransfers, _Mapping]] = ...,
        primary_bridge_state: _Optional[_Union[BridgeState, _Mapping]] = ...,
        asset_actions: _Optional[_Iterable[_Union[AssetAction, _Mapping]]] = ...,
        last_seen_primary_eth_block: _Optional[int] = ...,
        seen_refs: _Optional[_Iterable[str]] = ...,
        governance_transfers_at_time: _Optional[
            _Iterable[_Union[ScheduledGovernanceTransferAtTime, _Mapping]]
        ] = ...,
        recurring_governance_transfers: _Optional[
            _Iterable[_Union[GovernanceTransfer, _Mapping]]
        ] = ...,
        secondary_bridge_state: _Optional[_Union[BridgeState, _Mapping]] = ...,
        last_seen_secondary_eth_block: _Optional[int] = ...,
    ) -> None: ...

class BridgeState(_message.Message):
    __slots__ = ("active", "block_height", "log_index", "chain_id")
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    active: bool
    block_height: int
    log_index: int
    chain_id: str
    def __init__(
        self,
        active: bool = ...,
        block_height: _Optional[int] = ...,
        log_index: _Optional[int] = ...,
        chain_id: _Optional[str] = ...,
    ) -> None: ...

class Validators(_message.Message):
    __slots__ = (
        "validator_state",
        "pending_key_rotations",
        "pending_ethereum_key_rotations",
    )
    VALIDATOR_STATE_FIELD_NUMBER: _ClassVar[int]
    PENDING_KEY_ROTATIONS_FIELD_NUMBER: _ClassVar[int]
    PENDING_ETHEREUM_KEY_ROTATIONS_FIELD_NUMBER: _ClassVar[int]
    validator_state: _containers.RepeatedCompositeFieldContainer[ValidatorState]
    pending_key_rotations: _containers.RepeatedCompositeFieldContainer[
        PendingKeyRotation
    ]
    pending_ethereum_key_rotations: _containers.RepeatedCompositeFieldContainer[
        PendingEthereumKeyRotation
    ]
    def __init__(
        self,
        validator_state: _Optional[_Iterable[_Union[ValidatorState, _Mapping]]] = ...,
        pending_key_rotations: _Optional[
            _Iterable[_Union[PendingKeyRotation, _Mapping]]
        ] = ...,
        pending_ethereum_key_rotations: _Optional[
            _Iterable[_Union[PendingEthereumKeyRotation, _Mapping]]
        ] = ...,
    ) -> None: ...

class ValidatorState(_message.Message):
    __slots__ = (
        "validator_update",
        "status",
        "eth_events_forwarded",
        "validator_power",
        "ranking_score",
        "heartbeat_block_index",
        "heartbeat_block_sigs",
    )
    VALIDATOR_UPDATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ETH_EVENTS_FORWARDED_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_POWER_FIELD_NUMBER: _ClassVar[int]
    RANKING_SCORE_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_BLOCK_INDEX_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_BLOCK_SIGS_FIELD_NUMBER: _ClassVar[int]
    validator_update: _events_pb2.ValidatorUpdate
    status: int
    eth_events_forwarded: int
    validator_power: int
    ranking_score: _vega_pb2.RankingScore
    heartbeat_block_index: int
    heartbeat_block_sigs: _containers.RepeatedScalarFieldContainer[bool]
    def __init__(
        self,
        validator_update: _Optional[
            _Union[_events_pb2.ValidatorUpdate, _Mapping]
        ] = ...,
        status: _Optional[int] = ...,
        eth_events_forwarded: _Optional[int] = ...,
        validator_power: _Optional[int] = ...,
        ranking_score: _Optional[_Union[_vega_pb2.RankingScore, _Mapping]] = ...,
        heartbeat_block_index: _Optional[int] = ...,
        heartbeat_block_sigs: _Optional[_Iterable[bool]] = ...,
    ) -> None: ...

class Staking(_message.Message):
    __slots__ = ("accepted", "last_block_seen")
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    LAST_BLOCK_SEEN_FIELD_NUMBER: _ClassVar[int]
    accepted: _containers.RepeatedCompositeFieldContainer[_events_pb2.StakeLinking]
    last_block_seen: int
    def __init__(
        self,
        accepted: _Optional[
            _Iterable[_Union[_events_pb2.StakeLinking, _Mapping]]
        ] = ...,
        last_block_seen: _Optional[int] = ...,
    ) -> None: ...

class MultisigControl(_message.Message):
    __slots__ = ("signers", "threshold_set", "last_block_seen")
    SIGNERS_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_SET_FIELD_NUMBER: _ClassVar[int]
    LAST_BLOCK_SEEN_FIELD_NUMBER: _ClassVar[int]
    signers: _containers.RepeatedCompositeFieldContainer[
        _events_pb2.ERC20MultiSigSignerEvent
    ]
    threshold_set: _events_pb2.ERC20MultiSigThresholdSetEvent
    last_block_seen: int
    def __init__(
        self,
        signers: _Optional[
            _Iterable[_Union[_events_pb2.ERC20MultiSigSignerEvent, _Mapping]]
        ] = ...,
        threshold_set: _Optional[
            _Union[_events_pb2.ERC20MultiSigThresholdSetEvent, _Mapping]
        ] = ...,
        last_block_seen: _Optional[int] = ...,
    ) -> None: ...

class MarketTracker(_message.Message):
    __slots__ = (
        "market_activity",
        "taker_notional_volume",
        "market_to_party_taker_notional_volume",
        "epoch_taker_fees",
        "game_eligibility_tracker",
    )
    MARKET_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    TAKER_NOTIONAL_VOLUME_FIELD_NUMBER: _ClassVar[int]
    MARKET_TO_PARTY_TAKER_NOTIONAL_VOLUME_FIELD_NUMBER: _ClassVar[int]
    EPOCH_TAKER_FEES_FIELD_NUMBER: _ClassVar[int]
    GAME_ELIGIBILITY_TRACKER_FIELD_NUMBER: _ClassVar[int]
    market_activity: _containers.RepeatedCompositeFieldContainer[MarketActivityTracker]
    taker_notional_volume: _containers.RepeatedCompositeFieldContainer[
        TakerNotionalVolume
    ]
    market_to_party_taker_notional_volume: _containers.RepeatedCompositeFieldContainer[
        MarketToPartyTakerNotionalVolume
    ]
    epoch_taker_fees: _containers.RepeatedCompositeFieldContainer[EpochPartyTakerFees]
    game_eligibility_tracker: _containers.RepeatedCompositeFieldContainer[
        GameEligibilityTracker
    ]
    def __init__(
        self,
        market_activity: _Optional[
            _Iterable[_Union[MarketActivityTracker, _Mapping]]
        ] = ...,
        taker_notional_volume: _Optional[
            _Iterable[_Union[TakerNotionalVolume, _Mapping]]
        ] = ...,
        market_to_party_taker_notional_volume: _Optional[
            _Iterable[_Union[MarketToPartyTakerNotionalVolume, _Mapping]]
        ] = ...,
        epoch_taker_fees: _Optional[
            _Iterable[_Union[EpochPartyTakerFees, _Mapping]]
        ] = ...,
        game_eligibility_tracker: _Optional[
            _Iterable[_Union[GameEligibilityTracker, _Mapping]]
        ] = ...,
    ) -> None: ...

class MarketActivityTracker(_message.Message):
    __slots__ = (
        "market",
        "asset",
        "maker_fees_received",
        "maker_fees_paid",
        "lp_fees",
        "proposer",
        "bonus_paid",
        "value_traded",
        "ready_to_delete",
        "time_weighted_position",
        "time_weighted_notional",
        "returns_data",
        "maker_fees_received_history",
        "maker_fees_paid_history",
        "lp_fees_history",
        "time_weighted_position_data_history",
        "time_weighted_notional_data_history",
        "returns_data_history",
        "infra_fees",
        "lp_paid_fees",
        "realised_returns",
        "realised_returns_history",
        "amm_parties",
        "buy_back_fees",
        "treasury_fees",
        "notional_volume_for_epoch",
        "epoch_notional_volume",
    )
    MARKET_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    MAKER_FEES_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    MAKER_FEES_PAID_FIELD_NUMBER: _ClassVar[int]
    LP_FEES_FIELD_NUMBER: _ClassVar[int]
    PROPOSER_FIELD_NUMBER: _ClassVar[int]
    BONUS_PAID_FIELD_NUMBER: _ClassVar[int]
    VALUE_TRADED_FIELD_NUMBER: _ClassVar[int]
    READY_TO_DELETE_FIELD_NUMBER: _ClassVar[int]
    TIME_WEIGHTED_POSITION_FIELD_NUMBER: _ClassVar[int]
    TIME_WEIGHTED_NOTIONAL_FIELD_NUMBER: _ClassVar[int]
    RETURNS_DATA_FIELD_NUMBER: _ClassVar[int]
    MAKER_FEES_RECEIVED_HISTORY_FIELD_NUMBER: _ClassVar[int]
    MAKER_FEES_PAID_HISTORY_FIELD_NUMBER: _ClassVar[int]
    LP_FEES_HISTORY_FIELD_NUMBER: _ClassVar[int]
    TIME_WEIGHTED_POSITION_DATA_HISTORY_FIELD_NUMBER: _ClassVar[int]
    TIME_WEIGHTED_NOTIONAL_DATA_HISTORY_FIELD_NUMBER: _ClassVar[int]
    RETURNS_DATA_HISTORY_FIELD_NUMBER: _ClassVar[int]
    INFRA_FEES_FIELD_NUMBER: _ClassVar[int]
    LP_PAID_FEES_FIELD_NUMBER: _ClassVar[int]
    REALISED_RETURNS_FIELD_NUMBER: _ClassVar[int]
    REALISED_RETURNS_HISTORY_FIELD_NUMBER: _ClassVar[int]
    AMM_PARTIES_FIELD_NUMBER: _ClassVar[int]
    BUY_BACK_FEES_FIELD_NUMBER: _ClassVar[int]
    TREASURY_FEES_FIELD_NUMBER: _ClassVar[int]
    NOTIONAL_VOLUME_FOR_EPOCH_FIELD_NUMBER: _ClassVar[int]
    EPOCH_NOTIONAL_VOLUME_FIELD_NUMBER: _ClassVar[int]
    market: str
    asset: str
    maker_fees_received: _containers.RepeatedCompositeFieldContainer[PartyFees]
    maker_fees_paid: _containers.RepeatedCompositeFieldContainer[PartyFees]
    lp_fees: _containers.RepeatedCompositeFieldContainer[PartyFees]
    proposer: str
    bonus_paid: _containers.RepeatedScalarFieldContainer[str]
    value_traded: str
    ready_to_delete: bool
    time_weighted_position: _containers.RepeatedCompositeFieldContainer[TWPositionData]
    time_weighted_notional: _containers.RepeatedCompositeFieldContainer[TWNotionalData]
    returns_data: _containers.RepeatedCompositeFieldContainer[ReturnsData]
    maker_fees_received_history: _containers.RepeatedCompositeFieldContainer[
        EpochPartyFees
    ]
    maker_fees_paid_history: _containers.RepeatedCompositeFieldContainer[EpochPartyFees]
    lp_fees_history: _containers.RepeatedCompositeFieldContainer[EpochPartyFees]
    time_weighted_position_data_history: _containers.RepeatedCompositeFieldContainer[
        EpochTimeWeightPositionData
    ]
    time_weighted_notional_data_history: _containers.RepeatedCompositeFieldContainer[
        EpochTimeWeightedNotionalData
    ]
    returns_data_history: _containers.RepeatedCompositeFieldContainer[EpochReturnsData]
    infra_fees: _containers.RepeatedCompositeFieldContainer[PartyFees]
    lp_paid_fees: _containers.RepeatedCompositeFieldContainer[PartyFees]
    realised_returns: _containers.RepeatedCompositeFieldContainer[ReturnsData]
    realised_returns_history: _containers.RepeatedCompositeFieldContainer[
        EpochReturnsData
    ]
    amm_parties: _containers.RepeatedScalarFieldContainer[str]
    buy_back_fees: _containers.RepeatedCompositeFieldContainer[PartyFees]
    treasury_fees: _containers.RepeatedCompositeFieldContainer[PartyFees]
    notional_volume_for_epoch: str
    epoch_notional_volume: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        market: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        maker_fees_received: _Optional[_Iterable[_Union[PartyFees, _Mapping]]] = ...,
        maker_fees_paid: _Optional[_Iterable[_Union[PartyFees, _Mapping]]] = ...,
        lp_fees: _Optional[_Iterable[_Union[PartyFees, _Mapping]]] = ...,
        proposer: _Optional[str] = ...,
        bonus_paid: _Optional[_Iterable[str]] = ...,
        value_traded: _Optional[str] = ...,
        ready_to_delete: bool = ...,
        time_weighted_position: _Optional[
            _Iterable[_Union[TWPositionData, _Mapping]]
        ] = ...,
        time_weighted_notional: _Optional[
            _Iterable[_Union[TWNotionalData, _Mapping]]
        ] = ...,
        returns_data: _Optional[_Iterable[_Union[ReturnsData, _Mapping]]] = ...,
        maker_fees_received_history: _Optional[
            _Iterable[_Union[EpochPartyFees, _Mapping]]
        ] = ...,
        maker_fees_paid_history: _Optional[
            _Iterable[_Union[EpochPartyFees, _Mapping]]
        ] = ...,
        lp_fees_history: _Optional[_Iterable[_Union[EpochPartyFees, _Mapping]]] = ...,
        time_weighted_position_data_history: _Optional[
            _Iterable[_Union[EpochTimeWeightPositionData, _Mapping]]
        ] = ...,
        time_weighted_notional_data_history: _Optional[
            _Iterable[_Union[EpochTimeWeightedNotionalData, _Mapping]]
        ] = ...,
        returns_data_history: _Optional[
            _Iterable[_Union[EpochReturnsData, _Mapping]]
        ] = ...,
        infra_fees: _Optional[_Iterable[_Union[PartyFees, _Mapping]]] = ...,
        lp_paid_fees: _Optional[_Iterable[_Union[PartyFees, _Mapping]]] = ...,
        realised_returns: _Optional[_Iterable[_Union[ReturnsData, _Mapping]]] = ...,
        realised_returns_history: _Optional[
            _Iterable[_Union[EpochReturnsData, _Mapping]]
        ] = ...,
        amm_parties: _Optional[_Iterable[str]] = ...,
        buy_back_fees: _Optional[_Iterable[_Union[PartyFees, _Mapping]]] = ...,
        treasury_fees: _Optional[_Iterable[_Union[PartyFees, _Mapping]]] = ...,
        notional_volume_for_epoch: _Optional[str] = ...,
        epoch_notional_volume: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class GameEligibilityTracker(_message.Message):
    __slots__ = ("game_id", "epoch_eligibility")
    GAME_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_ELIGIBILITY_FIELD_NUMBER: _ClassVar[int]
    game_id: str
    epoch_eligibility: _containers.RepeatedCompositeFieldContainer[EpochEligibility]
    def __init__(
        self,
        game_id: _Optional[str] = ...,
        epoch_eligibility: _Optional[
            _Iterable[_Union[EpochEligibility, _Mapping]]
        ] = ...,
    ) -> None: ...

class EpochEligibility(_message.Message):
    __slots__ = ("eligible_parties",)
    ELIGIBLE_PARTIES_FIELD_NUMBER: _ClassVar[int]
    eligible_parties: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, eligible_parties: _Optional[_Iterable[str]] = ...) -> None: ...

class EpochPartyTakerFees(_message.Message):
    __slots__ = ("epoch_party_taker_fees_paid",)
    EPOCH_PARTY_TAKER_FEES_PAID_FIELD_NUMBER: _ClassVar[int]
    epoch_party_taker_fees_paid: _containers.RepeatedCompositeFieldContainer[
        AssetMarketPartyTakerFees
    ]
    def __init__(
        self,
        epoch_party_taker_fees_paid: _Optional[
            _Iterable[_Union[AssetMarketPartyTakerFees, _Mapping]]
        ] = ...,
    ) -> None: ...

class EpochTimeWeightPositionData(_message.Message):
    __slots__ = ("party_time_weighted_positions",)
    PARTY_TIME_WEIGHTED_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    party_time_weighted_positions: _containers.RepeatedCompositeFieldContainer[
        PartyTimeWeightedPosition
    ]
    def __init__(
        self,
        party_time_weighted_positions: _Optional[
            _Iterable[_Union[PartyTimeWeightedPosition, _Mapping]]
        ] = ...,
    ) -> None: ...

class EpochTimeWeightedNotionalData(_message.Message):
    __slots__ = ("party_time_weighted_notionals",)
    PARTY_TIME_WEIGHTED_NOTIONALS_FIELD_NUMBER: _ClassVar[int]
    party_time_weighted_notionals: _containers.RepeatedCompositeFieldContainer[
        PartyTimeWeightedNotional
    ]
    def __init__(
        self,
        party_time_weighted_notionals: _Optional[
            _Iterable[_Union[PartyTimeWeightedNotional, _Mapping]]
        ] = ...,
    ) -> None: ...

class PartyTimeWeightedNotional(_message.Message):
    __slots__ = ("party", "tw_notional")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    TW_NOTIONAL_FIELD_NUMBER: _ClassVar[int]
    party: str
    tw_notional: bytes
    def __init__(
        self, party: _Optional[str] = ..., tw_notional: _Optional[bytes] = ...
    ) -> None: ...

class PartyTimeWeightedPosition(_message.Message):
    __slots__ = ("party", "tw_position")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    TW_POSITION_FIELD_NUMBER: _ClassVar[int]
    party: str
    tw_position: int
    def __init__(
        self, party: _Optional[str] = ..., tw_position: _Optional[int] = ...
    ) -> None: ...

class AssetMarketPartyTakerFees(_message.Message):
    __slots__ = ("asset", "market", "taker_fees")
    ASSET_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    TAKER_FEES_FIELD_NUMBER: _ClassVar[int]
    asset: str
    market: str
    taker_fees: _containers.RepeatedCompositeFieldContainer[PartyTakerFees]
    def __init__(
        self,
        asset: _Optional[str] = ...,
        market: _Optional[str] = ...,
        taker_fees: _Optional[_Iterable[_Union[PartyTakerFees, _Mapping]]] = ...,
    ) -> None: ...

class PartyTakerFees(_message.Message):
    __slots__ = ("party", "taker_fees")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    TAKER_FEES_FIELD_NUMBER: _ClassVar[int]
    party: str
    taker_fees: bytes
    def __init__(
        self, party: _Optional[str] = ..., taker_fees: _Optional[bytes] = ...
    ) -> None: ...

class EpochPartyFees(_message.Message):
    __slots__ = ("party_fees",)
    PARTY_FEES_FIELD_NUMBER: _ClassVar[int]
    party_fees: _containers.RepeatedCompositeFieldContainer[PartyFeesHistory]
    def __init__(
        self, party_fees: _Optional[_Iterable[_Union[PartyFeesHistory, _Mapping]]] = ...
    ) -> None: ...

class TakerNotionalVolume(_message.Message):
    __slots__ = ("party", "volume")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    party: str
    volume: bytes
    def __init__(
        self, party: _Optional[str] = ..., volume: _Optional[bytes] = ...
    ) -> None: ...

class MarketToPartyTakerNotionalVolume(_message.Message):
    __slots__ = ("market", "taker_notional_volume")
    MARKET_FIELD_NUMBER: _ClassVar[int]
    TAKER_NOTIONAL_VOLUME_FIELD_NUMBER: _ClassVar[int]
    market: str
    taker_notional_volume: _containers.RepeatedCompositeFieldContainer[
        TakerNotionalVolume
    ]
    def __init__(
        self,
        market: _Optional[str] = ...,
        taker_notional_volume: _Optional[
            _Iterable[_Union[TakerNotionalVolume, _Mapping]]
        ] = ...,
    ) -> None: ...

class EpochReturnsData(_message.Message):
    __slots__ = ("returns",)
    RETURNS_FIELD_NUMBER: _ClassVar[int]
    returns: _containers.RepeatedCompositeFieldContainer[ReturnsData]
    def __init__(
        self, returns: _Optional[_Iterable[_Union[ReturnsData, _Mapping]]] = ...
    ) -> None: ...

class ReturnsData(_message.Message):
    __slots__ = ("party",)
    PARTY_FIELD_NUMBER: _ClassVar[int]
    RETURN_FIELD_NUMBER: _ClassVar[int]
    party: str
    def __init__(self, party: _Optional[str] = ..., **kwargs) -> None: ...

class TWPositionData(_message.Message):
    __slots__ = ("party", "position", "time", "tw_position")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    TW_POSITION_FIELD_NUMBER: _ClassVar[int]
    party: str
    position: int
    time: int
    tw_position: int
    def __init__(
        self,
        party: _Optional[str] = ...,
        position: _Optional[int] = ...,
        time: _Optional[int] = ...,
        tw_position: _Optional[int] = ...,
    ) -> None: ...

class TWNotionalData(_message.Message):
    __slots__ = ("party", "notional", "time", "tw_notional", "price")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    NOTIONAL_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    TW_NOTIONAL_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    party: str
    notional: bytes
    time: int
    tw_notional: bytes
    price: bytes
    def __init__(
        self,
        party: _Optional[str] = ...,
        notional: _Optional[bytes] = ...,
        time: _Optional[int] = ...,
        tw_notional: _Optional[bytes] = ...,
        price: _Optional[bytes] = ...,
    ) -> None: ...

class PartyFees(_message.Message):
    __slots__ = ("party", "fee")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    FEE_FIELD_NUMBER: _ClassVar[int]
    party: str
    fee: str
    def __init__(
        self, party: _Optional[str] = ..., fee: _Optional[str] = ...
    ) -> None: ...

class PartyFeesHistory(_message.Message):
    __slots__ = ("party", "fee")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    FEE_FIELD_NUMBER: _ClassVar[int]
    party: str
    fee: bytes
    def __init__(
        self, party: _Optional[str] = ..., fee: _Optional[bytes] = ...
    ) -> None: ...

class AssetAction(_message.Message):
    __slots__ = (
        "id",
        "state",
        "asset",
        "block_number",
        "tx_index",
        "hash",
        "builtin_deposit",
        "erc20_deposit",
        "asset_list",
        "erc20_asset_limits_updated",
        "erc20_bridge_stopped",
        "erc20_bridge_resumed",
        "chain_id",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    BLOCK_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TX_INDEX_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    BUILTIN_DEPOSIT_FIELD_NUMBER: _ClassVar[int]
    ERC20_DEPOSIT_FIELD_NUMBER: _ClassVar[int]
    ASSET_LIST_FIELD_NUMBER: _ClassVar[int]
    ERC20_ASSET_LIMITS_UPDATED_FIELD_NUMBER: _ClassVar[int]
    ERC20_BRIDGE_STOPPED_FIELD_NUMBER: _ClassVar[int]
    ERC20_BRIDGE_RESUMED_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    state: int
    asset: str
    block_number: int
    tx_index: int
    hash: str
    builtin_deposit: _chain_events_pb2.BuiltinAssetDeposit
    erc20_deposit: _chain_events_pb2.ERC20Deposit
    asset_list: _chain_events_pb2.ERC20AssetList
    erc20_asset_limits_updated: _chain_events_pb2.ERC20AssetLimitsUpdated
    erc20_bridge_stopped: bool
    erc20_bridge_resumed: bool
    chain_id: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        state: _Optional[int] = ...,
        asset: _Optional[str] = ...,
        block_number: _Optional[int] = ...,
        tx_index: _Optional[int] = ...,
        hash: _Optional[str] = ...,
        builtin_deposit: _Optional[
            _Union[_chain_events_pb2.BuiltinAssetDeposit, _Mapping]
        ] = ...,
        erc20_deposit: _Optional[
            _Union[_chain_events_pb2.ERC20Deposit, _Mapping]
        ] = ...,
        asset_list: _Optional[_Union[_chain_events_pb2.ERC20AssetList, _Mapping]] = ...,
        erc20_asset_limits_updated: _Optional[
            _Union[_chain_events_pb2.ERC20AssetLimitsUpdated, _Mapping]
        ] = ...,
        erc20_bridge_stopped: bool = ...,
        erc20_bridge_resumed: bool = ...,
        chain_id: _Optional[str] = ...,
    ) -> None: ...

class ELSShare(_message.Message):
    __slots__ = ("party_id", "share", "supplied_stake", "virtual_stake", "avg")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    SHARE_FIELD_NUMBER: _ClassVar[int]
    SUPPLIED_STAKE_FIELD_NUMBER: _ClassVar[int]
    VIRTUAL_STAKE_FIELD_NUMBER: _ClassVar[int]
    AVG_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    share: str
    supplied_stake: str
    virtual_stake: str
    avg: str
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        share: _Optional[str] = ...,
        supplied_stake: _Optional[str] = ...,
        virtual_stake: _Optional[str] = ...,
        avg: _Optional[str] = ...,
    ) -> None: ...

class MarketState(_message.Message):
    __slots__ = (
        "id",
        "shares",
        "insurance_balance",
        "last_trade_value",
        "last_trade_volume",
        "succession_window",
        "market",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    SHARES_FIELD_NUMBER: _ClassVar[int]
    INSURANCE_BALANCE_FIELD_NUMBER: _ClassVar[int]
    LAST_TRADE_VALUE_FIELD_NUMBER: _ClassVar[int]
    LAST_TRADE_VOLUME_FIELD_NUMBER: _ClassVar[int]
    SUCCESSION_WINDOW_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    id: str
    shares: _containers.RepeatedCompositeFieldContainer[ELSShare]
    insurance_balance: str
    last_trade_value: str
    last_trade_volume: str
    succession_window: int
    market: _markets_pb2.Market
    def __init__(
        self,
        id: _Optional[str] = ...,
        shares: _Optional[_Iterable[_Union[ELSShare, _Mapping]]] = ...,
        insurance_balance: _Optional[str] = ...,
        last_trade_value: _Optional[str] = ...,
        last_trade_volume: _Optional[str] = ...,
        succession_window: _Optional[int] = ...,
        market: _Optional[_Union[_markets_pb2.Market, _Mapping]] = ...,
    ) -> None: ...

class ExecutionState(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[MarketState]
    def __init__(
        self, data: _Optional[_Iterable[_Union[MarketState, _Mapping]]] = ...
    ) -> None: ...
