from vega import assets_pb2 as _assets_pb2
from vega import data_source_pb2 as _data_source_pb2
from vega import markets_pb2 as _markets_pb2
from vega import vega_pb2 as _vega_pb2
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

class ProposalError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROPOSAL_ERROR_UNSPECIFIED: _ClassVar[ProposalError]
    PROPOSAL_ERROR_CLOSE_TIME_TOO_SOON: _ClassVar[ProposalError]
    PROPOSAL_ERROR_CLOSE_TIME_TOO_LATE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_ENACT_TIME_TOO_SOON: _ClassVar[ProposalError]
    PROPOSAL_ERROR_ENACT_TIME_TOO_LATE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INSUFFICIENT_TOKENS: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_INSTRUMENT_SECURITY: _ClassVar[ProposalError]
    PROPOSAL_ERROR_NO_PRODUCT: _ClassVar[ProposalError]
    PROPOSAL_ERROR_UNSUPPORTED_PRODUCT: _ClassVar[ProposalError]
    PROPOSAL_ERROR_NO_TRADING_MODE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_UNSUPPORTED_TRADING_MODE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_NODE_VALIDATION_FAILED: _ClassVar[ProposalError]
    PROPOSAL_ERROR_MISSING_BUILTIN_ASSET_FIELD: _ClassVar[ProposalError]
    PROPOSAL_ERROR_MISSING_ERC20_CONTRACT_ADDRESS: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_ASSET: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INCOMPATIBLE_TIMESTAMPS: _ClassVar[ProposalError]
    PROPOSAL_ERROR_NO_RISK_PARAMETERS: _ClassVar[ProposalError]
    PROPOSAL_ERROR_NETWORK_PARAMETER_INVALID_KEY: _ClassVar[ProposalError]
    PROPOSAL_ERROR_NETWORK_PARAMETER_INVALID_VALUE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_NETWORK_PARAMETER_VALIDATION_FAILED: _ClassVar[ProposalError]
    PROPOSAL_ERROR_OPENING_AUCTION_DURATION_TOO_SMALL: _ClassVar[ProposalError]
    PROPOSAL_ERROR_OPENING_AUCTION_DURATION_TOO_LARGE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_COULD_NOT_INSTANTIATE_MARKET: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_FUTURE_PRODUCT: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_RISK_PARAMETER: _ClassVar[ProposalError]
    PROPOSAL_ERROR_MAJORITY_THRESHOLD_NOT_REACHED: _ClassVar[ProposalError]
    PROPOSAL_ERROR_PARTICIPATION_THRESHOLD_NOT_REACHED: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_ASSET_DETAILS: _ClassVar[ProposalError]
    PROPOSAL_ERROR_UNKNOWN_TYPE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_UNKNOWN_RISK_PARAMETER_TYPE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_FREEFORM: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INSUFFICIENT_EQUITY_LIKE_SHARE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_MARKET: _ClassVar[ProposalError]
    PROPOSAL_ERROR_TOO_MANY_MARKET_DECIMAL_PLACES: _ClassVar[ProposalError]
    PROPOSAL_ERROR_TOO_MANY_PRICE_MONITORING_TRIGGERS: _ClassVar[ProposalError]
    PROPOSAL_ERROR_ERC20_ADDRESS_ALREADY_IN_USE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_LP_PRICE_RANGE_NONPOSITIVE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_LP_PRICE_RANGE_TOO_LARGE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_LINEAR_SLIPPAGE_FACTOR_OUT_OF_RANGE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_QUADRATIC_SLIPPAGE_FACTOR_OUT_OF_RANGE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_SPOT: _ClassVar[ProposalError]
    PROPOSAL_ERROR_SPOT_PRODUCT_DISABLED: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_SUCCESSOR_MARKET: _ClassVar[ProposalError]
    PROPOSAL_ERROR_GOVERNANCE_TRANSFER_PROPOSAL_FAILED: _ClassVar[ProposalError]
    PROPOSAL_ERROR_GOVERNANCE_TRANSFER_PROPOSAL_INVALID: _ClassVar[ProposalError]
    PROPOSAL_ERROR_GOVERNANCE_CANCEL_TRANSFER_PROPOSAL_INVALID: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_MARKET_STATE_UPDATE: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_SLA_PARAMS: _ClassVar[ProposalError]
    PROPOSAL_ERROR_MISSING_SLA_PARAMS: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_PERPETUAL_PRODUCT: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_REFERRAL_PROGRAM: _ClassVar[ProposalError]
    PROPOSAL_ERROR_INVALID_VOLUME_DISCOUNT_PROGRAM: _ClassVar[ProposalError]

class MarketStateUpdateType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MARKET_STATE_UPDATE_TYPE_UNSPECIFIED: _ClassVar[MarketStateUpdateType]
    MARKET_STATE_UPDATE_TYPE_TERMINATE: _ClassVar[MarketStateUpdateType]
    MARKET_STATE_UPDATE_TYPE_SUSPEND: _ClassVar[MarketStateUpdateType]
    MARKET_STATE_UPDATE_TYPE_RESUME: _ClassVar[MarketStateUpdateType]

class GovernanceTransferType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GOVERNANCE_TRANSFER_TYPE_UNSPECIFIED: _ClassVar[GovernanceTransferType]
    GOVERNANCE_TRANSFER_TYPE_ALL_OR_NOTHING: _ClassVar[GovernanceTransferType]
    GOVERNANCE_TRANSFER_TYPE_BEST_EFFORT: _ClassVar[GovernanceTransferType]

