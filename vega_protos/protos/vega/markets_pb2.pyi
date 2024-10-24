from vega import data_source_pb2 as _data_source_pb2
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

class CompositePriceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMPOSITE_PRICE_TYPE_UNSPECIFIED: _ClassVar[CompositePriceType]
    COMPOSITE_PRICE_TYPE_WEIGHTED: _ClassVar[CompositePriceType]
    COMPOSITE_PRICE_TYPE_MEDIAN: _ClassVar[CompositePriceType]
    COMPOSITE_PRICE_TYPE_LAST_TRADE: _ClassVar[CompositePriceType]

COMPOSITE_PRICE_TYPE_UNSPECIFIED: CompositePriceType
COMPOSITE_PRICE_TYPE_WEIGHTED: CompositePriceType
COMPOSITE_PRICE_TYPE_MEDIAN: CompositePriceType
COMPOSITE_PRICE_TYPE_LAST_TRADE: CompositePriceType

class AuctionDuration(_message.Message):
    __slots__ = ("duration", "volume")
    DURATION_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    duration: int
    volume: int
    def __init__(
        self, duration: _Optional[int] = ..., volume: _Optional[int] = ...
    ) -> None: ...

class Spot(_message.Message):
    __slots__ = ("base_asset", "quote_asset")
    BASE_ASSET_FIELD_NUMBER: _ClassVar[int]
    QUOTE_ASSET_FIELD_NUMBER: _ClassVar[int]
    base_asset: str
    quote_asset: str
    def __init__(
        self, base_asset: _Optional[str] = ..., quote_asset: _Optional[str] = ...
    ) -> None: ...

class Future(_message.Message):
    __slots__ = (
        "settlement_asset",
        "quote_name",
        "data_source_spec_for_settlement_data",
        "data_source_spec_for_trading_termination",
        "data_source_spec_binding",
        "cap",
    )
    SETTLEMENT_ASSET_FIELD_NUMBER: _ClassVar[int]
    QUOTE_NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_FOR_SETTLEMENT_DATA_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_FOR_TRADING_TERMINATION_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_SPEC_BINDING_FIELD_NUMBER: _ClassVar[int]
    CAP_FIELD_NUMBER: _ClassVar[int]
    settlement_asset: str
    quote_name: str
    data_source_spec_for_settlement_data: _data_source_pb2.DataSourceSpec
    data_source_spec_for_trading_termination: _data_source_pb2.DataSourceSpec
    data_source_spec_binding: DataSourceSpecToFutureBinding
    cap: FutureCap
    def __init__(
        self,
        settlement_asset: _Optional[str] = ...,
        quote_name: _Optional[str] = ...,
        data_source_spec_for_settlement_data: _Optional[
            _Union[_data_source_pb2.DataSourceSpec, _Mapping]
        ] = ...,
        data_source_spec_for_trading_termination: _Optional[
            _Union[_data_source_pb2.DataSourceSpec, _Mapping]
        ] = ...,
        data_source_spec_binding: _Optional[
            _Union[DataSourceSpecToFutureBinding, _Mapping]
        ] = ...,
        cap: _Optional[_Union[FutureCap, _Mapping]] = ...,
    ) -> None: ...

class FutureCap(_message.Message):
    __slots__ = ("max_price", "binary_settlement", "fully_collateralised")
    MAX_PRICE_FIELD_NUMBER: _ClassVar[int]
    BINARY_SETTLEMENT_FIELD_NUMBER: _ClassVar[int]
    FULLY_COLLATERALISED_FIELD_NUMBER: _ClassVar[int]
    max_price: str
    binary_settlement: bool
    fully_collateralised: bool
    def __init__(
        self,
        max_price: _Optional[str] = ...,
        binary_settlement: bool = ...,
        fully_collateralised: bool = ...,
    ) -> None: ...

