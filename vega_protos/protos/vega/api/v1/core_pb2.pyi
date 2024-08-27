from google.api import field_behavior_pb2 as _field_behavior_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2
from vega.commands.v1 import transaction_pb2 as _transaction_pb2
from vega.events.v1 import events_pb2 as _events_pb2
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

class PropagateChainEventRequest(_message.Message):
    __slots__ = ("event", "pub_key", "signature")
    EVENT_FIELD_NUMBER: _ClassVar[int]
    PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    event: bytes
    pub_key: str
    signature: bytes
    def __init__(
        self,
        event: _Optional[bytes] = ...,
        pub_key: _Optional[str] = ...,
        signature: _Optional[bytes] = ...,
    ) -> None: ...

class PropagateChainEventResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class SubmitTransactionRequest(_message.Message):
    __slots__ = ("tx", "type")

    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[SubmitTransactionRequest.Type]
        TYPE_ASYNC: _ClassVar[SubmitTransactionRequest.Type]
        TYPE_SYNC: _ClassVar[SubmitTransactionRequest.Type]
        TYPE_COMMIT: _ClassVar[SubmitTransactionRequest.Type]

    TYPE_UNSPECIFIED: SubmitTransactionRequest.Type
    TYPE_ASYNC: SubmitTransactionRequest.Type
    TYPE_SYNC: SubmitTransactionRequest.Type
    TYPE_COMMIT: SubmitTransactionRequest.Type
    TX_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    tx: _transaction_pb2.Transaction
    type: SubmitTransactionRequest.Type
    def __init__(
        self,
        tx: _Optional[_Union[_transaction_pb2.Transaction, _Mapping]] = ...,
        type: _Optional[_Union[SubmitTransactionRequest.Type, str]] = ...,
    ) -> None: ...

class SubmitTransactionResponse(_message.Message):
    __slots__ = ("success", "tx_hash", "code", "data", "log", "height")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    tx_hash: str
    code: int
    data: str
    log: str
    height: int
    def __init__(
        self,
        success: bool = ...,
        tx_hash: _Optional[str] = ...,
        code: _Optional[int] = ...,
        data: _Optional[str] = ...,
        log: _Optional[str] = ...,
        height: _Optional[int] = ...,
    ) -> None: ...

class CheckTransactionRequest(_message.Message):
    __slots__ = ("tx",)
    TX_FIELD_NUMBER: _ClassVar[int]
    tx: _transaction_pb2.Transaction
    def __init__(
        self, tx: _Optional[_Union[_transaction_pb2.Transaction, _Mapping]] = ...
    ) -> None: ...

class CheckTransactionResponse(_message.Message):
    __slots__ = ("success", "code", "gas_wanted", "gas_used", "data", "log", "info")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    GAS_WANTED_FIELD_NUMBER: _ClassVar[int]
    GAS_USED_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    success: bool
    code: int
    gas_wanted: int
    gas_used: int
    data: str
    log: str
    info: str
    def __init__(
        self,
        success: bool = ...,
        code: _Optional[int] = ...,
        gas_wanted: _Optional[int] = ...,
        gas_used: _Optional[int] = ...,
        data: _Optional[str] = ...,
        log: _Optional[str] = ...,
        info: _Optional[str] = ...,
    ) -> None: ...

class SubmitRawTransactionRequest(_message.Message):
    __slots__ = ("tx", "type")

    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[SubmitRawTransactionRequest.Type]
        TYPE_ASYNC: _ClassVar[SubmitRawTransactionRequest.Type]
        TYPE_SYNC: _ClassVar[SubmitRawTransactionRequest.Type]
        TYPE_COMMIT: _ClassVar[SubmitRawTransactionRequest.Type]

    TYPE_UNSPECIFIED: SubmitRawTransactionRequest.Type
    TYPE_ASYNC: SubmitRawTransactionRequest.Type
    TYPE_SYNC: SubmitRawTransactionRequest.Type
    TYPE_COMMIT: SubmitRawTransactionRequest.Type
    TX_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    tx: bytes
    type: SubmitRawTransactionRequest.Type
    def __init__(
        self,
        tx: _Optional[bytes] = ...,
        type: _Optional[_Union[SubmitRawTransactionRequest.Type, str]] = ...,
    ) -> None: ...

