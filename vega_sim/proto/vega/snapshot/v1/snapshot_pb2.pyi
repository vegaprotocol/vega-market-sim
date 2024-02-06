from vega import assets_pb2 as _assets_pb2
from vega import chain_events_pb2 as _chain_events_pb2
from vega.checkpoint.v1 import checkpoint_pb2 as _checkpoint_pb2
from vega.data.v1 import data_pb2 as _data_pb2
from vega.events.v1 import events_pb2 as _events_pb2
from vega import governance_pb2 as _governance_pb2
from vega import markets_pb2 as _markets_pb2
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

class Format(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FORMAT_UNSPECIFIED: _ClassVar[Format]
    FORMAT_PROTO: _ClassVar[Format]
    FORMAT_PROTO_COMPRESSED: _ClassVar[Format]
    FORMAT_JSON: _ClassVar[Format]

FORMAT_UNSPECIFIED: Format
FORMAT_PROTO: Format
FORMAT_PROTO_COMPRESSED: Format
FORMAT_JSON: Format

class Snapshot(_message.Message):
    __slots__ = ("height", "format", "chunks", "hash", "metadata")
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    CHUNKS_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    height: int
    format: Format
    chunks: int
    hash: bytes
    metadata: bytes
    def __init__(
        self,
        height: _Optional[int] = ...,
        format: _Optional[_Union[Format, str]] = ...,
        chunks: _Optional[int] = ...,
        hash: _Optional[bytes] = ...,
        metadata: _Optional[bytes] = ...,
    ) -> None: ...

class NodeHash(_message.Message):
    __slots__ = ("key", "hash", "height", "version", "is_leaf")
    KEY_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    IS_LEAF_FIELD_NUMBER: _ClassVar[int]
    key: str
    hash: str
    height: int
    version: int
    is_leaf: bool
    def __init__(
        self,
        key: _Optional[str] = ...,
        hash: _Optional[str] = ...,
        height: _Optional[int] = ...,
        version: _Optional[int] = ...,
        is_leaf: bool = ...,
    ) -> None: ...

class Metadata(_message.Message):
    __slots__ = (
        "version",
        "chunk_hashes",
        "node_hashes",
        "protocol_version",
        "protocol_upgrade",
    )
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CHUNK_HASHES_FIELD_NUMBER: _ClassVar[int]
    NODE_HASHES_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_UPGRADE_FIELD_NUMBER: _ClassVar[int]
    version: int
    chunk_hashes: _containers.RepeatedScalarFieldContainer[str]
    node_hashes: _containers.RepeatedCompositeFieldContainer[NodeHash]
    protocol_version: str
    protocol_upgrade: bool
    def __init__(
        self,
        version: _Optional[int] = ...,
        chunk_hashes: _Optional[_Iterable[str]] = ...,
        node_hashes: _Optional[_Iterable[_Union[NodeHash, _Mapping]]] = ...,
        protocol_version: _Optional[str] = ...,
        protocol_upgrade: bool = ...,
    ) -> None: ...

class Chunk(_message.Message):
    __slots__ = ("data", "nr", "of")
    DATA_FIELD_NUMBER: _ClassVar[int]
    NR_FIELD_NUMBER: _ClassVar[int]
    OF_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Payload]
    nr: int
    of: int
    def __init__(
        self,
        data: _Optional[_Iterable[_Union[Payload, _Mapping]]] = ...,
        nr: _Optional[int] = ...,
        of: _Optional[int] = ...,
    ) -> None: ...

class Payload(_message.Message):
    __slots__ = (
        "active_assets",
        "pending_assets",
        "banking_withdrawals",
        "banking_deposits",
        "banking_seen",
        "banking_asset_actions",
        "checkpoint",
        "collateral_accounts",
        "collateral_assets",
        "delegation_active",
        "delegation_pending",
        "delegation_auto",
        "governance_active",
        "governance_enacted",
        "staking_accounts",
        "matching_book",
        "network_parameters",
        "execution_markets",
        "market_positions",
        "app_state",
        "epoch",
        "rewards_pending_payouts",
        "governance_node",
        "limit_state",
        "vote_spam_policy",
        "simple_spam_policy",
        "notary",
        "event_forwarder",
        "stake_verifier_deposited",
        "stake_verifier_removed",
        "witness",
        "delegation_last_reconciliation_time",
        "topology",
        "oracle_data",
        "liquidity_parameters",
        "liquidity_pending_provisions",
        "liquidity_parties_liquidity_orders",
        "liquidity_parties_orders",
        "liquidity_provisions",
        "liquidity_supplied",
        "liquidity_target",
        "floating_point_consensus",
        "market_tracker",
        "banking_recurring_transfers",
        "banking_scheduled_transfers",
        "erc20_multisig_topology_verified",
        "erc20_multisig_topology_pending",
        "proof_of_work",
        "pending_asset_updates",
        "protocol_upgrade_proposals",
        "banking_bridge_state",
        "settlement_state",
        "liquidity_scores",
        "spot_liquidity_target",
        "banking_recurring_governance_transfers",
        "banking_scheduled_governance_transfers",
        "eth_contract_call_results",
        "eth_oracle_verifier_last_block",
        "liquidity_v2_provisions",
        "liquidity_v2_pending_provisions",
        "liquidity_v2_performances",
        "liquidity_v2_supplied",
        "liquidity_v2_scores",
        "holding_account_tracker",
        "teams",
        "team_switches",
        "vesting",
        "referral_program",
        "activity_streak",
        "volume_discount_program",
        "liquidity_v2_parameters",
        "liquidity_v2_paid_fees_stats",
        "liquidation",
        "banking_transfer_fee_discounts",
        "governance_batch_active",
        "parties",
        "l2_eth_oracles",
    )
    ACTIVE_ASSETS_FIELD_NUMBER: _ClassVar[int]
    PENDING_ASSETS_FIELD_NUMBER: _ClassVar[int]
    BANKING_WITHDRAWALS_FIELD_NUMBER: _ClassVar[int]
    BANKING_DEPOSITS_FIELD_NUMBER: _ClassVar[int]
    BANKING_SEEN_FIELD_NUMBER: _ClassVar[int]
    BANKING_ASSET_ACTIONS_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINT_FIELD_NUMBER: _ClassVar[int]
    COLLATERAL_ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    COLLATERAL_ASSETS_FIELD_NUMBER: _ClassVar[int]
    DELEGATION_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DELEGATION_PENDING_FIELD_NUMBER: _ClassVar[int]
    DELEGATION_AUTO_FIELD_NUMBER: _ClassVar[int]
    GOVERNANCE_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    GOVERNANCE_ENACTED_FIELD_NUMBER: _ClassVar[int]
    STAKING_ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    MATCHING_BOOK_FIELD_NUMBER: _ClassVar[int]
    NETWORK_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_MARKETS_FIELD_NUMBER: _ClassVar[int]
    MARKET_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    APP_STATE_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    REWARDS_PENDING_PAYOUTS_FIELD_NUMBER: _ClassVar[int]
    GOVERNANCE_NODE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_STATE_FIELD_NUMBER: _ClassVar[int]
    VOTE_SPAM_POLICY_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_SPAM_POLICY_FIELD_NUMBER: _ClassVar[int]
    NOTARY_FIELD_NUMBER: _ClassVar[int]
    EVENT_FORWARDER_FIELD_NUMBER: _ClassVar[int]
    STAKE_VERIFIER_DEPOSITED_FIELD_NUMBER: _ClassVar[int]
    STAKE_VERIFIER_REMOVED_FIELD_NUMBER: _ClassVar[int]
    WITNESS_FIELD_NUMBER: _ClassVar[int]
    DELEGATION_LAST_RECONCILIATION_TIME_FIELD_NUMBER: _ClassVar[int]
    TOPOLOGY_FIELD_NUMBER: _ClassVar[int]
    ORACLE_DATA_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PENDING_PROVISIONS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PARTIES_LIQUIDITY_ORDERS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PARTIES_ORDERS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISIONS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_SUPPLIED_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_TARGET_FIELD_NUMBER: _ClassVar[int]
    FLOATING_POINT_CONSENSUS_FIELD_NUMBER: _ClassVar[int]
    MARKET_TRACKER_FIELD_NUMBER: _ClassVar[int]
    BANKING_RECURRING_TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    BANKING_SCHEDULED_TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    ERC20_MULTISIG_TOPOLOGY_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    ERC20_MULTISIG_TOPOLOGY_PENDING_FIELD_NUMBER: _ClassVar[int]
    PROOF_OF_WORK_FIELD_NUMBER: _ClassVar[int]
    PENDING_ASSET_UPDATES_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_UPGRADE_PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    BANKING_BRIDGE_STATE_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_STATE_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_SCORES_FIELD_NUMBER: _ClassVar[int]
    SPOT_LIQUIDITY_TARGET_FIELD_NUMBER: _ClassVar[int]
    BANKING_RECURRING_GOVERNANCE_TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    BANKING_SCHEDULED_GOVERNANCE_TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    ETH_CONTRACT_CALL_RESULTS_FIELD_NUMBER: _ClassVar[int]
    ETH_ORACLE_VERIFIER_LAST_BLOCK_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_V2_PROVISIONS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_V2_PENDING_PROVISIONS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_V2_PERFORMANCES_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_V2_SUPPLIED_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_V2_SCORES_FIELD_NUMBER: _ClassVar[int]
    HOLDING_ACCOUNT_TRACKER_FIELD_NUMBER: _ClassVar[int]
    TEAMS_FIELD_NUMBER: _ClassVar[int]
    TEAM_SWITCHES_FIELD_NUMBER: _ClassVar[int]
    VESTING_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_PROGRAM_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_STREAK_FIELD_NUMBER: _ClassVar[int]
    VOLUME_DISCOUNT_PROGRAM_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_V2_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_V2_PAID_FEES_STATS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDATION_FIELD_NUMBER: _ClassVar[int]
    BANKING_TRANSFER_FEE_DISCOUNTS_FIELD_NUMBER: _ClassVar[int]
    GOVERNANCE_BATCH_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    L2_ETH_ORACLES_FIELD_NUMBER: _ClassVar[int]
    active_assets: ActiveAssets
    pending_assets: PendingAssets
    banking_withdrawals: BankingWithdrawals
    banking_deposits: BankingDeposits
    banking_seen: BankingSeen
    banking_asset_actions: BankingAssetActions
    checkpoint: Checkpoint
    collateral_accounts: CollateralAccounts
    collateral_assets: CollateralAssets
    delegation_active: DelegationActive
    delegation_pending: DelegationPending
    delegation_auto: DelegationAuto
    governance_active: GovernanceActive
    governance_enacted: GovernanceEnacted
    staking_accounts: StakingAccounts
    matching_book: MatchingBook
    network_parameters: NetParams
    execution_markets: ExecutionMarkets
    market_positions: MarketPositions
    app_state: AppState
    epoch: EpochState
    rewards_pending_payouts: RewardsPendingPayouts
    governance_node: GovernanceNode
    limit_state: LimitState
    vote_spam_policy: VoteSpamPolicy
    simple_spam_policy: SimpleSpamPolicy
    notary: Notary
    event_forwarder: EventForwarder
    stake_verifier_deposited: StakeVerifierDeposited
    stake_verifier_removed: StakeVerifierRemoved
    witness: Witness
    delegation_last_reconciliation_time: DelegationLastReconciliationTime
    topology: Topology
    oracle_data: OracleDataBatch
    liquidity_parameters: LiquidityParameters
    liquidity_pending_provisions: LiquidityPendingProvisions
    liquidity_parties_liquidity_orders: LiquidityPartiesLiquidityOrders
    liquidity_parties_orders: LiquidityPartiesOrders
    liquidity_provisions: LiquidityProvisions
    liquidity_supplied: LiquiditySupplied
    liquidity_target: LiquidityTarget
    floating_point_consensus: FloatingPointConsensus
    market_tracker: MarketTracker
    banking_recurring_transfers: BankingRecurringTransfers
    banking_scheduled_transfers: BankingScheduledTransfers
    erc20_multisig_topology_verified: ERC20MultiSigTopologyVerified
    erc20_multisig_topology_pending: ERC20MultiSigTopologyPending
    proof_of_work: ProofOfWork
    pending_asset_updates: PendingAssetUpdates
    protocol_upgrade_proposals: ProtocolUpgradeProposals
    banking_bridge_state: BankingBridgeState
    settlement_state: SettlementState
    liquidity_scores: LiquidityScores
    spot_liquidity_target: SpotLiquidityTarget
    banking_recurring_governance_transfers: BankingRecurringGovernanceTransfers
    banking_scheduled_governance_transfers: BankingScheduledGovernanceTransfers
    eth_contract_call_results: EthContractCallResults
    eth_oracle_verifier_last_block: EthOracleVerifierLastBlock
    liquidity_v2_provisions: LiquidityV2Provisions
    liquidity_v2_pending_provisions: LiquidityV2PendingProvisions
    liquidity_v2_performances: LiquidityV2Performances
    liquidity_v2_supplied: LiquidityV2Supplied
    liquidity_v2_scores: LiquidityV2Scores
    holding_account_tracker: HoldingAccountTracker
    teams: Teams
    team_switches: TeamSwitches
    vesting: Vesting
    referral_program: ReferralProgramData
    activity_streak: ActivityStreak
    volume_discount_program: VolumeDiscountProgram
    liquidity_v2_parameters: LiquidityV2Parameters
    liquidity_v2_paid_fees_stats: LiquidityV2PaidFeesStats
    liquidation: Liquidation
    banking_transfer_fee_discounts: BankingTransferFeeDiscounts
    governance_batch_active: GovernanceBatchActive
    parties: Parties
    l2_eth_oracles: L2EthOracles
    def __init__(
        self,
        active_assets: _Optional[_Union[ActiveAssets, _Mapping]] = ...,
        pending_assets: _Optional[_Union[PendingAssets, _Mapping]] = ...,
        banking_withdrawals: _Optional[_Union[BankingWithdrawals, _Mapping]] = ...,
        banking_deposits: _Optional[_Union[BankingDeposits, _Mapping]] = ...,
        banking_seen: _Optional[_Union[BankingSeen, _Mapping]] = ...,
        banking_asset_actions: _Optional[_Union[BankingAssetActions, _Mapping]] = ...,
        checkpoint: _Optional[_Union[Checkpoint, _Mapping]] = ...,
        collateral_accounts: _Optional[_Union[CollateralAccounts, _Mapping]] = ...,
        collateral_assets: _Optional[_Union[CollateralAssets, _Mapping]] = ...,
        delegation_active: _Optional[_Union[DelegationActive, _Mapping]] = ...,
        delegation_pending: _Optional[_Union[DelegationPending, _Mapping]] = ...,
        delegation_auto: _Optional[_Union[DelegationAuto, _Mapping]] = ...,
        governance_active: _Optional[_Union[GovernanceActive, _Mapping]] = ...,
        governance_enacted: _Optional[_Union[GovernanceEnacted, _Mapping]] = ...,
        staking_accounts: _Optional[_Union[StakingAccounts, _Mapping]] = ...,
        matching_book: _Optional[_Union[MatchingBook, _Mapping]] = ...,
        network_parameters: _Optional[_Union[NetParams, _Mapping]] = ...,
        execution_markets: _Optional[_Union[ExecutionMarkets, _Mapping]] = ...,
        market_positions: _Optional[_Union[MarketPositions, _Mapping]] = ...,
        app_state: _Optional[_Union[AppState, _Mapping]] = ...,
        epoch: _Optional[_Union[EpochState, _Mapping]] = ...,
        rewards_pending_payouts: _Optional[
            _Union[RewardsPendingPayouts, _Mapping]
        ] = ...,
        governance_node: _Optional[_Union[GovernanceNode, _Mapping]] = ...,
        limit_state: _Optional[_Union[LimitState, _Mapping]] = ...,
        vote_spam_policy: _Optional[_Union[VoteSpamPolicy, _Mapping]] = ...,
        simple_spam_policy: _Optional[_Union[SimpleSpamPolicy, _Mapping]] = ...,
        notary: _Optional[_Union[Notary, _Mapping]] = ...,
        event_forwarder: _Optional[_Union[EventForwarder, _Mapping]] = ...,
        stake_verifier_deposited: _Optional[
            _Union[StakeVerifierDeposited, _Mapping]
        ] = ...,
        stake_verifier_removed: _Optional[_Union[StakeVerifierRemoved, _Mapping]] = ...,
        witness: _Optional[_Union[Witness, _Mapping]] = ...,
        delegation_last_reconciliation_time: _Optional[
            _Union[DelegationLastReconciliationTime, _Mapping]
        ] = ...,
        topology: _Optional[_Union[Topology, _Mapping]] = ...,
        oracle_data: _Optional[_Union[OracleDataBatch, _Mapping]] = ...,
        liquidity_parameters: _Optional[_Union[LiquidityParameters, _Mapping]] = ...,
        liquidity_pending_provisions: _Optional[
            _Union[LiquidityPendingProvisions, _Mapping]
        ] = ...,
        liquidity_parties_liquidity_orders: _Optional[
            _Union[LiquidityPartiesLiquidityOrders, _Mapping]
        ] = ...,
        liquidity_parties_orders: _Optional[
            _Union[LiquidityPartiesOrders, _Mapping]
        ] = ...,
        liquidity_provisions: _Optional[_Union[LiquidityProvisions, _Mapping]] = ...,
        liquidity_supplied: _Optional[_Union[LiquiditySupplied, _Mapping]] = ...,
        liquidity_target: _Optional[_Union[LiquidityTarget, _Mapping]] = ...,
        floating_point_consensus: _Optional[
            _Union[FloatingPointConsensus, _Mapping]
        ] = ...,
        market_tracker: _Optional[_Union[MarketTracker, _Mapping]] = ...,
        banking_recurring_transfers: _Optional[
            _Union[BankingRecurringTransfers, _Mapping]
        ] = ...,
        banking_scheduled_transfers: _Optional[
            _Union[BankingScheduledTransfers, _Mapping]
        ] = ...,
        erc20_multisig_topology_verified: _Optional[
            _Union[ERC20MultiSigTopologyVerified, _Mapping]
        ] = ...,
        erc20_multisig_topology_pending: _Optional[
            _Union[ERC20MultiSigTopologyPending, _Mapping]
        ] = ...,
        proof_of_work: _Optional[_Union[ProofOfWork, _Mapping]] = ...,
        pending_asset_updates: _Optional[_Union[PendingAssetUpdates, _Mapping]] = ...,
        protocol_upgrade_proposals: _Optional[
            _Union[ProtocolUpgradeProposals, _Mapping]
        ] = ...,
        banking_bridge_state: _Optional[_Union[BankingBridgeState, _Mapping]] = ...,
        settlement_state: _Optional[_Union[SettlementState, _Mapping]] = ...,
        liquidity_scores: _Optional[_Union[LiquidityScores, _Mapping]] = ...,
        spot_liquidity_target: _Optional[_Union[SpotLiquidityTarget, _Mapping]] = ...,
        banking_recurring_governance_transfers: _Optional[
            _Union[BankingRecurringGovernanceTransfers, _Mapping]
        ] = ...,
        banking_scheduled_governance_transfers: _Optional[
            _Union[BankingScheduledGovernanceTransfers, _Mapping]
        ] = ...,
        eth_contract_call_results: _Optional[
            _Union[EthContractCallResults, _Mapping]
        ] = ...,
        eth_oracle_verifier_last_block: _Optional[
            _Union[EthOracleVerifierLastBlock, _Mapping]
        ] = ...,
        liquidity_v2_provisions: _Optional[
            _Union[LiquidityV2Provisions, _Mapping]
        ] = ...,
        liquidity_v2_pending_provisions: _Optional[
            _Union[LiquidityV2PendingProvisions, _Mapping]
        ] = ...,
        liquidity_v2_performances: _Optional[
            _Union[LiquidityV2Performances, _Mapping]
        ] = ...,
        liquidity_v2_supplied: _Optional[_Union[LiquidityV2Supplied, _Mapping]] = ...,
        liquidity_v2_scores: _Optional[_Union[LiquidityV2Scores, _Mapping]] = ...,
        holding_account_tracker: _Optional[
            _Union[HoldingAccountTracker, _Mapping]
        ] = ...,
        teams: _Optional[_Union[Teams, _Mapping]] = ...,
        team_switches: _Optional[_Union[TeamSwitches, _Mapping]] = ...,
        vesting: _Optional[_Union[Vesting, _Mapping]] = ...,
        referral_program: _Optional[_Union[ReferralProgramData, _Mapping]] = ...,
        activity_streak: _Optional[_Union[ActivityStreak, _Mapping]] = ...,
        volume_discount_program: _Optional[
            _Union[VolumeDiscountProgram, _Mapping]
        ] = ...,
        liquidity_v2_parameters: _Optional[
            _Union[LiquidityV2Parameters, _Mapping]
        ] = ...,
        liquidity_v2_paid_fees_stats: _Optional[
            _Union[LiquidityV2PaidFeesStats, _Mapping]
        ] = ...,
        liquidation: _Optional[_Union[Liquidation, _Mapping]] = ...,
        banking_transfer_fee_discounts: _Optional[
            _Union[BankingTransferFeeDiscounts, _Mapping]
        ] = ...,
        governance_batch_active: _Optional[
            _Union[GovernanceBatchActive, _Mapping]
        ] = ...,
        parties: _Optional[_Union[Parties, _Mapping]] = ...,
        l2_eth_oracles: _Optional[_Union[L2EthOracles, _Mapping]] = ...,
    ) -> None: ...