PROPOSAL_ERROR_UNSPECIFIED: ProposalError
PROPOSAL_ERROR_CLOSE_TIME_TOO_SOON: ProposalError
PROPOSAL_ERROR_CLOSE_TIME_TOO_LATE: ProposalError
PROPOSAL_ERROR_ENACT_TIME_TOO_SOON: ProposalError
PROPOSAL_ERROR_ENACT_TIME_TOO_LATE: ProposalError
PROPOSAL_ERROR_INSUFFICIENT_TOKENS: ProposalError
PROPOSAL_ERROR_INVALID_INSTRUMENT_SECURITY: ProposalError
PROPOSAL_ERROR_NO_PRODUCT: ProposalError
PROPOSAL_ERROR_UNSUPPORTED_PRODUCT: ProposalError
PROPOSAL_ERROR_NO_TRADING_MODE: ProposalError
PROPOSAL_ERROR_UNSUPPORTED_TRADING_MODE: ProposalError
PROPOSAL_ERROR_NODE_VALIDATION_FAILED: ProposalError
PROPOSAL_ERROR_MISSING_BUILTIN_ASSET_FIELD: ProposalError
PROPOSAL_ERROR_MISSING_ERC20_CONTRACT_ADDRESS: ProposalError
PROPOSAL_ERROR_INVALID_ASSET: ProposalError
PROPOSAL_ERROR_INCOMPATIBLE_TIMESTAMPS: ProposalError
PROPOSAL_ERROR_NO_RISK_PARAMETERS: ProposalError
PROPOSAL_ERROR_NETWORK_PARAMETER_INVALID_KEY: ProposalError
PROPOSAL_ERROR_NETWORK_PARAMETER_INVALID_VALUE: ProposalError
PROPOSAL_ERROR_NETWORK_PARAMETER_VALIDATION_FAILED: ProposalError
PROPOSAL_ERROR_OPENING_AUCTION_DURATION_TOO_SMALL: ProposalError
PROPOSAL_ERROR_OPENING_AUCTION_DURATION_TOO_LARGE: ProposalError
PROPOSAL_ERROR_COULD_NOT_INSTANTIATE_MARKET: ProposalError
PROPOSAL_ERROR_INVALID_FUTURE_PRODUCT: ProposalError
PROPOSAL_ERROR_INVALID_RISK_PARAMETER: ProposalError
PROPOSAL_ERROR_MAJORITY_THRESHOLD_NOT_REACHED: ProposalError
PROPOSAL_ERROR_PARTICIPATION_THRESHOLD_NOT_REACHED: ProposalError
PROPOSAL_ERROR_INVALID_ASSET_DETAILS: ProposalError
PROPOSAL_ERROR_UNKNOWN_TYPE: ProposalError
PROPOSAL_ERROR_UNKNOWN_RISK_PARAMETER_TYPE: ProposalError
PROPOSAL_ERROR_INVALID_FREEFORM: ProposalError
PROPOSAL_ERROR_INSUFFICIENT_EQUITY_LIKE_SHARE: ProposalError
PROPOSAL_ERROR_INVALID_MARKET: ProposalError
PROPOSAL_ERROR_TOO_MANY_MARKET_DECIMAL_PLACES: ProposalError
PROPOSAL_ERROR_TOO_MANY_PRICE_MONITORING_TRIGGERS: ProposalError
PROPOSAL_ERROR_ERC20_ADDRESS_ALREADY_IN_USE: ProposalError
PROPOSAL_ERROR_LP_PRICE_RANGE_NONPOSITIVE: ProposalError
PROPOSAL_ERROR_LP_PRICE_RANGE_TOO_LARGE: ProposalError
PROPOSAL_ERROR_LINEAR_SLIPPAGE_FACTOR_OUT_OF_RANGE: ProposalError
PROPOSAL_ERROR_QUADRATIC_SLIPPAGE_FACTOR_OUT_OF_RANGE: ProposalError
PROPOSAL_ERROR_INVALID_SPOT: ProposalError
PROPOSAL_ERROR_SPOT_PRODUCT_DISABLED: ProposalError
PROPOSAL_ERROR_INVALID_SUCCESSOR_MARKET: ProposalError
PROPOSAL_ERROR_GOVERNANCE_TRANSFER_PROPOSAL_FAILED: ProposalError
PROPOSAL_ERROR_GOVERNANCE_TRANSFER_PROPOSAL_INVALID: ProposalError
PROPOSAL_ERROR_GOVERNANCE_CANCEL_TRANSFER_PROPOSAL_INVALID: ProposalError
PROPOSAL_ERROR_INVALID_MARKET_STATE_UPDATE: ProposalError
PROPOSAL_ERROR_INVALID_SLA_PARAMS: ProposalError
PROPOSAL_ERROR_MISSING_SLA_PARAMS: ProposalError
PROPOSAL_ERROR_INVALID_PERPETUAL_PRODUCT: ProposalError
PROPOSAL_ERROR_INVALID_REFERRAL_PROGRAM: ProposalError
PROPOSAL_ERROR_INVALID_VOLUME_DISCOUNT_PROGRAM: ProposalError
MARKET_STATE_UPDATE_TYPE_UNSPECIFIED: MarketStateUpdateType
MARKET_STATE_UPDATE_TYPE_TERMINATE: MarketStateUpdateType
MARKET_STATE_UPDATE_TYPE_SUSPEND: MarketStateUpdateType
MARKET_STATE_UPDATE_TYPE_RESUME: MarketStateUpdateType
GOVERNANCE_TRANSFER_TYPE_UNSPECIFIED: GovernanceTransferType
GOVERNANCE_TRANSFER_TYPE_ALL_OR_NOTHING: GovernanceTransferType
GOVERNANCE_TRANSFER_TYPE_BEST_EFFORT: GovernanceTransferType

