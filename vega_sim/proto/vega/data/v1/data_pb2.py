# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: vega/data/v1/data.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC, 5, 27, 2, "", "vega/data/v1/data.proto"
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x17vega/data/v1/data.proto\x12\x0cvega.data.v1"&\n\nETHAddress\x12\x18\n\x07\x61\x64\x64ress\x18\x01 \x01(\tR\x07\x61\x64\x64ress"\x1a\n\x06PubKey\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key"\x80\x01\n\x06Signer\x12/\n\x07pub_key\x18\x01 \x01(\x0b\x32\x14.vega.data.v1.PubKeyH\x00R\x06pubKey\x12;\n\x0b\x65th_address\x18\x02 \x01(\x0b\x32\x18.vega.data.v1.ETHAddressH\x00R\nethAddressB\x08\n\x06signer"4\n\x08Property\x12\x12\n\x04name\x18\x01 \x01(\tR\x04name\x12\x14\n\x05value\x18\x02 \x01(\tR\x05value"\x89\x02\n\x04\x44\x61ta\x12.\n\x07signers\x18\x01 \x03(\x0b\x32\x14.vega.data.v1.SignerR\x07signers\x12*\n\x04\x64\x61ta\x18\x02 \x03(\x0b\x32\x16.vega.data.v1.PropertyR\x04\x64\x61ta\x12(\n\x10matched_spec_ids\x18\x03 \x03(\tR\x0ematchedSpecIds\x12!\n\x0c\x62roadcast_at\x18\x04 \x01(\x03R\x0b\x62roadcastAt\x12\x33\n\tmeta_data\x18\x05 \x03(\x0b\x32\x16.vega.data.v1.PropertyR\x08metaData\x12\x19\n\x05\x65rror\x18\x06 \x01(\tH\x00R\x05\x65rror\x88\x01\x01\x42\x08\n\x06_error"6\n\x0c\x45xternalData\x12&\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x12.vega.data.v1.DataR\x04\x64\x61taB/Z-code.vegaprotocol.io/vega/protos/vega/data/v1b\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "vega.data.v1.data_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    _globals["DESCRIPTOR"]._loaded_options = None
    _globals["DESCRIPTOR"]._serialized_options = (
        b"Z-code.vegaprotocol.io/vega/protos/vega/data/v1"
    )
    _globals["_ETHADDRESS"]._serialized_start = 41
    _globals["_ETHADDRESS"]._serialized_end = 79
    _globals["_PUBKEY"]._serialized_start = 81
    _globals["_PUBKEY"]._serialized_end = 107
    _globals["_SIGNER"]._serialized_start = 110
    _globals["_SIGNER"]._serialized_end = 238
    _globals["_PROPERTY"]._serialized_start = 240
    _globals["_PROPERTY"]._serialized_end = 292
    _globals["_DATA"]._serialized_start = 295
    _globals["_DATA"]._serialized_end = 560
    _globals["_EXTERNALDATA"]._serialized_start = 562
    _globals["_EXTERNALDATA"]._serialized_end = 616
# @@protoc_insertion_point(module_scope)
