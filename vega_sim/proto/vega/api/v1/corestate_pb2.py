# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/api/v1/corestate.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ... import assets_pb2 as vega_dot_assets__pb2
from ... import governance_pb2 as vega_dot_governance__pb2
from ... import markets_pb2 as vega_dot_markets__pb2
from ... import vega_pb2 as vega_dot_vega__pb2
from ...events.v1 import events_pb2 as vega_dot_events_dot_v1_dot_events__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1bvega/api/v1/corestate.proto\x12\x0bvega.api.v1\x1a\x11vega/assets.proto\x1a\x15vega/governance.proto\x1a\x12vega/markets.proto\x1a\x0fvega/vega.proto\x1a\x1bvega/events/v1/events.proto"V\n\x07\x41\x63\x63ount\x12\r\n\x05party\x18\x01 \x01(\t\x12\x0e\n\x06market\x18\x02 \x01(\t\x12\x0f\n\x07\x62\x61lance\x18\x03 \x01(\t\x12\r\n\x05\x61sset\x18\x05 \x01(\t\x12\x0c\n\x04type\x18\x06 \x01(\t"4\n\x13ListAccountsRequest\x12\r\n\x05party\x18\x01 \x01(\t\x12\x0e\n\x06market\x18\x02 \x01(\t">\n\x14ListAccountsResponse\x12&\n\x08\x61\x63\x63ounts\x18\x01 \x03(\x0b\x32\x14.vega.api.v1.Account""\n\x11ListAssetsRequest\x12\r\n\x05\x61sset\x18\x01 \x01(\t"1\n\x12ListAssetsResponse\x12\x1b\n\x06\x61ssets\x18\x01 \x03(\x0b\x32\x0b.vega.Asset"=\n\x1cListNetworkParametersRequest\x12\x1d\n\x15network_parameter_key\x18\x01 \x01(\t"S\n\x1dListNetworkParametersResponse\x12\x32\n\x12network_parameters\x18\x01 \x03(\x0b\x32\x16.vega.NetworkParameter"\x1a\n\x18ListNetworkLimitsRequest"H\n\x19ListNetworkLimitsResponse\x12+\n\x0enetwork_limits\x18\x01 \x01(\x0b\x32\x13.vega.NetworkLimits"\x14\n\x12ListPartiesRequest"3\n\x13ListPartiesResponse\x12\x1c\n\x07parties\x18\x01 \x03(\x0b\x32\x0b.vega.Party"\x17\n\x15ListValidatorsRequest"M\n\x16ListValidatorsResponse\x12\x33\n\nvalidators\x18\x01 \x03(\x0b\x32\x1f.vega.events.v1.ValidatorUpdate"$\n\x12ListMarketsRequest\x12\x0e\n\x06market\x18\x01 \x01(\t"4\n\x13ListMarketsResponse\x12\x1d\n\x07markets\x18\x01 \x03(\x0b\x32\x0c.vega.Market":\n\x14ListProposalsRequest\x12\x10\n\x08proposal\x18\x01 \x01(\t\x12\x10\n\x08proposer\x18\x02 \x01(\t":\n\x15ListProposalsResponse\x12!\n\tproposals\x18\x01 \x03(\x0b\x32\x0e.vega.Proposal"(\n\x16ListMarketsDataRequest\x12\x0e\n\x06market\x18\x01 \x01(\t"A\n\x17ListMarketsDataResponse\x12&\n\x0cmarkets_data\x18\x01 \x03(\x0b\x32\x10.vega.MarketData"3\n\x10ListVotesRequest\x12\x10\n\x08proposal\x18\x01 \x01(\t\x12\r\n\x05party\x18\x02 \x01(\t".\n\x11ListVotesResponse\x12\x19\n\x05votes\x18\x01 \x03(\x0b\x32\n.vega.Vote"r\n\nPartyStake\x12\r\n\x05party\x18\x01 \x01(\t\x12\x1f\n\x17\x63urrent_stake_available\x18\x02 \x01(\t\x12\x34\n\x0estake_linkings\x18\x03 \x03(\x0b\x32\x1c.vega.events.v1.StakeLinking"(\n\x17ListPartiesStakeRequest\x12\r\n\x05party\x18\x01 \x01(\t"J\n\x18ListPartiesStakeResponse\x12.\n\rparties_stake\x18\x01 \x03(\x0b\x32\x17.vega.api.v1.PartyStake"H\n\x16ListDelegationsRequest\x12\r\n\x05party\x18\x01 \x01(\t\x12\x0c\n\x04node\x18\x02 \x01(\t\x12\x11\n\tepoch_seq\x18\x03 \x01(\t"@\n\x17ListDelegationsResponse\x12%\n\x0b\x64\x65legations\x18\x01 \x03(\x0b\x32\x10.vega.Delegation2\xca\x08\n\x10\x43oreStateService\x12S\n\x0cListAccounts\x12 .vega.api.v1.ListAccountsRequest\x1a!.vega.api.v1.ListAccountsResponse\x12M\n\nListAssets\x12\x1e.vega.api.v1.ListAssetsRequest\x1a\x1f.vega.api.v1.ListAssetsResponse\x12n\n\x15ListNetworkParameters\x12).vega.api.v1.ListNetworkParametersRequest\x1a*.vega.api.v1.ListNetworkParametersResponse\x12\x62\n\x11ListNetworkLimits\x12%.vega.api.v1.ListNetworkLimitsRequest\x1a&.vega.api.v1.ListNetworkLimitsResponse\x12P\n\x0bListParties\x12\x1f.vega.api.v1.ListPartiesRequest\x1a .vega.api.v1.ListPartiesResponse\x12Y\n\x0eListValidators\x12".vega.api.v1.ListValidatorsRequest\x1a#.vega.api.v1.ListValidatorsResponse\x12P\n\x0bListMarkets\x12\x1f.vega.api.v1.ListMarketsRequest\x1a .vega.api.v1.ListMarketsResponse\x12V\n\rListProposals\x12!.vega.api.v1.ListProposalsRequest\x1a".vega.api.v1.ListProposalsResponse\x12\\\n\x0fListMarketsData\x12#.vega.api.v1.ListMarketsDataRequest\x1a$.vega.api.v1.ListMarketsDataResponse\x12J\n\tListVotes\x12\x1d.vega.api.v1.ListVotesRequest\x1a\x1e.vega.api.v1.ListVotesResponse\x12_\n\x10ListPartiesStake\x12$.vega.api.v1.ListPartiesStakeRequest\x1a%.vega.api.v1.ListPartiesStakeResponse\x12\\\n\x0fListDelegations\x12#.vega.api.v1.ListDelegationsRequest\x1a$.vega.api.v1.ListDelegationsResponseB)Z\'code.vegaprotocol.io/protos/vega/api/v1b\x06proto3'
)


_ACCOUNT = DESCRIPTOR.message_types_by_name["Account"]
_LISTACCOUNTSREQUEST = DESCRIPTOR.message_types_by_name["ListAccountsRequest"]
_LISTACCOUNTSRESPONSE = DESCRIPTOR.message_types_by_name["ListAccountsResponse"]
_LISTASSETSREQUEST = DESCRIPTOR.message_types_by_name["ListAssetsRequest"]
_LISTASSETSRESPONSE = DESCRIPTOR.message_types_by_name["ListAssetsResponse"]
_LISTNETWORKPARAMETERSREQUEST = DESCRIPTOR.message_types_by_name[
    "ListNetworkParametersRequest"
]
_LISTNETWORKPARAMETERSRESPONSE = DESCRIPTOR.message_types_by_name[
    "ListNetworkParametersResponse"
]
_LISTNETWORKLIMITSREQUEST = DESCRIPTOR.message_types_by_name["ListNetworkLimitsRequest"]
_LISTNETWORKLIMITSRESPONSE = DESCRIPTOR.message_types_by_name[
    "ListNetworkLimitsResponse"
]
_LISTPARTIESREQUEST = DESCRIPTOR.message_types_by_name["ListPartiesRequest"]
_LISTPARTIESRESPONSE = DESCRIPTOR.message_types_by_name["ListPartiesResponse"]
_LISTVALIDATORSREQUEST = DESCRIPTOR.message_types_by_name["ListValidatorsRequest"]
_LISTVALIDATORSRESPONSE = DESCRIPTOR.message_types_by_name["ListValidatorsResponse"]
_LISTMARKETSREQUEST = DESCRIPTOR.message_types_by_name["ListMarketsRequest"]
_LISTMARKETSRESPONSE = DESCRIPTOR.message_types_by_name["ListMarketsResponse"]
_LISTPROPOSALSREQUEST = DESCRIPTOR.message_types_by_name["ListProposalsRequest"]
_LISTPROPOSALSRESPONSE = DESCRIPTOR.message_types_by_name["ListProposalsResponse"]
_LISTMARKETSDATAREQUEST = DESCRIPTOR.message_types_by_name["ListMarketsDataRequest"]
_LISTMARKETSDATARESPONSE = DESCRIPTOR.message_types_by_name["ListMarketsDataResponse"]
_LISTVOTESREQUEST = DESCRIPTOR.message_types_by_name["ListVotesRequest"]
_LISTVOTESRESPONSE = DESCRIPTOR.message_types_by_name["ListVotesResponse"]
_PARTYSTAKE = DESCRIPTOR.message_types_by_name["PartyStake"]
_LISTPARTIESSTAKEREQUEST = DESCRIPTOR.message_types_by_name["ListPartiesStakeRequest"]
_LISTPARTIESSTAKERESPONSE = DESCRIPTOR.message_types_by_name["ListPartiesStakeResponse"]
_LISTDELEGATIONSREQUEST = DESCRIPTOR.message_types_by_name["ListDelegationsRequest"]
_LISTDELEGATIONSRESPONSE = DESCRIPTOR.message_types_by_name["ListDelegationsResponse"]
Account = _reflection.GeneratedProtocolMessageType(
    "Account",
    (_message.Message,),
    {
        "DESCRIPTOR": _ACCOUNT,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.Account)
    },
)
_sym_db.RegisterMessage(Account)

ListAccountsRequest = _reflection.GeneratedProtocolMessageType(
    "ListAccountsRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTACCOUNTSREQUEST,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListAccountsRequest)
    },
)
_sym_db.RegisterMessage(ListAccountsRequest)

ListAccountsResponse = _reflection.GeneratedProtocolMessageType(
    "ListAccountsResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTACCOUNTSRESPONSE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListAccountsResponse)
    },
)
_sym_db.RegisterMessage(ListAccountsResponse)

ListAssetsRequest = _reflection.GeneratedProtocolMessageType(
    "ListAssetsRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTASSETSREQUEST,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListAssetsRequest)
    },
)
_sym_db.RegisterMessage(ListAssetsRequest)

ListAssetsResponse = _reflection.GeneratedProtocolMessageType(
    "ListAssetsResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTASSETSRESPONSE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListAssetsResponse)
    },
)
_sym_db.RegisterMessage(ListAssetsResponse)

ListNetworkParametersRequest = _reflection.GeneratedProtocolMessageType(
    "ListNetworkParametersRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTNETWORKPARAMETERSREQUEST,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListNetworkParametersRequest)
    },
)
_sym_db.RegisterMessage(ListNetworkParametersRequest)

ListNetworkParametersResponse = _reflection.GeneratedProtocolMessageType(
    "ListNetworkParametersResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTNETWORKPARAMETERSRESPONSE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListNetworkParametersResponse)
    },
)
_sym_db.RegisterMessage(ListNetworkParametersResponse)

ListNetworkLimitsRequest = _reflection.GeneratedProtocolMessageType(
    "ListNetworkLimitsRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTNETWORKLIMITSREQUEST,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListNetworkLimitsRequest)
    },
)
_sym_db.RegisterMessage(ListNetworkLimitsRequest)

ListNetworkLimitsResponse = _reflection.GeneratedProtocolMessageType(
    "ListNetworkLimitsResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTNETWORKLIMITSRESPONSE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListNetworkLimitsResponse)
    },
)
_sym_db.RegisterMessage(ListNetworkLimitsResponse)

ListPartiesRequest = _reflection.GeneratedProtocolMessageType(
    "ListPartiesRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTPARTIESREQUEST,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListPartiesRequest)
    },
)
_sym_db.RegisterMessage(ListPartiesRequest)

ListPartiesResponse = _reflection.GeneratedProtocolMessageType(
    "ListPartiesResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTPARTIESRESPONSE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListPartiesResponse)
    },
)
_sym_db.RegisterMessage(ListPartiesResponse)

ListValidatorsRequest = _reflection.GeneratedProtocolMessageType(
    "ListValidatorsRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTVALIDATORSREQUEST,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListValidatorsRequest)
    },
)
_sym_db.RegisterMessage(ListValidatorsRequest)

ListValidatorsResponse = _reflection.GeneratedProtocolMessageType(
    "ListValidatorsResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTVALIDATORSRESPONSE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListValidatorsResponse)
    },
)
_sym_db.RegisterMessage(ListValidatorsResponse)

ListMarketsRequest = _reflection.GeneratedProtocolMessageType(
    "ListMarketsRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTMARKETSREQUEST,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListMarketsRequest)
    },
)
_sym_db.RegisterMessage(ListMarketsRequest)

ListMarketsResponse = _reflection.GeneratedProtocolMessageType(
    "ListMarketsResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTMARKETSRESPONSE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListMarketsResponse)
    },
)
_sym_db.RegisterMessage(ListMarketsResponse)

