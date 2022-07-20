# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/markets.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from .oracles.v1 import spec_pb2 as vega_dot_oracles_dot_v1_dot_spec__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x12vega/markets.proto\x12\x04vega\x1a\x1avega/oracles/v1/spec.proto"3\n\x0f\x41uctionDuration\x12\x10\n\x08\x64uration\x18\x01 \x01(\x03\x12\x0e\n\x06volume\x18\x02 \x01(\x04"\x9e\x02\n\x06\x46uture\x12\x18\n\x10settlement_asset\x18\x02 \x01(\t\x12\x12\n\nquote_name\x18\x04 \x01(\t\x12@\n oracle_spec_for_settlement_price\x18\x05 \x01(\x0b\x32\x16.oracles.v1.OracleSpec\x12\x43\n#oracle_spec_for_trading_termination\x18\x06 \x01(\x0b\x32\x16.oracles.v1.OracleSpec\x12<\n\x13oracle_spec_binding\x18\x07 \x01(\x0b\x32\x1f.vega.OracleSpecToFutureBinding\x12!\n\x19settlement_price_decimals\x18\x08 \x01(\r"d\n\x19OracleSpecToFutureBinding\x12!\n\x19settlement_price_property\x18\x01 \x01(\t\x12$\n\x1ctrading_termination_property\x18\x02 \x01(\t""\n\x12InstrumentMetadata\x12\x0c\n\x04tags\x18\x01 \x03(\t"\x8b\x01\n\nInstrument\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04\x63ode\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\x12*\n\x08metadata\x18\x04 \x01(\x0b\x32\x18.vega.InstrumentMetadata\x12\x1e\n\x06\x66uture\x18\x64 \x01(\x0b\x32\x0c.vega.FutureH\x00\x42\t\n\x07product"n\n\x12LogNormalRiskModel\x12\x1f\n\x17risk_aversion_parameter\x18\x01 \x01(\x01\x12\x0b\n\x03tau\x18\x02 \x01(\x01\x12*\n\x06params\x18\x03 \x01(\x0b\x32\x1a.vega.LogNormalModelParams"<\n\x14LogNormalModelParams\x12\n\n\x02mu\x18\x01 \x01(\x01\x12\t\n\x01r\x18\x02 \x01(\x01\x12\r\n\x05sigma\x18\x03 \x01(\x01":\n\x0fSimpleRiskModel\x12\'\n\x06params\x18\x01 \x01(\x0b\x32\x17.vega.SimpleModelParams"\x8a\x01\n\x11SimpleModelParams\x12\x13\n\x0b\x66\x61\x63tor_long\x18\x01 \x01(\x01\x12\x14\n\x0c\x66\x61\x63tor_short\x18\x02 \x01(\x01\x12\x13\n\x0bmax_move_up\x18\x03 \x01(\x01\x12\x15\n\rmin_move_down\x18\x04 \x01(\x01\x12\x1e\n\x16probability_of_trading\x18\x05 \x01(\x01"Z\n\x0eScalingFactors\x12\x14\n\x0csearch_level\x18\x01 \x01(\x01\x12\x16\n\x0einitial_margin\x18\x02 \x01(\x01\x12\x1a\n\x12\x63ollateral_release\x18\x03 \x01(\x01"A\n\x10MarginCalculator\x12-\n\x0fscaling_factors\x18\x01 \x01(\x0b\x32\x14.vega.ScalingFactors"\xea\x01\n\x12TradableInstrument\x12$\n\ninstrument\x18\x01 \x01(\x0b\x32\x10.vega.Instrument\x12\x31\n\x11margin_calculator\x18\x02 \x01(\x0b\x32\x16.vega.MarginCalculator\x12\x39\n\x15log_normal_risk_model\x18\x64 \x01(\x0b\x32\x18.vega.LogNormalRiskModelH\x00\x12\x32\n\x11simple_risk_model\x18\x65 \x01(\x0b\x32\x15.vega.SimpleRiskModelH\x00\x42\x0c\n\nrisk_model"R\n\nFeeFactors\x12\x11\n\tmaker_fee\x18\x01 \x01(\t\x12\x1a\n\x12infrastructure_fee\x18\x02 \x01(\t\x12\x15\n\rliquidity_fee\x18\x03 \x01(\t")\n\x04\x46\x65\x65s\x12!\n\x07\x66\x61\x63tors\x18\x01 \x01(\x0b\x32\x10.vega.FeeFactors"Y\n\x16PriceMonitoringTrigger\x12\x0f\n\x07horizon\x18\x01 \x01(\x03\x12\x13\n\x0bprobability\x18\x02 \x01(\t\x12\x19\n\x11\x61uction_extension\x18\x03 \x01(\x03"K\n\x19PriceMonitoringParameters\x12.\n\x08triggers\x18\x01 \x03(\x0b\x32\x1c.vega.PriceMonitoringTrigger"h\n\x17PriceMonitoringSettings\x12\x33\n\nparameters\x18\x01 \x01(\x0b\x32\x1f.vega.PriceMonitoringParameters\x12\x18\n\x10update_frequency\x18\x02 \x01(\x03"\x92\x01\n\x1dLiquidityMonitoringParameters\x12<\n\x17target_stake_parameters\x18\x01 \x01(\x0b\x32\x1b.vega.TargetStakeParameters\x12\x18\n\x10triggering_ratio\x18\x02 \x01(\x01\x12\x19\n\x11\x61uction_extension\x18\x03 \x01(\x03"D\n\x15TargetStakeParameters\x12\x13\n\x0btime_window\x18\x01 \x01(\x03\x12\x16\n\x0escaling_factor\x18\x02 \x01(\x01"\x8e\x07\n\x06Market\x12\n\n\x02id\x18\x01 \x01(\t\x12\x35\n\x13tradable_instrument\x18\x02 \x01(\x0b\x32\x18.vega.TradableInstrument\x12\x16\n\x0e\x64\x65\x63imal_places\x18\x03 \x01(\x04\x12\x18\n\x04\x66\x65\x65s\x18\x04 \x01(\x0b\x32\n.vega.Fees\x12.\n\x0fopening_auction\x18\x05 \x01(\x0b\x32\x15.vega.AuctionDuration\x12@\n\x19price_monitoring_settings\x18\x06 \x01(\x0b\x32\x1d.vega.PriceMonitoringSettings\x12L\n\x1fliquidity_monitoring_parameters\x18\x07 \x01(\x0b\x32#.vega.LiquidityMonitoringParameters\x12.\n\x0ctrading_mode\x18\x08 \x01(\x0e\x32\x18.vega.Market.TradingMode\x12!\n\x05state\x18\t \x01(\x0e\x32\x12.vega.Market.State\x12\x31\n\x11market_timestamps\x18\n \x01(\x0b\x32\x16.vega.MarketTimestamps\x12\x1f\n\x17position_decimal_places\x18\x0b \x01(\x04"\xd8\x01\n\x05State\x12\x15\n\x11STATE_UNSPECIFIED\x10\x00\x12\x12\n\x0eSTATE_PROPOSED\x10\x01\x12\x12\n\x0eSTATE_REJECTED\x10\x02\x12\x11\n\rSTATE_PENDING\x10\x03\x12\x13\n\x0fSTATE_CANCELLED\x10\x04\x12\x10\n\x0cSTATE_ACTIVE\x10\x05\x12\x13\n\x0fSTATE_SUSPENDED\x10\x06\x12\x10\n\x0cSTATE_CLOSED\x10\x07\x12\x1c\n\x18STATE_TRADING_TERMINATED\x10\x08\x12\x11\n\rSTATE_SETTLED\x10\t"\xcc\x01\n\x0bTradingMode\x12\x1c\n\x18TRADING_MODE_UNSPECIFIED\x10\x00\x12\x1b\n\x17TRADING_MODE_CONTINUOUS\x10\x01\x12\x1e\n\x1aTRADING_MODE_BATCH_AUCTION\x10\x02\x12 \n\x1cTRADING_MODE_OPENING_AUCTION\x10\x03\x12#\n\x1fTRADING_MODE_MONITORING_AUCTION\x10\x04\x12\x1b\n\x17TRADING_MODE_NO_TRADING\x10\x05"R\n\x10MarketTimestamps\x12\x10\n\x08proposed\x18\x01 \x01(\x03\x12\x0f\n\x07pending\x18\x02 \x01(\x03\x12\x0c\n\x04open\x18\x03 \x01(\x03\x12\r\n\x05\x63lose\x18\x04 \x01(\x03\x42"Z code.vegaprotocol.io/protos/vegab\x06proto3'
)