class SubmitRawTransactionResponse(_message.Message):
    __slots__ = ("success", "tx_hash", "code", "data", "log", "height")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    tx_hash: str
    code: int
    data: str
    log: str
    height: int
    def __init__(
        self,
        success: bool = ...,
        tx_hash: _Optional[str] = ...,
        code: _Optional[int] = ...,
        data: _Optional[str] = ...,
        log: _Optional[str] = ...,
        height: _Optional[int] = ...,
    ) -> None: ...

class CheckRawTransactionRequest(_message.Message):
    __slots__ = ("tx",)
    TX_FIELD_NUMBER: _ClassVar[int]
    tx: bytes
    def __init__(self, tx: _Optional[bytes] = ...) -> None: ...

class CheckRawTransactionResponse(_message.Message):
    __slots__ = ("success", "code", "gas_wanted", "gas_used", "data", "log", "info")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    GAS_WANTED_FIELD_NUMBER: _ClassVar[int]
    GAS_USED_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    success: bool
    code: int
    gas_wanted: int
    gas_used: int
    data: str
    log: str
    info: str
    def __init__(
        self,
        success: bool = ...,
        code: _Optional[int] = ...,
        gas_wanted: _Optional[int] = ...,
        gas_used: _Optional[int] = ...,
        data: _Optional[str] = ...,
        log: _Optional[str] = ...,
        info: _Optional[str] = ...,
    ) -> None: ...

class GetVegaTimeRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetVegaTimeResponse(_message.Message):
    __slots__ = ("timestamp",)
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    def __init__(self, timestamp: _Optional[int] = ...) -> None: ...

class ObserveEventBusRequest(_message.Message):
    __slots__ = ("type", "market_id", "party_id", "batch_size")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    type: _containers.RepeatedScalarFieldContainer[_events_pb2.BusEventType]
    market_id: str
    party_id: str
    batch_size: int
    def __init__(
        self,
        type: _Optional[_Iterable[_Union[_events_pb2.BusEventType, str]]] = ...,
        market_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        batch_size: _Optional[int] = ...,
    ) -> None: ...

class ObserveEventBusResponse(_message.Message):
    __slots__ = ("events",)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[_events_pb2.BusEvent]
    def __init__(
        self, events: _Optional[_Iterable[_Union[_events_pb2.BusEvent, _Mapping]]] = ...
    ) -> None: ...

class StatisticsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StatisticsResponse(_message.Message):
    __slots__ = ("statistics",)
    STATISTICS_FIELD_NUMBER: _ClassVar[int]
    statistics: Statistics
    def __init__(
        self, statistics: _Optional[_Union[Statistics, _Mapping]] = ...
    ) -> None: ...