class Perpetual(_message.Message):
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
        "funding_rate_scaling_factor",
        "funding_rate_lower_bound",
        "funding_rate_upper_bound",
        "internal_composite_price_config",
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
    FUNDING_RATE_SCALING_FACTOR_FIELD_NUMBER: _ClassVar[int]
    FUNDING_RATE_LOWER_BOUND_FIELD_NUMBER: _ClassVar[int]
    FUNDING_RATE_UPPER_BOUND_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_COMPOSITE_PRICE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    settlement_asset: str
    quote_name: str
    margin_funding_factor: str
    interest_rate: str
    clamp_lower_bound: str
    clamp_upper_bound: str
    data_source_spec_for_settlement_schedule: _data_source_pb2.DataSourceSpec
    data_source_spec_for_settlement_data: _data_source_pb2.DataSourceSpec
    data_source_spec_binding: DataSourceSpecToPerpetualBinding
    funding_rate_scaling_factor: str
    funding_rate_lower_bound: str
    funding_rate_upper_bound: str
    internal_composite_price_config: CompositePriceConfiguration
    def __init__(
        self,
        settlement_asset: _Optional[str] = ...,
        quote_name: _Optional[str] = ...,
        margin_funding_factor: _Optional[str] = ...,
        interest_rate: _Optional[str] = ...,
        clamp_lower_bound: _Optional[str] = ...,
        clamp_upper_bound: _Optional[str] = ...,
        data_source_spec_for_settlement_schedule: _Optional[
            _Union[_data_source_pb2.DataSourceSpec, _Mapping]
        ] = ...,
        data_source_spec_for_settlement_data: _Optional[
            _Union[_data_source_pb2.DataSourceSpec, _Mapping]
        ] = ...,
        data_source_spec_binding: _Optional[
            _Union[DataSourceSpecToPerpetualBinding, _Mapping]
        ] = ...,
        funding_rate_scaling_factor: _Optional[str] = ...,
        funding_rate_lower_bound: _Optional[str] = ...,
        funding_rate_upper_bound: _Optional[str] = ...,
        internal_composite_price_config: _Optional[
            _Union[CompositePriceConfiguration, _Mapping]
        ] = ...,
    ) -> None: ...

class DataSourceSpecToFutureBinding(_message.Message):
    __slots__ = ("settlement_data_property", "trading_termination_property")
    SETTLEMENT_DATA_PROPERTY_FIELD_NUMBER: _ClassVar[int]
    TRADING_TERMINATION_PROPERTY_FIELD_NUMBER: _ClassVar[int]
    settlement_data_property: str
    trading_termination_property: str
    def __init__(
        self,
        settlement_data_property: _Optional[str] = ...,
        trading_termination_property: _Optional[str] = ...,
    ) -> None: ...

class DataSourceSpecToPerpetualBinding(_message.Message):
    __slots__ = ("settlement_data_property", "settlement_schedule_property")
    SETTLEMENT_DATA_PROPERTY_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_SCHEDULE_PROPERTY_FIELD_NUMBER: _ClassVar[int]
    settlement_data_property: str
    settlement_schedule_property: str
    def __init__(
        self,
        settlement_data_property: _Optional[str] = ...,
        settlement_schedule_property: _Optional[str] = ...,
    ) -> None: ...

class InstrumentMetadata(_message.Message):
    __slots__ = ("tags",)
    TAGS_FIELD_NUMBER: _ClassVar[int]
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, tags: _Optional[_Iterable[str]] = ...) -> None: ...

class Instrument(_message.Message):
    __slots__ = ("id", "code", "name", "metadata", "future", "spot", "perpetual")
    ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    FUTURE_FIELD_NUMBER: _ClassVar[int]
    SPOT_FIELD_NUMBER: _ClassVar[int]
    PERPETUAL_FIELD_NUMBER: _ClassVar[int]
    id: str
    code: str
    name: str
    metadata: InstrumentMetadata
    future: Future
    spot: Spot
    perpetual: Perpetual
    def __init__(
        self,
        id: _Optional[str] = ...,
        code: _Optional[str] = ...,
        name: _Optional[str] = ...,
        metadata: _Optional[_Union[InstrumentMetadata, _Mapping]] = ...,
        future: _Optional[_Union[Future, _Mapping]] = ...,
        spot: _Optional[_Union[Spot, _Mapping]] = ...,
        perpetual: _Optional[_Union[Perpetual, _Mapping]] = ...,
    ) -> None: ...

class LogNormalRiskModel(_message.Message):
    __slots__ = ("risk_aversion_parameter", "tau", "params", "risk_factor_override")
    RISK_AVERSION_PARAMETER_FIELD_NUMBER: _ClassVar[int]
    TAU_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    RISK_FACTOR_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    risk_aversion_parameter: float
    tau: float
    params: LogNormalModelParams
    risk_factor_override: RiskFactorOverride
    def __init__(
        self,
        risk_aversion_parameter: _Optional[float] = ...,
        tau: _Optional[float] = ...,
        params: _Optional[_Union[LogNormalModelParams, _Mapping]] = ...,
        risk_factor_override: _Optional[_Union[RiskFactorOverride, _Mapping]] = ...,
    ) -> None: ...