class OrderHoldingQuantities(_message.Message):
    __slots__ = ("id", "quantity", "fee")
    ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    FEE_FIELD_NUMBER: _ClassVar[int]
    id: str
    quantity: str
    fee: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        quantity: _Optional[str] = ...,
        fee: _Optional[str] = ...,
    ) -> None: ...

class HoldingAccountTracker(_message.Message):
    __slots__ = ("market_id", "order_holding")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_HOLDING_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    order_holding: _containers.RepeatedCompositeFieldContainer[OrderHoldingQuantities]
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        order_holding: _Optional[
            _Iterable[_Union[OrderHoldingQuantities, _Mapping]]
        ] = ...,
    ) -> None: ...

class TimestampedTotalStake(_message.Message):
    __slots__ = ("total_stake", "time")
    TOTAL_STAKE_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    total_stake: int
    time: int
    def __init__(
        self, total_stake: _Optional[int] = ..., time: _Optional[int] = ...
    ) -> None: ...

class TimestampedOpenInterest(_message.Message):
    __slots__ = ("open_interest", "time")
    OPEN_INTEREST_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    open_interest: int
    time: int
    def __init__(
        self, open_interest: _Optional[int] = ..., time: _Optional[int] = ...
    ) -> None: ...

class LiquidityTarget(_message.Message):
    __slots__ = (
        "market_id",
        "current_time",
        "scheduled_truncate",
        "current_open_interests",
        "previous_open_interests",
        "max_open_interests",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_TIME_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_TRUNCATE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_OPEN_INTERESTS_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_OPEN_INTERESTS_FIELD_NUMBER: _ClassVar[int]
    MAX_OPEN_INTERESTS_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    current_time: int
    scheduled_truncate: int
    current_open_interests: _containers.RepeatedScalarFieldContainer[int]
    previous_open_interests: _containers.RepeatedCompositeFieldContainer[
        TimestampedOpenInterest
    ]
    max_open_interests: TimestampedOpenInterest
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        current_time: _Optional[int] = ...,
        scheduled_truncate: _Optional[int] = ...,
        current_open_interests: _Optional[_Iterable[int]] = ...,
        previous_open_interests: _Optional[
            _Iterable[_Union[TimestampedOpenInterest, _Mapping]]
        ] = ...,
        max_open_interests: _Optional[_Union[TimestampedOpenInterest, _Mapping]] = ...,
    ) -> None: ...

class SpotLiquidityTarget(_message.Message):
    __slots__ = (
        "market_id",
        "current_time",
        "scheduled_truncate",
        "current_total_stake",
        "previous_total_stake",
        "max_total_stake",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_TIME_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_TRUNCATE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_TOTAL_STAKE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_TOTAL_STAKE_FIELD_NUMBER: _ClassVar[int]
    MAX_TOTAL_STAKE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    current_time: int
    scheduled_truncate: int
    current_total_stake: _containers.RepeatedScalarFieldContainer[int]
    previous_total_stake: _containers.RepeatedCompositeFieldContainer[
        TimestampedTotalStake
    ]
    max_total_stake: TimestampedTotalStake
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        current_time: _Optional[int] = ...,
        scheduled_truncate: _Optional[int] = ...,
        current_total_stake: _Optional[_Iterable[int]] = ...,
        previous_total_stake: _Optional[
            _Iterable[_Union[TimestampedTotalStake, _Mapping]]
        ] = ...,
        max_total_stake: _Optional[_Union[TimestampedTotalStake, _Mapping]] = ...,
    ) -> None: ...

class LiquidityOffsetProbabilityPair(_message.Message):
    __slots__ = ("offset", "probability")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    offset: int
    probability: str
    def __init__(
        self, offset: _Optional[int] = ..., probability: _Optional[str] = ...
    ) -> None: ...

class LiquiditySupplied(_message.Message):
    __slots__ = ("market_id", "consensus_reached", "bid_cache", "ask_cache")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    CONSENSUS_REACHED_FIELD_NUMBER: _ClassVar[int]
    BID_CACHE_FIELD_NUMBER: _ClassVar[int]
    ASK_CACHE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    consensus_reached: bool
    bid_cache: _containers.RepeatedCompositeFieldContainer[
        LiquidityOffsetProbabilityPair
    ]
    ask_cache: _containers.RepeatedCompositeFieldContainer[
        LiquidityOffsetProbabilityPair
    ]
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        consensus_reached: bool = ...,
        bid_cache: _Optional[
            _Iterable[_Union[LiquidityOffsetProbabilityPair, _Mapping]]
        ] = ...,
        ask_cache: _Optional[
            _Iterable[_Union[LiquidityOffsetProbabilityPair, _Mapping]]
        ] = ...,
    ) -> None: ...

class OracleDataBatch(_message.Message):
    __slots__ = ("oracle_data",)
    ORACLE_DATA_FIELD_NUMBER: _ClassVar[int]
    oracle_data: _containers.RepeatedCompositeFieldContainer[OracleData]
    def __init__(
        self, oracle_data: _Optional[_Iterable[_Union[OracleData, _Mapping]]] = ...
    ) -> None: ...

class OracleData(_message.Message):
    __slots__ = ("signers", "data", "meta_data")
    SIGNERS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    META_DATA_FIELD_NUMBER: _ClassVar[int]
    signers: _containers.RepeatedCompositeFieldContainer[_data_pb2.Signer]
    data: _containers.RepeatedCompositeFieldContainer[OracleDataPair]
    meta_data: _containers.RepeatedCompositeFieldContainer[_data_pb2.Property]
    def __init__(
        self,
        signers: _Optional[_Iterable[_Union[_data_pb2.Signer, _Mapping]]] = ...,
        data: _Optional[_Iterable[_Union[OracleDataPair, _Mapping]]] = ...,
        meta_data: _Optional[_Iterable[_Union[_data_pb2.Property, _Mapping]]] = ...,
    ) -> None: ...

class OracleDataPair(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(
        self, key: _Optional[str] = ..., value: _Optional[str] = ...
    ) -> None: ...

class Witness(_message.Message):
    __slots__ = ("resources",)
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    resources: _containers.RepeatedCompositeFieldContainer[Resource]
    def __init__(
        self, resources: _Optional[_Iterable[_Union[Resource, _Mapping]]] = ...
    ) -> None: ...

class Resource(_message.Message):
    __slots__ = ("id", "check_until", "votes", "state")
    ID_FIELD_NUMBER: _ClassVar[int]
    CHECK_UNTIL_FIELD_NUMBER: _ClassVar[int]
    VOTES_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    check_until: int
    votes: _containers.RepeatedScalarFieldContainer[str]
    state: int
    def __init__(
        self,
        id: _Optional[str] = ...,
        check_until: _Optional[int] = ...,
        votes: _Optional[_Iterable[str]] = ...,
        state: _Optional[int] = ...,
    ) -> None: ...

class EventForwarderBucket(_message.Message):
    __slots__ = ("ts", "hashes")
    TS_FIELD_NUMBER: _ClassVar[int]
    HASHES_FIELD_NUMBER: _ClassVar[int]
    ts: int
    hashes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self, ts: _Optional[int] = ..., hashes: _Optional[_Iterable[str]] = ...
    ) -> None: ...

class EventForwarder(_message.Message):
    __slots__ = ("acked_events", "buckets")
    ACKED_EVENTS_FIELD_NUMBER: _ClassVar[int]
    BUCKETS_FIELD_NUMBER: _ClassVar[int]
    acked_events: _containers.RepeatedScalarFieldContainer[str]
    buckets: _containers.RepeatedCompositeFieldContainer[EventForwarderBucket]
    def __init__(
        self,
        acked_events: _Optional[_Iterable[str]] = ...,
        buckets: _Optional[_Iterable[_Union[EventForwarderBucket, _Mapping]]] = ...,
    ) -> None: ...

class CollateralAccounts(_message.Message):
    __slots__ = ("accounts", "next_balance_snapshot")
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    NEXT_BALANCE_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    accounts: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Account]
    next_balance_snapshot: int
    def __init__(
        self,
        accounts: _Optional[_Iterable[_Union[_vega_pb2.Account, _Mapping]]] = ...,
        next_balance_snapshot: _Optional[int] = ...,
    ) -> None: ...

class CollateralAssets(_message.Message):
    __slots__ = ("assets",)
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    assets: _containers.RepeatedCompositeFieldContainer[_assets_pb2.Asset]
    def __init__(
        self, assets: _Optional[_Iterable[_Union[_assets_pb2.Asset, _Mapping]]] = ...
    ) -> None: ...

class ActiveAssets(_message.Message):
    __slots__ = ("assets",)
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    assets: _containers.RepeatedCompositeFieldContainer[_assets_pb2.Asset]
    def __init__(
        self, assets: _Optional[_Iterable[_Union[_assets_pb2.Asset, _Mapping]]] = ...
    ) -> None: ...

class PendingAssets(_message.Message):
    __slots__ = ("assets",)
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    assets: _containers.RepeatedCompositeFieldContainer[_assets_pb2.Asset]
    def __init__(
        self, assets: _Optional[_Iterable[_Union[_assets_pb2.Asset, _Mapping]]] = ...
    ) -> None: ...

class PendingAssetUpdates(_message.Message):
    __slots__ = ("assets",)
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    assets: _containers.RepeatedCompositeFieldContainer[_assets_pb2.Asset]
    def __init__(
        self, assets: _Optional[_Iterable[_Union[_assets_pb2.Asset, _Mapping]]] = ...
    ) -> None: ...

class Withdrawal(_message.Message):
    __slots__ = ("ref", "withdrawal")
    REF_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWAL_FIELD_NUMBER: _ClassVar[int]
    ref: str
    withdrawal: _vega_pb2.Withdrawal
    def __init__(
        self,
        ref: _Optional[str] = ...,
        withdrawal: _Optional[_Union[_vega_pb2.Withdrawal, _Mapping]] = ...,
    ) -> None: ...

class Deposit(_message.Message):
    __slots__ = ("id", "deposit")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEPOSIT_FIELD_NUMBER: _ClassVar[int]
    id: str
    deposit: _vega_pb2.Deposit
    def __init__(
        self,
        id: _Optional[str] = ...,
        deposit: _Optional[_Union[_vega_pb2.Deposit, _Mapping]] = ...,
    ) -> None: ...

class TxRef(_message.Message):
    __slots__ = ("asset", "block_nr", "hash", "log_index")
    ASSET_FIELD_NUMBER: _ClassVar[int]
    BLOCK_NR_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    asset: str
    block_nr: int
    hash: str
    log_index: int
    def __init__(
        self,
        asset: _Optional[str] = ...,
        block_nr: _Optional[int] = ...,
        hash: _Optional[str] = ...,
        log_index: _Optional[int] = ...,
    ) -> None: ...

class BankingWithdrawals(_message.Message):
    __slots__ = ("withdrawals",)
    WITHDRAWALS_FIELD_NUMBER: _ClassVar[int]
    withdrawals: _containers.RepeatedCompositeFieldContainer[Withdrawal]
    def __init__(
        self, withdrawals: _Optional[_Iterable[_Union[Withdrawal, _Mapping]]] = ...
    ) -> None: ...

class BankingDeposits(_message.Message):
    __slots__ = ("deposit",)
    DEPOSIT_FIELD_NUMBER: _ClassVar[int]
    deposit: _containers.RepeatedCompositeFieldContainer[Deposit]
    def __init__(
        self, deposit: _Optional[_Iterable[_Union[Deposit, _Mapping]]] = ...
    ) -> None: ...

class BankingSeen(_message.Message):
    __slots__ = ("refs", "last_seen_eth_block")
    REFS_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_ETH_BLOCK_FIELD_NUMBER: _ClassVar[int]
    refs: _containers.RepeatedScalarFieldContainer[str]
    last_seen_eth_block: int
    def __init__(
        self,
        refs: _Optional[_Iterable[str]] = ...,
        last_seen_eth_block: _Optional[int] = ...,
    ) -> None: ...

class BankingAssetActions(_message.Message):
    __slots__ = ("asset_action",)
    ASSET_ACTION_FIELD_NUMBER: _ClassVar[int]
    asset_action: _containers.RepeatedCompositeFieldContainer[
        _checkpoint_pb2.AssetAction
    ]
    def __init__(
        self,
        asset_action: _Optional[
            _Iterable[_Union[_checkpoint_pb2.AssetAction, _Mapping]]
        ] = ...,
    ) -> None: ...

class BankingRecurringTransfers(_message.Message):
    __slots__ = ("recurring_transfers",)
    RECURRING_TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    recurring_transfers: _checkpoint_pb2.RecurringTransfers
    def __init__(
        self,
        recurring_transfers: _Optional[
            _Union[_checkpoint_pb2.RecurringTransfers, _Mapping]
        ] = ...,
    ) -> None: ...

class BankingScheduledTransfers(_message.Message):
    __slots__ = ("transfers_at_time",)
    TRANSFERS_AT_TIME_FIELD_NUMBER: _ClassVar[int]
    transfers_at_time: _containers.RepeatedCompositeFieldContainer[
        _checkpoint_pb2.ScheduledTransferAtTime
    ]
    def __init__(
        self,
        transfers_at_time: _Optional[
            _Iterable[_Union[_checkpoint_pb2.ScheduledTransferAtTime, _Mapping]]
        ] = ...,
    ) -> None: ...

class BankingRecurringGovernanceTransfers(_message.Message):
    __slots__ = ("recurring_transfers",)
    RECURRING_TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    recurring_transfers: _containers.RepeatedCompositeFieldContainer[
        _checkpoint_pb2.GovernanceTransfer
    ]
    def __init__(
        self,
        recurring_transfers: _Optional[
            _Iterable[_Union[_checkpoint_pb2.GovernanceTransfer, _Mapping]]
        ] = ...,
    ) -> None: ...

class BankingScheduledGovernanceTransfers(_message.Message):
    __slots__ = ("transfers_at_time",)
    TRANSFERS_AT_TIME_FIELD_NUMBER: _ClassVar[int]
    transfers_at_time: _containers.RepeatedCompositeFieldContainer[
        _checkpoint_pb2.ScheduledGovernanceTransferAtTime
    ]
    def __init__(
        self,
        transfers_at_time: _Optional[
            _Iterable[
                _Union[_checkpoint_pb2.ScheduledGovernanceTransferAtTime, _Mapping]
            ]
        ] = ...,
    ) -> None: ...

