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


from . import data_source_pb2 as vega_dot_data__source__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x12vega/markets.proto\x12\x04vega\x1a\x16vega/data_source.proto"E\n\x0f\x41uctionDuration\x12\x1a\n\x08\x64uration\x18\x01 \x01(\x03R\x08\x64uration\x12\x16\n\x06volume\x18\x02 \x01(\x04R\x06volume"Z\n\x04Spot\x12\x1d\n\nbase_asset\x18\x01 \x01(\tR\tbaseAsset\x12\x1f\n\x0bquote_asset\x18\x02 \x01(\tR\nquoteAsset\x12\x12\n\x04name\x18\x03 \x01(\tR\x04name"\x82\x03\n\x06\x46uture\x12)\n\x10settlement_asset\x18\x01 \x01(\tR\x0fsettlementAsset\x12\x1d\n\nquote_name\x18\x02 \x01(\tR\tquoteName\x12\x63\n$data_source_spec_for_settlement_data\x18\x03 \x01(\x0b\x32\x14.vega.DataSourceSpecR\x1f\x64\x61taSourceSpecForSettlementData\x12k\n(data_source_spec_for_trading_termination\x18\x04 \x01(\x0b\x32\x14.vega.DataSourceSpecR#dataSourceSpecForTradingTermination\x12\\\n\x18\x64\x61ta_source_spec_binding\x18\x05 \x01(\x0b\x32#.vega.DataSourceSpecToFutureBindingR\x15\x64\x61taSourceSpecBinding"\x9b\x01\n\x1d\x44\x61taSourceSpecToFutureBinding\x12\x38\n\x18settlement_data_property\x18\x01 \x01(\tR\x16settlementDataProperty\x12@\n\x1ctrading_termination_property\x18\x02 \x01(\tR\x1atradingTerminationProperty"(\n\x12InstrumentMetadata\x12\x12\n\x04tags\x18\x01 \x03(\tR\x04tags"\xcf\x01\n\nInstrument\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x12\n\x04\x63ode\x18\x02 \x01(\tR\x04\x63ode\x12\x12\n\x04name\x18\x03 \x01(\tR\x04name\x12\x34\n\x08metadata\x18\x04 \x01(\x0b\x32\x18.vega.InstrumentMetadataR\x08metadata\x12&\n\x06\x66uture\x18\x64 \x01(\x0b\x32\x0c.vega.FutureH\x00R\x06\x66uture\x12 \n\x04spot\x18\x65 \x01(\x0b\x32\n.vega.SpotH\x00R\x04spotB\t\n\x07product"\x92\x01\n\x12LogNormalRiskModel\x12\x36\n\x17risk_aversion_parameter\x18\x01 \x01(\x01R\x15riskAversionParameter\x12\x10\n\x03tau\x18\x02 \x01(\x01R\x03tau\x12\x32\n\x06params\x18\x03 \x01(\x0b\x32\x1a.vega.LogNormalModelParamsR\x06params"J\n\x14LogNormalModelParams\x12\x0e\n\x02mu\x18\x01 \x01(\x01R\x02mu\x12\x0c\n\x01r\x18\x02 \x01(\x01R\x01r\x12\x14\n\x05sigma\x18\x03 \x01(\x01R\x05sigma"B\n\x0fSimpleRiskModel\x12/\n\x06params\x18\x01 \x01(\x0b\x32\x17.vega.SimpleModelParamsR\x06params"\xd1\x01\n\x11SimpleModelParams\x12\x1f\n\x0b\x66\x61\x63tor_long\x18\x01 \x01(\x01R\nfactorLong\x12!\n\x0c\x66\x61\x63tor_short\x18\x02 \x01(\x01R\x0b\x66\x61\x63torShort\x12\x1e\n\x0bmax_move_up\x18\x03 \x01(\x01R\tmaxMoveUp\x12"\n\rmin_move_down\x18\x04 \x01(\x01R\x0bminMoveDown\x12\x34\n\x16probability_of_trading\x18\x05 \x01(\x01R\x14probabilityOfTrading"\x89\x01\n\x0eScalingFactors\x12!\n\x0csearch_level\x18\x01 \x01(\x01R\x0bsearchLevel\x12%\n\x0einitial_margin\x18\x02 \x01(\x01R\rinitialMargin\x12-\n\x12\x63ollateral_release\x18\x03 \x01(\x01R\x11\x63ollateralRelease"Q\n\x10MarginCalculator\x12=\n\x0fscaling_factors\x18\x01 \x01(\x0b\x32\x14.vega.ScalingFactorsR\x0escalingFactors"\xad\x02\n\x12TradableInstrument\x12\x30\n\ninstrument\x18\x01 \x01(\x0b\x32\x10.vega.InstrumentR\ninstrument\x12\x43\n\x11margin_calculator\x18\x02 \x01(\x0b\x32\x16.vega.MarginCalculatorR\x10marginCalculator\x12M\n\x15log_normal_risk_model\x18\x64 \x01(\x0b\x32\x18.vega.LogNormalRiskModelH\x00R\x12logNormalRiskModel\x12\x43\n\x11simple_risk_model\x18\x65 \x01(\x0b\x32\x15.vega.SimpleRiskModelH\x00R\x0fsimpleRiskModelB\x0c\n\nrisk_model"}\n\nFeeFactors\x12\x1b\n\tmaker_fee\x18\x01 \x01(\tR\x08makerFee\x12-\n\x12infrastructure_fee\x18\x02 \x01(\tR\x11infrastructureFee\x12#\n\rliquidity_fee\x18\x03 \x01(\tR\x0cliquidityFee"2\n\x04\x46\x65\x65s\x12*\n\x07\x66\x61\x63tors\x18\x01 \x01(\x0b\x32\x10.vega.FeeFactorsR\x07\x66\x61\x63tors"\x81\x01\n\x16PriceMonitoringTrigger\x12\x18\n\x07horizon\x18\x01 \x01(\x03R\x07horizon\x12 \n\x0bprobability\x18\x02 \x01(\tR\x0bprobability\x12+\n\x11\x61uction_extension\x18\x03 \x01(\x03R\x10\x61uctionExtension"U\n\x19PriceMonitoringParameters\x12\x38\n\x08triggers\x18\x01 \x03(\x0b\x32\x1c.vega.PriceMonitoringTriggerR\x08triggers"Z\n\x17PriceMonitoringSettings\x12?\n\nparameters\x18\x01 \x01(\x0b\x32\x1f.vega.PriceMonitoringParametersR\nparameters"\xcc\x01\n\x1dLiquidityMonitoringParameters\x12S\n\x17target_stake_parameters\x18\x01 \x01(\x0b\x32\x1b.vega.TargetStakeParametersR\x15targetStakeParameters\x12)\n\x10triggering_ratio\x18\x02 \x01(\tR\x0ftriggeringRatio\x12+\n\x11\x61uction_extension\x18\x03 \x01(\x03R\x10\x61uctionExtension"_\n\x15TargetStakeParameters\x12\x1f\n\x0btime_window\x18\x01 \x01(\x03R\ntimeWindow\x12%\n\x0escaling_factor\x18\x02 \x01(\x01R\rscalingFactor"\xc2\x0b\n\x06Market\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12I\n\x13tradable_instrument\x18\x02 \x01(\x0b\x32\x18.vega.TradableInstrumentR\x12tradableInstrument\x12%\n\x0e\x64\x65\x63imal_places\x18\x03 \x01(\x04R\rdecimalPlaces\x12\x1e\n\x04\x66\x65\x65s\x18\x04 \x01(\x0b\x32\n.vega.FeesR\x04\x66\x65\x65s\x12>\n\x0fopening_auction\x18\x05 \x01(\x0b\x32\x15.vega.AuctionDurationR\x0eopeningAuction\x12Y\n\x19price_monitoring_settings\x18\x06 \x01(\x0b\x32\x1d.vega.PriceMonitoringSettingsR\x17priceMonitoringSettings\x12k\n\x1fliquidity_monitoring_parameters\x18\x07 \x01(\x0b\x32#.vega.LiquidityMonitoringParametersR\x1dliquidityMonitoringParameters\x12;\n\x0ctrading_mode\x18\x08 \x01(\x0e\x32\x18.vega.Market.TradingModeR\x0btradingMode\x12(\n\x05state\x18\t \x01(\x0e\x32\x12.vega.Market.StateR\x05state\x12\x43\n\x11market_timestamps\x18\n \x01(\x0b\x32\x16.vega.MarketTimestampsR\x10marketTimestamps\x12\x36\n\x17position_decimal_places\x18\x0b \x01(\x03R\x15positionDecimalPlaces\x12$\n\x0elp_price_range\x18\x0c \x01(\tR\x0clpPriceRange\x12\x34\n\x16linear_slippage_factor\x18\r \x01(\tR\x14linearSlippageFactor\x12:\n\x19quadratic_slippage_factor\x18\x0e \x01(\tR\x17quadraticSlippageFactor\x12-\n\x10parent_market_id\x18\x0f \x01(\tH\x00R\x0eparentMarketId\x88\x01\x01\x12;\n\x17insurance_pool_fraction\x18\x10 \x01(\tH\x01R\x15insurancePoolFraction\x88\x01\x01\x12\x33\n\x13successor_market_id\x18\x11 \x01(\tH\x02R\x11successorMarketId\x88\x01\x01"\xd8\x01\n\x05State\x12\x15\n\x11STATE_UNSPECIFIED\x10\x00\x12\x12\n\x0eSTATE_PROPOSED\x10\x01\x12\x12\n\x0eSTATE_REJECTED\x10\x02\x12\x11\n\rSTATE_PENDING\x10\x03\x12\x13\n\x0fSTATE_CANCELLED\x10\x04\x12\x10\n\x0cSTATE_ACTIVE\x10\x05\x12\x13\n\x0fSTATE_SUSPENDED\x10\x06\x12\x10\n\x0cSTATE_CLOSED\x10\x07\x12\x1c\n\x18STATE_TRADING_TERMINATED\x10\x08\x12\x11\n\rSTATE_SETTLED\x10\t"\xcc\x01\n\x0bTradingMode\x12\x1c\n\x18TRADING_MODE_UNSPECIFIED\x10\x00\x12\x1b\n\x17TRADING_MODE_CONTINUOUS\x10\x01\x12\x1e\n\x1aTRADING_MODE_BATCH_AUCTION\x10\x02\x12 \n\x1cTRADING_MODE_OPENING_AUCTION\x10\x03\x12#\n\x1fTRADING_MODE_MONITORING_AUCTION\x10\x04\x12\x1b\n\x17TRADING_MODE_NO_TRADING\x10\x05\x42\x13\n\x11_parent_market_idB\x1a\n\x18_insurance_pool_fractionB\x16\n\x14_successor_market_id"r\n\x10MarketTimestamps\x12\x1a\n\x08proposed\x18\x01 \x01(\x03R\x08proposed\x12\x18\n\x07pending\x18\x02 \x01(\x03R\x07pending\x12\x12\n\x04open\x18\x03 \x01(\x03R\x04open\x12\x14\n\x05\x63lose\x18\x04 \x01(\x03R\x05\x63loseB\'Z%code.vegaprotocol.io/vega/protos/vegab\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "vega.markets_pb2", globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z%code.vegaprotocol.io/vega/protos/vega"
    _AUCTIONDURATION._serialized_start = 52
    _AUCTIONDURATION._serialized_end = 121
    _SPOT._serialized_start = 123
    _SPOT._serialized_end = 213
    _FUTURE._serialized_start = 216
    _FUTURE._serialized_end = 602
    _DATASOURCESPECTOFUTUREBINDING._serialized_start = 605
    _DATASOURCESPECTOFUTUREBINDING._serialized_end = 760
    _INSTRUMENTMETADATA._serialized_start = 762
    _INSTRUMENTMETADATA._serialized_end = 802
    _INSTRUMENT._serialized_start = 805
    _INSTRUMENT._serialized_end = 1012
    _LOGNORMALRISKMODEL._serialized_start = 1015
    _LOGNORMALRISKMODEL._serialized_end = 1161
    _LOGNORMALMODELPARAMS._serialized_start = 1163
    _LOGNORMALMODELPARAMS._serialized_end = 1237
    _SIMPLERISKMODEL._serialized_start = 1239
    _SIMPLERISKMODEL._serialized_end = 1305
    _SIMPLEMODELPARAMS._serialized_start = 1308
    _SIMPLEMODELPARAMS._serialized_end = 1517
    _SCALINGFACTORS._serialized_start = 1520
    _SCALINGFACTORS._serialized_end = 1657
    _MARGINCALCULATOR._serialized_start = 1659
    _MARGINCALCULATOR._serialized_end = 1740
    _TRADABLEINSTRUMENT._serialized_start = 1743
    _TRADABLEINSTRUMENT._serialized_end = 2044
    _FEEFACTORS._serialized_start = 2046
    _FEEFACTORS._serialized_end = 2171
    _FEES._serialized_start = 2173
    _FEES._serialized_end = 2223
    _PRICEMONITORINGTRIGGER._serialized_start = 2226
    _PRICEMONITORINGTRIGGER._serialized_end = 2355
    _PRICEMONITORINGPARAMETERS._serialized_start = 2357
    _PRICEMONITORINGPARAMETERS._serialized_end = 2442
    _PRICEMONITORINGSETTINGS._serialized_start = 2444
    _PRICEMONITORINGSETTINGS._serialized_end = 2534
    _LIQUIDITYMONITORINGPARAMETERS._serialized_start = 2537
    _LIQUIDITYMONITORINGPARAMETERS._serialized_end = 2741
    _TARGETSTAKEPARAMETERS._serialized_start = 2743
    _TARGETSTAKEPARAMETERS._serialized_end = 2838
    _MARKET._serialized_start = 2841
    _MARKET._serialized_end = 4315
    _MARKET_STATE._serialized_start = 3819
    _MARKET_STATE._serialized_end = 4035
    _MARKET_TRADINGMODE._serialized_start = 4038
    _MARKET_TRADINGMODE._serialized_end = 4242
    _MARKETTIMESTAMPS._serialized_start = 4317
    _MARKETTIMESTAMPS._serialized_end = 4431
# @@protoc_insertion_point(module_scope)
