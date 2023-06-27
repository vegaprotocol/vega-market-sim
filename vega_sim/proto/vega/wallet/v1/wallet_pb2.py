# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/wallet/v1/wallet.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ...commands.v1 import commands_pb2 as vega_dot_commands_dot_v1_dot_commands__pb2
from ...commands.v1 import data_pb2 as vega_dot_commands_dot_v1_dot_data__pb2
from ...commands.v1 import (
    validator_commands_pb2 as vega_dot_commands_dot_v1_dot_validator__commands__pb2,
)


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b"\n\x1bvega/wallet/v1/wallet.proto\x12\x0evega.wallet.v1\x1a\x1fvega/commands/v1/commands.proto\x1a\x1bvega/commands/v1/data.proto\x1a)vega/commands/v1/validator_commands.proto\"\xff\x13\n\x18SubmitTransactionRequest\x12\x17\n\x07pub_key\x18\x01 \x01(\tR\x06pubKey\x12\x1c\n\tpropagate\x18\x02 \x01(\x08R\tpropagate\x12O\n\x10order_submission\x18\xe9\x07 \x01(\x0b\x32!.vega.commands.v1.OrderSubmissionH\x00R\x0forderSubmission\x12U\n\x12order_cancellation\x18\xea\x07 \x01(\x0b\x32#.vega.commands.v1.OrderCancellationH\x00R\x11orderCancellation\x12L\n\x0forder_amendment\x18\xeb\x07 \x01(\x0b\x32 .vega.commands.v1.OrderAmendmentH\x00R\x0eorderAmendment\x12X\n\x13withdraw_submission\x18\xec\x07 \x01(\x0b\x32$.vega.commands.v1.WithdrawSubmissionH\x00R\x12withdrawSubmission\x12X\n\x13proposal_submission\x18\xed\x07 \x01(\x0b\x32$.vega.commands.v1.ProposalSubmissionH\x00R\x12proposalSubmission\x12L\n\x0fvote_submission\x18\xee\x07 \x01(\x0b\x32 .vega.commands.v1.VoteSubmissionH\x00R\x0evoteSubmission\x12w\n\x1eliquidity_provision_submission\x18\xef\x07 \x01(\x0b\x32..vega.commands.v1.LiquidityProvisionSubmissionH\x00R\x1cliquidityProvisionSubmission\x12X\n\x13\x64\x65legate_submission\x18\xf0\x07 \x01(\x0b\x32$.vega.commands.v1.DelegateSubmissionH\x00R\x12\x64\x65legateSubmission\x12^\n\x15undelegate_submission\x18\xf1\x07 \x01(\x0b\x32&.vega.commands.v1.UndelegateSubmissionH\x00R\x14undelegateSubmission\x12}\n liquidity_provision_cancellation\x18\xf2\x07 \x01(\x0b\x32\x30.vega.commands.v1.LiquidityProvisionCancellationH\x00R\x1eliquidityProvisionCancellation\x12t\n\x1dliquidity_provision_amendment\x18\xf3\x07 \x01(\x0b\x32-.vega.commands.v1.LiquidityProvisionAmendmentH\x00R\x1bliquidityProvisionAmendment\x12\x39\n\x08transfer\x18\xf4\x07 \x01(\x0b\x32\x1a.vega.commands.v1.TransferH\x00R\x08transfer\x12L\n\x0f\x63\x61ncel_transfer\x18\xf5\x07 \x01(\x0b\x32 .vega.commands.v1.CancelTransferH\x00R\x0e\x63\x61ncelTransfer\x12\x46\n\rannounce_node\x18\xf6\x07 \x01(\x0b\x32\x1e.vega.commands.v1.AnnounceNodeH\x00R\x0c\x61nnounceNode\x12h\n\x19\x62\x61tch_market_instructions\x18\xf7\x07 \x01(\x0b\x32).vega.commands.v1.BatchMarketInstructionsH\x00R\x17\x62\x61tchMarketInstructions\x12_\n\x16stop_orders_submission\x18\xf8\x07 \x01(\x0b\x32&.vega.commands.v1.StopOrdersSubmissionH\x00R\x14stopOrdersSubmission\x12\x65\n\x18stop_orders_cancellation\x18\xf9\x07 \x01(\x0b\x32(.vega.commands.v1.StopOrdersCancellationH\x00R\x16stopOrdersCancellation\x12:\n\tnode_vote\x18\xd2\x0f \x01(\x0b\x32\x1a.vega.commands.v1.NodeVoteH\x00R\x08nodeVote\x12I\n\x0enode_signature\x18\xd3\x0f \x01(\x0b\x32\x1f.vega.commands.v1.NodeSignatureH\x00R\rnodeSignature\x12@\n\x0b\x63hain_event\x18\xd4\x0f \x01(\x0b\x32\x1c.vega.commands.v1.ChainEventH\x00R\nchainEvent\x12\\\n\x15key_rotate_submission\x18\xd5\x0f \x01(\x0b\x32%.vega.commands.v1.KeyRotateSubmissionH\x00R\x13keyRotateSubmission\x12\x62\n\x17state_variable_proposal\x18\xd6\x0f \x01(\x0b\x32'.vega.commands.v1.StateVariableProposalH\x00R\x15stateVariableProposal\x12X\n\x13validator_heartbeat\x18\xd7\x0f \x01(\x0b\x32$.vega.commands.v1.ValidatorHeartbeatH\x00R\x12validatorHeartbeat\x12u\n\x1e\x65thereum_key_rotate_submission\x18\xd8\x0f \x01(\x0b\x32-.vega.commands.v1.EthereumKeyRotateSubmissionH\x00R\x1b\x65thereumKeyRotateSubmission\x12h\n\x19protocol_upgrade_proposal\x18\xd9\x0f \x01(\x0b\x32).vega.commands.v1.ProtocolUpgradeProposalH\x00R\x17protocolUpgradeProposal\x12O\n\x10issue_signatures\x18\xda\x0f \x01(\x0b\x32!.vega.commands.v1.IssueSignaturesH\x00R\x0fissueSignatures\x12_\n\x16oracle_data_submission\x18\xb9\x17 \x01(\x0b\x32&.vega.commands.v1.OracleDataSubmissionH\x00R\x14oracleDataSubmissionB\t\n\x07\x63ommandJ\x06\x08\xd1\x0f\x10\xd2\x0f\x42\x31Z/code.vegaprotocol.io/vega/protos/vega/wallet/v1b\x06proto3"
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "vega.wallet.v1.wallet_pb2", globals()
)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = (
        b"Z/code.vegaprotocol.io/vega/protos/vega/wallet/v1"
    )
    _SUBMITTRANSACTIONREQUEST._serialized_start = 153
    _SUBMITTRANSACTIONREQUEST._serialized_end = 2712
# @@protoc_insertion_point(module_scope)