class BankingBridgeState(_message.Message):
    __slots__ = ("bridge_state",)
    BRIDGE_STATE_FIELD_NUMBER: _ClassVar[int]
    bridge_state: _checkpoint_pb2.BridgeState
    def __init__(
        self,
        bridge_state: _Optional[_Union[_checkpoint_pb2.BridgeState, _Mapping]] = ...,
    ) -> None: ...

class Checkpoint(_message.Message):
    __slots__ = ("next_cp",)
    NEXT_CP_FIELD_NUMBER: _ClassVar[int]
    next_cp: int
    def __init__(self, next_cp: _Optional[int] = ...) -> None: ...

class DelegationLastReconciliationTime(_message.Message):
    __slots__ = ("last_reconciliation_time",)
    LAST_RECONCILIATION_TIME_FIELD_NUMBER: _ClassVar[int]
    last_reconciliation_time: int
    def __init__(self, last_reconciliation_time: _Optional[int] = ...) -> None: ...

class DelegationActive(_message.Message):
    __slots__ = ("delegations",)
    DELEGATIONS_FIELD_NUMBER: _ClassVar[int]
    delegations: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Delegation]
    def __init__(
        self,
        delegations: _Optional[_Iterable[_Union[_vega_pb2.Delegation, _Mapping]]] = ...,
    ) -> None: ...

class DelegationPending(_message.Message):
    __slots__ = ("delegations", "undelegation")
    DELEGATIONS_FIELD_NUMBER: _ClassVar[int]
    UNDELEGATION_FIELD_NUMBER: _ClassVar[int]
    delegations: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Delegation]
    undelegation: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Delegation]
    def __init__(
        self,
        delegations: _Optional[_Iterable[_Union[_vega_pb2.Delegation, _Mapping]]] = ...,
        undelegation: _Optional[
            _Iterable[_Union[_vega_pb2.Delegation, _Mapping]]
        ] = ...,
    ) -> None: ...

class DelegationAuto(_message.Message):
    __slots__ = ("parties",)
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    parties: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, parties: _Optional[_Iterable[str]] = ...) -> None: ...

class ProposalData(_message.Message):
    __slots__ = ("proposal", "yes", "no", "invalid")
    PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    YES_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    INVALID_FIELD_NUMBER: _ClassVar[int]
    proposal: _governance_pb2.Proposal
    yes: _containers.RepeatedCompositeFieldContainer[_governance_pb2.Vote]
    no: _containers.RepeatedCompositeFieldContainer[_governance_pb2.Vote]
    invalid: _containers.RepeatedCompositeFieldContainer[_governance_pb2.Vote]
    def __init__(
        self,
        proposal: _Optional[_Union[_governance_pb2.Proposal, _Mapping]] = ...,
        yes: _Optional[_Iterable[_Union[_governance_pb2.Vote, _Mapping]]] = ...,
        no: _Optional[_Iterable[_Union[_governance_pb2.Vote, _Mapping]]] = ...,
        invalid: _Optional[_Iterable[_Union[_governance_pb2.Vote, _Mapping]]] = ...,
    ) -> None: ...

class GovernanceEnacted(_message.Message):
    __slots__ = ("proposals",)
    PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    proposals: _containers.RepeatedCompositeFieldContainer[ProposalData]
    def __init__(
        self, proposals: _Optional[_Iterable[_Union[ProposalData, _Mapping]]] = ...
    ) -> None: ...

class GovernanceActive(_message.Message):
    __slots__ = ("proposals",)
    PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    proposals: _containers.RepeatedCompositeFieldContainer[ProposalData]
    def __init__(
        self, proposals: _Optional[_Iterable[_Union[ProposalData, _Mapping]]] = ...
    ) -> None: ...

class BatchProposalData(_message.Message):
    __slots__ = ("batch_proposal", "proposals")
    BATCH_PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    batch_proposal: ProposalData
    proposals: _containers.RepeatedCompositeFieldContainer[_governance_pb2.Proposal]
    def __init__(
        self,
        batch_proposal: _Optional[_Union[ProposalData, _Mapping]] = ...,
        proposals: _Optional[
            _Iterable[_Union[_governance_pb2.Proposal, _Mapping]]
        ] = ...,
    ) -> None: ...

class GovernanceBatchActive(_message.Message):
    __slots__ = ("batch_proposals",)
    BATCH_PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    batch_proposals: _containers.RepeatedCompositeFieldContainer[BatchProposalData]
    def __init__(
        self,
        batch_proposals: _Optional[
            _Iterable[_Union[BatchProposalData, _Mapping]]
        ] = ...,
    ) -> None: ...

class GovernanceNode(_message.Message):
    __slots__ = ("proposals", "proposal_data")
    PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    PROPOSAL_DATA_FIELD_NUMBER: _ClassVar[int]
    proposals: _containers.RepeatedCompositeFieldContainer[_governance_pb2.Proposal]
    proposal_data: _containers.RepeatedCompositeFieldContainer[ProposalData]
    def __init__(
        self,
        proposals: _Optional[
            _Iterable[_Union[_governance_pb2.Proposal, _Mapping]]
        ] = ...,
        proposal_data: _Optional[_Iterable[_Union[ProposalData, _Mapping]]] = ...,
    ) -> None: ...

class StakingAccount(_message.Message):
    __slots__ = ("party", "balance", "events")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    party: str
    balance: str
    events: _containers.RepeatedCompositeFieldContainer[_events_pb2.StakeLinking]
    def __init__(
        self,
        party: _Optional[str] = ...,
        balance: _Optional[str] = ...,
        events: _Optional[_Iterable[_Union[_events_pb2.StakeLinking, _Mapping]]] = ...,
    ) -> None: ...

class StakingAccounts(_message.Message):
    __slots__ = ("accounts", "staking_asset_total_supply", "pending_stake_total_supply")
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    STAKING_ASSET_TOTAL_SUPPLY_FIELD_NUMBER: _ClassVar[int]
    PENDING_STAKE_TOTAL_SUPPLY_FIELD_NUMBER: _ClassVar[int]
    accounts: _containers.RepeatedCompositeFieldContainer[StakingAccount]
    staking_asset_total_supply: str
    pending_stake_total_supply: _chain_events_pb2.StakeTotalSupply
    def __init__(
        self,
        accounts: _Optional[_Iterable[_Union[StakingAccount, _Mapping]]] = ...,
        staking_asset_total_supply: _Optional[str] = ...,
        pending_stake_total_supply: _Optional[
            _Union[_chain_events_pb2.StakeTotalSupply, _Mapping]
        ] = ...,
    ) -> None: ...

class MatchingBook(_message.Message):
    __slots__ = (
        "market_id",
        "buy",
        "sell",
        "last_traded_price",
        "auction",
        "batch_id",
        "pegged_order_ids",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    BUY_FIELD_NUMBER: _ClassVar[int]
    SELL_FIELD_NUMBER: _ClassVar[int]
    LAST_TRADED_PRICE_FIELD_NUMBER: _ClassVar[int]
    AUCTION_FIELD_NUMBER: _ClassVar[int]
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    PEGGED_ORDER_IDS_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    buy: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Order]
    sell: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Order]
    last_traded_price: str
    auction: bool
    batch_id: int
    pegged_order_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        buy: _Optional[_Iterable[_Union[_vega_pb2.Order, _Mapping]]] = ...,
        sell: _Optional[_Iterable[_Union[_vega_pb2.Order, _Mapping]]] = ...,
        last_traded_price: _Optional[str] = ...,
        auction: bool = ...,
        batch_id: _Optional[int] = ...,
        pegged_order_ids: _Optional[_Iterable[str]] = ...,
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

class DecimalMap(_message.Message):
    __slots__ = ("key", "val")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VAL_FIELD_NUMBER: _ClassVar[int]
    key: int
    val: str
    def __init__(
        self, key: _Optional[int] = ..., val: _Optional[str] = ...
    ) -> None: ...

class TimePrice(_message.Message):
    __slots__ = ("time", "price")
    TIME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    time: int
    price: str
    def __init__(
        self, time: _Optional[int] = ..., price: _Optional[str] = ...
    ) -> None: ...

class PriceVolume(_message.Message):
    __slots__ = ("price", "volume")
    PRICE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    price: str
    volume: int
    def __init__(
        self, price: _Optional[str] = ..., volume: _Optional[int] = ...
    ) -> None: ...

class PriceRange(_message.Message):
    __slots__ = ("min", "max", "ref")
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    min: str
    max: str
    ref: str
    def __init__(
        self,
        min: _Optional[str] = ...,
        max: _Optional[str] = ...,
        ref: _Optional[str] = ...,
    ) -> None: ...

class PriceBound(_message.Message):
    __slots__ = ("active", "up_factor", "down_factor", "trigger")
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    UP_FACTOR_FIELD_NUMBER: _ClassVar[int]
    DOWN_FACTOR_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_FIELD_NUMBER: _ClassVar[int]
    active: bool
    up_factor: str
    down_factor: str
    trigger: _markets_pb2.PriceMonitoringTrigger
    def __init__(
        self,
        active: bool = ...,
        up_factor: _Optional[str] = ...,
        down_factor: _Optional[str] = ...,
        trigger: _Optional[_Union[_markets_pb2.PriceMonitoringTrigger, _Mapping]] = ...,
    ) -> None: ...

class PriceRangeCache(_message.Message):
    __slots__ = ("bound", "range")
    BOUND_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    bound: PriceBound
    range: PriceRange
    def __init__(
        self,
        bound: _Optional[_Union[PriceBound, _Mapping]] = ...,
        range: _Optional[_Union[PriceRange, _Mapping]] = ...,
    ) -> None: ...

class CurrentPrice(_message.Message):
    __slots__ = ("price", "volume")
    PRICE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    price: str
    volume: int
    def __init__(
        self, price: _Optional[str] = ..., volume: _Optional[int] = ...
    ) -> None: ...

class PastPrice(_message.Message):
    __slots__ = ("time", "volume_weighted_price")
    TIME_FIELD_NUMBER: _ClassVar[int]
    VOLUME_WEIGHTED_PRICE_FIELD_NUMBER: _ClassVar[int]
    time: int
    volume_weighted_price: str
    def __init__(
        self, time: _Optional[int] = ..., volume_weighted_price: _Optional[str] = ...
    ) -> None: ...

class PriceMonitor(_message.Message):
    __slots__ = (
        "initialised",
        "fp_horizons",
        "now",
        "update",
        "bounds",
        "price_range_cache_time",
        "price_range_cache",
        "ref_price_cache_time",
        "ref_price_cache",
        "prices_now",
        "prices_past",
        "consensus_reached",
    )
    INITIALISED_FIELD_NUMBER: _ClassVar[int]
    FP_HORIZONS_FIELD_NUMBER: _ClassVar[int]
    NOW_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    BOUNDS_FIELD_NUMBER: _ClassVar[int]
    PRICE_RANGE_CACHE_TIME_FIELD_NUMBER: _ClassVar[int]
    PRICE_RANGE_CACHE_FIELD_NUMBER: _ClassVar[int]
    REF_PRICE_CACHE_TIME_FIELD_NUMBER: _ClassVar[int]
    REF_PRICE_CACHE_FIELD_NUMBER: _ClassVar[int]
    PRICES_NOW_FIELD_NUMBER: _ClassVar[int]
    PRICES_PAST_FIELD_NUMBER: _ClassVar[int]
    CONSENSUS_REACHED_FIELD_NUMBER: _ClassVar[int]
    initialised: bool
    fp_horizons: _containers.RepeatedCompositeFieldContainer[DecimalMap]
    now: int
    update: int
    bounds: _containers.RepeatedCompositeFieldContainer[PriceBound]
    price_range_cache_time: int
    price_range_cache: _containers.RepeatedCompositeFieldContainer[PriceRangeCache]
    ref_price_cache_time: int
    ref_price_cache: _containers.RepeatedCompositeFieldContainer[DecimalMap]
    prices_now: _containers.RepeatedCompositeFieldContainer[CurrentPrice]
    prices_past: _containers.RepeatedCompositeFieldContainer[PastPrice]
    consensus_reached: bool
    def __init__(
        self,
        initialised: bool = ...,
        fp_horizons: _Optional[_Iterable[_Union[DecimalMap, _Mapping]]] = ...,
        now: _Optional[int] = ...,
        update: _Optional[int] = ...,
        bounds: _Optional[_Iterable[_Union[PriceBound, _Mapping]]] = ...,
        price_range_cache_time: _Optional[int] = ...,
        price_range_cache: _Optional[
            _Iterable[_Union[PriceRangeCache, _Mapping]]
        ] = ...,
        ref_price_cache_time: _Optional[int] = ...,
        ref_price_cache: _Optional[_Iterable[_Union[DecimalMap, _Mapping]]] = ...,
        prices_now: _Optional[_Iterable[_Union[CurrentPrice, _Mapping]]] = ...,
        prices_past: _Optional[_Iterable[_Union[PastPrice, _Mapping]]] = ...,
        consensus_reached: bool = ...,
    ) -> None: ...

class AuctionState(_message.Message):
    __slots__ = (
        "mode",
        "default_mode",
        "trigger",
        "begin",
        "end",
        "start",
        "stop",
        "extension",
        "extension_event_sent",
    )
    MODE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_MODE_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_FIELD_NUMBER: _ClassVar[int]
    BEGIN_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_EVENT_SENT_FIELD_NUMBER: _ClassVar[int]
    mode: _markets_pb2.Market.TradingMode
    default_mode: _markets_pb2.Market.TradingMode
    trigger: _vega_pb2.AuctionTrigger
    begin: int
    end: _markets_pb2.AuctionDuration
    start: bool
    stop: bool
    extension: _vega_pb2.AuctionTrigger
    extension_event_sent: bool
    def __init__(
        self,
        mode: _Optional[_Union[_markets_pb2.Market.TradingMode, str]] = ...,
        default_mode: _Optional[_Union[_markets_pb2.Market.TradingMode, str]] = ...,
        trigger: _Optional[_Union[_vega_pb2.AuctionTrigger, str]] = ...,
        begin: _Optional[int] = ...,
        end: _Optional[_Union[_markets_pb2.AuctionDuration, _Mapping]] = ...,
        start: bool = ...,
        stop: bool = ...,
        extension: _Optional[_Union[_vega_pb2.AuctionTrigger, str]] = ...,
        extension_event_sent: bool = ...,
    ) -> None: ...

class EquityShareLP(_message.Message):
    __slots__ = ("id", "stake", "share", "avg", "vshare")
    ID_FIELD_NUMBER: _ClassVar[int]
    STAKE_FIELD_NUMBER: _ClassVar[int]
    SHARE_FIELD_NUMBER: _ClassVar[int]
    AVG_FIELD_NUMBER: _ClassVar[int]
    VSHARE_FIELD_NUMBER: _ClassVar[int]
    id: str
    stake: str
    share: str
    avg: str
    vshare: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        stake: _Optional[str] = ...,
        share: _Optional[str] = ...,
        avg: _Optional[str] = ...,
        vshare: _Optional[str] = ...,
    ) -> None: ...

class EquityShare(_message.Message):
    __slots__ = ("mvp", "opening_auction_ended", "lps", "r", "p_mvp")
    MVP_FIELD_NUMBER: _ClassVar[int]
    OPENING_AUCTION_ENDED_FIELD_NUMBER: _ClassVar[int]
    LPS_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    P_MVP_FIELD_NUMBER: _ClassVar[int]
    mvp: str
    opening_auction_ended: bool
    lps: _containers.RepeatedCompositeFieldContainer[EquityShareLP]
    r: str
    p_mvp: str
    def __init__(
        self,
        mvp: _Optional[str] = ...,
        opening_auction_ended: bool = ...,
        lps: _Optional[_Iterable[_Union[EquityShareLP, _Mapping]]] = ...,
        r: _Optional[str] = ...,
        p_mvp: _Optional[str] = ...,
    ) -> None: ...

class FeeSplitter(_message.Message):
    __slots__ = ("time_window_start", "trade_value", "avg", "window")
    TIME_WINDOW_START_FIELD_NUMBER: _ClassVar[int]
    TRADE_VALUE_FIELD_NUMBER: _ClassVar[int]
    AVG_FIELD_NUMBER: _ClassVar[int]
    WINDOW_FIELD_NUMBER: _ClassVar[int]
    time_window_start: int
    trade_value: str
    avg: str
    window: int
    def __init__(
        self,
        time_window_start: _Optional[int] = ...,
        trade_value: _Optional[str] = ...,
        avg: _Optional[str] = ...,
        window: _Optional[int] = ...,
    ) -> None: ...

