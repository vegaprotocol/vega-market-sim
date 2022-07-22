# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/commands/v1/validator_commands.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ... import vega_pb2 as vega_dot_vega__pb2
from ... import chain_events_pb2 as vega_dot_chain__events__pb2
from ...commands.v1 import signature_pb2 as vega_dot_commands_dot_v1_dot_signature__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n)vega/commands/v1/validator_commands.proto\x12\x10vega.commands.v1\x1a\x0fvega/vega.proto\x1a\x17vega/chain_events.proto\x1a vega/commands/v1/signature.proto"\x93\x01\n\x12ValidatorHeartbeat\x12\x0f\n\x07node_id\x18\x01 \x01(\t\x12\x37\n\x12\x65thereum_signature\x18\x02 \x01(\x0b\x32\x1b.vega.commands.v1.Signature\x12\x33\n\x0evega_signature\x18\x03 \x01(\x0b\x32\x1b.vega.commands.v1.Signature"\xc4\x02\n\x0c\x41nnounceNode\x12\x14\n\x0cvega_pub_key\x18\x01 \x01(\t\x12\x18\n\x10\x65thereum_address\x18\x02 \x01(\t\x12\x15\n\rchain_pub_key\x18\x03 \x01(\t\x12\x10\n\x08info_url\x18\x04 \x01(\t\x12\x0f\n\x07\x63ountry\x18\x05 \x01(\t\x12\n\n\x02id\x18\x06 \x01(\t\x12\x0c\n\x04name\x18\x07 \x01(\t\x12\x12\n\navatar_url\x18\x08 \x01(\t\x12\x1a\n\x12vega_pub_key_index\x18\t \x01(\r\x12\x12\n\nfrom_epoch\x18\n \x01(\x04\x12\x37\n\x12\x65thereum_signature\x18\x0b \x01(\x0b\x32\x1b.vega.commands.v1.Signature\x12\x33\n\x0evega_signature\x18\x0c \x01(\x0b\x32\x1b.vega.commands.v1.Signature"#\n\x08NodeVote\x12\x11\n\treference\x18\x02 \x01(\tJ\x04\x08\x01\x10\x02"[\n\rNodeSignature\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0b\n\x03sig\x18\x02 \x01(\x0c\x12\x31\n\x04kind\x18\x03 \x01(\x0e\x32#.vega.commands.v1.NodeSignatureKind"\xf7\x01\n\nChainEvent\x12\r\n\x05tx_id\x18\x01 \x01(\t\x12\r\n\x05nonce\x18\x02 \x01(\x04\x12+\n\x07\x62uiltin\x18\xe9\x07 \x01(\x0b\x32\x17.vega.BuiltinAssetEventH\x00\x12"\n\x05\x65rc20\x18\xea\x07 \x01(\x0b\x32\x10.vega.ERC20EventH\x00\x12,\n\rstaking_event\x18\xed\x07 \x01(\x0b\x32\x12.vega.StakingEventH\x00\x12\x33\n\x0e\x65rc20_multisig\x18\xee\x07 \x01(\x0b\x32\x18.vega.ERC20MultiSigEventH\x00\x42\x07\n\x05\x65ventJ\x06\x08\xeb\x07\x10\xec\x07J\x06\x08\xec\x07\x10\xed\x07"y\n\x13KeyRotateSubmission\x12\x19\n\x11new_pub_key_index\x18\x01 \x01(\r\x12\x14\n\x0ctarget_block\x18\x02 \x01(\x04\x12\x13\n\x0bnew_pub_key\x18\x03 \x01(\t\x12\x1c\n\x14\x63urrent_pub_key_hash\x18\x04 \x01(\t"a\n\x1b\x45thereumKeyRotateSubmission\x12\x14\n\x0ctarget_block\x18\x01 \x01(\x04\x12\x13\n\x0bnew_address\x18\x02 \x01(\t\x12\x17\n\x0f\x63urrent_address\x18\x03 \x01(\t"C\n\x15StateVariableProposal\x12*\n\x08proposal\x18\x01 \x01(\x0b\x32\x18.vega.StateValueProposal"p\n\x17ProtocolUpgradeProposal\x12\x1c\n\x14upgrade_block_height\x18\x01 \x01(\x04\x12\x18\n\x10vega_release_tag\x18\x02 \x01(\t\x12\x1d\n\x15\x64\x61ta_node_release_tag\x18\x03 \x01(\t*\x97\x02\n\x11NodeSignatureKind\x12#\n\x1fNODE_SIGNATURE_KIND_UNSPECIFIED\x10\x00\x12!\n\x1dNODE_SIGNATURE_KIND_ASSET_NEW\x10\x01\x12(\n$NODE_SIGNATURE_KIND_ASSET_WITHDRAWAL\x10\x02\x12\x33\n/NODE_SIGNATURE_KIND_ERC20_MULTISIG_SIGNER_ADDED\x10\x03\x12\x35\n1NODE_SIGNATURE_KIND_ERC20_MULTISIG_SIGNER_REMOVED\x10\x04\x12$\n NODE_SIGNATURE_KIND_ASSET_UPDATE\x10\x05\x42.Z,code.vegaprotocol.io/protos/vega/commands/v1b\x06proto3'
)

_NODESIGNATUREKIND = DESCRIPTOR.enum_types_by_name["NodeSignatureKind"]
NodeSignatureKind = enum_type_wrapper.EnumTypeWrapper(_NODESIGNATUREKIND)
NODE_SIGNATURE_KIND_UNSPECIFIED = 0
NODE_SIGNATURE_KIND_ASSET_NEW = 1
NODE_SIGNATURE_KIND_ASSET_WITHDRAWAL = 2
NODE_SIGNATURE_KIND_ERC20_MULTISIG_SIGNER_ADDED = 3
NODE_SIGNATURE_KIND_ERC20_MULTISIG_SIGNER_REMOVED = 4
NODE_SIGNATURE_KIND_ASSET_UPDATE = 5


_VALIDATORHEARTBEAT = DESCRIPTOR.message_types_by_name["ValidatorHeartbeat"]
_ANNOUNCENODE = DESCRIPTOR.message_types_by_name["AnnounceNode"]
_NODEVOTE = DESCRIPTOR.message_types_by_name["NodeVote"]
_NODESIGNATURE = DESCRIPTOR.message_types_by_name["NodeSignature"]
_CHAINEVENT = DESCRIPTOR.message_types_by_name["ChainEvent"]
_KEYROTATESUBMISSION = DESCRIPTOR.message_types_by_name["KeyRotateSubmission"]
_ETHEREUMKEYROTATESUBMISSION = DESCRIPTOR.message_types_by_name[
    "EthereumKeyRotateSubmission"
]
_STATEVARIABLEPROPOSAL = DESCRIPTOR.message_types_by_name["StateVariableProposal"]
_PROTOCOLUPGRADEPROPOSAL = DESCRIPTOR.message_types_by_name["ProtocolUpgradeProposal"]
ValidatorHeartbeat = _reflection.GeneratedProtocolMessageType(
    "ValidatorHeartbeat",
    (_message.Message,),
    {
        "DESCRIPTOR": _VALIDATORHEARTBEAT,
        "__module__": "vega.commands.v1.validator_commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.ValidatorHeartbeat)
    },
)
_sym_db.RegisterMessage(ValidatorHeartbeat)

AnnounceNode = _reflection.GeneratedProtocolMessageType(
    "AnnounceNode",
    (_message.Message,),
    {
        "DESCRIPTOR": _ANNOUNCENODE,
        "__module__": "vega.commands.v1.validator_commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.AnnounceNode)
    },
)
_sym_db.RegisterMessage(AnnounceNode)

NodeVote = _reflection.GeneratedProtocolMessageType(
    "NodeVote",
    (_message.Message,),
    {
        "DESCRIPTOR": _NODEVOTE,
        "__module__": "vega.commands.v1.validator_commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.NodeVote)
    },
)
_sym_db.RegisterMessage(NodeVote)

NodeSignature = _reflection.GeneratedProtocolMessageType(
    "NodeSignature",
    (_message.Message,),
    {
        "DESCRIPTOR": _NODESIGNATURE,
        "__module__": "vega.commands.v1.validator_commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.NodeSignature)
    },
)
_sym_db.RegisterMessage(NodeSignature)

ChainEvent = _reflection.GeneratedProtocolMessageType(
    "ChainEvent",
    (_message.Message,),
    {
        "DESCRIPTOR": _CHAINEVENT,
        "__module__": "vega.commands.v1.validator_commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.ChainEvent)
    },
)
_sym_db.RegisterMessage(ChainEvent)

KeyRotateSubmission = _reflection.GeneratedProtocolMessageType(
    "KeyRotateSubmission",
    (_message.Message,),
    {
        "DESCRIPTOR": _KEYROTATESUBMISSION,
        "__module__": "vega.commands.v1.validator_commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.KeyRotateSubmission)
    },
)
_sym_db.RegisterMessage(KeyRotateSubmission)

EthereumKeyRotateSubmission = _reflection.GeneratedProtocolMessageType(
    "EthereumKeyRotateSubmission",
    (_message.Message,),
    {
        "DESCRIPTOR": _ETHEREUMKEYROTATESUBMISSION,
        "__module__": "vega.commands.v1.validator_commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.EthereumKeyRotateSubmission)
    },
)
_sym_db.RegisterMessage(EthereumKeyRotateSubmission)

StateVariableProposal = _reflection.GeneratedProtocolMessageType(
    "StateVariableProposal",
    (_message.Message,),
    {
        "DESCRIPTOR": _STATEVARIABLEPROPOSAL,
        "__module__": "vega.commands.v1.validator_commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.StateVariableProposal)
    },
)
_sym_db.RegisterMessage(StateVariableProposal)

ProtocolUpgradeProposal = _reflection.GeneratedProtocolMessageType(
    "ProtocolUpgradeProposal",
    (_message.Message,),
    {
        "DESCRIPTOR": _PROTOCOLUPGRADEPROPOSAL,
        "__module__": "vega.commands.v1.validator_commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.ProtocolUpgradeProposal)
    },
)
_sym_db.RegisterMessage(ProtocolUpgradeProposal)

if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z,code.vegaprotocol.io/protos/vega/commands/v1"
    _NODESIGNATUREKIND._serialized_start = 1402
    _NODESIGNATUREKIND._serialized_end = 1681
    _VALIDATORHEARTBEAT._serialized_start = 140
    _VALIDATORHEARTBEAT._serialized_end = 287
    _ANNOUNCENODE._serialized_start = 290
    _ANNOUNCENODE._serialized_end = 614
    _NODEVOTE._serialized_start = 616
    _NODEVOTE._serialized_end = 651
    _NODESIGNATURE._serialized_start = 653
    _NODESIGNATURE._serialized_end = 744
    _CHAINEVENT._serialized_start = 747
    _CHAINEVENT._serialized_end = 994
    _KEYROTATESUBMISSION._serialized_start = 996
    _KEYROTATESUBMISSION._serialized_end = 1117
    _ETHEREUMKEYROTATESUBMISSION._serialized_start = 1119
    _ETHEREUMKEYROTATESUBMISSION._serialized_end = 1216
    _STATEVARIABLEPROPOSAL._serialized_start = 1218
    _STATEVARIABLEPROPOSAL._serialized_end = 1285
    _PROTOCOLUPGRADEPROPOSAL._serialized_start = 1287
    _PROTOCOLUPGRADEPROPOSAL._serialized_end = 1399
# @@protoc_insertion_point(module_scope)
