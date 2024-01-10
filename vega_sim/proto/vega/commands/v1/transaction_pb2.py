# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/commands/v1/transaction.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ...commands.v1 import commands_pb2 as vega_dot_commands_dot_v1_dot_commands__pb2
from ...commands.v1 import data_pb2 as vega_dot_commands_dot_v1_dot_data__pb2
from ...commands.v1 import signature_pb2 as vega_dot_commands_dot_v1_dot_signature__pb2
from ...commands.v1 import (
    validator_commands_pb2 as vega_dot_commands_dot_v1_dot_validator__commands__pb2,
)


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n"vega/commands/v1/transaction.proto\x12\x10vega.commands.v1\x1a\x1fvega/commands/v1/commands.proto\x1a\x1bvega/commands/v1/data.proto\x1a vega/commands/v1/signature.proto\x1a)vega/commands/v1/validator_commands.proto"\xfa\x15\n\tInputData\x12\x14\n\x05nonce\x18\x01 \x01(\x04R\x05nonce\x12!\n\x0c\x62lock_height\x18\x02 \x01(\x04R\x0b\x62lockHeight\x12O\n\x10order_submission\x18\xe9\x07 \x01(\x0b\x32!.vega.commands.v1.OrderSubmissionH\x00R\x0forderSubmission\x12U\n\x12order_cancellation\x18\xea\x07 \x01(\x0b\x32#.vega.commands.v1.OrderCancellationH\x00R\x11orderCancellation\x12L\n\x0forder_amendment\x18\xeb\x07 \x01(\x0b\x32 .vega.commands.v1.OrderAmendmentH\x00R\x0eorderAmendment\x12X\n\x13withdraw_submission\x18\xec\x07 \x01(\x0b\x32$.vega.commands.v1.WithdrawSubmissionH\x00R\x12withdrawSubmission\x12X\n\x13proposal_submission\x18\xed\x07 \x01(\x0b\x32$.vega.commands.v1.ProposalSubmissionH\x00R\x12proposalSubmission\x12L\n\x0fvote_submission\x18\xee\x07 \x01(\x0b\x32 .vega.commands.v1.VoteSubmissionH\x00R\x0evoteSubmission\x12w\n\x1eliquidity_provision_submission\x18\xef\x07 \x01(\x0b\x32..vega.commands.v1.LiquidityProvisionSubmissionH\x00R\x1cliquidityProvisionSubmission\x12X\n\x13\x64\x65legate_submission\x18\xf0\x07 \x01(\x0b\x32$.vega.commands.v1.DelegateSubmissionH\x00R\x12\x64\x65legateSubmission\x12^\n\x15undelegate_submission\x18\xf1\x07 \x01(\x0b\x32&.vega.commands.v1.UndelegateSubmissionH\x00R\x14undelegateSubmission\x12}\n liquidity_provision_cancellation\x18\xf2\x07 \x01(\x0b\x32\x30.vega.commands.v1.LiquidityProvisionCancellationH\x00R\x1eliquidityProvisionCancellation\x12t\n\x1dliquidity_provision_amendment\x18\xf3\x07 \x01(\x0b\x32-.vega.commands.v1.LiquidityProvisionAmendmentH\x00R\x1bliquidityProvisionAmendment\x12\x39\n\x08transfer\x18\xf4\x07 \x01(\x0b\x32\x1a.vega.commands.v1.TransferH\x00R\x08transfer\x12L\n\x0f\x63\x61ncel_transfer\x18\xf5\x07 \x01(\x0b\x32 .vega.commands.v1.CancelTransferH\x00R\x0e\x63\x61ncelTransfer\x12\x46\n\rannounce_node\x18\xf6\x07 \x01(\x0b\x32\x1e.vega.commands.v1.AnnounceNodeH\x00R\x0c\x61nnounceNode\x12h\n\x19\x62\x61tch_market_instructions\x18\xf7\x07 \x01(\x0b\x32).vega.commands.v1.BatchMarketInstructionsH\x00R\x17\x62\x61tchMarketInstructions\x12_\n\x16stop_orders_submission\x18\xf8\x07 \x01(\x0b\x32&.vega.commands.v1.StopOrdersSubmissionH\x00R\x14stopOrdersSubmission\x12\x65\n\x18stop_orders_cancellation\x18\xf9\x07 \x01(\x0b\x32(.vega.commands.v1.StopOrdersCancellationH\x00R\x16stopOrdersCancellation\x12V\n\x13\x63reate_referral_set\x18\xfa\x07 \x01(\x0b\x32#.vega.commands.v1.CreateReferralSetH\x00R\x11\x63reateReferralSet\x12V\n\x13update_referral_set\x18\xfb\x07 \x01(\x0b\x32#.vega.commands.v1.UpdateReferralSetH\x00R\x11updateReferralSet\x12V\n\x13\x61pply_referral_code\x18\xfc\x07 \x01(\x0b\x32#.vega.commands.v1.ApplyReferralCodeH\x00R\x11\x61pplyReferralCode\x12:\n\tnode_vote\x18\xd2\x0f \x01(\x0b\x32\x1a.vega.commands.v1.NodeVoteH\x00R\x08nodeVote\x12I\n\x0enode_signature\x18\xd3\x0f \x01(\x0b\x32\x1f.vega.commands.v1.NodeSignatureH\x00R\rnodeSignature\x12@\n\x0b\x63hain_event\x18\xd4\x0f \x01(\x0b\x32\x1c.vega.commands.v1.ChainEventH\x00R\nchainEvent\x12\\\n\x15key_rotate_submission\x18\xd5\x0f \x01(\x0b\x32%.vega.commands.v1.KeyRotateSubmissionH\x00R\x13keyRotateSubmission\x12\x62\n\x17state_variable_proposal\x18\xd6\x0f \x01(\x0b\x32\'.vega.commands.v1.StateVariableProposalH\x00R\x15stateVariableProposal\x12X\n\x13validator_heartbeat\x18\xd7\x0f \x01(\x0b\x32$.vega.commands.v1.ValidatorHeartbeatH\x00R\x12validatorHeartbeat\x12u\n\x1e\x65thereum_key_rotate_submission\x18\xd8\x0f \x01(\x0b\x32-.vega.commands.v1.EthereumKeyRotateSubmissionH\x00R\x1b\x65thereumKeyRotateSubmission\x12h\n\x19protocol_upgrade_proposal\x18\xd9\x0f \x01(\x0b\x32).vega.commands.v1.ProtocolUpgradeProposalH\x00R\x17protocolUpgradeProposal\x12O\n\x10issue_signatures\x18\xda\x0f \x01(\x0b\x32!.vega.commands.v1.IssueSignaturesH\x00R\x0fissueSignatures\x12_\n\x16oracle_data_submission\x18\xb9\x17 \x01(\x0b\x32&.vega.commands.v1.OracleDataSubmissionH\x00R\x14oracleDataSubmissionB\t\n\x07\x63ommandJ\x06\x08\xa1\x1f\x10\xa2\x1f"\x92\x02\n\x0bTransaction\x12\x1d\n\ninput_data\x18\x01 \x01(\x0cR\tinputData\x12\x39\n\tsignature\x18\x02 \x01(\x0b\x32\x1b.vega.commands.v1.SignatureR\tsignature\x12\x1b\n\x07\x61\x64\x64ress\x18\xe9\x07 \x01(\tH\x00R\x07\x61\x64\x64ress\x12\x1a\n\x07pub_key\x18\xea\x07 \x01(\tH\x00R\x06pubKey\x12\x36\n\x07version\x18\xd0\x0f \x01(\x0e\x32\x1b.vega.commands.v1.TxVersionR\x07version\x12\x30\n\x03pow\x18\xb8\x17 \x01(\x0b\x32\x1d.vega.commands.v1.ProofOfWorkR\x03powB\x06\n\x04\x66rom"5\n\x0bProofOfWork\x12\x10\n\x03tid\x18\x01 \x01(\tR\x03tid\x12\x14\n\x05nonce\x18\x02 \x01(\x04R\x05nonce*S\n\tTxVersion\x12\x1a\n\x16TX_VERSION_UNSPECIFIED\x10\x00\x12\x11\n\rTX_VERSION_V2\x10\x02\x12\x11\n\rTX_VERSION_V3\x10\x03"\x04\x08\x01\x10\x01\x42\x33Z1code.vegaprotocol.io/vega/protos/vega/commands/v1b\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "vega.commands.v1.transaction_pb2", _globals
)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals[
        "DESCRIPTOR"
    ]._serialized_options = b"Z1code.vegaprotocol.io/vega/protos/vega/commands/v1"
    _globals["_TXVERSION"]._serialized_start = 3340
    _globals["_TXVERSION"]._serialized_end = 3423
    _globals["_INPUTDATA"]._serialized_start = 196
    _globals["_INPUTDATA"]._serialized_end = 3006
    _globals["_TRANSACTION"]._serialized_start = 3009
    _globals["_TRANSACTION"]._serialized_end = 3283
    _globals["_PROOFOFWORK"]._serialized_start = 3285
    _globals["_PROOFOFWORK"]._serialized_end = 3338
# @@protoc_insertion_point(module_scope)
