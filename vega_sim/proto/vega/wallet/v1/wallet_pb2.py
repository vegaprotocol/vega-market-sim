# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/wallet/v1/wallet.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ...commands.v1 import commands_pb2 as vega_dot_commands_dot_v1_dot_commands__pb2
from ...commands.v1 import validator_commands_pb2 as vega_dot_commands_dot_v1_dot_validator__commands__pb2
from ...commands.v1 import oracles_pb2 as vega_dot_commands_dot_v1_dot_oracles__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bvega/wallet/v1/wallet.proto\x12\x0evega.wallet.v1\x1a\x1fvega/commands/v1/commands.proto\x1a)vega/commands/v1/validator_commands.proto\x1a\x1evega/commands/v1/oracles.proto\"\xce\x0c\n\x18SubmitTransactionRequest\x12\x0f\n\x07pub_key\x18\x01 \x01(\t\x12\x11\n\tpropagate\x18\x02 \x01(\x08\x12>\n\x10order_submission\x18\xe9\x07 \x01(\x0b\x32!.vega.commands.v1.OrderSubmissionH\x00\x12\x42\n\x12order_cancellation\x18\xea\x07 \x01(\x0b\x32#.vega.commands.v1.OrderCancellationH\x00\x12<\n\x0forder_amendment\x18\xeb\x07 \x01(\x0b\x32 .vega.commands.v1.OrderAmendmentH\x00\x12\x44\n\x13withdraw_submission\x18\xec\x07 \x01(\x0b\x32$.vega.commands.v1.WithdrawSubmissionH\x00\x12\x44\n\x13proposal_submission\x18\xed\x07 \x01(\x0b\x32$.vega.commands.v1.ProposalSubmissionH\x00\x12<\n\x0fvote_submission\x18\xee\x07 \x01(\x0b\x32 .vega.commands.v1.VoteSubmissionH\x00\x12Y\n\x1eliquidity_provision_submission\x18\xef\x07 \x01(\x0b\x32..vega.commands.v1.LiquidityProvisionSubmissionH\x00\x12\x44\n\x13\x64\x65legate_submission\x18\xf0\x07 \x01(\x0b\x32$.vega.commands.v1.DelegateSubmissionH\x00\x12H\n\x15undelegate_submission\x18\xf1\x07 \x01(\x0b\x32&.vega.commands.v1.UndelegateSubmissionH\x00\x12]\n liquidity_provision_cancellation\x18\xf2\x07 \x01(\x0b\x32\x30.vega.commands.v1.LiquidityProvisionCancellationH\x00\x12W\n\x1dliquidity_provision_amendment\x18\xf3\x07 \x01(\x0b\x32-.vega.commands.v1.LiquidityProvisionAmendmentH\x00\x12/\n\x08transfer\x18\xf4\x07 \x01(\x0b\x32\x1a.vega.commands.v1.TransferH\x00\x12<\n\x0f\x63\x61ncel_transfer\x18\xf5\x07 \x01(\x0b\x32 .vega.commands.v1.CancelTransferH\x00\x12\x38\n\rannounce_node\x18\xf6\x07 \x01(\x0b\x32\x1e.vega.commands.v1.AnnounceNodeH\x00\x12\x30\n\tnode_vote\x18\xd2\x0f \x01(\x0b\x32\x1a.vega.commands.v1.NodeVoteH\x00\x12:\n\x0enode_signature\x18\xd3\x0f \x01(\x0b\x32\x1f.vega.commands.v1.NodeSignatureH\x00\x12\x34\n\x0b\x63hain_event\x18\xd4\x0f \x01(\x0b\x32\x1c.vega.commands.v1.ChainEventH\x00\x12G\n\x15key_rotate_submission\x18\xd5\x0f \x01(\x0b\x32%.vega.commands.v1.KeyRotateSubmissionH\x00\x12K\n\x17state_variable_proposal\x18\xd6\x0f \x01(\x0b\x32\'.vega.commands.v1.StateVariableProposalH\x00\x12\x44\n\x13validator_heartbeat\x18\xd7\x0f \x01(\x0b\x32$.vega.commands.v1.ValidatorHeartbeatH\x00\x12X\n\x1e\x65thereum_key_rotate_submission\x18\xd8\x0f \x01(\x0b\x32-.vega.commands.v1.EthereumKeyRotateSubmissionH\x00\x12I\n\x16oracle_data_submission\x18\xb9\x17 \x01(\x0b\x32&.vega.commands.v1.OracleDataSubmissionH\x00\x42\t\n\x07\x63ommandJ\x06\x08\xd1\x0f\x10\xd2\x0f\x42,Z*code.vegaprotocol.io/protos/vega/wallet/v1b\x06proto3')



_SUBMITTRANSACTIONREQUEST = DESCRIPTOR.message_types_by_name['SubmitTransactionRequest']
SubmitTransactionRequest = _reflection.GeneratedProtocolMessageType('SubmitTransactionRequest', (_message.Message,), {
  'DESCRIPTOR' : _SUBMITTRANSACTIONREQUEST,
  '__module__' : 'vega.wallet.v1.wallet_pb2'
  # @@protoc_insertion_point(class_scope:vega.wallet.v1.SubmitTransactionRequest)
  })
_sym_db.RegisterMessage(SubmitTransactionRequest)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z*code.vegaprotocol.io/protos/vega/wallet/v1'
  _SUBMITTRANSACTIONREQUEST._serialized_start=156
  _SUBMITTRANSACTIONREQUEST._serialized_end=1770
# @@protoc_insertion_point(module_scope)