class SpotProduct(_message.Message):
    __slots__ = ("base_asset", "quote_asset", "name")
    BASE_ASSET_FIELD_NUMBER: _ClassVar[int]
    QUOTE_ASSET_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    base_asset: str
    quote_asset: str
    name: str
    def __init__(
        self,
        base_asset: _Optional[str] = ...,
        quote_asset: _Optional[str] = ...,
        name: _Optional[str] = ...,
    ) -> None: ...

class FutureProduct(_message.Message):
    __slots__ = (
        "settlement_asset",
        "quote_name",
        "data_source_spec_for_settlement_data",
        "data_source_spec_for_trading_termination",
        "data_source_spec_binding",
    )
    SETTLEMENT_ASSET_FIELD_NUMBER: _ClassVar[int]
    QUOTE_NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_FOR_SETTLEMENT_DATA_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_FOR_TRADING_TERMINATION_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_BINDING_FIELD_NUMBER: _ClassVar[int]
    settlement_asset: str
    quote_name: str
    data_source_spec_for_settlement_data: _data_source_pb2.DataSourceDefinition
    data_source_spec_for_trading_termination: _data_source_pb2.DataSourceDefinition
    data_source_spec_binding: _markets_pb2.DataSourceSpecToFutureBinding
    def __init__(
        self,
        settlement_asset: _Optional[str] = ...,
        quote_name: _Optional[str] = ...,
        data_source_spec_for_settlement_data: _Optional[
            _Union[_data_source_pb2.DataSourceDefinition, _Mapping]
        ] = ...,
        data_source_spec_for_trading_termination: _Optional[
            _Union[_data_source_pb2.DataSourceDefinition, _Mapping]
        ] = ...,
        data_source_spec_binding: _Optional[
            _Union[_markets_pb2.DataSourceSpecToFutureBinding, _Mapping]
        ] = ...,
    ) -> None: ...

class PerpetualProduct(_message.Message):
    __slots__ = (
        "settlement_asset",
        "quote_name",
        "margin_funding_factor",
        "interest_rate",
        "clamp_lower_bound",
        "clamp_upper_bound",
        "data_source_spec_for_settlement_schedule",
        "data_source_spec_for_settlement_data",
        "data_source_spec_binding",
    )
    SETTLEMENT_ASSET_FIELD_NUMBER: _ClassVar[int]
    QUOTE_NAME_FIELD_NUMBER: _ClassVar[int]
    MARGIN_FUNDING_FACTOR_FIELD_NUMBER: _ClassVar[int]
    INTEREST_RATE_FIELD_NUMBER: _ClassVar[int]
    CLAMP_LOWER_BOUND_FIELD_NUMBER: _ClassVar[int]
    CLAMP_UPPER_BOUND_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_FOR_SETTLEMENT_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_FOR_SETTLEMENT_DATA_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_BINDING_FIELD_NUMBER: _ClassVar[int]
    settlement_asset: str
    quote_name: str
    margin_funding_factor: str
    interest_rate: str
    clamp_lower_bound: str
    clamp_upper_bound: str
    data_source_spec_for_settlement_schedule: _data_source_pb2.DataSourceDefinition
    data_source_spec_for_settlement_data: _data_source_pb2.DataSourceDefinition
    data_source_spec_binding: _markets_pb2.DataSourceSpecToPerpetualBinding
    def __init__(
        self,
        settlement_asset: _Optional[str] = ...,
        quote_name: _Optional[str] = ...,
        margin_funding_factor: _Optional[str] = ...,
        interest_rate: _Optional[str] = ...,
        clamp_lower_bound: _Optional[str] = ...,
        clamp_upper_bound: _Optional[str] = ...,
        data_source_spec_for_settlement_schedule: _Optional[
            _Union[_data_source_pb2.DataSourceDefinition, _Mapping]
        ] = ...,
        data_source_spec_for_settlement_data: _Optional[
            _Union[_data_source_pb2.DataSourceDefinition, _Mapping]
        ] = ...,
        data_source_spec_binding: _Optional[
            _Union[_markets_pb2.DataSourceSpecToPerpetualBinding, _Mapping]
        ] = ...,
    ) -> None: ...

class InstrumentConfiguration(_message.Message):
    __slots__ = ("name", "code", "future", "spot", "perpetual")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    FUTURE_FIELD_NUMBER: _ClassVar[int]
    SPOT_FIELD_NUMBER: _ClassVar[int]
    PERPETUAL_FIELD_NUMBER: _ClassVar[int]
    name: str
    code: str
    future: FutureProduct
    spot: SpotProduct
    perpetual: PerpetualProduct
    def __init__(
        self,
        name: _Optional[str] = ...,
        code: _Optional[str] = ...,
        future: _Optional[_Union[FutureProduct, _Mapping]] = ...,
        spot: _Optional[_Union[SpotProduct, _Mapping]] = ...,
        perpetual: _Optional[_Union[PerpetualProduct, _Mapping]] = ...,
    ) -> None: ...