class SpotMarket(_message.Message):
    __slots__ = (
        "market",
        "price_monitor",
        "auction_state",
        "pegged_orders",
        "expiring_orders",
        "last_best_bid",
        "last_best_ask",
        "last_mid_bid",
        "last_mid_ask",
        "last_market_value_proxy",
        "last_equity_share_distributed",
        "equity_share",
        "current_mark_price",
        "fee_splitter",
        "next_mark_to_market",
        "last_traded_price",
        "parties",
        "closed",
        "stop_orders",
        "expiring_stop_orders",
        "fees_stats",
    )
    MARKET_FIELD_NUMBER: _ClassVar[int]
    PRICE_MONITOR_FIELD_NUMBER: _ClassVar[int]
    AUCTION_STATE_FIELD_NUMBER: _ClassVar[int]
    PEGGED_ORDERS_FIELD_NUMBER: _ClassVar[int]
    EXPIRING_ORDERS_FIELD_NUMBER: _ClassVar[int]
    LAST_BEST_BID_FIELD_NUMBER: _ClassVar[int]
    LAST_BEST_ASK_FIELD_NUMBER: _ClassVar[int]
    LAST_MID_BID_FIELD_NUMBER: _ClassVar[int]
    LAST_MID_ASK_FIELD_NUMBER: _ClassVar[int]
    LAST_MARKET_VALUE_PROXY_FIELD_NUMBER: _ClassVar[int]
    LAST_EQUITY_SHARE_DISTRIBUTED_FIELD_NUMBER: _ClassVar[int]
    EQUITY_SHARE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_MARK_PRICE_FIELD_NUMBER: _ClassVar[int]
    FEE_SPLITTER_FIELD_NUMBER: _ClassVar[int]
    NEXT_MARK_TO_MARKET_FIELD_NUMBER: _ClassVar[int]
    LAST_TRADED_PRICE_FIELD_NUMBER: _ClassVar[int]
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    CLOSED_FIELD_NUMBER: _ClassVar[int]
    STOP_ORDERS_FIELD_NUMBER: _ClassVar[int]
    EXPIRING_STOP_ORDERS_FIELD_NUMBER: _ClassVar[int]
    FEES_STATS_FIELD_NUMBER: _ClassVar[int]
    market: _markets_pb2.Market
    price_monitor: PriceMonitor
    auction_state: AuctionState
    pegged_orders: PeggedOrders
    expiring_orders: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Order]
    last_best_bid: str
    last_best_ask: str
    last_mid_bid: str
    last_mid_ask: str
    last_market_value_proxy: str
    last_equity_share_distributed: int
    equity_share: EquityShare
    current_mark_price: str
    fee_splitter: FeeSplitter
    next_mark_to_market: int
    last_traded_price: str
    parties: _containers.RepeatedScalarFieldContainer[str]
    closed: bool
    stop_orders: StopOrders
    expiring_stop_orders: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Order]
    fees_stats: _events_pb2.FeesStats
    def __init__(
        self,
        market: _Optional[_Union[_markets_pb2.Market, _Mapping]] = ...,
        price_monitor: _Optional[_Union[PriceMonitor, _Mapping]] = ...,
        auction_state: _Optional[_Union[AuctionState, _Mapping]] = ...,
        pegged_orders: _Optional[_Union[PeggedOrders, _Mapping]] = ...,
        expiring_orders: _Optional[_Iterable[_Union[_vega_pb2.Order, _Mapping]]] = ...,
        last_best_bid: _Optional[str] = ...,
        last_best_ask: _Optional[str] = ...,
        last_mid_bid: _Optional[str] = ...,
        last_mid_ask: _Optional[str] = ...,
        last_market_value_proxy: _Optional[str] = ...,
        last_equity_share_distributed: _Optional[int] = ...,
        equity_share: _Optional[_Union[EquityShare, _Mapping]] = ...,
        current_mark_price: _Optional[str] = ...,
        fee_splitter: _Optional[_Union[FeeSplitter, _Mapping]] = ...,
        next_mark_to_market: _Optional[int] = ...,
        last_traded_price: _Optional[str] = ...,
        parties: _Optional[_Iterable[str]] = ...,
        closed: bool = ...,
        stop_orders: _Optional[_Union[StopOrders, _Mapping]] = ...,
        expiring_stop_orders: _Optional[
            _Iterable[_Union[_vega_pb2.Order, _Mapping]]
        ] = ...,
        fees_stats: _Optional[_Union[_events_pb2.FeesStats, _Mapping]] = ...,
    ) -> None: ...

class Market(_message.Message):
    __slots__ = (
        "market",
        "price_monitor",
        "auction_state",
        "pegged_orders",
        "expiring_orders",
        "last_best_bid",
        "last_best_ask",
        "last_mid_bid",
        "last_mid_ask",
        "last_market_value_proxy",
        "last_equity_share_distributed",
        "equity_share",
        "current_mark_price",
        "risk_factor_short",
        "risk_factor_long",
        "risk_factor_consensus_reached",
        "fee_splitter",
        "settlement_data",
        "next_mark_to_market",
        "last_traded_price",
        "parties",
        "closed",
        "succeeded",
        "stop_orders",
        "expiring_stop_orders",
        "product",
        "fees_stats",
        "party_margin_factor",
        "mark_price_calculator",
        "internal_composite_price_calculator",
        "next_internal_composite_price_calc",
    )
    MARKET_FIELD_NUMBER: _ClassVar[int]
    PRICE_MONITOR_FIELD_NUMBER: _ClassVar[int]
    AUCTION_STATE_FIELD_NUMBER: _ClassVar[int]
    PEGGED_ORDERS_FIELD_NUMBER: _ClassVar[int]
    EXPIRING_ORDERS_FIELD_NUMBER: _ClassVar[int]
    LAST_BEST_BID_FIELD_NUMBER: _ClassVar[int]
    LAST_BEST_ASK_FIELD_NUMBER: _ClassVar[int]
    LAST_MID_BID_FIELD_NUMBER: _ClassVar[int]
    LAST_MID_ASK_FIELD_NUMBER: _ClassVar[int]
    LAST_MARKET_VALUE_PROXY_FIELD_NUMBER: _ClassVar[int]
    LAST_EQUITY_SHARE_DISTRIBUTED_FIELD_NUMBER: _ClassVar[int]
    EQUITY_SHARE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_MARK_PRICE_FIELD_NUMBER: _ClassVar[int]
    RISK_FACTOR_SHORT_FIELD_NUMBER: _ClassVar[int]
    RISK_FACTOR_LONG_FIELD_NUMBER: _ClassVar[int]
    RISK_FACTOR_CONSENSUS_REACHED_FIELD_NUMBER: _ClassVar[int]
    FEE_SPLITTER_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_DATA_FIELD_NUMBER: _ClassVar[int]
    NEXT_MARK_TO_MARKET_FIELD_NUMBER: _ClassVar[int]
    LAST_TRADED_PRICE_FIELD_NUMBER: _ClassVar[int]
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    CLOSED_FIELD_NUMBER: _ClassVar[int]
    SUCCEEDED_FIELD_NUMBER: _ClassVar[int]
    STOP_ORDERS_FIELD_NUMBER: _ClassVar[int]
    EXPIRING_STOP_ORDERS_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    FEES_STATS_FIELD_NUMBER: _ClassVar[int]
    PARTY_MARGIN_FACTOR_FIELD_NUMBER: _ClassVar[int]
    MARK_PRICE_CALCULATOR_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_COMPOSITE_PRICE_CALCULATOR_FIELD_NUMBER: _ClassVar[int]
    NEXT_INTERNAL_COMPOSITE_PRICE_CALC_FIELD_NUMBER: _ClassVar[int]
    market: _markets_pb2.Market
    price_monitor: PriceMonitor
    auction_state: AuctionState
    pegged_orders: PeggedOrders
    expiring_orders: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Order]
    last_best_bid: str
    last_best_ask: str
    last_mid_bid: str
    last_mid_ask: str
    last_market_value_proxy: str
    last_equity_share_distributed: int
    equity_share: EquityShare
    current_mark_price: str
    risk_factor_short: str
    risk_factor_long: str
    risk_factor_consensus_reached: bool
    fee_splitter: FeeSplitter
    settlement_data: str
    next_mark_to_market: int
    last_traded_price: str
    parties: _containers.RepeatedScalarFieldContainer[str]
    closed: bool
    succeeded: bool
    stop_orders: StopOrders
    expiring_stop_orders: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Order]
    product: Product
    fees_stats: _events_pb2.FeesStats
    party_margin_factor: _containers.RepeatedCompositeFieldContainer[PartyMarginFactor]
    mark_price_calculator: CompositePriceCalculator
    internal_composite_price_calculator: CompositePriceCalculator
    next_internal_composite_price_calc: int
    def __init__(
        self,
        market: _Optional[_Union[_markets_pb2.Market, _Mapping]] = ...,
        price_monitor: _Optional[_Union[PriceMonitor, _Mapping]] = ...,
        auction_state: _Optional[_Union[AuctionState, _Mapping]] = ...,
        pegged_orders: _Optional[_Union[PeggedOrders, _Mapping]] = ...,
        expiring_orders: _Optional[_Iterable[_Union[_vega_pb2.Order, _Mapping]]] = ...,
        last_best_bid: _Optional[str] = ...,
        last_best_ask: _Optional[str] = ...,
        last_mid_bid: _Optional[str] = ...,
        last_mid_ask: _Optional[str] = ...,
        last_market_value_proxy: _Optional[str] = ...,
        last_equity_share_distributed: _Optional[int] = ...,
        equity_share: _Optional[_Union[EquityShare, _Mapping]] = ...,
        current_mark_price: _Optional[str] = ...,
        risk_factor_short: _Optional[str] = ...,
        risk_factor_long: _Optional[str] = ...,
        risk_factor_consensus_reached: bool = ...,
        fee_splitter: _Optional[_Union[FeeSplitter, _Mapping]] = ...,
        settlement_data: _Optional[str] = ...,
        next_mark_to_market: _Optional[int] = ...,
        last_traded_price: _Optional[str] = ...,
        parties: _Optional[_Iterable[str]] = ...,
        closed: bool = ...,
        succeeded: bool = ...,
        stop_orders: _Optional[_Union[StopOrders, _Mapping]] = ...,
        expiring_stop_orders: _Optional[
            _Iterable[_Union[_vega_pb2.Order, _Mapping]]
        ] = ...,
        product: _Optional[_Union[Product, _Mapping]] = ...,
        fees_stats: _Optional[_Union[_events_pb2.FeesStats, _Mapping]] = ...,
        party_margin_factor: _Optional[
            _Iterable[_Union[PartyMarginFactor, _Mapping]]
        ] = ...,
        mark_price_calculator: _Optional[
            _Union[CompositePriceCalculator, _Mapping]
        ] = ...,
        internal_composite_price_calculator: _Optional[
            _Union[CompositePriceCalculator, _Mapping]
        ] = ...,
        next_internal_composite_price_calc: _Optional[int] = ...,
    ) -> None: ...

class PartyMarginFactor(_message.Message):
    __slots__ = ("party", "margin_factor")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    MARGIN_FACTOR_FIELD_NUMBER: _ClassVar[int]
    party: str
    margin_factor: str
    def __init__(
        self, party: _Optional[str] = ..., margin_factor: _Optional[str] = ...
    ) -> None: ...

class Product(_message.Message):
    __slots__ = ("perps",)
    PERPS_FIELD_NUMBER: _ClassVar[int]
    perps: Perps
    def __init__(self, perps: _Optional[_Union[Perps, _Mapping]] = ...) -> None: ...

class DataPoint(_message.Message):
    __slots__ = ("price", "timestamp")
    PRICE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    price: str
    timestamp: int
    def __init__(
        self, price: _Optional[str] = ..., timestamp: _Optional[int] = ...
    ) -> None: ...

class AuctionIntervals(_message.Message):
    __slots__ = ("t", "auction_start", "total")
    T_FIELD_NUMBER: _ClassVar[int]
    AUCTION_START_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    t: _containers.RepeatedScalarFieldContainer[int]
    auction_start: int
    total: int
    def __init__(
        self,
        t: _Optional[_Iterable[int]] = ...,
        auction_start: _Optional[int] = ...,
        total: _Optional[int] = ...,
    ) -> None: ...

class TWAPData(_message.Message):
    __slots__ = ("start", "end", "sum_product")
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    SUM_PRODUCT_FIELD_NUMBER: _ClassVar[int]
    start: int
    end: int
    sum_product: str
    def __init__(
        self,
        start: _Optional[int] = ...,
        end: _Optional[int] = ...,
        sum_product: _Optional[str] = ...,
    ) -> None: ...

class Perps(_message.Message):
    __slots__ = (
        "id",
        "external_data_point",
        "internal_data_point",
        "seq",
        "started_at",
        "external_twap_data",
        "internal_twap_data",
        "auction_intervals",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_DATA_POINT_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_DATA_POINT_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_TWAP_DATA_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_TWAP_DATA_FIELD_NUMBER: _ClassVar[int]
    AUCTION_INTERVALS_FIELD_NUMBER: _ClassVar[int]
    id: str
    external_data_point: _containers.RepeatedCompositeFieldContainer[DataPoint]
    internal_data_point: _containers.RepeatedCompositeFieldContainer[DataPoint]
    seq: int
    started_at: int
    external_twap_data: TWAPData
    internal_twap_data: TWAPData
    auction_intervals: AuctionIntervals
    def __init__(
        self,
        id: _Optional[str] = ...,
        external_data_point: _Optional[_Iterable[_Union[DataPoint, _Mapping]]] = ...,
        internal_data_point: _Optional[_Iterable[_Union[DataPoint, _Mapping]]] = ...,
        seq: _Optional[int] = ...,
        started_at: _Optional[int] = ...,
        external_twap_data: _Optional[_Union[TWAPData, _Mapping]] = ...,
        internal_twap_data: _Optional[_Union[TWAPData, _Mapping]] = ...,
        auction_intervals: _Optional[_Union[AuctionIntervals, _Mapping]] = ...,
    ) -> None: ...

class OrdersAtPrice(_message.Message):
    __slots__ = ("price", "orders")
    PRICE_FIELD_NUMBER: _ClassVar[int]
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    price: str
    orders: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self, price: _Optional[str] = ..., orders: _Optional[_Iterable[str]] = ...
    ) -> None: ...

class PricedStopOrders(_message.Message):
    __slots__ = ("falls_bellow", "rises_above")
    FALLS_BELLOW_FIELD_NUMBER: _ClassVar[int]
    RISES_ABOVE_FIELD_NUMBER: _ClassVar[int]
    falls_bellow: _containers.RepeatedCompositeFieldContainer[OrdersAtPrice]
    rises_above: _containers.RepeatedCompositeFieldContainer[OrdersAtPrice]
    def __init__(
        self,
        falls_bellow: _Optional[_Iterable[_Union[OrdersAtPrice, _Mapping]]] = ...,
        rises_above: _Optional[_Iterable[_Union[OrdersAtPrice, _Mapping]]] = ...,
    ) -> None: ...

class TrailingStopOrders(_message.Message):
    __slots__ = ("last_seen_price", "falls_bellow", "rises_above")
    LAST_SEEN_PRICE_FIELD_NUMBER: _ClassVar[int]
    FALLS_BELLOW_FIELD_NUMBER: _ClassVar[int]
    RISES_ABOVE_FIELD_NUMBER: _ClassVar[int]
    last_seen_price: str
    falls_bellow: _containers.RepeatedCompositeFieldContainer[OffsetsAtPrice]
    rises_above: _containers.RepeatedCompositeFieldContainer[OffsetsAtPrice]
    def __init__(
        self,
        last_seen_price: _Optional[str] = ...,
        falls_bellow: _Optional[_Iterable[_Union[OffsetsAtPrice, _Mapping]]] = ...,
        rises_above: _Optional[_Iterable[_Union[OffsetsAtPrice, _Mapping]]] = ...,
    ) -> None: ...

class OrdersAtOffset(_message.Message):
    __slots__ = ("offset", "orders")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    offset: str
    orders: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self, offset: _Optional[str] = ..., orders: _Optional[_Iterable[str]] = ...
    ) -> None: ...

class OffsetsAtPrice(_message.Message):
    __slots__ = ("price", "offsets")
    PRICE_FIELD_NUMBER: _ClassVar[int]
    OFFSETS_FIELD_NUMBER: _ClassVar[int]
    price: str
    offsets: _containers.RepeatedCompositeFieldContainer[OrdersAtOffset]
    def __init__(
        self,
        price: _Optional[str] = ...,
        offsets: _Optional[_Iterable[_Union[OrdersAtOffset, _Mapping]]] = ...,
    ) -> None: ...

class StopOrders(_message.Message):
    __slots__ = ("stop_orders", "priced_stop_orders", "trailing_stop_orders")
    STOP_ORDERS_FIELD_NUMBER: _ClassVar[int]
    PRICED_STOP_ORDERS_FIELD_NUMBER: _ClassVar[int]
    TRAILING_STOP_ORDERS_FIELD_NUMBER: _ClassVar[int]
    stop_orders: _containers.RepeatedCompositeFieldContainer[_events_pb2.StopOrderEvent]
    priced_stop_orders: PricedStopOrders
    trailing_stop_orders: TrailingStopOrders
    def __init__(
        self,
        stop_orders: _Optional[
            _Iterable[_Union[_events_pb2.StopOrderEvent, _Mapping]]
        ] = ...,
        priced_stop_orders: _Optional[_Union[PricedStopOrders, _Mapping]] = ...,
        trailing_stop_orders: _Optional[_Union[TrailingStopOrders, _Mapping]] = ...,
    ) -> None: ...

class PeggedOrders(_message.Message):
    __slots__ = ("parked_orders",)
    PARKED_ORDERS_FIELD_NUMBER: _ClassVar[int]
    parked_orders: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Order]
    def __init__(
        self,
        parked_orders: _Optional[_Iterable[_Union[_vega_pb2.Order, _Mapping]]] = ...,
    ) -> None: ...

