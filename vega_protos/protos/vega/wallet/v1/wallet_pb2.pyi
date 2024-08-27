from vega.commands.v1 import commands_pb2 as _commands_pb2
from vega.commands.v1 import data_pb2 as _data_pb2
from vega.commands.v1 import validator_commands_pb2 as _validator_commands_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class SubmitTransactionRequest(_message.Message):
    __slots__ = (
        "pub_key",
        "propagate",
        "order_submission",
        "order_cancellation",
        "order_amendment",
        "withdraw_submission",
        "proposal_submission",
        "vote_submission",
        "liquidity_provision_submission",
        "delegate_submission",
        "undelegate_submission",
        "liquidity_provision_cancellation",
        "liquidity_provision_amendment",
        "transfer",
        "cancel_transfer",
        "announce_node",
        "batch_market_instructions",
        "stop_orders_submission",
        "stop_orders_cancellation",
        "create_referral_set",
        "update_referral_set",
        "apply_referral_code",
        "update_margin_mode",
        "join_team",
        "batch_proposal_submission",
        "update_party_profile",
        "submit_amm",
        "amend_amm",
        "cancel_amm",
        "node_vote",
        "node_signature",
        "chain_event",
        "key_rotate_submission",
        "state_variable_proposal",
        "validator_heartbeat",
        "ethereum_key_rotate_submission",
        "protocol_upgrade_proposal",
        "issue_signatures",
        "oracle_data_submission",
    )
    PUB_KEY_FIELD_NUMBER: _ClassVar[int]
    PROPAGATE_FIELD_NUMBER: _ClassVar[int]
    ORDER_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    ORDER_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    ORDER_AMENDMENT_FIELD_NUMBER: _ClassVar[int]
    WITHDRAW_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    PROPOSAL_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    VOTE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISION_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    DELEGATE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    UNDELEGATE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISION_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_PROVISION_AMENDMENT_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_FIELD_NUMBER: _ClassVar[int]
    CANCEL_TRANSFER_FIELD_NUMBER: _ClassVar[int]
    ANNOUNCE_NODE_FIELD_NUMBER: _ClassVar[int]
    BATCH_MARKET_INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    STOP_ORDERS_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    STOP_ORDERS_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    CREATE_REFERRAL_SET_FIELD_NUMBER: _ClassVar[int]
    UPDATE_REFERRAL_SET_FIELD_NUMBER: _ClassVar[int]
    APPLY_REFERRAL_CODE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MARGIN_MODE_FIELD_NUMBER: _ClassVar[int]
    JOIN_TEAM_FIELD_NUMBER: _ClassVar[int]
    BATCH_PROPOSAL_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    UPDATE_PARTY_PROFILE_FIELD_NUMBER: _ClassVar[int]
    SUBMIT_AMM_FIELD_NUMBER: _ClassVar[int]
    AMEND_AMM_FIELD_NUMBER: _ClassVar[int]
    CANCEL_AMM_FIELD_NUMBER: _ClassVar[int]
    NODE_VOTE_FIELD_NUMBER: _ClassVar[int]
    NODE_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    CHAIN_EVENT_FIELD_NUMBER: _ClassVar[int]
    KEY_ROTATE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    STATE_VARIABLE_PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    ETHEREUM_KEY_ROTATE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_UPGRADE_PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    ISSUE_SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    ORACLE_DATA_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    pub_key: str
    propagate: bool
    order_submission: _commands_pb2.OrderSubmission
    order_cancellation: _commands_pb2.OrderCancellation
    order_amendment: _commands_pb2.OrderAmendment
    withdraw_submission: _commands_pb2.WithdrawSubmission
    proposal_submission: _commands_pb2.ProposalSubmission
    vote_submission: _commands_pb2.VoteSubmission
    liquidity_provision_submission: _commands_pb2.LiquidityProvisionSubmission
    delegate_submission: _commands_pb2.DelegateSubmission
    undelegate_submission: _commands_pb2.UndelegateSubmission
    liquidity_provision_cancellation: _commands_pb2.LiquidityProvisionCancellation
    liquidity_provision_amendment: _commands_pb2.LiquidityProvisionAmendment
    transfer: _commands_pb2.Transfer
    cancel_transfer: _commands_pb2.CancelTransfer
    announce_node: _validator_commands_pb2.AnnounceNode
    batch_market_instructions: _commands_pb2.BatchMarketInstructions
    stop_orders_submission: _commands_pb2.StopOrdersSubmission
    stop_orders_cancellation: _commands_pb2.StopOrdersCancellation
    create_referral_set: _commands_pb2.CreateReferralSet
    update_referral_set: _commands_pb2.UpdateReferralSet
    apply_referral_code: _commands_pb2.ApplyReferralCode
    update_margin_mode: _commands_pb2.UpdateMarginMode
    join_team: _commands_pb2.JoinTeam
    batch_proposal_submission: _commands_pb2.BatchProposalSubmission
    update_party_profile: _commands_pb2.UpdatePartyProfile
    submit_amm: _commands_pb2.SubmitAMM
    amend_amm: _commands_pb2.AmendAMM
    cancel_amm: _commands_pb2.CancelAMM
    node_vote: _validator_commands_pb2.NodeVote
    node_signature: _validator_commands_pb2.NodeSignature
    chain_event: _validator_commands_pb2.ChainEvent
    key_rotate_submission: _validator_commands_pb2.KeyRotateSubmission
    state_variable_proposal: _validator_commands_pb2.StateVariableProposal
    validator_heartbeat: _validator_commands_pb2.ValidatorHeartbeat
    ethereum_key_rotate_submission: _validator_commands_pb2.EthereumKeyRotateSubmission
    protocol_upgrade_proposal: _validator_commands_pb2.ProtocolUpgradeProposal
    issue_signatures: _commands_pb2.IssueSignatures
    oracle_data_submission: _data_pb2.OracleDataSubmission
    def __init__(
        self,
        pub_key: _Optional[str] = ...,
        propagate: bool = ...,
        order_submission: _Optional[
            _Union[_commands_pb2.OrderSubmission, _Mapping]
        ] = ...,
        order_cancellation: _Optional[
            _Union[_commands_pb2.OrderCancellation, _Mapping]
        ] = ...,
        order_amendment: _Optional[
            _Union[_commands_pb2.OrderAmendment, _Mapping]
        ] = ...,
        withdraw_submission: _Optional[
            _Union[_commands_pb2.WithdrawSubmission, _Mapping]
        ] = ...,
        proposal_submission: _Optional[
            _Union[_commands_pb2.ProposalSubmission, _Mapping]
        ] = ...,
        vote_submission: _Optional[
            _Union[_commands_pb2.VoteSubmission, _Mapping]
        ] = ...,
        liquidity_provision_submission: _Optional[
            _Union[_commands_pb2.LiquidityProvisionSubmission, _Mapping]
        ] = ...,
        delegate_submission: _Optional[
            _Union[_commands_pb2.DelegateSubmission, _Mapping]
        ] = ...,
        undelegate_submission: _Optional[
            _Union[_commands_pb2.UndelegateSubmission, _Mapping]
        ] = ...,
        liquidity_provision_cancellation: _Optional[
            _Union[_commands_pb2.LiquidityProvisionCancellation, _Mapping]
        ] = ...,
        liquidity_provision_amendment: _Optional[
            _Union[_commands_pb2.LiquidityProvisionAmendment, _Mapping]
        ] = ...,
        transfer: _Optional[_Union[_commands_pb2.Transfer, _Mapping]] = ...,
        cancel_transfer: _Optional[
            _Union[_commands_pb2.CancelTransfer, _Mapping]
        ] = ...,
        announce_node: _Optional[
            _Union[_validator_commands_pb2.AnnounceNode, _Mapping]
        ] = ...,
        batch_market_instructions: _Optional[
            _Union[_commands_pb2.BatchMarketInstructions, _Mapping]
        ] = ...,
        stop_orders_submission: _Optional[
            _Union[_commands_pb2.StopOrdersSubmission, _Mapping]
        ] = ...,
        stop_orders_cancellation: _Optional[
            _Union[_commands_pb2.StopOrdersCancellation, _Mapping]
        ] = ...,
        create_referral_set: _Optional[
            _Union[_commands_pb2.CreateReferralSet, _Mapping]
        ] = ...,
        update_referral_set: _Optional[
            _Union[_commands_pb2.UpdateReferralSet, _Mapping]
        ] = ...,
        apply_referral_code: _Optional[
            _Union[_commands_pb2.ApplyReferralCode, _Mapping]
        ] = ...,
        update_margin_mode: _Optional[
            _Union[_commands_pb2.UpdateMarginMode, _Mapping]
        ] = ...,
        join_team: _Optional[_Union[_commands_pb2.JoinTeam, _Mapping]] = ...,
        batch_proposal_submission: _Optional[
            _Union[_commands_pb2.BatchProposalSubmission, _Mapping]
        ] = ...,
        update_party_profile: _Optional[
            _Union[_commands_pb2.UpdatePartyProfile, _Mapping]
        ] = ...,
        submit_amm: _Optional[_Union[_commands_pb2.SubmitAMM, _Mapping]] = ...,
        amend_amm: _Optional[_Union[_commands_pb2.AmendAMM, _Mapping]] = ...,
        cancel_amm: _Optional[_Union[_commands_pb2.CancelAMM, _Mapping]] = ...,
        node_vote: _Optional[_Union[_validator_commands_pb2.NodeVote, _Mapping]] = ...,
        node_signature: _Optional[
            _Union[_validator_commands_pb2.NodeSignature, _Mapping]
        ] = ...,
        chain_event: _Optional[
            _Union[_validator_commands_pb2.ChainEvent, _Mapping]
        ] = ...,
        key_rotate_submission: _Optional[
            _Union[_validator_commands_pb2.KeyRotateSubmission, _Mapping]
        ] = ...,
        state_variable_proposal: _Optional[
            _Union[_validator_commands_pb2.StateVariableProposal, _Mapping]
        ] = ...,
        validator_heartbeat: _Optional[
            _Union[_validator_commands_pb2.ValidatorHeartbeat, _Mapping]
        ] = ...,
        ethereum_key_rotate_submission: _Optional[
            _Union[_validator_commands_pb2.EthereumKeyRotateSubmission, _Mapping]
        ] = ...,
        protocol_upgrade_proposal: _Optional[
            _Union[_validator_commands_pb2.ProtocolUpgradeProposal, _Mapping]
        ] = ...,
        issue_signatures: _Optional[
            _Union[_commands_pb2.IssueSignatures, _Mapping]
        ] = ...,
        oracle_data_submission: _Optional[
            _Union[_data_pb2.OracleDataSubmission, _Mapping]
        ] = ...,
    ) -> None: ...