class NewSpotMarketConfiguration(_message.Message):
    __slots__ = (
        "instrument",
        "decimal_places",
        "metadata",
        "price_monitoring_parameters",
        "target_stake_parameters",
        "simple",
        "log_normal",
        "position_decimal_places",
        "sla_params",
    )
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    DECIMAL_PLACES_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PRICE_MONITORING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    TARGET_STAKE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_FIELD_NUMBER: _ClassVar[int]
    LOG_NORMAL_FIELD_NUMBER: _ClassVar[int]
    POSITION_DECIMAL_PLACES_FIELD_NUMBER: _ClassVar[int]
    SLA_PARAMS_FIELD_NUMBER: _ClassVar[int]
    instrument: InstrumentConfiguration
    decimal_places: int
    metadata: _containers.RepeatedScalarFieldContainer[str]
    price_monitoring_parameters: _markets_pb2.PriceMonitoringParameters
    target_stake_parameters: _markets_pb2.TargetStakeParameters
    simple: _markets_pb2.SimpleModelParams
    log_normal: _markets_pb2.LogNormalRiskModel
    position_decimal_places: int
    sla_params: _markets_pb2.LiquiditySLAParameters
    def __init__(
        self,
        instrument: _Optional[_Union[InstrumentConfiguration, _Mapping]] = ...,
        decimal_places: _Optional[int] = ...,
        metadata: _Optional[_Iterable[str]] = ...,
        price_monitoring_parameters: _Optional[
            _Union[_markets_pb2.PriceMonitoringParameters, _Mapping]
        ] = ...,
        target_stake_parameters: _Optional[
            _Union[_markets_pb2.TargetStakeParameters, _Mapping]
        ] = ...,
        simple: _Optional[_Union[_markets_pb2.SimpleModelParams, _Mapping]] = ...,
        log_normal: _Optional[_Union[_markets_pb2.LogNormalRiskModel, _Mapping]] = ...,
        position_decimal_places: _Optional[int] = ...,
        sla_params: _Optional[
            _Union[_markets_pb2.LiquiditySLAParameters, _Mapping]
        ] = ...,
    ) -> None: ...

class NewMarketConfiguration(_message.Message):
    __slots__ = (
        "instrument",
        "decimal_places",
        "metadata",
        "price_monitoring_parameters",
        "liquidity_monitoring_parameters",
        "simple",
        "log_normal",
        "position_decimal_places",
        "lp_price_range",
        "linear_slippage_factor",
        "quadratic_slippage_factor",
        "successor",
        "liquidity_sla_parameters",
    )
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    DECIMAL_PLACES_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PRICE_MONITORING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_MONITORING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_FIELD_NUMBER: _ClassVar[int]
    LOG_NORMAL_FIELD_NUMBER: _ClassVar[int]
    POSITION_DECIMAL_PLACES_FIELD_NUMBER: _ClassVar[int]
    LP_PRICE_RANGE_FIELD_NUMBER: _ClassVar[int]
    LINEAR_SLIPPAGE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    QUADRATIC_SLIPPAGE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    SUCCESSOR_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_SLA_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    instrument: InstrumentConfiguration
    decimal_places: int
    metadata: _containers.RepeatedScalarFieldContainer[str]
    price_monitoring_parameters: _markets_pb2.PriceMonitoringParameters
    liquidity_monitoring_parameters: _markets_pb2.LiquidityMonitoringParameters
    simple: _markets_pb2.SimpleModelParams
    log_normal: _markets_pb2.LogNormalRiskModel
    position_decimal_places: int
    lp_price_range: str
    linear_slippage_factor: str
    quadratic_slippage_factor: str
    successor: SuccessorConfiguration
    liquidity_sla_parameters: _markets_pb2.LiquiditySLAParameters
    def __init__(
        self,
        instrument: _Optional[_Union[InstrumentConfiguration, _Mapping]] = ...,
        decimal_places: _Optional[int] = ...,
        metadata: _Optional[_Iterable[str]] = ...,
        price_monitoring_parameters: _Optional[
            _Union[_markets_pb2.PriceMonitoringParameters, _Mapping]
        ] = ...,
        liquidity_monitoring_parameters: _Optional[
            _Union[_markets_pb2.LiquidityMonitoringParameters, _Mapping]
        ] = ...,
        simple: _Optional[_Union[_markets_pb2.SimpleModelParams, _Mapping]] = ...,
        log_normal: _Optional[_Union[_markets_pb2.LogNormalRiskModel, _Mapping]] = ...,
        position_decimal_places: _Optional[int] = ...,
        lp_price_range: _Optional[str] = ...,
        linear_slippage_factor: _Optional[str] = ...,
        quadratic_slippage_factor: _Optional[str] = ...,
        successor: _Optional[_Union[SuccessorConfiguration, _Mapping]] = ...,
        liquidity_sla_parameters: _Optional[
            _Union[_markets_pb2.LiquiditySLAParameters, _Mapping]
        ] = ...,
    ) -> None: ...

class NewSpotMarket(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: NewSpotMarketConfiguration
    def __init__(
        self, changes: _Optional[_Union[NewSpotMarketConfiguration, _Mapping]] = ...
    ) -> None: ...

class SuccessorConfiguration(_message.Message):
    __slots__ = ("parent_market_id", "insurance_pool_fraction")
    PARENT_MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    INSURANCE_POOL_FRACTION_FIELD_NUMBER: _ClassVar[int]
    parent_market_id: str
    insurance_pool_fraction: str
    def __init__(
        self,
        parent_market_id: _Optional[str] = ...,
        insurance_pool_fraction: _Optional[str] = ...,
    ) -> None: ...

class NewMarket(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: NewMarketConfiguration
    def __init__(
        self, changes: _Optional[_Union[NewMarketConfiguration, _Mapping]] = ...
    ) -> None: ...

class UpdateMarket(_message.Message):
    __slots__ = ("market_id", "changes")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    changes: UpdateMarketConfiguration
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        changes: _Optional[_Union[UpdateMarketConfiguration, _Mapping]] = ...,
    ) -> None: ...

class UpdateSpotMarket(_message.Message):
    __slots__ = ("market_id", "changes")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    changes: UpdateSpotMarketConfiguration
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        changes: _Optional[_Union[UpdateSpotMarketConfiguration, _Mapping]] = ...,
    ) -> None: ...

