# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/commands/v1/commands.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ... import governance_pb2 as vega_dot_governance__pb2
from ... import vega_pb2 as vega_dot_vega__pb2
from ...commands.v1 import (
    validator_commands_pb2 as vega_dot_commands_dot_v1_dot_validator__commands__pb2,
)


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1fvega/commands/v1/commands.proto\x12\x10vega.commands.v1\x1a\x15vega/governance.proto\x1a\x0fvega/vega.proto\x1a)vega/commands/v1/validator_commands.proto"\xeb\x01\n\x17\x42\x61tchMarketInstructions\x12I\n\rcancellations\x18\x01 \x03(\x0b\x32#.vega.commands.v1.OrderCancellationR\rcancellations\x12@\n\namendments\x18\x02 \x03(\x0b\x32 .vega.commands.v1.OrderAmendmentR\namendments\x12\x43\n\x0bsubmissions\x18\x03 \x03(\x0b\x32!.vega.commands.v1.OrderSubmissionR\x0bsubmissions"\xce\x02\n\x0fOrderSubmission\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12\x14\n\x05price\x18\x02 \x01(\tR\x05price\x12\x12\n\x04size\x18\x03 \x01(\x04R\x04size\x12\x1e\n\x04side\x18\x04 \x01(\x0e\x32\n.vega.SideR\x04side\x12;\n\rtime_in_force\x18\x05 \x01(\x0e\x32\x17.vega.Order.TimeInForceR\x0btimeInForce\x12\x1d\n\nexpires_at\x18\x06 \x01(\x03R\texpiresAt\x12$\n\x04type\x18\x07 \x01(\x0e\x32\x10.vega.Order.TypeR\x04type\x12\x1c\n\treference\x18\x08 \x01(\tR\treference\x12\x34\n\x0cpegged_order\x18\t \x01(\x0b\x32\x11.vega.PeggedOrderR\x0bpeggedOrder"K\n\x11OrderCancellation\x12\x19\n\x08order_id\x18\x01 \x01(\tR\x07orderId\x12\x1b\n\tmarket_id\x18\x02 \x01(\tR\x08marketId"\xe3\x02\n\x0eOrderAmendment\x12\x19\n\x08order_id\x18\x01 \x01(\tR\x07orderId\x12\x1b\n\tmarket_id\x18\x02 \x01(\tR\x08marketId\x12\x19\n\x05price\x18\x03 \x01(\tH\x00R\x05price\x88\x01\x01\x12\x1d\n\nsize_delta\x18\x04 \x01(\x03R\tsizeDelta\x12"\n\nexpires_at\x18\x05 \x01(\x03H\x01R\texpiresAt\x88\x01\x01\x12;\n\rtime_in_force\x18\x06 \x01(\x0e\x32\x17.vega.Order.TimeInForceR\x0btimeInForce\x12#\n\rpegged_offset\x18\x07 \x01(\tR\x0cpeggedOffset\x12@\n\x10pegged_reference\x18\x08 \x01(\x0e\x32\x15.vega.PeggedReferenceR\x0fpeggedReferenceB\x08\n\x06_priceB\r\n\x0b_expires_at"\xee\x01\n\x1cLiquidityProvisionSubmission\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12+\n\x11\x63ommitment_amount\x18\x02 \x01(\tR\x10\x63ommitmentAmount\x12\x10\n\x03\x66\x65\x65\x18\x03 \x01(\tR\x03\x66\x65\x65\x12*\n\x05sells\x18\x04 \x03(\x0b\x32\x14.vega.LiquidityOrderR\x05sells\x12(\n\x04\x62uys\x18\x05 \x03(\x0b\x32\x14.vega.LiquidityOrderR\x04\x62uys\x12\x1c\n\treference\x18\x06 \x01(\tR\treference"=\n\x1eLiquidityProvisionCancellation\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId"\xed\x01\n\x1bLiquidityProvisionAmendment\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12+\n\x11\x63ommitment_amount\x18\x02 \x01(\tR\x10\x63ommitmentAmount\x12\x10\n\x03\x66\x65\x65\x18\x03 \x01(\tR\x03\x66\x65\x65\x12*\n\x05sells\x18\x04 \x03(\x0b\x32\x14.vega.LiquidityOrderR\x05sells\x12(\n\x04\x62uys\x18\x05 \x03(\x0b\x32\x14.vega.LiquidityOrderR\x04\x62uys\x12\x1c\n\treference\x18\x06 \x01(\tR\treference"g\n\x12WithdrawSubmission\x12\x16\n\x06\x61mount\x18\x01 \x01(\tR\x06\x61mount\x12\x14\n\x05\x61sset\x18\x02 \x01(\tR\x05\x61sset\x12#\n\x03\x65xt\x18\x03 \x01(\x0b\x32\x11.vega.WithdrawExtR\x03\x65xt"\x94\x01\n\x12ProposalSubmission\x12\x1c\n\treference\x18\x01 \x01(\tR\treference\x12)\n\x05terms\x18\x02 \x01(\x0b\x32\x13.vega.ProposalTermsR\x05terms\x12\x35\n\trationale\x18\x03 \x01(\x0b\x32\x17.vega.ProposalRationaleR\trationale"Y\n\x0eVoteSubmission\x12\x1f\n\x0bproposal_id\x18\x01 \x01(\tR\nproposalId\x12&\n\x05value\x18\x02 \x01(\x0e\x32\x10.vega.Vote.ValueR\x05value"E\n\x12\x44\x65legateSubmission\x12\x17\n\x07node_id\x18\x01 \x01(\tR\x06nodeId\x12\x16\n\x06\x61mount\x18\x02 \x01(\tR\x06\x61mount"\xe2\x01\n\x14UndelegateSubmission\x12\x17\n\x07node_id\x18\x01 \x01(\tR\x06nodeId\x12\x16\n\x06\x61mount\x18\x02 \x01(\tR\x06\x61mount\x12\x45\n\x06method\x18\x03 \x01(\x0e\x32-.vega.commands.v1.UndelegateSubmission.MethodR\x06method"R\n\x06Method\x12\x16\n\x12METHOD_UNSPECIFIED\x10\x00\x12\x0e\n\nMETHOD_NOW\x10\x01\x12\x1a\n\x16METHOD_AT_END_OF_EPOCH\x10\x02"\x04\x08\x03\x10\x03"\xea\x02\n\x08Transfer\x12=\n\x11\x66rom_account_type\x18\x01 \x01(\x0e\x32\x11.vega.AccountTypeR\x0f\x66romAccountType\x12\x0e\n\x02to\x18\x02 \x01(\tR\x02to\x12\x39\n\x0fto_account_type\x18\x03 \x01(\x0e\x32\x11.vega.AccountTypeR\rtoAccountType\x12\x14\n\x05\x61sset\x18\x04 \x01(\tR\x05\x61sset\x12\x16\n\x06\x61mount\x18\x05 \x01(\tR\x06\x61mount\x12\x1c\n\treference\x18\x06 \x01(\tR\treference\x12;\n\x07one_off\x18\x65 \x01(\x0b\x32 .vega.commands.v1.OneOffTransferH\x00R\x06oneOff\x12\x43\n\trecurring\x18\x66 \x01(\x0b\x32#.vega.commands.v1.RecurringTransferH\x00R\trecurringB\x06\n\x04kind"/\n\x0eOneOffTransfer\x12\x1d\n\ndeliver_on\x18\x01 \x01(\x03R\tdeliverOn"\xc1\x01\n\x11RecurringTransfer\x12\x1f\n\x0bstart_epoch\x18\x01 \x01(\x04R\nstartEpoch\x12 \n\tend_epoch\x18\x02 \x01(\x04H\x00R\x08\x65ndEpoch\x88\x01\x01\x12\x16\n\x06\x66\x61\x63tor\x18\x03 \x01(\tR\x06\x66\x61\x63tor\x12\x43\n\x11\x64ispatch_strategy\x18\x04 \x01(\x0b\x32\x16.vega.DispatchStrategyR\x10\x64ispatchStrategyB\x0c\n\n_end_epoch"1\n\x0e\x43\x61ncelTransfer\x12\x1f\n\x0btransfer_id\x18\x01 \x01(\tR\ntransferId"\x94\x01\n\x0fIssueSignatures\x12\x1c\n\tsubmitter\x18\x01 \x01(\tR\tsubmitter\x12\x37\n\x04kind\x18\x02 \x01(\x0e\x32#.vega.commands.v1.NodeSignatureKindR\x04kind\x12*\n\x11validator_node_id\x18\x03 \x01(\tR\x0fvalidatorNodeIdB3Z1code.vegaprotocol.io/vega/protos/vega/commands/v1b\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "vega.commands.v1.commands_pb2", globals()
)
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = (
        b"Z1code.vegaprotocol.io/vega/protos/vega/commands/v1"
    )
    _BATCHMARKETINSTRUCTIONS._serialized_start = 137
    _BATCHMARKETINSTRUCTIONS._serialized_end = 372
    _ORDERSUBMISSION._serialized_start = 375
    _ORDERSUBMISSION._serialized_end = 709
    _ORDERCANCELLATION._serialized_start = 711
    _ORDERCANCELLATION._serialized_end = 786
    _ORDERAMENDMENT._serialized_start = 789
    _ORDERAMENDMENT._serialized_end = 1144
    _LIQUIDITYPROVISIONSUBMISSION._serialized_start = 1147
    _LIQUIDITYPROVISIONSUBMISSION._serialized_end = 1385
    _LIQUIDITYPROVISIONCANCELLATION._serialized_start = 1387
    _LIQUIDITYPROVISIONCANCELLATION._serialized_end = 1448
    _LIQUIDITYPROVISIONAMENDMENT._serialized_start = 1451
    _LIQUIDITYPROVISIONAMENDMENT._serialized_end = 1688
    _WITHDRAWSUBMISSION._serialized_start = 1690
    _WITHDRAWSUBMISSION._serialized_end = 1793
    _PROPOSALSUBMISSION._serialized_start = 1796
    _PROPOSALSUBMISSION._serialized_end = 1944
    _VOTESUBMISSION._serialized_start = 1946
    _VOTESUBMISSION._serialized_end = 2035
    _DELEGATESUBMISSION._serialized_start = 2037
    _DELEGATESUBMISSION._serialized_end = 2106
    _UNDELEGATESUBMISSION._serialized_start = 2109
    _UNDELEGATESUBMISSION._serialized_end = 2335
    _UNDELEGATESUBMISSION_METHOD._serialized_start = 2253
    _UNDELEGATESUBMISSION_METHOD._serialized_end = 2335
    _TRANSFER._serialized_start = 2338
    _TRANSFER._serialized_end = 2700
    _ONEOFFTRANSFER._serialized_start = 2702
    _ONEOFFTRANSFER._serialized_end = 2749
    _RECURRINGTRANSFER._serialized_start = 2752
    _RECURRINGTRANSFER._serialized_end = 2945
    _CANCELTRANSFER._serialized_start = 2947
    _CANCELTRANSFER._serialized_end = 2996
    _ISSUESIGNATURES._serialized_start = 2999
    _ISSUESIGNATURES._serialized_end = 3147
# @@protoc_insertion_point(module_scope)