class Statistics(_message.Message):
    __slots__ = (
        "block_height",
        "backlog_length",
        "total_peers",
        "genesis_time",
        "current_time",
        "vega_time",
        "status",
        "tx_per_block",
        "average_tx_bytes",
        "average_orders_per_block",
        "trades_per_second",
        "orders_per_second",
        "total_markets",
        "total_amend_order",
        "total_cancel_order",
        "total_create_order",
        "total_orders",
        "total_trades",
        "order_subscriptions",
        "trade_subscriptions",
        "candle_subscriptions",
        "market_depth_subscriptions",
        "positions_subscriptions",
        "account_subscriptions",
        "market_data_subscriptions",
        "app_version_hash",
        "app_version",
        "chain_version",
        "block_duration",
        "uptime",
        "chain_id",
        "market_depth_updates_subscriptions",
        "block_hash",
        "epoch_seq",
        "epoch_start_time",
        "epoch_expiry_time",
        "event_count",
        "events_per_second",
    )
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BACKLOG_LENGTH_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PEERS_FIELD_NUMBER: _ClassVar[int]
    GENESIS_TIME_FIELD_NUMBER: _ClassVar[int]
    CURRENT_TIME_FIELD_NUMBER: _ClassVar[int]
    VEGA_TIME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TX_PER_BLOCK_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_TX_BYTES_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_ORDERS_PER_BLOCK_FIELD_NUMBER: _ClassVar[int]
    TRADES_PER_SECOND_FIELD_NUMBER: _ClassVar[int]
    ORDERS_PER_SECOND_FIELD_NUMBER: _ClassVar[int]
    TOTAL_MARKETS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_AMEND_ORDER_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CANCEL_ORDER_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CREATE_ORDER_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ORDERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TRADES_FIELD_NUMBER: _ClassVar[int]
    ORDER_SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    TRADE_SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    CANDLE_SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    MARKET_DEPTH_SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    POSITIONS_SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    MARKET_DATA_SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    APP_VERSION_HASH_FIELD_NUMBER: _ClassVar[int]
    APP_VERSION_FIELD_NUMBER: _ClassVar[int]
    CHAIN_VERSION_FIELD_NUMBER: _ClassVar[int]
    BLOCK_DURATION_FIELD_NUMBER: _ClassVar[int]
    UPTIME_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_DEPTH_UPDATES_SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HASH_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    EPOCH_START_TIME_FIELD_NUMBER: _ClassVar[int]
    EPOCH_EXPIRY_TIME_FIELD_NUMBER: _ClassVar[int]
    EVENT_COUNT_FIELD_NUMBER: _ClassVar[int]
    EVENTS_PER_SECOND_FIELD_NUMBER: _ClassVar[int]
    block_height: int
    backlog_length: int
    total_peers: int
    genesis_time: str
    current_time: str
    vega_time: str
    status: _vega_pb2.ChainStatus
    tx_per_block: int
    average_tx_bytes: int
    average_orders_per_block: int
    trades_per_second: int
    orders_per_second: int
    total_markets: int
    total_amend_order: int
    total_cancel_order: int
    total_create_order: int
    total_orders: int
    total_trades: int
    order_subscriptions: int
    trade_subscriptions: int
    candle_subscriptions: int
    market_depth_subscriptions: int
    positions_subscriptions: int
    account_subscriptions: int
    market_data_subscriptions: int
    app_version_hash: str
    app_version: str
    chain_version: str
    block_duration: int
    uptime: str
    chain_id: str
    market_depth_updates_subscriptions: int
    block_hash: str
    epoch_seq: int
    epoch_start_time: str
    epoch_expiry_time: str
    event_count: int
    events_per_second: int
    def __init__(
        self,
        block_height: _Optional[int] = ...,
        backlog_length: _Optional[int] = ...,
        total_peers: _Optional[int] = ...,
        genesis_time: _Optional[str] = ...,
        current_time: _Optional[str] = ...,
        vega_time: _Optional[str] = ...,
        status: _Optional[_Union[_vega_pb2.ChainStatus, str]] = ...,
        tx_per_block: _Optional[int] = ...,
        average_tx_bytes: _Optional[int] = ...,
        average_orders_per_block: _Optional[int] = ...,
        trades_per_second: _Optional[int] = ...,
        orders_per_second: _Optional[int] = ...,
        total_markets: _Optional[int] = ...,
        total_amend_order: _Optional[int] = ...,
        total_cancel_order: _Optional[int] = ...,
        total_create_order: _Optional[int] = ...,
        total_orders: _Optional[int] = ...,
        total_trades: _Optional[int] = ...,
        order_subscriptions: _Optional[int] = ...,
        trade_subscriptions: _Optional[int] = ...,
        candle_subscriptions: _Optional[int] = ...,
        market_depth_subscriptions: _Optional[int] = ...,
        positions_subscriptions: _Optional[int] = ...,
        account_subscriptions: _Optional[int] = ...,
        market_data_subscriptions: _Optional[int] = ...,
        app_version_hash: _Optional[str] = ...,
        app_version: _Optional[str] = ...,
        chain_version: _Optional[str] = ...,
        block_duration: _Optional[int] = ...,
        uptime: _Optional[str] = ...,
        chain_id: _Optional[str] = ...,
        market_depth_updates_subscriptions: _Optional[int] = ...,
        block_hash: _Optional[str] = ...,
        epoch_seq: _Optional[int] = ...,
        epoch_start_time: _Optional[str] = ...,
        epoch_expiry_time: _Optional[str] = ...,
        event_count: _Optional[int] = ...,
        events_per_second: _Optional[int] = ...,
    ) -> None: ...

class LastBlockHeightRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LastBlockHeightResponse(_message.Message):
    __slots__ = (
        "height",
        "hash",
        "spam_pow_hash_function",
        "spam_pow_difficulty",
        "spam_pow_number_of_past_blocks",
        "spam_pow_number_of_tx_per_block",
        "spam_pow_increasing_difficulty",
        "chain_id",
    )
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    SPAM_POW_HASH_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    SPAM_POW_DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    SPAM_POW_NUMBER_OF_PAST_BLOCKS_FIELD_NUMBER: _ClassVar[int]
    SPAM_POW_NUMBER_OF_TX_PER_BLOCK_FIELD_NUMBER: _ClassVar[int]
    SPAM_POW_INCREASING_DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    height: int
    hash: str
    spam_pow_hash_function: str
    spam_pow_difficulty: int
    spam_pow_number_of_past_blocks: int
    spam_pow_number_of_tx_per_block: int
    spam_pow_increasing_difficulty: bool
    chain_id: str
    def __init__(
        self,
        height: _Optional[int] = ...,
        hash: _Optional[str] = ...,
        spam_pow_hash_function: _Optional[str] = ...,
        spam_pow_difficulty: _Optional[int] = ...,
        spam_pow_number_of_past_blocks: _Optional[int] = ...,
        spam_pow_number_of_tx_per_block: _Optional[int] = ...,
        spam_pow_increasing_difficulty: bool = ...,
        chain_id: _Optional[str] = ...,
    ) -> None: ...

class GetSpamStatisticsRequest(_message.Message):
    __slots__ = ("party_id",)
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    def __init__(self, party_id: _Optional[str] = ...) -> None: ...

class SpamStatistic(_message.Message):
    __slots__ = (
        "count_for_epoch",
        "max_for_epoch",
        "banned_until",
        "min_tokens_required",
    )
    COUNT_FOR_EPOCH_FIELD_NUMBER: _ClassVar[int]
    MAX_FOR_EPOCH_FIELD_NUMBER: _ClassVar[int]
    BANNED_UNTIL_FIELD_NUMBER: _ClassVar[int]
    MIN_TOKENS_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    count_for_epoch: int
    max_for_epoch: int
    banned_until: str
    min_tokens_required: str
    def __init__(
        self,
        count_for_epoch: _Optional[int] = ...,
        max_for_epoch: _Optional[int] = ...,
        banned_until: _Optional[str] = ...,
        min_tokens_required: _Optional[str] = ...,
    ) -> None: ...

class VoteSpamStatistics(_message.Message):
    __slots__ = ("statistics", "max_for_epoch", "banned_until")
    STATISTICS_FIELD_NUMBER: _ClassVar[int]
    MAX_FOR_EPOCH_FIELD_NUMBER: _ClassVar[int]
    BANNED_UNTIL_FIELD_NUMBER: _ClassVar[int]
    statistics: _containers.RepeatedCompositeFieldContainer[VoteSpamStatistic]
    max_for_epoch: int
    banned_until: str
    def __init__(
        self,
        statistics: _Optional[_Iterable[_Union[VoteSpamStatistic, _Mapping]]] = ...,
        max_for_epoch: _Optional[int] = ...,
        banned_until: _Optional[str] = ...,
    ) -> None: ...

class VoteSpamStatistic(_message.Message):
    __slots__ = ("proposal", "count_for_epoch", "min_tokens_required")
    PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    COUNT_FOR_EPOCH_FIELD_NUMBER: _ClassVar[int]
    MIN_TOKENS_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    proposal: str
    count_for_epoch: int
    min_tokens_required: str
    def __init__(
        self,
        proposal: _Optional[str] = ...,
        count_for_epoch: _Optional[int] = ...,
        min_tokens_required: _Optional[str] = ...,
    ) -> None: ...

