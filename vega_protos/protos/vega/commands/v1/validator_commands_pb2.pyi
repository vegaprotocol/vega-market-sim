from vega import chain_events_pb2 as _chain_events_pb2
from vega.commands.v1 import signature_pb2 as _signature_pb2
from vega import vega_pb2 as _vega_pb2
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

class NodeSignatureKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NODE_SIGNATURE_KIND_UNSPECIFIED: _ClassVar[NodeSignatureKind]
    NODE_SIGNATURE_KIND_ASSET_NEW: _ClassVar[NodeSignatureKind]
    NODE_SIGNATURE_KIND_ASSET_WITHDRAWAL: _ClassVar[NodeSignatureKind]
    NODE_SIGNATURE_KIND_ERC20_MULTISIG_SIGNER_ADDED: _ClassVar[NodeSignatureKind]
    NODE_SIGNATURE_KIND_ERC20_MULTISIG_SIGNER_REMOVED: _ClassVar[NodeSignatureKind]
    NODE_SIGNATURE_KIND_ASSET_UPDATE: _ClassVar[NodeSignatureKind]

NODE_SIGNATURE_KIND_UNSPECIFIED: NodeSignatureKind
NODE_SIGNATURE_KIND_ASSET_NEW: NodeSignatureKind
NODE_SIGNATURE_KIND_ASSET_WITHDRAWAL: NodeSignatureKind
NODE_SIGNATURE_KIND_ERC20_MULTISIG_SIGNER_ADDED: NodeSignatureKind
NODE_SIGNATURE_KIND_ERC20_MULTISIG_SIGNER_REMOVED: NodeSignatureKind
NODE_SIGNATURE_KIND_ASSET_UPDATE: NodeSignatureKind

class ValidatorHeartbeat(_message.Message):
    __slots__ = ("node_id", "ethereum_signature", "vega_signature", "message")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    VEGA_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    ethereum_signature: _signature_pb2.Signature
    vega_signature: _signature_pb2.Signature
    message: str
    def __init__(
        self,
        node_id: _Optional[str] = ...,
        ethereum_signature: _Optional[_Union[_signature_pb2.Signature, _Mapping]] = ...,
        vega_signature: _Optional[_Union[_signature_pb2.Signature, _Mapping]] = ...,
        message: _Optional[str] = ...,
    ) -> None: ...

class AnnounceNode(_message.Message):
    __slots__ = (
        "vega_pub_key",
        "ethereum_address",
        "chain_pub_key",
        "info_url",
        "country",
        "id",
        "name",
        "avatar_url",
        "vega_pub_key_index",
        "from_epoch",
        "ethereum_signature",
        "vega_signature",
        "submitter_address",
    )
    VEGA_PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CHAIN_PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    INFO_URL_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    VEGA_PUB_KEY_INDEX_FIELD_NUMBER: _ClassVar[int]
    FROM_EPOCH_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    VEGA_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    vega_pub_key: str
    ethereum_address: str
    chain_pub_key: str
    info_url: str
    country: str
    id: str
    name: str
    avatar_url: str
    vega_pub_key_index: int
    from_epoch: int
    ethereum_signature: _signature_pb2.Signature
    vega_signature: _signature_pb2.Signature
    submitter_address: str
    def __init__(
        self,
        vega_pub_key: _Optional[str] = ...,
        ethereum_address: _Optional[str] = ...,
        chain_pub_key: _Optional[str] = ...,
        info_url: _Optional[str] = ...,
        country: _Optional[str] = ...,
        id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        avatar_url: _Optional[str] = ...,
        vega_pub_key_index: _Optional[int] = ...,
        from_epoch: _Optional[int] = ...,
        ethereum_signature: _Optional[_Union[_signature_pb2.Signature, _Mapping]] = ...,
        vega_signature: _Optional[_Union[_signature_pb2.Signature, _Mapping]] = ...,
        submitter_address: _Optional[str] = ...,
    ) -> None: ...

class NodeVote(_message.Message):
    __slots__ = ("reference", "type")

    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[NodeVote.Type]
        TYPE_STAKE_DEPOSITED: _ClassVar[NodeVote.Type]
        TYPE_STAKE_REMOVED: _ClassVar[NodeVote.Type]
        TYPE_FUNDS_DEPOSITED: _ClassVar[NodeVote.Type]
        TYPE_SIGNER_ADDED: _ClassVar[NodeVote.Type]
        TYPE_SIGNER_REMOVED: _ClassVar[NodeVote.Type]
        TYPE_BRIDGE_STOPPED: _ClassVar[NodeVote.Type]
        TYPE_BRIDGE_RESUMED: _ClassVar[NodeVote.Type]
        TYPE_ASSET_LISTED: _ClassVar[NodeVote.Type]
        TYPE_LIMITS_UPDATED: _ClassVar[NodeVote.Type]
        TYPE_STAKE_TOTAL_SUPPLY: _ClassVar[NodeVote.Type]
        TYPE_SIGNER_THRESHOLD_SET: _ClassVar[NodeVote.Type]
        TYPE_GOVERNANCE_VALIDATE_ASSET: _ClassVar[NodeVote.Type]
        TYPE_ETHEREUM_CONTRACT_CALL_RESULT: _ClassVar[NodeVote.Type]
        TYPE_ETHEREUM_HEARTBEAT: _ClassVar[NodeVote.Type]

    TYPE_UNSPECIFIED: NodeVote.Type
    TYPE_STAKE_DEPOSITED: NodeVote.Type
    TYPE_STAKE_REMOVED: NodeVote.Type
    TYPE_FUNDS_DEPOSITED: NodeVote.Type
    TYPE_SIGNER_ADDED: NodeVote.Type
    TYPE_SIGNER_REMOVED: NodeVote.Type
    TYPE_BRIDGE_STOPPED: NodeVote.Type
    TYPE_BRIDGE_RESUMED: NodeVote.Type
    TYPE_ASSET_LISTED: NodeVote.Type
    TYPE_LIMITS_UPDATED: NodeVote.Type
    TYPE_STAKE_TOTAL_SUPPLY: NodeVote.Type
    TYPE_SIGNER_THRESHOLD_SET: NodeVote.Type
    TYPE_GOVERNANCE_VALIDATE_ASSET: NodeVote.Type
    TYPE_ETHEREUM_CONTRACT_CALL_RESULT: NodeVote.Type
    TYPE_ETHEREUM_HEARTBEAT: NodeVote.Type
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    reference: str
    type: NodeVote.Type
    def __init__(
        self,
        reference: _Optional[str] = ...,
        type: _Optional[_Union[NodeVote.Type, str]] = ...,
    ) -> None: ...