ListProposalsRequest = _reflection.GeneratedProtocolMessageType(
    "ListProposalsRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTPROPOSALSREQUEST,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListProposalsRequest)
    },
)
_sym_db.RegisterMessage(ListProposalsRequest)

ListProposalsResponse = _reflection.GeneratedProtocolMessageType(
    "ListProposalsResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTPROPOSALSRESPONSE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListProposalsResponse)
    },
)
_sym_db.RegisterMessage(ListProposalsResponse)

ListMarketsDataRequest = _reflection.GeneratedProtocolMessageType(
    "ListMarketsDataRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTMARKETSDATAREQUEST,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListMarketsDataRequest)
    },
)
_sym_db.RegisterMessage(ListMarketsDataRequest)

ListMarketsDataResponse = _reflection.GeneratedProtocolMessageType(
    "ListMarketsDataResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTMARKETSDATARESPONSE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListMarketsDataResponse)
    },
)
_sym_db.RegisterMessage(ListMarketsDataResponse)

ListVotesRequest = _reflection.GeneratedProtocolMessageType(
    "ListVotesRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTVOTESREQUEST,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListVotesRequest)
    },
)
_sym_db.RegisterMessage(ListVotesRequest)

ListVotesResponse = _reflection.GeneratedProtocolMessageType(
    "ListVotesResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTVOTESRESPONSE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListVotesResponse)
    },
)
_sym_db.RegisterMessage(ListVotesResponse)

