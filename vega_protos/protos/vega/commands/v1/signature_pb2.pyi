from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Signature(_message.Message):
    __slots__ = ("value", "algo", "version")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    ALGO_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    value: str
    algo: str
    version: int
    def __init__(
        self,
        value: _Optional[str] = ...,
        algo: _Optional[str] = ...,
        version: _Optional[int] = ...,
    ) -> None: ...