class SLANetworkParams(_message.Message):
    __slots__ = (
        "bond_penalty_factor",
        "early_exit_penalty",
        "max_liquidity_fee",
        "non_performance_bond_penalty_max",
        "non_performance_bond_penalty_slope",
        "stake_to_ccy_volume",
        "providers_fee_calculation_time_step",
    )
    BOND_PENALTY_FACTOR_FIELD_NUMBER: _ClassVar[int]
    EARLY_EXIT_PENALTY_FIELD_NUMBER: _ClassVar[int]
    MAX_LIQUIDITY_FEE_FIELD_NUMBER: _ClassVar[int]
    NON_PERFORMANCE_BOND_PENALTY_MAX_FIELD_NUMBER: _ClassVar[int]
    NON_PERFORMANCE_BOND_PENALTY_SLOPE_FIELD_NUMBER: _ClassVar[int]
    STAKE_TO_CCY_VOLUME_FIELD_NUMBER: _ClassVar[int]
    PROVIDERS_FEE_CALCULATION_TIME_STEP_FIELD_NUMBER: _ClassVar[int]
    bond_penalty_factor: str
    early_exit_penalty: str
    max_liquidity_fee: str
    non_performance_bond_penalty_max: str
    non_performance_bond_penalty_slope: str
    stake_to_ccy_volume: str
    providers_fee_calculation_time_step: int
    def __init__(
        self,
        bond_penalty_factor: _Optional[str] = ...,
        early_exit_penalty: _Optional[str] = ...,
        max_liquidity_fee: _Optional[str] = ...,
        non_performance_bond_penalty_max: _Optional[str] = ...,
        non_performance_bond_penalty_slope: _Optional[str] = ...,
        stake_to_ccy_volume: _Optional[str] = ...,
        providers_fee_calculation_time_step: _Optional[int] = ...,
    ) -> None: ...

class ExecutionMarkets(_message.Message):
    __slots__ = (
        "markets",
        "spot_markets",
        "settled_markets",
        "successors",
        "market_ids",
        "sla_network_params",
    )
    MARKETS_FIELD_NUMBER: _ClassVar[int]
    SPOT_MARKETS_FIELD_NUMBER: _ClassVar[int]
    SETTLED_MARKETS_FIELD_NUMBER: _ClassVar[int]
    SUCCESSORS_FIELD_NUMBER: _ClassVar[int]
    MARKET_IDS_FIELD_NUMBER: _ClassVar[int]
    SLA_NETWORK_PARAMS_FIELD_NUMBER: _ClassVar[int]
    markets: _containers.RepeatedCompositeFieldContainer[Market]
    spot_markets: _containers.RepeatedCompositeFieldContainer[SpotMarket]
    settled_markets: _containers.RepeatedCompositeFieldContainer[
        _checkpoint_pb2.MarketState
    ]
    successors: _containers.RepeatedCompositeFieldContainer[Successors]
    market_ids: _containers.RepeatedScalarFieldContainer[str]
    sla_network_params: SLANetworkParams
    def __init__(
        self,
        markets: _Optional[_Iterable[_Union[Market, _Mapping]]] = ...,
        spot_markets: _Optional[_Iterable[_Union[SpotMarket, _Mapping]]] = ...,
        settled_markets: _Optional[
            _Iterable[_Union[_checkpoint_pb2.MarketState, _Mapping]]
        ] = ...,
        successors: _Optional[_Iterable[_Union[Successors, _Mapping]]] = ...,
        market_ids: _Optional[_Iterable[str]] = ...,
        sla_network_params: _Optional[_Union[SLANetworkParams, _Mapping]] = ...,
    ) -> None: ...

class Successors(_message.Message):
    __slots__ = ("parent_market", "successor_markets")
    PARENT_MARKET_FIELD_NUMBER: _ClassVar[int]
    SUCCESSOR_MARKETS_FIELD_NUMBER: _ClassVar[int]
    parent_market: str
    successor_markets: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        parent_market: _Optional[str] = ...,
        successor_markets: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class Position(_message.Message):
    __slots__ = (
        "party_id",
        "size",
        "buy",
        "sell",
        "price",
        "buy_sum_product",
        "sell_sum_product",
        "distressed",
        "average_entry_price",
    )
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    BUY_FIELD_NUMBER: _ClassVar[int]
    SELL_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    BUY_SUM_PRODUCT_FIELD_NUMBER: _ClassVar[int]
    SELL_SUM_PRODUCT_FIELD_NUMBER: _ClassVar[int]
    DISTRESSED_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_ENTRY_PRICE_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    size: int
    buy: int
    sell: int
    price: str
    buy_sum_product: str
    sell_sum_product: str
    distressed: bool
    average_entry_price: bytes
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        size: _Optional[int] = ...,
        buy: _Optional[int] = ...,
        sell: _Optional[int] = ...,
        price: _Optional[str] = ...,
        buy_sum_product: _Optional[str] = ...,
        sell_sum_product: _Optional[str] = ...,
        distressed: bool = ...,
        average_entry_price: _Optional[bytes] = ...,
    ) -> None: ...

class MarketPositions(_message.Message):
    __slots__ = ("market_id", "positions", "parties_records")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    PARTIES_RECORDS_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    positions: _containers.RepeatedCompositeFieldContainer[Position]
    parties_records: _containers.RepeatedCompositeFieldContainer[PartyPositionStats]
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        positions: _Optional[_Iterable[_Union[Position, _Mapping]]] = ...,
        parties_records: _Optional[
            _Iterable[_Union[PartyPositionStats, _Mapping]]
        ] = ...,
    ) -> None: ...

class PartyPositionStats(_message.Message):
    __slots__ = (
        "party",
        "latest_open_interest",
        "lowest_open_interest",
        "traded_volume",
    )
    PARTY_FIELD_NUMBER: _ClassVar[int]
    LATEST_OPEN_INTEREST_FIELD_NUMBER: _ClassVar[int]
    LOWEST_OPEN_INTEREST_FIELD_NUMBER: _ClassVar[int]
    TRADED_VOLUME_FIELD_NUMBER: _ClassVar[int]
    party: str
    latest_open_interest: int
    lowest_open_interest: int
    traded_volume: int
    def __init__(
        self,
        party: _Optional[str] = ...,
        latest_open_interest: _Optional[int] = ...,
        lowest_open_interest: _Optional[int] = ...,
        traded_volume: _Optional[int] = ...,
    ) -> None: ...

class SettlementState(_message.Message):
    __slots__ = ("market_id", "last_mark_price", "last_settled_positions", "trades")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_MARK_PRICE_FIELD_NUMBER: _ClassVar[int]
    LAST_SETTLED_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    TRADES_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    last_mark_price: str
    last_settled_positions: _containers.RepeatedCompositeFieldContainer[
        LastSettledPosition
    ]
    trades: _containers.RepeatedCompositeFieldContainer[SettlementTrade]
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        last_mark_price: _Optional[str] = ...,
        last_settled_positions: _Optional[
            _Iterable[_Union[LastSettledPosition, _Mapping]]
        ] = ...,
        trades: _Optional[_Iterable[_Union[SettlementTrade, _Mapping]]] = ...,
    ) -> None: ...

class LastSettledPosition(_message.Message):
    __slots__ = ("party", "settled_position")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    SETTLED_POSITION_FIELD_NUMBER: _ClassVar[int]
    party: str
    settled_position: int
    def __init__(
        self, party: _Optional[str] = ..., settled_position: _Optional[int] = ...
    ) -> None: ...

class SettlementTrade(_message.Message):
    __slots__ = ("party_id", "price", "market_price", "size", "new_size")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    MARKET_PRICE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    NEW_SIZE_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    price: str
    market_price: str
    size: int
    new_size: int
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        price: _Optional[str] = ...,
        market_price: _Optional[str] = ...,
        size: _Optional[int] = ...,
        new_size: _Optional[int] = ...,
    ) -> None: ...

class AppState(_message.Message):
    __slots__ = (
        "height",
        "block",
        "time",
        "chain_id",
        "protocol_version",
        "protocol_upgrade",
    )
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_UPGRADE_FIELD_NUMBER: _ClassVar[int]
    height: int
    block: str
    time: int
    chain_id: str
    protocol_version: str
    protocol_upgrade: bool
    def __init__(
        self,
        height: _Optional[int] = ...,
        block: _Optional[str] = ...,
        time: _Optional[int] = ...,
        chain_id: _Optional[str] = ...,
        protocol_version: _Optional[str] = ...,
        protocol_upgrade: bool = ...,
    ) -> None: ...

class EpochState(_message.Message):
    __slots__ = (
        "seq",
        "start_time",
        "expire_time",
        "ready_to_start_new_epoch",
        "ready_to_end_epoch",
    )
    SEQ_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_TIME_FIELD_NUMBER: _ClassVar[int]
    READY_TO_START_NEW_EPOCH_FIELD_NUMBER: _ClassVar[int]
    READY_TO_END_EPOCH_FIELD_NUMBER: _ClassVar[int]
    seq: int
    start_time: int
    expire_time: int
    ready_to_start_new_epoch: bool
    ready_to_end_epoch: bool
    def __init__(
        self,
        seq: _Optional[int] = ...,
        start_time: _Optional[int] = ...,
        expire_time: _Optional[int] = ...,
        ready_to_start_new_epoch: bool = ...,
        ready_to_end_epoch: bool = ...,
    ) -> None: ...

class RewardsPendingPayouts(_message.Message):
    __slots__ = ("scheduled_rewards_payout",)
    SCHEDULED_REWARDS_PAYOUT_FIELD_NUMBER: _ClassVar[int]
    scheduled_rewards_payout: _containers.RepeatedCompositeFieldContainer[
        ScheduledRewardsPayout
    ]
    def __init__(
        self,
        scheduled_rewards_payout: _Optional[
            _Iterable[_Union[ScheduledRewardsPayout, _Mapping]]
        ] = ...,
    ) -> None: ...

class ScheduledRewardsPayout(_message.Message):
    __slots__ = ("payout_time", "rewards_payout")
    PAYOUT_TIME_FIELD_NUMBER: _ClassVar[int]
    REWARDS_PAYOUT_FIELD_NUMBER: _ClassVar[int]
    payout_time: int
    rewards_payout: _containers.RepeatedCompositeFieldContainer[RewardsPayout]
    def __init__(
        self,
        payout_time: _Optional[int] = ...,
        rewards_payout: _Optional[_Iterable[_Union[RewardsPayout, _Mapping]]] = ...,
    ) -> None: ...

class RewardsPayout(_message.Message):
    __slots__ = (
        "from_account",
        "asset",
        "reward_party_amount",
        "total_reward",
        "epoch_seq",
        "timestamp",
    )
    FROM_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    REWARD_PARTY_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REWARD_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    from_account: str
    asset: str
    reward_party_amount: _containers.RepeatedCompositeFieldContainer[RewardsPartyAmount]
    total_reward: str
    epoch_seq: str
    timestamp: int
    def __init__(
        self,
        from_account: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        reward_party_amount: _Optional[
            _Iterable[_Union[RewardsPartyAmount, _Mapping]]
        ] = ...,
        total_reward: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
    ) -> None: ...

class RewardsPartyAmount(_message.Message):
    __slots__ = ("party", "amount")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    party: str
    amount: str
    def __init__(
        self, party: _Optional[str] = ..., amount: _Optional[str] = ...
    ) -> None: ...

class LimitState(_message.Message):
    __slots__ = (
        "block_count",
        "can_propose_market",
        "can_propose_asset",
        "genesis_loaded",
        "propose_market_enabled",
        "propose_asset_enabled",
        "propose_market_enabled_from",
        "propose_asset_enabled_from",
        "propose_spot_market_enabled",
        "propose_perps_market_enabled",
    )
    BLOCK_COUNT_FIELD_NUMBER: _ClassVar[int]
    CAN_PROPOSE_MARKET_FIELD_NUMBER: _ClassVar[int]
    CAN_PROPOSE_ASSET_FIELD_NUMBER: _ClassVar[int]
    GENESIS_LOADED_FIELD_NUMBER: _ClassVar[int]
    PROPOSE_MARKET_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROPOSE_ASSET_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROPOSE_MARKET_ENABLED_FROM_FIELD_NUMBER: _ClassVar[int]
    PROPOSE_ASSET_ENABLED_FROM_FIELD_NUMBER: _ClassVar[int]
    PROPOSE_SPOT_MARKET_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROPOSE_PERPS_MARKET_ENABLED_FIELD_NUMBER: _ClassVar[int]
    block_count: int
    can_propose_market: bool
    can_propose_asset: bool
    genesis_loaded: bool
    propose_market_enabled: bool
    propose_asset_enabled: bool
    propose_market_enabled_from: int
    propose_asset_enabled_from: int
    propose_spot_market_enabled: bool
    propose_perps_market_enabled: bool
    def __init__(
        self,
        block_count: _Optional[int] = ...,
        can_propose_market: bool = ...,
        can_propose_asset: bool = ...,
        genesis_loaded: bool = ...,
        propose_market_enabled: bool = ...,
        propose_asset_enabled: bool = ...,
        propose_market_enabled_from: _Optional[int] = ...,
        propose_asset_enabled_from: _Optional[int] = ...,
        propose_spot_market_enabled: bool = ...,
        propose_perps_market_enabled: bool = ...,
    ) -> None: ...

class VoteSpamPolicy(_message.Message):
    __slots__ = (
        "party_to_vote",
        "banned_parties",
        "token_balance",
        "recent_blocks_reject_stats",
        "current_block_index",
        "last_increase_block",
        "current_epoch_seq",
        "min_voting_tokens_factor",
    )
    PARTY_TO_VOTE_FIELD_NUMBER: _ClassVar[int]
    BANNED_PARTIES_FIELD_NUMBER: _ClassVar[int]
    TOKEN_BALANCE_FIELD_NUMBER: _ClassVar[int]
    RECENT_BLOCKS_REJECT_STATS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_BLOCK_INDEX_FIELD_NUMBER: _ClassVar[int]
    LAST_INCREASE_BLOCK_FIELD_NUMBER: _ClassVar[int]
    CURRENT_EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    MIN_VOTING_TOKENS_FACTOR_FIELD_NUMBER: _ClassVar[int]
    party_to_vote: _containers.RepeatedCompositeFieldContainer[PartyProposalVoteCount]
    banned_parties: _containers.RepeatedCompositeFieldContainer[BannedParty]
    token_balance: _containers.RepeatedCompositeFieldContainer[PartyTokenBalance]
    recent_blocks_reject_stats: _containers.RepeatedCompositeFieldContainer[
        BlockRejectStats
    ]
    current_block_index: int
    last_increase_block: int
    current_epoch_seq: int
    min_voting_tokens_factor: str
    def __init__(
        self,
        party_to_vote: _Optional[
            _Iterable[_Union[PartyProposalVoteCount, _Mapping]]
        ] = ...,
        banned_parties: _Optional[_Iterable[_Union[BannedParty, _Mapping]]] = ...,
        token_balance: _Optional[_Iterable[_Union[PartyTokenBalance, _Mapping]]] = ...,
        recent_blocks_reject_stats: _Optional[
            _Iterable[_Union[BlockRejectStats, _Mapping]]
        ] = ...,
        current_block_index: _Optional[int] = ...,
        last_increase_block: _Optional[int] = ...,
        current_epoch_seq: _Optional[int] = ...,
        min_voting_tokens_factor: _Optional[str] = ...,
    ) -> None: ...

class PartyProposalVoteCount(_message.Message):
    __slots__ = ("party", "proposal", "count")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    party: str
    proposal: str
    count: int
    def __init__(
        self,
        party: _Optional[str] = ...,
        proposal: _Optional[str] = ...,
        count: _Optional[int] = ...,
    ) -> None: ...

class PartyTokenBalance(_message.Message):
    __slots__ = ("party", "balance")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    party: str
    balance: str
    def __init__(
        self, party: _Optional[str] = ..., balance: _Optional[str] = ...
    ) -> None: ...

class BlockRejectStats(_message.Message):
    __slots__ = ("rejected", "total")
    REJECTED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    rejected: int
    total: int
    def __init__(
        self, rejected: _Optional[int] = ..., total: _Optional[int] = ...
    ) -> None: ...

class SpamPartyTransactionCount(_message.Message):
    __slots__ = ("party", "count")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    party: str
    count: int
    def __init__(
        self, party: _Optional[str] = ..., count: _Optional[int] = ...
    ) -> None: ...

class SimpleSpamPolicy(_message.Message):
    __slots__ = (
        "policy_name",
        "party_to_count",
        "banned_parties",
        "token_balance",
        "current_epoch_seq",
    )
    POLICY_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTY_TO_COUNT_FIELD_NUMBER: _ClassVar[int]
    BANNED_PARTIES_FIELD_NUMBER: _ClassVar[int]
    TOKEN_BALANCE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    policy_name: str
    party_to_count: _containers.RepeatedCompositeFieldContainer[
        SpamPartyTransactionCount
    ]
    banned_parties: _containers.RepeatedCompositeFieldContainer[BannedParty]
    token_balance: _containers.RepeatedCompositeFieldContainer[PartyTokenBalance]
    current_epoch_seq: int
    def __init__(
        self,
        policy_name: _Optional[str] = ...,
        party_to_count: _Optional[
            _Iterable[_Union[SpamPartyTransactionCount, _Mapping]]
        ] = ...,
        banned_parties: _Optional[_Iterable[_Union[BannedParty, _Mapping]]] = ...,
        token_balance: _Optional[_Iterable[_Union[PartyTokenBalance, _Mapping]]] = ...,
        current_epoch_seq: _Optional[int] = ...,
    ) -> None: ...

class NotarySigs(_message.Message):
    __slots__ = ("id", "kind", "node", "sig", "pending")
    ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    SIG_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    id: str
    kind: int
    node: str
    sig: str
    pending: bool
    def __init__(
        self,
        id: _Optional[str] = ...,
        kind: _Optional[int] = ...,
        node: _Optional[str] = ...,
        sig: _Optional[str] = ...,
        pending: bool = ...,
    ) -> None: ...

class Notary(_message.Message):
    __slots__ = ("notary_sigs",)
    NOTARY_SIGS_FIELD_NUMBER: _ClassVar[int]
    notary_sigs: _containers.RepeatedCompositeFieldContainer[NotarySigs]
    def __init__(
        self, notary_sigs: _Optional[_Iterable[_Union[NotarySigs, _Mapping]]] = ...
    ) -> None: ...