PartyStake = _reflection.GeneratedProtocolMessageType(
    "PartyStake",
    (_message.Message,),
    {
        "DESCRIPTOR": _PARTYSTAKE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.PartyStake)
    },
)
_sym_db.RegisterMessage(PartyStake)

ListPartiesStakeRequest = _reflection.GeneratedProtocolMessageType(
    "ListPartiesStakeRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTPARTIESSTAKEREQUEST,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListPartiesStakeRequest)
    },
)
_sym_db.RegisterMessage(ListPartiesStakeRequest)

ListPartiesStakeResponse = _reflection.GeneratedProtocolMessageType(
    "ListPartiesStakeResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTPARTIESSTAKERESPONSE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListPartiesStakeResponse)
    },
)
_sym_db.RegisterMessage(ListPartiesStakeResponse)

ListDelegationsRequest = _reflection.GeneratedProtocolMessageType(
    "ListDelegationsRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTDELEGATIONSREQUEST,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListDelegationsRequest)
    },
)
_sym_db.RegisterMessage(ListDelegationsRequest)

ListDelegationsResponse = _reflection.GeneratedProtocolMessageType(
    "ListDelegationsResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _LISTDELEGATIONSRESPONSE,
        "__module__": "vega.api.v1.corestate_pb2"
        # @@protoc_insertion_point(class_scope:vega.api.v1.ListDelegationsResponse)
    },
)
_sym_db.RegisterMessage(ListDelegationsResponse)