_AUCTIONDURATION = DESCRIPTOR.message_types_by_name["AuctionDuration"]
_FUTURE = DESCRIPTOR.message_types_by_name["Future"]
_ORACLESPECTOFUTUREBINDING = DESCRIPTOR.message_types_by_name[
    "OracleSpecToFutureBinding"
]
_INSTRUMENTMETADATA = DESCRIPTOR.message_types_by_name["InstrumentMetadata"]
_INSTRUMENT = DESCRIPTOR.message_types_by_name["Instrument"]
_LOGNORMALRISKMODEL = DESCRIPTOR.message_types_by_name["LogNormalRiskModel"]
_LOGNORMALMODELPARAMS = DESCRIPTOR.message_types_by_name["LogNormalModelParams"]
_SIMPLERISKMODEL = DESCRIPTOR.message_types_by_name["SimpleRiskModel"]
_SIMPLEMODELPARAMS = DESCRIPTOR.message_types_by_name["SimpleModelParams"]
_SCALINGFACTORS = DESCRIPTOR.message_types_by_name["ScalingFactors"]
_MARGINCALCULATOR = DESCRIPTOR.message_types_by_name["MarginCalculator"]
_TRADABLEINSTRUMENT = DESCRIPTOR.message_types_by_name["TradableInstrument"]
_FEEFACTORS = DESCRIPTOR.message_types_by_name["FeeFactors"]
_FEES = DESCRIPTOR.message_types_by_name["Fees"]
_PRICEMONITORINGTRIGGER = DESCRIPTOR.message_types_by_name["PriceMonitoringTrigger"]
_PRICEMONITORINGPARAMETERS = DESCRIPTOR.message_types_by_name[
    "PriceMonitoringParameters"
]
_PRICEMONITORINGSETTINGS = DESCRIPTOR.message_types_by_name["PriceMonitoringSettings"]
_LIQUIDITYMONITORINGPARAMETERS = DESCRIPTOR.message_types_by_name[
    "LiquidityMonitoringParameters"
]
_TARGETSTAKEPARAMETERS = DESCRIPTOR.message_types_by_name["TargetStakeParameters"]
_MARKET = DESCRIPTOR.message_types_by_name["Market"]
_MARKETTIMESTAMPS = DESCRIPTOR.message_types_by_name["MarketTimestamps"]
_MARKET_STATE = _MARKET.enum_types_by_name["State"]
_MARKET_TRADINGMODE = _MARKET.enum_types_by_name["TradingMode"]
AuctionDuration = _reflection.GeneratedProtocolMessageType(
    "AuctionDuration",
    (_message.Message,),
    {
        "DESCRIPTOR": _AUCTIONDURATION,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.AuctionDuration)
    },
)
_sym_db.RegisterMessage(AuctionDuration)

