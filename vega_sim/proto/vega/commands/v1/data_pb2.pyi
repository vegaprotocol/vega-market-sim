from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OracleDataSubmission(_message.Message):
    __slots__ = ["source", "payload"]

    class OracleSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        ORACLE_SOURCE_UNSPECIFIED: _ClassVar[OracleDataSubmission.OracleSource]
        ORACLE_SOURCE_OPEN_ORACLE: _ClassVar[OracleDataSubmission.OracleSource]
        ORACLE_SOURCE_JSON: _ClassVar[OracleDataSubmission.OracleSource]
        ORACLE_SOURCE_ETHEREUM: _ClassVar[OracleDataSubmission.OracleSource]
    ORACLE_SOURCE_UNSPECIFIED: OracleDataSubmission.OracleSource
    ORACLE_SOURCE_OPEN_ORACLE: OracleDataSubmission.OracleSource
    ORACLE_SOURCE_JSON: OracleDataSubmission.OracleSource
    ORACLE_SOURCE_ETHEREUM: OracleDataSubmission.OracleSource
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    source: OracleDataSubmission.OracleSource
    payload: bytes
    def __init__(
        self,
        source: _Optional[_Union[OracleDataSubmission.OracleSource, str]] = ...,
        payload: _Optional[bytes] = ...,
    ) -> None: ...