class NodeSignature(_message.Message):
    __slots__ = ("id", "sig", "kind")
    ID_FIELD_NUMBER: _ClassVar[int]
    SIG_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    id: str
    sig: bytes
    kind: NodeSignatureKind
    def __init__(
        self,
        id: _Optional[str] = ...,
        sig: _Optional[bytes] = ...,
        kind: _Optional[_Union[NodeSignatureKind, str]] = ...,
    ) -> None: ...

class ChainEvent(_message.Message):
    __slots__ = (
        "tx_id",
        "nonce",
        "builtin",
        "erc20",
        "staking_event",
        "erc20_multisig",
        "contract_call",
        "heartbeat",
    )
    TX_ID_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    BUILTIN_FIELD_NUMBER: _ClassVar[int]
    ERC20_FIELD_NUMBER: _ClassVar[int]
    STAKING_EVENT_FIELD_NUMBER: _ClassVar[int]
    ERC20_MULTISIG_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_CALL_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    tx_id: str
    nonce: int
    builtin: _chain_events_pb2.BuiltinAssetEvent
    erc20: _chain_events_pb2.ERC20Event
    staking_event: _chain_events_pb2.StakingEvent
    erc20_multisig: _chain_events_pb2.ERC20MultiSigEvent
    contract_call: _chain_events_pb2.EthContractCallEvent
    heartbeat: _chain_events_pb2.ERC20Heartbeat
    def __init__(
        self,
        tx_id: _Optional[str] = ...,
        nonce: _Optional[int] = ...,
        builtin: _Optional[_Union[_chain_events_pb2.BuiltinAssetEvent, _Mapping]] = ...,
        erc20: _Optional[_Union[_chain_events_pb2.ERC20Event, _Mapping]] = ...,
        staking_event: _Optional[
            _Union[_chain_events_pb2.StakingEvent, _Mapping]
        ] = ...,
        erc20_multisig: _Optional[
            _Union[_chain_events_pb2.ERC20MultiSigEvent, _Mapping]
        ] = ...,
        contract_call: _Optional[
            _Union[_chain_events_pb2.EthContractCallEvent, _Mapping]
        ] = ...,
        heartbeat: _Optional[_Union[_chain_events_pb2.ERC20Heartbeat, _Mapping]] = ...,
    ) -> None: ...

class KeyRotateSubmission(_message.Message):
    __slots__ = (
        "new_pub_key_index",
        "target_block",
        "new_pub_key",
        "current_pub_key_hash",
    )
    NEW_PUB_KEY_INDEX_FIELD_NUMBER: _ClassVar[int]
    TARGET_BLOCK_FIELD_NUMBER: _ClassVar[int]
    NEW_PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PUB_KEY_HASH_FIELD_NUMBER: _ClassVar[int]
    new_pub_key_index: int
    target_block: int
    new_pub_key: str
    current_pub_key_hash: str
    def __init__(
        self,
        new_pub_key_index: _Optional[int] = ...,
        target_block: _Optional[int] = ...,
        new_pub_key: _Optional[str] = ...,
        current_pub_key_hash: _Optional[str] = ...,
    ) -> None: ...

class EthereumKeyRotateSubmission(_message.Message):
    __slots__ = (
        "target_block",
        "new_address",
        "current_address",
        "submitter_address",
        "ethereum_signature",
    )
    TARGET_BLOCK_FIELD_NUMBER: _ClassVar[int]
    NEW_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    target_block: int
    new_address: str
    current_address: str
    submitter_address: str
    ethereum_signature: _signature_pb2.Signature
    def __init__(
        self,
        target_block: _Optional[int] = ...,
        new_address: _Optional[str] = ...,
        current_address: _Optional[str] = ...,
        submitter_address: _Optional[str] = ...,
        ethereum_signature: _Optional[_Union[_signature_pb2.Signature, _Mapping]] = ...,
    ) -> None: ...

class StateVariableProposal(_message.Message):
    __slots__ = ("proposal",)
    PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    proposal: _vega_pb2.StateValueProposal
    def __init__(
        self, proposal: _Optional[_Union[_vega_pb2.StateValueProposal, _Mapping]] = ...
    ) -> None: ...

class ProtocolUpgradeProposal(_message.Message):
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
