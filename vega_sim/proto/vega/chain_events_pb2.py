# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/chain_events.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x17vega/chain_events.proto\x12\x04vega"\xae\x01\n\x14\x45thContractCallEvent\x12\x17\n\x07spec_id\x18\x01 \x01(\tR\x06specId\x12!\n\x0c\x62lock_height\x18\x02 \x01(\x04R\x0b\x62lockHeight\x12\x1d\n\nblock_time\x18\x03 \x01(\x04R\tblockTime\x12\x16\n\x06result\x18\x04 \x01(\x0cR\x06result\x12\x19\n\x05\x65rror\x18\x05 \x01(\tH\x00R\x05\x65rror\x88\x01\x01\x42\x08\n\x06_error"l\n\x13\x42uiltinAssetDeposit\x12"\n\rvega_asset_id\x18\x01 \x01(\tR\x0bvegaAssetId\x12\x19\n\x08party_id\x18\x02 \x01(\tR\x07partyId\x12\x16\n\x06\x61mount\x18\x03 \x01(\tR\x06\x61mount"o\n\x16\x42uiltinAssetWithdrawal\x12"\n\rvega_asset_id\x18\x01 \x01(\tR\x0bvegaAssetId\x12\x19\n\x08party_id\x18\x02 \x01(\tR\x07partyId\x12\x16\n\x06\x61mount\x18\x03 \x01(\tR\x06\x61mount"\x96\x01\n\x11\x42uiltinAssetEvent\x12\x36\n\x07\x64\x65posit\x18\xe9\x07 \x01(\x0b\x32\x19.vega.BuiltinAssetDepositH\x00R\x07\x64\x65posit\x12?\n\nwithdrawal\x18\xea\x07 \x01(\x0b\x32\x1c.vega.BuiltinAssetWithdrawalH\x00R\nwithdrawalB\x08\n\x06\x61\x63tion"W\n\x0e\x45RC20AssetList\x12"\n\rvega_asset_id\x18\x01 \x01(\tR\x0bvegaAssetId\x12!\n\x0c\x61sset_source\x18\x02 \x01(\tR\x0b\x61ssetSource"6\n\x10\x45RC20AssetDelist\x12"\n\rvega_asset_id\x18\x01 \x01(\tR\x0bvegaAssetId"\xcd\x01\n\x17\x45RC20AssetLimitsUpdated\x12"\n\rvega_asset_id\x18\x01 \x01(\tR\x0bvegaAssetId\x12\x36\n\x17source_ethereum_address\x18\x02 \x01(\tR\x15sourceEthereumAddress\x12\'\n\x0flifetime_limits\x18\x03 \x01(\tR\x0elifetimeLimits\x12-\n\x12withdraw_threshold\x18\x04 \x01(\tR\x11withdrawThreshold"\xaa\x01\n\x0c\x45RC20Deposit\x12"\n\rvega_asset_id\x18\x01 \x01(\tR\x0bvegaAssetId\x12\x36\n\x17source_ethereum_address\x18\x02 \x01(\tR\x15sourceEthereumAddress\x12&\n\x0ftarget_party_id\x18\x03 \x01(\tR\rtargetPartyId\x12\x16\n\x06\x61mount\x18\x04 \x01(\tR\x06\x61mount"\x96\x01\n\x0f\x45RC20Withdrawal\x12"\n\rvega_asset_id\x18\x01 \x01(\tR\x0bvegaAssetId\x12\x36\n\x17target_ethereum_address\x18\x02 \x01(\tR\x15targetEthereumAddress\x12\'\n\x0freference_nonce\x18\x03 \x01(\tR\x0ereferenceNonce"\xcb\x03\n\nERC20Event\x12\x14\n\x05index\x18\x01 \x01(\x04R\x05index\x12\x14\n\x05\x62lock\x18\x02 \x01(\x04R\x05\x62lock\x12\x36\n\nasset_list\x18\xe9\x07 \x01(\x0b\x32\x14.vega.ERC20AssetListH\x00R\tassetList\x12<\n\x0c\x61sset_delist\x18\xea\x07 \x01(\x0b\x32\x16.vega.ERC20AssetDelistH\x00R\x0b\x61ssetDelist\x12/\n\x07\x64\x65posit\x18\xeb\x07 \x01(\x0b\x32\x12.vega.ERC20DepositH\x00R\x07\x64\x65posit\x12\x38\n\nwithdrawal\x18\xec\x07 \x01(\x0b\x32\x15.vega.ERC20WithdrawalH\x00R\nwithdrawal\x12R\n\x14\x61sset_limits_updated\x18\xed\x07 \x01(\x0b\x32\x1d.vega.ERC20AssetLimitsUpdatedH\x00R\x12\x61ssetLimitsUpdated\x12(\n\x0e\x62ridge_stopped\x18\xee\x07 \x01(\x08H\x00R\rbridgeStopped\x12(\n\x0e\x62ridge_resumed\x18\xef\x07 \x01(\x08H\x00R\rbridgeResumedB\x08\n\x06\x61\x63tion"f\n\x10\x45RC20SignerAdded\x12\x1d\n\nnew_signer\x18\x01 \x01(\tR\tnewSigner\x12\x14\n\x05nonce\x18\x02 \x01(\tR\x05nonce\x12\x1d\n\nblock_time\x18\x03 \x01(\x03R\tblockTime"h\n\x12\x45RC20SignerRemoved\x12\x1d\n\nold_signer\x18\x01 \x01(\tR\toldSigner\x12\x14\n\x05nonce\x18\x02 \x01(\tR\x05nonce\x12\x1d\n\nblock_time\x18\x03 \x01(\x03R\tblockTime"m\n\x11\x45RC20ThresholdSet\x12#\n\rnew_threshold\x18\x01 \x01(\rR\x0cnewThreshold\x12\x14\n\x05nonce\x18\x02 \x01(\tR\x05nonce\x12\x1d\n\nblock_time\x18\x03 \x01(\x03R\tblockTime"\x8d\x02\n\x12\x45RC20MultiSigEvent\x12\x14\n\x05index\x18\x01 \x01(\x04R\x05index\x12\x14\n\x05\x62lock\x18\x02 \x01(\x04R\x05\x62lock\x12<\n\x0csigner_added\x18\xe9\x07 \x01(\x0b\x32\x16.vega.ERC20SignerAddedH\x00R\x0bsignerAdded\x12\x42\n\x0esigner_removed\x18\xea\x07 \x01(\x0b\x32\x18.vega.ERC20SignerRemovedH\x00R\rsignerRemoved\x12?\n\rthreshold_set\x18\xeb\x07 \x01(\x0b\x32\x17.vega.ERC20ThresholdSetH\x00R\x0cthresholdSetB\x08\n\x06\x61\x63tion"\x80\x02\n\x0cStakingEvent\x12\x14\n\x05index\x18\x01 \x01(\x04R\x05index\x12\x14\n\x05\x62lock\x18\x02 \x01(\x04R\x05\x62lock\x12@\n\x0fstake_deposited\x18\xe9\x07 \x01(\x0b\x32\x14.vega.StakeDepositedH\x00R\x0estakeDeposited\x12:\n\rstake_removed\x18\xea\x07 \x01(\x0b\x32\x12.vega.StakeRemovedH\x00R\x0cstakeRemoved\x12<\n\x0ctotal_supply\x18\xeb\x07 \x01(\x0b\x32\x16.vega.StakeTotalSupplyH\x00R\x0btotalSupplyB\x08\n\x06\x61\x63tion"\x9a\x01\n\x0eStakeDeposited\x12)\n\x10\x65thereum_address\x18\x01 \x01(\tR\x0f\x65thereumAddress\x12&\n\x0fvega_public_key\x18\x02 \x01(\tR\rvegaPublicKey\x12\x16\n\x06\x61mount\x18\x03 \x01(\tR\x06\x61mount\x12\x1d\n\nblock_time\x18\x04 \x01(\x03R\tblockTime"\x98\x01\n\x0cStakeRemoved\x12)\n\x10\x65thereum_address\x18\x01 \x01(\tR\x0f\x65thereumAddress\x12&\n\x0fvega_public_key\x18\x02 \x01(\tR\rvegaPublicKey\x12\x16\n\x06\x61mount\x18\x03 \x01(\tR\x06\x61mount\x12\x1d\n\nblock_time\x18\x04 \x01(\x03R\tblockTime"Z\n\x10StakeTotalSupply\x12#\n\rtoken_address\x18\x01 \x01(\tR\x0ctokenAddress\x12!\n\x0ctotal_supply\x18\x02 \x01(\tR\x0btotalSupplyB\'Z%code.vegaprotocol.io/vega/protos/vegab\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "vega.chain_events_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals[
        "DESCRIPTOR"
    ]._serialized_options = b"Z%code.vegaprotocol.io/vega/protos/vega"
    _globals["_ETHCONTRACTCALLEVENT"]._serialized_start = 34
    _globals["_ETHCONTRACTCALLEVENT"]._serialized_end = 208
    _globals["_BUILTINASSETDEPOSIT"]._serialized_start = 210
    _globals["_BUILTINASSETDEPOSIT"]._serialized_end = 318
    _globals["_BUILTINASSETWITHDRAWAL"]._serialized_start = 320
    _globals["_BUILTINASSETWITHDRAWAL"]._serialized_end = 431
    _globals["_BUILTINASSETEVENT"]._serialized_start = 434
    _globals["_BUILTINASSETEVENT"]._serialized_end = 584
    _globals["_ERC20ASSETLIST"]._serialized_start = 586
    _globals["_ERC20ASSETLIST"]._serialized_end = 673
    _globals["_ERC20ASSETDELIST"]._serialized_start = 675
    _globals["_ERC20ASSETDELIST"]._serialized_end = 729
    _globals["_ERC20ASSETLIMITSUPDATED"]._serialized_start = 732
    _globals["_ERC20ASSETLIMITSUPDATED"]._serialized_end = 937
    _globals["_ERC20DEPOSIT"]._serialized_start = 940
    _globals["_ERC20DEPOSIT"]._serialized_end = 1110
    _globals["_ERC20WITHDRAWAL"]._serialized_start = 1113
    _globals["_ERC20WITHDRAWAL"]._serialized_end = 1263
    _globals["_ERC20EVENT"]._serialized_start = 1266
    _globals["_ERC20EVENT"]._serialized_end = 1725
    _globals["_ERC20SIGNERADDED"]._serialized_start = 1727
    _globals["_ERC20SIGNERADDED"]._serialized_end = 1829
    _globals["_ERC20SIGNERREMOVED"]._serialized_start = 1831
    _globals["_ERC20SIGNERREMOVED"]._serialized_end = 1935
    _globals["_ERC20THRESHOLDSET"]._serialized_start = 1937
    _globals["_ERC20THRESHOLDSET"]._serialized_end = 2046
    _globals["_ERC20MULTISIGEVENT"]._serialized_start = 2049
    _globals["_ERC20MULTISIGEVENT"]._serialized_end = 2318
    _globals["_STAKINGEVENT"]._serialized_start = 2321
    _globals["_STAKINGEVENT"]._serialized_end = 2577
    _globals["_STAKEDEPOSITED"]._serialized_start = 2580
    _globals["_STAKEDEPOSITED"]._serialized_end = 2734
    _globals["_STAKEREMOVED"]._serialized_start = 2737
    _globals["_STAKEREMOVED"]._serialized_end = 2889
    _globals["_STAKETOTALSUPPLY"]._serialized_start = 2891
    _globals["_STAKETOTALSUPPLY"]._serialized_end = 2981
# @@protoc_insertion_point(module_scope)
