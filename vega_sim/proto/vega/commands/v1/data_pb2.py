# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/commands/v1/data.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1bvega/commands/v1/data.proto\x12\x10vega.commands.v1"\xe3\x01\n\x14OracleDataSubmission\x12K\n\x06source\x18\x01 \x01(\x0e\x32\x33.vega.commands.v1.OracleDataSubmission.OracleSourceR\x06source\x12\x18\n\x07payload\x18\x02 \x01(\x0cR\x07payload"d\n\x0cOracleSource\x12\x1d\n\x19ORACLE_SOURCE_UNSPECIFIED\x10\x00\x12\x1d\n\x19ORACLE_SOURCE_OPEN_ORACLE\x10\x01\x12\x16\n\x12ORACLE_SOURCE_JSON\x10\x02\x42\x33Z1code.vegaprotocol.io/vega/protos/vega/commands/v1b\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "vega.commands.v1.data_pb2", globals()
)
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = (
        b"Z1code.vegaprotocol.io/vega/protos/vega/commands/v1"
    )
    _ORACLEDATASUBMISSION._serialized_start = 50
    _ORACLEDATASUBMISSION._serialized_end = 277
    _ORACLEDATASUBMISSION_ORACLESOURCE._serialized_start = 177
    _ORACLEDATASUBMISSION_ORACLESOURCE._serialized_end = 277
# @@protoc_insertion_point(module_scope)
