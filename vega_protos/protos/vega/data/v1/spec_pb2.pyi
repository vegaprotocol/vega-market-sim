from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class Filter(_message.Message):
    __slots__ = ("key", "conditions")
    KEY_FIELD_NUMBER: _ClassVar[int]
    CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    key: PropertyKey
    conditions: _containers.RepeatedCompositeFieldContainer[Condition]
    def __init__(
        self,
        key: _Optional[_Union[PropertyKey, _Mapping]] = ...,
        conditions: _Optional[_Iterable[_Union[Condition, _Mapping]]] = ...,
    ) -> None: ...

class PropertyKey(_message.Message):
    __slots__ = ("name", "type", "number_decimal_places")

    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[PropertyKey.Type]
        TYPE_EMPTY: _ClassVar[PropertyKey.Type]
        TYPE_INTEGER: _ClassVar[PropertyKey.Type]
        TYPE_STRING: _ClassVar[PropertyKey.Type]
        TYPE_BOOLEAN: _ClassVar[PropertyKey.Type]
        TYPE_DECIMAL: _ClassVar[PropertyKey.Type]
        TYPE_TIMESTAMP: _ClassVar[PropertyKey.Type]

    TYPE_UNSPECIFIED: PropertyKey.Type
    TYPE_EMPTY: PropertyKey.Type
    TYPE_INTEGER: PropertyKey.Type
    TYPE_STRING: PropertyKey.Type
    TYPE_BOOLEAN: PropertyKey.Type
    TYPE_DECIMAL: PropertyKey.Type
    TYPE_TIMESTAMP: PropertyKey.Type
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_DECIMAL_PLACES_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: PropertyKey.Type
    number_decimal_places: int
    def __init__(
        self,
        name: _Optional[str] = ...,
        type: _Optional[_Union[PropertyKey.Type, str]] = ...,
        number_decimal_places: _Optional[int] = ...,
    ) -> None: ...

class Condition(_message.Message):
    __slots__ = ("operator", "value")

    class Operator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OPERATOR_UNSPECIFIED: _ClassVar[Condition.Operator]
        OPERATOR_EQUALS: _ClassVar[Condition.Operator]
        OPERATOR_GREATER_THAN: _ClassVar[Condition.Operator]
        OPERATOR_GREATER_THAN_OR_EQUAL: _ClassVar[Condition.Operator]
        OPERATOR_LESS_THAN: _ClassVar[Condition.Operator]
        OPERATOR_LESS_THAN_OR_EQUAL: _ClassVar[Condition.Operator]

    OPERATOR_UNSPECIFIED: Condition.Operator
    OPERATOR_EQUALS: Condition.Operator
    OPERATOR_GREATER_THAN: Condition.Operator
    OPERATOR_GREATER_THAN_OR_EQUAL: Condition.Operator
    OPERATOR_LESS_THAN: Condition.Operator
    OPERATOR_LESS_THAN_OR_EQUAL: Condition.Operator
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    operator: Condition.Operator
    value: str
    def __init__(
        self,
        operator: _Optional[_Union[Condition.Operator, str]] = ...,
        value: _Optional[str] = ...,
    ) -> None: ...

class InternalTimeTrigger(_message.Message):
    __slots__ = ("initial", "every")
    INITIAL_FIELD_NUMBER: _ClassVar[int]
    EVERY_FIELD_NUMBER: _ClassVar[int]
    initial: int
    every: int
    def __init__(
        self, initial: _Optional[int] = ..., every: _Optional[int] = ...
    ) -> None: ...