class StakeVerifierDeposited(_message.Message):
    __slots__ = ("pending_deposited",)
    PENDING_DEPOSITED_FIELD_NUMBER: _ClassVar[int]
    pending_deposited: _containers.RepeatedCompositeFieldContainer[StakeVerifierPending]
    def __init__(
        self,
        pending_deposited: _Optional[
            _Iterable[_Union[StakeVerifierPending, _Mapping]]
        ] = ...,
    ) -> None: ...

class StakeVerifierRemoved(_message.Message):
    __slots__ = ("pending_removed",)
    PENDING_REMOVED_FIELD_NUMBER: _ClassVar[int]
    pending_removed: _containers.RepeatedCompositeFieldContainer[StakeVerifierPending]
    def __init__(
        self,
        pending_removed: _Optional[
            _Iterable[_Union[StakeVerifierPending, _Mapping]]
        ] = ...,
    ) -> None: ...

class StakeVerifierPending(_message.Message):
    __slots__ = (
        "ethereum_address",
        "vega_public_key",
        "amount",
        "block_time",
        "block_number",
        "log_index",
        "tx_id",
        "id",
    )
    ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    VEGA_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    BLOCK_NUMBER_FIELD_NUMBER: _ClassVar[int]
    LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    TX_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ethereum_address: str
    vega_public_key: str
    amount: str
    block_time: int
    block_number: int
    log_index: int
    tx_id: str
    id: str
    def __init__(
        self,
        ethereum_address: _Optional[str] = ...,
        vega_public_key: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        block_time: _Optional[int] = ...,
        block_number: _Optional[int] = ...,
        log_index: _Optional[int] = ...,
        tx_id: _Optional[str] = ...,
        id: _Optional[str] = ...,
    ) -> None: ...

class L2EthOracles(_message.Message):
    __slots__ = ("chain_id_eth_oracles",)
    CHAIN_ID_ETH_ORACLES_FIELD_NUMBER: _ClassVar[int]
    chain_id_eth_oracles: _containers.RepeatedCompositeFieldContainer[ChainIdEthOracles]
    def __init__(
        self,
        chain_id_eth_oracles: _Optional[
            _Iterable[_Union[ChainIdEthOracles, _Mapping]]
        ] = ...,
    ) -> None: ...

class ChainIdEthOracles(_message.Message):
    __slots__ = ("source_chain_id", "last_block", "call_results")
    SOURCE_CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_BLOCK_FIELD_NUMBER: _ClassVar[int]
    CALL_RESULTS_FIELD_NUMBER: _ClassVar[int]
    source_chain_id: str
    last_block: EthOracleVerifierLastBlock
    call_results: EthContractCallResults
    def __init__(
        self,
        source_chain_id: _Optional[str] = ...,
        last_block: _Optional[_Union[EthOracleVerifierLastBlock, _Mapping]] = ...,
        call_results: _Optional[_Union[EthContractCallResults, _Mapping]] = ...,
    ) -> None: ...

class EthOracleVerifierLastBlock(_message.Message):
    __slots__ = ("block_height", "block_time")
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    block_height: int
    block_time: int
    def __init__(
        self, block_height: _Optional[int] = ..., block_time: _Optional[int] = ...
    ) -> None: ...

class EthContractCallResults(_message.Message):
    __slots__ = ("pending_contract_call_result",)
    PENDING_CONTRACT_CALL_RESULT_FIELD_NUMBER: _ClassVar[int]
    pending_contract_call_result: _containers.RepeatedCompositeFieldContainer[
        EthContractCallResult
    ]
    def __init__(
        self,
        pending_contract_call_result: _Optional[
            _Iterable[_Union[EthContractCallResult, _Mapping]]
        ] = ...,
    ) -> None: ...

class EthContractCallResult(_message.Message):
    __slots__ = ("block_height", "block_time", "spec_id", "result", "error")
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    SPEC_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    block_height: int
    block_time: int
    spec_id: str
    result: bytes
    error: str
    def __init__(
        self,
        block_height: _Optional[int] = ...,
        block_time: _Optional[int] = ...,
        spec_id: _Optional[str] = ...,
        result: _Optional[bytes] = ...,
        error: _Optional[str] = ...,
    ) -> None: ...

class PendingKeyRotation(_message.Message):
    __slots__ = ("block_height", "node_id", "new_pub_key", "new_pub_key_index")
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    NEW_PUB_KEY_INDEX_FIELD_NUMBER: _ClassVar[int]
    block_height: int
    node_id: str
    new_pub_key: str
    new_pub_key_index: int
    def __init__(
        self,
        block_height: _Optional[int] = ...,
        node_id: _Optional[str] = ...,
        new_pub_key: _Optional[str] = ...,
        new_pub_key_index: _Optional[int] = ...,
    ) -> None: ...

class PendingEthereumKeyRotation(_message.Message):
    __slots__ = ("block_height", "node_id", "new_address", "submitter", "old_address")
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_FIELD_NUMBER: _ClassVar[int]
    OLD_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    block_height: int
    node_id: str
    new_address: str
    submitter: str
    old_address: str
    def __init__(
        self,
        block_height: _Optional[int] = ...,
        node_id: _Optional[str] = ...,
        new_address: _Optional[str] = ...,
        submitter: _Optional[str] = ...,
        old_address: _Optional[str] = ...,
    ) -> None: ...

class Topology(_message.Message):
    __slots__ = (
        "validator_data",
        "chain_keys",
        "pending_pub_key_rotations",
        "validator_performance",
        "pending_ethereum_key_rotations",
        "signatures",
        "unsolved_ethereum_key_rotations",
    )
    VALIDATOR_DATA_FIELD_NUMBER: _ClassVar[int]
    CHAIN_KEYS_FIELD_NUMBER: _ClassVar[int]
    PENDING_PUB_KEY_ROTATIONS_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_PERFORMANCE_FIELD_NUMBER: _ClassVar[int]
    PENDING_ETHEREUM_KEY_ROTATIONS_FIELD_NUMBER: _ClassVar[int]
    SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    UNSOLVED_ETHEREUM_KEY_ROTATIONS_FIELD_NUMBER: _ClassVar[int]
    validator_data: _containers.RepeatedCompositeFieldContainer[ValidatorState]
    chain_keys: _containers.RepeatedScalarFieldContainer[str]
    pending_pub_key_rotations: _containers.RepeatedCompositeFieldContainer[
        PendingKeyRotation
    ]
    validator_performance: ValidatorPerformance
    pending_ethereum_key_rotations: _containers.RepeatedCompositeFieldContainer[
        PendingEthereumKeyRotation
    ]
    signatures: ToplogySignatures
    unsolved_ethereum_key_rotations: _containers.RepeatedCompositeFieldContainer[
        PendingEthereumKeyRotation
    ]
    def __init__(
        self,
        validator_data: _Optional[_Iterable[_Union[ValidatorState, _Mapping]]] = ...,
        chain_keys: _Optional[_Iterable[str]] = ...,
        pending_pub_key_rotations: _Optional[
            _Iterable[_Union[PendingKeyRotation, _Mapping]]
        ] = ...,
        validator_performance: _Optional[_Union[ValidatorPerformance, _Mapping]] = ...,
        pending_ethereum_key_rotations: _Optional[
            _Iterable[_Union[PendingEthereumKeyRotation, _Mapping]]
        ] = ...,
        signatures: _Optional[_Union[ToplogySignatures, _Mapping]] = ...,
        unsolved_ethereum_key_rotations: _Optional[
            _Iterable[_Union[PendingEthereumKeyRotation, _Mapping]]
        ] = ...,
    ) -> None: ...

class ToplogySignatures(_message.Message):
    __slots__ = ("pending_signatures", "issued_signatures")
    PENDING_SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    ISSUED_SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    pending_signatures: _containers.RepeatedCompositeFieldContainer[
        PendingERC20MultisigControlSignature
    ]
    issued_signatures: _containers.RepeatedCompositeFieldContainer[
        IssuedERC20MultisigControlSignature
    ]
    def __init__(
        self,
        pending_signatures: _Optional[
            _Iterable[_Union[PendingERC20MultisigControlSignature, _Mapping]]
        ] = ...,
        issued_signatures: _Optional[
            _Iterable[_Union[IssuedERC20MultisigControlSignature, _Mapping]]
        ] = ...,
    ) -> None: ...

class PendingERC20MultisigControlSignature(_message.Message):
    __slots__ = ("node_id", "ethereum_address", "nonce", "epoch_seq", "added")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    ADDED_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    ethereum_address: str
    nonce: str
    epoch_seq: int
    added: bool
    def __init__(
        self,
        node_id: _Optional[str] = ...,
        ethereum_address: _Optional[str] = ...,
        nonce: _Optional[str] = ...,
        epoch_seq: _Optional[int] = ...,
        added: bool = ...,
    ) -> None: ...

class IssuedERC20MultisigControlSignature(_message.Message):
    __slots__ = ("resource_id", "ethereum_address", "submitter_address")
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    resource_id: str
    ethereum_address: str
    submitter_address: str
    def __init__(
        self,
        resource_id: _Optional[str] = ...,
        ethereum_address: _Optional[str] = ...,
        submitter_address: _Optional[str] = ...,
    ) -> None: ...

class ValidatorState(_message.Message):
    __slots__ = (
        "validator_update",
        "block_added",
        "status",
        "status_change_block",
        "last_block_with_positive_ranking",
        "eth_events_forwarded",
        "heartbeat_tracker",
        "validator_power",
        "ranking_score",
    )
    VALIDATOR_UPDATE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_ADDED_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_CHANGE_BLOCK_FIELD_NUMBER: _ClassVar[int]
    LAST_BLOCK_WITH_POSITIVE_RANKING_FIELD_NUMBER: _ClassVar[int]
    ETH_EVENTS_FORWARDED_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_TRACKER_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_POWER_FIELD_NUMBER: _ClassVar[int]
    RANKING_SCORE_FIELD_NUMBER: _ClassVar[int]
    validator_update: _events_pb2.ValidatorUpdate
    block_added: int
    status: int
    status_change_block: int
    last_block_with_positive_ranking: int
    eth_events_forwarded: int
    heartbeat_tracker: HeartbeatTracker
    validator_power: int
    ranking_score: _vega_pb2.RankingScore
    def __init__(
        self,
        validator_update: _Optional[
            _Union[_events_pb2.ValidatorUpdate, _Mapping]
        ] = ...,
        block_added: _Optional[int] = ...,
        status: _Optional[int] = ...,
        status_change_block: _Optional[int] = ...,
        last_block_with_positive_ranking: _Optional[int] = ...,
        eth_events_forwarded: _Optional[int] = ...,
        heartbeat_tracker: _Optional[_Union[HeartbeatTracker, _Mapping]] = ...,
        validator_power: _Optional[int] = ...,
        ranking_score: _Optional[_Union[_vega_pb2.RankingScore, _Mapping]] = ...,
    ) -> None: ...

class HeartbeatTracker(_message.Message):
    __slots__ = (
        "expected_next_hash",
        "expected_next_hash_since",
        "block_index",
        "block_sigs",
    )
    EXPECTED_NEXT_HASH_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_NEXT_HASH_SINCE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_INDEX_FIELD_NUMBER: _ClassVar[int]
    BLOCK_SIGS_FIELD_NUMBER: _ClassVar[int]
    expected_next_hash: str
    expected_next_hash_since: int
    block_index: int
    block_sigs: _containers.RepeatedScalarFieldContainer[bool]
    def __init__(
        self,
        expected_next_hash: _Optional[str] = ...,
        expected_next_hash_since: _Optional[int] = ...,
        block_index: _Optional[int] = ...,
        block_sigs: _Optional[_Iterable[bool]] = ...,
    ) -> None: ...

class PerformanceStats(_message.Message):
    __slots__ = (
        "validator_address",
        "proposed",
        "elected",
        "voted",
        "last_height_voted",
        "last_height_proposed",
        "last_height_elected",
    )
    VALIDATOR_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PROPOSED_FIELD_NUMBER: _ClassVar[int]
    ELECTED_FIELD_NUMBER: _ClassVar[int]
    VOTED_FIELD_NUMBER: _ClassVar[int]
    LAST_HEIGHT_VOTED_FIELD_NUMBER: _ClassVar[int]
    LAST_HEIGHT_PROPOSED_FIELD_NUMBER: _ClassVar[int]
    LAST_HEIGHT_ELECTED_FIELD_NUMBER: _ClassVar[int]
    validator_address: str
    proposed: int
    elected: int
    voted: int
    last_height_voted: int
    last_height_proposed: int
    last_height_elected: int
    def __init__(
        self,
        validator_address: _Optional[str] = ...,
        proposed: _Optional[int] = ...,
        elected: _Optional[int] = ...,
        voted: _Optional[int] = ...,
        last_height_voted: _Optional[int] = ...,
        last_height_proposed: _Optional[int] = ...,
        last_height_elected: _Optional[int] = ...,
    ) -> None: ...

class ValidatorPerformance(_message.Message):
    __slots__ = ("validator_perf_stats",)
    VALIDATOR_PERF_STATS_FIELD_NUMBER: _ClassVar[int]
    validator_perf_stats: _containers.RepeatedCompositeFieldContainer[PerformanceStats]
    def __init__(
        self,
        validator_perf_stats: _Optional[
            _Iterable[_Union[PerformanceStats, _Mapping]]
        ] = ...,
    ) -> None: ...

class LiquidityParameters(_message.Message):
    __slots__ = ("max_fee", "max_shape_size", "stake_to_obligation_factor", "market_id")
    MAX_FEE_FIELD_NUMBER: _ClassVar[int]
    MAX_SHAPE_SIZE_FIELD_NUMBER: _ClassVar[int]
    STAKE_TO_OBLIGATION_FACTOR_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    max_fee: str
    max_shape_size: str
    stake_to_obligation_factor: str
    market_id: str
    def __init__(
        self,
        max_fee: _Optional[str] = ...,
        max_shape_size: _Optional[str] = ...,
        stake_to_obligation_factor: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
    ) -> None: ...

class LiquidityPendingProvisions(_message.Message):
    __slots__ = ("pending_provisions", "market_id")
    PENDING_PROVISIONS_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    pending_provisions: _containers.RepeatedScalarFieldContainer[str]
    market_id: str
    def __init__(
        self,
        pending_provisions: _Optional[_Iterable[str]] = ...,
        market_id: _Optional[str] = ...,
    ) -> None: ...

class LiquidityPartiesLiquidityOrders(_message.Message):
    __slots__ = ("party_orders", "market_id")
    PARTY_ORDERS_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    party_orders: _containers.RepeatedCompositeFieldContainer[PartyOrders]
    market_id: str
    def __init__(
        self,
        party_orders: _Optional[_Iterable[_Union[PartyOrders, _Mapping]]] = ...,
        market_id: _Optional[str] = ...,
    ) -> None: ...

class PartyOrders(_message.Message):
    __slots__ = ("party", "orders")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    party: str
    orders: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Order]
    def __init__(
        self,
        party: _Optional[str] = ...,
        orders: _Optional[_Iterable[_Union[_vega_pb2.Order, _Mapping]]] = ...,
    ) -> None: ...

class LiquidityPartiesOrders(_message.Message):
    __slots__ = ("party_orders", "market_id")
    PARTY_ORDERS_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    party_orders: _containers.RepeatedCompositeFieldContainer[PartyOrders]
    market_id: str
    def __init__(
        self,
        party_orders: _Optional[_Iterable[_Union[PartyOrders, _Mapping]]] = ...,
        market_id: _Optional[str] = ...,
    ) -> None: ...

class LiquidityProvisions(_message.Message):
    __slots__ = ("liquidity_provisions", "market_id")
    LIQUIDITY_PROVISIONS_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    liquidity_provisions: _containers.RepeatedCompositeFieldContainer[
        _vega_pb2.LiquidityProvision
    ]
    market_id: str
    def __init__(
        self,
        liquidity_provisions: _Optional[
            _Iterable[_Union[_vega_pb2.LiquidityProvision, _Mapping]]
        ] = ...,
        market_id: _Optional[str] = ...,
    ) -> None: ...

class LiquidityScores(_message.Message):
    __slots__ = ("running_average_counter", "scores", "market_id")
    RUNNING_AVERAGE_COUNTER_FIELD_NUMBER: _ClassVar[int]
    SCORES_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    running_average_counter: int
    scores: _containers.RepeatedCompositeFieldContainer[LiquidityScore]
    market_id: str
    def __init__(
        self,
        running_average_counter: _Optional[int] = ...,
        scores: _Optional[_Iterable[_Union[LiquidityScore, _Mapping]]] = ...,
        market_id: _Optional[str] = ...,
    ) -> None: ...

class LiquidityScore(_message.Message):
    __slots__ = ("score", "party_id")
    SCORE_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    score: str
    party_id: str
    def __init__(
        self, score: _Optional[str] = ..., party_id: _Optional[str] = ...
    ) -> None: ...

class LiquidityV2Parameters(_message.Message):
    __slots__ = (
        "market_id",
        "market_sla_parameters",
        "stake_to_volume",
        "bond_penalty_slope",
        "bond_penalty_max",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_SLA_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    STAKE_TO_VOLUME_FIELD_NUMBER: _ClassVar[int]
    BOND_PENALTY_SLOPE_FIELD_NUMBER: _ClassVar[int]
    BOND_PENALTY_MAX_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    market_sla_parameters: _markets_pb2.LiquiditySLAParameters
    stake_to_volume: str
    bond_penalty_slope: str
    bond_penalty_max: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        market_sla_parameters: _Optional[
            _Union[_markets_pb2.LiquiditySLAParameters, _Mapping]
        ] = ...,
        stake_to_volume: _Optional[str] = ...,
        bond_penalty_slope: _Optional[str] = ...,
        bond_penalty_max: _Optional[str] = ...,
    ) -> None: ...

class LiquidityV2PaidFeesStats(_message.Message):
    __slots__ = ("market_id", "stats")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    stats: _events_pb2.PaidLiquidityFeesStats
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        stats: _Optional[_Union[_events_pb2.PaidLiquidityFeesStats, _Mapping]] = ...,
    ) -> None: ...