class UpdateMarketConfiguration(_message.Message):
    __slots__ = (
        "instrument",
        "metadata",
        "price_monitoring_parameters",
        "liquidity_monitoring_parameters",
        "simple",
        "log_normal",
        "lp_price_range",
        "linear_slippage_factor",
        "quadratic_slippage_factor",
        "liquidity_sla_parameters",
    )
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PRICE_MONITORING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_MONITORING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_FIELD_NUMBER: _ClassVar[int]
    LOG_NORMAL_FIELD_NUMBER: _ClassVar[int]
    LP_PRICE_RANGE_FIELD_NUMBER: _ClassVar[int]
    LINEAR_SLIPPAGE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    QUADRATIC_SLIPPAGE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_SLA_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    instrument: UpdateInstrumentConfiguration
    metadata: _containers.RepeatedScalarFieldContainer[str]
    price_monitoring_parameters: _markets_pb2.PriceMonitoringParameters
    liquidity_monitoring_parameters: _markets_pb2.LiquidityMonitoringParameters
    simple: _markets_pb2.SimpleModelParams
    log_normal: _markets_pb2.LogNormalRiskModel
    lp_price_range: str
    linear_slippage_factor: str
    quadratic_slippage_factor: str
    liquidity_sla_parameters: _markets_pb2.LiquiditySLAParameters
    def __init__(
        self,
        instrument: _Optional[_Union[UpdateInstrumentConfiguration, _Mapping]] = ...,
        metadata: _Optional[_Iterable[str]] = ...,
        price_monitoring_parameters: _Optional[
            _Union[_markets_pb2.PriceMonitoringParameters, _Mapping]
        ] = ...,
        liquidity_monitoring_parameters: _Optional[
            _Union[_markets_pb2.LiquidityMonitoringParameters, _Mapping]
        ] = ...,
        simple: _Optional[_Union[_markets_pb2.SimpleModelParams, _Mapping]] = ...,
        log_normal: _Optional[_Union[_markets_pb2.LogNormalRiskModel, _Mapping]] = ...,
        lp_price_range: _Optional[str] = ...,
        linear_slippage_factor: _Optional[str] = ...,
        quadratic_slippage_factor: _Optional[str] = ...,
        liquidity_sla_parameters: _Optional[
            _Union[_markets_pb2.LiquiditySLAParameters, _Mapping]
        ] = ...,
    ) -> None: ...

class UpdateSpotMarketConfiguration(_message.Message):
    __slots__ = (
        "metadata",
        "price_monitoring_parameters",
        "target_stake_parameters",
        "simple",
        "log_normal",
        "sla_params",
    )
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PRICE_MONITORING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    TARGET_STAKE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_FIELD_NUMBER: _ClassVar[int]
    LOG_NORMAL_FIELD_NUMBER: _ClassVar[int]
    SLA_PARAMS_FIELD_NUMBER: _ClassVar[int]
    metadata: _containers.RepeatedScalarFieldContainer[str]
    price_monitoring_parameters: _markets_pb2.PriceMonitoringParameters
    target_stake_parameters: _markets_pb2.TargetStakeParameters
    simple: _markets_pb2.SimpleModelParams
    log_normal: _markets_pb2.LogNormalRiskModel
    sla_params: _markets_pb2.LiquiditySLAParameters
    def __init__(
        self,
        metadata: _Optional[_Iterable[str]] = ...,
        price_monitoring_parameters: _Optional[
            _Union[_markets_pb2.PriceMonitoringParameters, _Mapping]
        ] = ...,
        target_stake_parameters: _Optional[
            _Union[_markets_pb2.TargetStakeParameters, _Mapping]
        ] = ...,
        simple: _Optional[_Union[_markets_pb2.SimpleModelParams, _Mapping]] = ...,
        log_normal: _Optional[_Union[_markets_pb2.LogNormalRiskModel, _Mapping]] = ...,
        sla_params: _Optional[
            _Union[_markets_pb2.LiquiditySLAParameters, _Mapping]
        ] = ...,
    ) -> None: ...

class UpdateInstrumentConfiguration(_message.Message):
    __slots__ = ("code", "future", "perpetual")
    CODE_FIELD_NUMBER: _ClassVar[int]
    FUTURE_FIELD_NUMBER: _ClassVar[int]
    PERPETUAL_FIELD_NUMBER: _ClassVar[int]
    code: str
    future: UpdateFutureProduct
    perpetual: UpdatePerpetualProduct
    def __init__(
        self,
        code: _Optional[str] = ...,
        future: _Optional[_Union[UpdateFutureProduct, _Mapping]] = ...,
        perpetual: _Optional[_Union[UpdatePerpetualProduct, _Mapping]] = ...,
    ) -> None: ...

class UpdateFutureProduct(_message.Message):
    __slots__ = (
        "quote_name",
        "data_source_spec_for_settlement_data",
        "data_source_spec_for_trading_termination",
        "data_source_spec_binding",
    )
    QUOTE_NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_FOR_SETTLEMENT_DATA_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_FOR_TRADING_TERMINATION_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_BINDING_FIELD_NUMBER: _ClassVar[int]
    quote_name: str
    data_source_spec_for_settlement_data: _data_source_pb2.DataSourceDefinition
    data_source_spec_for_trading_termination: _data_source_pb2.DataSourceDefinition
    data_source_spec_binding: _markets_pb2.DataSourceSpecToFutureBinding
    def __init__(
        self,
        quote_name: _Optional[str] = ...,
        data_source_spec_for_settlement_data: _Optional[
            _Union[_data_source_pb2.DataSourceDefinition, _Mapping]
        ] = ...,
        data_source_spec_for_trading_termination: _Optional[
            _Union[_data_source_pb2.DataSourceDefinition, _Mapping]
        ] = ...,
        data_source_spec_binding: _Optional[
            _Union[_markets_pb2.DataSourceSpecToFutureBinding, _Mapping]
        ] = ...,
    ) -> None: ...