class RiskFactorOverride(_message.Message):
    __slots__ = ("short", "long")
    SHORT_FIELD_NUMBER: _ClassVar[int]
    LONG_FIELD_NUMBER: _ClassVar[int]
    short: str
    long: str
    def __init__(
        self, short: _Optional[str] = ..., long: _Optional[str] = ...
    ) -> None: ...

class LogNormalModelParams(_message.Message):
    __slots__ = ("mu", "r", "sigma")
    MU_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    SIGMA_FIELD_NUMBER: _ClassVar[int]
    mu: float
    r: float
    sigma: float
    def __init__(
        self,
        mu: _Optional[float] = ...,
        r: _Optional[float] = ...,
        sigma: _Optional[float] = ...,
    ) -> None: ...

class SimpleRiskModel(_message.Message):
    __slots__ = ("params",)
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    params: SimpleModelParams
    def __init__(
        self, params: _Optional[_Union[SimpleModelParams, _Mapping]] = ...
    ) -> None: ...

class SimpleModelParams(_message.Message):
    __slots__ = (
        "factor_long",
        "factor_short",
        "max_move_up",
        "min_move_down",
        "probability_of_trading",
    )
    FACTOR_LONG_FIELD_NUMBER: _ClassVar[int]
    FACTOR_SHORT_FIELD_NUMBER: _ClassVar[int]
    MAX_MOVE_UP_FIELD_NUMBER: _ClassVar[int]
    MIN_MOVE_DOWN_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_OF_TRADING_FIELD_NUMBER: _ClassVar[int]
    factor_long: float
    factor_short: float
    max_move_up: float
    min_move_down: float
    probability_of_trading: float
    def __init__(
        self,
        factor_long: _Optional[float] = ...,
        factor_short: _Optional[float] = ...,
        max_move_up: _Optional[float] = ...,
        min_move_down: _Optional[float] = ...,
        probability_of_trading: _Optional[float] = ...,
    ) -> None: ...

class ScalingFactors(_message.Message):
    __slots__ = ("search_level", "initial_margin", "collateral_release")
    SEARCH_LEVEL_FIELD_NUMBER: _ClassVar[int]
    INITIAL_MARGIN_FIELD_NUMBER: _ClassVar[int]
    COLLATERAL_RELEASE_FIELD_NUMBER: _ClassVar[int]
    search_level: float
    initial_margin: float
    collateral_release: float
    def __init__(
        self,
        search_level: _Optional[float] = ...,
        initial_margin: _Optional[float] = ...,
        collateral_release: _Optional[float] = ...,
    ) -> None: ...

class MarginCalculator(_message.Message):
    __slots__ = ("scaling_factors", "fully_collateralised")
    SCALING_FACTORS_FIELD_NUMBER: _ClassVar[int]
    FULLY_COLLATERALISED_FIELD_NUMBER: _ClassVar[int]
    scaling_factors: ScalingFactors
    fully_collateralised: bool
    def __init__(
        self,
        scaling_factors: _Optional[_Union[ScalingFactors, _Mapping]] = ...,
        fully_collateralised: bool = ...,
    ) -> None: ...

class TradableInstrument(_message.Message):
    __slots__ = (
        "instrument",
        "margin_calculator",
        "log_normal_risk_model",
        "simple_risk_model",
    )
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    MARGIN_CALCULATOR_FIELD_NUMBER: _ClassVar[int]
    LOG_NORMAL_RISK_MODEL_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_RISK_MODEL_FIELD_NUMBER: _ClassVar[int]
    instrument: Instrument
    margin_calculator: MarginCalculator
    log_normal_risk_model: LogNormalRiskModel
    simple_risk_model: SimpleRiskModel
    def __init__(
        self,
        instrument: _Optional[_Union[Instrument, _Mapping]] = ...,
        margin_calculator: _Optional[_Union[MarginCalculator, _Mapping]] = ...,
        log_normal_risk_model: _Optional[_Union[LogNormalRiskModel, _Mapping]] = ...,
        simple_risk_model: _Optional[_Union[SimpleRiskModel, _Mapping]] = ...,
    ) -> None: ...