class LiquidityV2Provisions(_message.Message):
    __slots__ = ("market_id", "liquidity_provisions")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISIONS_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    liquidity_provisions: _containers.RepeatedCompositeFieldContainer[
        _vega_pb2.LiquidityProvision
    ]
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        liquidity_provisions: _Optional[
            _Iterable[_Union[_vega_pb2.LiquidityProvision, _Mapping]]
        ] = ...,
    ) -> None: ...

class LiquidityV2PendingProvisions(_message.Message):
    __slots__ = ("market_id", "pending_liquidity_provisions")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PENDING_LIQUIDITY_PROVISIONS_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    pending_liquidity_provisions: _containers.RepeatedCompositeFieldContainer[
        _vega_pb2.LiquidityProvision
    ]
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        pending_liquidity_provisions: _Optional[
            _Iterable[_Union[_vega_pb2.LiquidityProvision, _Mapping]]
        ] = ...,
    ) -> None: ...

class LiquidityV2Performances(_message.Message):
    __slots__ = ("market_id", "epoch_start_time", "performance_per_party")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_START_TIME_FIELD_NUMBER: _ClassVar[int]
    PERFORMANCE_PER_PARTY_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    epoch_start_time: int
    performance_per_party: _containers.RepeatedCompositeFieldContainer[
        LiquidityV2PerformancePerParty
    ]
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        epoch_start_time: _Optional[int] = ...,
        performance_per_party: _Optional[
            _Iterable[_Union[LiquidityV2PerformancePerParty, _Mapping]]
        ] = ...,
    ) -> None: ...

class LiquidityV2PerformancePerParty(_message.Message):
    __slots__ = (
        "party",
        "elapsed_time_meeting_sla_during_epoch",
        "commitment_start_time",
        "registered_penalties_per_epoch",
        "position_in_penalties_per_epoch",
        "last_epoch_fraction_of_time_on_book",
        "last_epoch_fee_penalty",
        "last_epoch_bond_penalty",
        "required_liquidity",
        "notional_volume_buys",
        "notional_volume_sells",
    )
    PARTY_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_TIME_MEETING_SLA_DURING_EPOCH_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_START_TIME_FIELD_NUMBER: _ClassVar[int]
    REGISTERED_PENALTIES_PER_EPOCH_FIELD_NUMBER: _ClassVar[int]
    POSITION_IN_PENALTIES_PER_EPOCH_FIELD_NUMBER: _ClassVar[int]
    LAST_EPOCH_FRACTION_OF_TIME_ON_BOOK_FIELD_NUMBER: _ClassVar[int]
    LAST_EPOCH_FEE_PENALTY_FIELD_NUMBER: _ClassVar[int]
    LAST_EPOCH_BOND_PENALTY_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_LIQUIDITY_FIELD_NUMBER: _ClassVar[int]
    NOTIONAL_VOLUME_BUYS_FIELD_NUMBER: _ClassVar[int]
    NOTIONAL_VOLUME_SELLS_FIELD_NUMBER: _ClassVar[int]
    party: str
    elapsed_time_meeting_sla_during_epoch: int
    commitment_start_time: int
    registered_penalties_per_epoch: _containers.RepeatedScalarFieldContainer[str]
    position_in_penalties_per_epoch: int
    last_epoch_fraction_of_time_on_book: str
    last_epoch_fee_penalty: str
    last_epoch_bond_penalty: str
    required_liquidity: str
    notional_volume_buys: str
    notional_volume_sells: str
    def __init__(
        self,
        party: _Optional[str] = ...,
        elapsed_time_meeting_sla_during_epoch: _Optional[int] = ...,
        commitment_start_time: _Optional[int] = ...,
        registered_penalties_per_epoch: _Optional[_Iterable[str]] = ...,
        position_in_penalties_per_epoch: _Optional[int] = ...,
        last_epoch_fraction_of_time_on_book: _Optional[str] = ...,
        last_epoch_fee_penalty: _Optional[str] = ...,
        last_epoch_bond_penalty: _Optional[str] = ...,
        required_liquidity: _Optional[str] = ...,
        notional_volume_buys: _Optional[str] = ...,
        notional_volume_sells: _Optional[str] = ...,
    ) -> None: ...

class LiquidityV2Scores(_message.Message):
    __slots__ = (
        "market_id",
        "running_average_counter",
        "scores",
        "last_fee_distribution_time",
        "fee_calculation_time_step",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    RUNNING_AVERAGE_COUNTER_FIELD_NUMBER: _ClassVar[int]
    SCORES_FIELD_NUMBER: _ClassVar[int]
    LAST_FEE_DISTRIBUTION_TIME_FIELD_NUMBER: _ClassVar[int]
    FEE_CALCULATION_TIME_STEP_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    running_average_counter: int
    scores: _containers.RepeatedCompositeFieldContainer[LiquidityScore]
    last_fee_distribution_time: int
    fee_calculation_time_step: int
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        running_average_counter: _Optional[int] = ...,
        scores: _Optional[_Iterable[_Union[LiquidityScore, _Mapping]]] = ...,
        last_fee_distribution_time: _Optional[int] = ...,
        fee_calculation_time_step: _Optional[int] = ...,
    ) -> None: ...

class LiquidityV2Supplied(_message.Message):
    __slots__ = ("market_id", "consensus_reached", "bid_cache", "ask_cache")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    CONSENSUS_REACHED_FIELD_NUMBER: _ClassVar[int]
    BID_CACHE_FIELD_NUMBER: _ClassVar[int]
    ASK_CACHE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    consensus_reached: bool
    bid_cache: _containers.RepeatedCompositeFieldContainer[
        LiquidityOffsetProbabilityPair
    ]
    ask_cache: _containers.RepeatedCompositeFieldContainer[
        LiquidityOffsetProbabilityPair
    ]
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        consensus_reached: bool = ...,
        bid_cache: _Optional[
            _Iterable[_Union[LiquidityOffsetProbabilityPair, _Mapping]]
        ] = ...,
        ask_cache: _Optional[
            _Iterable[_Union[LiquidityOffsetProbabilityPair, _Mapping]]
        ] = ...,
    ) -> None: ...

class FloatingPointConsensus(_message.Message):
    __slots__ = ("next_time_trigger", "state_variables")
    NEXT_TIME_TRIGGER_FIELD_NUMBER: _ClassVar[int]
    STATE_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    next_time_trigger: _containers.RepeatedCompositeFieldContainer[NextTimeTrigger]
    state_variables: _containers.RepeatedCompositeFieldContainer[StateVarInternalState]
    def __init__(
        self,
        next_time_trigger: _Optional[
            _Iterable[_Union[NextTimeTrigger, _Mapping]]
        ] = ...,
        state_variables: _Optional[
            _Iterable[_Union[StateVarInternalState, _Mapping]]
        ] = ...,
    ) -> None: ...

