# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: vega/data/v1/spec.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC, 5, 27, 2, "", "vega/data/v1/spec.proto"
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x17vega/data/v1/spec.proto\x12\x0cvega.data.v1"n\n\x06\x46ilter\x12+\n\x03key\x18\x01 \x01(\x0b\x32\x19.vega.data.v1.PropertyKeyR\x03key\x12\x37\n\nconditions\x18\x02 \x03(\x0b\x32\x17.vega.data.v1.ConditionR\nconditions"\xb2\x02\n\x0bPropertyKey\x12\x12\n\x04name\x18\x01 \x01(\tR\x04name\x12\x32\n\x04type\x18\x02 \x01(\x0e\x32\x1e.vega.data.v1.PropertyKey.TypeR\x04type\x12\x37\n\x15number_decimal_places\x18\x03 \x01(\x04H\x00R\x13numberDecimalPlaces\x88\x01\x01"\x87\x01\n\x04Type\x12\x14\n\x10TYPE_UNSPECIFIED\x10\x00\x12\x0e\n\nTYPE_EMPTY\x10\x01\x12\x10\n\x0cTYPE_INTEGER\x10\x02\x12\x0f\n\x0bTYPE_STRING\x10\x03\x12\x10\n\x0cTYPE_BOOLEAN\x10\x04\x12\x10\n\x0cTYPE_DECIMAL\x10\x05\x12\x12\n\x0eTYPE_TIMESTAMP\x10\x06\x42\x18\n\x16_number_decimal_places"\x93\x02\n\tCondition\x12<\n\x08operator\x18\x01 \x01(\x0e\x32 .vega.data.v1.Condition.OperatorR\x08operator\x12\x14\n\x05value\x18\x02 \x01(\tR\x05value"\xb1\x01\n\x08Operator\x12\x18\n\x14OPERATOR_UNSPECIFIED\x10\x00\x12\x13\n\x0fOPERATOR_EQUALS\x10\x01\x12\x19\n\x15OPERATOR_GREATER_THAN\x10\x02\x12"\n\x1eOPERATOR_GREATER_THAN_OR_EQUAL\x10\x03\x12\x16\n\x12OPERATOR_LESS_THAN\x10\x04\x12\x1f\n\x1bOPERATOR_LESS_THAN_OR_EQUAL\x10\x05"V\n\x13InternalTimeTrigger\x12\x1d\n\x07initial\x18\x01 \x01(\x03H\x00R\x07initial\x88\x01\x01\x12\x14\n\x05\x65very\x18\x02 \x01(\x03R\x05\x65veryB\n\n\x08_initialB/Z-code.vegaprotocol.io/vega/protos/vega/data/v1b\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "vega.data.v1.spec_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    _globals["DESCRIPTOR"]._loaded_options = None
    _globals["DESCRIPTOR"]._serialized_options = (
        b"Z-code.vegaprotocol.io/vega/protos/vega/data/v1"
    )
    _globals["_FILTER"]._serialized_start = 41
    _globals["_FILTER"]._serialized_end = 151
    _globals["_PROPERTYKEY"]._serialized_start = 154
    _globals["_PROPERTYKEY"]._serialized_end = 460
    _globals["_PROPERTYKEY_TYPE"]._serialized_start = 299
    _globals["_PROPERTYKEY_TYPE"]._serialized_end = 434
    _globals["_CONDITION"]._serialized_start = 463
    _globals["_CONDITION"]._serialized_end = 738
    _globals["_CONDITION_OPERATOR"]._serialized_start = 561
    _globals["_CONDITION_OPERATOR"]._serialized_end = 738
    _globals["_INTERNALTIMETRIGGER"]._serialized_start = 740
    _globals["_INTERNALTIMETRIGGER"]._serialized_end = 826
# @@protoc_insertion_point(module_scope)
