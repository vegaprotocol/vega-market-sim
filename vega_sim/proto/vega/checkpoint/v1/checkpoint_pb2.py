# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/checkpoint/v1/checkpoint.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ... import assets_pb2 as vega_dot_assets__pb2
from ... import chain_events_pb2 as vega_dot_chain__events__pb2
from ...events.v1 import events_pb2 as vega_dot_events_dot_v1_dot_events__pb2
from ... import governance_pb2 as vega_dot_governance__pb2
from ... import markets_pb2 as vega_dot_markets__pb2
from ... import vega_pb2 as vega_dot_vega__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n#vega/checkpoint/v1/checkpoint.proto\x12\x12vega.checkpoint.v1\x1a\x11vega/assets.proto\x1a\x17vega/chain_events.proto\x1a\x1bvega/events/v1/events.proto\x1a\x15vega/governance.proto\x1a\x12vega/markets.proto\x1a\x0fvega/vega.proto";\n\x0f\x43heckpointState\x12\x12\n\x04hash\x18\x01 \x01(\x0cR\x04hash\x12\x14\n\x05state\x18\x02 \x01(\x0cR\x05state"\xbd\x03\n\nCheckpoint\x12\x1e\n\ngovernance\x18\x01 \x01(\x0cR\ngovernance\x12\x16\n\x06\x61ssets\x18\x02 \x01(\x0cR\x06\x61ssets\x12\x1e\n\ncollateral\x18\x03 \x01(\x0cR\ncollateral\x12-\n\x12network_parameters\x18\x04 \x01(\x0cR\x11networkParameters\x12\x1e\n\ndelegation\x18\x05 \x01(\x0cR\ndelegation\x12\x14\n\x05\x65poch\x18\x06 \x01(\x0cR\x05\x65poch\x12\x14\n\x05\x62lock\x18\x07 \x01(\x0cR\x05\x62lock\x12\x18\n\x07rewards\x18\x08 \x01(\x0cR\x07rewards\x12\x18\n\x07\x62\x61nking\x18\t \x01(\x0cR\x07\x62\x61nking\x12\x1e\n\nvalidators\x18\n \x01(\x0cR\nvalidators\x12\x18\n\x07staking\x18\x0b \x01(\x0cR\x07staking\x12)\n\x10multisig_control\x18\x0c \x01(\x0cR\x0fmultisigControl\x12%\n\x0emarket_tracker\x18\r \x01(\x0cR\rmarketTracker\x12\x1c\n\texecution\x18\x0e \x01(\x0cR\texecution"U\n\nAssetEntry\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x37\n\rasset_details\x18\x02 \x01(\x0b\x32\x12.vega.AssetDetailsR\x0c\x61ssetDetails"\x96\x01\n\x06\x41ssets\x12\x36\n\x06\x61ssets\x18\x01 \x03(\x0b\x32\x1e.vega.checkpoint.v1.AssetEntryR\x06\x61ssets\x12T\n\x16pending_listing_assets\x18\x02 \x03(\x0b\x32\x1e.vega.checkpoint.v1.AssetEntryR\x14pendingListingAssets"T\n\x0c\x41ssetBalance\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x14\n\x05\x61sset\x18\x02 \x01(\tR\x05\x61sset\x12\x18\n\x07\x62\x61lance\x18\x03 \x01(\tR\x07\x62\x61lance"J\n\nCollateral\x12<\n\x08\x62\x61lances\x18\x01 \x03(\x0b\x32 .vega.checkpoint.v1.AssetBalanceR\x08\x62\x61lances";\n\tNetParams\x12.\n\x06params\x18\x01 \x03(\x0b\x32\x16.vega.NetworkParameterR\x06params"9\n\tProposals\x12,\n\tproposals\x18\x01 \x03(\x0b\x32\x0e.vega.ProposalR\tproposals"\x8e\x01\n\rDelegateEntry\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x12\n\x04node\x18\x02 \x01(\tR\x04node\x12\x16\n\x06\x61mount\x18\x03 \x01(\tR\x06\x61mount\x12\x1e\n\nundelegate\x18\x04 \x01(\x08R\nundelegate\x12\x1b\n\tepoch_seq\x18\x05 \x01(\x04R\x08\x65pochSeq"\xab\x01\n\x08\x44\x65legate\x12\x39\n\x06\x61\x63tive\x18\x01 \x03(\x0b\x32!.vega.checkpoint.v1.DelegateEntryR\x06\x61\x63tive\x12;\n\x07pending\x18\x02 \x03(\x0b\x32!.vega.checkpoint.v1.DelegateEntryR\x07pending\x12\'\n\x0f\x61uto_delegation\x18\x03 \x03(\tR\x0e\x61utoDelegation"\x1f\n\x05\x42lock\x12\x16\n\x06height\x18\x01 \x01(\x03R\x06height"E\n\x07Rewards\x12:\n\x07rewards\x18\x01 \x03(\x0b\x32 .vega.checkpoint.v1.RewardPayoutR\x07rewards"\x7f\n\x0cRewardPayout\x12\x1f\n\x0bpayout_time\x18\x01 \x01(\x03R\npayoutTime\x12N\n\x0erewards_payout\x18\x02 \x03(\x0b\x32\'.vega.checkpoint.v1.PendingRewardPayoutR\rrewardsPayout"\xf0\x01\n\x13PendingRewardPayout\x12!\n\x0c\x66rom_account\x18\x01 \x01(\tR\x0b\x66romAccount\x12\x14\n\x05\x61sset\x18\x02 \x01(\tR\x05\x61sset\x12\x42\n\x0cparty_amount\x18\x03 \x03(\x0b\x32\x1f.vega.checkpoint.v1.PartyAmountR\x0bpartyAmount\x12!\n\x0ctotal_reward\x18\x04 \x01(\tR\x0btotalReward\x12\x1b\n\tepoch_seq\x18\x05 \x01(\tR\x08\x65pochSeq\x12\x1c\n\ttimestamp\x18\x06 \x01(\x03R\ttimestamp";\n\x0bPartyAmount\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x16\n\x06\x61mount\x18\x02 \x01(\tR\x06\x61mount"\xb9\x01\n\x12PendingKeyRotation\x12?\n\x1crelative_target_block_height\x18\x01 \x01(\x04R\x19relativeTargetBlockHeight\x12\x17\n\x07node_id\x18\x02 \x01(\tR\x06nodeId\x12\x1e\n\x0bnew_pub_key\x18\x03 \x01(\tR\tnewPubKey\x12)\n\x11new_pub_key_index\x18\x04 \x01(\rR\x0enewPubKeyIndex"\x97\x01\n\x1aPendingEthereumKeyRotation\x12?\n\x1crelative_target_block_height\x18\x01 \x01(\x04R\x19relativeTargetBlockHeight\x12\x17\n\x07node_id\x18\x02 \x01(\tR\x06nodeId\x12\x1f\n\x0bnew_address\x18\x03 \x01(\tR\nnewAddress"\xd6\x01\n\x11ScheduledTransfer\x12*\n\x08transfer\x18\x01 \x01(\x0b\x32\x0e.vega.TransferR\x08transfer\x12\x34\n\x0c\x61\x63\x63ount_type\x18\x02 \x01(\x0e\x32\x11.vega.AccountTypeR\x0b\x61\x63\x63ountType\x12\x1c\n\treference\x18\x03 \x01(\tR\treference\x12\x41\n\x0foneoff_transfer\x18\x04 \x01(\x0b\x32\x18.vega.events.v1.TransferR\x0eoneoffTransfer"}\n\x17ScheduledTransferAtTime\x12\x1d\n\ndeliver_on\x18\x01 \x01(\x03R\tdeliverOn\x12\x43\n\ttransfers\x18\x02 \x03(\x0b\x32%.vega.checkpoint.v1.ScheduledTransferR\ttransfers"_\n\x12RecurringTransfers\x12I\n\x13recurring_transfers\x18\x01 \x03(\x0b\x32\x18.vega.events.v1.TransferR\x12recurringTransfers"\xd1\x01\n\x12GovernanceTransfer\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x1c\n\treference\x18\x02 \x01(\tR\treference\x12\x37\n\x06status\x18\x03 \x01(\x0e\x32\x1f.vega.events.v1.Transfer.StatusR\x06status\x12\x1c\n\ttimestamp\x18\x04 \x01(\x03R\ttimestamp\x12\x36\n\x06\x63onfig\x18\x05 \x01(\x0b\x32\x1e.vega.NewTransferConfigurationR\x06\x63onfig"\x88\x01\n!ScheduledGovernanceTransferAtTime\x12\x1d\n\ndeliver_on\x18\x01 \x01(\x03R\tdeliverOn\x12\x44\n\ttransfers\x18\x02 \x03(\x0b\x32&.vega.checkpoint.v1.GovernanceTransferR\ttransfers"\xae\x06\n\x07\x42\x61nking\x12W\n\x11transfers_at_time\x18\x01 \x03(\x0b\x32+.vega.checkpoint.v1.ScheduledTransferAtTimeR\x0ftransfersAtTime\x12W\n\x13recurring_transfers\x18\x02 \x01(\x0b\x32&.vega.checkpoint.v1.RecurringTransfersR\x12recurringTransfers\x12Q\n\x14primary_bridge_state\x18\x03 \x01(\x0b\x32\x1f.vega.checkpoint.v1.BridgeStateR\x12primaryBridgeState\x12\x44\n\rasset_actions\x18\x04 \x03(\x0b\x32\x1f.vega.checkpoint.v1.AssetActionR\x0c\x61ssetActions\x12<\n\x1blast_seen_primary_eth_block\x18\x05 \x01(\x04R\x17lastSeenPrimaryEthBlock\x12\x1b\n\tseen_refs\x18\x06 \x03(\tR\x08seenRefs\x12v\n\x1cgovernance_transfers_at_time\x18\x07 \x03(\x0b\x32\x35.vega.checkpoint.v1.ScheduledGovernanceTransferAtTimeR\x19governanceTransfersAtTime\x12l\n\x1erecurring_governance_transfers\x18\x08 \x03(\x0b\x32&.vega.checkpoint.v1.GovernanceTransferR\x1crecurringGovernanceTransfers\x12U\n\x16secondary_bridge_state\x18\t \x01(\x0b\x32\x1f.vega.checkpoint.v1.BridgeStateR\x14secondaryBridgeState\x12@\n\x1dlast_seen_secondary_eth_block\x18\n \x01(\x04R\x19lastSeenSecondaryEthBlock"e\n\x0b\x42ridgeState\x12\x16\n\x06\x61\x63tive\x18\x01 \x01(\x08R\x06\x61\x63tive\x12!\n\x0c\x62lock_height\x18\x02 \x01(\x04R\x0b\x62lockHeight\x12\x1b\n\tlog_index\x18\x03 \x01(\x04R\x08logIndex"\xaa\x02\n\nValidators\x12K\n\x0fvalidator_state\x18\x01 \x03(\x0b\x32".vega.checkpoint.v1.ValidatorStateR\x0evalidatorState\x12Z\n\x15pending_key_rotations\x18\x02 \x03(\x0b\x32&.vega.checkpoint.v1.PendingKeyRotationR\x13pendingKeyRotations\x12s\n\x1epending_ethereum_key_rotations\x18\x03 \x03(\x0b\x32..vega.checkpoint.v1.PendingEthereumKeyRotationR\x1bpendingEthereumKeyRotations"\xee\x02\n\x0eValidatorState\x12J\n\x10validator_update\x18\x01 \x01(\x0b\x32\x1f.vega.events.v1.ValidatorUpdateR\x0fvalidatorUpdate\x12\x16\n\x06status\x18\x02 \x01(\x05R\x06status\x12\x30\n\x14\x65th_events_forwarded\x18\x03 \x01(\x04R\x12\x65thEventsForwarded\x12\'\n\x0fvalidator_power\x18\x04 \x01(\x03R\x0evalidatorPower\x12\x37\n\rranking_score\x18\x05 \x01(\x0b\x32\x12.vega.RankingScoreR\x0crankingScore\x12\x32\n\x15heartbeat_block_index\x18\x06 \x01(\x05R\x13heartbeatBlockIndex\x12\x30\n\x14heartbeat_block_sigs\x18\x07 \x03(\x08R\x12heartbeatBlockSigs"k\n\x07Staking\x12\x38\n\x08\x61\x63\x63\x65pted\x18\x01 \x03(\x0b\x32\x1c.vega.events.v1.StakeLinkingR\x08\x61\x63\x63\x65pted\x12&\n\x0flast_block_seen\x18\x02 \x01(\x04R\rlastBlockSeen"\xd2\x01\n\x0fMultisigControl\x12\x42\n\x07signers\x18\x01 \x03(\x0b\x32(.vega.events.v1.ERC20MultiSigSignerEventR\x07signers\x12S\n\rthreshold_set\x18\x02 \x01(\x0b\x32..vega.events.v1.ERC20MultiSigThresholdSetEventR\x0cthresholdSet\x12&\n\x0flast_block_seen\x18\x03 \x01(\x04R\rlastBlockSeen"\xc8\x02\n\rMarketTracker\x12R\n\x0fmarket_activity\x18\x01 \x03(\x0b\x32).vega.checkpoint.v1.MarketActivityTrackerR\x0emarketActivity\x12[\n\x15taker_notional_volume\x18\x02 \x03(\x0b\x32\'.vega.checkpoint.v1.TakerNotionalVolumeR\x13takerNotionalVolume\x12\x85\x01\n%market_to_party_taker_notional_volume\x18\x03 \x03(\x0b\x32\x34.vega.checkpoint.v1.MarketToPartyTakerNotionalVolumeR marketToPartyTakerNotionalVolume"\xf3\t\n\x15MarketActivityTracker\x12\x16\n\x06market\x18\x01 \x01(\tR\x06market\x12\x14\n\x05\x61sset\x18\x02 \x01(\tR\x05\x61sset\x12M\n\x13maker_fees_received\x18\x03 \x03(\x0b\x32\x1d.vega.checkpoint.v1.PartyFeesR\x11makerFeesReceived\x12\x45\n\x0fmaker_fees_paid\x18\x04 \x03(\x0b\x32\x1d.vega.checkpoint.v1.PartyFeesR\rmakerFeesPaid\x12\x36\n\x07lp_fees\x18\x05 \x03(\x0b\x32\x1d.vega.checkpoint.v1.PartyFeesR\x06lpFees\x12\x1a\n\x08proposer\x18\x06 \x01(\tR\x08proposer\x12\x1d\n\nbonus_paid\x18\x07 \x03(\tR\tbonusPaid\x12!\n\x0cvalue_traded\x18\x08 \x01(\tR\x0bvalueTraded\x12&\n\x0fready_to_delete\x18\t \x01(\x08R\rreadyToDelete\x12X\n\x16time_weighted_position\x18\n \x03(\x0b\x32".vega.checkpoint.v1.TWPositionDataR\x14timeWeightedPosition\x12X\n\x16time_weighted_notional\x18\x0b \x03(\x0b\x32".vega.checkpoint.v1.TWNotionalDataR\x14timeWeightedNotional\x12\x42\n\x0creturns_data\x18\x0c \x03(\x0b\x32\x1f.vega.checkpoint.v1.ReturnsDataR\x0breturnsData\x12\x61\n\x1bmaker_fees_received_history\x18\r \x03(\x0b\x32".vega.checkpoint.v1.EpochPartyFeesR\x18makerFeesReceivedHistory\x12Y\n\x17maker_fees_paid_history\x18\x0e \x03(\x0b\x32".vega.checkpoint.v1.EpochPartyFeesR\x14makerFeesPaidHistory\x12J\n\x0flp_fees_history\x18\x0f \x03(\x0b\x32".vega.checkpoint.v1.EpochPartyFeesR\rlpFeesHistory\x12}\n#time_weighted_position_data_history\x18\x10 \x03(\x0b\x32/.vega.checkpoint.v1.EpochTimeWeightPositionDataR\x1ftimeWeightedPositionDataHistory\x12\x7f\n#time_weighted_notional_data_history\x18\x11 \x03(\x0b\x32\x31.vega.checkpoint.v1.EpochTimeWeightedNotionalDataR\x1ftimeWeightedNotionalDataHistory\x12V\n\x14returns_data_history\x18\x12 \x03(\x0b\x32$.vega.checkpoint.v1.EpochReturnsDataR\x12returnsDataHistory"\x8f\x01\n\x1b\x45pochTimeWeightPositionData\x12p\n\x1dparty_time_weighted_positions\x18\x01 \x03(\x0b\x32-.vega.checkpoint.v1.PartyTimeWeightedPositionR\x1apartyTimeWeightedPositions"\x91\x01\n\x1d\x45pochTimeWeightedNotionalData\x12p\n\x1dparty_time_weighted_notionals\x18\x01 \x03(\x0b\x32-.vega.checkpoint.v1.PartyTimeWeightedNotionalR\x1apartyTimeWeightedNotionals"R\n\x19PartyTimeWeightedNotional\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x1f\n\x0btw_notional\x18\x02 \x01(\x0cR\ntwNotional"R\n\x19PartyTimeWeightedPosition\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x1f\n\x0btw_position\x18\x02 \x01(\x04R\ntwPosition"U\n\x0e\x45pochPartyFees\x12\x43\n\nparty_fees\x18\x01 \x03(\x0b\x32$.vega.checkpoint.v1.PartyFeesHistoryR\tpartyFees"C\n\x13TakerNotionalVolume\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x16\n\x06volume\x18\x02 \x01(\x0cR\x06volume"\x97\x01\n MarketToPartyTakerNotionalVolume\x12\x16\n\x06market\x18\x01 \x01(\tR\x06market\x12[\n\x15taker_notional_volume\x18\x02 \x03(\x0b\x32\'.vega.checkpoint.v1.TakerNotionalVolumeR\x13takerNotionalVolume"M\n\x10\x45pochReturnsData\x12\x39\n\x07returns\x18\x01 \x03(\x0b\x32\x1f.vega.checkpoint.v1.ReturnsDataR\x07returns";\n\x0bReturnsData\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x16\n\x06return\x18\x02 \x01(\x0cR\x06return"w\n\x0eTWPositionData\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x1a\n\x08position\x18\x02 \x01(\x04R\x08position\x12\x12\n\x04time\x18\x03 \x01(\x03R\x04time\x12\x1f\n\x0btw_position\x18\x04 \x01(\x04R\ntwPosition"w\n\x0eTWNotionalData\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x1a\n\x08notional\x18\x02 \x01(\x0cR\x08notional\x12\x12\n\x04time\x18\x03 \x01(\x03R\x04time\x12\x1f\n\x0btw_notional\x18\x04 \x01(\x0cR\ntwNotional"3\n\tPartyFees\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x10\n\x03\x66\x65\x65\x18\x02 \x01(\tR\x03\x66\x65\x65":\n\x10PartyFeesHistory\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x10\n\x03\x66\x65\x65\x18\x02 \x01(\x0cR\x03\x66\x65\x65"\xa8\x04\n\x0b\x41ssetAction\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x14\n\x05state\x18\x02 \x01(\rR\x05state\x12\x14\n\x05\x61sset\x18\x03 \x01(\tR\x05\x61sset\x12!\n\x0c\x62lock_number\x18\x04 \x01(\x04R\x0b\x62lockNumber\x12\x19\n\x08tx_index\x18\x05 \x01(\x04R\x07txIndex\x12\x12\n\x04hash\x18\x06 \x01(\tR\x04hash\x12\x42\n\x0f\x62uiltin_deposit\x18\x07 \x01(\x0b\x32\x19.vega.BuiltinAssetDepositR\x0e\x62uiltinDeposit\x12\x37\n\rerc20_deposit\x18\x08 \x01(\x0b\x32\x12.vega.ERC20DepositR\x0c\x65rc20Deposit\x12\x33\n\nasset_list\x18\t \x01(\x0b\x32\x14.vega.ERC20AssetListR\tassetList\x12Z\n\x1a\x65rc20_asset_limits_updated\x18\n \x01(\x0b\x32\x1d.vega.ERC20AssetLimitsUpdatedR\x17\x65rc20AssetLimitsUpdated\x12\x30\n\x14\x65rc20_bridge_stopped\x18\x0b \x01(\x08R\x12\x65rc20BridgeStopped\x12\x30\n\x14\x65rc20_bridge_resumed\x18\x0c \x01(\x08R\x12\x65rc20BridgeResumed\x12\x19\n\x08\x63hain_id\x18\r \x01(\tR\x07\x63hainId"\x99\x01\n\x08\x45LSShare\x12\x19\n\x08party_id\x18\x01 \x01(\tR\x07partyId\x12\x14\n\x05share\x18\x02 \x01(\tR\x05share\x12%\n\x0esupplied_stake\x18\x03 \x01(\tR\rsuppliedStake\x12#\n\rvirtual_stake\x18\x04 \x01(\tR\x0cvirtualStake\x12\x10\n\x03\x61vg\x18\x05 \x01(\tR\x03\x61vg"\xa9\x02\n\x0bMarketState\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x34\n\x06shares\x18\x02 \x03(\x0b\x32\x1c.vega.checkpoint.v1.ELSShareR\x06shares\x12+\n\x11insurance_balance\x18\x03 \x01(\tR\x10insuranceBalance\x12(\n\x10last_trade_value\x18\x04 \x01(\tR\x0elastTradeValue\x12*\n\x11last_trade_volume\x18\x05 \x01(\tR\x0flastTradeVolume\x12+\n\x11succession_window\x18\x06 \x01(\x03R\x10successionWindow\x12$\n\x06market\x18\x07 \x01(\x0b\x32\x0c.vega.MarketR\x06market"E\n\x0e\x45xecutionState\x12\x33\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x1f.vega.checkpoint.v1.MarketStateR\x04\x64\x61taB5Z3code.vegaprotocol.io/vega/protos/vega/checkpoint/v1b\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "vega.checkpoint.v1.checkpoint_pb2", _globals
)
if not _descriptor._USE_C_DESCRIPTORS:
    _globals["DESCRIPTOR"]._loaded_options = None
    _globals["DESCRIPTOR"]._serialized_options = (
        b"Z3code.vegaprotocol.io/vega/protos/vega/checkpoint/v1"
    )
    _globals["_CHECKPOINTSTATE"]._serialized_start = 192
    _globals["_CHECKPOINTSTATE"]._serialized_end = 251
    _globals["_CHECKPOINT"]._serialized_start = 254
    _globals["_CHECKPOINT"]._serialized_end = 699
    _globals["_ASSETENTRY"]._serialized_start = 701
    _globals["_ASSETENTRY"]._serialized_end = 786
    _globals["_ASSETS"]._serialized_start = 789
    _globals["_ASSETS"]._serialized_end = 939
    _globals["_ASSETBALANCE"]._serialized_start = 941
    _globals["_ASSETBALANCE"]._serialized_end = 1025
    _globals["_COLLATERAL"]._serialized_start = 1027
    _globals["_COLLATERAL"]._serialized_end = 1101
    _globals["_NETPARAMS"]._serialized_start = 1103
    _globals["_NETPARAMS"]._serialized_end = 1162
    _globals["_PROPOSALS"]._serialized_start = 1164
    _globals["_PROPOSALS"]._serialized_end = 1221
    _globals["_DELEGATEENTRY"]._serialized_start = 1224
    _globals["_DELEGATEENTRY"]._serialized_end = 1366
    _globals["_DELEGATE"]._serialized_start = 1369
    _globals["_DELEGATE"]._serialized_end = 1540
    _globals["_BLOCK"]._serialized_start = 1542
    _globals["_BLOCK"]._serialized_end = 1573
    _globals["_REWARDS"]._serialized_start = 1575
    _globals["_REWARDS"]._serialized_end = 1644
    _globals["_REWARDPAYOUT"]._serialized_start = 1646
    _globals["_REWARDPAYOUT"]._serialized_end = 1773
    _globals["_PENDINGREWARDPAYOUT"]._serialized_start = 1776
    _globals["_PENDINGREWARDPAYOUT"]._serialized_end = 2016
    _globals["_PARTYAMOUNT"]._serialized_start = 2018
    _globals["_PARTYAMOUNT"]._serialized_end = 2077
    _globals["_PENDINGKEYROTATION"]._serialized_start = 2080
    _globals["_PENDINGKEYROTATION"]._serialized_end = 2265
    _globals["_PENDINGETHEREUMKEYROTATION"]._serialized_start = 2268
    _globals["_PENDINGETHEREUMKEYROTATION"]._serialized_end = 2419
    _globals["_SCHEDULEDTRANSFER"]._serialized_start = 2422
    _globals["_SCHEDULEDTRANSFER"]._serialized_end = 2636
    _globals["_SCHEDULEDTRANSFERATTIME"]._serialized_start = 2638
    _globals["_SCHEDULEDTRANSFERATTIME"]._serialized_end = 2763
    _globals["_RECURRINGTRANSFERS"]._serialized_start = 2765
    _globals["_RECURRINGTRANSFERS"]._serialized_end = 2860
    _globals["_GOVERNANCETRANSFER"]._serialized_start = 2863
    _globals["_GOVERNANCETRANSFER"]._serialized_end = 3072
    _globals["_SCHEDULEDGOVERNANCETRANSFERATTIME"]._serialized_start = 3075
    _globals["_SCHEDULEDGOVERNANCETRANSFERATTIME"]._serialized_end = 3211
    _globals["_BANKING"]._serialized_start = 3214
    _globals["_BANKING"]._serialized_end = 4028
    _globals["_BRIDGESTATE"]._serialized_start = 4030
    _globals["_BRIDGESTATE"]._serialized_end = 4131
    _globals["_VALIDATORS"]._serialized_start = 4134
    _globals["_VALIDATORS"]._serialized_end = 4432
    _globals["_VALIDATORSTATE"]._serialized_start = 4435
    _globals["_VALIDATORSTATE"]._serialized_end = 4801
    _globals["_STAKING"]._serialized_start = 4803
    _globals["_STAKING"]._serialized_end = 4910
    _globals["_MULTISIGCONTROL"]._serialized_start = 4913
    _globals["_MULTISIGCONTROL"]._serialized_end = 5123
    _globals["_MARKETTRACKER"]._serialized_start = 5126
    _globals["_MARKETTRACKER"]._serialized_end = 5454
    _globals["_MARKETACTIVITYTRACKER"]._serialized_start = 5457
    _globals["_MARKETACTIVITYTRACKER"]._serialized_end = 6724
    _globals["_EPOCHTIMEWEIGHTPOSITIONDATA"]._serialized_start = 6727
    _globals["_EPOCHTIMEWEIGHTPOSITIONDATA"]._serialized_end = 6870
    _globals["_EPOCHTIMEWEIGHTEDNOTIONALDATA"]._serialized_start = 6873
    _globals["_EPOCHTIMEWEIGHTEDNOTIONALDATA"]._serialized_end = 7018
    _globals["_PARTYTIMEWEIGHTEDNOTIONAL"]._serialized_start = 7020
    _globals["_PARTYTIMEWEIGHTEDNOTIONAL"]._serialized_end = 7102
    _globals["_PARTYTIMEWEIGHTEDPOSITION"]._serialized_start = 7104
    _globals["_PARTYTIMEWEIGHTEDPOSITION"]._serialized_end = 7186
    _globals["_EPOCHPARTYFEES"]._serialized_start = 7188
    _globals["_EPOCHPARTYFEES"]._serialized_end = 7273
    _globals["_TAKERNOTIONALVOLUME"]._serialized_start = 7275
    _globals["_TAKERNOTIONALVOLUME"]._serialized_end = 7342
    _globals["_MARKETTOPARTYTAKERNOTIONALVOLUME"]._serialized_start = 7345
    _globals["_MARKETTOPARTYTAKERNOTIONALVOLUME"]._serialized_end = 7496
    _globals["_EPOCHRETURNSDATA"]._serialized_start = 7498
    _globals["_EPOCHRETURNSDATA"]._serialized_end = 7575
    _globals["_RETURNSDATA"]._serialized_start = 7577
    _globals["_RETURNSDATA"]._serialized_end = 7636
    _globals["_TWPOSITIONDATA"]._serialized_start = 7638
    _globals["_TWPOSITIONDATA"]._serialized_end = 7757
    _globals["_TWNOTIONALDATA"]._serialized_start = 7759
    _globals["_TWNOTIONALDATA"]._serialized_end = 7878
    _globals["_PARTYFEES"]._serialized_start = 7880
    _globals["_PARTYFEES"]._serialized_end = 7931
    _globals["_PARTYFEESHISTORY"]._serialized_start = 7933
    _globals["_PARTYFEESHISTORY"]._serialized_end = 7991
    _globals["_ASSETACTION"]._serialized_start = 7994
    _globals["_ASSETACTION"]._serialized_end = 8546
    _globals["_ELSSHARE"]._serialized_start = 8549
    _globals["_ELSSHARE"]._serialized_end = 8702
    _globals["_MARKETSTATE"]._serialized_start = 8705
    _globals["_MARKETSTATE"]._serialized_end = 9002
    _globals["_EXECUTIONSTATE"]._serialized_start = 9004
    _globals["_EXECUTIONSTATE"]._serialized_end = 9073
# @@protoc_insertion_point(module_scope)