class PoWBlockState(_message.Message):
    __slots__ = (
        "block_height",
        "block_hash",
        "transactions_seen",
        "expected_difficulty",
        "hash_function",
        "difficulty",
        "tx_per_block",
        "increasing_difficulty",
    )
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HASH_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONS_SEEN_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    HASH_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    TX_PER_BLOCK_FIELD_NUMBER: _ClassVar[int]
    INCREASING_DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    block_height: int
    block_hash: str
    transactions_seen: int
    expected_difficulty: int
    hash_function: str
    difficulty: int
    tx_per_block: int
    increasing_difficulty: bool
    def __init__(
        self,
        block_height: _Optional[int] = ...,
        block_hash: _Optional[str] = ...,
        transactions_seen: _Optional[int] = ...,
        expected_difficulty: _Optional[int] = ...,
        hash_function: _Optional[str] = ...,
        difficulty: _Optional[int] = ...,
        tx_per_block: _Optional[int] = ...,
        increasing_difficulty: bool = ...,
    ) -> None: ...

class PoWStatistic(_message.Message):
    __slots__ = ("block_states", "banned_until", "number_of_past_blocks")
    BLOCK_STATES_FIELD_NUMBER: _ClassVar[int]
    BANNED_UNTIL_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_PAST_BLOCKS_FIELD_NUMBER: _ClassVar[int]
    block_states: _containers.RepeatedCompositeFieldContainer[PoWBlockState]
    banned_until: str
    number_of_past_blocks: int
    def __init__(
        self,
        block_states: _Optional[_Iterable[_Union[PoWBlockState, _Mapping]]] = ...,
        banned_until: _Optional[str] = ...,
        number_of_past_blocks: _Optional[int] = ...,
    ) -> None: ...

class SpamStatistics(_message.Message):
    __slots__ = (
        "proposals",
        "delegations",
        "transfers",
        "node_announcements",
        "votes",
        "pow",
        "issue_signatures",
        "epoch_seq",
        "create_referral_set",
        "update_referral_set",
        "apply_referral_code",
    )
    PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    DELEGATIONS_FIELD_NUMBER: _ClassVar[int]
    TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    NODE_ANNOUNCEMENTS_FIELD_NUMBER: _ClassVar[int]
    VOTES_FIELD_NUMBER: _ClassVar[int]
    POW_FIELD_NUMBER: _ClassVar[int]
    ISSUE_SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    CREATE_REFERRAL_SET_FIELD_NUMBER: _ClassVar[int]
    UPDATE_REFERRAL_SET_FIELD_NUMBER: _ClassVar[int]
    APPLY_REFERRAL_CODE_FIELD_NUMBER: _ClassVar[int]
    proposals: SpamStatistic
    delegations: SpamStatistic
    transfers: SpamStatistic
    node_announcements: SpamStatistic
    votes: VoteSpamStatistics
    pow: PoWStatistic
    issue_signatures: SpamStatistic
    epoch_seq: int
    create_referral_set: SpamStatistic
    update_referral_set: SpamStatistic
    apply_referral_code: SpamStatistic
    def __init__(
        self,
        proposals: _Optional[_Union[SpamStatistic, _Mapping]] = ...,
        delegations: _Optional[_Union[SpamStatistic, _Mapping]] = ...,
        transfers: _Optional[_Union[SpamStatistic, _Mapping]] = ...,
        node_announcements: _Optional[_Union[SpamStatistic, _Mapping]] = ...,
        votes: _Optional[_Union[VoteSpamStatistics, _Mapping]] = ...,
        pow: _Optional[_Union[PoWStatistic, _Mapping]] = ...,
        issue_signatures: _Optional[_Union[SpamStatistic, _Mapping]] = ...,
        epoch_seq: _Optional[int] = ...,
        create_referral_set: _Optional[_Union[SpamStatistic, _Mapping]] = ...,
        update_referral_set: _Optional[_Union[SpamStatistic, _Mapping]] = ...,
        apply_referral_code: _Optional[_Union[SpamStatistic, _Mapping]] = ...,
    ) -> None: ...

class GetSpamStatisticsResponse(_message.Message):
    __slots__ = ("chain_id", "statistics")
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    STATISTICS_FIELD_NUMBER: _ClassVar[int]
    chain_id: str
    statistics: SpamStatistics
    def __init__(
        self,
        chain_id: _Optional[str] = ...,
        statistics: _Optional[_Union[SpamStatistics, _Mapping]] = ...,
    ) -> None: ...