class UpdatePerpetualProduct(_message.Message):
    __slots__ = (
        "quote_name",
        "margin_funding_factor",
        "interest_rate",
        "clamp_lower_bound",
        "clamp_upper_bound",
        "data_source_spec_for_settlement_schedule",
        "data_source_spec_for_settlement_data",
        "data_source_spec_binding",
    )
    QUOTE_NAME_FIELD_NUMBER: _ClassVar[int]
    MARGIN_FUNDING_FACTOR_FIELD_NUMBER: _ClassVar[int]
    INTEREST_RATE_FIELD_NUMBER: _ClassVar[int]
    CLAMP_LOWER_BOUND_FIELD_NUMBER: _ClassVar[int]
    CLAMP_UPPER_BOUND_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_FOR_SETTLEMENT_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_FOR_SETTLEMENT_DATA_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_BINDING_FIELD_NUMBER: _ClassVar[int]
    quote_name: str
    margin_funding_factor: str
    interest_rate: str
    clamp_lower_bound: str
    clamp_upper_bound: str
    data_source_spec_for_settlement_schedule: _data_source_pb2.DataSourceDefinition
    data_source_spec_for_settlement_data: _data_source_pb2.DataSourceDefinition
    data_source_spec_binding: _markets_pb2.DataSourceSpecToPerpetualBinding
    def __init__(
        self,
        quote_name: _Optional[str] = ...,
        margin_funding_factor: _Optional[str] = ...,
        interest_rate: _Optional[str] = ...,
        clamp_lower_bound: _Optional[str] = ...,
        clamp_upper_bound: _Optional[str] = ...,
        data_source_spec_for_settlement_schedule: _Optional[
            _Union[_data_source_pb2.DataSourceDefinition, _Mapping]
        ] = ...,
        data_source_spec_for_settlement_data: _Optional[
            _Union[_data_source_pb2.DataSourceDefinition, _Mapping]
        ] = ...,
        data_source_spec_binding: _Optional[
            _Union[_markets_pb2.DataSourceSpecToPerpetualBinding, _Mapping]
        ] = ...,
    ) -> None: ...