class FeeFactors(_message.Message):
    __slots__ = (
        "maker_fee",
        "infrastructure_fee",
        "liquidity_fee",
        "treasury_fee",
        "buy_back_fee",
    )
    MAKER_FEE_FIELD_NUMBER: _ClassVar[int]
    INFRASTRUCTURE_FEE_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_FEE_FIELD_NUMBER: _ClassVar[int]
    TREASURY_FEE_FIELD_NUMBER: _ClassVar[int]
    BUY_BACK_FEE_FIELD_NUMBER: _ClassVar[int]
    maker_fee: str
    infrastructure_fee: str
    liquidity_fee: str
    treasury_fee: str
    buy_back_fee: str
    def __init__(
        self,
        maker_fee: _Optional[str] = ...,
        infrastructure_fee: _Optional[str] = ...,
        liquidity_fee: _Optional[str] = ...,
        treasury_fee: _Optional[str] = ...,
        buy_back_fee: _Optional[str] = ...,
    ) -> None: ...

class Fees(_message.Message):
    __slots__ = ("factors", "liquidity_fee_settings")
    FACTORS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_FEE_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    factors: FeeFactors
    liquidity_fee_settings: LiquidityFeeSettings
    def __init__(
        self,
        factors: _Optional[_Union[FeeFactors, _Mapping]] = ...,
        liquidity_fee_settings: _Optional[_Union[LiquidityFeeSettings, _Mapping]] = ...,
    ) -> None: ...

class PriceMonitoringTrigger(_message.Message):
    __slots__ = ("horizon", "probability", "auction_extension")
    HORIZON_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    AUCTION_EXTENSION_FIELD_NUMBER: _ClassVar[int]
    horizon: int
    probability: str
    auction_extension: int
    def __init__(
        self,
        horizon: _Optional[int] = ...,
        probability: _Optional[str] = ...,
        auction_extension: _Optional[int] = ...,
    ) -> None: ...

class PriceMonitoringParameters(_message.Message):
    __slots__ = ("triggers",)
    TRIGGERS_FIELD_NUMBER: _ClassVar[int]
    triggers: _containers.RepeatedCompositeFieldContainer[PriceMonitoringTrigger]
    def __init__(
        self,
        triggers: _Optional[_Iterable[_Union[PriceMonitoringTrigger, _Mapping]]] = ...,
    ) -> None: ...

class PriceMonitoringSettings(_message.Message):
    __slots__ = ("parameters",)
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    parameters: PriceMonitoringParameters
    def __init__(
        self, parameters: _Optional[_Union[PriceMonitoringParameters, _Mapping]] = ...
    ) -> None: ...

class LiquidityMonitoringParameters(_message.Message):
    __slots__ = ("target_stake_parameters", "triggering_ratio", "auction_extension")
    TARGET_STAKE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    TRIGGERING_RATIO_FIELD_NUMBER: _ClassVar[int]
    AUCTION_EXTENSION_FIELD_NUMBER: _ClassVar[int]
    target_stake_parameters: TargetStakeParameters
    triggering_ratio: str
    auction_extension: int
    def __init__(
        self,
        target_stake_parameters: _Optional[
            _Union[TargetStakeParameters, _Mapping]
        ] = ...,
        triggering_ratio: _Optional[str] = ...,
        auction_extension: _Optional[int] = ...,
    ) -> None: ...

class LiquiditySLAParameters(_message.Message):
    __slots__ = (
        "price_range",
        "commitment_min_time_fraction",
        "performance_hysteresis_epochs",
        "sla_competition_factor",
    )
    PRICE_RANGE_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_MIN_TIME_FRACTION_FIELD_NUMBER: _ClassVar[int]
    PERFORMANCE_HYSTERESIS_EPOCHS_FIELD_NUMBER: _ClassVar[int]
    SLA_COMPETITION_FACTOR_FIELD_NUMBER: _ClassVar[int]
    price_range: str
    commitment_min_time_fraction: str
    performance_hysteresis_epochs: int
    sla_competition_factor: str
    def __init__(
        self,
        price_range: _Optional[str] = ...,
        commitment_min_time_fraction: _Optional[str] = ...,
        performance_hysteresis_epochs: _Optional[int] = ...,
        sla_competition_factor: _Optional[str] = ...,
    ) -> None: ...

