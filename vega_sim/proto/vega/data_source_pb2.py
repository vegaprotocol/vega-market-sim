# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/data_source.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from .data.v1 import data_pb2 as vega_dot_data_dot_v1_dot_data__pb2
from .data.v1 import spec_pb2 as vega_dot_data_dot_v1_dot_spec__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x16vega/data_source.proto\x12\x04vega\x1a\x1cgoogle/protobuf/struct.proto\x1a\x17vega/data/v1/data.proto\x1a\x17vega/data/v1/spec.proto"\xa9\x01\n\x14\x44\x61taSourceDefinition\x12@\n\x08internal\x18\x01 \x01(\x0b\x32".vega.DataSourceDefinitionInternalH\x00R\x08internal\x12@\n\x08\x65xternal\x18\x02 \x01(\x0b\x32".vega.DataSourceDefinitionExternalH\x00R\x08\x65xternalB\r\n\x0bsource_type"Z\n\x1f\x44\x61taSourceSpecConfigurationTime\x12\x37\n\nconditions\x18\x01 \x03(\x0b\x32\x17.vega.data.v1.ConditionR\nconditions"j\n\x1c\x44\x61taSourceDefinitionInternal\x12;\n\x04time\x18\x01 \x01(\x0b\x32%.vega.DataSourceSpecConfigurationTimeH\x00R\x04timeB\r\n\x0bsource_type"\x9e\x01\n\x1c\x44\x61taSourceDefinitionExternal\x12;\n\x06oracle\x18\x01 \x01(\x0b\x32!.vega.DataSourceSpecConfigurationH\x00R\x06oracle\x12\x32\n\neth_oracle\x18\x02 \x01(\x0b\x32\x11.vega.EthCallSpecH\x00R\tethOracleB\r\n\x0bsource_type"}\n\x1b\x44\x61taSourceSpecConfiguration\x12.\n\x07signers\x18\x01 \x03(\x0b\x32\x14.vega.data.v1.SignerR\x07signers\x12.\n\x07\x66ilters\x18\x02 \x03(\x0b\x32\x14.vega.data.v1.FilterR\x07\x66ilters"\xc8\x02\n\x0b\x45thCallSpec\x12\x18\n\x07\x61\x64\x64ress\x18\x01 \x01(\tR\x07\x61\x64\x64ress\x12\x10\n\x03\x61\x62i\x18\x02 \x01(\tR\x03\x61\x62i\x12\x16\n\x06method\x18\x03 \x01(\tR\x06method\x12*\n\x04\x61rgs\x18\x04 \x03(\x0b\x32\x16.google.protobuf.ValueR\x04\x61rgs\x12.\n\x07trigger\x18\x05 \x01(\x0b\x32\x14.vega.EthCallTriggerR\x07trigger\x12\x35\n\x16required_confirmations\x18\x06 \x01(\x04R\x15requiredConfirmations\x12.\n\x07\x66ilters\x18\x07 \x03(\x0b\x32\x14.vega.data.v1.FilterR\x07\x66ilters\x12\x32\n\x0bnormalisers\x18\x08 \x03(\x0b\x32\x10.vega.NormaliserR\x0bnormalisers"@\n\nNormaliser\x12\x12\n\x04name\x18\x01 \x01(\tR\x04name\x12\x1e\n\nexpression\x18\x02 \x01(\tR\nexpression"V\n\x0e\x45thCallTrigger\x12\x39\n\x0ctime_trigger\x18\x01 \x01(\x0b\x32\x14.vega.EthTimeTriggerH\x00R\x0btimeTriggerB\t\n\x07trigger"\x85\x01\n\x0e\x45thTimeTrigger\x12\x1d\n\x07initial\x18\x01 \x01(\x04H\x00R\x07initial\x88\x01\x01\x12\x19\n\x05\x65very\x18\x02 \x01(\x04H\x01R\x05\x65very\x88\x01\x01\x12\x19\n\x05until\x18\x03 \x01(\x04H\x02R\x05until\x88\x01\x01\x42\n\n\x08_initialB\x08\n\x06_everyB\x08\n\x06_until"\x90\x02\n\x0e\x44\x61taSourceSpec\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x1d\n\ncreated_at\x18\x02 \x01(\x03R\tcreatedAt\x12\x1d\n\nupdated_at\x18\x03 \x01(\x03R\tupdatedAt\x12.\n\x04\x64\x61ta\x18\x04 \x01(\x0b\x32\x1a.vega.DataSourceDefinitionR\x04\x64\x61ta\x12\x33\n\x06status\x18\x05 \x01(\x0e\x32\x1b.vega.DataSourceSpec.StatusR\x06status"K\n\x06Status\x12\x16\n\x12STATUS_UNSPECIFIED\x10\x00\x12\x11\n\rSTATUS_ACTIVE\x10\x01\x12\x16\n\x12STATUS_DEACTIVATED\x10\x02"B\n\x16\x45xternalDataSourceSpec\x12(\n\x04spec\x18\x01 \x01(\x0b\x32\x14.vega.DataSourceSpecR\x04specB\'Z%code.vegaprotocol.io/vega/protos/vegab\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "vega.data_source_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z%code.vegaprotocol.io/vega/protos/vega"
    _globals["_DATASOURCEDEFINITION"]._serialized_start = 113
    _globals["_DATASOURCEDEFINITION"]._serialized_end = 282
    _globals["_DATASOURCESPECCONFIGURATIONTIME"]._serialized_start = 284
    _globals["_DATASOURCESPECCONFIGURATIONTIME"]._serialized_end = 374
    _globals["_DATASOURCEDEFINITIONINTERNAL"]._serialized_start = 376
    _globals["_DATASOURCEDEFINITIONINTERNAL"]._serialized_end = 482
    _globals["_DATASOURCEDEFINITIONEXTERNAL"]._serialized_start = 485
    _globals["_DATASOURCEDEFINITIONEXTERNAL"]._serialized_end = 643
    _globals["_DATASOURCESPECCONFIGURATION"]._serialized_start = 645
    _globals["_DATASOURCESPECCONFIGURATION"]._serialized_end = 770
    _globals["_ETHCALLSPEC"]._serialized_start = 773
    _globals["_ETHCALLSPEC"]._serialized_end = 1101
    _globals["_NORMALISER"]._serialized_start = 1103
    _globals["_NORMALISER"]._serialized_end = 1167
    _globals["_ETHCALLTRIGGER"]._serialized_start = 1169
    _globals["_ETHCALLTRIGGER"]._serialized_end = 1255
    _globals["_ETHTIMETRIGGER"]._serialized_start = 1258
    _globals["_ETHTIMETRIGGER"]._serialized_end = 1391
    _globals["_DATASOURCESPEC"]._serialized_start = 1394
    _globals["_DATASOURCESPEC"]._serialized_end = 1666
    _globals["_DATASOURCESPEC_STATUS"]._serialized_start = 1591
    _globals["_DATASOURCESPEC_STATUS"]._serialized_end = 1666
    _globals["_EXTERNALDATASOURCESPEC"]._serialized_start = 1668
    _globals["_EXTERNALDATASOURCESPEC"]._serialized_end = 1734
# @@protoc_insertion_point(module_scope)