_CORESTATESERVICE = DESCRIPTOR.services_by_name["CoreStateService"]
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z'code.vegaprotocol.io/protos/vega/api/v1"
    _ACCOUNT._serialized_start = 152
    _ACCOUNT._serialized_end = 238
    _LISTACCOUNTSREQUEST._serialized_start = 240
    _LISTACCOUNTSREQUEST._serialized_end = 292
    _LISTACCOUNTSRESPONSE._serialized_start = 294
    _LISTACCOUNTSRESPONSE._serialized_end = 356
    _LISTASSETSREQUEST._serialized_start = 358
    _LISTASSETSREQUEST._serialized_end = 392
    _LISTASSETSRESPONSE._serialized_start = 394
    _LISTASSETSRESPONSE._serialized_end = 443
    _LISTNETWORKPARAMETERSREQUEST._serialized_start = 445
    _LISTNETWORKPARAMETERSREQUEST._serialized_end = 506
    _LISTNETWORKPARAMETERSRESPONSE._serialized_start = 508
    _LISTNETWORKPARAMETERSRESPONSE._serialized_end = 591
    _LISTNETWORKLIMITSREQUEST._serialized_start = 593
    _LISTNETWORKLIMITSREQUEST._serialized_end = 619
    _LISTNETWORKLIMITSRESPONSE._serialized_start = 621
    _LISTNETWORKLIMITSRESPONSE._serialized_end = 693
    _LISTPARTIESREQUEST._serialized_start = 695
    _LISTPARTIESREQUEST._serialized_end = 715
    _LISTPARTIESRESPONSE._serialized_start = 717
    _LISTPARTIESRESPONSE._serialized_end = 768
    _LISTVALIDATORSREQUEST._serialized_start = 770
    _LISTVALIDATORSREQUEST._serialized_end = 793
    _LISTVALIDATORSRESPONSE._serialized_start = 795
    _LISTVALIDATORSRESPONSE._serialized_end = 872
    _LISTMARKETSREQUEST._serialized_start = 874
    _LISTMARKETSREQUEST._serialized_end = 910
    _LISTMARKETSRESPONSE._serialized_start = 912
    _LISTMARKETSRESPONSE._serialized_end = 964
    _LISTPROPOSALSREQUEST._serialized_start = 966
    _LISTPROPOSALSREQUEST._serialized_end = 1024
    _LISTPROPOSALSRESPONSE._serialized_start = 1026
    _LISTPROPOSALSRESPONSE._serialized_end = 1084
    _LISTMARKETSDATAREQUEST._serialized_start = 1086
    _LISTMARKETSDATAREQUEST._serialized_end = 1126
    _LISTMARKETSDATARESPONSE._serialized_start = 1128
    _LISTMARKETSDATARESPONSE._serialized_end = 1193
    _LISTVOTESREQUEST._serialized_start = 1195
    _LISTVOTESREQUEST._serialized_end = 1246
    _LISTVOTESRESPONSE._serialized_start = 1248
    _LISTVOTESRESPONSE._serialized_end = 1294
    _PARTYSTAKE._serialized_start = 1296
    _PARTYSTAKE._serialized_end = 1410
    _LISTPARTIESSTAKEREQUEST._serialized_start = 1412
    _LISTPARTIESSTAKEREQUEST._serialized_end = 1452
    _LISTPARTIESSTAKERESPONSE._serialized_start = 1454
    _LISTPARTIESSTAKERESPONSE._serialized_end = 1528
    _LISTDELEGATIONSREQUEST._serialized_start = 1530
    _LISTDELEGATIONSREQUEST._serialized_end = 1602
    _LISTDELEGATIONSRESPONSE._serialized_start = 1604
    _LISTDELEGATIONSRESPONSE._serialized_end = 1668
    _CORESTATESERVICE._serialized_start = 1671
    _CORESTATESERVICE._serialized_end = 2769
# @@protoc_insertion_point(module_scope)
