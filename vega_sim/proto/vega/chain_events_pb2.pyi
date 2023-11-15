from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class EthContractCallEvent(_message.Message):
    __slots__ = ("spec_id", "block_height", "block_time", "result", "error")
    SPEC_ID_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    spec_id: str
    block_height: int
    block_time: int
    result: bytes
    error: str
    def __init__(
        self,
        spec_id: _Optional[str] = ...,
        block_height: _Optional[int] = ...,
        block_time: _Optional[int] = ...,
        result: _Optional[bytes] = ...,
        error: _Optional[str] = ...,
    ) -> None: ...

class BuiltinAssetDeposit(_message.Message):
    __slots__ = ("vega_asset_id", "party_id", "amount")
    VEGA_ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    vega_asset_id: str
    party_id: str
    amount: str
    def __init__(
        self,
        vega_asset_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        amount: _Optional[str] = ...,
    ) -> None: ...

class BuiltinAssetWithdrawal(_message.Message):
    __slots__ = ("vega_asset_id", "party_id", "amount")
    VEGA_ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    vega_asset_id: str
    party_id: str
    amount: str
    def __init__(
        self,
        vega_asset_id: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        amount: _Optional[str] = ...,
    ) -> None: ...

class BuiltinAssetEvent(_message.Message):
    __slots__ = ("deposit", "withdrawal")
    DEPOSIT_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWAL_FIELD_NUMBER: _ClassVar[int]
    deposit: BuiltinAssetDeposit
    withdrawal: BuiltinAssetWithdrawal
    def __init__(
        self,
        deposit: _Optional[_Union[BuiltinAssetDeposit, _Mapping]] = ...,
        withdrawal: _Optional[_Union[BuiltinAssetWithdrawal, _Mapping]] = ...,
    ) -> None: ...

class ERC20AssetList(_message.Message):
    __slots__ = ("vega_asset_id", "asset_source")
    VEGA_ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_SOURCE_FIELD_NUMBER: _ClassVar[int]
    vega_asset_id: str
    asset_source: str
    def __init__(
        self, vega_asset_id: _Optional[str] = ..., asset_source: _Optional[str] = ...
    ) -> None: ...

class ERC20AssetDelist(_message.Message):
    __slots__ = ("vega_asset_id",)
    VEGA_ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    vega_asset_id: str
    def __init__(self, vega_asset_id: _Optional[str] = ...) -> None: ...

class ERC20AssetLimitsUpdated(_message.Message):
    __slots__ = (
        "vega_asset_id",
        "source_ethereum_address",
        "lifetime_limits",
        "withdraw_threshold",
    )
    VEGA_ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    LIFETIME_LIMITS_FIELD_NUMBER: _ClassVar[int]
    WITHDRAW_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    vega_asset_id: str
    source_ethereum_address: str
    lifetime_limits: str
    withdraw_threshold: str
    def __init__(
        self,
        vega_asset_id: _Optional[str] = ...,
        source_ethereum_address: _Optional[str] = ...,
        lifetime_limits: _Optional[str] = ...,
        withdraw_threshold: _Optional[str] = ...,
    ) -> None: ...

class ERC20Deposit(_message.Message):
    __slots__ = (
        "vega_asset_id",
        "source_ethereum_address",
        "target_party_id",
        "amount",
    )
    VEGA_ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TARGET_PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    vega_asset_id: str
    source_ethereum_address: str
    target_party_id: str
    amount: str
    def __init__(
        self,
        vega_asset_id: _Optional[str] = ...,
        source_ethereum_address: _Optional[str] = ...,
        target_party_id: _Optional[str] = ...,
        amount: _Optional[str] = ...,
    ) -> None: ...

class ERC20Withdrawal(_message.Message):
    __slots__ = ("vega_asset_id", "target_ethereum_address", "reference_nonce")
    VEGA_ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_NONCE_FIELD_NUMBER: _ClassVar[int]
    vega_asset_id: str
    target_ethereum_address: str
    reference_nonce: str
    def __init__(
        self,
        vega_asset_id: _Optional[str] = ...,
        target_ethereum_address: _Optional[str] = ...,
        reference_nonce: _Optional[str] = ...,
    ) -> None: ...