Future = _reflection.GeneratedProtocolMessageType(
    "Future",
    (_message.Message,),
    {
        "DESCRIPTOR": _FUTURE,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.Future)
    },
)
_sym_db.RegisterMessage(Future)

OracleSpecToFutureBinding = _reflection.GeneratedProtocolMessageType(
    "OracleSpecToFutureBinding",
    (_message.Message,),
    {
        "DESCRIPTOR": _ORACLESPECTOFUTUREBINDING,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.OracleSpecToFutureBinding)
    },
)
_sym_db.RegisterMessage(OracleSpecToFutureBinding)

InstrumentMetadata = _reflection.GeneratedProtocolMessageType(
    "InstrumentMetadata",
    (_message.Message,),
    {
        "DESCRIPTOR": _INSTRUMENTMETADATA,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.InstrumentMetadata)
    },
)
_sym_db.RegisterMessage(InstrumentMetadata)

Instrument = _reflection.GeneratedProtocolMessageType(
    "Instrument",
    (_message.Message,),
    {
        "DESCRIPTOR": _INSTRUMENT,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.Instrument)
    },
)
_sym_db.RegisterMessage(Instrument)

LogNormalRiskModel = _reflection.GeneratedProtocolMessageType(
    "LogNormalRiskModel",
    (_message.Message,),
    {
        "DESCRIPTOR": _LOGNORMALRISKMODEL,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.LogNormalRiskModel)
    },
)
_sym_db.RegisterMessage(LogNormalRiskModel)

