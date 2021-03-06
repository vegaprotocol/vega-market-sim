# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/commands/v1/commands.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ... import governance_pb2 as vega_dot_governance__pb2
from ... import vega_pb2 as vega_dot_vega__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1fvega/commands/v1/commands.proto\x12\x10vega.commands.v1\x1a\x15vega/governance.proto\x1a\x0fvega/vega.proto"\x1b\n\nInt64Value\x12\r\n\x05value\x18\x01 \x01(\x03"\xfb\x01\n\x0fOrderSubmission\x12\x11\n\tmarket_id\x18\x01 \x01(\t\x12\r\n\x05price\x18\x02 \x01(\t\x12\x0c\n\x04size\x18\x03 \x01(\x04\x12\x18\n\x04side\x18\x04 \x01(\x0e\x32\n.vega.Side\x12.\n\rtime_in_force\x18\x05 \x01(\x0e\x32\x17.vega.Order.TimeInForce\x12\x12\n\nexpires_at\x18\x06 \x01(\x03\x12\x1e\n\x04type\x18\x07 \x01(\x0e\x32\x10.vega.Order.Type\x12\x11\n\treference\x18\x08 \x01(\t\x12\'\n\x0cpegged_order\x18\t \x01(\x0b\x32\x11.vega.PeggedOrder"8\n\x11OrderCancellation\x12\x10\n\x08order_id\x18\x01 \x01(\t\x12\x11\n\tmarket_id\x18\x02 \x01(\t"\x82\x02\n\x0eOrderAmendment\x12\x10\n\x08order_id\x18\x01 \x01(\t\x12\x11\n\tmarket_id\x18\x02 \x01(\t\x12\x1a\n\x05price\x18\x03 \x01(\x0b\x32\x0b.vega.Price\x12\x12\n\nsize_delta\x18\x04 \x01(\x03\x12#\n\nexpires_at\x18\x05 \x01(\x0b\x32\x0f.vega.Timestamp\x12.\n\rtime_in_force\x18\x06 \x01(\x0e\x32\x17.vega.Order.TimeInForce\x12\x15\n\rpegged_offset\x18\x07 \x01(\t\x12/\n\x10pegged_reference\x18\x08 \x01(\x0e\x32\x15.vega.PeggedReference"\xb5\x01\n\x1cLiquidityProvisionSubmission\x12\x11\n\tmarket_id\x18\x01 \x01(\t\x12\x19\n\x11\x63ommitment_amount\x18\x02 \x01(\t\x12\x0b\n\x03\x66\x65\x65\x18\x03 \x01(\t\x12#\n\x05sells\x18\x04 \x03(\x0b\x32\x14.vega.LiquidityOrder\x12"\n\x04\x62uys\x18\x05 \x03(\x0b\x32\x14.vega.LiquidityOrder\x12\x11\n\treference\x18\x06 \x01(\t"3\n\x1eLiquidityProvisionCancellation\x12\x11\n\tmarket_id\x18\x01 \x01(\t"\xb4\x01\n\x1bLiquidityProvisionAmendment\x12\x11\n\tmarket_id\x18\x01 \x01(\t\x12\x19\n\x11\x63ommitment_amount\x18\x02 \x01(\t\x12\x0b\n\x03\x66\x65\x65\x18\x03 \x01(\t\x12#\n\x05sells\x18\x04 \x03(\x0b\x32\x14.vega.LiquidityOrder\x12"\n\x04\x62uys\x18\x05 \x03(\x0b\x32\x14.vega.LiquidityOrder\x12\x11\n\treference\x18\x06 \x01(\t"S\n\x12WithdrawSubmission\x12\x0e\n\x06\x61mount\x18\x01 \x01(\t\x12\r\n\x05\x61sset\x18\x02 \x01(\t\x12\x1e\n\x03\x65xt\x18\x03 \x01(\x0b\x32\x11.vega.WithdrawExt"w\n\x12ProposalSubmission\x12\x11\n\treference\x18\x01 \x01(\t\x12"\n\x05terms\x18\x02 \x01(\x0b\x32\x13.vega.ProposalTerms\x12*\n\trationale\x18\x03 \x01(\x0b\x32\x17.vega.ProposalRationale"F\n\x0eVoteSubmission\x12\x13\n\x0bproposal_id\x18\x01 \x01(\t\x12\x1f\n\x05value\x18\x02 \x01(\x0e\x32\x10.vega.Vote.Value"5\n\x12\x44\x65legateSubmission\x12\x0f\n\x07node_id\x18\x01 \x01(\t\x12\x0e\n\x06\x61mount\x18\x02 \x01(\t"\xd9\x01\n\x14UndelegateSubmission\x12\x0f\n\x07node_id\x18\x01 \x01(\t\x12\x0e\n\x06\x61mount\x18\x02 \x01(\t\x12=\n\x06method\x18\x03 \x01(\x0e\x32-.vega.commands.v1.UndelegateSubmission.Method"a\n\x06Method\x12\x16\n\x12METHOD_UNSPECIFIED\x10\x00\x12\x0e\n\nMETHOD_NOW\x10\x01\x12\x1a\n\x16METHOD_AT_END_OF_EPOCH\x10\x02\x12\x13\n\x0fMETHOD_IN_ANGER\x10\x03"\x99\x02\n\x08Transfer\x12,\n\x11\x66rom_account_type\x18\x01 \x01(\x0e\x32\x11.vega.AccountType\x12\n\n\x02to\x18\x02 \x01(\t\x12*\n\x0fto_account_type\x18\x03 \x01(\x0e\x32\x11.vega.AccountType\x12\r\n\x05\x61sset\x18\x04 \x01(\t\x12\x0e\n\x06\x61mount\x18\x05 \x01(\t\x12\x11\n\treference\x18\x06 \x01(\t\x12\x33\n\x07one_off\x18\x65 \x01(\x0b\x32 .vega.commands.v1.OneOffTransferH\x00\x12\x38\n\trecurring\x18\x66 \x01(\x0b\x32#.vega.commands.v1.RecurringTransferH\x00\x42\x06\n\x04kind"$\n\x0eOneOffTransfer\x12\x12\n\ndeliver_on\x18\x01 \x01(\x03"\x91\x01\n\x11RecurringTransfer\x12\x13\n\x0bstart_epoch\x18\x01 \x01(\x04\x12$\n\tend_epoch\x18\x02 \x01(\x0b\x32\x11.vega.Uint64Value\x12\x0e\n\x06\x66\x61\x63tor\x18\x03 \x01(\t\x12\x31\n\x11\x64ispatch_strategy\x18\x04 \x01(\x0b\x32\x16.vega.DispatchStrategy"%\n\x0e\x43\x61ncelTransfer\x12\x13\n\x0btransfer_id\x18\x01 \x01(\tB.Z,code.vegaprotocol.io/protos/vega/commands/v1b\x06proto3'
)


_INT64VALUE = DESCRIPTOR.message_types_by_name["Int64Value"]
_ORDERSUBMISSION = DESCRIPTOR.message_types_by_name["OrderSubmission"]
_ORDERCANCELLATION = DESCRIPTOR.message_types_by_name["OrderCancellation"]
_ORDERAMENDMENT = DESCRIPTOR.message_types_by_name["OrderAmendment"]
_LIQUIDITYPROVISIONSUBMISSION = DESCRIPTOR.message_types_by_name[
    "LiquidityProvisionSubmission"
]
_LIQUIDITYPROVISIONCANCELLATION = DESCRIPTOR.message_types_by_name[
    "LiquidityProvisionCancellation"
]
_LIQUIDITYPROVISIONAMENDMENT = DESCRIPTOR.message_types_by_name[
    "LiquidityProvisionAmendment"
]
_WITHDRAWSUBMISSION = DESCRIPTOR.message_types_by_name["WithdrawSubmission"]
_PROPOSALSUBMISSION = DESCRIPTOR.message_types_by_name["ProposalSubmission"]
_VOTESUBMISSION = DESCRIPTOR.message_types_by_name["VoteSubmission"]
_DELEGATESUBMISSION = DESCRIPTOR.message_types_by_name["DelegateSubmission"]
_UNDELEGATESUBMISSION = DESCRIPTOR.message_types_by_name["UndelegateSubmission"]
_TRANSFER = DESCRIPTOR.message_types_by_name["Transfer"]
_ONEOFFTRANSFER = DESCRIPTOR.message_types_by_name["OneOffTransfer"]
_RECURRINGTRANSFER = DESCRIPTOR.message_types_by_name["RecurringTransfer"]
_CANCELTRANSFER = DESCRIPTOR.message_types_by_name["CancelTransfer"]
_UNDELEGATESUBMISSION_METHOD = _UNDELEGATESUBMISSION.enum_types_by_name["Method"]
Int64Value = _reflection.GeneratedProtocolMessageType(
    "Int64Value",
    (_message.Message,),
    {
        "DESCRIPTOR": _INT64VALUE,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.Int64Value)
    },
)
_sym_db.RegisterMessage(Int64Value)

OrderSubmission = _reflection.GeneratedProtocolMessageType(
    "OrderSubmission",
    (_message.Message,),
    {
        "DESCRIPTOR": _ORDERSUBMISSION,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.OrderSubmission)
    },
)
_sym_db.RegisterMessage(OrderSubmission)

OrderCancellation = _reflection.GeneratedProtocolMessageType(
    "OrderCancellation",
    (_message.Message,),
    {
        "DESCRIPTOR": _ORDERCANCELLATION,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.OrderCancellation)
    },
)
_sym_db.RegisterMessage(OrderCancellation)

OrderAmendment = _reflection.GeneratedProtocolMessageType(
    "OrderAmendment",
    (_message.Message,),
    {
        "DESCRIPTOR": _ORDERAMENDMENT,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.OrderAmendment)
    },
)
_sym_db.RegisterMessage(OrderAmendment)

LiquidityProvisionSubmission = _reflection.GeneratedProtocolMessageType(
    "LiquidityProvisionSubmission",
    (_message.Message,),
    {
        "DESCRIPTOR": _LIQUIDITYPROVISIONSUBMISSION,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.LiquidityProvisionSubmission)
    },
)
_sym_db.RegisterMessage(LiquidityProvisionSubmission)

LiquidityProvisionCancellation = _reflection.GeneratedProtocolMessageType(
    "LiquidityProvisionCancellation",
    (_message.Message,),
    {
        "DESCRIPTOR": _LIQUIDITYPROVISIONCANCELLATION,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.LiquidityProvisionCancellation)
    },
)
_sym_db.RegisterMessage(LiquidityProvisionCancellation)

LiquidityProvisionAmendment = _reflection.GeneratedProtocolMessageType(
    "LiquidityProvisionAmendment",
    (_message.Message,),
    {
        "DESCRIPTOR": _LIQUIDITYPROVISIONAMENDMENT,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.LiquidityProvisionAmendment)
    },
)
_sym_db.RegisterMessage(LiquidityProvisionAmendment)

