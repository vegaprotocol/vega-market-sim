# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/markets.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from .oracles.v1 import spec_pb2 as vega_dot_oracles_dot_v1_dot_spec__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x12vega/markets.proto\x12\x04vega\x1a\x1avega/oracles/v1/spec.proto"E\n\x0f\x41uctionDuration\x12\x1a\n\x08\x64uration\x18\x01 \x01(\x03R\x08\x64uration\x12\x16\n\x06volume\x18\x02 \x01(\x04R\x06volume"\xa3\x03\n\x06\x46uture\x12)\n\x10settlement_asset\x18\x02 \x01(\tR\x0fsettlementAsset\x12\x1d\n\nquote_name\x18\x04 \x01(\tR\tquoteName\x12^\n oracle_spec_for_settlement_price\x18\x05 \x01(\x0b\x32\x16.oracles.v1.OracleSpecR\x1coracleSpecForSettlementPrice\x12\x64\n#oracle_spec_for_trading_termination\x18\x06 \x01(\x0b\x32\x16.oracles.v1.OracleSpecR\x1foracleSpecForTradingTermination\x12O\n\x13oracle_spec_binding\x18\x07 \x01(\x0b\x32\x1f.vega.OracleSpecToFutureBindingR\x11oracleSpecBinding\x12\x38\n\x18settlement_data_decimals\x18\x08 \x01(\rR\x16settlementDataDecimals"\x99\x01\n\x19OracleSpecToFutureBinding\x12:\n\x19settlement_price_property\x18\x01 \x01(\tR\x17settlementPriceProperty\x12@\n\x1ctrading_termination_property\x18\x02 \x01(\tR\x1atradingTerminationProperty"(\n\x12InstrumentMetadata\x12\x12\n\x04tags\x18\x01 \x03(\tR\x04tags"\xad\x01\n\nInstrument\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x12\n\x04\x63ode\x18\x02 \x01(\tR\x04\x63ode\x12\x12\n\x04name\x18\x03 \x01(\tR\x04name\x12\x34\n\x08metadata\x18\x04 \x01(\x0b\x32\x18.vega.InstrumentMetadataR\x08metadata\x12&\n\x06\x66uture\x18\x64 \x01(\x0b\x32\x0c.vega.FutureH\x00R\x06\x66utureB\t\n\x07product"\x92\x01\n\x12LogNormalRiskModel\x12\x36\n\x17risk_aversion_parameter\x18\x01 \x01(\x01R\x15riskAversionParameter\x12\x10\n\x03tau\x18\x02 \x01(\x01R\x03tau\x12\x32\n\x06params\x18\x03 \x01(\x0b\x32\x1a.vega.LogNormalModelParamsR\x06params"J\n\x14LogNormalModelParams\x12\x0e\n\x02mu\x18\x01 \x01(\x01R\x02mu\x12\x0c\n\x01r\x18\x02 \x01(\x01R\x01r\x12\x14\n\x05sigma\x18\x03 \x01(\x01R\x05sigma"B\n\x0fSimpleRiskModel\x12/\n\x06params\x18\x01 \x01(\x0b\x32\x17.vega.SimpleModelParamsR\x06params"\xd1\x01\n\x11SimpleModelParams\x12\x1f\n\x0b\x66\x61\x63tor_long\x18\x01 \x01(\x01R\nfactorLong\x12!\n\x0c\x66\x61\x63tor_short\x18\x02 \x01(\x01R\x0b\x66\x61\x63torShort\x12\x1e\n\x0bmax_move_up\x18\x03 \x01(\x01R\tmaxMoveUp\x12"\n\rmin_move_down\x18\x04 \x01(\x01R\x0bminMoveDown\x12\x34\n\x16probability_of_trading\x18\x05 \x01(\x01R\x14probabilityOfTrading"\x89\x01\n\x0eScalingFactors\x12!\n\x0csearch_level\x18\x01 \x01(\x01R\x0bsearchLevel\x12%\n\x0einitial_margin\x18\x02 \x01(\x01R\rinitialMargin\x12-\n\x12\x63ollateral_release\x18\x03 \x01(\x01R\x11\x63ollateralRelease"Q\n\x10MarginCalculator\x12=\n\x0fscaling_factors\x18\x01 \x01(\x0b\x32\x14.vega.ScalingFactorsR\x0escalingFactors"\xad\x02\n\x12TradableInstrument\x12\x30\n\ninstrument\x18\x01 \x01(\x0b\x32\x10.vega.InstrumentR\ninstrument\x12\x43\n\x11margin_calculator\x18\x02 \x01(\x0b\x32\x16.vega.MarginCalculatorR\x10marginCalculator\x12M\n\x15log_normal_risk_model\x18\x64 \x01(\x0b\x32\x18.vega.LogNormalRiskModelH\x00R\x12logNormalRiskModel\x12\x43\n\x11simple_risk_model\x18\x65 \x01(\x0b\x32\x15.vega.SimpleRiskModelH\x00R\x0fsimpleRiskModelB\x0c\n\nrisk_model"}\n\nFeeFactors\x12\x1b\n\tmaker_fee\x18\x01 \x01(\tR\x08makerFee\x12-\n\x12infrastructure_fee\x18\x02 \x01(\tR\x11infrastructureFee\x12#\n\rliquidity_fee\x18\x03 \x01(\tR\x0cliquidityFee"2\n\x04\x46\x65\x65s\x12*\n\x07\x66\x61\x63tors\x18\x01 \x01(\x0b\x32\x10.vega.FeeFactorsR\x07\x66\x61\x63tors"\x81\x01\n\x16PriceMonitoringTrigger\x12\x18\n\x07horizon\x18\x01 \x01(\x03R\x07horizon\x12 \n\x0bprobability\x18\x02 \x01(\tR\x0bprobability\x12+\n\x11\x61uction_extension\x18\x03 \x01(\x03R\x10\x61uctionExtension"U\n\x19PriceMonitoringParameters\x12\x38\n\x08triggers\x18\x01 \x03(\x0b\x32\x1c.vega.PriceMonitoringTriggerR\x08triggers"Z\n\x17PriceMonitoringSettings\x12?\n\nparameters\x18\x01 \x01(\x0b\x32\x1f.vega.PriceMonitoringParametersR\nparameters"\xcc\x01\n\x1dLiquidityMonitoringParameters\x12S\n\x17target_stake_parameters\x18\x01 \x01(\x0b\x32\x1b.vega.TargetStakeParametersR\x15targetStakeParameters\x12)\n\x10triggering_ratio\x18\x02 \x01(\x01R\x0ftriggeringRatio\x12+\n\x11\x61uction_extension\x18\x03 \x01(\x03R\x10\x61uctionExtension"_\n\x15TargetStakeParameters\x12\x1f\n\x0btime_window\x18\x01 \x01(\x03R\ntimeWindow\x12%\n\x0escaling_factor\x18\x02 \x01(\x01R\rscalingFactor"\xc0\x08\n\x06Market\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12I\n\x13tradable_instrument\x18\x02 \x01(\x0b\x32\x18.vega.TradableInstrumentR\x12tradableInstrument\x12%\n\x0e\x64\x65\x63imal_places\x18\x03 \x01(\x04R\rdecimalPlaces\x12\x1e\n\x04\x66\x65\x65s\x18\x04 \x01(\x0b\x32\n.vega.FeesR\x04\x66\x65\x65s\x12>\n\x0fopening_auction\x18\x05 \x01(\x0b\x32\x15.vega.AuctionDurationR\x0eopeningAuction\x12Y\n\x19price_monitoring_settings\x18\x06 \x01(\x0b\x32\x1d.vega.PriceMonitoringSettingsR\x17priceMonitoringSettings\x12k\n\x1fliquidity_monitoring_parameters\x18\x07 \x01(\x0b\x32#.vega.LiquidityMonitoringParametersR\x1dliquidityMonitoringParameters\x12;\n\x0ctrading_mode\x18\x08 \x01(\x0e\x32\x18.vega.Market.TradingModeR\x0btradingMode\x12(\n\x05state\x18\t \x01(\x0e\x32\x12.vega.Market.StateR\x05state\x12\x43\n\x11market_timestamps\x18\n \x01(\x0b\x32\x16.vega.MarketTimestampsR\x10marketTimestamps\x12\x36\n\x17position_decimal_places\x18\x0b \x01(\x04R\x15positionDecimalPlaces"\xd8\x01\n\x05State\x12\x15\n\x11STATE_UNSPECIFIED\x10\x00\x12\x12\n\x0eSTATE_PROPOSED\x10\x01\x12\x12\n\x0eSTATE_REJECTED\x10\x02\x12\x11\n\rSTATE_PENDING\x10\x03\x12\x13\n\x0fSTATE_CANCELLED\x10\x04\x12\x10\n\x0cSTATE_ACTIVE\x10\x05\x12\x13\n\x0fSTATE_SUSPENDED\x10\x06\x12\x10\n\x0cSTATE_CLOSED\x10\x07\x12\x1c\n\x18STATE_TRADING_TERMINATED\x10\x08\x12\x11\n\rSTATE_SETTLED\x10\t"\xcc\x01\n\x0bTradingMode\x12\x1c\n\x18TRADING_MODE_UNSPECIFIED\x10\x00\x12\x1b\n\x17TRADING_MODE_CONTINUOUS\x10\x01\x12\x1e\n\x1aTRADING_MODE_BATCH_AUCTION\x10\x02\x12 \n\x1cTRADING_MODE_OPENING_AUCTION\x10\x03\x12#\n\x1fTRADING_MODE_MONITORING_AUCTION\x10\x04\x12\x1b\n\x17TRADING_MODE_NO_TRADING\x10\x05"r\n\x10MarketTimestamps\x12\x1a\n\x08proposed\x18\x01 \x01(\x03R\x08proposed\x12\x18\n\x07pending\x18\x02 \x01(\x03R\x07pending\x12\x12\n\x04open\x18\x03 \x01(\x03R\x04open\x12\x14\n\x05\x63lose\x18\x04 \x01(\x03R\x05\x63loseB\'Z%code.vegaprotocol.io/vega/protos/vegab\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "vega.markets_pb2", globals())
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z%code.vegaprotocol.io/vega/protos/vega"
    _AUCTIONDURATION._serialized_start = 56
    _AUCTIONDURATION._serialized_end = 125
    _FUTURE._serialized_start = 128
    _FUTURE._serialized_end = 547
    _ORACLESPECTOFUTUREBINDING._serialized_start = 550
    _ORACLESPECTOFUTUREBINDING._serialized_end = 703
    _INSTRUMENTMETADATA._serialized_start = 705
    _INSTRUMENTMETADATA._serialized_end = 745
    _INSTRUMENT._serialized_start = 748
    _INSTRUMENT._serialized_end = 921
    _LOGNORMALRISKMODEL._serialized_start = 924
    _LOGNORMALRISKMODEL._serialized_end = 1070
    _LOGNORMALMODELPARAMS._serialized_start = 1072
    _LOGNORMALMODELPARAMS._serialized_end = 1146
    _SIMPLERISKMODEL._serialized_start = 1148
    _SIMPLERISKMODEL._serialized_end = 1214
    _SIMPLEMODELPARAMS._serialized_start = 1217
    _SIMPLEMODELPARAMS._serialized_end = 1426
    _SCALINGFACTORS._serialized_start = 1429
    _SCALINGFACTORS._serialized_end = 1566
    _MARGINCALCULATOR._serialized_start = 1568
    _MARGINCALCULATOR._serialized_end = 1649
    _TRADABLEINSTRUMENT._serialized_start = 1652
    _TRADABLEINSTRUMENT._serialized_end = 1953
    _FEEFACTORS._serialized_start = 1955
    _FEEFACTORS._serialized_end = 2080
    _FEES._serialized_start = 2082
    _FEES._serialized_end = 2132
    _PRICEMONITORINGTRIGGER._serialized_start = 2135
    _PRICEMONITORINGTRIGGER._serialized_end = 2264
    _PRICEMONITORINGPARAMETERS._serialized_start = 2266
    _PRICEMONITORINGPARAMETERS._serialized_end = 2351
    _PRICEMONITORINGSETTINGS._serialized_start = 2353
    _PRICEMONITORINGSETTINGS._serialized_end = 2443
    _LIQUIDITYMONITORINGPARAMETERS._serialized_start = 2446
    _LIQUIDITYMONITORINGPARAMETERS._serialized_end = 2650
    _TARGETSTAKEPARAMETERS._serialized_start = 2652
    _TARGETSTAKEPARAMETERS._serialized_end = 2747
    _MARKET._serialized_start = 2750
    _MARKET._serialized_end = 3838
    _MARKET_STATE._serialized_start = 3415
    _MARKET_STATE._serialized_end = 3631
    _MARKET_TRADINGMODE._serialized_start = 3634
    _MARKET_TRADINGMODE._serialized_end = 3838
    _MARKETTIMESTAMPS._serialized_start = 3840
    _MARKETTIMESTAMPS._serialized_end = 3954
# @@protoc_insertion_point(module_scope)