class LiquidityFeeSettings(_message.Message):
    __slots__ = ("method", "fee_constant")

    class Method(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        METHOD_UNSPECIFIED: _ClassVar[LiquidityFeeSettings.Method]
        METHOD_MARGINAL_COST: _ClassVar[LiquidityFeeSettings.Method]
        METHOD_WEIGHTED_AVERAGE: _ClassVar[LiquidityFeeSettings.Method]
        METHOD_CONSTANT: _ClassVar[LiquidityFeeSettings.Method]

    METHOD_UNSPECIFIED: LiquidityFeeSettings.Method
    METHOD_MARGINAL_COST: LiquidityFeeSettings.Method
    METHOD_WEIGHTED_AVERAGE: LiquidityFeeSettings.Method
    METHOD_CONSTANT: LiquidityFeeSettings.Method
    METHOD_FIELD_NUMBER: _ClassVar[int]
    FEE_CONSTANT_FIELD_NUMBER: _ClassVar[int]
    method: LiquidityFeeSettings.Method
    fee_constant: str
    def __init__(
        self,
        method: _Optional[_Union[LiquidityFeeSettings.Method, str]] = ...,
        fee_constant: _Optional[str] = ...,
    ) -> None: ...

class TargetStakeParameters(_message.Message):
    __slots__ = ("time_window", "scaling_factor")
    TIME_WINDOW_FIELD_NUMBER: _ClassVar[int]
    SCALING_FACTOR_FIELD_NUMBER: _ClassVar[int]
    time_window: int
    scaling_factor: float
    def __init__(
        self, time_window: _Optional[int] = ..., scaling_factor: _Optional[float] = ...
    ) -> None: ...

class Market(_message.Message):
    __slots__ = (
        "id",
        "tradable_instrument",
        "decimal_places",
        "fees",
        "opening_auction",
        "price_monitoring_settings",
        "liquidity_monitoring_parameters",
        "trading_mode",
        "state",
        "market_timestamps",
        "position_decimal_places",
        "lp_price_range",
        "linear_slippage_factor",
        "quadratic_slippage_factor",
        "parent_market_id",
        "insurance_pool_fraction",
        "successor_market_id",
        "liquidity_sla_params",
        "liquidation_strategy",
        "mark_price_configuration",
        "tick_size",
        "enable_transaction_reordering",
        "allowed_empty_amm_levels",
        "allowed_sellers",
    )

    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATE_UNSPECIFIED: _ClassVar[Market.State]
        STATE_PROPOSED: _ClassVar[Market.State]
        STATE_REJECTED: _ClassVar[Market.State]
        STATE_PENDING: _ClassVar[Market.State]
        STATE_CANCELLED: _ClassVar[Market.State]
        STATE_ACTIVE: _ClassVar[Market.State]
        STATE_SUSPENDED: _ClassVar[Market.State]
        STATE_CLOSED: _ClassVar[Market.State]
        STATE_TRADING_TERMINATED: _ClassVar[Market.State]
        STATE_SETTLED: _ClassVar[Market.State]
        STATE_SUSPENDED_VIA_GOVERNANCE: _ClassVar[Market.State]

    STATE_UNSPECIFIED: Market.State
    STATE_PROPOSED: Market.State
    STATE_REJECTED: Market.State
    STATE_PENDING: Market.State
    STATE_CANCELLED: Market.State
    STATE_ACTIVE: Market.State
    STATE_SUSPENDED: Market.State
    STATE_CLOSED: Market.State
    STATE_TRADING_TERMINATED: Market.State
    STATE_SETTLED: Market.State
    STATE_SUSPENDED_VIA_GOVERNANCE: Market.State

    class TradingMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRADING_MODE_UNSPECIFIED: _ClassVar[Market.TradingMode]
        TRADING_MODE_CONTINUOUS: _ClassVar[Market.TradingMode]
        TRADING_MODE_BATCH_AUCTION: _ClassVar[Market.TradingMode]
        TRADING_MODE_OPENING_AUCTION: _ClassVar[Market.TradingMode]
        TRADING_MODE_MONITORING_AUCTION: _ClassVar[Market.TradingMode]
        TRADING_MODE_NO_TRADING: _ClassVar[Market.TradingMode]
        TRADING_MODE_SUSPENDED_VIA_GOVERNANCE: _ClassVar[Market.TradingMode]
        TRADING_MODE_LONG_BLOCK_AUCTION: _ClassVar[Market.TradingMode]
        TRADING_MODE_PROTOCOL_AUTOMATED_PURCHASE_AUCTION: _ClassVar[Market.TradingMode]

    TRADING_MODE_UNSPECIFIED: Market.TradingMode
    TRADING_MODE_CONTINUOUS: Market.TradingMode
    TRADING_MODE_BATCH_AUCTION: Market.TradingMode
    TRADING_MODE_OPENING_AUCTION: Market.TradingMode
    TRADING_MODE_MONITORING_AUCTION: Market.TradingMode
    TRADING_MODE_NO_TRADING: Market.TradingMode
    TRADING_MODE_SUSPENDED_VIA_GOVERNANCE: Market.TradingMode
    TRADING_MODE_LONG_BLOCK_AUCTION: Market.TradingMode
    TRADING_MODE_PROTOCOL_AUTOMATED_PURCHASE_AUCTION: Market.TradingMode
    ID_FIELD_NUMBER: _ClassVar[int]
    TRADABLE_INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    DECIMAL_PLACES_FIELD_NUMBER: _ClassVar[int]
    FEES_FIELD_NUMBER: _ClassVar[int]
    OPENING_AUCTION_FIELD_NUMBER: _ClassVar[int]
    PRICE_MONITORING_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_MONITORING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    TRADING_MODE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    MARKET_TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    POSITION_DECIMAL_PLACES_FIELD_NUMBER: _ClassVar[int]
    LP_PRICE_RANGE_FIELD_NUMBER: _ClassVar[int]
    LINEAR_SLIPPAGE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    QUADRATIC_SLIPPAGE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    PARENT_MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    INSURANCE_POOL_FRACTION_FIELD_NUMBER: _ClassVar[int]
    SUCCESSOR_MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    LIQUIDITY_SLA_PARAMS_FIELD_NUMBER: _ClassVar[int]
    LIQUIDATION_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    MARK_PRICE_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    TICK_SIZE_FIELD_NUMBER: _ClassVar[int]
    ENABLE_TRANSACTION_REORDERING_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_EMPTY_AMM_LEVELS_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_SELLERS_FIELD_NUMBER: _ClassVar[int]
    id: str
    tradable_instrument: TradableInstrument
    decimal_places: int
    fees: Fees
    opening_auction: AuctionDuration
    price_monitoring_settings: PriceMonitoringSettings
    liquidity_monitoring_parameters: LiquidityMonitoringParameters
    trading_mode: Market.TradingMode
    state: Market.State
    market_timestamps: MarketTimestamps
    position_decimal_places: int
    lp_price_range: str
    linear_slippage_factor: str
    quadratic_slippage_factor: str
    parent_market_id: str
    insurance_pool_fraction: str
    successor_market_id: str
    liquidity_sla_params: LiquiditySLAParameters
    liquidation_strategy: LiquidationStrategy
    mark_price_configuration: CompositePriceConfiguration
    tick_size: str
    enable_transaction_reordering: bool
    allowed_empty_amm_levels: int
    allowed_sellers: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        id: _Optional[str] = ...,
        tradable_instrument: _Optional[_Union[TradableInstrument, _Mapping]] = ...,
        decimal_places: _Optional[int] = ...,
        fees: _Optional[_Union[Fees, _Mapping]] = ...,
        opening_auction: _Optional[_Union[AuctionDuration, _Mapping]] = ...,
        price_monitoring_settings: _Optional[
            _Union[PriceMonitoringSettings, _Mapping]
        ] = ...,
        liquidity_monitoring_parameters: _Optional[
            _Union[LiquidityMonitoringParameters, _Mapping]
        ] = ...,
        trading_mode: _Optional[_Union[Market.TradingMode, str]] = ...,
        state: _Optional[_Union[Market.State, str]] = ...,
        market_timestamps: _Optional[_Union[MarketTimestamps, _Mapping]] = ...,
        position_decimal_places: _Optional[int] = ...,
        lp_price_range: _Optional[str] = ...,
        linear_slippage_factor: _Optional[str] = ...,
        quadratic_slippage_factor: _Optional[str] = ...,
        parent_market_id: _Optional[str] = ...,
        insurance_pool_fraction: _Optional[str] = ...,
        successor_market_id: _Optional[str] = ...,
        liquidity_sla_params: _Optional[_Union[LiquiditySLAParameters, _Mapping]] = ...,
        liquidation_strategy: _Optional[_Union[LiquidationStrategy, _Mapping]] = ...,
        mark_price_configuration: _Optional[
            _Union[CompositePriceConfiguration, _Mapping]
        ] = ...,
        tick_size: _Optional[str] = ...,
        enable_transaction_reordering: bool = ...,
        allowed_empty_amm_levels: _Optional[int] = ...,
        allowed_sellers: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class MarketTimestamps(_message.Message):
    __slots__ = ("proposed", "pending", "open", "close")
    PROPOSED_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    proposed: int
    pending: int
    open: int
    close: int
    def __init__(
        self,
        proposed: _Optional[int] = ...,
        pending: _Optional[int] = ...,
        open: _Optional[int] = ...,
        close: _Optional[int] = ...,
    ) -> None: ...

class LiquidationStrategy(_message.Message):
    __slots__ = (
        "disposal_time_step",
        "disposal_fraction",
        "full_disposal_size",
        "max_fraction_consumed",
        "disposal_slippage_range",
    )
    DISPOSAL_TIME_STEP_FIELD_NUMBER: _ClassVar[int]
    DISPOSAL_FRACTION_FIELD_NUMBER: _ClassVar[int]
    FULL_DISPOSAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    MAX_FRACTION_CONSUMED_FIELD_NUMBER: _ClassVar[int]
    DISPOSAL_SLIPPAGE_RANGE_FIELD_NUMBER: _ClassVar[int]
    disposal_time_step: int
    disposal_fraction: str
    full_disposal_size: int
    max_fraction_consumed: str
    disposal_slippage_range: str
    def __init__(
        self,
        disposal_time_step: _Optional[int] = ...,
        disposal_fraction: _Optional[str] = ...,
        full_disposal_size: _Optional[int] = ...,
        max_fraction_consumed: _Optional[str] = ...,
        disposal_slippage_range: _Optional[str] = ...,
    ) -> None: ...

class CompositePriceConfiguration(_message.Message):
    __slots__ = (
        "decay_weight",
        "decay_power",
        "cash_amount",
        "source_weights",
        "source_staleness_tolerance",
        "composite_price_type",
        "data_sources_spec",
        "data_sources_spec_binding",
    )
    DECAY_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    DECAY_POWER_FIELD_NUMBER: _ClassVar[int]
    CASH_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_WEIGHTS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_STALENESS_TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    COMPOSITE_PRICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCES_SPEC_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCES_SPEC_BINDING_FIELD_NUMBER: _ClassVar[int]
    decay_weight: str
    decay_power: int
    cash_amount: str
    source_weights: _containers.RepeatedScalarFieldContainer[str]
    source_staleness_tolerance: _containers.RepeatedScalarFieldContainer[str]
    composite_price_type: CompositePriceType
    data_sources_spec: _containers.RepeatedCompositeFieldContainer[
        _data_source_pb2.DataSourceDefinition
    ]
    data_sources_spec_binding: _containers.RepeatedCompositeFieldContainer[
        _data_source_pb2.SpecBindingForCompositePrice
    ]
    def __init__(
        self,
        decay_weight: _Optional[str] = ...,
        decay_power: _Optional[int] = ...,
        cash_amount: _Optional[str] = ...,
        source_weights: _Optional[_Iterable[str]] = ...,
        source_staleness_tolerance: _Optional[_Iterable[str]] = ...,
        composite_price_type: _Optional[_Union[CompositePriceType, str]] = ...,
        data_sources_spec: _Optional[
            _Iterable[_Union[_data_source_pb2.DataSourceDefinition, _Mapping]]
        ] = ...,
        data_sources_spec_binding: _Optional[
            _Iterable[_Union[_data_source_pb2.SpecBindingForCompositePrice, _Mapping]]
        ] = ...,
    ) -> None: ...

class DataSourceSpecToAutomatedPurchaseBinding(_message.Message):
    __slots__ = (
        "auction_schedule_property",
        "auction_volume_snapshot_schedule_property",
    )
    AUCTION_SCHEDULE_PROPERTY_FIELD_NUMBER: _ClassVar[int]
    AUCTION_VOLUME_SNAPSHOT_SCHEDULE_PROPERTY_FIELD_NUMBER: _ClassVar[int]
    auction_schedule_property: str
    auction_volume_snapshot_schedule_property: str
    def __init__(
        self,
        auction_schedule_property: _Optional[str] = ...,
        auction_volume_snapshot_schedule_property: _Optional[str] = ...,
    ) -> None: ...
