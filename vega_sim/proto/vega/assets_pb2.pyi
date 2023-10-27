from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class Asset(_message.Message):
    __slots__ = ["id", "details", "status"]

    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        STATUS_UNSPECIFIED: _ClassVar[Asset.Status]
        STATUS_PROPOSED: _ClassVar[Asset.Status]
        STATUS_REJECTED: _ClassVar[Asset.Status]
        STATUS_PENDING_LISTING: _ClassVar[Asset.Status]
        STATUS_ENABLED: _ClassVar[Asset.Status]
    STATUS_UNSPECIFIED: Asset.Status
    STATUS_PROPOSED: Asset.Status
    STATUS_REJECTED: Asset.Status
    STATUS_PENDING_LISTING: Asset.Status
    STATUS_ENABLED: Asset.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    details: AssetDetails
    status: Asset.Status
    def __init__(
        self,
        id: _Optional[str] = ...,
        details: _Optional[_Union[AssetDetails, _Mapping]] = ...,
        status: _Optional[_Union[Asset.Status, str]] = ...,
    ) -> None: ...

class AssetDetails(_message.Message):
    __slots__ = ["name", "symbol", "decimals", "quantum", "builtin_asset", "erc20"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DECIMALS_FIELD_NUMBER: _ClassVar[int]
    QUANTUM_FIELD_NUMBER: _ClassVar[int]
    BUILTIN_ASSET_FIELD_NUMBER: _ClassVar[int]
    ERC20_FIELD_NUMBER: _ClassVar[int]
    name: str
    symbol: str
    decimals: int
    quantum: str
    builtin_asset: BuiltinAsset
    erc20: ERC20
    def __init__(
        self,
        name: _Optional[str] = ...,
        symbol: _Optional[str] = ...,
        decimals: _Optional[int] = ...,
        quantum: _Optional[str] = ...,
        builtin_asset: _Optional[_Union[BuiltinAsset, _Mapping]] = ...,
        erc20: _Optional[_Union[ERC20, _Mapping]] = ...,
    ) -> None: ...

class BuiltinAsset(_message.Message):
    __slots__ = ["max_faucet_amount_mint"]
    MAX_FAUCET_AMOUNT_MINT_FIELD_NUMBER: _ClassVar[int]
    max_faucet_amount_mint: str
    def __init__(self, max_faucet_amount_mint: _Optional[str] = ...) -> None: ...

class ERC20(_message.Message):
    __slots__ = ["contract_address", "lifetime_limit", "withdraw_threshold"]
    CONTRACT_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    LIFETIME_LIMIT_FIELD_NUMBER: _ClassVar[int]
    WITHDRAW_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    contract_address: str
    lifetime_limit: str
    withdraw_threshold: str
    def __init__(
        self,
        contract_address: _Optional[str] = ...,
        lifetime_limit: _Optional[str] = ...,
        withdraw_threshold: _Optional[str] = ...,
    ) -> None: ...

class AssetDetailsUpdate(_message.Message):
    __slots__ = ["quantum", "erc20"]
    QUANTUM_FIELD_NUMBER: _ClassVar[int]
    ERC20_FIELD_NUMBER: _ClassVar[int]
    quantum: str
    erc20: ERC20Update
    def __init__(
        self,
        quantum: _Optional[str] = ...,
        erc20: _Optional[_Union[ERC20Update, _Mapping]] = ...,
    ) -> None: ...

class ERC20Update(_message.Message):
    __slots__ = ["lifetime_limit", "withdraw_threshold"]
    LIFETIME_LIMIT_FIELD_NUMBER: _ClassVar[int]
    WITHDRAW_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    lifetime_limit: str
    withdraw_threshold: str
    def __init__(
        self,
        lifetime_limit: _Optional[str] = ...,
        withdraw_threshold: _Optional[str] = ...,
    ) -> None: ...
