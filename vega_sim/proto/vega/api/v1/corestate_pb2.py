# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/api/v1/corestate.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from protoc_gen_openapiv2.options import (
    annotations_pb2 as protoc__gen__openapiv2_dot_options_dot_annotations__pb2,
)
from ... import assets_pb2 as vega_dot_assets__pb2
from ...events.v1 import events_pb2 as vega_dot_events_dot_v1_dot_events__pb2
from ... import governance_pb2 as vega_dot_governance__pb2
from ... import markets_pb2 as vega_dot_markets__pb2
from ... import vega_pb2 as vega_dot_vega__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1bvega/api/v1/corestate.proto\x12\x0bvega.api.v1\x1a.protoc-gen-openapiv2/options/annotations.proto\x1a\x11vega/assets.proto\x1a\x1bvega/events/v1/events.proto\x1a\x15vega/governance.proto\x1a\x12vega/markets.proto\x1a\x0fvega/vega.proto"{\n\x07\x41\x63\x63ount\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x16\n\x06market\x18\x02 \x01(\tR\x06market\x12\x18\n\x07\x62\x61lance\x18\x03 \x01(\tR\x07\x62\x61lance\x12\x14\n\x05\x61sset\x18\x05 \x01(\tR\x05\x61sset\x12\x12\n\x04type\x18\x06 \x01(\tR\x04type"C\n\x13ListAccountsRequest\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x16\n\x06market\x18\x02 \x01(\tR\x06market"H\n\x14ListAccountsResponse\x12\x30\n\x08\x61\x63\x63ounts\x18\x01 \x03(\x0b\x32\x14.vega.api.v1.AccountR\x08\x61\x63\x63ounts")\n\x11ListAssetsRequest\x12\x14\n\x05\x61sset\x18\x01 \x01(\tR\x05\x61sset"9\n\x12ListAssetsResponse\x12#\n\x06\x61ssets\x18\x01 \x03(\x0b\x32\x0b.vega.AssetR\x06\x61ssets"R\n\x1cListNetworkParametersRequest\x12\x32\n\x15network_parameter_key\x18\x01 \x01(\tR\x13networkParameterKey"f\n\x1dListNetworkParametersResponse\x12\x45\n\x12network_parameters\x18\x01 \x03(\x0b\x32\x16.vega.NetworkParameterR\x11networkParameters"\x1a\n\x18ListNetworkLimitsRequest"W\n\x19ListNetworkLimitsResponse\x12:\n\x0enetwork_limits\x18\x01 \x01(\x0b\x32\x13.vega.NetworkLimitsR\rnetworkLimits"\x14\n\x12ListPartiesRequest"<\n\x13ListPartiesResponse\x12%\n\x07parties\x18\x01 \x03(\x0b\x32\x0b.vega.PartyR\x07parties"\x17\n\x15ListValidatorsRequest"Y\n\x16ListValidatorsResponse\x12?\n\nvalidators\x18\x01 \x03(\x0b\x32\x1f.vega.events.v1.ValidatorUpdateR\nvalidators",\n\x12ListMarketsRequest\x12\x16\n\x06market\x18\x01 \x01(\tR\x06market"=\n\x13ListMarketsResponse\x12&\n\x07markets\x18\x01 \x03(\x0b\x32\x0c.vega.MarketR\x07markets"N\n\x14ListProposalsRequest\x12\x1a\n\x08proposal\x18\x01 \x01(\tR\x08proposal\x12\x1a\n\x08proposer\x18\x02 \x01(\tR\x08proposer"E\n\x15ListProposalsResponse\x12,\n\tproposals\x18\x01 \x03(\x0b\x32\x0e.vega.ProposalR\tproposals"0\n\x16ListMarketsDataRequest\x12\x16\n\x06market\x18\x01 \x01(\tR\x06market"N\n\x17ListMarketsDataResponse\x12\x33\n\x0cmarkets_data\x18\x01 \x03(\x0b\x32\x10.vega.MarketDataR\x0bmarketsData"D\n\x10ListVotesRequest\x12\x1a\n\x08proposal\x18\x01 \x01(\tR\x08proposal\x12\x14\n\x05party\x18\x02 \x01(\tR\x05party"5\n\x11ListVotesResponse\x12 \n\x05votes\x18\x01 \x03(\x0b\x32\n.vega.VoteR\x05votes"\x9f\x01\n\nPartyStake\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x36\n\x17\x63urrent_stake_available\x18\x02 \x01(\tR\x15\x63urrentStakeAvailable\x12\x43\n\x0estake_linkings\x18\x03 \x03(\x0b\x32\x1c.vega.events.v1.StakeLinkingR\rstakeLinkings"/\n\x17ListPartiesStakeRequest\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party"X\n\x18ListPartiesStakeResponse\x12<\n\rparties_stake\x18\x01 \x03(\x0b\x32\x17.vega.api.v1.PartyStakeR\x0cpartiesStake"_\n\x16ListDelegationsRequest\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x12\n\x04node\x18\x02 \x01(\tR\x04node\x12\x1b\n\tepoch_seq\x18\x03 \x01(\tR\x08\x65pochSeq"M\n\x17ListDelegationsResponse\x12\x32\n\x0b\x64\x65legations\x18\x01 \x03(\x0b\x32\x10.vega.DelegationR\x0b\x64\x65legations2\xca\x08\n\x10\x43oreStateService\x12S\n\x0cListAccounts\x12 .vega.api.v1.ListAccountsRequest\x1a!.vega.api.v1.ListAccountsResponse\x12M\n\nListAssets\x12\x1e.vega.api.v1.ListAssetsRequest\x1a\x1f.vega.api.v1.ListAssetsResponse\x12n\n\x15ListNetworkParameters\x12).vega.api.v1.ListNetworkParametersRequest\x1a*.vega.api.v1.ListNetworkParametersResponse\x12\x62\n\x11ListNetworkLimits\x12%.vega.api.v1.ListNetworkLimitsRequest\x1a&.vega.api.v1.ListNetworkLimitsResponse\x12P\n\x0bListParties\x12\x1f.vega.api.v1.ListPartiesRequest\x1a .vega.api.v1.ListPartiesResponse\x12Y\n\x0eListValidators\x12".vega.api.v1.ListValidatorsRequest\x1a#.vega.api.v1.ListValidatorsResponse\x12P\n\x0bListMarkets\x12\x1f.vega.api.v1.ListMarketsRequest\x1a .vega.api.v1.ListMarketsResponse\x12V\n\rListProposals\x12!.vega.api.v1.ListProposalsRequest\x1a".vega.api.v1.ListProposalsResponse\x12\\\n\x0fListMarketsData\x12#.vega.api.v1.ListMarketsDataRequest\x1a$.vega.api.v1.ListMarketsDataResponse\x12J\n\tListVotes\x12\x1d.vega.api.v1.ListVotesRequest\x1a\x1e.vega.api.v1.ListVotesResponse\x12_\n\x10ListPartiesStake\x12$.vega.api.v1.ListPartiesStakeRequest\x1a%.vega.api.v1.ListPartiesStakeResponse\x12\\\n\x0fListDelegations\x12#.vega.api.v1.ListDelegationsRequest\x1a$.vega.api.v1.ListDelegationsResponseBlZ,code.vegaprotocol.io/vega/protos/vega/api/v1\x92\x41;\x12 \n\x14Vega core state APIs2\x08v0.74.10\x1a\x13lb.testnet.vega.xyz*\x02\x01\x02\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "vega.api.v1.corestate_pb2", _globals
)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals["DESCRIPTOR"]._serialized_options = (
        b"Z,code.vegaprotocol.io/vega/protos/vega/api/v1\222A;\022 \n\024Vega core state APIs2\010v0.74.10\032\023lb.testnet.vega.xyz*\002\001\002"
    )
    _globals["_ACCOUNT"]._serialized_start = 200
    _globals["_ACCOUNT"]._serialized_end = 323
    _globals["_LISTACCOUNTSREQUEST"]._serialized_start = 325
    _globals["_LISTACCOUNTSREQUEST"]._serialized_end = 392
    _globals["_LISTACCOUNTSRESPONSE"]._serialized_start = 394
    _globals["_LISTACCOUNTSRESPONSE"]._serialized_end = 466
    _globals["_LISTASSETSREQUEST"]._serialized_start = 468
    _globals["_LISTASSETSREQUEST"]._serialized_end = 509
    _globals["_LISTASSETSRESPONSE"]._serialized_start = 511
    _globals["_LISTASSETSRESPONSE"]._serialized_end = 568
    _globals["_LISTNETWORKPARAMETERSREQUEST"]._serialized_start = 570
    _globals["_LISTNETWORKPARAMETERSREQUEST"]._serialized_end = 652
    _globals["_LISTNETWORKPARAMETERSRESPONSE"]._serialized_start = 654
    _globals["_LISTNETWORKPARAMETERSRESPONSE"]._serialized_end = 756
    _globals["_LISTNETWORKLIMITSREQUEST"]._serialized_start = 758
    _globals["_LISTNETWORKLIMITSREQUEST"]._serialized_end = 784
    _globals["_LISTNETWORKLIMITSRESPONSE"]._serialized_start = 786
    _globals["_LISTNETWORKLIMITSRESPONSE"]._serialized_end = 873
    _globals["_LISTPARTIESREQUEST"]._serialized_start = 875
    _globals["_LISTPARTIESREQUEST"]._serialized_end = 895
    _globals["_LISTPARTIESRESPONSE"]._serialized_start = 897
    _globals["_LISTPARTIESRESPONSE"]._serialized_end = 957
    _globals["_LISTVALIDATORSREQUEST"]._serialized_start = 959
    _globals["_LISTVALIDATORSREQUEST"]._serialized_end = 982
    _globals["_LISTVALIDATORSRESPONSE"]._serialized_start = 984
    _globals["_LISTVALIDATORSRESPONSE"]._serialized_end = 1073
    _globals["_LISTMARKETSREQUEST"]._serialized_start = 1075
    _globals["_LISTMARKETSREQUEST"]._serialized_end = 1119
    _globals["_LISTMARKETSRESPONSE"]._serialized_start = 1121
    _globals["_LISTMARKETSRESPONSE"]._serialized_end = 1182
    _globals["_LISTPROPOSALSREQUEST"]._serialized_start = 1184
    _globals["_LISTPROPOSALSREQUEST"]._serialized_end = 1262
    _globals["_LISTPROPOSALSRESPONSE"]._serialized_start = 1264
    _globals["_LISTPROPOSALSRESPONSE"]._serialized_end = 1333
    _globals["_LISTMARKETSDATAREQUEST"]._serialized_start = 1335
    _globals["_LISTMARKETSDATAREQUEST"]._serialized_end = 1383
    _globals["_LISTMARKETSDATARESPONSE"]._serialized_start = 1385
    _globals["_LISTMARKETSDATARESPONSE"]._serialized_end = 1463
    _globals["_LISTVOTESREQUEST"]._serialized_start = 1465
    _globals["_LISTVOTESREQUEST"]._serialized_end = 1533
    _globals["_LISTVOTESRESPONSE"]._serialized_start = 1535
    _globals["_LISTVOTESRESPONSE"]._serialized_end = 1588
    _globals["_PARTYSTAKE"]._serialized_start = 1591
    _globals["_PARTYSTAKE"]._serialized_end = 1750
    _globals["_LISTPARTIESSTAKEREQUEST"]._serialized_start = 1752
    _globals["_LISTPARTIESSTAKEREQUEST"]._serialized_end = 1799
    _globals["_LISTPARTIESSTAKERESPONSE"]._serialized_start = 1801
    _globals["_LISTPARTIESSTAKERESPONSE"]._serialized_end = 1889
    _globals["_LISTDELEGATIONSREQUEST"]._serialized_start = 1891
    _globals["_LISTDELEGATIONSREQUEST"]._serialized_end = 1986
    _globals["_LISTDELEGATIONSRESPONSE"]._serialized_start = 1988
    _globals["_LISTDELEGATIONSRESPONSE"]._serialized_end = 2065
    _globals["_CORESTATESERVICE"]._serialized_start = 2068
    _globals["_CORESTATESERVICE"]._serialized_end = 3166
# @@protoc_insertion_point(module_scope)