LogNormalModelParams = _reflection.GeneratedProtocolMessageType(
    "LogNormalModelParams",
    (_message.Message,),
    {
        "DESCRIPTOR": _LOGNORMALMODELPARAMS,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.LogNormalModelParams)
    },
)
_sym_db.RegisterMessage(LogNormalModelParams)

SimpleRiskModel = _reflection.GeneratedProtocolMessageType(
    "SimpleRiskModel",
    (_message.Message,),
    {
        "DESCRIPTOR": _SIMPLERISKMODEL,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.SimpleRiskModel)
    },
)
_sym_db.RegisterMessage(SimpleRiskModel)

SimpleModelParams = _reflection.GeneratedProtocolMessageType(
    "SimpleModelParams",
    (_message.Message,),
    {
        "DESCRIPTOR": _SIMPLEMODELPARAMS,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.SimpleModelParams)
    },
)
_sym_db.RegisterMessage(SimpleModelParams)

ScalingFactors = _reflection.GeneratedProtocolMessageType(
    "ScalingFactors",
    (_message.Message,),
    {
        "DESCRIPTOR": _SCALINGFACTORS,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.ScalingFactors)
    },
)
_sym_db.RegisterMessage(ScalingFactors)

MarginCalculator = _reflection.GeneratedProtocolMessageType(
    "MarginCalculator",
    (_message.Message,),
    {
        "DESCRIPTOR": _MARGINCALCULATOR,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.MarginCalculator)
    },
)
_sym_db.RegisterMessage(MarginCalculator)

TradableInstrument = _reflection.GeneratedProtocolMessageType(
    "TradableInstrument",
    (_message.Message,),
    {
        "DESCRIPTOR": _TRADABLEINSTRUMENT,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.TradableInstrument)
    },
)
_sym_db.RegisterMessage(TradableInstrument)

FeeFactors = _reflection.GeneratedProtocolMessageType(
    "FeeFactors",
    (_message.Message,),
    {
        "DESCRIPTOR": _FEEFACTORS,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.FeeFactors)
    },
)
_sym_db.RegisterMessage(FeeFactors)

Fees = _reflection.GeneratedProtocolMessageType(
    "Fees",
    (_message.Message,),
    {
        "DESCRIPTOR": _FEES,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.Fees)
    },
)
_sym_db.RegisterMessage(Fees)

PriceMonitoringTrigger = _reflection.GeneratedProtocolMessageType(
    "PriceMonitoringTrigger",
    (_message.Message,),
    {
        "DESCRIPTOR": _PRICEMONITORINGTRIGGER,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.PriceMonitoringTrigger)
    },
)
_sym_db.RegisterMessage(PriceMonitoringTrigger)

PriceMonitoringParameters = _reflection.GeneratedProtocolMessageType(
    "PriceMonitoringParameters",
    (_message.Message,),
    {
        "DESCRIPTOR": _PRICEMONITORINGPARAMETERS,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.PriceMonitoringParameters)
    },
)
_sym_db.RegisterMessage(PriceMonitoringParameters)

PriceMonitoringSettings = _reflection.GeneratedProtocolMessageType(
    "PriceMonitoringSettings",
    (_message.Message,),
    {
        "DESCRIPTOR": _PRICEMONITORINGSETTINGS,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.PriceMonitoringSettings)
    },
)
_sym_db.RegisterMessage(PriceMonitoringSettings)

