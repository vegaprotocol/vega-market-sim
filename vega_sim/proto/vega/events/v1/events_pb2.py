# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/events/v1/events.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ... import markets_pb2 as vega_dot_markets__pb2
from ... import assets_pb2 as vega_dot_assets__pb2
from ... import governance_pb2 as vega_dot_governance__pb2
from ... import vega_pb2 as vega_dot_vega__pb2
from ...oracles.v1 import spec_pb2 as vega_dot_oracles_dot_v1_dot_spec__pb2
from ...oracles.v1 import data_pb2 as vega_dot_oracles_dot_v1_dot_data__pb2
from ...commands.v1 import commands_pb2 as vega_dot_commands_dot_v1_dot_commands__pb2
from ...commands.v1 import oracles_pb2 as vega_dot_commands_dot_v1_dot_oracles__pb2
from ...commands.v1 import (
    validator_commands_pb2 as vega_dot_commands_dot_v1_dot_validator__commands__pb2,
)


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1bvega/events/v1/events.proto\x12\x0evega.events.v1\x1a\x12vega/markets.proto\x1a\x11vega/assets.proto\x1a\x15vega/governance.proto\x1a\x0fvega/vega.proto\x1a\x1avega/oracles/v1/spec.proto\x1a\x1avega/oracles/v1/data.proto\x1a\x1fvega/commands/v1/commands.proto\x1a\x1evega/commands/v1/oracles.proto\x1a)vega/commands/v1/validator_commands.proto"\xee\x01\n\x18\x45RC20MultiSigSignerAdded\x12!\n\x0csignature_id\x18\x01 \x01(\tR\x0bsignatureId\x12!\n\x0cvalidator_id\x18\x02 \x01(\tR\x0bvalidatorId\x12\x1c\n\ttimestamp\x18\x03 \x01(\x03R\ttimestamp\x12\x1d\n\nnew_signer\x18\x04 \x01(\tR\tnewSigner\x12\x1c\n\tsubmitter\x18\x05 \x01(\tR\tsubmitter\x12\x14\n\x05nonce\x18\x06 \x01(\tR\x05nonce\x12\x1b\n\tepoch_seq\x18\x07 \x01(\tR\x08\x65pochSeq"f\n#ERC20MultiSigSignerRemovedSubmitter\x12!\n\x0csignature_id\x18\x01 \x01(\tR\x0bsignatureId\x12\x1c\n\tsubmitter\x18\x02 \x01(\tR\tsubmitter"\x97\x02\n\x1a\x45RC20MultiSigSignerRemoved\x12\x66\n\x14signature_submitters\x18\x01 \x03(\x0b\x32\x33.vega.events.v1.ERC20MultiSigSignerRemovedSubmitterR\x13signatureSubmitters\x12!\n\x0cvalidator_id\x18\x02 \x01(\tR\x0bvalidatorId\x12\x1c\n\ttimestamp\x18\x03 \x01(\x03R\ttimestamp\x12\x1d\n\nold_signer\x18\x04 \x01(\tR\toldSigner\x12\x14\n\x05nonce\x18\x05 \x01(\tR\x05nonce\x12\x1b\n\tepoch_seq\x18\x06 \x01(\tR\x08\x65pochSeq"\xe8\x04\n\x08Transfer\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x12\n\x04\x66rom\x18\x02 \x01(\tR\x04\x66rom\x12=\n\x11\x66rom_account_type\x18\x03 \x01(\x0e\x32\x11.vega.AccountTypeR\x0f\x66romAccountType\x12\x0e\n\x02to\x18\x04 \x01(\tR\x02to\x12\x39\n\x0fto_account_type\x18\x05 \x01(\x0e\x32\x11.vega.AccountTypeR\rtoAccountType\x12\x14\n\x05\x61sset\x18\x06 \x01(\tR\x05\x61sset\x12\x16\n\x06\x61mount\x18\x07 \x01(\tR\x06\x61mount\x12\x1c\n\treference\x18\x08 \x01(\tR\treference\x12\x37\n\x06status\x18\t \x01(\x0e\x32\x1f.vega.events.v1.Transfer.StatusR\x06status\x12\x1c\n\ttimestamp\x18\n \x01(\x03R\ttimestamp\x12\x39\n\x07one_off\x18\x65 \x01(\x0b\x32\x1e.vega.events.v1.OneOffTransferH\x00R\x06oneOff\x12\x41\n\trecurring\x18\x66 \x01(\x0b\x32!.vega.events.v1.RecurringTransferH\x00R\trecurring"\x84\x01\n\x06Status\x12\x16\n\x12STATUS_UNSPECIFIED\x10\x00\x12\x12\n\x0eSTATUS_PENDING\x10\x01\x12\x0f\n\x0bSTATUS_DONE\x10\x02\x12\x13\n\x0fSTATUS_REJECTED\x10\x03\x12\x12\n\x0eSTATUS_STOPPED\x10\x04\x12\x14\n\x10STATUS_CANCELLED\x10\x05\x42\x06\n\x04kind"/\n\x0eOneOffTransfer\x12\x1d\n\ndeliver_on\x18\x01 \x01(\x03R\tdeliverOn"\xc1\x01\n\x11RecurringTransfer\x12\x1f\n\x0bstart_epoch\x18\x01 \x01(\x04R\nstartEpoch\x12 \n\tend_epoch\x18\x02 \x01(\x04H\x00R\x08\x65ndEpoch\x88\x01\x01\x12\x16\n\x06\x66\x61\x63tor\x18\x03 \x01(\tR\x06\x66\x61\x63tor\x12\x43\n\x11\x64ispatch_strategy\x18\x04 \x01(\x0b\x32\x16.vega.DispatchStrategyR\x10\x64ispatchStrategyB\x0c\n\n_end_epoch"\xb4\x04\n\x0cStakeLinking\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x35\n\x04type\x18\x02 \x01(\x0e\x32!.vega.events.v1.StakeLinking.TypeR\x04type\x12\x0e\n\x02ts\x18\x03 \x01(\x03R\x02ts\x12\x14\n\x05party\x18\x04 \x01(\tR\x05party\x12\x16\n\x06\x61mount\x18\x05 \x01(\tR\x06\x61mount\x12;\n\x06status\x18\x06 \x01(\x0e\x32#.vega.events.v1.StakeLinking.StatusR\x06status\x12!\n\x0c\x66inalized_at\x18\x07 \x01(\x03R\x0b\x66inalizedAt\x12\x17\n\x07tx_hash\x18\x08 \x01(\tR\x06txHash\x12!\n\x0c\x62lock_height\x18\t \x01(\x04R\x0b\x62lockHeight\x12\x1d\n\nblock_time\x18\n \x01(\x03R\tblockTime\x12\x1b\n\tlog_index\x18\x0b \x01(\x04R\x08logIndex\x12)\n\x10\x65thereum_address\x18\x0c \x01(\tR\x0f\x65thereumAddress"<\n\x04Type\x12\x14\n\x10TYPE_UNSPECIFIED\x10\x00\x12\r\n\tTYPE_LINK\x10\x01\x12\x0f\n\x0bTYPE_UNLINK\x10\x02"^\n\x06Status\x12\x16\n\x12STATUS_UNSPECIFIED\x10\x00\x12\x12\n\x0eSTATUS_PENDING\x10\x01\x12\x13\n\x0fSTATUS_ACCEPTED\x10\x02\x12\x13\n\x0fSTATUS_REJECTED\x10\x03"\xd3\x02\n\x18\x45RC20MultiSigSignerEvent\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x41\n\x04type\x18\x02 \x01(\x0e\x32-.vega.events.v1.ERC20MultiSigSignerEvent.TypeR\x04type\x12\x16\n\x06signer\x18\x03 \x01(\tR\x06signer\x12\x14\n\x05nonce\x18\x04 \x01(\tR\x05nonce\x12\x1d\n\nblock_time\x18\x05 \x01(\x03R\tblockTime\x12\x17\n\x07tx_hash\x18\x06 \x01(\tR\x06txHash\x12\x1b\n\tlog_index\x18\x07 \x01(\x04R\x08logIndex\x12!\n\x0c\x62lock_number\x18\x08 \x01(\x04R\x0b\x62lockNumber">\n\x04Type\x12\x14\n\x10TYPE_UNSPECIFIED\x10\x00\x12\x0e\n\nTYPE_ADDED\x10\x01\x12\x10\n\x0cTYPE_REMOVED\x10\x02"\xe3\x01\n\x1e\x45RC20MultiSigThresholdSetEvent\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12#\n\rnew_threshold\x18\x02 \x01(\rR\x0cnewThreshold\x12\x14\n\x05nonce\x18\x03 \x01(\tR\x05nonce\x12\x1d\n\nblock_time\x18\x04 \x01(\x03R\tblockTime\x12\x17\n\x07tx_hash\x18\x05 \x01(\tR\x06txHash\x12\x1b\n\tlog_index\x18\x06 \x01(\x04R\x08logIndex\x12!\n\x0c\x62lock_number\x18\x07 \x01(\x04R\x0b\x62lockNumber"g\n\x0f\x43heckpointEvent\x12\x12\n\x04hash\x18\x01 \x01(\tR\x04hash\x12\x1d\n\nblock_hash\x18\x02 \x01(\tR\tblockHash\x12!\n\x0c\x62lock_height\x18\x03 \x01(\x04R\x0b\x62lockHeight"-\n\x10StreamStartEvent\x12\x19\n\x08\x63hain_id\x18\x01 \x01(\tR\x07\x63hainId"\x82\x02\n\x11RewardPayoutEvent\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x1b\n\tepoch_seq\x18\x02 \x01(\tR\x08\x65pochSeq\x12\x14\n\x05\x61sset\x18\x03 \x01(\tR\x05\x61sset\x12\x16\n\x06\x61mount\x18\x04 \x01(\tR\x06\x61mount\x12\x35\n\x17percent_of_total_reward\x18\x05 \x01(\tR\x14percentOfTotalReward\x12\x1c\n\ttimestamp\x18\x06 \x01(\x03R\ttimestamp\x12\x1f\n\x0breward_type\x18\x07 \x01(\tR\nrewardType\x12\x16\n\x06market\x18\x08 \x01(\tR\x06market"\xd6\x02\n\x13ValidatorScoreEvent\x12\x17\n\x07node_id\x18\x01 \x01(\tR\x06nodeId\x12\x1b\n\tepoch_seq\x18\x02 \x01(\tR\x08\x65pochSeq\x12\'\n\x0fvalidator_score\x18\x03 \x01(\tR\x0evalidatorScore\x12)\n\x10normalised_score\x18\x04 \x01(\tR\x0fnormalisedScore\x12\x33\n\x15validator_performance\x18\x05 \x01(\tR\x14validatorPerformance\x12.\n\x13raw_validator_score\x18\x06 \x01(\tR\x11rawValidatorScore\x12)\n\x10validator_status\x18\x07 \x01(\tR\x0fvalidatorStatus\x12%\n\x0emultisig_score\x18\x08 \x01(\tR\rmultisigScore"|\n\x16\x44\x65legationBalanceEvent\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x17\n\x07node_id\x18\x02 \x01(\tR\x06nodeId\x12\x16\n\x06\x61mount\x18\x03 \x01(\tR\x06\x61mount\x12\x1b\n\tepoch_seq\x18\x04 \x01(\tR\x08\x65pochSeq"D\n\x0bMarketEvent\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12\x18\n\x07payload\x18\x02 \x01(\tR\x07payload"\xbe\x0c\n\x0cTxErrorEvent\x12\x19\n\x08party_id\x18\x01 \x01(\tR\x07partyId\x12\x17\n\x07\x65rr_msg\x18\x02 \x01(\tR\x06\x65rrMsg\x12N\n\x10order_submission\x18\x65 \x01(\x0b\x32!.vega.commands.v1.OrderSubmissionH\x00R\x0forderSubmission\x12K\n\x0forder_amendment\x18\x66 \x01(\x0b\x32 .vega.commands.v1.OrderAmendmentH\x00R\x0eorderAmendment\x12T\n\x12order_cancellation\x18g \x01(\x0b\x32#.vega.commands.v1.OrderCancellationH\x00R\x11orderCancellation\x12\x42\n\x08proposal\x18h \x01(\x0b\x32$.vega.commands.v1.ProposalSubmissionH\x00R\x08proposal\x12K\n\x0fvote_submission\x18i \x01(\x0b\x32 .vega.commands.v1.VoteSubmissionH\x00R\x0evoteSubmission\x12v\n\x1eliquidity_provision_submission\x18j \x01(\x0b\x32..vega.commands.v1.LiquidityProvisionSubmissionH\x00R\x1cliquidityProvisionSubmission\x12W\n\x13withdraw_submission\x18k \x01(\x0b\x32$.vega.commands.v1.WithdrawSubmissionH\x00R\x12withdrawSubmission\x12W\n\x13\x64\x65legate_submission\x18l \x01(\x0b\x32$.vega.commands.v1.DelegateSubmissionH\x00R\x12\x64\x65legateSubmission\x12]\n\x15undelegate_submission\x18m \x01(\x0b\x32&.vega.commands.v1.UndelegateSubmissionH\x00R\x14undelegateSubmission\x12|\n liquidity_provision_cancellation\x18o \x01(\x0b\x32\x30.vega.commands.v1.LiquidityProvisionCancellationH\x00R\x1eliquidityProvisionCancellation\x12s\n\x1dliquidity_provision_amendment\x18p \x01(\x0b\x32-.vega.commands.v1.LiquidityProvisionAmendmentH\x00R\x1bliquidityProvisionAmendment\x12\x38\n\x08transfer\x18q \x01(\x0b\x32\x1a.vega.commands.v1.TransferH\x00R\x08transfer\x12K\n\x0f\x63\x61ncel_transfer\x18r \x01(\x0b\x32 .vega.commands.v1.CancelTransferH\x00R\x0e\x63\x61ncelTransfer\x12\x45\n\rannounce_node\x18s \x01(\x0b\x32\x1e.vega.commands.v1.AnnounceNodeH\x00R\x0c\x61nnounceNode\x12^\n\x16oracle_data_submission\x18t \x01(\x0b\x32&.vega.commands.v1.OracleDataSubmissionH\x00R\x14oracleDataSubmission\x12g\n\x19protocol_upgrade_proposal\x18u \x01(\x0b\x32).vega.commands.v1.ProtocolUpgradeProposalH\x00R\x17protocolUpgradeProposal\x12N\n\x10issue_signatures\x18v \x01(\x0b\x32!.vega.commands.v1.IssueSignaturesH\x00R\x0fissueSignaturesB\r\n\x0btransactionJ\x04\x08n\x10o"*\n\nTimeUpdate\x12\x1c\n\ttimestamp\x18\x01 \x01(\x03R\ttimestamp"\xa4\x01\n\nEpochEvent\x12\x10\n\x03seq\x18\x01 \x01(\x04R\x03seq\x12)\n\x06\x61\x63tion\x18\x02 \x01(\x0e\x32\x11.vega.EpochActionR\x06\x61\x63tion\x12\x1d\n\nstart_time\x18\x03 \x01(\x03R\tstartTime\x12\x1f\n\x0b\x65xpire_time\x18\x04 \x01(\x03R\nexpireTime\x12\x19\n\x08\x65nd_time\x18\x05 \x01(\x03R\x07\x65ndTime"I\n\x11TransferResponses\x12\x34\n\tresponses\x18\x01 \x03(\x0b\x32\x16.vega.TransferResponseR\tresponses"\x88\x01\n\x12PositionResolution\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12\x1e\n\ndistressed\x18\x02 \x01(\x03R\ndistressed\x12\x16\n\x06\x63losed\x18\x03 \x01(\x03R\x06\x63losed\x12\x1d\n\nmark_price\x18\x04 \x01(\tR\tmarkPrice"c\n\x11LossSocialization\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12\x19\n\x08party_id\x18\x02 \x01(\tR\x07partyId\x12\x16\n\x06\x61mount\x18\x03 \x01(\tR\x06\x61mount"^\n\x0fTradeSettlement\x12\x12\n\x04size\x18\x01 \x01(\x03R\x04size\x12\x14\n\x05price\x18\x02 \x01(\tR\x05price\x12!\n\x0cmarket_price\x18\x03 \x01(\tR\x0bmarketPrice"\xd5\x01\n\x0eSettlePosition\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12\x19\n\x08party_id\x18\x02 \x01(\tR\x07partyId\x12\x14\n\x05price\x18\x03 \x01(\tR\x05price\x12L\n\x11trade_settlements\x18\x04 \x03(\x0b\x32\x1f.vega.events.v1.TradeSettlementR\x10tradeSettlements\x12\'\n\x0fposition_factor\x18\x05 \x01(\tR\x0epositionFactor"\xf6\x01\n\x12PositionStateEvent\x12\x19\n\x08party_id\x18\x01 \x01(\tR\x07partyId\x12\x1b\n\tmarket_id\x18\x02 \x01(\tR\x08marketId\x12\x12\n\x04size\x18\x03 \x01(\x03R\x04size\x12%\n\x0epotential_buys\x18\x04 \x01(\x03R\rpotentialBuys\x12\'\n\x0fpotential_sells\x18\x05 \x01(\x03R\x0epotentialSells\x12 \n\x0cvw_buy_price\x18\x06 \x01(\tR\nvwBuyPrice\x12"\n\rvw_sell_price\x18\x07 \x01(\tR\x0bvwSellPrice"x\n\x10SettleDistressed\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12\x19\n\x08party_id\x18\x02 \x01(\tR\x07partyId\x12\x16\n\x06margin\x18\x03 \x01(\tR\x06margin\x12\x14\n\x05price\x18\x04 \x01(\tR\x05price"0\n\nMarketTick\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x12\n\x04time\x18\x02 \x01(\x03R\x04time"\x85\x02\n\x0c\x41uctionEvent\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12\'\n\x0fopening_auction\x18\x02 \x01(\x08R\x0eopeningAuction\x12\x14\n\x05leave\x18\x03 \x01(\x08R\x05leave\x12\x14\n\x05start\x18\x04 \x01(\x03R\x05start\x12\x10\n\x03\x65nd\x18\x05 \x01(\x03R\x03\x65nd\x12.\n\x07trigger\x18\x06 \x01(\x0e\x32\x14.vega.AuctionTriggerR\x07trigger\x12\x41\n\x11\x65xtension_trigger\x18\x07 \x01(\x0e\x32\x14.vega.AuctionTriggerR\x10\x65xtensionTrigger"\x8c\x03\n\x0fValidatorUpdate\x12\x17\n\x07node_id\x18\x01 \x01(\tR\x06nodeId\x12 \n\x0cvega_pub_key\x18\x02 \x01(\tR\nvegaPubKey\x12)\n\x10\x65thereum_address\x18\x03 \x01(\tR\x0f\x65thereumAddress\x12\x1c\n\ntm_pub_key\x18\x04 \x01(\tR\x08tmPubKey\x12\x19\n\x08info_url\x18\x05 \x01(\tR\x07infoUrl\x12\x18\n\x07\x63ountry\x18\x06 \x01(\tR\x07\x63ountry\x12\x12\n\x04name\x18\x07 \x01(\tR\x04name\x12\x1d\n\navatar_url\x18\x08 \x01(\tR\tavatarUrl\x12+\n\x12vega_pub_key_index\x18\t \x01(\rR\x0fvegaPubKeyIndex\x12\x14\n\x05\x61\x64\x64\x65\x64\x18\n \x01(\x08R\x05\x61\x64\x64\x65\x64\x12\x1d\n\nfrom_epoch\x18\x0b \x01(\x04R\tfromEpoch\x12+\n\x11submitter_address\x18\x0c \x01(\tR\x10submitterAddress"\xb2\x02\n\x15ValidatorRankingEvent\x12\x17\n\x07node_id\x18\x01 \x01(\tR\x06nodeId\x12\x1f\n\x0bstake_score\x18\x02 \x01(\tR\nstakeScore\x12+\n\x11performance_score\x18\x03 \x01(\tR\x10performanceScore\x12#\n\rranking_score\x18\x04 \x01(\tR\x0crankingScore\x12\'\n\x0fprevious_status\x18\x05 \x01(\tR\x0epreviousStatus\x12\x1f\n\x0bnext_status\x18\x06 \x01(\tR\nnextStatus\x12\x1b\n\tepoch_seq\x18\x07 \x01(\tR\x08\x65pochSeq\x12&\n\x0ftm_voting_power\x18\x08 \x01(\rR\rtmVotingPower"\x89\x01\n\x0bKeyRotation\x12\x17\n\x07node_id\x18\x01 \x01(\tR\x06nodeId\x12\x1e\n\x0bold_pub_key\x18\x02 \x01(\tR\toldPubKey\x12\x1e\n\x0bnew_pub_key\x18\x03 \x01(\tR\tnewPubKey\x12!\n\x0c\x62lock_height\x18\x04 \x01(\x04R\x0b\x62lockHeight"\x93\x01\n\x13\x45thereumKeyRotation\x12\x17\n\x07node_id\x18\x01 \x01(\tR\x06nodeId\x12\x1f\n\x0bold_address\x18\x02 \x01(\tR\noldAddress\x12\x1f\n\x0bnew_address\x18\x03 \x01(\tR\nnewAddress\x12!\n\x0c\x62lock_height\x18\x04 \x01(\x04R\x0b\x62lockHeight"\xd7\x01\n\x14ProtocolUpgradeEvent\x12\x30\n\x14upgrade_block_height\x18\x01 \x01(\x04R\x12upgradeBlockHeight\x12(\n\x10vega_release_tag\x18\x02 \x01(\tR\x0evegaReleaseTag\x12\x1c\n\tapprovers\x18\x03 \x03(\tR\tapprovers\x12\x45\n\x06status\x18\x04 \x01(\x0e\x32-.vega.events.v1.ProtocolUpgradeProposalStatusR\x06status"K\n\x08StateVar\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x19\n\x08\x65vent_id\x18\x02 \x01(\tR\x07\x65ventId\x12\x14\n\x05state\x18\x03 \x01(\tR\x05state"\x8c\x1b\n\x08\x42usEvent\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x14\n\x05\x62lock\x18\x02 \x01(\tR\x05\x62lock\x12\x30\n\x04type\x18\x03 \x01(\x0e\x32\x1c.vega.events.v1.BusEventTypeR\x04type\x12=\n\x0btime_update\x18\x65 \x01(\x0b\x32\x1a.vega.events.v1.TimeUpdateH\x00R\ntimeUpdate\x12R\n\x12transfer_responses\x18\x66 \x01(\x0b\x32!.vega.events.v1.TransferResponsesH\x00R\x11transferResponses\x12U\n\x13position_resolution\x18g \x01(\x0b\x32".vega.events.v1.PositionResolutionH\x00R\x12positionResolution\x12#\n\x05order\x18h \x01(\x0b\x32\x0b.vega.OrderH\x00R\x05order\x12)\n\x07\x61\x63\x63ount\x18i \x01(\x0b\x32\r.vega.AccountH\x00R\x07\x61\x63\x63ount\x12#\n\x05party\x18j \x01(\x0b\x32\x0b.vega.PartyH\x00R\x05party\x12#\n\x05trade\x18k \x01(\x0b\x32\x0b.vega.TradeH\x00R\x05trade\x12\x39\n\rmargin_levels\x18l \x01(\x0b\x32\x12.vega.MarginLevelsH\x00R\x0cmarginLevels\x12,\n\x08proposal\x18m \x01(\x0b\x32\x0e.vega.ProposalH\x00R\x08proposal\x12 \n\x04vote\x18n \x01(\x0b\x32\n.vega.VoteH\x00R\x04vote\x12\x33\n\x0bmarket_data\x18o \x01(\x0b\x32\x10.vega.MarketDataH\x00R\nmarketData\x12H\n\x0enode_signature\x18p \x01(\x0b\x32\x1f.vega.commands.v1.NodeSignatureH\x00R\rnodeSignature\x12R\n\x12loss_socialization\x18q \x01(\x0b\x32!.vega.events.v1.LossSocializationH\x00R\x11lossSocialization\x12I\n\x0fsettle_position\x18r \x01(\x0b\x32\x1e.vega.events.v1.SettlePositionH\x00R\x0esettlePosition\x12O\n\x11settle_distressed\x18s \x01(\x0b\x32 .vega.events.v1.SettleDistressedH\x00R\x10settleDistressed\x12\x35\n\x0emarket_created\x18t \x01(\x0b\x32\x0c.vega.MarketH\x00R\rmarketCreated\x12#\n\x05\x61sset\x18u \x01(\x0b\x32\x0b.vega.AssetH\x00R\x05\x61sset\x12=\n\x0bmarket_tick\x18v \x01(\x0b\x32\x1a.vega.events.v1.MarketTickH\x00R\nmarketTick\x12\x32\n\nwithdrawal\x18w \x01(\x0b\x32\x10.vega.WithdrawalH\x00R\nwithdrawal\x12)\n\x07\x64\x65posit\x18x \x01(\x0b\x32\r.vega.DepositH\x00R\x07\x64\x65posit\x12\x38\n\x07\x61uction\x18y \x01(\x0b\x32\x1c.vega.events.v1.AuctionEventH\x00R\x07\x61uction\x12\x33\n\x0brisk_factor\x18z \x01(\x0b\x32\x10.vega.RiskFactorH\x00R\nriskFactor\x12\x45\n\x11network_parameter\x18{ \x01(\x0b\x32\x16.vega.NetworkParameterH\x00R\x10networkParameter\x12K\n\x13liquidity_provision\x18| \x01(\x0b\x32\x18.vega.LiquidityProvisionH\x00R\x12liquidityProvision\x12\x35\n\x0emarket_updated\x18} \x01(\x0b\x32\x0c.vega.MarketH\x00R\rmarketUpdated\x12\x39\n\x0boracle_spec\x18~ \x01(\x0b\x32\x16.oracles.v1.OracleSpecH\x00R\noracleSpec\x12\x39\n\x0boracle_data\x18\x7f \x01(\x0b\x32\x16.oracles.v1.OracleDataH\x00R\noracleData\x12X\n\x12\x64\x65legation_balance\x18\x81\x01 \x01(\x0b\x32&.vega.events.v1.DelegationBalanceEventH\x00R\x11\x64\x65legationBalance\x12O\n\x0fvalidator_score\x18\x82\x01 \x01(\x0b\x32#.vega.events.v1.ValidatorScoreEventH\x00R\x0evalidatorScore\x12>\n\x0b\x65poch_event\x18\x83\x01 \x01(\x0b\x32\x1a.vega.events.v1.EpochEventH\x00R\nepochEvent\x12M\n\x10validator_update\x18\x84\x01 \x01(\x0b\x32\x1f.vega.events.v1.ValidatorUpdateH\x00R\x0fvalidatorUpdate\x12\x44\n\rstake_linking\x18\x85\x01 \x01(\x0b\x32\x1c.vega.events.v1.StakeLinkingH\x00R\x0cstakeLinking\x12I\n\rreward_payout\x18\x86\x01 \x01(\x0b\x32!.vega.events.v1.RewardPayoutEventH\x00R\x0crewardPayout\x12\x42\n\ncheckpoint\x18\x87\x01 \x01(\x0b\x32\x1f.vega.events.v1.CheckpointEventH\x00R\ncheckpoint\x12\x41\n\x0ckey_rotation\x18\x88\x01 \x01(\x0b\x32\x1b.vega.events.v1.KeyRotationH\x00R\x0bkeyRotation\x12\x38\n\tstate_var\x18\x89\x01 \x01(\x0b\x32\x18.vega.events.v1.StateVarH\x00R\x08stateVar\x12=\n\x0enetwork_limits\x18\x8a\x01 \x01(\x0b\x32\x13.vega.NetworkLimitsH\x00R\rnetworkLimits\x12\x37\n\x08transfer\x18\x8b\x01 \x01(\x0b\x32\x18.vega.events.v1.TransferH\x00R\x08transfer\x12M\n\rranking_event\x18\x8c\x01 \x01(\x0b\x32%.vega.events.v1.ValidatorRankingEventH\x00R\x0crankingEvent\x12j\n\x1b\x65rc20_multisig_signer_event\x18\x8d\x01 \x01(\x0b\x32(.vega.events.v1.ERC20MultiSigSignerEventH\x00R\x18\x65rc20MultisigSignerEvent\x12}\n"erc20_multisig_set_threshold_event\x18\x8e\x01 \x01(\x0b\x32..vega.events.v1.ERC20MultiSigThresholdSetEventH\x00R\x1e\x65rc20MultisigSetThresholdEvent\x12j\n\x1b\x65rc20_multisig_signer_added\x18\x8f\x01 \x01(\x0b\x32(.vega.events.v1.ERC20MultiSigSignerAddedH\x00R\x18\x65rc20MultisigSignerAdded\x12p\n\x1d\x65rc20_multisig_signer_removed\x18\x90\x01 \x01(\x0b\x32*.vega.events.v1.ERC20MultiSigSignerRemovedH\x00R\x1a\x65rc20MultisigSignerRemoved\x12W\n\x14position_state_event\x18\x91\x01 \x01(\x0b\x32".vega.events.v1.PositionStateEventH\x00R\x12positionStateEvent\x12Z\n\x15\x65thereum_key_rotation\x18\x92\x01 \x01(\x0b\x32#.vega.events.v1.EthereumKeyRotationH\x00R\x13\x65thereumKeyRotation\x12]\n\x16protocol_upgrade_event\x18\x93\x01 \x01(\x0b\x32$.vega.events.v1.ProtocolUpgradeEventH\x00R\x14protocolUpgradeEvent\x12\x36\n\x06market\x18\xe9\x07 \x01(\x0b\x32\x1b.vega.events.v1.MarketEventH\x00R\x06market\x12\x41\n\x0ctx_err_event\x18\xd1\x0f \x01(\x0b\x32\x1c.vega.events.v1.TxErrorEventH\x00R\ntxErrEvent\x12\x18\n\x07version\x18\x04 \x01(\rR\x07version\x12\x19\n\x08\x63hain_id\x18\x05 \x01(\tR\x07\x63hainId\x12\x17\n\x07tx_hash\x18\x06 \x01(\tR\x06txHashB\x07\n\x05\x65vent*\xdd\x01\n\x1dProtocolUpgradeProposalStatus\x12\x30\n,PROTOCOL_UPGRADE_PROPOSAL_STATUS_UNSPECIFIED\x10\x00\x12,\n(PROTOCOL_UPGRADE_PROPOSAL_STATUS_PENDING\x10\x01\x12-\n)PROTOCOL_UPGRADE_PROPOSAL_STATUS_APPROVED\x10\x02\x12-\n)PROTOCOL_UPGRADE_PROPOSAL_STATUS_REJECTED\x10\x03*\xeb\r\n\x0c\x42usEventType\x12\x1e\n\x1a\x42US_EVENT_TYPE_UNSPECIFIED\x10\x00\x12\x16\n\x12\x42US_EVENT_TYPE_ALL\x10\x01\x12\x1e\n\x1a\x42US_EVENT_TYPE_TIME_UPDATE\x10\x02\x12%\n!BUS_EVENT_TYPE_TRANSFER_RESPONSES\x10\x03\x12&\n"BUS_EVENT_TYPE_POSITION_RESOLUTION\x10\x04\x12\x18\n\x14\x42US_EVENT_TYPE_ORDER\x10\x05\x12\x1a\n\x16\x42US_EVENT_TYPE_ACCOUNT\x10\x06\x12\x18\n\x14\x42US_EVENT_TYPE_PARTY\x10\x07\x12\x18\n\x14\x42US_EVENT_TYPE_TRADE\x10\x08\x12 \n\x1c\x42US_EVENT_TYPE_MARGIN_LEVELS\x10\t\x12\x1b\n\x17\x42US_EVENT_TYPE_PROPOSAL\x10\n\x12\x17\n\x13\x42US_EVENT_TYPE_VOTE\x10\x0b\x12\x1e\n\x1a\x42US_EVENT_TYPE_MARKET_DATA\x10\x0c\x12!\n\x1d\x42US_EVENT_TYPE_NODE_SIGNATURE\x10\r\x12%\n!BUS_EVENT_TYPE_LOSS_SOCIALIZATION\x10\x0e\x12"\n\x1e\x42US_EVENT_TYPE_SETTLE_POSITION\x10\x0f\x12$\n BUS_EVENT_TYPE_SETTLE_DISTRESSED\x10\x10\x12!\n\x1d\x42US_EVENT_TYPE_MARKET_CREATED\x10\x11\x12\x18\n\x14\x42US_EVENT_TYPE_ASSET\x10\x12\x12\x1e\n\x1a\x42US_EVENT_TYPE_MARKET_TICK\x10\x13\x12\x1d\n\x19\x42US_EVENT_TYPE_WITHDRAWAL\x10\x14\x12\x1a\n\x16\x42US_EVENT_TYPE_DEPOSIT\x10\x15\x12\x1a\n\x16\x42US_EVENT_TYPE_AUCTION\x10\x16\x12\x1e\n\x1a\x42US_EVENT_TYPE_RISK_FACTOR\x10\x17\x12$\n BUS_EVENT_TYPE_NETWORK_PARAMETER\x10\x18\x12&\n"BUS_EVENT_TYPE_LIQUIDITY_PROVISION\x10\x19\x12!\n\x1d\x42US_EVENT_TYPE_MARKET_UPDATED\x10\x1a\x12\x1e\n\x1a\x42US_EVENT_TYPE_ORACLE_SPEC\x10\x1b\x12\x1e\n\x1a\x42US_EVENT_TYPE_ORACLE_DATA\x10\x1c\x12%\n!BUS_EVENT_TYPE_DELEGATION_BALANCE\x10\x1d\x12"\n\x1e\x42US_EVENT_TYPE_VALIDATOR_SCORE\x10\x1e\x12\x1f\n\x1b\x42US_EVENT_TYPE_EPOCH_UPDATE\x10\x1f\x12#\n\x1f\x42US_EVENT_TYPE_VALIDATOR_UPDATE\x10 \x12 \n\x1c\x42US_EVENT_TYPE_STAKE_LINKING\x10!\x12&\n"BUS_EVENT_TYPE_REWARD_PAYOUT_EVENT\x10"\x12\x1d\n\x19\x42US_EVENT_TYPE_CHECKPOINT\x10#\x12\x1f\n\x1b\x42US_EVENT_TYPE_STREAM_START\x10$\x12\x1f\n\x1b\x42US_EVENT_TYPE_KEY_ROTATION\x10%\x12\x1c\n\x18\x42US_EVENT_TYPE_STATE_VAR\x10&\x12!\n\x1d\x42US_EVENT_TYPE_NETWORK_LIMITS\x10\'\x12\x1b\n\x17\x42US_EVENT_TYPE_TRANSFER\x10(\x12$\n BUS_EVENT_TYPE_VALIDATOR_RANKING\x10)\x12/\n+BUS_EVENT_TYPE_ERC20_MULTI_SIG_SIGNER_EVENT\x10*\x12\x30\n,BUS_EVENT_TYPE_ERC20_MULTI_SIG_SET_THRESHOLD\x10+\x12/\n+BUS_EVENT_TYPE_ERC20_MULTI_SIG_SIGNER_ADDED\x10,\x12\x31\n-BUS_EVENT_TYPE_ERC20_MULTI_SIG_SIGNER_REMOVED\x10-\x12!\n\x1d\x42US_EVENT_TYPE_POSITION_STATE\x10.\x12(\n$BUS_EVENT_TYPE_ETHEREUM_KEY_ROTATION\x10/\x12,\n(BUS_EVENT_TYPE_PROTOCOL_UPGRADE_PROPOSAL\x10\x30\x12\x19\n\x15\x42US_EVENT_TYPE_MARKET\x10\x65\x12\x1c\n\x17\x42US_EVENT_TYPE_TX_ERROR\x10\xc9\x01\x42\x31Z/code.vegaprotocol.io/vega/protos/vega/events/v1b\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "vega.events.v1.events_pb2", globals()
)
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = (
        b"Z/code.vegaprotocol.io/vega/protos/vega/events/v1"
    )
    _PROTOCOLUPGRADEPROPOSALSTATUS._serialized_start = 11763
    _PROTOCOLUPGRADEPROPOSALSTATUS._serialized_end = 11984
    _BUSEVENTTYPE._serialized_start = 11987
    _BUSEVENTTYPE._serialized_end = 13758
    _ERC20MULTISIGSIGNERADDED._serialized_start = 291
    _ERC20MULTISIGSIGNERADDED._serialized_end = 529
    _ERC20MULTISIGSIGNERREMOVEDSUBMITTER._serialized_start = 531
    _ERC20MULTISIGSIGNERREMOVEDSUBMITTER._serialized_end = 633
    _ERC20MULTISIGSIGNERREMOVED._serialized_start = 636
    _ERC20MULTISIGSIGNERREMOVED._serialized_end = 915
    _TRANSFER._serialized_start = 918
    _TRANSFER._serialized_end = 1534
    _TRANSFER_STATUS._serialized_start = 1394
    _TRANSFER_STATUS._serialized_end = 1526
    _ONEOFFTRANSFER._serialized_start = 1536
    _ONEOFFTRANSFER._serialized_end = 1583
    _RECURRINGTRANSFER._serialized_start = 1586
    _RECURRINGTRANSFER._serialized_end = 1779
    _STAKELINKING._serialized_start = 1782
    _STAKELINKING._serialized_end = 2346
    _STAKELINKING_TYPE._serialized_start = 2190
    _STAKELINKING_TYPE._serialized_end = 2250
    _STAKELINKING_STATUS._serialized_start = 2252
    _STAKELINKING_STATUS._serialized_end = 2346
    _ERC20MULTISIGSIGNEREVENT._serialized_start = 2349
    _ERC20MULTISIGSIGNEREVENT._serialized_end = 2688
    _ERC20MULTISIGSIGNEREVENT_TYPE._serialized_start = 2626
    _ERC20MULTISIGSIGNEREVENT_TYPE._serialized_end = 2688
    _ERC20MULTISIGTHRESHOLDSETEVENT._serialized_start = 2691
    _ERC20MULTISIGTHRESHOLDSETEVENT._serialized_end = 2918
    _CHECKPOINTEVENT._serialized_start = 2920
    _CHECKPOINTEVENT._serialized_end = 3023
    _STREAMSTARTEVENT._serialized_start = 3025
    _STREAMSTARTEVENT._serialized_end = 3070
    _REWARDPAYOUTEVENT._serialized_start = 3073
    _REWARDPAYOUTEVENT._serialized_end = 3331
    _VALIDATORSCOREEVENT._serialized_start = 3334
    _VALIDATORSCOREEVENT._serialized_end = 3676
    _DELEGATIONBALANCEEVENT._serialized_start = 3678
    _DELEGATIONBALANCEEVENT._serialized_end = 3802
    _MARKETEVENT._serialized_start = 3804
    _MARKETEVENT._serialized_end = 3872
    _TXERROREVENT._serialized_start = 3875
    _TXERROREVENT._serialized_end = 5473
    _TIMEUPDATE._serialized_start = 5475
    _TIMEUPDATE._serialized_end = 5517
    _EPOCHEVENT._serialized_start = 5520
    _EPOCHEVENT._serialized_end = 5684
    _TRANSFERRESPONSES._serialized_start = 5686
    _TRANSFERRESPONSES._serialized_end = 5759
    _POSITIONRESOLUTION._serialized_start = 5762
    _POSITIONRESOLUTION._serialized_end = 5898
    _LOSSSOCIALIZATION._serialized_start = 5900
    _LOSSSOCIALIZATION._serialized_end = 5999
    _TRADESETTLEMENT._serialized_start = 6001
    _TRADESETTLEMENT._serialized_end = 6095
    _SETTLEPOSITION._serialized_start = 6098
    _SETTLEPOSITION._serialized_end = 6311
    _POSITIONSTATEEVENT._serialized_start = 6314
    _POSITIONSTATEEVENT._serialized_end = 6560
    _SETTLEDISTRESSED._serialized_start = 6562
    _SETTLEDISTRESSED._serialized_end = 6682
    _MARKETTICK._serialized_start = 6684
    _MARKETTICK._serialized_end = 6732
    _AUCTIONEVENT._serialized_start = 6735
    _AUCTIONEVENT._serialized_end = 6996
    _VALIDATORUPDATE._serialized_start = 6999
    _VALIDATORUPDATE._serialized_end = 7395
    _VALIDATORRANKINGEVENT._serialized_start = 7398
    _VALIDATORRANKINGEVENT._serialized_end = 7704
    _KEYROTATION._serialized_start = 7707
    _KEYROTATION._serialized_end = 7844
    _ETHEREUMKEYROTATION._serialized_start = 7847
    _ETHEREUMKEYROTATION._serialized_end = 7994
    _PROTOCOLUPGRADEEVENT._serialized_start = 7997
    _PROTOCOLUPGRADEEVENT._serialized_end = 8212
    _STATEVAR._serialized_start = 8214
    _STATEVAR._serialized_end = 8289
    _BUSEVENT._serialized_start = 8292
    _BUSEVENT._serialized_end = 11760
# @@protoc_insertion_point(module_scope)
