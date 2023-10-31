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

class ETHAddress(_message.Message):
    __slots__ = ["address"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...

class PubKey(_message.Message):
    __slots__ = ["key"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class Signer(_message.Message):
    __slots__ = ["pub_key", "eth_address"]
    PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    ETH_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    pub_key: PubKey
    eth_address: ETHAddress
    def __init__(
        self,
        pub_key: _Optional[_Union[PubKey, _Mapping]] = ...,
        eth_address: _Optional[_Union[ETHAddress, _Mapping]] = ...,
    ) -> None: ...

class Property(_message.Message):
    __slots__ = ["name", "value"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(
        self, name: _Optional[str] = ..., value: _Optional[str] = ...
    ) -> None: ...

class Data(_message.Message):
    __slots__ = [
        "signers",
        "data",
        "matched_spec_ids",
        "broadcast_at",
        "meta_data",
        "error",
    ]
    SIGNERS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    MATCHED_SPEC_IDS_FIELD_NUMBER: _ClassVar[int]
    BROADCAST_AT_FIELD_NUMBER: _ClassVar[int]
    META_DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    signers: _containers.RepeatedCompositeFieldContainer[Signer]
    data: _containers.RepeatedCompositeFieldContainer[Property]
    matched_spec_ids: _containers.RepeatedScalarFieldContainer[str]
    broadcast_at: int
    meta_data: _containers.RepeatedCompositeFieldContainer[Property]
    error: str
    def __init__(
        self,
        signers: _Optional[_Iterable[_Union[Signer, _Mapping]]] = ...,
        data: _Optional[_Iterable[_Union[Property, _Mapping]]] = ...,
        matched_spec_ids: _Optional[_Iterable[str]] = ...,
        broadcast_at: _Optional[int] = ...,
        meta_data: _Optional[_Iterable[_Union[Property, _Mapping]]] = ...,
        error: _Optional[str] = ...,
    ) -> None: ...

class ExternalData(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: Data
    def __init__(self, data: _Optional[_Union[Data, _Mapping]] = ...) -> None: ...