WithdrawSubmission = _reflection.GeneratedProtocolMessageType(
    "WithdrawSubmission",
    (_message.Message,),
    {
        "DESCRIPTOR": _WITHDRAWSUBMISSION,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.WithdrawSubmission)
    },
)
_sym_db.RegisterMessage(WithdrawSubmission)

ProposalSubmission = _reflection.GeneratedProtocolMessageType(
    "ProposalSubmission",
    (_message.Message,),
    {
        "DESCRIPTOR": _PROPOSALSUBMISSION,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.ProposalSubmission)
    },
)
_sym_db.RegisterMessage(ProposalSubmission)

VoteSubmission = _reflection.GeneratedProtocolMessageType(
    "VoteSubmission",
    (_message.Message,),
    {
        "DESCRIPTOR": _VOTESUBMISSION,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.VoteSubmission)
    },
)
_sym_db.RegisterMessage(VoteSubmission)

DelegateSubmission = _reflection.GeneratedProtocolMessageType(
    "DelegateSubmission",
    (_message.Message,),
    {
        "DESCRIPTOR": _DELEGATESUBMISSION,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.DelegateSubmission)
    },
)
_sym_db.RegisterMessage(DelegateSubmission)

UndelegateSubmission = _reflection.GeneratedProtocolMessageType(
    "UndelegateSubmission",
    (_message.Message,),
    {
        "DESCRIPTOR": _UNDELEGATESUBMISSION,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.UndelegateSubmission)
    },
)
_sym_db.RegisterMessage(UndelegateSubmission)