LiquidityMonitoringParameters = _reflection.GeneratedProtocolMessageType(
    "LiquidityMonitoringParameters",
    (_message.Message,),
    {
        "DESCRIPTOR": _LIQUIDITYMONITORINGPARAMETERS,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.LiquidityMonitoringParameters)
    },
)
_sym_db.RegisterMessage(LiquidityMonitoringParameters)

TargetStakeParameters = _reflection.GeneratedProtocolMessageType(
    "TargetStakeParameters",
    (_message.Message,),
    {
        "DESCRIPTOR": _TARGETSTAKEPARAMETERS,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.TargetStakeParameters)
    },
)
_sym_db.RegisterMessage(TargetStakeParameters)

Market = _reflection.GeneratedProtocolMessageType(
    "Market",
    (_message.Message,),
    {
        "DESCRIPTOR": _MARKET,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.Market)
    },
)
_sym_db.RegisterMessage(Market)

MarketTimestamps = _reflection.GeneratedProtocolMessageType(
    "MarketTimestamps",
    (_message.Message,),
    {
        "DESCRIPTOR": _MARKETTIMESTAMPS,
        "__module__": "vega.markets_pb2"
        # @@protoc_insertion_point(class_scope:vega.MarketTimestamps)
    },
)
_sym_db.RegisterMessage(MarketTimestamps)

if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z code.vegaprotocol.io/protos/vega"
    _AUCTIONDURATION._serialized_start = 56
    _AUCTIONDURATION._serialized_end = 107
    _FUTURE._serialized_start = 110
    _FUTURE._serialized_end = 396
    _ORACLESPECTOFUTUREBINDING._serialized_start = 398
    _ORACLESPECTOFUTUREBINDING._serialized_end = 498
    _INSTRUMENTMETADATA._serialized_start = 500
    _INSTRUMENTMETADATA._serialized_end = 534
    _INSTRUMENT._serialized_start = 537
    _INSTRUMENT._serialized_end = 676
    _LOGNORMALRISKMODEL._serialized_start = 678
    _LOGNORMALRISKMODEL._serialized_end = 788
    _LOGNORMALMODELPARAMS._serialized_start = 790
    _LOGNORMALMODELPARAMS._serialized_end = 850
    _SIMPLERISKMODEL._serialized_start = 852
    _SIMPLERISKMODEL._serialized_end = 910
    _SIMPLEMODELPARAMS._serialized_start = 913
    _SIMPLEMODELPARAMS._serialized_end = 1051
    _SCALINGFACTORS._serialized_start = 1053
    _SCALINGFACTORS._serialized_end = 1143
    _MARGINCALCULATOR._serialized_start = 1145
    _MARGINCALCULATOR._serialized_end = 1210
    _TRADABLEINSTRUMENT._serialized_start = 1213
    _TRADABLEINSTRUMENT._serialized_end = 1447
    _FEEFACTORS._serialized_start = 1449
    _FEEFACTORS._serialized_end = 1531
    _FEES._serialized_start = 1533
    _FEES._serialized_end = 1574
    _PRICEMONITORINGTRIGGER._serialized_start = 1576
    _PRICEMONITORINGTRIGGER._serialized_end = 1665
    _PRICEMONITORINGPARAMETERS._serialized_start = 1667
    _PRICEMONITORINGPARAMETERS._serialized_end = 1742
    _PRICEMONITORINGSETTINGS._serialized_start = 1744
    _PRICEMONITORINGSETTINGS._serialized_end = 1848
    _LIQUIDITYMONITORINGPARAMETERS._serialized_start = 1851
    _LIQUIDITYMONITORINGPARAMETERS._serialized_end = 1997
    _TARGETSTAKEPARAMETERS._serialized_start = 1999
    _TARGETSTAKEPARAMETERS._serialized_end = 2067
    _MARKET._serialized_start = 2070
    _MARKET._serialized_end = 2980
    _MARKET_STATE._serialized_start = 2557
    _MARKET_STATE._serialized_end = 2773
    _MARKET_TRADINGMODE._serialized_start = 2776
    _MARKET_TRADINGMODE._serialized_end = 2980
    _MARKETTIMESTAMPS._serialized_start = 2982
    _MARKETTIMESTAMPS._serialized_end = 3064
# @@protoc_insertion_point(module_scope)
