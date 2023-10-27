from google.protobuf import struct_pb2 as _struct_pb2
from vega.data.v1 import data_pb2 as _data_pb2
from vega.data.v1 import spec_pb2 as _spec_pb2
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

class DataSourceDefinition(_message.Message):
    __slots__ = ["internal", "external"]
    INTERNAL_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_FIELD_NUMBER: _ClassVar[int]
    internal: DataSourceDefinitionInternal
    external: DataSourceDefinitionExternal
    def __init__(
        self,
        internal: _Optional[_Union[DataSourceDefinitionInternal, _Mapping]] = ...,
        external: _Optional[_Union[DataSourceDefinitionExternal, _Mapping]] = ...,
    ) -> None: ...

class DataSourceSpecConfigurationTime(_message.Message):
    __slots__ = ["conditions"]
    CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    conditions: _containers.RepeatedCompositeFieldContainer[_spec_pb2.Condition]
    def __init__(
        self,
        conditions: _Optional[_Iterable[_Union[_spec_pb2.Condition, _Mapping]]] = ...,
    ) -> None: ...

class DataSourceSpecConfigurationTimeTrigger(_message.Message):
    __slots__ = ["conditions", "triggers"]
    CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    TRIGGERS_FIELD_NUMBER: _ClassVar[int]
    conditions: _containers.RepeatedCompositeFieldContainer[_spec_pb2.Condition]
    triggers: _containers.RepeatedCompositeFieldContainer[_spec_pb2.InternalTimeTrigger]
    def __init__(
        self,
        conditions: _Optional[_Iterable[_Union[_spec_pb2.Condition, _Mapping]]] = ...,
        triggers: _Optional[
            _Iterable[_Union[_spec_pb2.InternalTimeTrigger, _Mapping]]
        ] = ...,
    ) -> None: ...

class DataSourceDefinitionInternal(_message.Message):
    __slots__ = ["time", "time_trigger"]
    TIME_FIELD_NUMBER: _ClassVar[int]
    TIME_TRIGGER_FIELD_NUMBER: _ClassVar[int]
    time: DataSourceSpecConfigurationTime
    time_trigger: DataSourceSpecConfigurationTimeTrigger
    def __init__(
        self,
        time: _Optional[_Union[DataSourceSpecConfigurationTime, _Mapping]] = ...,
        time_trigger: _Optional[
            _Union[DataSourceSpecConfigurationTimeTrigger, _Mapping]
        ] = ...,
    ) -> None: ...

class DataSourceDefinitionExternal(_message.Message):
    __slots__ = ["oracle", "eth_oracle"]
    ORACLE_FIELD_NUMBER: _ClassVar[int]
    ETH_ORACLE_FIELD_NUMBER: _ClassVar[int]
    oracle: DataSourceSpecConfiguration
    eth_oracle: EthCallSpec
    def __init__(
        self,
        oracle: _Optional[_Union[DataSourceSpecConfiguration, _Mapping]] = ...,
        eth_oracle: _Optional[_Union[EthCallSpec, _Mapping]] = ...,
    ) -> None: ...

class DataSourceSpecConfiguration(_message.Message):
    __slots__ = ["signers", "filters"]
    SIGNERS_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    signers: _containers.RepeatedCompositeFieldContainer[_data_pb2.Signer]
    filters: _containers.RepeatedCompositeFieldContainer[_spec_pb2.Filter]
    def __init__(
        self,
        signers: _Optional[_Iterable[_Union[_data_pb2.Signer, _Mapping]]] = ...,
        filters: _Optional[_Iterable[_Union[_spec_pb2.Filter, _Mapping]]] = ...,
    ) -> None: ...

class EthCallSpec(_message.Message):
    __slots__ = [
        "address",
        "abi",
        "method",
        "args",
        "trigger",
        "required_confirmations",
        "filters",
        "normalisers",
    ]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ABI_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_CONFIRMATIONS_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    NORMALISERS_FIELD_NUMBER: _ClassVar[int]
    address: str
    abi: str
    method: str
    args: _containers.RepeatedCompositeFieldContainer[_struct_pb2.Value]
    trigger: EthCallTrigger
    required_confirmations: int
    filters: _containers.RepeatedCompositeFieldContainer[_spec_pb2.Filter]
    normalisers: _containers.RepeatedCompositeFieldContainer[Normaliser]
    def __init__(
        self,
        address: _Optional[str] = ...,
        abi: _Optional[str] = ...,
        method: _Optional[str] = ...,
        args: _Optional[_Iterable[_Union[_struct_pb2.Value, _Mapping]]] = ...,
        trigger: _Optional[_Union[EthCallTrigger, _Mapping]] = ...,
        required_confirmations: _Optional[int] = ...,
        filters: _Optional[_Iterable[_Union[_spec_pb2.Filter, _Mapping]]] = ...,
        normalisers: _Optional[_Iterable[_Union[Normaliser, _Mapping]]] = ...,
    ) -> None: ...

class Normaliser(_message.Message):
    __slots__ = ["name", "expression"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    name: str
    expression: str
    def __init__(
        self, name: _Optional[str] = ..., expression: _Optional[str] = ...
    ) -> None: ...

class EthCallTrigger(_message.Message):
    __slots__ = ["time_trigger"]
    TIME_TRIGGER_FIELD_NUMBER: _ClassVar[int]
    time_trigger: EthTimeTrigger
    def __init__(
        self, time_trigger: _Optional[_Union[EthTimeTrigger, _Mapping]] = ...
    ) -> None: ...

class EthTimeTrigger(_message.Message):
    __slots__ = ["initial", "every", "until"]
    INITIAL_FIELD_NUMBER: _ClassVar[int]
    EVERY_FIELD_NUMBER: _ClassVar[int]
    UNTIL_FIELD_NUMBER: _ClassVar[int]
    initial: int
    every: int
    until: int
    def __init__(
        self,
        initial: _Optional[int] = ...,
        every: _Optional[int] = ...,
        until: _Optional[int] = ...,
    ) -> None: ...

class DataSourceSpec(_message.Message):
    __slots__ = ["id", "created_at", "updated_at", "data", "status"]

    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        STATUS_UNSPECIFIED: _ClassVar[DataSourceSpec.Status]
        STATUS_ACTIVE: _ClassVar[DataSourceSpec.Status]
        STATUS_DEACTIVATED: _ClassVar[DataSourceSpec.Status]
    STATUS_UNSPECIFIED: DataSourceSpec.Status
    STATUS_ACTIVE: DataSourceSpec.Status
    STATUS_DEACTIVATED: DataSourceSpec.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: int
    updated_at: int
    data: DataSourceDefinition
    status: DataSourceSpec.Status
    def __init__(
        self,
        id: _Optional[str] = ...,
        created_at: _Optional[int] = ...,
        updated_at: _Optional[int] = ...,
        data: _Optional[_Union[DataSourceDefinition, _Mapping]] = ...,
        status: _Optional[_Union[DataSourceSpec.Status, str]] = ...,
    ) -> None: ...

class ExternalDataSourceSpec(_message.Message):
    __slots__ = ["spec"]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    spec: DataSourceSpec
    def __init__(
        self, spec: _Optional[_Union[DataSourceSpec, _Mapping]] = ...
    ) -> None: ...
