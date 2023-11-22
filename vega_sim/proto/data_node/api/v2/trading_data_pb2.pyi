from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.api import httpbody_pb2 as _httpbody_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2
from vega import assets_pb2 as _assets_pb2
from vega.commands.v1 import validator_commands_pb2 as _validator_commands_pb2
from vega.events.v1 import events_pb2 as _events_pb2
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

class LedgerEntryField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LEDGER_ENTRY_FIELD_UNSPECIFIED: _ClassVar[LedgerEntryField]
    LEDGER_ENTRY_FIELD_ACCOUNT_FROM_ID: _ClassVar[LedgerEntryField]
    LEDGER_ENTRY_FIELD_ACCOUNT_TO_ID: _ClassVar[LedgerEntryField]
    LEDGER_ENTRY_FIELD_TRANSFER_TYPE: _ClassVar[LedgerEntryField]

class AccountField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACCOUNT_FIELD_UNSPECIFIED: _ClassVar[AccountField]
    ACCOUNT_FIELD_ID: _ClassVar[AccountField]
    ACCOUNT_FIELD_PARTY_ID: _ClassVar[AccountField]
    ACCOUNT_FIELD_ASSET_ID: _ClassVar[AccountField]
    ACCOUNT_FIELD_MARKET_ID: _ClassVar[AccountField]
    ACCOUNT_FIELD_TYPE: _ClassVar[AccountField]

class TransferDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRANSFER_DIRECTION_UNSPECIFIED: _ClassVar[TransferDirection]
    TRANSFER_DIRECTION_TRANSFER_FROM: _ClassVar[TransferDirection]
    TRANSFER_DIRECTION_TRANSFER_TO: _ClassVar[TransferDirection]
    TRANSFER_DIRECTION_TRANSFER_TO_OR_FROM: _ClassVar[TransferDirection]

class Table(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TABLE_UNSPECIFIED: _ClassVar[Table]
    TABLE_BALANCES: _ClassVar[Table]
    TABLE_CHECKPOINTS: _ClassVar[Table]
    TABLE_DELEGATIONS: _ClassVar[Table]
    TABLE_LEDGER: _ClassVar[Table]
    TABLE_ORDERS: _ClassVar[Table]
    TABLE_TRADES: _ClassVar[Table]
    TABLE_MARKET_DATA: _ClassVar[Table]
    TABLE_MARGIN_LEVELS: _ClassVar[Table]
    TABLE_POSITIONS: _ClassVar[Table]
    TABLE_LIQUIDITY_PROVISIONS: _ClassVar[Table]
    TABLE_MARKETS: _ClassVar[Table]
    TABLE_DEPOSITS: _ClassVar[Table]
    TABLE_WITHDRAWALS: _ClassVar[Table]
    TABLE_BLOCKS: _ClassVar[Table]
    TABLE_REWARDS: _ClassVar[Table]

LEDGER_ENTRY_FIELD_UNSPECIFIED: LedgerEntryField
LEDGER_ENTRY_FIELD_ACCOUNT_FROM_ID: LedgerEntryField
LEDGER_ENTRY_FIELD_ACCOUNT_TO_ID: LedgerEntryField
LEDGER_ENTRY_FIELD_TRANSFER_TYPE: LedgerEntryField
ACCOUNT_FIELD_UNSPECIFIED: AccountField
ACCOUNT_FIELD_ID: AccountField
ACCOUNT_FIELD_PARTY_ID: AccountField
ACCOUNT_FIELD_ASSET_ID: AccountField
ACCOUNT_FIELD_MARKET_ID: AccountField
ACCOUNT_FIELD_TYPE: AccountField
TRANSFER_DIRECTION_UNSPECIFIED: TransferDirection
TRANSFER_DIRECTION_TRANSFER_FROM: TransferDirection
TRANSFER_DIRECTION_TRANSFER_TO: TransferDirection
TRANSFER_DIRECTION_TRANSFER_TO_OR_FROM: TransferDirection
TABLE_UNSPECIFIED: Table
TABLE_BALANCES: Table
TABLE_CHECKPOINTS: Table
TABLE_DELEGATIONS: Table
TABLE_LEDGER: Table
TABLE_ORDERS: Table
TABLE_TRADES: Table
TABLE_MARKET_DATA: Table
TABLE_MARGIN_LEVELS: Table
TABLE_POSITIONS: Table
TABLE_LIQUIDITY_PROVISIONS: Table
TABLE_MARKETS: Table
TABLE_DEPOSITS: Table
TABLE_WITHDRAWALS: Table
TABLE_BLOCKS: Table
TABLE_REWARDS: Table

class Pagination(_message.Message):
    __slots__ = ("first", "after", "last", "before", "newest_first")
    FIRST_FIELD_NUMBER: _ClassVar[int]
    AFTER_FIELD_NUMBER: _ClassVar[int]
    LAST_FIELD_NUMBER: _ClassVar[int]
    BEFORE_FIELD_NUMBER: _ClassVar[int]
    NEWEST_FIRST_FIELD_NUMBER: _ClassVar[int]
    first: int
    after: str
    last: int
    before: str
    newest_first: bool
    def __init__(
        self,
        first: _Optional[int] = ...,
        after: _Optional[str] = ...,
        last: _Optional[int] = ...,
        before: _Optional[str] = ...,
        newest_first: bool = ...,
    ) -> None: ...

class PageInfo(_message.Message):
    __slots__ = ("has_next_page", "has_previous_page", "start_cursor", "end_cursor")
    HAS_NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    HAS_PREVIOUS_PAGE_FIELD_NUMBER: _ClassVar[int]
    START_CURSOR_FIELD_NUMBER: _ClassVar[int]
    END_CURSOR_FIELD_NUMBER: _ClassVar[int]
    has_next_page: bool
    has_previous_page: bool
    start_cursor: str
    end_cursor: str
    def __init__(
        self,
        has_next_page: bool = ...,
        has_previous_page: bool = ...,
        start_cursor: _Optional[str] = ...,
        end_cursor: _Optional[str] = ...,
    ) -> None: ...

class GetPartyVestingStatsRequest(_message.Message):
    __slots__ = ("party_id",)
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    def __init__(self, party_id: _Optional[str] = ...) -> None: ...

class GetPartyVestingStatsResponse(_message.Message):
    __slots__ = ("party_id", "reward_bonus_multiplier", "epoch_seq", "quantum_balance")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    REWARD_BONUS_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    QUANTUM_BALANCE_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    reward_bonus_multiplier: str
    epoch_seq: int
    quantum_balance: str
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        reward_bonus_multiplier: _Optional[str] = ...,
        epoch_seq: _Optional[int] = ...,
        quantum_balance: _Optional[str] = ...,
    ) -> None: ...

class GetVestingBalancesSummaryRequest(_message.Message):
    __slots__ = ("party_id", "asset_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    asset_id: str
    def __init__(
        self, party_id: _Optional[str] = ..., asset_id: _Optional[str] = ...
    ) -> None: ...

class GetVestingBalancesSummaryResponse(_message.Message):
    __slots__ = ("party_id", "epoch_seq", "locked_balances", "vesting_balances")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    LOCKED_BALANCES_FIELD_NUMBER: _ClassVar[int]
    VESTING_BALANCES_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    epoch_seq: int
    locked_balances: _containers.RepeatedCompositeFieldContainer[
        _events_pb2.PartyLockedBalance
    ]
    vesting_balances: _containers.RepeatedCompositeFieldContainer[
        _events_pb2.PartyVestingBalance
    ]
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        epoch_seq: _Optional[int] = ...,
        locked_balances: _Optional[
            _Iterable[_Union[_events_pb2.PartyLockedBalance, _Mapping]]
        ] = ...,
        vesting_balances: _Optional[
            _Iterable[_Union[_events_pb2.PartyVestingBalance, _Mapping]]
        ] = ...,
    ) -> None: ...

class AccountBalance(_message.Message):
    __slots__ = ("owner", "balance", "asset", "market_id", "type")
    OWNER_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    owner: str
    balance: str
    asset: str
    market_id: str
    type: _vega_pb2.AccountType
    def __init__(
        self,
        owner: _Optional[str] = ...,
        balance: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
    ) -> None: ...