Transfer = _reflection.GeneratedProtocolMessageType(
    "Transfer",
    (_message.Message,),
    {
        "DESCRIPTOR": _TRANSFER,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.Transfer)
    },
)
_sym_db.RegisterMessage(Transfer)

OneOffTransfer = _reflection.GeneratedProtocolMessageType(
    "OneOffTransfer",
    (_message.Message,),
    {
        "DESCRIPTOR": _ONEOFFTRANSFER,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.OneOffTransfer)
    },
)
_sym_db.RegisterMessage(OneOffTransfer)

RecurringTransfer = _reflection.GeneratedProtocolMessageType(
    "RecurringTransfer",
    (_message.Message,),
    {
        "DESCRIPTOR": _RECURRINGTRANSFER,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.RecurringTransfer)
    },
)
_sym_db.RegisterMessage(RecurringTransfer)

CancelTransfer = _reflection.GeneratedProtocolMessageType(
    "CancelTransfer",
    (_message.Message,),
    {
        "DESCRIPTOR": _CANCELTRANSFER,
        "__module__": "vega.commands.v1.commands_pb2"
        # @@protoc_insertion_point(class_scope:vega.commands.v1.CancelTransfer)
    },
)
_sym_db.RegisterMessage(CancelTransfer)

if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z,code.vegaprotocol.io/protos/vega/commands/v1"
    _INT64VALUE._serialized_start = 93
    _INT64VALUE._serialized_end = 120
    _ORDERSUBMISSION._serialized_start = 123
    _ORDERSUBMISSION._serialized_end = 374
    _ORDERCANCELLATION._serialized_start = 376
    _ORDERCANCELLATION._serialized_end = 432
    _ORDERAMENDMENT._serialized_start = 435
    _ORDERAMENDMENT._serialized_end = 693
    _LIQUIDITYPROVISIONSUBMISSION._serialized_start = 696
    _LIQUIDITYPROVISIONSUBMISSION._serialized_end = 877
    _LIQUIDITYPROVISIONCANCELLATION._serialized_start = 879
    _LIQUIDITYPROVISIONCANCELLATION._serialized_end = 930
    _LIQUIDITYPROVISIONAMENDMENT._serialized_start = 933
    _LIQUIDITYPROVISIONAMENDMENT._serialized_end = 1113
    _WITHDRAWSUBMISSION._serialized_start = 1115
    _WITHDRAWSUBMISSION._serialized_end = 1198
    _PROPOSALSUBMISSION._serialized_start = 1200
    _PROPOSALSUBMISSION._serialized_end = 1319
    _VOTESUBMISSION._serialized_start = 1321
    _VOTESUBMISSION._serialized_end = 1391
    _DELEGATESUBMISSION._serialized_start = 1393
    _DELEGATESUBMISSION._serialized_end = 1446
    _UNDELEGATESUBMISSION._serialized_start = 1449
    _UNDELEGATESUBMISSION._serialized_end = 1666
    _UNDELEGATESUBMISSION_METHOD._serialized_start = 1569
    _UNDELEGATESUBMISSION_METHOD._serialized_end = 1666
    _TRANSFER._serialized_start = 1669
    _TRANSFER._serialized_end = 1950
    _ONEOFFTRANSFER._serialized_start = 1952
    _ONEOFFTRANSFER._serialized_end = 1988
    _RECURRINGTRANSFER._serialized_start = 1991
    _RECURRINGTRANSFER._serialized_end = 2136
    _CANCELTRANSFER._serialized_start = 2138
    _CANCELTRANSFER._serialized_end = 2175
# @@protoc_insertion_point(module_scope)