class StateVarInternalState(_message.Message):
    __slots__ = (
        "id",
        "state",
        "event_id",
        "validators_results",
        "rounds_since_meaningful_update",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    VALIDATORS_RESULTS_FIELD_NUMBER: _ClassVar[int]
    ROUNDS_SINCE_MEANINGFUL_UPDATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    state: int
    event_id: str
    validators_results: _containers.RepeatedCompositeFieldContainer[
        FloatingPointValidatorResult
    ]
    rounds_since_meaningful_update: int
    def __init__(
        self,
        id: _Optional[str] = ...,
        state: _Optional[int] = ...,
        event_id: _Optional[str] = ...,
        validators_results: _Optional[
            _Iterable[_Union[FloatingPointValidatorResult, _Mapping]]
        ] = ...,
        rounds_since_meaningful_update: _Optional[int] = ...,
    ) -> None: ...

class FloatingPointValidatorResult(_message.Message):
    __slots__ = ("id", "bundle")
    ID_FIELD_NUMBER: _ClassVar[int]
    BUNDLE_FIELD_NUMBER: _ClassVar[int]
    id: str
    bundle: _containers.RepeatedCompositeFieldContainer[_vega_pb2.KeyValueBundle]
    def __init__(
        self,
        id: _Optional[str] = ...,
        bundle: _Optional[_Iterable[_Union[_vega_pb2.KeyValueBundle, _Mapping]]] = ...,
    ) -> None: ...

class NextTimeTrigger(_message.Message):
    __slots__ = ("asset", "market", "id", "next_trigger")
    ASSET_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NEXT_TRIGGER_FIELD_NUMBER: _ClassVar[int]
    asset: str
    market: str
    id: str
    next_trigger: int
    def __init__(
        self,
        asset: _Optional[str] = ...,
        market: _Optional[str] = ...,
        id: _Optional[str] = ...,
        next_trigger: _Optional[int] = ...,
    ) -> None: ...

class MarketTracker(_message.Message):
    __slots__ = ("market_activity", "taker_notional_volume")
    MARKET_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    TAKER_NOTIONAL_VOLUME_FIELD_NUMBER: _ClassVar[int]
    market_activity: _containers.RepeatedCompositeFieldContainer[
        _checkpoint_pb2.MarketActivityTracker
    ]
    taker_notional_volume: _containers.RepeatedCompositeFieldContainer[
        _checkpoint_pb2.TakerNotionalVolume
    ]
    def __init__(
        self,
        market_activity: _Optional[
            _Iterable[_Union[_checkpoint_pb2.MarketActivityTracker, _Mapping]]
        ] = ...,
        taker_notional_volume: _Optional[
            _Iterable[_Union[_checkpoint_pb2.TakerNotionalVolume, _Mapping]]
        ] = ...,
    ) -> None: ...

class SignerEventsPerAddress(_message.Message):
    __slots__ = ("address", "events")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    address: str
    events: _containers.RepeatedCompositeFieldContainer[
        _events_pb2.ERC20MultiSigSignerEvent
    ]
    def __init__(
        self,
        address: _Optional[str] = ...,
        events: _Optional[
            _Iterable[_Union[_events_pb2.ERC20MultiSigSignerEvent, _Mapping]]
        ] = ...,
    ) -> None: ...

class ERC20MultiSigTopologyVerified(_message.Message):
    __slots__ = ("signers", "events_per_address", "threshold", "seen_events")
    SIGNERS_FIELD_NUMBER: _ClassVar[int]
    EVENTS_PER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    SEEN_EVENTS_FIELD_NUMBER: _ClassVar[int]
    signers: _containers.RepeatedScalarFieldContainer[str]
    events_per_address: _containers.RepeatedCompositeFieldContainer[
        SignerEventsPerAddress
    ]
    threshold: _events_pb2.ERC20MultiSigThresholdSetEvent
    seen_events: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        signers: _Optional[_Iterable[str]] = ...,
        events_per_address: _Optional[
            _Iterable[_Union[SignerEventsPerAddress, _Mapping]]
        ] = ...,
        threshold: _Optional[
            _Union[_events_pb2.ERC20MultiSigThresholdSetEvent, _Mapping]
        ] = ...,
        seen_events: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class ERC20MultiSigTopologyPending(_message.Message):
    __slots__ = (
        "pending_signers",
        "pending_threshold_set",
        "witnessed_signers",
        "witnessed_threshold_sets",
    )
    PENDING_SIGNERS_FIELD_NUMBER: _ClassVar[int]
    PENDING_THRESHOLD_SET_FIELD_NUMBER: _ClassVar[int]
    WITNESSED_SIGNERS_FIELD_NUMBER: _ClassVar[int]
    WITNESSED_THRESHOLD_SETS_FIELD_NUMBER: _ClassVar[int]
    pending_signers: _containers.RepeatedCompositeFieldContainer[
        _events_pb2.ERC20MultiSigSignerEvent
    ]
    pending_threshold_set: _containers.RepeatedCompositeFieldContainer[
        _events_pb2.ERC20MultiSigThresholdSetEvent
    ]
    witnessed_signers: _containers.RepeatedScalarFieldContainer[str]
    witnessed_threshold_sets: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        pending_signers: _Optional[
            _Iterable[_Union[_events_pb2.ERC20MultiSigSignerEvent, _Mapping]]
        ] = ...,
        pending_threshold_set: _Optional[
            _Iterable[_Union[_events_pb2.ERC20MultiSigThresholdSetEvent, _Mapping]]
        ] = ...,
        witnessed_signers: _Optional[_Iterable[str]] = ...,
        witnessed_threshold_sets: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class ProofOfWork(_message.Message):
    __slots__ = (
        "block_height",
        "block_hash",
        "tx_at_height",
        "tid_at_height",
        "banned",
        "pow_params",
        "pow_state",
        "last_pruning_block",
        "nonce_refs_at_height",
    )
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HASH_FIELD_NUMBER: _ClassVar[int]
    TX_AT_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TID_AT_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BANNED_FIELD_NUMBER: _ClassVar[int]
    POW_PARAMS_FIELD_NUMBER: _ClassVar[int]
    POW_STATE_FIELD_NUMBER: _ClassVar[int]
    LAST_PRUNING_BLOCK_FIELD_NUMBER: _ClassVar[int]
    NONCE_REFS_AT_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    block_height: _containers.RepeatedScalarFieldContainer[int]
    block_hash: _containers.RepeatedScalarFieldContainer[str]
    tx_at_height: _containers.RepeatedCompositeFieldContainer[TransactionsAtHeight]
    tid_at_height: _containers.RepeatedCompositeFieldContainer[TransactionsAtHeight]
    banned: _containers.RepeatedCompositeFieldContainer[BannedParty]
    pow_params: _containers.RepeatedCompositeFieldContainer[ProofOfWorkParams]
    pow_state: _containers.RepeatedCompositeFieldContainer[ProofOfWorkState]
    last_pruning_block: int
    nonce_refs_at_height: _containers.RepeatedCompositeFieldContainer[NonceRefsAtHeight]
    def __init__(
        self,
        block_height: _Optional[_Iterable[int]] = ...,
        block_hash: _Optional[_Iterable[str]] = ...,
        tx_at_height: _Optional[
            _Iterable[_Union[TransactionsAtHeight, _Mapping]]
        ] = ...,
        tid_at_height: _Optional[
            _Iterable[_Union[TransactionsAtHeight, _Mapping]]
        ] = ...,
        banned: _Optional[_Iterable[_Union[BannedParty, _Mapping]]] = ...,
        pow_params: _Optional[_Iterable[_Union[ProofOfWorkParams, _Mapping]]] = ...,
        pow_state: _Optional[_Iterable[_Union[ProofOfWorkState, _Mapping]]] = ...,
        last_pruning_block: _Optional[int] = ...,
        nonce_refs_at_height: _Optional[
            _Iterable[_Union[NonceRefsAtHeight, _Mapping]]
        ] = ...,
    ) -> None: ...

class BannedParty(_message.Message):
    __slots__ = ("party", "until")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    UNTIL_FIELD_NUMBER: _ClassVar[int]
    party: str
    until: int
    def __init__(
        self, party: _Optional[str] = ..., until: _Optional[int] = ...
    ) -> None: ...

class ProofOfWorkParams(_message.Message):
    __slots__ = (
        "spam_pow_number_of_past_blocks",
        "spam_pow_difficulty",
        "spam_pow_hash_function",
        "spam_pow_number_of_tx_per_block",
        "spam_pow_increasing_difficulty",
        "from_block",
        "until_block",
    )
    SPAM_POW_NUMBER_OF_PAST_BLOCKS_FIELD_NUMBER: _ClassVar[int]
    SPAM_POW_DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    SPAM_POW_HASH_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    SPAM_POW_NUMBER_OF_TX_PER_BLOCK_FIELD_NUMBER: _ClassVar[int]
    SPAM_POW_INCREASING_DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    FROM_BLOCK_FIELD_NUMBER: _ClassVar[int]
    UNTIL_BLOCK_FIELD_NUMBER: _ClassVar[int]
    spam_pow_number_of_past_blocks: int
    spam_pow_difficulty: int
    spam_pow_hash_function: str
    spam_pow_number_of_tx_per_block: int
    spam_pow_increasing_difficulty: bool
    from_block: int
    until_block: int
    def __init__(
        self,
        spam_pow_number_of_past_blocks: _Optional[int] = ...,
        spam_pow_difficulty: _Optional[int] = ...,
        spam_pow_hash_function: _Optional[str] = ...,
        spam_pow_number_of_tx_per_block: _Optional[int] = ...,
        spam_pow_increasing_difficulty: bool = ...,
        from_block: _Optional[int] = ...,
        until_block: _Optional[int] = ...,
    ) -> None: ...

class ProofOfWorkState(_message.Message):
    __slots__ = ("pow_state",)
    POW_STATE_FIELD_NUMBER: _ClassVar[int]
    pow_state: _containers.RepeatedCompositeFieldContainer[ProofOfWorkBlockState]
    def __init__(
        self,
        pow_state: _Optional[_Iterable[_Union[ProofOfWorkBlockState, _Mapping]]] = ...,
    ) -> None: ...

class ProofOfWorkBlockState(_message.Message):
    __slots__ = ("block_height", "party_state")
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    PARTY_STATE_FIELD_NUMBER: _ClassVar[int]
    block_height: int
    party_state: _containers.RepeatedCompositeFieldContainer[
        ProofOfWorkPartyStateForBlock
    ]
    def __init__(
        self,
        block_height: _Optional[int] = ...,
        party_state: _Optional[
            _Iterable[_Union[ProofOfWorkPartyStateForBlock, _Mapping]]
        ] = ...,
    ) -> None: ...

class ProofOfWorkPartyStateForBlock(_message.Message):
    __slots__ = ("party", "seen_count", "observed_difficulty")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    SEEN_COUNT_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    party: str
    seen_count: int
    observed_difficulty: int
    def __init__(
        self,
        party: _Optional[str] = ...,
        seen_count: _Optional[int] = ...,
        observed_difficulty: _Optional[int] = ...,
    ) -> None: ...

class TransactionsAtHeight(_message.Message):
    __slots__ = ("height", "transactions")
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    height: int
    transactions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        height: _Optional[int] = ...,
        transactions: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class NonceRef(_message.Message):
    __slots__ = ("party", "nonce")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    party: str
    nonce: int
    def __init__(
        self, party: _Optional[str] = ..., nonce: _Optional[int] = ...
    ) -> None: ...

class NonceRefsAtHeight(_message.Message):
    __slots__ = ("height", "refs")
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    REFS_FIELD_NUMBER: _ClassVar[int]
    height: int
    refs: _containers.RepeatedCompositeFieldContainer[NonceRef]
    def __init__(
        self,
        height: _Optional[int] = ...,
        refs: _Optional[_Iterable[_Union[NonceRef, _Mapping]]] = ...,
    ) -> None: ...

class ProtocolUpgradeProposals(_message.Message):
    __slots__ = ("active_proposals", "accepted_proposal")
    ACTIVE_PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    active_proposals: _containers.RepeatedCompositeFieldContainer[
        _events_pb2.ProtocolUpgradeEvent
    ]
    accepted_proposal: AcceptedProtocolUpgradeProposal
    def __init__(
        self,
        active_proposals: _Optional[
            _Iterable[_Union[_events_pb2.ProtocolUpgradeEvent, _Mapping]]
        ] = ...,
        accepted_proposal: _Optional[
            _Union[AcceptedProtocolUpgradeProposal, _Mapping]
        ] = ...,
    ) -> None: ...

class AcceptedProtocolUpgradeProposal(_message.Message):
    __slots__ = ("upgrade_block_height", "vega_release_tag")
    UPGRADE_BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    VEGA_RELEASE_TAG_FIELD_NUMBER: _ClassVar[int]
    upgrade_block_height: int
    vega_release_tag: str
    def __init__(
        self,
        upgrade_block_height: _Optional[int] = ...,
        vega_release_tag: _Optional[str] = ...,
    ) -> None: ...

class Teams(_message.Message):
    __slots__ = ("teams",)
    TEAMS_FIELD_NUMBER: _ClassVar[int]
    teams: _containers.RepeatedCompositeFieldContainer[Team]
    def __init__(
        self, teams: _Optional[_Iterable[_Union[Team, _Mapping]]] = ...
    ) -> None: ...

class Team(_message.Message):
    __slots__ = (
        "id",
        "referrer",
        "referees",
        "name",
        "team_url",
        "avatar_url",
        "created_at",
        "closed",
        "allow_list",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    REFERRER_FIELD_NUMBER: _ClassVar[int]
    REFEREES_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEAM_URL_FIELD_NUMBER: _ClassVar[int]
    AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CLOSED_FIELD_NUMBER: _ClassVar[int]
    ALLOW_LIST_FIELD_NUMBER: _ClassVar[int]
    id: str
    referrer: Membership
    referees: _containers.RepeatedCompositeFieldContainer[Membership]
    name: str
    team_url: str
    avatar_url: str
    created_at: int
    closed: bool
    allow_list: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        id: _Optional[str] = ...,
        referrer: _Optional[_Union[Membership, _Mapping]] = ...,
        referees: _Optional[_Iterable[_Union[Membership, _Mapping]]] = ...,
        name: _Optional[str] = ...,
        team_url: _Optional[str] = ...,
        avatar_url: _Optional[str] = ...,
        created_at: _Optional[int] = ...,
        closed: bool = ...,
        allow_list: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class Membership(_message.Message):
    __slots__ = ("party_id", "joined_at", "started_at_epoch")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    joined_at: int
    started_at_epoch: int
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        joined_at: _Optional[int] = ...,
        started_at_epoch: _Optional[int] = ...,
    ) -> None: ...

class TeamSwitches(_message.Message):
    __slots__ = ("team_switches",)
    TEAM_SWITCHES_FIELD_NUMBER: _ClassVar[int]
    team_switches: _containers.RepeatedCompositeFieldContainer[TeamSwitch]
    def __init__(
        self, team_switches: _Optional[_Iterable[_Union[TeamSwitch, _Mapping]]] = ...
    ) -> None: ...

class TeamSwitch(_message.Message):
    __slots__ = ("from_team_id", "to_team_id", "party_id")
    FROM_TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    TO_TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    from_team_id: str
    to_team_id: str
    party_id: str
    def __init__(
        self,
        from_team_id: _Optional[str] = ...,
        to_team_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
    ) -> None: ...

class Vesting(_message.Message):
    __slots__ = ("parties_reward",)
    PARTIES_REWARD_FIELD_NUMBER: _ClassVar[int]
    parties_reward: _containers.RepeatedCompositeFieldContainer[PartyReward]
    def __init__(
        self, parties_reward: _Optional[_Iterable[_Union[PartyReward, _Mapping]]] = ...
    ) -> None: ...

class PartyReward(_message.Message):
    __slots__ = ("party", "asset_locked", "in_vesting")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    ASSET_LOCKED_FIELD_NUMBER: _ClassVar[int]
    IN_VESTING_FIELD_NUMBER: _ClassVar[int]
    party: str
    asset_locked: _containers.RepeatedCompositeFieldContainer[AssetLocked]
    in_vesting: _containers.RepeatedCompositeFieldContainer[InVesting]
    def __init__(
        self,
        party: _Optional[str] = ...,
        asset_locked: _Optional[_Iterable[_Union[AssetLocked, _Mapping]]] = ...,
        in_vesting: _Optional[_Iterable[_Union[InVesting, _Mapping]]] = ...,
    ) -> None: ...

class ReferralProgramData(_message.Message):
    __slots__ = (
        "factor_by_referee",
        "current_program",
        "new_program",
        "last_program_version",
        "program_has_ended",
        "sets",
    )
    FACTOR_BY_REFEREE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PROGRAM_FIELD_NUMBER: _ClassVar[int]
    NEW_PROGRAM_FIELD_NUMBER: _ClassVar[int]
    LAST_PROGRAM_VERSION_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_HAS_ENDED_FIELD_NUMBER: _ClassVar[int]
    SETS_FIELD_NUMBER: _ClassVar[int]
    factor_by_referee: _containers.RepeatedCompositeFieldContainer[FactorByReferee]
    current_program: _vega_pb2.ReferralProgram
    new_program: _vega_pb2.ReferralProgram
    last_program_version: int
    program_has_ended: bool
    sets: _containers.RepeatedCompositeFieldContainer[ReferralSet]
    def __init__(
        self,
        factor_by_referee: _Optional[
            _Iterable[_Union[FactorByReferee, _Mapping]]
        ] = ...,
        current_program: _Optional[_Union[_vega_pb2.ReferralProgram, _Mapping]] = ...,
        new_program: _Optional[_Union[_vega_pb2.ReferralProgram, _Mapping]] = ...,
        last_program_version: _Optional[int] = ...,
        program_has_ended: bool = ...,
        sets: _Optional[_Iterable[_Union[ReferralSet, _Mapping]]] = ...,
    ) -> None: ...

class ReferralSet(_message.Message):
    __slots__ = (
        "id",
        "created_at",
        "updated_at",
        "referrer",
        "referees",
        "running_volumes",
        "current_reward_factor",
        "current_rewards_multiplier",
        "current_rewards_factor_multiplier",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    REFERRER_FIELD_NUMBER: _ClassVar[int]
    REFEREES_FIELD_NUMBER: _ClassVar[int]
    RUNNING_VOLUMES_FIELD_NUMBER: _ClassVar[int]
    CURRENT_REWARD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    CURRENT_REWARDS_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    CURRENT_REWARDS_FACTOR_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: int
    updated_at: int
    referrer: Membership
    referees: _containers.RepeatedCompositeFieldContainer[Membership]
    running_volumes: _containers.RepeatedCompositeFieldContainer[RunningVolume]
    current_reward_factor: str
    current_rewards_multiplier: str
    current_rewards_factor_multiplier: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        created_at: _Optional[int] = ...,
        updated_at: _Optional[int] = ...,
        referrer: _Optional[_Union[Membership, _Mapping]] = ...,
        referees: _Optional[_Iterable[_Union[Membership, _Mapping]]] = ...,
        running_volumes: _Optional[_Iterable[_Union[RunningVolume, _Mapping]]] = ...,
        current_reward_factor: _Optional[str] = ...,
        current_rewards_multiplier: _Optional[str] = ...,
        current_rewards_factor_multiplier: _Optional[str] = ...,
    ) -> None: ...

class RunningVolume(_message.Message):
    __slots__ = ("epoch", "volume")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    epoch: int
    volume: bytes
    def __init__(
        self, epoch: _Optional[int] = ..., volume: _Optional[bytes] = ...
    ) -> None: ...

class FactorByReferee(_message.Message):
    __slots__ = ("party", "discount_factor", "taker_volume")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    TAKER_VOLUME_FIELD_NUMBER: _ClassVar[int]
    party: str
    discount_factor: bytes
    taker_volume: bytes
    def __init__(
        self,
        party: _Optional[str] = ...,
        discount_factor: _Optional[bytes] = ...,
        taker_volume: _Optional[bytes] = ...,
    ) -> None: ...

class AssetLocked(_message.Message):
    __slots__ = ("asset", "epoch_balances")
    ASSET_FIELD_NUMBER: _ClassVar[int]
    EPOCH_BALANCES_FIELD_NUMBER: _ClassVar[int]
    asset: str
    epoch_balances: _containers.RepeatedCompositeFieldContainer[EpochBalance]
    def __init__(
        self,
        asset: _Optional[str] = ...,
        epoch_balances: _Optional[_Iterable[_Union[EpochBalance, _Mapping]]] = ...,
    ) -> None: ...

class EpochBalance(_message.Message):
    __slots__ = ("epoch", "balance")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    epoch: int
    balance: str
    def __init__(
        self, epoch: _Optional[int] = ..., balance: _Optional[str] = ...
    ) -> None: ...

class InVesting(_message.Message):
    __slots__ = ("asset", "balance")
    ASSET_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    asset: str
    balance: str
    def __init__(
        self, asset: _Optional[str] = ..., balance: _Optional[str] = ...
    ) -> None: ...

class ActivityStreak(_message.Message):
    __slots__ = ("parties_activity_streak",)
    PARTIES_ACTIVITY_STREAK_FIELD_NUMBER: _ClassVar[int]
    parties_activity_streak: _containers.RepeatedCompositeFieldContainer[
        PartyActivityStreak
    ]
    def __init__(
        self,
        parties_activity_streak: _Optional[
            _Iterable[_Union[PartyActivityStreak, _Mapping]]
        ] = ...,
    ) -> None: ...

class PartyActivityStreak(_message.Message):
    __slots__ = (
        "party",
        "active",
        "inactive",
        "reward_distribution_multiplier",
        "reward_vesting_multiplier",
    )
    PARTY_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    INACTIVE_FIELD_NUMBER: _ClassVar[int]
    REWARD_DISTRIBUTION_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    REWARD_VESTING_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    party: str
    active: int
    inactive: int
    reward_distribution_multiplier: bytes
    reward_vesting_multiplier: bytes
    def __init__(
        self,
        party: _Optional[str] = ...,
        active: _Optional[int] = ...,
        inactive: _Optional[int] = ...,
        reward_distribution_multiplier: _Optional[bytes] = ...,
        reward_vesting_multiplier: _Optional[bytes] = ...,
    ) -> None: ...

class VolumeDiscountProgram(_message.Message):
    __slots__ = (
        "parties",
        "epoch_party_volumes",
        "epoch_data_index",
        "average_party_volume",
        "current_program",
        "new_program",
        "factors_by_party",
        "last_program_version",
        "program_has_ended",
    )
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    EPOCH_PARTY_VOLUMES_FIELD_NUMBER: _ClassVar[int]
    EPOCH_DATA_INDEX_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_PARTY_VOLUME_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PROGRAM_FIELD_NUMBER: _ClassVar[int]
    NEW_PROGRAM_FIELD_NUMBER: _ClassVar[int]
    FACTORS_BY_PARTY_FIELD_NUMBER: _ClassVar[int]
    LAST_PROGRAM_VERSION_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_HAS_ENDED_FIELD_NUMBER: _ClassVar[int]
    parties: _containers.RepeatedScalarFieldContainer[str]
    epoch_party_volumes: _containers.RepeatedCompositeFieldContainer[EpochPartyVolumes]
    epoch_data_index: int
    average_party_volume: _containers.RepeatedCompositeFieldContainer[PartyVolume]
    current_program: _vega_pb2.VolumeDiscountProgram
    new_program: _vega_pb2.VolumeDiscountProgram
    factors_by_party: _containers.RepeatedCompositeFieldContainer[VolumeDiscountStats]
    last_program_version: int
    program_has_ended: bool
    def __init__(
        self,
        parties: _Optional[_Iterable[str]] = ...,
        epoch_party_volumes: _Optional[
            _Iterable[_Union[EpochPartyVolumes, _Mapping]]
        ] = ...,
        epoch_data_index: _Optional[int] = ...,
        average_party_volume: _Optional[_Iterable[_Union[PartyVolume, _Mapping]]] = ...,
        current_program: _Optional[
            _Union[_vega_pb2.VolumeDiscountProgram, _Mapping]
        ] = ...,
        new_program: _Optional[_Union[_vega_pb2.VolumeDiscountProgram, _Mapping]] = ...,
        factors_by_party: _Optional[
            _Iterable[_Union[VolumeDiscountStats, _Mapping]]
        ] = ...,
        last_program_version: _Optional[int] = ...,
        program_has_ended: bool = ...,
    ) -> None: ...

class VolumeDiscountStats(_message.Message):
    __slots__ = ("party", "discount_factor")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    party: str
    discount_factor: str
    def __init__(
        self, party: _Optional[str] = ..., discount_factor: _Optional[str] = ...
    ) -> None: ...

class EpochPartyVolumes(_message.Message):
    __slots__ = ("party_volume",)
    PARTY_VOLUME_FIELD_NUMBER: _ClassVar[int]
    party_volume: _containers.RepeatedCompositeFieldContainer[PartyVolume]
    def __init__(
        self, party_volume: _Optional[_Iterable[_Union[PartyVolume, _Mapping]]] = ...
    ) -> None: ...

class PartyVolume(_message.Message):
    __slots__ = ("party", "volume")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    party: str
    volume: bytes
    def __init__(
        self, party: _Optional[str] = ..., volume: _Optional[bytes] = ...
    ) -> None: ...

class Liquidation(_message.Message):
    __slots__ = ("market_id", "network_pos", "next_step", "config")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    NETWORK_POS_FIELD_NUMBER: _ClassVar[int]
    NEXT_STEP_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    network_pos: int
    next_step: int
    config: _markets_pb2.LiquidationStrategy
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        network_pos: _Optional[int] = ...,
        next_step: _Optional[int] = ...,
        config: _Optional[_Union[_markets_pb2.LiquidationStrategy, _Mapping]] = ...,
    ) -> None: ...

class PartyAssetAmount(_message.Message):
    __slots__ = ("party", "asset", "amount")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    party: str
    asset: str
    amount: str
    def __init__(
        self,
        party: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        amount: _Optional[str] = ...,
    ) -> None: ...

class BankingTransferFeeDiscounts(_message.Message):
    __slots__ = ("party_asset_discount",)
    PARTY_ASSET_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    party_asset_discount: _containers.RepeatedCompositeFieldContainer[PartyAssetAmount]
    def __init__(
        self,
        party_asset_discount: _Optional[
            _Iterable[_Union[PartyAssetAmount, _Mapping]]
        ] = ...,
    ) -> None: ...

class CompositePriceCalculator(_message.Message):
    __slots__ = (
        "composite_price",
        "price_configuration",
        "trades",
        "price_sources",
        "price_source_last_update",
        "book_price_at_time",
    )
    COMPOSITE_PRICE_FIELD_NUMBER: _ClassVar[int]
    PRICE_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    TRADES_FIELD_NUMBER: _ClassVar[int]
    PRICE_SOURCES_FIELD_NUMBER: _ClassVar[int]
    PRICE_SOURCE_LAST_UPDATE_FIELD_NUMBER: _ClassVar[int]
    BOOK_PRICE_AT_TIME_FIELD_NUMBER: _ClassVar[int]
    composite_price: str
    price_configuration: _markets_pb2.CompositePriceConfiguration
    trades: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Trade]
    price_sources: _containers.RepeatedScalarFieldContainer[str]
    price_source_last_update: _containers.RepeatedScalarFieldContainer[int]
    book_price_at_time: _containers.RepeatedCompositeFieldContainer[TimePrice]
    def __init__(
        self,
        composite_price: _Optional[str] = ...,
        price_configuration: _Optional[
            _Union[_markets_pb2.CompositePriceConfiguration, _Mapping]
        ] = ...,
        trades: _Optional[_Iterable[_Union[_vega_pb2.Trade, _Mapping]]] = ...,
        price_sources: _Optional[_Iterable[str]] = ...,
        price_source_last_update: _Optional[_Iterable[int]] = ...,
        book_price_at_time: _Optional[_Iterable[_Union[TimePrice, _Mapping]]] = ...,
    ) -> None: ...

class Parties(_message.Message):
    __slots__ = ("profiles",)
    PROFILES_FIELD_NUMBER: _ClassVar[int]
    profiles: _containers.RepeatedCompositeFieldContainer[PartyProfile]
    def __init__(
        self, profiles: _Optional[_Iterable[_Union[PartyProfile, _Mapping]]] = ...
    ) -> None: ...

class PartyProfile(_message.Message):
    __slots__ = ("party_id", "alias", "metadata")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    alias: str
    metadata: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Metadata]
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        alias: _Optional[str] = ...,
        metadata: _Optional[_Iterable[_Union[_vega_pb2.Metadata, _Mapping]]] = ...,
    ) -> None: ...