class ListAccountsRequest(_message.Message):
    __slots__ = ("filter", "pagination")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    filter: AccountFilter
    pagination: Pagination
    def __init__(
        self,
        filter: _Optional[_Union[AccountFilter, _Mapping]] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListAccountsResponse(_message.Message):
    __slots__ = ("accounts",)
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    accounts: AccountsConnection
    def __init__(
        self, accounts: _Optional[_Union[AccountsConnection, _Mapping]] = ...
    ) -> None: ...

class AccountsConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[AccountEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[AccountEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class AccountEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: AccountBalance
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[AccountBalance, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ObserveAccountsRequest(_message.Message):
    __slots__ = ("market_id", "party_id", "asset", "type")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    party_id: str
    asset: str
    type: _vega_pb2.AccountType
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
    ) -> None: ...

class ObserveAccountsResponse(_message.Message):
    __slots__ = ("snapshot", "updates")
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    snapshot: AccountSnapshotPage
    updates: AccountUpdates
    def __init__(
        self,
        snapshot: _Optional[_Union[AccountSnapshotPage, _Mapping]] = ...,
        updates: _Optional[_Union[AccountUpdates, _Mapping]] = ...,
    ) -> None: ...

class AccountSnapshotPage(_message.Message):
    __slots__ = ("accounts", "last_page")
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    accounts: _containers.RepeatedCompositeFieldContainer[AccountBalance]
    last_page: bool
    def __init__(
        self,
        accounts: _Optional[_Iterable[_Union[AccountBalance, _Mapping]]] = ...,
        last_page: bool = ...,
    ) -> None: ...

class AccountUpdates(_message.Message):
    __slots__ = ("accounts",)
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    accounts: _containers.RepeatedCompositeFieldContainer[AccountBalance]
    def __init__(
        self, accounts: _Optional[_Iterable[_Union[AccountBalance, _Mapping]]] = ...
    ) -> None: ...

class InfoRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class InfoResponse(_message.Message):
    __slots__ = ("version", "commit_hash")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    COMMIT_HASH_FIELD_NUMBER: _ClassVar[int]
    version: str
    commit_hash: str
    def __init__(
        self, version: _Optional[str] = ..., commit_hash: _Optional[str] = ...
    ) -> None: ...

class GetOrderRequest(_message.Message):
    __slots__ = ("order_id", "version")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    version: int
    def __init__(
        self, order_id: _Optional[str] = ..., version: _Optional[int] = ...
    ) -> None: ...

class GetOrderResponse(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: _vega_pb2.Order
    def __init__(
        self, order: _Optional[_Union[_vega_pb2.Order, _Mapping]] = ...
    ) -> None: ...

class OrderFilter(_message.Message):
    __slots__ = (
        "statuses",
        "types",
        "time_in_forces",
        "exclude_liquidity",
        "party_ids",
        "market_ids",
        "reference",
        "date_range",
        "live_only",
    )
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    TYPES_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCES_FIELD_NUMBER: _ClassVar[int]
    EXCLUDE_LIQUIDITY_FIELD_NUMBER: _ClassVar[int]
    PARTY_IDS_FIELD_NUMBER: _ClassVar[int]
    MARKET_IDS_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    LIVE_ONLY_FIELD_NUMBER: _ClassVar[int]
    statuses: _containers.RepeatedScalarFieldContainer[_vega_pb2.Order.Status]
    types: _containers.RepeatedScalarFieldContainer[_vega_pb2.Order.Type]
    time_in_forces: _containers.RepeatedScalarFieldContainer[
        _vega_pb2.Order.TimeInForce
    ]
    exclude_liquidity: bool
    party_ids: _containers.RepeatedScalarFieldContainer[str]
    market_ids: _containers.RepeatedScalarFieldContainer[str]
    reference: str
    date_range: DateRange
    live_only: bool
    def __init__(
        self,
        statuses: _Optional[_Iterable[_Union[_vega_pb2.Order.Status, str]]] = ...,
        types: _Optional[_Iterable[_Union[_vega_pb2.Order.Type, str]]] = ...,
        time_in_forces: _Optional[
            _Iterable[_Union[_vega_pb2.Order.TimeInForce, str]]
        ] = ...,
        exclude_liquidity: bool = ...,
        party_ids: _Optional[_Iterable[str]] = ...,
        market_ids: _Optional[_Iterable[str]] = ...,
        reference: _Optional[str] = ...,
        date_range: _Optional[_Union[DateRange, _Mapping]] = ...,
        live_only: bool = ...,
    ) -> None: ...

class ListOrdersRequest(_message.Message):
    __slots__ = ("pagination", "filter")
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    pagination: Pagination
    filter: OrderFilter
    def __init__(
        self,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        filter: _Optional[_Union[OrderFilter, _Mapping]] = ...,
    ) -> None: ...

class ListOrdersResponse(_message.Message):
    __slots__ = ("orders",)
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    orders: OrderConnection
    def __init__(
        self, orders: _Optional[_Union[OrderConnection, _Mapping]] = ...
    ) -> None: ...

class ListOrderVersionsRequest(_message.Message):
    __slots__ = ("order_id", "pagination")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    pagination: Pagination
    def __init__(
        self,
        order_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListOrderVersionsResponse(_message.Message):
    __slots__ = ("orders",)
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    orders: OrderConnection
    def __init__(
        self, orders: _Optional[_Union[OrderConnection, _Mapping]] = ...
    ) -> None: ...

class ObserveOrdersRequest(_message.Message):
    __slots__ = ("market_ids", "party_ids", "exclude_liquidity")
    MARKET_IDS_FIELD_NUMBER: _ClassVar[int]
    PARTY_IDS_FIELD_NUMBER: _ClassVar[int]
    EXCLUDE_LIQUIDITY_FIELD_NUMBER: _ClassVar[int]
    market_ids: _containers.RepeatedScalarFieldContainer[str]
    party_ids: _containers.RepeatedScalarFieldContainer[str]
    exclude_liquidity: bool
    def __init__(
        self,
        market_ids: _Optional[_Iterable[str]] = ...,
        party_ids: _Optional[_Iterable[str]] = ...,
        exclude_liquidity: bool = ...,
    ) -> None: ...

class ObserveOrdersResponse(_message.Message):
    __slots__ = ("snapshot", "updates")
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    snapshot: OrderSnapshotPage
    updates: OrderUpdates
    def __init__(
        self,
        snapshot: _Optional[_Union[OrderSnapshotPage, _Mapping]] = ...,
        updates: _Optional[_Union[OrderUpdates, _Mapping]] = ...,
    ) -> None: ...

class OrderSnapshotPage(_message.Message):
    __slots__ = ("orders", "last_page")
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    orders: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Order]
    last_page: bool
    def __init__(
        self,
        orders: _Optional[_Iterable[_Union[_vega_pb2.Order, _Mapping]]] = ...,
        last_page: bool = ...,
    ) -> None: ...

class OrderUpdates(_message.Message):
    __slots__ = ("orders",)
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    orders: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Order]
    def __init__(
        self, orders: _Optional[_Iterable[_Union[_vega_pb2.Order, _Mapping]]] = ...
    ) -> None: ...

class GetStopOrderRequest(_message.Message):
    __slots__ = ("order_id",)
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    def __init__(self, order_id: _Optional[str] = ...) -> None: ...

class GetStopOrderResponse(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: _events_pb2.StopOrderEvent
    def __init__(
        self, order: _Optional[_Union[_events_pb2.StopOrderEvent, _Mapping]] = ...
    ) -> None: ...

class ListStopOrdersRequest(_message.Message):
    __slots__ = ("pagination", "filter")
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    pagination: Pagination
    filter: StopOrderFilter
    def __init__(
        self,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        filter: _Optional[_Union[StopOrderFilter, _Mapping]] = ...,
    ) -> None: ...

class StopOrderFilter(_message.Message):
    __slots__ = (
        "statuses",
        "expiry_strategies",
        "date_range",
        "party_ids",
        "market_ids",
        "live_only",
    )
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_STRATEGIES_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    PARTY_IDS_FIELD_NUMBER: _ClassVar[int]
    MARKET_IDS_FIELD_NUMBER: _ClassVar[int]
    LIVE_ONLY_FIELD_NUMBER: _ClassVar[int]
    statuses: _containers.RepeatedScalarFieldContainer[_vega_pb2.StopOrder.Status]
    expiry_strategies: _containers.RepeatedScalarFieldContainer[
        _vega_pb2.StopOrder.ExpiryStrategy
    ]
    date_range: DateRange
    party_ids: _containers.RepeatedScalarFieldContainer[str]
    market_ids: _containers.RepeatedScalarFieldContainer[str]
    live_only: bool
    def __init__(
        self,
        statuses: _Optional[_Iterable[_Union[_vega_pb2.StopOrder.Status, str]]] = ...,
        expiry_strategies: _Optional[
            _Iterable[_Union[_vega_pb2.StopOrder.ExpiryStrategy, str]]
        ] = ...,
        date_range: _Optional[_Union[DateRange, _Mapping]] = ...,
        party_ids: _Optional[_Iterable[str]] = ...,
        market_ids: _Optional[_Iterable[str]] = ...,
        live_only: bool = ...,
    ) -> None: ...

class StopOrderEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _events_pb2.StopOrderEvent
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_events_pb2.StopOrderEvent, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class StopOrderConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[StopOrderEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[StopOrderEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListStopOrdersResponse(_message.Message):
    __slots__ = ("orders",)
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    orders: StopOrderConnection
    def __init__(
        self, orders: _Optional[_Union[StopOrderConnection, _Mapping]] = ...
    ) -> None: ...

class ListPositionsRequest(_message.Message):
    __slots__ = ("party_id", "market_id", "pagination")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    market_id: str
    pagination: Pagination
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListPositionsResponse(_message.Message):
    __slots__ = ("positions",)
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    positions: PositionConnection
    def __init__(
        self, positions: _Optional[_Union[PositionConnection, _Mapping]] = ...
    ) -> None: ...

class PositionsFilter(_message.Message):
    __slots__ = ("party_ids", "market_ids")
    PARTY_IDS_FIELD_NUMBER: _ClassVar[int]
    MARKET_IDS_FIELD_NUMBER: _ClassVar[int]
    party_ids: _containers.RepeatedScalarFieldContainer[str]
    market_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        party_ids: _Optional[_Iterable[str]] = ...,
        market_ids: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class ListAllPositionsRequest(_message.Message):
    __slots__ = ("filter", "pagination")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    filter: PositionsFilter
    pagination: Pagination
    def __init__(
        self,
        filter: _Optional[_Union[PositionsFilter, _Mapping]] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListAllPositionsResponse(_message.Message):
    __slots__ = ("positions",)
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    positions: PositionConnection
    def __init__(
        self, positions: _Optional[_Union[PositionConnection, _Mapping]] = ...
    ) -> None: ...

class PositionEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.Position
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.Position, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class PositionConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[PositionEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[PositionEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ObservePositionsRequest(_message.Message):
    __slots__ = ("party_id", "market_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    market_id: str
    def __init__(
        self, party_id: _Optional[str] = ..., market_id: _Optional[str] = ...
    ) -> None: ...

class ObservePositionsResponse(_message.Message):
    __slots__ = ("snapshot", "updates")
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    snapshot: PositionSnapshotPage
    updates: PositionUpdates
    def __init__(
        self,
        snapshot: _Optional[_Union[PositionSnapshotPage, _Mapping]] = ...,
        updates: _Optional[_Union[PositionUpdates, _Mapping]] = ...,
    ) -> None: ...

class PositionSnapshotPage(_message.Message):
    __slots__ = ("positions", "last_page")
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    positions: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Position]
    last_page: bool
    def __init__(
        self,
        positions: _Optional[_Iterable[_Union[_vega_pb2.Position, _Mapping]]] = ...,
        last_page: bool = ...,
    ) -> None: ...

class PositionUpdates(_message.Message):
    __slots__ = ("positions",)
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    positions: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Position]
    def __init__(
        self,
        positions: _Optional[_Iterable[_Union[_vega_pb2.Position, _Mapping]]] = ...,
    ) -> None: ...

class LedgerEntryFilter(_message.Message):
    __slots__ = (
        "close_on_account_filters",
        "from_account_filter",
        "to_account_filter",
        "transfer_types",
        "transfer_id",
    )
    CLOSE_ON_ACCOUNT_FILTERS_FIELD_NUMBER: _ClassVar[int]
    FROM_ACCOUNT_FILTER_FIELD_NUMBER: _ClassVar[int]
    TO_ACCOUNT_FILTER_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_TYPES_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    close_on_account_filters: bool
    from_account_filter: AccountFilter
    to_account_filter: AccountFilter
    transfer_types: _containers.RepeatedScalarFieldContainer[_vega_pb2.TransferType]
    transfer_id: str
    def __init__(
        self,
        close_on_account_filters: bool = ...,
        from_account_filter: _Optional[_Union[AccountFilter, _Mapping]] = ...,
        to_account_filter: _Optional[_Union[AccountFilter, _Mapping]] = ...,
        transfer_types: _Optional[_Iterable[_Union[_vega_pb2.TransferType, str]]] = ...,
        transfer_id: _Optional[str] = ...,
    ) -> None: ...

class AggregatedLedgerEntry(_message.Message):
    __slots__ = (
        "timestamp",
        "quantity",
        "transfer_type",
        "asset_id",
        "from_account_type",
        "to_account_type",
        "from_account_party_id",
        "to_account_party_id",
        "from_account_market_id",
        "to_account_market_id",
        "from_account_balance",
        "to_account_balance",
    )
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_TYPE_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TO_ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    FROM_ACCOUNT_PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    TO_ACCOUNT_PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_ACCOUNT_MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    TO_ACCOUNT_MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_ACCOUNT_BALANCE_FIELD_NUMBER: _ClassVar[int]
    TO_ACCOUNT_BALANCE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    quantity: str
    transfer_type: _vega_pb2.TransferType
    asset_id: str
    from_account_type: _vega_pb2.AccountType
    to_account_type: _vega_pb2.AccountType
    from_account_party_id: str
    to_account_party_id: str
    from_account_market_id: str
    to_account_market_id: str
    from_account_balance: str
    to_account_balance: str
    def __init__(
        self,
        timestamp: _Optional[int] = ...,
        quantity: _Optional[str] = ...,
        transfer_type: _Optional[_Union[_vega_pb2.TransferType, str]] = ...,
        asset_id: _Optional[str] = ...,
        from_account_type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
        to_account_type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
        from_account_party_id: _Optional[str] = ...,
        to_account_party_id: _Optional[str] = ...,
        from_account_market_id: _Optional[str] = ...,
        to_account_market_id: _Optional[str] = ...,
        from_account_balance: _Optional[str] = ...,
        to_account_balance: _Optional[str] = ...,
    ) -> None: ...

class ListLedgerEntriesRequest(_message.Message):
    __slots__ = ("filter", "pagination", "date_range")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    filter: LedgerEntryFilter
    pagination: Pagination
    date_range: DateRange
    def __init__(
        self,
        filter: _Optional[_Union[LedgerEntryFilter, _Mapping]] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        date_range: _Optional[_Union[DateRange, _Mapping]] = ...,
    ) -> None: ...

class ExportLedgerEntriesRequest(_message.Message):
    __slots__ = ("party_id", "asset_id", "date_range")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    asset_id: str
    date_range: DateRange
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        asset_id: _Optional[str] = ...,
        date_range: _Optional[_Union[DateRange, _Mapping]] = ...,
    ) -> None: ...

class ListLedgerEntriesResponse(_message.Message):
    __slots__ = ("ledger_entries",)
    LEDGER_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    ledger_entries: AggregatedLedgerEntriesConnection
    def __init__(
        self,
        ledger_entries: _Optional[
            _Union[AggregatedLedgerEntriesConnection, _Mapping]
        ] = ...,
    ) -> None: ...

class AggregatedLedgerEntriesEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: AggregatedLedgerEntry
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[AggregatedLedgerEntry, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class AggregatedLedgerEntriesConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[AggregatedLedgerEntriesEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[
            _Iterable[_Union[AggregatedLedgerEntriesEdge, _Mapping]]
        ] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListBalanceChangesRequest(_message.Message):
    __slots__ = ("filter", "pagination", "date_range")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    filter: AccountFilter
    pagination: Pagination
    date_range: DateRange
    def __init__(
        self,
        filter: _Optional[_Union[AccountFilter, _Mapping]] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        date_range: _Optional[_Union[DateRange, _Mapping]] = ...,
    ) -> None: ...

class ListBalanceChangesResponse(_message.Message):
    __slots__ = ("balances",)
    BALANCES_FIELD_NUMBER: _ClassVar[int]
    balances: AggregatedBalanceConnection
    def __init__(
        self, balances: _Optional[_Union[AggregatedBalanceConnection, _Mapping]] = ...
    ) -> None: ...

class GetBalanceHistoryRequest(_message.Message):
    __slots__ = ("filter", "group_by", "pagination", "date_range")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    GROUP_BY_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    filter: AccountFilter
    group_by: _containers.RepeatedScalarFieldContainer[AccountField]
    pagination: Pagination
    date_range: DateRange
    def __init__(
        self,
        filter: _Optional[_Union[AccountFilter, _Mapping]] = ...,
        group_by: _Optional[_Iterable[_Union[AccountField, str]]] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        date_range: _Optional[_Union[DateRange, _Mapping]] = ...,
    ) -> None: ...

class GetBalanceHistoryResponse(_message.Message):
    __slots__ = ("balances",)
    BALANCES_FIELD_NUMBER: _ClassVar[int]
    balances: AggregatedBalanceConnection
    def __init__(
        self, balances: _Optional[_Union[AggregatedBalanceConnection, _Mapping]] = ...
    ) -> None: ...

class AggregatedBalanceEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: AggregatedBalance
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[AggregatedBalance, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class AggregatedBalanceConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[AggregatedBalanceEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[AggregatedBalanceEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class AccountFilter(_message.Message):
    __slots__ = ("asset_id", "party_ids", "market_ids", "account_types")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_IDS_FIELD_NUMBER: _ClassVar[int]
    MARKET_IDS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPES_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    party_ids: _containers.RepeatedScalarFieldContainer[str]
    market_ids: _containers.RepeatedScalarFieldContainer[str]
    account_types: _containers.RepeatedScalarFieldContainer[_vega_pb2.AccountType]
    def __init__(
        self,
        asset_id: _Optional[str] = ...,
        party_ids: _Optional[_Iterable[str]] = ...,
        market_ids: _Optional[_Iterable[str]] = ...,
        account_types: _Optional[_Iterable[_Union[_vega_pb2.AccountType, str]]] = ...,
    ) -> None: ...

class AggregatedBalance(_message.Message):
    __slots__ = (
        "timestamp",
        "balance",
        "party_id",
        "asset_id",
        "market_id",
        "account_type",
    )
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    balance: str
    party_id: str
    asset_id: str
    market_id: str
    account_type: _vega_pb2.AccountType
    def __init__(
        self,
        timestamp: _Optional[int] = ...,
        balance: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        asset_id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        account_type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
    ) -> None: ...

class ObserveMarketsDepthRequest(_message.Message):
    __slots__ = ("market_ids",)
    MARKET_IDS_FIELD_NUMBER: _ClassVar[int]
    market_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, market_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class ObserveMarketsDepthResponse(_message.Message):
    __slots__ = ("market_depth",)
    MARKET_DEPTH_FIELD_NUMBER: _ClassVar[int]
    market_depth: _containers.RepeatedCompositeFieldContainer[_vega_pb2.MarketDepth]
    def __init__(
        self,
        market_depth: _Optional[
            _Iterable[_Union[_vega_pb2.MarketDepth, _Mapping]]
        ] = ...,
    ) -> None: ...

class ObserveMarketsDepthUpdatesRequest(_message.Message):
    __slots__ = ("market_ids",)
    MARKET_IDS_FIELD_NUMBER: _ClassVar[int]
    market_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, market_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class ObserveMarketsDepthUpdatesResponse(_message.Message):
    __slots__ = ("update",)
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    update: _containers.RepeatedCompositeFieldContainer[_vega_pb2.MarketDepthUpdate]
    def __init__(
        self,
        update: _Optional[
            _Iterable[_Union[_vega_pb2.MarketDepthUpdate, _Mapping]]
        ] = ...,
    ) -> None: ...

class ObserveMarketsDataRequest(_message.Message):
    __slots__ = ("market_ids",)
    MARKET_IDS_FIELD_NUMBER: _ClassVar[int]
    market_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, market_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class ObserveMarketsDataResponse(_message.Message):
    __slots__ = ("market_data",)
    MARKET_DATA_FIELD_NUMBER: _ClassVar[int]
    market_data: _containers.RepeatedCompositeFieldContainer[_vega_pb2.MarketData]
    def __init__(
        self,
        market_data: _Optional[_Iterable[_Union[_vega_pb2.MarketData, _Mapping]]] = ...,
    ) -> None: ...

class GetLatestMarketDepthRequest(_message.Message):
    __slots__ = ("market_id", "max_depth")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_DEPTH_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    max_depth: int
    def __init__(
        self, market_id: _Optional[str] = ..., max_depth: _Optional[int] = ...
    ) -> None: ...

class GetLatestMarketDepthResponse(_message.Message):
    __slots__ = ("market_id", "buy", "sell", "last_trade", "sequence_number")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    BUY_FIELD_NUMBER: _ClassVar[int]
    SELL_FIELD_NUMBER: _ClassVar[int]
    LAST_TRADE_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    buy: _containers.RepeatedCompositeFieldContainer[_vega_pb2.PriceLevel]
    sell: _containers.RepeatedCompositeFieldContainer[_vega_pb2.PriceLevel]
    last_trade: _vega_pb2.Trade
    sequence_number: int
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        buy: _Optional[_Iterable[_Union[_vega_pb2.PriceLevel, _Mapping]]] = ...,
        sell: _Optional[_Iterable[_Union[_vega_pb2.PriceLevel, _Mapping]]] = ...,
        last_trade: _Optional[_Union[_vega_pb2.Trade, _Mapping]] = ...,
        sequence_number: _Optional[int] = ...,
    ) -> None: ...

class ListLatestMarketDataRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListLatestMarketDataResponse(_message.Message):
    __slots__ = ("markets_data",)
    MARKETS_DATA_FIELD_NUMBER: _ClassVar[int]
    markets_data: _containers.RepeatedCompositeFieldContainer[_vega_pb2.MarketData]
    def __init__(
        self,
        markets_data: _Optional[
            _Iterable[_Union[_vega_pb2.MarketData, _Mapping]]
        ] = ...,
    ) -> None: ...

class GetLatestMarketDataRequest(_message.Message):
    __slots__ = ("market_id",)
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    def __init__(self, market_id: _Optional[str] = ...) -> None: ...

class GetLatestMarketDataResponse(_message.Message):
    __slots__ = ("market_data",)
    MARKET_DATA_FIELD_NUMBER: _ClassVar[int]
    market_data: _vega_pb2.MarketData
    def __init__(
        self, market_data: _Optional[_Union[_vega_pb2.MarketData, _Mapping]] = ...
    ) -> None: ...

class GetMarketDataHistoryByIDRequest(_message.Message):
    __slots__ = ("market_id", "start_timestamp", "end_timestamp", "pagination")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    start_timestamp: int
    end_timestamp: int
    pagination: Pagination
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        start_timestamp: _Optional[int] = ...,
        end_timestamp: _Optional[int] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class GetMarketDataHistoryByIDResponse(_message.Message):
    __slots__ = ("market_data",)
    MARKET_DATA_FIELD_NUMBER: _ClassVar[int]
    market_data: MarketDataConnection
    def __init__(
        self, market_data: _Optional[_Union[MarketDataConnection, _Mapping]] = ...
    ) -> None: ...

class MarketDataEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.MarketData
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.MarketData, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class MarketDataConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[MarketDataEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[MarketDataEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListTransfersRequest(_message.Message):
    __slots__ = (
        "pubkey",
        "direction",
        "pagination",
        "is_reward",
        "from_epoch",
        "to_epoch",
        "status",
        "scope",
    )

    class Scope(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SCOPE_UNSPECIFIED: _ClassVar[ListTransfersRequest.Scope]
        SCOPE_INDIVIDUAL: _ClassVar[ListTransfersRequest.Scope]
        SCOPE_TEAM: _ClassVar[ListTransfersRequest.Scope]
    SCOPE_UNSPECIFIED: ListTransfersRequest.Scope
    SCOPE_INDIVIDUAL: ListTransfersRequest.Scope
    SCOPE_TEAM: ListTransfersRequest.Scope
    PUBKEY_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    IS_REWARD_FIELD_NUMBER: _ClassVar[int]
    FROM_EPOCH_FIELD_NUMBER: _ClassVar[int]
    TO_EPOCH_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    pubkey: str
    direction: TransferDirection
    pagination: Pagination
    is_reward: bool
    from_epoch: int
    to_epoch: int
    status: _events_pb2.Transfer.Status
    scope: ListTransfersRequest.Scope
    def __init__(
        self,
        pubkey: _Optional[str] = ...,
        direction: _Optional[_Union[TransferDirection, str]] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        is_reward: bool = ...,
        from_epoch: _Optional[int] = ...,
        to_epoch: _Optional[int] = ...,
        status: _Optional[_Union[_events_pb2.Transfer.Status, str]] = ...,
        scope: _Optional[_Union[ListTransfersRequest.Scope, str]] = ...,
    ) -> None: ...

class ListTransfersResponse(_message.Message):
    __slots__ = ("transfers",)
    TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    transfers: TransferConnection
    def __init__(
        self, transfers: _Optional[_Union[TransferConnection, _Mapping]] = ...
    ) -> None: ...

class TransferNode(_message.Message):
    __slots__ = ("transfer", "fees")
    TRANSFER_FIELD_NUMBER: _ClassVar[int]
    FEES_FIELD_NUMBER: _ClassVar[int]
    transfer: _events_pb2.Transfer
    fees: _containers.RepeatedCompositeFieldContainer[_events_pb2.TransferFees]
    def __init__(
        self,
        transfer: _Optional[_Union[_events_pb2.Transfer, _Mapping]] = ...,
        fees: _Optional[_Iterable[_Union[_events_pb2.TransferFees, _Mapping]]] = ...,
    ) -> None: ...

class TransferEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: TransferNode
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[TransferNode, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class TransferConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[TransferEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[TransferEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class GetTransferRequest(_message.Message):
    __slots__ = ("transfer_id",)
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    def __init__(self, transfer_id: _Optional[str] = ...) -> None: ...

class GetTransferResponse(_message.Message):
    __slots__ = ("transfer", "fees")
    TRANSFER_FIELD_NUMBER: _ClassVar[int]
    FEES_FIELD_NUMBER: _ClassVar[int]
    transfer: _events_pb2.Transfer
    fees: _containers.RepeatedCompositeFieldContainer[_events_pb2.TransferFees]
    def __init__(
        self,
        transfer: _Optional[_Union[_events_pb2.Transfer, _Mapping]] = ...,
        fees: _Optional[_Iterable[_Union[_events_pb2.TransferFees, _Mapping]]] = ...,
    ) -> None: ...

class GetNetworkLimitsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetNetworkLimitsResponse(_message.Message):
    __slots__ = ("limits",)
    LIMITS_FIELD_NUMBER: _ClassVar[int]
    limits: _vega_pb2.NetworkLimits
    def __init__(
        self, limits: _Optional[_Union[_vega_pb2.NetworkLimits, _Mapping]] = ...
    ) -> None: ...

class ListCandleIntervalsRequest(_message.Message):
    __slots__ = ("market_id",)
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    def __init__(self, market_id: _Optional[str] = ...) -> None: ...

class IntervalToCandleId(_message.Message):
    __slots__ = ("interval", "candle_id")
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    CANDLE_ID_FIELD_NUMBER: _ClassVar[int]
    interval: str
    candle_id: str
    def __init__(
        self, interval: _Optional[str] = ..., candle_id: _Optional[str] = ...
    ) -> None: ...

class ListCandleIntervalsResponse(_message.Message):
    __slots__ = ("interval_to_candle_id",)
    INTERVAL_TO_CANDLE_ID_FIELD_NUMBER: _ClassVar[int]
    interval_to_candle_id: _containers.RepeatedCompositeFieldContainer[
        IntervalToCandleId
    ]
    def __init__(
        self,
        interval_to_candle_id: _Optional[
            _Iterable[_Union[IntervalToCandleId, _Mapping]]
        ] = ...,
    ) -> None: ...

class Candle(_message.Message):
    __slots__ = (
        "start",
        "last_update",
        "high",
        "low",
        "open",
        "close",
        "volume",
        "notional",
    )
    START_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATE_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    NOTIONAL_FIELD_NUMBER: _ClassVar[int]
    start: int
    last_update: int
    high: str
    low: str
    open: str
    close: str
    volume: int
    notional: int
    def __init__(
        self,
        start: _Optional[int] = ...,
        last_update: _Optional[int] = ...,
        high: _Optional[str] = ...,
        low: _Optional[str] = ...,
        open: _Optional[str] = ...,
        close: _Optional[str] = ...,
        volume: _Optional[int] = ...,
        notional: _Optional[int] = ...,
    ) -> None: ...

class ObserveCandleDataRequest(_message.Message):
    __slots__ = ("candle_id",)
    CANDLE_ID_FIELD_NUMBER: _ClassVar[int]
    candle_id: str
    def __init__(self, candle_id: _Optional[str] = ...) -> None: ...

class ObserveCandleDataResponse(_message.Message):
    __slots__ = ("candle",)
    CANDLE_FIELD_NUMBER: _ClassVar[int]
    candle: Candle
    def __init__(self, candle: _Optional[_Union[Candle, _Mapping]] = ...) -> None: ...

class ListCandleDataRequest(_message.Message):
    __slots__ = ("candle_id", "from_timestamp", "to_timestamp", "pagination")
    CANDLE_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TO_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    candle_id: str
    from_timestamp: int
    to_timestamp: int
    pagination: Pagination
    def __init__(
        self,
        candle_id: _Optional[str] = ...,
        from_timestamp: _Optional[int] = ...,
        to_timestamp: _Optional[int] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListCandleDataResponse(_message.Message):
    __slots__ = ("candles",)
    CANDLES_FIELD_NUMBER: _ClassVar[int]
    candles: CandleDataConnection
    def __init__(
        self, candles: _Optional[_Union[CandleDataConnection, _Mapping]] = ...
    ) -> None: ...

class CandleEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: Candle
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[Candle, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class CandleDataConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[CandleEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[CandleEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListVotesRequest(_message.Message):
    __slots__ = ("party_id", "proposal_id", "pagination")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PROPOSAL_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    proposal_id: str
    pagination: Pagination
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        proposal_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListVotesResponse(_message.Message):
    __slots__ = ("votes",)
    VOTES_FIELD_NUMBER: _ClassVar[int]
    votes: VoteConnection
    def __init__(
        self, votes: _Optional[_Union[VoteConnection, _Mapping]] = ...
    ) -> None: ...

class VoteEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _governance_pb2.Vote
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_governance_pb2.Vote, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class VoteConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[VoteEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[VoteEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ObserveVotesRequest(_message.Message):
    __slots__ = ("party_id", "proposal_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PROPOSAL_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    proposal_id: str
    def __init__(
        self, party_id: _Optional[str] = ..., proposal_id: _Optional[str] = ...
    ) -> None: ...

class ObserveVotesResponse(_message.Message):
    __slots__ = ("vote",)
    VOTE_FIELD_NUMBER: _ClassVar[int]
    vote: _governance_pb2.Vote
    def __init__(
        self, vote: _Optional[_Union[_governance_pb2.Vote, _Mapping]] = ...
    ) -> None: ...

class ListERC20MultiSigSignerAddedBundlesRequest(_message.Message):
    __slots__ = ("node_id", "submitter", "epoch_seq", "pagination")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    submitter: str
    epoch_seq: str
    pagination: Pagination
    def __init__(
        self,
        node_id: _Optional[str] = ...,
        submitter: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListERC20MultiSigSignerAddedBundlesResponse(_message.Message):
    __slots__ = ("bundles",)
    BUNDLES_FIELD_NUMBER: _ClassVar[int]
    bundles: ERC20MultiSigSignerAddedConnection
    def __init__(
        self,
        bundles: _Optional[_Union[ERC20MultiSigSignerAddedConnection, _Mapping]] = ...,
    ) -> None: ...

class ERC20MultiSigSignerAddedEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _events_pb2.ERC20MultiSigSignerAdded
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_events_pb2.ERC20MultiSigSignerAdded, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ERC20MultiSigSignerAddedBundleEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: ERC20MultiSigSignerAddedBundle
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[ERC20MultiSigSignerAddedBundle, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ERC20MultiSigSignerAddedConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[
        ERC20MultiSigSignerAddedBundleEdge
    ]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[
            _Iterable[_Union[ERC20MultiSigSignerAddedBundleEdge, _Mapping]]
        ] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ERC20MultiSigSignerAddedBundle(_message.Message):
    __slots__ = (
        "new_signer",
        "submitter",
        "nonce",
        "timestamp",
        "signatures",
        "epoch_seq",
    )
    NEW_SIGNER_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    new_signer: str
    submitter: str
    nonce: str
    timestamp: int
    signatures: str
    epoch_seq: str
    def __init__(
        self,
        new_signer: _Optional[str] = ...,
        submitter: _Optional[str] = ...,
        nonce: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
        signatures: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
    ) -> None: ...

class ListERC20MultiSigSignerRemovedBundlesRequest(_message.Message):
    __slots__ = ("node_id", "submitter", "epoch_seq", "pagination")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    submitter: str
    epoch_seq: str
    pagination: Pagination
    def __init__(
        self,
        node_id: _Optional[str] = ...,
        submitter: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListERC20MultiSigSignerRemovedBundlesResponse(_message.Message):
    __slots__ = ("bundles",)
    BUNDLES_FIELD_NUMBER: _ClassVar[int]
    bundles: ERC20MultiSigSignerRemovedConnection
    def __init__(
        self,
        bundles: _Optional[
            _Union[ERC20MultiSigSignerRemovedConnection, _Mapping]
        ] = ...,
    ) -> None: ...

class ERC20MultiSigSignerRemovedEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _events_pb2.ERC20MultiSigSignerRemoved
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_events_pb2.ERC20MultiSigSignerRemoved, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ERC20MultiSigSignerRemovedBundleEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: ERC20MultiSigSignerRemovedBundle
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[ERC20MultiSigSignerRemovedBundle, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ERC20MultiSigSignerRemovedConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[
        ERC20MultiSigSignerRemovedBundleEdge
    ]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[
            _Iterable[_Union[ERC20MultiSigSignerRemovedBundleEdge, _Mapping]]
        ] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ERC20MultiSigSignerRemovedBundle(_message.Message):
    __slots__ = (
        "old_signer",
        "submitter",
        "nonce",
        "timestamp",
        "signatures",
        "epoch_seq",
    )
    OLD_SIGNER_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    old_signer: str
    submitter: str
    nonce: str
    timestamp: int
    signatures: str
    epoch_seq: str
    def __init__(
        self,
        old_signer: _Optional[str] = ...,
        submitter: _Optional[str] = ...,
        nonce: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
        signatures: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
    ) -> None: ...

class GetERC20ListAssetBundleRequest(_message.Message):
    __slots__ = ("asset_id",)
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    def __init__(self, asset_id: _Optional[str] = ...) -> None: ...

class GetERC20ListAssetBundleResponse(_message.Message):
    __slots__ = ("asset_source", "vega_asset_id", "nonce", "signatures")
    ASSET_SOURCE_FIELD_NUMBER: _ClassVar[int]
    VEGA_ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    asset_source: str
    vega_asset_id: str
    nonce: str
    signatures: str
    def __init__(
        self,
        asset_source: _Optional[str] = ...,
        vega_asset_id: _Optional[str] = ...,
        nonce: _Optional[str] = ...,
        signatures: _Optional[str] = ...,
    ) -> None: ...

class GetERC20SetAssetLimitsBundleRequest(_message.Message):
    __slots__ = ("proposal_id",)
    PROPOSAL_ID_FIELD_NUMBER: _ClassVar[int]
    proposal_id: str
    def __init__(self, proposal_id: _Optional[str] = ...) -> None: ...

class GetERC20SetAssetLimitsBundleResponse(_message.Message):
    __slots__ = (
        "asset_source",
        "vega_asset_id",
        "nonce",
        "lifetime_limit",
        "threshold",
        "signatures",
    )
    ASSET_SOURCE_FIELD_NUMBER: _ClassVar[int]
    VEGA_ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    LIFETIME_LIMIT_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    asset_source: str
    vega_asset_id: str
    nonce: str
    lifetime_limit: str
    threshold: str
    signatures: str
    def __init__(
        self,
        asset_source: _Optional[str] = ...,
        vega_asset_id: _Optional[str] = ...,
        nonce: _Optional[str] = ...,
        lifetime_limit: _Optional[str] = ...,
        threshold: _Optional[str] = ...,
        signatures: _Optional[str] = ...,
    ) -> None: ...

class GetERC20WithdrawalApprovalRequest(_message.Message):
    __slots__ = ("withdrawal_id",)
    WITHDRAWAL_ID_FIELD_NUMBER: _ClassVar[int]
    withdrawal_id: str
    def __init__(self, withdrawal_id: _Optional[str] = ...) -> None: ...

class GetERC20WithdrawalApprovalResponse(_message.Message):
    __slots__ = (
        "asset_source",
        "amount",
        "nonce",
        "signatures",
        "target_address",
        "creation",
    )
    ASSET_SOURCE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    TARGET_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CREATION_FIELD_NUMBER: _ClassVar[int]
    asset_source: str
    amount: str
    nonce: str
    signatures: str
    target_address: str
    creation: int
    def __init__(
        self,
        asset_source: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        nonce: _Optional[str] = ...,
        signatures: _Optional[str] = ...,
        target_address: _Optional[str] = ...,
        creation: _Optional[int] = ...,
    ) -> None: ...

class GetLastTradeRequest(_message.Message):
    __slots__ = ("market_id",)
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    def __init__(self, market_id: _Optional[str] = ...) -> None: ...

class GetLastTradeResponse(_message.Message):
    __slots__ = ("trade",)
    TRADE_FIELD_NUMBER: _ClassVar[int]
    trade: _vega_pb2.Trade
    def __init__(
        self, trade: _Optional[_Union[_vega_pb2.Trade, _Mapping]] = ...
    ) -> None: ...

class ListTradesRequest(_message.Message):
    __slots__ = ("market_ids", "order_ids", "party_ids", "pagination", "date_range")
    MARKET_IDS_FIELD_NUMBER: _ClassVar[int]
    ORDER_IDS_FIELD_NUMBER: _ClassVar[int]
    PARTY_IDS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    market_ids: _containers.RepeatedScalarFieldContainer[str]
    order_ids: _containers.RepeatedScalarFieldContainer[str]
    party_ids: _containers.RepeatedScalarFieldContainer[str]
    pagination: Pagination
    date_range: DateRange
    def __init__(
        self,
        market_ids: _Optional[_Iterable[str]] = ...,
        order_ids: _Optional[_Iterable[str]] = ...,
        party_ids: _Optional[_Iterable[str]] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        date_range: _Optional[_Union[DateRange, _Mapping]] = ...,
    ) -> None: ...

class ListTradesResponse(_message.Message):
    __slots__ = ("trades",)
    TRADES_FIELD_NUMBER: _ClassVar[int]
    trades: TradeConnection
    def __init__(
        self, trades: _Optional[_Union[TradeConnection, _Mapping]] = ...
    ) -> None: ...

class TradeConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[TradeEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[TradeEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class TradeEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.Trade
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.Trade, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ObserveTradesRequest(_message.Message):
    __slots__ = ("market_ids", "party_ids")
    MARKET_IDS_FIELD_NUMBER: _ClassVar[int]
    PARTY_IDS_FIELD_NUMBER: _ClassVar[int]
    market_ids: _containers.RepeatedScalarFieldContainer[str]
    party_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        market_ids: _Optional[_Iterable[str]] = ...,
        party_ids: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class ObserveTradesResponse(_message.Message):
    __slots__ = ("trades",)
    TRADES_FIELD_NUMBER: _ClassVar[int]
    trades: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Trade]
    def __init__(
        self, trades: _Optional[_Iterable[_Union[_vega_pb2.Trade, _Mapping]]] = ...
    ) -> None: ...

class GetOracleSpecRequest(_message.Message):
    __slots__ = ("oracle_spec_id",)
    ORACLE_SPEC_ID_FIELD_NUMBER: _ClassVar[int]
    oracle_spec_id: str
    def __init__(self, oracle_spec_id: _Optional[str] = ...) -> None: ...

class GetOracleSpecResponse(_message.Message):
    __slots__ = ("oracle_spec",)
    ORACLE_SPEC_FIELD_NUMBER: _ClassVar[int]
    oracle_spec: _oracle_pb2.OracleSpec
    def __init__(
        self, oracle_spec: _Optional[_Union[_oracle_pb2.OracleSpec, _Mapping]] = ...
    ) -> None: ...

class ListOracleSpecsRequest(_message.Message):
    __slots__ = ("pagination",)
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    pagination: Pagination
    def __init__(
        self, pagination: _Optional[_Union[Pagination, _Mapping]] = ...
    ) -> None: ...

class ListOracleSpecsResponse(_message.Message):
    __slots__ = ("oracle_specs",)
    ORACLE_SPECS_FIELD_NUMBER: _ClassVar[int]
    oracle_specs: OracleSpecsConnection
    def __init__(
        self, oracle_specs: _Optional[_Union[OracleSpecsConnection, _Mapping]] = ...
    ) -> None: ...

class ListOracleDataRequest(_message.Message):
    __slots__ = ("oracle_spec_id", "pagination")
    ORACLE_SPEC_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    oracle_spec_id: str
    pagination: Pagination
    def __init__(
        self,
        oracle_spec_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListOracleDataResponse(_message.Message):
    __slots__ = ("oracle_data",)
    ORACLE_DATA_FIELD_NUMBER: _ClassVar[int]
    oracle_data: OracleDataConnection
    def __init__(
        self, oracle_data: _Optional[_Union[OracleDataConnection, _Mapping]] = ...
    ) -> None: ...

class OracleSpecEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _oracle_pb2.OracleSpec
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_oracle_pb2.OracleSpec, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class OracleSpecsConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[OracleSpecEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[OracleSpecEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class OracleDataEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _oracle_pb2.OracleData
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_oracle_pb2.OracleData, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class OracleDataConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[OracleDataEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[OracleDataEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class GetMarketRequest(_message.Message):
    __slots__ = ("market_id",)
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    def __init__(self, market_id: _Optional[str] = ...) -> None: ...

class GetMarketResponse(_message.Message):
    __slots__ = ("market",)
    MARKET_FIELD_NUMBER: _ClassVar[int]
    market: _markets_pb2.Market
    def __init__(
        self, market: _Optional[_Union[_markets_pb2.Market, _Mapping]] = ...
    ) -> None: ...

class ListMarketsRequest(_message.Message):
    __slots__ = ("pagination", "include_settled")
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_SETTLED_FIELD_NUMBER: _ClassVar[int]
    pagination: Pagination
    include_settled: bool
    def __init__(
        self,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        include_settled: bool = ...,
    ) -> None: ...

class ListMarketsResponse(_message.Message):
    __slots__ = ("markets",)
    MARKETS_FIELD_NUMBER: _ClassVar[int]
    markets: MarketConnection
    def __init__(
        self, markets: _Optional[_Union[MarketConnection, _Mapping]] = ...
    ) -> None: ...

class MarketEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _markets_pb2.Market
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_markets_pb2.Market, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class MarketConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[MarketEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[MarketEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListSuccessorMarketsRequest(_message.Message):
    __slots__ = ("market_id", "include_full_history", "pagination")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_FULL_HISTORY_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    include_full_history: bool
    pagination: Pagination
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        include_full_history: bool = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class SuccessorMarket(_message.Message):
    __slots__ = ("market", "proposals")
    MARKET_FIELD_NUMBER: _ClassVar[int]
    PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    market: _markets_pb2.Market
    proposals: _containers.RepeatedCompositeFieldContainer[
        _governance_pb2.GovernanceData
    ]
    def __init__(
        self,
        market: _Optional[_Union[_markets_pb2.Market, _Mapping]] = ...,
        proposals: _Optional[
            _Iterable[_Union[_governance_pb2.GovernanceData, _Mapping]]
        ] = ...,
    ) -> None: ...

class SuccessorMarketEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: SuccessorMarket
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[SuccessorMarket, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class SuccessorMarketConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[SuccessorMarketEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[SuccessorMarketEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListSuccessorMarketsResponse(_message.Message):
    __slots__ = ("successor_markets",)
    SUCCESSOR_MARKETS_FIELD_NUMBER: _ClassVar[int]
    successor_markets: SuccessorMarketConnection
    def __init__(
        self,
        successor_markets: _Optional[_Union[SuccessorMarketConnection, _Mapping]] = ...,
    ) -> None: ...

class GetPartyRequest(_message.Message):
    __slots__ = ("party_id",)
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    def __init__(self, party_id: _Optional[str] = ...) -> None: ...

class GetPartyResponse(_message.Message):
    __slots__ = ("party",)
    PARTY_FIELD_NUMBER: _ClassVar[int]
    party: _vega_pb2.Party
    def __init__(
        self, party: _Optional[_Union[_vega_pb2.Party, _Mapping]] = ...
    ) -> None: ...

class ListPartiesRequest(_message.Message):
    __slots__ = ("party_id", "pagination")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    pagination: Pagination
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListPartiesResponse(_message.Message):
    __slots__ = ("parties",)
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    parties: PartyConnection
    def __init__(
        self, parties: _Optional[_Union[PartyConnection, _Mapping]] = ...
    ) -> None: ...

class PartyEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.Party
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.Party, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class PartyConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[PartyEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[PartyEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class OrderEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.Order
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.Order, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ListMarginLevelsRequest(_message.Message):
    __slots__ = ("party_id", "market_id", "pagination")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    market_id: str
    pagination: Pagination
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListMarginLevelsResponse(_message.Message):
    __slots__ = ("margin_levels",)
    MARGIN_LEVELS_FIELD_NUMBER: _ClassVar[int]
    margin_levels: MarginConnection
    def __init__(
        self, margin_levels: _Optional[_Union[MarginConnection, _Mapping]] = ...
    ) -> None: ...

class ObserveMarginLevelsRequest(_message.Message):
    __slots__ = ("party_id", "market_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    market_id: str
    def __init__(
        self, party_id: _Optional[str] = ..., market_id: _Optional[str] = ...
    ) -> None: ...

class ObserveMarginLevelsResponse(_message.Message):
    __slots__ = ("margin_levels",)
    MARGIN_LEVELS_FIELD_NUMBER: _ClassVar[int]
    margin_levels: _vega_pb2.MarginLevels
    def __init__(
        self, margin_levels: _Optional[_Union[_vega_pb2.MarginLevels, _Mapping]] = ...
    ) -> None: ...

class OrderConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[OrderEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[OrderEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class MarginEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.MarginLevels
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.MarginLevels, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class MarginConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[MarginEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[MarginEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListRewardsRequest(_message.Message):
    __slots__ = ("party_id", "asset_id", "pagination", "from_epoch", "to_epoch")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    FROM_EPOCH_FIELD_NUMBER: _ClassVar[int]
    TO_EPOCH_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    asset_id: str
    pagination: Pagination
    from_epoch: int
    to_epoch: int
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        asset_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        from_epoch: _Optional[int] = ...,
        to_epoch: _Optional[int] = ...,
    ) -> None: ...

class ListRewardsResponse(_message.Message):
    __slots__ = ("rewards",)
    REWARDS_FIELD_NUMBER: _ClassVar[int]
    rewards: RewardsConnection
    def __init__(
        self, rewards: _Optional[_Union[RewardsConnection, _Mapping]] = ...
    ) -> None: ...

class RewardEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.Reward
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.Reward, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class RewardsConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[RewardEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[RewardEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListRewardSummariesRequest(_message.Message):
    __slots__ = ("party_id", "asset_id", "pagination")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    asset_id: str
    pagination: Pagination
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        asset_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListRewardSummariesResponse(_message.Message):
    __slots__ = ("summaries",)
    SUMMARIES_FIELD_NUMBER: _ClassVar[int]
    summaries: _containers.RepeatedCompositeFieldContainer[_vega_pb2.RewardSummary]
    def __init__(
        self,
        summaries: _Optional[
            _Iterable[_Union[_vega_pb2.RewardSummary, _Mapping]]
        ] = ...,
    ) -> None: ...

class RewardSummaryFilter(_message.Message):
    __slots__ = ("asset_ids", "market_ids", "from_epoch", "to_epoch")
    ASSET_IDS_FIELD_NUMBER: _ClassVar[int]
    MARKET_IDS_FIELD_NUMBER: _ClassVar[int]
    FROM_EPOCH_FIELD_NUMBER: _ClassVar[int]
    TO_EPOCH_FIELD_NUMBER: _ClassVar[int]
    asset_ids: _containers.RepeatedScalarFieldContainer[str]
    market_ids: _containers.RepeatedScalarFieldContainer[str]
    from_epoch: int
    to_epoch: int
    def __init__(
        self,
        asset_ids: _Optional[_Iterable[str]] = ...,
        market_ids: _Optional[_Iterable[str]] = ...,
        from_epoch: _Optional[int] = ...,
        to_epoch: _Optional[int] = ...,
    ) -> None: ...

class ListEpochRewardSummariesRequest(_message.Message):
    __slots__ = ("filter", "pagination")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    filter: RewardSummaryFilter
    pagination: Pagination
    def __init__(
        self,
        filter: _Optional[_Union[RewardSummaryFilter, _Mapping]] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListEpochRewardSummariesResponse(_message.Message):
    __slots__ = ("summaries",)
    SUMMARIES_FIELD_NUMBER: _ClassVar[int]
    summaries: EpochRewardSummaryConnection
    def __init__(
        self, summaries: _Optional[_Union[EpochRewardSummaryConnection, _Mapping]] = ...
    ) -> None: ...

class EpochRewardSummaryConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[EpochRewardSummaryEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[EpochRewardSummaryEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class EpochRewardSummaryEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.EpochRewardSummary
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.EpochRewardSummary, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ObserveRewardsRequest(_message.Message):
    __slots__ = ("asset_id", "party_id")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    party_id: str
    def __init__(
        self, asset_id: _Optional[str] = ..., party_id: _Optional[str] = ...
    ) -> None: ...

class ObserveRewardsResponse(_message.Message):
    __slots__ = ("reward",)
    REWARD_FIELD_NUMBER: _ClassVar[int]
    reward: _vega_pb2.Reward
    def __init__(
        self, reward: _Optional[_Union[_vega_pb2.Reward, _Mapping]] = ...
    ) -> None: ...

class GetDepositRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetDepositResponse(_message.Message):
    __slots__ = ("deposit",)
    DEPOSIT_FIELD_NUMBER: _ClassVar[int]
    deposit: _vega_pb2.Deposit
    def __init__(
        self, deposit: _Optional[_Union[_vega_pb2.Deposit, _Mapping]] = ...
    ) -> None: ...

class ListDepositsRequest(_message.Message):
    __slots__ = ("party_id", "pagination", "date_range")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    pagination: Pagination
    date_range: DateRange
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        date_range: _Optional[_Union[DateRange, _Mapping]] = ...,
    ) -> None: ...

class ListDepositsResponse(_message.Message):
    __slots__ = ("deposits",)
    DEPOSITS_FIELD_NUMBER: _ClassVar[int]
    deposits: DepositsConnection
    def __init__(
        self, deposits: _Optional[_Union[DepositsConnection, _Mapping]] = ...
    ) -> None: ...

class DepositEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.Deposit
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.Deposit, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class DepositsConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[DepositEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[DepositEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class GetWithdrawalRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetWithdrawalResponse(_message.Message):
    __slots__ = ("withdrawal",)
    WITHDRAWAL_FIELD_NUMBER: _ClassVar[int]
    withdrawal: _vega_pb2.Withdrawal
    def __init__(
        self, withdrawal: _Optional[_Union[_vega_pb2.Withdrawal, _Mapping]] = ...
    ) -> None: ...

class ListWithdrawalsRequest(_message.Message):
    __slots__ = ("party_id", "pagination", "date_range")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    pagination: Pagination
    date_range: DateRange
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        date_range: _Optional[_Union[DateRange, _Mapping]] = ...,
    ) -> None: ...

class ListWithdrawalsResponse(_message.Message):
    __slots__ = ("withdrawals",)
    WITHDRAWALS_FIELD_NUMBER: _ClassVar[int]
    withdrawals: WithdrawalsConnection
    def __init__(
        self, withdrawals: _Optional[_Union[WithdrawalsConnection, _Mapping]] = ...
    ) -> None: ...

class WithdrawalEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.Withdrawal
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.Withdrawal, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class WithdrawalsConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[WithdrawalEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[WithdrawalEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class GetAssetRequest(_message.Message):
    __slots__ = ("asset_id",)
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    def __init__(self, asset_id: _Optional[str] = ...) -> None: ...

class GetAssetResponse(_message.Message):
    __slots__ = ("asset",)
    ASSET_FIELD_NUMBER: _ClassVar[int]
    asset: _assets_pb2.Asset
    def __init__(
        self, asset: _Optional[_Union[_assets_pb2.Asset, _Mapping]] = ...
    ) -> None: ...

class ListAssetsRequest(_message.Message):
    __slots__ = ("asset_id", "pagination")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    pagination: Pagination
    def __init__(
        self,
        asset_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListAssetsResponse(_message.Message):
    __slots__ = ("assets",)
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    assets: AssetsConnection
    def __init__(
        self, assets: _Optional[_Union[AssetsConnection, _Mapping]] = ...
    ) -> None: ...

class AssetEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _assets_pb2.Asset
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_assets_pb2.Asset, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class AssetsConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[AssetEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[AssetEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListLiquidityProvisionsRequest(_message.Message):
    __slots__ = ("market_id", "party_id", "reference", "live", "pagination")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    LIVE_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    party_id: str
    reference: str
    live: bool
    pagination: Pagination
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        reference: _Optional[str] = ...,
        live: bool = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListAllLiquidityProvisionsRequest(_message.Message):
    __slots__ = ("market_id", "party_id", "reference", "live", "pagination")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    LIVE_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    party_id: str
    reference: str
    live: bool
    pagination: Pagination
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        reference: _Optional[str] = ...,
        live: bool = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListLiquidityProvisionsResponse(_message.Message):
    __slots__ = ("liquidity_provisions",)
    LIQUIDITY_PROVISIONS_FIELD_NUMBER: _ClassVar[int]
    liquidity_provisions: LiquidityProvisionsConnection
    def __init__(
        self,
        liquidity_provisions: _Optional[
            _Union[LiquidityProvisionsConnection, _Mapping]
        ] = ...,
    ) -> None: ...

class ListAllLiquidityProvisionsResponse(_message.Message):
    __slots__ = ("liquidity_provisions",)
    LIQUIDITY_PROVISIONS_FIELD_NUMBER: _ClassVar[int]
    liquidity_provisions: LiquidityProvisionsWithPendingConnection
    def __init__(
        self,
        liquidity_provisions: _Optional[
            _Union[LiquidityProvisionsWithPendingConnection, _Mapping]
        ] = ...,
    ) -> None: ...

class LiquidityProvision(_message.Message):
    __slots__ = ("current", "pending")
    CURRENT_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    current: _vega_pb2.LiquidityProvision
    pending: _vega_pb2.LiquidityProvision
    def __init__(
        self,
        current: _Optional[_Union[_vega_pb2.LiquidityProvision, _Mapping]] = ...,
        pending: _Optional[_Union[_vega_pb2.LiquidityProvision, _Mapping]] = ...,
    ) -> None: ...

class LiquidityProvisionsEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.LiquidityProvision
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.LiquidityProvision, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class LiquidityProvisionWithPendingEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: LiquidityProvision
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[LiquidityProvision, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class LiquidityProvisionsConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[LiquidityProvisionsEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[LiquidityProvisionsEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class LiquidityProvisionsWithPendingConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[
        LiquidityProvisionWithPendingEdge
    ]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[
            _Iterable[_Union[LiquidityProvisionWithPendingEdge, _Mapping]]
        ] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ObserveLiquidityProvisionsRequest(_message.Message):
    __slots__ = ("market_id", "party_id")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    party_id: str
    def __init__(
        self, market_id: _Optional[str] = ..., party_id: _Optional[str] = ...
    ) -> None: ...

class ObserveLiquidityProvisionsResponse(_message.Message):
    __slots__ = ("liquidity_provisions",)
    LIQUIDITY_PROVISIONS_FIELD_NUMBER: _ClassVar[int]
    liquidity_provisions: _containers.RepeatedCompositeFieldContainer[
        _vega_pb2.LiquidityProvision
    ]
    def __init__(
        self,
        liquidity_provisions: _Optional[
            _Iterable[_Union[_vega_pb2.LiquidityProvision, _Mapping]]
        ] = ...,
    ) -> None: ...

class ListLiquidityProvidersRequest(_message.Message):
    __slots__ = ("market_id", "party_id", "pagination")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    party_id: str
    pagination: Pagination
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class LiquidityProvider(_message.Message):
    __slots__ = ("party_id", "market_id", "fee_share", "sla")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    FEE_SHARE_FIELD_NUMBER: _ClassVar[int]
    SLA_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    market_id: str
    fee_share: _vega_pb2.LiquidityProviderFeeShare
    sla: _vega_pb2.LiquidityProviderSLA
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        fee_share: _Optional[
            _Union[_vega_pb2.LiquidityProviderFeeShare, _Mapping]
        ] = ...,
        sla: _Optional[_Union[_vega_pb2.LiquidityProviderSLA, _Mapping]] = ...,
    ) -> None: ...

class LiquidityProviderEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: LiquidityProvider
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[LiquidityProvider, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class LiquidityProviderConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[LiquidityProviderEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[LiquidityProviderEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListLiquidityProvidersResponse(_message.Message):
    __slots__ = ("liquidity_providers",)
    LIQUIDITY_PROVIDERS_FIELD_NUMBER: _ClassVar[int]
    liquidity_providers: LiquidityProviderConnection
    def __init__(
        self,
        liquidity_providers: _Optional[
            _Union[LiquidityProviderConnection, _Mapping]
        ] = ...,
    ) -> None: ...

class ListPaidLiquidityFeesRequest(_message.Message):
    __slots__ = ("market_id", "asset_id", "epoch_seq", "party_ids", "pagination")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    PARTY_IDS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    asset_id: str
    epoch_seq: int
    party_ids: _containers.RepeatedScalarFieldContainer[str]
    pagination: Pagination
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        asset_id: _Optional[str] = ...,
        epoch_seq: _Optional[int] = ...,
        party_ids: _Optional[_Iterable[str]] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListPaidLiquidityFeesResponse(_message.Message):
    __slots__ = ("paid_liquidity_fees",)
    PAID_LIQUIDITY_FEES_FIELD_NUMBER: _ClassVar[int]
    paid_liquidity_fees: PaidLiquidityFeesConnection
    def __init__(
        self,
        paid_liquidity_fees: _Optional[
            _Union[PaidLiquidityFeesConnection, _Mapping]
        ] = ...,
    ) -> None: ...

class PaidLiquidityFeesEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _events_pb2.PaidLiquidityFeesStats
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_events_pb2.PaidLiquidityFeesStats, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class PaidLiquidityFeesConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[PaidLiquidityFeesEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[PaidLiquidityFeesEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class GetGovernanceDataRequest(_message.Message):
    __slots__ = ("proposal_id", "reference")
    PROPOSAL_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    proposal_id: str
    reference: str
    def __init__(
        self, proposal_id: _Optional[str] = ..., reference: _Optional[str] = ...
    ) -> None: ...

class GetGovernanceDataResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _governance_pb2.GovernanceData
    def __init__(
        self, data: _Optional[_Union[_governance_pb2.GovernanceData, _Mapping]] = ...
    ) -> None: ...

class ListGovernanceDataRequest(_message.Message):
    __slots__ = (
        "proposal_state",
        "proposal_type",
        "proposer_party_id",
        "proposal_reference",
        "pagination",
    )

    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_ALL: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_NEW_MARKET: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_UPDATE_MARKET: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_NETWORK_PARAMETERS: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_NEW_ASSET: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_NEW_FREE_FORM: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_UPDATE_ASSET: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_NEW_SPOT_MARKET: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_UPDATE_SPOT_MARKET: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_NEW_TRANSFER: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_CANCEL_TRANSFER: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_UPDATE_MARKET_STATE: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_UPDATE_REFERRAL_PROGRAM: _ClassVar[ListGovernanceDataRequest.Type]
        TYPE_UPDATE_VOLUME_DISCOUNT_PROGRAM: _ClassVar[ListGovernanceDataRequest.Type]
    TYPE_UNSPECIFIED: ListGovernanceDataRequest.Type
    TYPE_ALL: ListGovernanceDataRequest.Type
    TYPE_NEW_MARKET: ListGovernanceDataRequest.Type
    TYPE_UPDATE_MARKET: ListGovernanceDataRequest.Type
    TYPE_NETWORK_PARAMETERS: ListGovernanceDataRequest.Type
    TYPE_NEW_ASSET: ListGovernanceDataRequest.Type
    TYPE_NEW_FREE_FORM: ListGovernanceDataRequest.Type
    TYPE_UPDATE_ASSET: ListGovernanceDataRequest.Type
    TYPE_NEW_SPOT_MARKET: ListGovernanceDataRequest.Type
    TYPE_UPDATE_SPOT_MARKET: ListGovernanceDataRequest.Type
    TYPE_NEW_TRANSFER: ListGovernanceDataRequest.Type
    TYPE_CANCEL_TRANSFER: ListGovernanceDataRequest.Type
    TYPE_UPDATE_MARKET_STATE: ListGovernanceDataRequest.Type
    TYPE_UPDATE_REFERRAL_PROGRAM: ListGovernanceDataRequest.Type
    TYPE_UPDATE_VOLUME_DISCOUNT_PROGRAM: ListGovernanceDataRequest.Type
    PROPOSAL_STATE_FIELD_NUMBER: _ClassVar[int]
    PROPOSAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    PROPOSER_PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PROPOSAL_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    proposal_state: _governance_pb2.Proposal.State
    proposal_type: ListGovernanceDataRequest.Type
    proposer_party_id: str
    proposal_reference: str
    pagination: Pagination
    def __init__(
        self,
        proposal_state: _Optional[_Union[_governance_pb2.Proposal.State, str]] = ...,
        proposal_type: _Optional[_Union[ListGovernanceDataRequest.Type, str]] = ...,
        proposer_party_id: _Optional[str] = ...,
        proposal_reference: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListGovernanceDataResponse(_message.Message):
    __slots__ = ("connection",)
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    connection: GovernanceDataConnection
    def __init__(
        self, connection: _Optional[_Union[GovernanceDataConnection, _Mapping]] = ...
    ) -> None: ...

class GovernanceDataEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _governance_pb2.GovernanceData
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_governance_pb2.GovernanceData, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class GovernanceDataConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[GovernanceDataEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[GovernanceDataEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ObserveGovernanceRequest(_message.Message):
    __slots__ = ("party_id",)
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    def __init__(self, party_id: _Optional[str] = ...) -> None: ...

class ObserveGovernanceResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _governance_pb2.GovernanceData
    def __init__(
        self, data: _Optional[_Union[_governance_pb2.GovernanceData, _Mapping]] = ...
    ) -> None: ...

class ListDelegationsRequest(_message.Message):
    __slots__ = ("party_id", "node_id", "epoch_id", "pagination")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    node_id: str
    epoch_id: str
    pagination: Pagination
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        node_id: _Optional[str] = ...,
        epoch_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListDelegationsResponse(_message.Message):
    __slots__ = ("delegations",)
    DELEGATIONS_FIELD_NUMBER: _ClassVar[int]
    delegations: DelegationsConnection
    def __init__(
        self, delegations: _Optional[_Union[DelegationsConnection, _Mapping]] = ...
    ) -> None: ...

class DelegationEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.Delegation
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.Delegation, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class DelegationsConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[DelegationEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[DelegationEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ObserveDelegationsRequest(_message.Message):
    __slots__ = ("party_id", "node_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    node_id: str
    def __init__(
        self, party_id: _Optional[str] = ..., node_id: _Optional[str] = ...
    ) -> None: ...

class ObserveDelegationsResponse(_message.Message):
    __slots__ = ("delegation",)
    DELEGATION_FIELD_NUMBER: _ClassVar[int]
    delegation: _vega_pb2.Delegation
    def __init__(
        self, delegation: _Optional[_Union[_vega_pb2.Delegation, _Mapping]] = ...
    ) -> None: ...

class NodeBasic(_message.Message):
    __slots__ = (
        "id",
        "pub_key",
        "tm_pub_key",
        "ethereum_address",
        "info_url",
        "location",
        "status",
        "name",
        "avatar_url",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    TM_PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    INFO_URL_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    id: str
    pub_key: str
    tm_pub_key: str
    ethereum_address: str
    info_url: str
    location: str
    status: _vega_pb2.NodeStatus
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
        status: _Optional[_Union[_vega_pb2.NodeStatus, str]] = ...,
        name: _Optional[str] = ...,
        avatar_url: _Optional[str] = ...,
    ) -> None: ...

class GetNetworkDataRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetNetworkDataResponse(_message.Message):
    __slots__ = ("node_data",)
    NODE_DATA_FIELD_NUMBER: _ClassVar[int]
    node_data: _vega_pb2.NodeData
    def __init__(
        self, node_data: _Optional[_Union[_vega_pb2.NodeData, _Mapping]] = ...
    ) -> None: ...

class GetNodeRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetNodeResponse(_message.Message):
    __slots__ = ("node",)
    NODE_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.Node
    def __init__(
        self, node: _Optional[_Union[_vega_pb2.Node, _Mapping]] = ...
    ) -> None: ...

class ListNodesRequest(_message.Message):
    __slots__ = ("epoch_seq", "pagination")
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    epoch_seq: int
    pagination: Pagination
    def __init__(
        self,
        epoch_seq: _Optional[int] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListNodesResponse(_message.Message):
    __slots__ = ("nodes",)
    NODES_FIELD_NUMBER: _ClassVar[int]
    nodes: NodesConnection
    def __init__(
        self, nodes: _Optional[_Union[NodesConnection, _Mapping]] = ...
    ) -> None: ...

class NodeEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.Node
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.Node, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class NodesConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[NodeEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[NodeEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListNodeSignaturesRequest(_message.Message):
    __slots__ = ("id", "pagination")
    ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    pagination: Pagination
    def __init__(
        self,
        id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListNodeSignaturesResponse(_message.Message):
    __slots__ = ("signatures",)
    SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    signatures: NodeSignaturesConnection
    def __init__(
        self, signatures: _Optional[_Union[NodeSignaturesConnection, _Mapping]] = ...
    ) -> None: ...

class NodeSignatureEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _validator_commands_pb2.NodeSignature
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_validator_commands_pb2.NodeSignature, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class NodeSignaturesConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[NodeSignatureEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[NodeSignatureEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class GetEpochRequest(_message.Message):
    __slots__ = ("id", "block")
    ID_FIELD_NUMBER: _ClassVar[int]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    id: int
    block: int
    def __init__(
        self, id: _Optional[int] = ..., block: _Optional[int] = ...
    ) -> None: ...

class GetEpochResponse(_message.Message):
    __slots__ = ("epoch",)
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    epoch: _vega_pb2.Epoch
    def __init__(
        self, epoch: _Optional[_Union[_vega_pb2.Epoch, _Mapping]] = ...
    ) -> None: ...

class EstimateFeeRequest(_message.Message):
    __slots__ = ("market_id", "price", "size")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    price: str
    size: int
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        price: _Optional[str] = ...,
        size: _Optional[int] = ...,
    ) -> None: ...

class EstimateFeeResponse(_message.Message):
    __slots__ = ("fee",)
    FEE_FIELD_NUMBER: _ClassVar[int]
    fee: _vega_pb2.Fee
    def __init__(
        self, fee: _Optional[_Union[_vega_pb2.Fee, _Mapping]] = ...
    ) -> None: ...

class EstimateMarginRequest(_message.Message):
    __slots__ = ("market_id", "party_id", "side", "type", "size", "price")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    party_id: str
    side: _vega_pb2.Side
    type: _vega_pb2.Order.Type
    size: int
    price: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        side: _Optional[_Union[_vega_pb2.Side, str]] = ...,
        type: _Optional[_Union[_vega_pb2.Order.Type, str]] = ...,
        size: _Optional[int] = ...,
        price: _Optional[str] = ...,
    ) -> None: ...

class EstimateMarginResponse(_message.Message):
    __slots__ = ("margin_levels",)
    MARGIN_LEVELS_FIELD_NUMBER: _ClassVar[int]
    margin_levels: _vega_pb2.MarginLevels
    def __init__(
        self, margin_levels: _Optional[_Union[_vega_pb2.MarginLevels, _Mapping]] = ...
    ) -> None: ...

class ListNetworkParametersRequest(_message.Message):
    __slots__ = ("pagination",)
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    pagination: Pagination
    def __init__(
        self, pagination: _Optional[_Union[Pagination, _Mapping]] = ...
    ) -> None: ...

class ListNetworkParametersResponse(_message.Message):
    __slots__ = ("network_parameters",)
    NETWORK_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    network_parameters: NetworkParameterConnection
    def __init__(
        self,
        network_parameters: _Optional[
            _Union[NetworkParameterConnection, _Mapping]
        ] = ...,
    ) -> None: ...

class GetNetworkParameterRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class GetNetworkParameterResponse(_message.Message):
    __slots__ = ("network_parameter",)
    NETWORK_PARAMETER_FIELD_NUMBER: _ClassVar[int]
    network_parameter: _vega_pb2.NetworkParameter
    def __init__(
        self,
        network_parameter: _Optional[
            _Union[_vega_pb2.NetworkParameter, _Mapping]
        ] = ...,
    ) -> None: ...

class NetworkParameterEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _vega_pb2.NetworkParameter
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_vega_pb2.NetworkParameter, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class NetworkParameterConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[NetworkParameterEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[NetworkParameterEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class Checkpoint(_message.Message):
    __slots__ = ("hash", "block_hash", "at_block")
    HASH_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HASH_FIELD_NUMBER: _ClassVar[int]
    AT_BLOCK_FIELD_NUMBER: _ClassVar[int]
    hash: str
    block_hash: str
    at_block: int
    def __init__(
        self,
        hash: _Optional[str] = ...,
        block_hash: _Optional[str] = ...,
        at_block: _Optional[int] = ...,
    ) -> None: ...

class ListCheckpointsRequest(_message.Message):
    __slots__ = ("pagination",)
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    pagination: Pagination
    def __init__(
        self, pagination: _Optional[_Union[Pagination, _Mapping]] = ...
    ) -> None: ...

class ListCheckpointsResponse(_message.Message):
    __slots__ = ("checkpoints",)
    CHECKPOINTS_FIELD_NUMBER: _ClassVar[int]
    checkpoints: CheckpointsConnection
    def __init__(
        self, checkpoints: _Optional[_Union[CheckpointsConnection, _Mapping]] = ...
    ) -> None: ...

class CheckpointEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: Checkpoint
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[Checkpoint, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class CheckpointsConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[CheckpointEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[CheckpointEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class GetStakeRequest(_message.Message):
    __slots__ = ("party_id", "pagination")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    pagination: Pagination
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class GetStakeResponse(_message.Message):
    __slots__ = ("current_stake_available", "stake_linkings")
    CURRENT_STAKE_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    STAKE_LINKINGS_FIELD_NUMBER: _ClassVar[int]
    current_stake_available: str
    stake_linkings: StakesConnection
    def __init__(
        self,
        current_stake_available: _Optional[str] = ...,
        stake_linkings: _Optional[_Union[StakesConnection, _Mapping]] = ...,
    ) -> None: ...

class StakeLinkingEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _events_pb2.StakeLinking
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_events_pb2.StakeLinking, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class StakesConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[StakeLinkingEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[StakeLinkingEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class GetRiskFactorsRequest(_message.Message):
    __slots__ = ("market_id",)
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    def __init__(self, market_id: _Optional[str] = ...) -> None: ...

class GetRiskFactorsResponse(_message.Message):
    __slots__ = ("risk_factor",)
    RISK_FACTOR_FIELD_NUMBER: _ClassVar[int]
    risk_factor: _vega_pb2.RiskFactor
    def __init__(
        self, risk_factor: _Optional[_Union[_vega_pb2.RiskFactor, _Mapping]] = ...
    ) -> None: ...

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

class ObserveLedgerMovementsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ObserveLedgerMovementsResponse(_message.Message):
    __slots__ = ("ledger_movement",)
    LEDGER_MOVEMENT_FIELD_NUMBER: _ClassVar[int]
    ledger_movement: _vega_pb2.LedgerMovement
    def __init__(
        self,
        ledger_movement: _Optional[_Union[_vega_pb2.LedgerMovement, _Mapping]] = ...,
    ) -> None: ...

class ListKeyRotationsRequest(_message.Message):
    __slots__ = ("node_id", "pagination")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    pagination: Pagination
    def __init__(
        self,
        node_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListKeyRotationsResponse(_message.Message):
    __slots__ = ("rotations",)
    ROTATIONS_FIELD_NUMBER: _ClassVar[int]
    rotations: KeyRotationConnection
    def __init__(
        self, rotations: _Optional[_Union[KeyRotationConnection, _Mapping]] = ...
    ) -> None: ...

class KeyRotationEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _events_pb2.KeyRotation
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_events_pb2.KeyRotation, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class KeyRotationConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[KeyRotationEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[KeyRotationEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListEthereumKeyRotationsRequest(_message.Message):
    __slots__ = ("node_id", "pagination")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    pagination: Pagination
    def __init__(
        self,
        node_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListEthereumKeyRotationsResponse(_message.Message):
    __slots__ = ("key_rotations",)
    KEY_ROTATIONS_FIELD_NUMBER: _ClassVar[int]
    key_rotations: EthereumKeyRotationsConnection
    def __init__(
        self,
        key_rotations: _Optional[
            _Union[EthereumKeyRotationsConnection, _Mapping]
        ] = ...,
    ) -> None: ...

class EthereumKeyRotationsConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[EthereumKeyRotationEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[EthereumKeyRotationEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class EthereumKeyRotationEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _events_pb2.EthereumKeyRotation
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_events_pb2.EthereumKeyRotation, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class GetVegaTimeRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetVegaTimeResponse(_message.Message):
    __slots__ = ("timestamp",)
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    def __init__(self, timestamp: _Optional[int] = ...) -> None: ...

class DateRange(_message.Message):
    __slots__ = ("start_timestamp", "end_timestamp")
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    start_timestamp: int
    end_timestamp: int
    def __init__(
        self, start_timestamp: _Optional[int] = ..., end_timestamp: _Optional[int] = ...
    ) -> None: ...

class GetProtocolUpgradeStatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetProtocolUpgradeStatusResponse(_message.Message):
    __slots__ = ("ready",)
    READY_FIELD_NUMBER: _ClassVar[int]
    ready: bool
    def __init__(self, ready: bool = ...) -> None: ...

class ListProtocolUpgradeProposalsRequest(_message.Message):
    __slots__ = ("status", "approved_by", "pagination")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    status: _events_pb2.ProtocolUpgradeProposalStatus
    approved_by: str
    pagination: Pagination
    def __init__(
        self,
        status: _Optional[_Union[_events_pb2.ProtocolUpgradeProposalStatus, str]] = ...,
        approved_by: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListProtocolUpgradeProposalsResponse(_message.Message):
    __slots__ = ("protocol_upgrade_proposals",)
    PROTOCOL_UPGRADE_PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    protocol_upgrade_proposals: ProtocolUpgradeProposalConnection
    def __init__(
        self,
        protocol_upgrade_proposals: _Optional[
            _Union[ProtocolUpgradeProposalConnection, _Mapping]
        ] = ...,
    ) -> None: ...

class ProtocolUpgradeProposalConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[ProtocolUpgradeProposalEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[
            _Iterable[_Union[ProtocolUpgradeProposalEdge, _Mapping]]
        ] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ProtocolUpgradeProposalEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _events_pb2.ProtocolUpgradeEvent
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_events_pb2.ProtocolUpgradeEvent, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ListCoreSnapshotsRequest(_message.Message):
    __slots__ = ("pagination",)
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    pagination: Pagination
    def __init__(
        self, pagination: _Optional[_Union[Pagination, _Mapping]] = ...
    ) -> None: ...

class ListCoreSnapshotsResponse(_message.Message):
    __slots__ = ("core_snapshots",)
    CORE_SNAPSHOTS_FIELD_NUMBER: _ClassVar[int]
    core_snapshots: CoreSnapshotConnection
    def __init__(
        self, core_snapshots: _Optional[_Union[CoreSnapshotConnection, _Mapping]] = ...
    ) -> None: ...

class CoreSnapshotConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[CoreSnapshotEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[CoreSnapshotEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class CoreSnapshotEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _events_pb2.CoreSnapshotData
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_events_pb2.CoreSnapshotData, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class HistorySegment(_message.Message):
    __slots__ = (
        "from_height",
        "to_height",
        "history_segment_id",
        "previous_history_segment_id",
        "database_version",
        "chain_id",
    )
    FROM_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TO_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    HISTORY_SEGMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_HISTORY_SEGMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DATABASE_VERSION_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    from_height: int
    to_height: int
    history_segment_id: str
    previous_history_segment_id: str
    database_version: int
    chain_id: str
    def __init__(
        self,
        from_height: _Optional[int] = ...,
        to_height: _Optional[int] = ...,
        history_segment_id: _Optional[str] = ...,
        previous_history_segment_id: _Optional[str] = ...,
        database_version: _Optional[int] = ...,
        chain_id: _Optional[str] = ...,
    ) -> None: ...

class GetMostRecentNetworkHistorySegmentRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetMostRecentNetworkHistorySegmentResponse(_message.Message):
    __slots__ = ("segment", "swarm_key_seed")
    SEGMENT_FIELD_NUMBER: _ClassVar[int]
    SWARM_KEY_SEED_FIELD_NUMBER: _ClassVar[int]
    segment: HistorySegment
    swarm_key_seed: str
    def __init__(
        self,
        segment: _Optional[_Union[HistorySegment, _Mapping]] = ...,
        swarm_key_seed: _Optional[str] = ...,
    ) -> None: ...

class ListAllNetworkHistorySegmentsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListAllNetworkHistorySegmentsResponse(_message.Message):
    __slots__ = ("segments",)
    SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    segments: _containers.RepeatedCompositeFieldContainer[HistorySegment]
    def __init__(
        self, segments: _Optional[_Iterable[_Union[HistorySegment, _Mapping]]] = ...
    ) -> None: ...

class GetActiveNetworkHistoryPeerAddressesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetActiveNetworkHistoryPeerAddressesResponse(_message.Message):
    __slots__ = ("ip_addresses",)
    IP_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    ip_addresses: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, ip_addresses: _Optional[_Iterable[str]] = ...) -> None: ...

class GetNetworkHistoryStatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetNetworkHistoryStatusResponse(_message.Message):
    __slots__ = ("ipfs_address", "swarm_key", "swarm_key_seed", "connected_peers")
    IPFS_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SWARM_KEY_FIELD_NUMBER: _ClassVar[int]
    SWARM_KEY_SEED_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_PEERS_FIELD_NUMBER: _ClassVar[int]
    ipfs_address: str
    swarm_key: str
    swarm_key_seed: str
    connected_peers: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        ipfs_address: _Optional[str] = ...,
        swarm_key: _Optional[str] = ...,
        swarm_key_seed: _Optional[str] = ...,
        connected_peers: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class GetNetworkHistoryBootstrapPeersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetNetworkHistoryBootstrapPeersResponse(_message.Message):
    __slots__ = ("bootstrap_peers",)
    BOOTSTRAP_PEERS_FIELD_NUMBER: _ClassVar[int]
    bootstrap_peers: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, bootstrap_peers: _Optional[_Iterable[str]] = ...) -> None: ...

class ExportNetworkHistoryRequest(_message.Message):
    __slots__ = ("from_block", "to_block", "table")
    FROM_BLOCK_FIELD_NUMBER: _ClassVar[int]
    TO_BLOCK_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    from_block: int
    to_block: int
    table: Table
    def __init__(
        self,
        from_block: _Optional[int] = ...,
        to_block: _Optional[int] = ...,
        table: _Optional[_Union[Table, str]] = ...,
    ) -> None: ...

class ListEntitiesRequest(_message.Message):
    __slots__ = ("transaction_hash",)
    TRANSACTION_HASH_FIELD_NUMBER: _ClassVar[int]
    transaction_hash: str
    def __init__(self, transaction_hash: _Optional[str] = ...) -> None: ...

class ListEntitiesResponse(_message.Message):
    __slots__ = (
        "accounts",
        "orders",
        "positions",
        "ledger_entries",
        "balance_changes",
        "transfers",
        "votes",
        "erc20_multi_sig_signer_added_bundles",
        "erc20_multi_sig_signer_removed_bundles",
        "trades",
        "oracle_specs",
        "oracle_data",
        "markets",
        "parties",
        "margin_levels",
        "rewards",
        "deposits",
        "withdrawals",
        "assets",
        "liquidity_provisions",
        "proposals",
        "delegations",
        "nodes",
        "node_signatures",
        "network_parameters",
        "key_rotations",
        "ethereum_key_rotations",
        "protocol_upgrade_proposals",
    )
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    LEDGER_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    BALANCE_CHANGES_FIELD_NUMBER: _ClassVar[int]
    TRANSFERS_FIELD_NUMBER: _ClassVar[int]
    VOTES_FIELD_NUMBER: _ClassVar[int]
    ERC20_MULTI_SIG_SIGNER_ADDED_BUNDLES_FIELD_NUMBER: _ClassVar[int]
    ERC20_MULTI_SIG_SIGNER_REMOVED_BUNDLES_FIELD_NUMBER: _ClassVar[int]
    TRADES_FIELD_NUMBER: _ClassVar[int]
    ORACLE_SPECS_FIELD_NUMBER: _ClassVar[int]
    ORACLE_DATA_FIELD_NUMBER: _ClassVar[int]
    MARKETS_FIELD_NUMBER: _ClassVar[int]
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    MARGIN_LEVELS_FIELD_NUMBER: _ClassVar[int]
    REWARDS_FIELD_NUMBER: _ClassVar[int]
    DEPOSITS_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWALS_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISIONS_FIELD_NUMBER: _ClassVar[int]
    PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    DELEGATIONS_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    NODE_SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    NETWORK_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    KEY_ROTATIONS_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_KEY_ROTATIONS_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_UPGRADE_PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    accounts: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Account]
    orders: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Order]
    positions: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Position]
    ledger_entries: _containers.RepeatedCompositeFieldContainer[_vega_pb2.LedgerEntry]
    balance_changes: _containers.RepeatedCompositeFieldContainer[AccountBalance]
    transfers: _containers.RepeatedCompositeFieldContainer[_events_pb2.Transfer]
    votes: _containers.RepeatedCompositeFieldContainer[_governance_pb2.Vote]
    erc20_multi_sig_signer_added_bundles: _containers.RepeatedCompositeFieldContainer[
        ERC20MultiSigSignerAddedBundle
    ]
    erc20_multi_sig_signer_removed_bundles: _containers.RepeatedCompositeFieldContainer[
        ERC20MultiSigSignerRemovedBundle
    ]
    trades: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Trade]
    oracle_specs: _containers.RepeatedCompositeFieldContainer[_oracle_pb2.OracleSpec]
    oracle_data: _containers.RepeatedCompositeFieldContainer[_oracle_pb2.OracleData]
    markets: _containers.RepeatedCompositeFieldContainer[_markets_pb2.Market]
    parties: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Party]
    margin_levels: _containers.RepeatedCompositeFieldContainer[_vega_pb2.MarginLevels]
    rewards: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Reward]
    deposits: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Deposit]
    withdrawals: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Withdrawal]
    assets: _containers.RepeatedCompositeFieldContainer[_assets_pb2.Asset]
    liquidity_provisions: _containers.RepeatedCompositeFieldContainer[
        _vega_pb2.LiquidityProvision
    ]
    proposals: _containers.RepeatedCompositeFieldContainer[_governance_pb2.Proposal]
    delegations: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Delegation]
    nodes: _containers.RepeatedCompositeFieldContainer[NodeBasic]
    node_signatures: _containers.RepeatedCompositeFieldContainer[
        _validator_commands_pb2.NodeSignature
    ]
    network_parameters: _containers.RepeatedCompositeFieldContainer[
        _vega_pb2.NetworkParameter
    ]
    key_rotations: _containers.RepeatedCompositeFieldContainer[_events_pb2.KeyRotation]
    ethereum_key_rotations: _containers.RepeatedCompositeFieldContainer[
        _events_pb2.EthereumKeyRotation
    ]
    protocol_upgrade_proposals: _containers.RepeatedCompositeFieldContainer[
        _events_pb2.ProtocolUpgradeEvent
    ]
    def __init__(
        self,
        accounts: _Optional[_Iterable[_Union[_vega_pb2.Account, _Mapping]]] = ...,
        orders: _Optional[_Iterable[_Union[_vega_pb2.Order, _Mapping]]] = ...,
        positions: _Optional[_Iterable[_Union[_vega_pb2.Position, _Mapping]]] = ...,
        ledger_entries: _Optional[
            _Iterable[_Union[_vega_pb2.LedgerEntry, _Mapping]]
        ] = ...,
        balance_changes: _Optional[_Iterable[_Union[AccountBalance, _Mapping]]] = ...,
        transfers: _Optional[_Iterable[_Union[_events_pb2.Transfer, _Mapping]]] = ...,
        votes: _Optional[_Iterable[_Union[_governance_pb2.Vote, _Mapping]]] = ...,
        erc20_multi_sig_signer_added_bundles: _Optional[
            _Iterable[_Union[ERC20MultiSigSignerAddedBundle, _Mapping]]
        ] = ...,
        erc20_multi_sig_signer_removed_bundles: _Optional[
            _Iterable[_Union[ERC20MultiSigSignerRemovedBundle, _Mapping]]
        ] = ...,
        trades: _Optional[_Iterable[_Union[_vega_pb2.Trade, _Mapping]]] = ...,
        oracle_specs: _Optional[
            _Iterable[_Union[_oracle_pb2.OracleSpec, _Mapping]]
        ] = ...,
        oracle_data: _Optional[
            _Iterable[_Union[_oracle_pb2.OracleData, _Mapping]]
        ] = ...,
        markets: _Optional[_Iterable[_Union[_markets_pb2.Market, _Mapping]]] = ...,
        parties: _Optional[_Iterable[_Union[_vega_pb2.Party, _Mapping]]] = ...,
        margin_levels: _Optional[
            _Iterable[_Union[_vega_pb2.MarginLevels, _Mapping]]
        ] = ...,
        rewards: _Optional[_Iterable[_Union[_vega_pb2.Reward, _Mapping]]] = ...,
        deposits: _Optional[_Iterable[_Union[_vega_pb2.Deposit, _Mapping]]] = ...,
        withdrawals: _Optional[_Iterable[_Union[_vega_pb2.Withdrawal, _Mapping]]] = ...,
        assets: _Optional[_Iterable[_Union[_assets_pb2.Asset, _Mapping]]] = ...,
        liquidity_provisions: _Optional[
            _Iterable[_Union[_vega_pb2.LiquidityProvision, _Mapping]]
        ] = ...,
        proposals: _Optional[
            _Iterable[_Union[_governance_pb2.Proposal, _Mapping]]
        ] = ...,
        delegations: _Optional[_Iterable[_Union[_vega_pb2.Delegation, _Mapping]]] = ...,
        nodes: _Optional[_Iterable[_Union[NodeBasic, _Mapping]]] = ...,
        node_signatures: _Optional[
            _Iterable[_Union[_validator_commands_pb2.NodeSignature, _Mapping]]
        ] = ...,
        network_parameters: _Optional[
            _Iterable[_Union[_vega_pb2.NetworkParameter, _Mapping]]
        ] = ...,
        key_rotations: _Optional[
            _Iterable[_Union[_events_pb2.KeyRotation, _Mapping]]
        ] = ...,
        ethereum_key_rotations: _Optional[
            _Iterable[_Union[_events_pb2.EthereumKeyRotation, _Mapping]]
        ] = ...,
        protocol_upgrade_proposals: _Optional[
            _Iterable[_Union[_events_pb2.ProtocolUpgradeEvent, _Mapping]]
        ] = ...,
    ) -> None: ...

class GetPartyActivityStreakRequest(_message.Message):
    __slots__ = ("party_id", "epoch")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    epoch: int
    def __init__(
        self, party_id: _Optional[str] = ..., epoch: _Optional[int] = ...
    ) -> None: ...

class GetPartyActivityStreakResponse(_message.Message):
    __slots__ = ("activity_streak",)
    ACTIVITY_STREAK_FIELD_NUMBER: _ClassVar[int]
    activity_streak: _events_pb2.PartyActivityStreak
    def __init__(
        self,
        activity_streak: _Optional[
            _Union[_events_pb2.PartyActivityStreak, _Mapping]
        ] = ...,
    ) -> None: ...

class FundingPayment(_message.Message):
    __slots__ = ("party_id", "market_id", "funding_period_seq", "timestamp", "amount")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    FUNDING_PERIOD_SEQ_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    market_id: str
    funding_period_seq: int
    timestamp: int
    amount: str
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        funding_period_seq: _Optional[int] = ...,
        timestamp: _Optional[int] = ...,
        amount: _Optional[str] = ...,
    ) -> None: ...

class ListFundingPaymentsRequest(_message.Message):
    __slots__ = ("party_id", "market_id", "pagination")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    market_id: str
    pagination: Pagination
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class FundingPaymentEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: FundingPayment
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[FundingPayment, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class FundingPaymentConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[FundingPaymentEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[FundingPaymentEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListFundingPaymentsResponse(_message.Message):
    __slots__ = ("funding_payments",)
    FUNDING_PAYMENTS_FIELD_NUMBER: _ClassVar[int]
    funding_payments: FundingPaymentConnection
    def __init__(
        self,
        funding_payments: _Optional[_Union[FundingPaymentConnection, _Mapping]] = ...,
    ) -> None: ...

class ListFundingPeriodsRequest(_message.Message):
    __slots__ = ("market_id", "date_range", "pagination")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    date_range: DateRange
    pagination: Pagination
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        date_range: _Optional[_Union[DateRange, _Mapping]] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class FundingPeriodEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _events_pb2.FundingPeriod
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_events_pb2.FundingPeriod, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class FundingPeriodConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[FundingPeriodEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[FundingPeriodEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListFundingPeriodsResponse(_message.Message):
    __slots__ = ("funding_periods",)
    FUNDING_PERIODS_FIELD_NUMBER: _ClassVar[int]
    funding_periods: FundingPeriodConnection
    def __init__(
        self,
        funding_periods: _Optional[_Union[FundingPeriodConnection, _Mapping]] = ...,
    ) -> None: ...

class ListFundingPeriodDataPointsRequest(_message.Message):
    __slots__ = ("market_id", "date_range", "source", "seq", "pagination")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    date_range: DateRange
    source: _events_pb2.FundingPeriodDataPoint.Source
    seq: int
    pagination: Pagination
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        date_range: _Optional[_Union[DateRange, _Mapping]] = ...,
        source: _Optional[_Union[_events_pb2.FundingPeriodDataPoint.Source, str]] = ...,
        seq: _Optional[int] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class FundingPeriodDataPointEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: _events_pb2.FundingPeriodDataPoint
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[_events_pb2.FundingPeriodDataPoint, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class FundingPeriodDataPointConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[FundingPeriodDataPointEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[FundingPeriodDataPointEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListFundingPeriodDataPointsResponse(_message.Message):
    __slots__ = ("funding_period_data_points",)
    FUNDING_PERIOD_DATA_POINTS_FIELD_NUMBER: _ClassVar[int]
    funding_period_data_points: FundingPeriodDataPointConnection
    def __init__(
        self,
        funding_period_data_points: _Optional[
            _Union[FundingPeriodDataPointConnection, _Mapping]
        ] = ...,
    ) -> None: ...

class PingRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PingResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OrderInfo(_message.Message):
    __slots__ = ("side", "price", "remaining", "is_market_order")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    REMAINING_FIELD_NUMBER: _ClassVar[int]
    IS_MARKET_ORDER_FIELD_NUMBER: _ClassVar[int]
    side: _vega_pb2.Side
    price: str
    remaining: int
    is_market_order: bool
    def __init__(
        self,
        side: _Optional[_Union[_vega_pb2.Side, str]] = ...,
        price: _Optional[str] = ...,
        remaining: _Optional[int] = ...,
        is_market_order: bool = ...,
    ) -> None: ...

class EstimatePositionRequest(_message.Message):
    __slots__ = (
        "market_id",
        "open_volume",
        "orders",
        "collateral_available",
        "scale_liquidation_price_to_market_decimals",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    OPEN_VOLUME_FIELD_NUMBER: _ClassVar[int]
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    COLLATERAL_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    SCALE_LIQUIDATION_PRICE_TO_MARKET_DECIMALS_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    open_volume: int
    orders: _containers.RepeatedCompositeFieldContainer[OrderInfo]
    collateral_available: str
    scale_liquidation_price_to_market_decimals: bool
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        open_volume: _Optional[int] = ...,
        orders: _Optional[_Iterable[_Union[OrderInfo, _Mapping]]] = ...,
        collateral_available: _Optional[str] = ...,
        scale_liquidation_price_to_market_decimals: bool = ...,
    ) -> None: ...

class EstimatePositionResponse(_message.Message):
    __slots__ = ("margin", "liquidation")
    MARGIN_FIELD_NUMBER: _ClassVar[int]
    LIQUIDATION_FIELD_NUMBER: _ClassVar[int]
    margin: MarginEstimate
    liquidation: LiquidationEstimate
    def __init__(
        self,
        margin: _Optional[_Union[MarginEstimate, _Mapping]] = ...,
        liquidation: _Optional[_Union[LiquidationEstimate, _Mapping]] = ...,
    ) -> None: ...

class MarginEstimate(_message.Message):
    __slots__ = ("worst_case", "best_case")
    WORST_CASE_FIELD_NUMBER: _ClassVar[int]
    BEST_CASE_FIELD_NUMBER: _ClassVar[int]
    worst_case: _vega_pb2.MarginLevels
    best_case: _vega_pb2.MarginLevels
    def __init__(
        self,
        worst_case: _Optional[_Union[_vega_pb2.MarginLevels, _Mapping]] = ...,
        best_case: _Optional[_Union[_vega_pb2.MarginLevels, _Mapping]] = ...,
    ) -> None: ...

class LiquidationEstimate(_message.Message):
    __slots__ = ("worst_case", "best_case")
    WORST_CASE_FIELD_NUMBER: _ClassVar[int]
    BEST_CASE_FIELD_NUMBER: _ClassVar[int]
    worst_case: LiquidationPrice
    best_case: LiquidationPrice
    def __init__(
        self,
        worst_case: _Optional[_Union[LiquidationPrice, _Mapping]] = ...,
        best_case: _Optional[_Union[LiquidationPrice, _Mapping]] = ...,
    ) -> None: ...

class LiquidationPrice(_message.Message):
    __slots__ = ("open_volume_only", "including_buy_orders", "including_sell_orders")
    OPEN_VOLUME_ONLY_FIELD_NUMBER: _ClassVar[int]
    INCLUDING_BUY_ORDERS_FIELD_NUMBER: _ClassVar[int]
    INCLUDING_SELL_ORDERS_FIELD_NUMBER: _ClassVar[int]
    open_volume_only: str
    including_buy_orders: str
    including_sell_orders: str
    def __init__(
        self,
        open_volume_only: _Optional[str] = ...,
        including_buy_orders: _Optional[str] = ...,
        including_sell_orders: _Optional[str] = ...,
    ) -> None: ...

class GetCurrentReferralProgramRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCurrentReferralProgramResponse(_message.Message):
    __slots__ = ("current_referral_program",)
    CURRENT_REFERRAL_PROGRAM_FIELD_NUMBER: _ClassVar[int]
    current_referral_program: ReferralProgram
    def __init__(
        self,
        current_referral_program: _Optional[_Union[ReferralProgram, _Mapping]] = ...,
    ) -> None: ...

class ReferralProgram(_message.Message):
    __slots__ = (
        "version",
        "id",
        "benefit_tiers",
        "end_of_program_timestamp",
        "window_length",
        "staking_tiers",
        "ended_at",
    )
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    BENEFIT_TIERS_FIELD_NUMBER: _ClassVar[int]
    END_OF_PROGRAM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WINDOW_LENGTH_FIELD_NUMBER: _ClassVar[int]
    STAKING_TIERS_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    version: int
    id: str
    benefit_tiers: _containers.RepeatedCompositeFieldContainer[_vega_pb2.BenefitTier]
    end_of_program_timestamp: int
    window_length: int
    staking_tiers: _containers.RepeatedCompositeFieldContainer[_vega_pb2.StakingTier]
    ended_at: int
    def __init__(
        self,
        version: _Optional[int] = ...,
        id: _Optional[str] = ...,
        benefit_tiers: _Optional[
            _Iterable[_Union[_vega_pb2.BenefitTier, _Mapping]]
        ] = ...,
        end_of_program_timestamp: _Optional[int] = ...,
        window_length: _Optional[int] = ...,
        staking_tiers: _Optional[
            _Iterable[_Union[_vega_pb2.StakingTier, _Mapping]]
        ] = ...,
        ended_at: _Optional[int] = ...,
    ) -> None: ...

class ReferralSet(_message.Message):
    __slots__ = ("id", "referrer", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    REFERRER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    referrer: str
    created_at: int
    updated_at: int
    def __init__(
        self,
        id: _Optional[str] = ...,
        referrer: _Optional[str] = ...,
        created_at: _Optional[int] = ...,
        updated_at: _Optional[int] = ...,
    ) -> None: ...

class ReferralSetEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: ReferralSet
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[ReferralSet, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ReferralSetConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[ReferralSetEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[ReferralSetEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListReferralSetsRequest(_message.Message):
    __slots__ = ("referral_set_id", "pagination", "referrer", "referee")
    REFERRAL_SET_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    REFERRER_FIELD_NUMBER: _ClassVar[int]
    REFEREE_FIELD_NUMBER: _ClassVar[int]
    referral_set_id: str
    pagination: Pagination
    referrer: str
    referee: str
    def __init__(
        self,
        referral_set_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        referrer: _Optional[str] = ...,
        referee: _Optional[str] = ...,
    ) -> None: ...

class ListReferralSetsResponse(_message.Message):
    __slots__ = ("referral_sets",)
    REFERRAL_SETS_FIELD_NUMBER: _ClassVar[int]
    referral_sets: ReferralSetConnection
    def __init__(
        self, referral_sets: _Optional[_Union[ReferralSetConnection, _Mapping]] = ...
    ) -> None: ...

class ReferralSetReferee(_message.Message):
    __slots__ = (
        "referral_set_id",
        "referee",
        "joined_at",
        "at_epoch",
        "total_referee_notional_taker_volume",
        "total_referee_generated_rewards",
    )
    REFERRAL_SET_ID_FIELD_NUMBER: _ClassVar[int]
    REFEREE_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REFEREE_NOTIONAL_TAKER_VOLUME_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REFEREE_GENERATED_REWARDS_FIELD_NUMBER: _ClassVar[int]
    referral_set_id: str
    referee: str
    joined_at: int
    at_epoch: int
    total_referee_notional_taker_volume: str
    total_referee_generated_rewards: str
    def __init__(
        self,
        referral_set_id: _Optional[str] = ...,
        referee: _Optional[str] = ...,
        joined_at: _Optional[int] = ...,
        at_epoch: _Optional[int] = ...,
        total_referee_notional_taker_volume: _Optional[str] = ...,
        total_referee_generated_rewards: _Optional[str] = ...,
    ) -> None: ...

class ReferralSetRefereeEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: ReferralSetReferee
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[ReferralSetReferee, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ReferralSetRefereeConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[ReferralSetRefereeEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[ReferralSetRefereeEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListReferralSetRefereesRequest(_message.Message):
    __slots__ = (
        "referral_set_id",
        "pagination",
        "referrer",
        "referee",
        "aggregation_epochs",
    )
    REFERRAL_SET_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    REFERRER_FIELD_NUMBER: _ClassVar[int]
    REFEREE_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_EPOCHS_FIELD_NUMBER: _ClassVar[int]
    referral_set_id: str
    pagination: Pagination
    referrer: str
    referee: str
    aggregation_epochs: int
    def __init__(
        self,
        referral_set_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
        referrer: _Optional[str] = ...,
        referee: _Optional[str] = ...,
        aggregation_epochs: _Optional[int] = ...,
    ) -> None: ...

class ListReferralSetRefereesResponse(_message.Message):
    __slots__ = ("referral_set_referees",)
    REFERRAL_SET_REFEREES_FIELD_NUMBER: _ClassVar[int]
    referral_set_referees: ReferralSetRefereeConnection
    def __init__(
        self,
        referral_set_referees: _Optional[
            _Union[ReferralSetRefereeConnection, _Mapping]
        ] = ...,
    ) -> None: ...

class GetReferralSetStatsRequest(_message.Message):
    __slots__ = ("referral_set_id", "at_epoch", "referee", "pagination")
    REFERRAL_SET_ID_FIELD_NUMBER: _ClassVar[int]
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    REFEREE_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    referral_set_id: str
    at_epoch: int
    referee: str
    pagination: Pagination
    def __init__(
        self,
        referral_set_id: _Optional[str] = ...,
        at_epoch: _Optional[int] = ...,
        referee: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class GetReferralSetStatsResponse(_message.Message):
    __slots__ = ("stats",)
    STATS_FIELD_NUMBER: _ClassVar[int]
    stats: ReferralSetStatsConnection
    def __init__(
        self, stats: _Optional[_Union[ReferralSetStatsConnection, _Mapping]] = ...
    ) -> None: ...

class ReferralSetStatsConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[ReferralSetStatsEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[ReferralSetStatsEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ReferralSetStatsEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: ReferralSetStats
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[ReferralSetStats, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ReferralSetStats(_message.Message):
    __slots__ = (
        "at_epoch",
        "referral_set_running_notional_taker_volume",
        "party_id",
        "discount_factor",
        "reward_factor",
        "epoch_notional_taker_volume",
        "rewards_multiplier",
        "rewards_factor_multiplier",
        "was_eligible",
        "referrer_taker_volume",
    )
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    REFERRAL_SET_RUNNING_NOTIONAL_TAKER_VOLUME_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    REWARD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    EPOCH_NOTIONAL_TAKER_VOLUME_FIELD_NUMBER: _ClassVar[int]
    REWARDS_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    REWARDS_FACTOR_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    WAS_ELIGIBLE_FIELD_NUMBER: _ClassVar[int]
    REFERRER_TAKER_VOLUME_FIELD_NUMBER: _ClassVar[int]
    at_epoch: int
    referral_set_running_notional_taker_volume: str
    party_id: str
    discount_factor: str
    reward_factor: str
    epoch_notional_taker_volume: str
    rewards_multiplier: str
    rewards_factor_multiplier: str
    was_eligible: bool
    referrer_taker_volume: str
    def __init__(
        self,
        at_epoch: _Optional[int] = ...,
        referral_set_running_notional_taker_volume: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        discount_factor: _Optional[str] = ...,
        reward_factor: _Optional[str] = ...,
        epoch_notional_taker_volume: _Optional[str] = ...,
        rewards_multiplier: _Optional[str] = ...,
        rewards_factor_multiplier: _Optional[str] = ...,
        was_eligible: bool = ...,
        referrer_taker_volume: _Optional[str] = ...,
    ) -> None: ...

class Team(_message.Message):
    __slots__ = (
        "team_id",
        "referrer",
        "name",
        "team_url",
        "avatar_url",
        "created_at",
        "closed",
        "created_at_epoch",
    )
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    REFERRER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEAM_URL_FIELD_NUMBER: _ClassVar[int]
    AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CLOSED_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    referrer: str
    name: str
    team_url: str
    avatar_url: str
    created_at: int
    closed: bool
    created_at_epoch: int
    def __init__(
        self,
        team_id: _Optional[str] = ...,
        referrer: _Optional[str] = ...,
        name: _Optional[str] = ...,
        team_url: _Optional[str] = ...,
        avatar_url: _Optional[str] = ...,
        created_at: _Optional[int] = ...,
        closed: bool = ...,
        created_at_epoch: _Optional[int] = ...,
    ) -> None: ...

class TeamEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: Team
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[Team, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class TeamConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[TeamEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[TeamEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListTeamsRequest(_message.Message):
    __slots__ = ("team_id", "party_id", "pagination")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    party_id: str
    pagination: Pagination
    def __init__(
        self,
        team_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListTeamsResponse(_message.Message):
    __slots__ = ("teams",)
    TEAMS_FIELD_NUMBER: _ClassVar[int]
    teams: TeamConnection
    def __init__(
        self, teams: _Optional[_Union[TeamConnection, _Mapping]] = ...
    ) -> None: ...

class ListTeamRefereesRequest(_message.Message):
    __slots__ = ("team_id", "pagination")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    pagination: Pagination
    def __init__(
        self,
        team_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class TeamReferee(_message.Message):
    __slots__ = ("team_id", "referee", "joined_at", "joined_at_epoch")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    REFEREE_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    referee: str
    joined_at: int
    joined_at_epoch: int
    def __init__(
        self,
        team_id: _Optional[str] = ...,
        referee: _Optional[str] = ...,
        joined_at: _Optional[int] = ...,
        joined_at_epoch: _Optional[int] = ...,
    ) -> None: ...

class TeamRefereeEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: TeamReferee
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[TeamReferee, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class TeamRefereeConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[TeamRefereeEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[TeamRefereeEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListTeamRefereesResponse(_message.Message):
    __slots__ = ("team_referees",)
    TEAM_REFEREES_FIELD_NUMBER: _ClassVar[int]
    team_referees: TeamRefereeConnection
    def __init__(
        self, team_referees: _Optional[_Union[TeamRefereeConnection, _Mapping]] = ...
    ) -> None: ...

class TeamRefereeHistory(_message.Message):
    __slots__ = ("team_id", "joined_at", "joined_at_epoch")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    joined_at: int
    joined_at_epoch: int
    def __init__(
        self,
        team_id: _Optional[str] = ...,
        joined_at: _Optional[int] = ...,
        joined_at_epoch: _Optional[int] = ...,
    ) -> None: ...

class TeamRefereeHistoryEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: TeamRefereeHistory
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[TeamRefereeHistory, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class TeamRefereeHistoryConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[TeamRefereeHistoryEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[TeamRefereeHistoryEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class ListTeamRefereeHistoryRequest(_message.Message):
    __slots__ = ("referee", "pagination")
    REFEREE_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    referee: str
    pagination: Pagination
    def __init__(
        self,
        referee: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class ListTeamRefereeHistoryResponse(_message.Message):
    __slots__ = ("team_referee_history",)
    TEAM_REFEREE_HISTORY_FIELD_NUMBER: _ClassVar[int]
    team_referee_history: TeamRefereeHistoryConnection
    def __init__(
        self,
        team_referee_history: _Optional[
            _Union[TeamRefereeHistoryConnection, _Mapping]
        ] = ...,
    ) -> None: ...

class GetFeesStatsRequest(_message.Message):
    __slots__ = ("market_id", "asset_id", "epoch_seq", "party_id")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    asset_id: str
    epoch_seq: int
    party_id: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        asset_id: _Optional[str] = ...,
        epoch_seq: _Optional[int] = ...,
        party_id: _Optional[str] = ...,
    ) -> None: ...

class GetFeesStatsResponse(_message.Message):
    __slots__ = ("fees_stats",)
    FEES_STATS_FIELD_NUMBER: _ClassVar[int]
    fees_stats: _events_pb2.FeesStats
    def __init__(
        self, fees_stats: _Optional[_Union[_events_pb2.FeesStats, _Mapping]] = ...
    ) -> None: ...

class GetFeesStatsForPartyRequest(_message.Message):
    __slots__ = ("party_id", "asset_id", "from_epoch", "to_epoch")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_EPOCH_FIELD_NUMBER: _ClassVar[int]
    TO_EPOCH_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    asset_id: str
    from_epoch: int
    to_epoch: int
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        asset_id: _Optional[str] = ...,
        from_epoch: _Optional[int] = ...,
        to_epoch: _Optional[int] = ...,
    ) -> None: ...

class GetFeesStatsForPartyResponse(_message.Message):
    __slots__ = ("fees_stats_for_party",)
    FEES_STATS_FOR_PARTY_FIELD_NUMBER: _ClassVar[int]
    fees_stats_for_party: _containers.RepeatedCompositeFieldContainer[FeesStatsForParty]
    def __init__(
        self,
        fees_stats_for_party: _Optional[
            _Iterable[_Union[FeesStatsForParty, _Mapping]]
        ] = ...,
    ) -> None: ...

class GetCurrentVolumeDiscountProgramRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCurrentVolumeDiscountProgramResponse(_message.Message):
    __slots__ = ("current_volume_discount_program",)
    CURRENT_VOLUME_DISCOUNT_PROGRAM_FIELD_NUMBER: _ClassVar[int]
    current_volume_discount_program: VolumeDiscountProgram
    def __init__(
        self,
        current_volume_discount_program: _Optional[
            _Union[VolumeDiscountProgram, _Mapping]
        ] = ...,
    ) -> None: ...

class GetVolumeDiscountStatsRequest(_message.Message):
    __slots__ = ("at_epoch", "party_id", "pagination")
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    at_epoch: int
    party_id: str
    pagination: Pagination
    def __init__(
        self,
        at_epoch: _Optional[int] = ...,
        party_id: _Optional[str] = ...,
        pagination: _Optional[_Union[Pagination, _Mapping]] = ...,
    ) -> None: ...

class GetVolumeDiscountStatsResponse(_message.Message):
    __slots__ = ("stats",)
    STATS_FIELD_NUMBER: _ClassVar[int]
    stats: VolumeDiscountStatsConnection
    def __init__(
        self, stats: _Optional[_Union[VolumeDiscountStatsConnection, _Mapping]] = ...
    ) -> None: ...

class VolumeDiscountStatsConnection(_message.Message):
    __slots__ = ("edges", "page_info")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[VolumeDiscountStatsEdge]
    page_info: PageInfo
    def __init__(
        self,
        edges: _Optional[_Iterable[_Union[VolumeDiscountStatsEdge, _Mapping]]] = ...,
        page_info: _Optional[_Union[PageInfo, _Mapping]] = ...,
    ) -> None: ...

class VolumeDiscountStatsEdge(_message.Message):
    __slots__ = ("node", "cursor")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    node: VolumeDiscountStats
    cursor: str
    def __init__(
        self,
        node: _Optional[_Union[VolumeDiscountStats, _Mapping]] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class VolumeDiscountStats(_message.Message):
    __slots__ = ("at_epoch", "party_id", "discount_factor", "running_volume")
    AT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    RUNNING_VOLUME_FIELD_NUMBER: _ClassVar[int]
    at_epoch: int
    party_id: str
    discount_factor: str
    running_volume: str
    def __init__(
        self,
        at_epoch: _Optional[int] = ...,
        party_id: _Optional[str] = ...,
        discount_factor: _Optional[str] = ...,
        running_volume: _Optional[str] = ...,
    ) -> None: ...

class VolumeDiscountProgram(_message.Message):
    __slots__ = (
        "version",
        "id",
        "benefit_tiers",
        "end_of_program_timestamp",
        "window_length",
        "ended_at",
    )
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    BENEFIT_TIERS_FIELD_NUMBER: _ClassVar[int]
    END_OF_PROGRAM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WINDOW_LENGTH_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    version: int
    id: str
    benefit_tiers: _containers.RepeatedCompositeFieldContainer[
        _vega_pb2.VolumeBenefitTier
    ]
    end_of_program_timestamp: int
    window_length: int
    ended_at: int
    def __init__(
        self,
        version: _Optional[int] = ...,
        id: _Optional[str] = ...,
        benefit_tiers: _Optional[
            _Iterable[_Union[_vega_pb2.VolumeBenefitTier, _Mapping]]
        ] = ...,
        end_of_program_timestamp: _Optional[int] = ...,
        window_length: _Optional[int] = ...,
        ended_at: _Optional[int] = ...,
    ) -> None: ...

class FeesStatsForParty(_message.Message):
    __slots__ = (
        "asset_id",
        "total_rewards_received",
        "referees_discount_applied",
        "volume_discount_applied",
        "total_maker_fees_received",
    )
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REWARDS_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    REFEREES_DISCOUNT_APPLIED_FIELD_NUMBER: _ClassVar[int]
    VOLUME_DISCOUNT_APPLIED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_MAKER_FEES_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    total_rewards_received: str
    referees_discount_applied: str
    volume_discount_applied: str
    total_maker_fees_received: str
    def __init__(
        self,
        asset_id: _Optional[str] = ...,
        total_rewards_received: _Optional[str] = ...,
        referees_discount_applied: _Optional[str] = ...,
        volume_discount_applied: _Optional[str] = ...,
        total_maker_fees_received: _Optional[str] = ...,
    ) -> None: ...

class ObserveTransactionResultsRequest(_message.Message):
    __slots__ = ("party_ids", "hashes", "status")
    PARTY_IDS_FIELD_NUMBER: _ClassVar[int]
    HASHES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    party_ids: _containers.RepeatedScalarFieldContainer[str]
    hashes: _containers.RepeatedScalarFieldContainer[str]
    status: bool
    def __init__(
        self,
        party_ids: _Optional[_Iterable[str]] = ...,
        hashes: _Optional[_Iterable[str]] = ...,
        status: bool = ...,
    ) -> None: ...

class ObserveTransactionResultsResponse(_message.Message):
    __slots__ = ("transaction_results",)
    TRANSACTION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    transaction_results: _containers.RepeatedCompositeFieldContainer[
        _events_pb2.TransactionResult
    ]
    def __init__(
        self,
        transaction_results: _Optional[
            _Iterable[_Union[_events_pb2.TransactionResult, _Mapping]]
        ] = ...,
    ) -> None: ...

class EstimateTransferFeeRequest(_message.Message):
    __slots__ = (
        "from_account",
        "from_account_type",
        "to_account",
        "amount",
        "asset_id",
    )
    FROM_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    FROM_ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TO_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    from_account: str
    from_account_type: _vega_pb2.AccountType
    to_account: str
    amount: str
    asset_id: str
    def __init__(
        self,
        from_account: _Optional[str] = ...,
        from_account_type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
        to_account: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        asset_id: _Optional[str] = ...,
    ) -> None: ...

class EstimateTransferFeeResponse(_message.Message):
    __slots__ = ("fee", "discount")
    FEE_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    fee: str
    discount: str
    def __init__(
        self, fee: _Optional[str] = ..., discount: _Optional[str] = ...
    ) -> None: ...

class GetTotalTransferFeeDiscountRequest(_message.Message):
    __slots__ = ("party_id", "asset_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    asset_id: str
    def __init__(
        self, party_id: _Optional[str] = ..., asset_id: _Optional[str] = ...
    ) -> None: ...

class GetTotalTransferFeeDiscountResponse(_message.Message):
    __slots__ = ("total_discount",)
    TOTAL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    total_discount: str
    def __init__(self, total_discount: _Optional[str] = ...) -> None: ...
