# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/oracles/v1/spec.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1avega/oracles/v1/spec.proto\x12\noracles.v1\"P\n\x17OracleSpecConfiguration\x12\x10\n\x08pub_keys\x18\x01 \x03(\t\x12#\n\x07\x66ilters\x18\x02 \x03(\x0b\x32\x12.oracles.v1.Filter\"\xf3\x01\n\nOracleSpec\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\ncreated_at\x18\x02 \x01(\x03\x12\x12\n\nupdated_at\x18\x03 \x01(\x03\x12\x10\n\x08pub_keys\x18\x04 \x03(\t\x12#\n\x07\x66ilters\x18\x05 \x03(\x0b\x32\x12.oracles.v1.Filter\x12-\n\x06status\x18\x06 \x01(\x0e\x32\x1d.oracles.v1.OracleSpec.Status\"K\n\x06Status\x12\x16\n\x12STATUS_UNSPECIFIED\x10\x00\x12\x11\n\rSTATUS_ACTIVE\x10\x01\x12\x16\n\x12STATUS_DEACTIVATED\x10\x02\"Y\n\x06\x46ilter\x12$\n\x03key\x18\x01 \x01(\x0b\x32\x17.oracles.v1.PropertyKey\x12)\n\nconditions\x18\x02 \x03(\x0b\x32\x15.oracles.v1.Condition\"\xd1\x01\n\x0bPropertyKey\x12\x0c\n\x04name\x18\x01 \x01(\t\x12*\n\x04type\x18\x02 \x01(\x0e\x32\x1c.oracles.v1.PropertyKey.Type\"\x87\x01\n\x04Type\x12\x14\n\x10TYPE_UNSPECIFIED\x10\x00\x12\x0e\n\nTYPE_EMPTY\x10\x01\x12\x10\n\x0cTYPE_INTEGER\x10\x02\x12\x0f\n\x0bTYPE_STRING\x10\x03\x12\x10\n\x0cTYPE_BOOLEAN\x10\x04\x12\x10\n\x0cTYPE_DECIMAL\x10\x05\x12\x12\n\x0eTYPE_TIMESTAMP\x10\x06\"\x80\x02\n\tCondition\x12\x30\n\x08operator\x18\x01 \x01(\x0e\x32\x1e.oracles.v1.Condition.Operator\x12\r\n\x05value\x18\x02 \x01(\t\"\xb1\x01\n\x08Operator\x12\x18\n\x14OPERATOR_UNSPECIFIED\x10\x00\x12\x13\n\x0fOPERATOR_EQUALS\x10\x01\x12\x19\n\x15OPERATOR_GREATER_THAN\x10\x02\x12\"\n\x1eOPERATOR_GREATER_THAN_OR_EQUAL\x10\x03\x12\x16\n\x12OPERATOR_LESS_THAN\x10\x04\x12\x1f\n\x1bOPERATOR_LESS_THAN_OR_EQUAL\x10\x05\x42-Z+code.vegaprotocol.io/protos/vega/oracles/v1b\x06proto3')



_ORACLESPECCONFIGURATION = DESCRIPTOR.message_types_by_name['OracleSpecConfiguration']
_ORACLESPEC = DESCRIPTOR.message_types_by_name['OracleSpec']
_FILTER = DESCRIPTOR.message_types_by_name['Filter']
_PROPERTYKEY = DESCRIPTOR.message_types_by_name['PropertyKey']
_CONDITION = DESCRIPTOR.message_types_by_name['Condition']
_ORACLESPEC_STATUS = _ORACLESPEC.enum_types_by_name['Status']
_PROPERTYKEY_TYPE = _PROPERTYKEY.enum_types_by_name['Type']
_CONDITION_OPERATOR = _CONDITION.enum_types_by_name['Operator']
OracleSpecConfiguration = _reflection.GeneratedProtocolMessageType('OracleSpecConfiguration', (_message.Message,), {
  'DESCRIPTOR' : _ORACLESPECCONFIGURATION,
  '__module__' : 'vega.oracles.v1.spec_pb2'
  # @@protoc_insertion_point(class_scope:oracles.v1.OracleSpecConfiguration)
  })
_sym_db.RegisterMessage(OracleSpecConfiguration)

OracleSpec = _reflection.GeneratedProtocolMessageType('OracleSpec', (_message.Message,), {
  'DESCRIPTOR' : _ORACLESPEC,
  '__module__' : 'vega.oracles.v1.spec_pb2'
  # @@protoc_insertion_point(class_scope:oracles.v1.OracleSpec)
  })
_sym_db.RegisterMessage(OracleSpec)

Filter = _reflection.GeneratedProtocolMessageType('Filter', (_message.Message,), {
  'DESCRIPTOR' : _FILTER,
  '__module__' : 'vega.oracles.v1.spec_pb2'
  # @@protoc_insertion_point(class_scope:oracles.v1.Filter)
  })
_sym_db.RegisterMessage(Filter)

PropertyKey = _reflection.GeneratedProtocolMessageType('PropertyKey', (_message.Message,), {
  'DESCRIPTOR' : _PROPERTYKEY,
  '__module__' : 'vega.oracles.v1.spec_pb2'
  # @@protoc_insertion_point(class_scope:oracles.v1.PropertyKey)
  })
_sym_db.RegisterMessage(PropertyKey)

Condition = _reflection.GeneratedProtocolMessageType('Condition', (_message.Message,), {
  'DESCRIPTOR' : _CONDITION,
  '__module__' : 'vega.oracles.v1.spec_pb2'
  # @@protoc_insertion_point(class_scope:oracles.v1.Condition)
  })
_sym_db.RegisterMessage(Condition)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z+code.vegaprotocol.io/protos/vega/oracles/v1'
  _ORACLESPECCONFIGURATION._serialized_start=42
  _ORACLESPECCONFIGURATION._serialized_end=122
  _ORACLESPEC._serialized_start=125
  _ORACLESPEC._serialized_end=368
  _ORACLESPEC_STATUS._serialized_start=293
  _ORACLESPEC_STATUS._serialized_end=368
  _FILTER._serialized_start=370
  _FILTER._serialized_end=459
  _PROPERTYKEY._serialized_start=462
  _PROPERTYKEY._serialized_end=671
  _PROPERTYKEY_TYPE._serialized_start=536
  _PROPERTYKEY_TYPE._serialized_end=671
  _CONDITION._serialized_start=674
  _CONDITION._serialized_end=930
  _CONDITION_OPERATOR._serialized_start=753
  _CONDITION_OPERATOR._serialized_end=930
# @@protoc_insertion_point(module_scope)