class UpdateNetworkParameter(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: _vega_pb2.NetworkParameter
    def __init__(
        self, changes: _Optional[_Union[_vega_pb2.NetworkParameter, _Mapping]] = ...
    ) -> None: ...

class NewAsset(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: _assets_pb2.AssetDetails
    def __init__(
        self, changes: _Optional[_Union[_assets_pb2.AssetDetails, _Mapping]] = ...
    ) -> None: ...

class UpdateAsset(_message.Message):
    __slots__ = ("asset_id", "changes")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    changes: _assets_pb2.AssetDetailsUpdate
    def __init__(
        self,
        asset_id: _Optional[str] = ...,
        changes: _Optional[_Union[_assets_pb2.AssetDetailsUpdate, _Mapping]] = ...,
    ) -> None: ...

class NewFreeform(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ProposalTerms(_message.Message):
    __slots__ = (
        "closing_timestamp",
        "enactment_timestamp",
        "validation_timestamp",
        "update_market",
        "new_market",
        "update_network_parameter",
        "new_asset",
        "new_freeform",
        "update_asset",
        "new_spot_market",
        "update_spot_market",
        "new_transfer",
        "cancel_transfer",
        "update_market_state",
        "update_referral_program",
        "update_volume_discount_program",
    )
    CLOSING_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ENACTMENT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MARKET_FIELD_NUMBER: _ClassVar[int]
    NEW_MARKET_FIELD_NUMBER: _ClassVar[int]
    UPDATE_NETWORK_PARAMETER_FIELD_NUMBER: _ClassVar[int]
    NEW_ASSET_FIELD_NUMBER: _ClassVar[int]
    NEW_FREEFORM_FIELD_NUMBER: _ClassVar[int]
    UPDATE_ASSET_FIELD_NUMBER: _ClassVar[int]
    NEW_SPOT_MARKET_FIELD_NUMBER: _ClassVar[int]
    UPDATE_SPOT_MARKET_FIELD_NUMBER: _ClassVar[int]
    NEW_TRANSFER_FIELD_NUMBER: _ClassVar[int]
    CANCEL_TRANSFER_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MARKET_STATE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_REFERRAL_PROGRAM_FIELD_NUMBER: _ClassVar[int]
    UPDATE_VOLUME_DISCOUNT_PROGRAM_FIELD_NUMBER: _ClassVar[int]
    closing_timestamp: int
    enactment_timestamp: int
    validation_timestamp: int
    update_market: UpdateMarket
    new_market: NewMarket
    update_network_parameter: UpdateNetworkParameter
    new_asset: NewAsset
    new_freeform: NewFreeform
    update_asset: UpdateAsset
    new_spot_market: NewSpotMarket
    update_spot_market: UpdateSpotMarket
    new_transfer: NewTransfer
    cancel_transfer: CancelTransfer
    update_market_state: UpdateMarketState
    update_referral_program: UpdateReferralProgram
    update_volume_discount_program: UpdateVolumeDiscountProgram
    def __init__(
        self,
        closing_timestamp: _Optional[int] = ...,
        enactment_timestamp: _Optional[int] = ...,
        validation_timestamp: _Optional[int] = ...,
        update_market: _Optional[_Union[UpdateMarket, _Mapping]] = ...,
        new_market: _Optional[_Union[NewMarket, _Mapping]] = ...,
        update_network_parameter: _Optional[
            _Union[UpdateNetworkParameter, _Mapping]
        ] = ...,
        new_asset: _Optional[_Union[NewAsset, _Mapping]] = ...,
        new_freeform: _Optional[_Union[NewFreeform, _Mapping]] = ...,
        update_asset: _Optional[_Union[UpdateAsset, _Mapping]] = ...,
        new_spot_market: _Optional[_Union[NewSpotMarket, _Mapping]] = ...,
        update_spot_market: _Optional[_Union[UpdateSpotMarket, _Mapping]] = ...,
        new_transfer: _Optional[_Union[NewTransfer, _Mapping]] = ...,
        cancel_transfer: _Optional[_Union[CancelTransfer, _Mapping]] = ...,
        update_market_state: _Optional[_Union[UpdateMarketState, _Mapping]] = ...,
        update_referral_program: _Optional[
            _Union[UpdateReferralProgram, _Mapping]
        ] = ...,
        update_volume_discount_program: _Optional[
            _Union[UpdateVolumeDiscountProgram, _Mapping]
        ] = ...,
    ) -> None: ...

class ProposalRationale(_message.Message):
    __slots__ = ("description", "title")
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    description: str
    title: str
    def __init__(
        self, description: _Optional[str] = ..., title: _Optional[str] = ...
    ) -> None: ...

class GovernanceData(_message.Message):
    __slots__ = ("proposal", "yes", "no", "yes_party", "no_party")

    class YesPartyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Vote
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[_Union[Vote, _Mapping]] = ...,
        ) -> None: ...

    class NoPartyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Vote
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[_Union[Vote, _Mapping]] = ...,
        ) -> None: ...
    PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    YES_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    YES_PARTY_FIELD_NUMBER: _ClassVar[int]
    NO_PARTY_FIELD_NUMBER: _ClassVar[int]
    proposal: Proposal
    yes: _containers.RepeatedCompositeFieldContainer[Vote]
    no: _containers.RepeatedCompositeFieldContainer[Vote]
    yes_party: _containers.MessageMap[str, Vote]
    no_party: _containers.MessageMap[str, Vote]
    def __init__(
        self,
        proposal: _Optional[_Union[Proposal, _Mapping]] = ...,
        yes: _Optional[_Iterable[_Union[Vote, _Mapping]]] = ...,
        no: _Optional[_Iterable[_Union[Vote, _Mapping]]] = ...,
        yes_party: _Optional[_Mapping[str, Vote]] = ...,
        no_party: _Optional[_Mapping[str, Vote]] = ...,
    ) -> None: ...

class Proposal(_message.Message):
    __slots__ = (
        "id",
        "reference",
        "party_id",
        "state",
        "timestamp",
        "terms",
        "reason",
        "error_details",
        "rationale",
        "required_participation",
        "required_majority",
        "required_liquidity_provider_participation",
        "required_liquidity_provider_majority",
    )

    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATE_UNSPECIFIED: _ClassVar[Proposal.State]
        STATE_FAILED: _ClassVar[Proposal.State]
        STATE_OPEN: _ClassVar[Proposal.State]
        STATE_PASSED: _ClassVar[Proposal.State]
        STATE_REJECTED: _ClassVar[Proposal.State]
        STATE_DECLINED: _ClassVar[Proposal.State]
        STATE_ENACTED: _ClassVar[Proposal.State]
        STATE_WAITING_FOR_NODE_VOTE: _ClassVar[Proposal.State]
    STATE_UNSPECIFIED: Proposal.State
    STATE_FAILED: Proposal.State
    STATE_OPEN: Proposal.State
    STATE_PASSED: Proposal.State
    STATE_REJECTED: Proposal.State
    STATE_DECLINED: Proposal.State
    STATE_ENACTED: Proposal.State
    STATE_WAITING_FOR_NODE_VOTE: Proposal.State
    ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TERMS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    ERROR_DETAILS_FIELD_NUMBER: _ClassVar[int]
    RATIONALE_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_PARTICIPATION_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_MAJORITY_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_LIQUIDITY_PROVIDER_PARTICIPATION_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_LIQUIDITY_PROVIDER_MAJORITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    reference: str
    party_id: str
    state: Proposal.State
    timestamp: int
    terms: ProposalTerms
    reason: ProposalError
    error_details: str
    rationale: ProposalRationale
    required_participation: str
    required_majority: str
    required_liquidity_provider_participation: str
    required_liquidity_provider_majority: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        reference: _Optional[str] = ...,
        party_id: _Optional[str] = ...,
        state: _Optional[_Union[Proposal.State, str]] = ...,
        timestamp: _Optional[int] = ...,
        terms: _Optional[_Union[ProposalTerms, _Mapping]] = ...,
        reason: _Optional[_Union[ProposalError, str]] = ...,
        error_details: _Optional[str] = ...,
        rationale: _Optional[_Union[ProposalRationale, _Mapping]] = ...,
        required_participation: _Optional[str] = ...,
        required_majority: _Optional[str] = ...,
        required_liquidity_provider_participation: _Optional[str] = ...,
        required_liquidity_provider_majority: _Optional[str] = ...,
    ) -> None: ...

