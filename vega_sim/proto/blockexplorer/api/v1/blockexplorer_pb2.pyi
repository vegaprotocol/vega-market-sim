from google.api import field_behavior_pb2 as _field_behavior_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2
from vega.commands.v1 import signature_pb2 as _signature_pb2
from vega.commands.v1 import transaction_pb2 as _transaction_pb2
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

class InfoRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class InfoResponse(_message.Message):
    __slots__ = ["version", "commit_hash"]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    COMMIT_HASH_FIELD_NUMBER: _ClassVar[int]
    version: str
    commit_hash: str
    def __init__(
        self, version: _Optional[str] = ..., commit_hash: _Optional[str] = ...
    ) -> None: ...

class GetTransactionRequest(_message.Message):
    __slots__ = ["hash"]
    HASH_FIELD_NUMBER: _ClassVar[int]
    hash: str
    def __init__(self, hash: _Optional[str] = ...) -> None: ...

class GetTransactionResponse(_message.Message):
    __slots__ = ["transaction"]
    TRANSACTION_FIELD_NUMBER: _ClassVar[int]
    transaction: Transaction
    def __init__(
        self, transaction: _Optional[_Union[Transaction, _Mapping]] = ...
    ) -> None: ...

class ListTransactionsRequest(_message.Message):
    __slots__ = [
        "limit",
        "before",
        "after",
        "filters",
        "cmd_types",
        "exclude_cmd_types",
        "parties",
        "first",
        "last",
    ]

    class FiltersEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    BEFORE_FIELD_NUMBER: _ClassVar[int]
    AFTER_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    CMD_TYPES_FIELD_NUMBER: _ClassVar[int]
    EXCLUDE_CMD_TYPES_FIELD_NUMBER: _ClassVar[int]
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    FIRST_FIELD_NUMBER: _ClassVar[int]
    LAST_FIELD_NUMBER: _ClassVar[int]
    limit: int
    before: str
    after: str
    filters: _containers.ScalarMap[str, str]
    cmd_types: _containers.RepeatedScalarFieldContainer[str]
    exclude_cmd_types: _containers.RepeatedScalarFieldContainer[str]
    parties: _containers.RepeatedScalarFieldContainer[str]
    first: int
    last: int
    def __init__(
        self,
        limit: _Optional[int] = ...,
        before: _Optional[str] = ...,
        after: _Optional[str] = ...,
        filters: _Optional[_Mapping[str, str]] = ...,
        cmd_types: _Optional[_Iterable[str]] = ...,
        exclude_cmd_types: _Optional[_Iterable[str]] = ...,
        parties: _Optional[_Iterable[str]] = ...,
        first: _Optional[int] = ...,
        last: _Optional[int] = ...,
    ) -> None: ...

class ListTransactionsResponse(_message.Message):
    __slots__ = ["transactions"]
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    transactions: _containers.RepeatedCompositeFieldContainer[Transaction]
    def __init__(
        self, transactions: _Optional[_Iterable[_Union[Transaction, _Mapping]]] = ...
    ) -> None: ...

class Transaction(_message.Message):
    __slots__ = [
        "block",
        "index",
        "hash",
        "submitter",
        "type",
        "code",
        "cursor",
        "command",
        "signature",
        "error",
        "created_at",
        "version",
        "pow",
    ]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    POW_FIELD_NUMBER: _ClassVar[int]
    block: int
    index: int
    hash: str
    submitter: str
    type: str
    code: int
    cursor: str
    command: _transaction_pb2.InputData
    signature: _signature_pb2.Signature
    error: str
    created_at: str
    version: _transaction_pb2.TxVersion
    pow: _transaction_pb2.ProofOfWork
    def __init__(
        self,
        block: _Optional[int] = ...,
        index: _Optional[int] = ...,
        hash: _Optional[str] = ...,
        submitter: _Optional[str] = ...,
        type: _Optional[str] = ...,
        code: _Optional[int] = ...,
        cursor: _Optional[str] = ...,
        command: _Optional[_Union[_transaction_pb2.InputData, _Mapping]] = ...,
        signature: _Optional[_Union[_signature_pb2.Signature, _Mapping]] = ...,
        error: _Optional[str] = ...,
        created_at: _Optional[str] = ...,
        version: _Optional[_Union[_transaction_pb2.TxVersion, str]] = ...,
        pow: _Optional[_Union[_transaction_pb2.ProofOfWork, _Mapping]] = ...,
    ) -> None: ...
