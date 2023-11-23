# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/commands/v1/commands.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ...commands.v1 import (
    validator_commands_pb2 as vega_dot_commands_dot_v1_dot_validator__commands__pb2,
)
from ... import governance_pb2 as vega_dot_governance__pb2
from ... import vega_pb2 as vega_dot_vega__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1fvega/commands/v1/commands.proto\x12\x10vega.commands.v1\x1a)vega/commands/v1/validator_commands.proto\x1a\x15vega/governance.proto\x1a\x0fvega/vega.proto"\xff\x03\n\x17\x42\x61tchMarketInstructions\x12I\n\rcancellations\x18\x01 \x03(\x0b\x32#.vega.commands.v1.OrderCancellationR\rcancellations\x12@\n\namendments\x18\x02 \x03(\x0b\x32 .vega.commands.v1.OrderAmendmentR\namendments\x12\x43\n\x0bsubmissions\x18\x03 \x03(\x0b\x32!.vega.commands.v1.OrderSubmissionR\x0bsubmissions\x12\x62\n\x18stop_orders_cancellation\x18\x04 \x03(\x0b\x32(.vega.commands.v1.StopOrdersCancellationR\x16stopOrdersCancellation\x12\\\n\x16stop_orders_submission\x18\x05 \x03(\x0b\x32&.vega.commands.v1.StopOrdersSubmissionR\x14stopOrdersSubmission\x12P\n\x12update_margin_mode\x18\x06 \x01(\x0b\x32".vega.commands.v1.UpdateMarginModeR\x10updateMarginMode"\xc6\x01\n\x14StopOrdersSubmission\x12\x46\n\x0brises_above\x18\x01 \x01(\x0b\x32 .vega.commands.v1.StopOrderSetupH\x00R\nrisesAbove\x88\x01\x01\x12\x46\n\x0b\x66\x61lls_below\x18\x02 \x01(\x0b\x32 .vega.commands.v1.StopOrderSetupH\x01R\nfallsBelow\x88\x01\x01\x42\x0e\n\x0c_rises_aboveB\x0e\n\x0c_falls_below"\xd0\x02\n\x0eStopOrderSetup\x12L\n\x10order_submission\x18\x01 \x01(\x0b\x32!.vega.commands.v1.OrderSubmissionR\x0forderSubmission\x12"\n\nexpires_at\x18\x02 \x01(\x03H\x01R\texpiresAt\x88\x01\x01\x12L\n\x0f\x65xpiry_strategy\x18\x03 \x01(\x0e\x32\x1e.vega.StopOrder.ExpiryStrategyH\x02R\x0e\x65xpiryStrategy\x88\x01\x01\x12\x16\n\x05price\x18\x64 \x01(\tH\x00R\x05price\x12\x38\n\x17trailing_percent_offset\x18\x65 \x01(\tH\x00R\x15trailingPercentOffsetB\t\n\x07triggerB\r\n\x0b_expires_atB\x12\n\x10_expiry_strategy"\x83\x01\n\x16StopOrdersCancellation\x12 \n\tmarket_id\x18\x01 \x01(\tH\x00R\x08marketId\x88\x01\x01\x12\'\n\rstop_order_id\x18\x02 \x01(\tH\x01R\x0bstopOrderId\x88\x01\x01\x42\x0c\n\n_market_idB\x10\n\x0e_stop_order_id"\xe4\x03\n\x0fOrderSubmission\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12\x14\n\x05price\x18\x02 \x01(\tR\x05price\x12\x12\n\x04size\x18\x03 \x01(\x04R\x04size\x12\x1e\n\x04side\x18\x04 \x01(\x0e\x32\n.vega.SideR\x04side\x12;\n\rtime_in_force\x18\x05 \x01(\x0e\x32\x17.vega.Order.TimeInForceR\x0btimeInForce\x12\x1d\n\nexpires_at\x18\x06 \x01(\x03R\texpiresAt\x12$\n\x04type\x18\x07 \x01(\x0e\x32\x10.vega.Order.TypeR\x04type\x12\x1c\n\treference\x18\x08 \x01(\tR\treference\x12\x34\n\x0cpegged_order\x18\t \x01(\x0b\x32\x11.vega.PeggedOrderR\x0bpeggedOrder\x12\x1b\n\tpost_only\x18\n \x01(\x08R\x08postOnly\x12\x1f\n\x0breduce_only\x18\x0b \x01(\x08R\nreduceOnly\x12\x45\n\x0ciceberg_opts\x18\x0c \x01(\x0b\x32\x1d.vega.commands.v1.IcebergOptsH\x00R\x0bicebergOpts\x88\x01\x01\x42\x0f\n\r_iceberg_opts"\\\n\x0bIcebergOpts\x12\x1b\n\tpeak_size\x18\x01 \x01(\x04R\x08peakSize\x12\x30\n\x14minimum_visible_size\x18\x02 \x01(\x04R\x12minimumVisibleSize"\xfd\x01\n\x10UpdateMarginMode\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12;\n\x04mode\x18\x02 \x01(\x0e\x32\'.vega.commands.v1.UpdateMarginMode.ModeR\x04mode\x12(\n\rmargin_factor\x18\x03 \x01(\tH\x00R\x0cmarginFactor\x88\x01\x01"S\n\x04Mode\x12\x1a\n\x16MODE_CROSS_UNSPECIFIED\x10\x00\x12\x15\n\x11MODE_CROSS_MARGIN\x10\x01\x12\x18\n\x14MODE_ISOLATED_MARGIN\x10\x02\x42\x10\n\x0e_margin_factor"K\n\x11OrderCancellation\x12\x19\n\x08order_id\x18\x01 \x01(\tR\x07orderId\x12\x1b\n\tmarket_id\x18\x02 \x01(\tR\x08marketId"\x85\x03\n\x0eOrderAmendment\x12\x19\n\x08order_id\x18\x01 \x01(\tR\x07orderId\x12\x1b\n\tmarket_id\x18\x02 \x01(\tR\x08marketId\x12\x19\n\x05price\x18\x03 \x01(\tH\x00R\x05price\x88\x01\x01\x12\x1d\n\nsize_delta\x18\x04 \x01(\x03R\tsizeDelta\x12"\n\nexpires_at\x18\x05 \x01(\x03H\x01R\texpiresAt\x88\x01\x01\x12;\n\rtime_in_force\x18\x06 \x01(\x0e\x32\x17.vega.Order.TimeInForceR\x0btimeInForce\x12#\n\rpegged_offset\x18\x07 \x01(\tR\x0cpeggedOffset\x12@\n\x10pegged_reference\x18\x08 \x01(\x0e\x32\x15.vega.PeggedReferenceR\x0fpeggedReference\x12\x17\n\x04size\x18\t \x01(\x04H\x02R\x04size\x88\x01\x01\x42\x08\n\x06_priceB\r\n\x0b_expires_atB\x07\n\x05_size"\xa4\x01\n\x1cLiquidityProvisionSubmission\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12+\n\x11\x63ommitment_amount\x18\x02 \x01(\tR\x10\x63ommitmentAmount\x12\x10\n\x03\x66\x65\x65\x18\x03 \x01(\tR\x03\x66\x65\x65\x12\x1c\n\treference\x18\x06 \x01(\tR\treferenceJ\x04\x08\x04\x10\x05J\x04\x08\x05\x10\x06"=\n\x1eLiquidityProvisionCancellation\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId"\xa3\x01\n\x1bLiquidityProvisionAmendment\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12+\n\x11\x63ommitment_amount\x18\x02 \x01(\tR\x10\x63ommitmentAmount\x12\x10\n\x03\x66\x65\x65\x18\x03 \x01(\tR\x03\x66\x65\x65\x12\x1c\n\treference\x18\x06 \x01(\tR\treferenceJ\x04\x08\x04\x10\x05J\x04\x08\x05\x10\x06"g\n\x12WithdrawSubmission\x12\x16\n\x06\x61mount\x18\x01 \x01(\tR\x06\x61mount\x12\x14\n\x05\x61sset\x18\x02 \x01(\tR\x05\x61sset\x12#\n\x03\x65xt\x18\x03 \x01(\x0b\x32\x11.vega.WithdrawExtR\x03\x65xt"\x94\x01\n\x12ProposalSubmission\x12\x1c\n\treference\x18\x01 \x01(\tR\treference\x12)\n\x05terms\x18\x02 \x01(\x0b\x32\x13.vega.ProposalTermsR\x05terms\x12\x35\n\trationale\x18\x03 \x01(\x0b\x32\x17.vega.ProposalRationaleR\trationale"Y\n\x0eVoteSubmission\x12\x1f\n\x0bproposal_id\x18\x01 \x01(\tR\nproposalId\x12&\n\x05value\x18\x02 \x01(\x0e\x32\x10.vega.Vote.ValueR\x05value"E\n\x12\x44\x65legateSubmission\x12\x17\n\x07node_id\x18\x01 \x01(\tR\x06nodeId\x12\x16\n\x06\x61mount\x18\x02 \x01(\tR\x06\x61mount"\xe2\x01\n\x14UndelegateSubmission\x12\x17\n\x07node_id\x18\x01 \x01(\tR\x06nodeId\x12\x16\n\x06\x61mount\x18\x02 \x01(\tR\x06\x61mount\x12\x45\n\x06method\x18\x03 \x01(\x0e\x32-.vega.commands.v1.UndelegateSubmission.MethodR\x06method"R\n\x06Method\x12\x16\n\x12METHOD_UNSPECIFIED\x10\x00\x12\x0e\n\nMETHOD_NOW\x10\x01\x12\x1a\n\x16METHOD_AT_END_OF_EPOCH\x10\x02"\x04\x08\x03\x10\x03"\xea\x02\n\x08Transfer\x12=\n\x11\x66rom_account_type\x18\x01 \x01(\x0e\x32\x11.vega.AccountTypeR\x0f\x66romAccountType\x12\x0e\n\x02to\x18\x02 \x01(\tR\x02to\x12\x39\n\x0fto_account_type\x18\x03 \x01(\x0e\x32\x11.vega.AccountTypeR\rtoAccountType\x12\x14\n\x05\x61sset\x18\x04 \x01(\tR\x05\x61sset\x12\x16\n\x06\x61mount\x18\x05 \x01(\tR\x06\x61mount\x12\x1c\n\treference\x18\x06 \x01(\tR\treference\x12;\n\x07one_off\x18\x65 \x01(\x0b\x32 .vega.commands.v1.OneOffTransferH\x00R\x06oneOff\x12\x43\n\trecurring\x18\x66 \x01(\x0b\x32#.vega.commands.v1.RecurringTransferH\x00R\trecurringB\x06\n\x04kind"/\n\x0eOneOffTransfer\x12\x1d\n\ndeliver_on\x18\x01 \x01(\x03R\tdeliverOn"\xc1\x01\n\x11RecurringTransfer\x12\x1f\n\x0bstart_epoch\x18\x01 \x01(\x04R\nstartEpoch\x12 \n\tend_epoch\x18\x02 \x01(\x04H\x00R\x08\x65ndEpoch\x88\x01\x01\x12\x16\n\x06\x66\x61\x63tor\x18\x03 \x01(\tR\x06\x66\x61\x63tor\x12\x43\n\x11\x64ispatch_strategy\x18\x04 \x01(\x0b\x32\x16.vega.DispatchStrategyR\x10\x64ispatchStrategyB\x0c\n\n_end_epoch"1\n\x0e\x43\x61ncelTransfer\x12\x1f\n\x0btransfer_id\x18\x01 \x01(\tR\ntransferId"\x94\x01\n\x0fIssueSignatures\x12\x1c\n\tsubmitter\x18\x01 \x01(\tR\tsubmitter\x12\x37\n\x04kind\x18\x02 \x01(\x0e\x32#.vega.commands.v1.NodeSignatureKindR\x04kind\x12*\n\x11validator_node_id\x18\x03 \x01(\tR\x0fvalidatorNodeId"\x8d\x02\n\x11\x43reateReferralSet\x12\x17\n\x07is_team\x18\x01 \x01(\x08R\x06isTeam\x12\x41\n\x04team\x18\x02 \x01(\x0b\x32(.vega.commands.v1.CreateReferralSet.TeamH\x00R\x04team\x88\x01\x01\x1a\x92\x01\n\x04Team\x12\x12\n\x04name\x18\n \x01(\tR\x04name\x12\x1e\n\x08team_url\x18\x0b \x01(\tH\x00R\x07teamUrl\x88\x01\x01\x12"\n\navatar_url\x18\x0c \x01(\tH\x01R\tavatarUrl\x88\x01\x01\x12\x16\n\x06\x63losed\x18\r \x01(\x08R\x06\x63losedB\x0b\n\t_team_urlB\r\n\x0b_avatar_urlB\x07\n\x05_team"\xbb\x02\n\x11UpdateReferralSet\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x17\n\x07is_team\x18\x02 \x01(\x08R\x06isTeam\x12\x41\n\x04team\x18\x03 \x01(\x0b\x32(.vega.commands.v1.UpdateReferralSet.TeamH\x00R\x04team\x88\x01\x01\x1a\xb0\x01\n\x04Team\x12\x17\n\x04name\x18\n \x01(\tH\x00R\x04name\x88\x01\x01\x12\x1e\n\x08team_url\x18\x0b \x01(\tH\x01R\x07teamUrl\x88\x01\x01\x12"\n\navatar_url\x18\x0c \x01(\tH\x02R\tavatarUrl\x88\x01\x01\x12\x1b\n\x06\x63losed\x18\r \x01(\x08H\x03R\x06\x63losed\x88\x01\x01\x42\x07\n\x05_nameB\x0b\n\t_team_urlB\r\n\x0b_avatar_urlB\t\n\x07_closedB\x07\n\x05_team"#\n\x11\x41pplyReferralCode\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id"\x1a\n\x08JoinTeam\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02idB3Z1code.vegaprotocol.io/vega/protos/vega/commands/v1b\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "vega.commands.v1.commands_pb2", _globals
)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals[
        "DESCRIPTOR"
    ]._serialized_options = b"Z1code.vegaprotocol.io/vega/protos/vega/commands/v1"
    _globals["_BATCHMARKETINSTRUCTIONS"]._serialized_start = 137
    _globals["_BATCHMARKETINSTRUCTIONS"]._serialized_end = 648
    _globals["_STOPORDERSSUBMISSION"]._serialized_start = 651
    _globals["_STOPORDERSSUBMISSION"]._serialized_end = 849
    _globals["_STOPORDERSETUP"]._serialized_start = 852
    _globals["_STOPORDERSETUP"]._serialized_end = 1188
    _globals["_STOPORDERSCANCELLATION"]._serialized_start = 1191
    _globals["_STOPORDERSCANCELLATION"]._serialized_end = 1322
    _globals["_ORDERSUBMISSION"]._serialized_start = 1325
    _globals["_ORDERSUBMISSION"]._serialized_end = 1809
    _globals["_ICEBERGOPTS"]._serialized_start = 1811
    _globals["_ICEBERGOPTS"]._serialized_end = 1903
    _globals["_UPDATEMARGINMODE"]._serialized_start = 1906
    _globals["_UPDATEMARGINMODE"]._serialized_end = 2159
    _globals["_UPDATEMARGINMODE_MODE"]._serialized_start = 2058
    _globals["_UPDATEMARGINMODE_MODE"]._serialized_end = 2141
    _globals["_ORDERCANCELLATION"]._serialized_start = 2161
    _globals["_ORDERCANCELLATION"]._serialized_end = 2236
    _globals["_ORDERAMENDMENT"]._serialized_start = 2239
    _globals["_ORDERAMENDMENT"]._serialized_end = 2628
    _globals["_LIQUIDITYPROVISIONSUBMISSION"]._serialized_start = 2631
    _globals["_LIQUIDITYPROVISIONSUBMISSION"]._serialized_end = 2795
    _globals["_LIQUIDITYPROVISIONCANCELLATION"]._serialized_start = 2797
    _globals["_LIQUIDITYPROVISIONCANCELLATION"]._serialized_end = 2858
    _globals["_LIQUIDITYPROVISIONAMENDMENT"]._serialized_start = 2861
    _globals["_LIQUIDITYPROVISIONAMENDMENT"]._serialized_end = 3024
    _globals["_WITHDRAWSUBMISSION"]._serialized_start = 3026
    _globals["_WITHDRAWSUBMISSION"]._serialized_end = 3129
    _globals["_PROPOSALSUBMISSION"]._serialized_start = 3132
    _globals["_PROPOSALSUBMISSION"]._serialized_end = 3280
    _globals["_VOTESUBMISSION"]._serialized_start = 3282
    _globals["_VOTESUBMISSION"]._serialized_end = 3371
    _globals["_DELEGATESUBMISSION"]._serialized_start = 3373
    _globals["_DELEGATESUBMISSION"]._serialized_end = 3442
    _globals["_UNDELEGATESUBMISSION"]._serialized_start = 3445
    _globals["_UNDELEGATESUBMISSION"]._serialized_end = 3671
    _globals["_UNDELEGATESUBMISSION_METHOD"]._serialized_start = 3589
    _globals["_UNDELEGATESUBMISSION_METHOD"]._serialized_end = 3671
    _globals["_TRANSFER"]._serialized_start = 3674
    _globals["_TRANSFER"]._serialized_end = 4036
    _globals["_ONEOFFTRANSFER"]._serialized_start = 4038
    _globals["_ONEOFFTRANSFER"]._serialized_end = 4085
    _globals["_RECURRINGTRANSFER"]._serialized_start = 4088
    _globals["_RECURRINGTRANSFER"]._serialized_end = 4281
    _globals["_CANCELTRANSFER"]._serialized_start = 4283
    _globals["_CANCELTRANSFER"]._serialized_end = 4332
    _globals["_ISSUESIGNATURES"]._serialized_start = 4335
    _globals["_ISSUESIGNATURES"]._serialized_end = 4483
    _globals["_CREATEREFERRALSET"]._serialized_start = 4486
    _globals["_CREATEREFERRALSET"]._serialized_end = 4755
    _globals["_CREATEREFERRALSET_TEAM"]._serialized_start = 4600
    _globals["_CREATEREFERRALSET_TEAM"]._serialized_end = 4746
    _globals["_UPDATEREFERRALSET"]._serialized_start = 4758
    _globals["_UPDATEREFERRALSET"]._serialized_end = 5073
    _globals["_UPDATEREFERRALSET_TEAM"]._serialized_start = 4888
    _globals["_UPDATEREFERRALSET_TEAM"]._serialized_end = 5064
    _globals["_APPLYREFERRALCODE"]._serialized_start = 5075
    _globals["_APPLYREFERRALCODE"]._serialized_end = 5110
    _globals["_JOINTEAM"]._serialized_start = 5112
    _globals["_JOINTEAM"]._serialized_end = 5138
# @@protoc_insertion_point(module_scope)