class ERC20Event(_message.Message):
    __slots__ = (
        "index",
        "block",
        "asset_list",
        "asset_delist",
        "deposit",
        "withdrawal",
        "asset_limits_updated",
        "bridge_stopped",
        "bridge_resumed",
    )
    INDEX_FIELD_NUMBER: _ClassVar[int]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    ASSET_LIST_FIELD_NUMBER: _ClassVar[int]
    ASSET_DELIST_FIELD_NUMBER: _ClassVar[int]
    DEPOSIT_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWAL_FIELD_NUMBER: _ClassVar[int]
    ASSET_LIMITS_UPDATED_FIELD_NUMBER: _ClassVar[int]
    BRIDGE_STOPPED_FIELD_NUMBER: _ClassVar[int]
    BRIDGE_RESUMED_FIELD_NUMBER: _ClassVar[int]
    index: int
    block: int
    asset_list: ERC20AssetList
    asset_delist: ERC20AssetDelist
    deposit: ERC20Deposit
    withdrawal: ERC20Withdrawal
    asset_limits_updated: ERC20AssetLimitsUpdated
    bridge_stopped: bool
    bridge_resumed: bool
    def __init__(
        self,
        index: _Optional[int] = ...,
        block: _Optional[int] = ...,
        asset_list: _Optional[_Union[ERC20AssetList, _Mapping]] = ...,
        asset_delist: _Optional[_Union[ERC20AssetDelist, _Mapping]] = ...,
        deposit: _Optional[_Union[ERC20Deposit, _Mapping]] = ...,
        withdrawal: _Optional[_Union[ERC20Withdrawal, _Mapping]] = ...,
        asset_limits_updated: _Optional[
            _Union[ERC20AssetLimitsUpdated, _Mapping]
        ] = ...,
        bridge_stopped: bool = ...,
        bridge_resumed: bool = ...,
    ) -> None: ...

class ERC20SignerAdded(_message.Message):
    __slots__ = ("new_signer", "nonce", "block_time")
    NEW_SIGNER_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    new_signer: str
    nonce: str
    block_time: int
    def __init__(
        self,
        new_signer: _Optional[str] = ...,
        nonce: _Optional[str] = ...,
        block_time: _Optional[int] = ...,
    ) -> None: ...

class ERC20SignerRemoved(_message.Message):
    __slots__ = ("old_signer", "nonce", "block_time")
    OLD_SIGNER_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    old_signer: str
    nonce: str
    block_time: int
    def __init__(
        self,
        old_signer: _Optional[str] = ...,
        nonce: _Optional[str] = ...,
        block_time: _Optional[int] = ...,
    ) -> None: ...

class ERC20ThresholdSet(_message.Message):
    __slots__ = ("new_threshold", "nonce", "block_time")
    NEW_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    new_threshold: int
    nonce: str
    block_time: int
    def __init__(
        self,
        new_threshold: _Optional[int] = ...,
        nonce: _Optional[str] = ...,
        block_time: _Optional[int] = ...,
    ) -> None: ...

class ERC20MultiSigEvent(_message.Message):
    __slots__ = ("index", "block", "signer_added", "signer_removed", "threshold_set")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    SIGNER_ADDED_FIELD_NUMBER: _ClassVar[int]
    SIGNER_REMOVED_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_SET_FIELD_NUMBER: _ClassVar[int]
    index: int
    block: int
    signer_added: ERC20SignerAdded
    signer_removed: ERC20SignerRemoved
    threshold_set: ERC20ThresholdSet
    def __init__(
        self,
        index: _Optional[int] = ...,
        block: _Optional[int] = ...,
        signer_added: _Optional[_Union[ERC20SignerAdded, _Mapping]] = ...,
        signer_removed: _Optional[_Union[ERC20SignerRemoved, _Mapping]] = ...,
        threshold_set: _Optional[_Union[ERC20ThresholdSet, _Mapping]] = ...,
    ) -> None: ...

class StakingEvent(_message.Message):
    __slots__ = ("index", "block", "stake_deposited", "stake_removed", "total_supply")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    STAKE_DEPOSITED_FIELD_NUMBER: _ClassVar[int]
    STAKE_REMOVED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SUPPLY_FIELD_NUMBER: _ClassVar[int]
    index: int
    block: int
    stake_deposited: StakeDeposited
    stake_removed: StakeRemoved
    total_supply: StakeTotalSupply
    def __init__(
        self,
        index: _Optional[int] = ...,
        block: _Optional[int] = ...,
        stake_deposited: _Optional[_Union[StakeDeposited, _Mapping]] = ...,
        stake_removed: _Optional[_Union[StakeRemoved, _Mapping]] = ...,
        total_supply: _Optional[_Union[StakeTotalSupply, _Mapping]] = ...,
    ) -> None: ...

class StakeDeposited(_message.Message):
    __slots__ = ("ethereum_address", "vega_public_key", "amount", "block_time")
    ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    VEGA_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    ethereum_address: str
    vega_public_key: str
    amount: str
    block_time: int
    def __init__(
        self,
        ethereum_address: _Optional[str] = ...,
        vega_public_key: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        block_time: _Optional[int] = ...,
    ) -> None: ...

class StakeRemoved(_message.Message):
    __slots__ = ("ethereum_address", "vega_public_key", "amount", "block_time")
    ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    VEGA_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    ethereum_address: str
    vega_public_key: str
    amount: str
    block_time: int
    def __init__(
        self,
        ethereum_address: _Optional[str] = ...,
        vega_public_key: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        block_time: _Optional[int] = ...,
    ) -> None: ...

class StakeTotalSupply(_message.Message):
    __slots__ = ("token_address", "total_supply")
    TOKEN_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SUPPLY_FIELD_NUMBER: _ClassVar[int]
    token_address: str
    total_supply: str
    def __init__(
        self, token_address: _Optional[str] = ..., total_supply: _Optional[str] = ...
    ) -> None: ...