class Vote(_message.Message):
    __slots__ = (
        "party_id",
        "value",
        "proposal_id",
        "timestamp",
        "total_governance_token_balance",
        "total_governance_token_weight",
        "total_equity_like_share_weight",
    )

    class Value(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        VALUE_UNSPECIFIED: _ClassVar[Vote.Value]
        VALUE_NO: _ClassVar[Vote.Value]
        VALUE_YES: _ClassVar[Vote.Value]
    VALUE_UNSPECIFIED: Vote.Value
    VALUE_NO: Vote.Value
    VALUE_YES: Vote.Value
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    PROPOSAL_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TOTAL_GOVERNANCE_TOKEN_BALANCE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_GOVERNANCE_TOKEN_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_EQUITY_LIKE_SHARE_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    party_id: str
    value: Vote.Value
    proposal_id: str
    timestamp: int
    total_governance_token_balance: str
    total_governance_token_weight: str
    total_equity_like_share_weight: str
    def __init__(
        self,
        party_id: _Optional[str] = ...,
        value: _Optional[_Union[Vote.Value, str]] = ...,
        proposal_id: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
        total_governance_token_balance: _Optional[str] = ...,
        total_governance_token_weight: _Optional[str] = ...,
        total_equity_like_share_weight: _Optional[str] = ...,
    ) -> None: ...

class UpdateVolumeDiscountProgram(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: VolumeDiscountProgramChanges
    def __init__(
        self, changes: _Optional[_Union[VolumeDiscountProgramChanges, _Mapping]] = ...
    ) -> None: ...

class VolumeDiscountProgramChanges(_message.Message):
    __slots__ = ("benefit_tiers", "end_of_program_timestamp", "window_length")
    BENEFIT_TIERS_FIELD_NUMBER: _ClassVar[int]
    END_OF_PROGRAM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WINDOW_LENGTH_FIELD_NUMBER: _ClassVar[int]
    benefit_tiers: _containers.RepeatedCompositeFieldContainer[
        _vega_pb2.VolumeBenefitTier
    ]
    end_of_program_timestamp: int
    window_length: int
    def __init__(
        self,
        benefit_tiers: _Optional[
            _Iterable[_Union[_vega_pb2.VolumeBenefitTier, _Mapping]]
        ] = ...,
        end_of_program_timestamp: _Optional[int] = ...,
        window_length: _Optional[int] = ...,
    ) -> None: ...

class UpdateReferralProgram(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: ReferralProgramChanges
    def __init__(
        self, changes: _Optional[_Union[ReferralProgramChanges, _Mapping]] = ...
    ) -> None: ...

class ReferralProgramChanges(_message.Message):
    __slots__ = (
        "benefit_tiers",
        "end_of_program_timestamp",
        "window_length",
        "staking_tiers",
    )
    BENEFIT_TIERS_FIELD_NUMBER: _ClassVar[int]
    END_OF_PROGRAM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WINDOW_LENGTH_FIELD_NUMBER: _ClassVar[int]
    STAKING_TIERS_FIELD_NUMBER: _ClassVar[int]
    benefit_tiers: _containers.RepeatedCompositeFieldContainer[_vega_pb2.BenefitTier]
    end_of_program_timestamp: int
    window_length: int
    staking_tiers: _containers.RepeatedCompositeFieldContainer[_vega_pb2.StakingTier]
    def __init__(
        self,
        benefit_tiers: _Optional[
            _Iterable[_Union[_vega_pb2.BenefitTier, _Mapping]]
        ] = ...,
        end_of_program_timestamp: _Optional[int] = ...,
        window_length: _Optional[int] = ...,
        staking_tiers: _Optional[
            _Iterable[_Union[_vega_pb2.StakingTier, _Mapping]]
        ] = ...,
    ) -> None: ...

class UpdateMarketState(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: UpdateMarketStateConfiguration
    def __init__(
        self, changes: _Optional[_Union[UpdateMarketStateConfiguration, _Mapping]] = ...
    ) -> None: ...

class UpdateMarketStateConfiguration(_message.Message):
    __slots__ = ("market_id", "update_type", "price")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    update_type: MarketStateUpdateType
    price: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        update_type: _Optional[_Union[MarketStateUpdateType, str]] = ...,
        price: _Optional[str] = ...,
    ) -> None: ...

class CancelTransfer(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: CancelTransferConfiguration
    def __init__(
        self, changes: _Optional[_Union[CancelTransferConfiguration, _Mapping]] = ...
    ) -> None: ...

class CancelTransferConfiguration(_message.Message):
    __slots__ = ("transfer_id",)
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    def __init__(self, transfer_id: _Optional[str] = ...) -> None: ...

class NewTransfer(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: NewTransferConfiguration
    def __init__(
        self, changes: _Optional[_Union[NewTransferConfiguration, _Mapping]] = ...
    ) -> None: ...

class NewTransferConfiguration(_message.Message):
    __slots__ = (
        "source_type",
        "source",
        "transfer_type",
        "amount",
        "asset",
        "fraction_of_balance",
        "destination_type",
        "destination",
        "one_off",
        "recurring",
    )
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_TYPE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    FRACTION_OF_BALANCE_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    ONE_OFF_FIELD_NUMBER: _ClassVar[int]
    RECURRING_FIELD_NUMBER: _ClassVar[int]
    source_type: _vega_pb2.AccountType
    source: str
    transfer_type: GovernanceTransferType
    amount: str
    asset: str
    fraction_of_balance: str
    destination_type: _vega_pb2.AccountType
    destination: str
    one_off: OneOffTransfer
    recurring: RecurringTransfer
    def __init__(
        self,
        source_type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
        source: _Optional[str] = ...,
        transfer_type: _Optional[_Union[GovernanceTransferType, str]] = ...,
        amount: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        fraction_of_balance: _Optional[str] = ...,
        destination_type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
        destination: _Optional[str] = ...,
        one_off: _Optional[_Union[OneOffTransfer, _Mapping]] = ...,
        recurring: _Optional[_Union[RecurringTransfer, _Mapping]] = ...,
    ) -> None: ...

class OneOffTransfer(_message.Message):
    __slots__ = ("deliver_on",)
    DELIVER_ON_FIELD_NUMBER: _ClassVar[int]
    deliver_on: int
    def __init__(self, deliver_on: _Optional[int] = ...) -> None: ...

class RecurringTransfer(_message.Message):
    __slots__ = ("start_epoch", "end_epoch", "dispatch_strategy")
    START_EPOCH_FIELD_NUMBER: _ClassVar[int]
    END_EPOCH_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    start_epoch: int
    end_epoch: int
    dispatch_strategy: _vega_pb2.DispatchStrategy
    def __init__(
        self,
        start_epoch: _Optional[int] = ...,
        end_epoch: _Optional[int] = ...,
        dispatch_strategy: _Optional[
            _Union[_vega_pb2.DispatchStrategy, _Mapping]
        ] = ...,
    ) -> None: ...
