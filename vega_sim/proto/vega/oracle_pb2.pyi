from vega.data.v1 import data_pb2 as _data_pb2
from vega import data_source_pb2 as _data_source_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class OracleSpec(_message.Message):
    __slots__ = ["external_data_source_spec"]
    EXTERNAL_DATA_SOURCE_SPEC_FIELD_NUMBER: _ClassVar[int]
    external_data_source_spec: _data_source_pb2.ExternalDataSourceSpec
    def __init__(
        self,
        external_data_source_spec: _Optional[
            _Union[_data_source_pb2.ExternalDataSourceSpec, _Mapping]
        ] = ...,
    ) -> None: ...

class OracleData(_message.Message):
    __slots__ = ["external_data"]
    EXTERNAL_DATA_FIELD_NUMBER: _ClassVar[int]
    external_data: _data_pb2.ExternalData
    def __init__(
        self, external_data: _Optional[_Union[_data_pb2.ExternalData, _Mapping]] = ...
    ) -> None: ...
