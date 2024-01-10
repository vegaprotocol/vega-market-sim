# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/markets.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import data_source_pb2 as vega_dot_data__source__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x12vega/markets.proto\x12\x04vega\x1a\x16vega/data_source.proto"E\n\x0f\x41uctionDuration\x12\x1a\n\x08\x64uration\x18\x01 \x01(\x03R\x08\x64uration\x12\x16\n\x06volume\x18\x02 \x01(\x04R\x06volume"Z\n\x04Spot\x12\x1d\n\nbase_asset\x18\x01 \x01(\tR\tbaseAsset\x12\x1f\n\x0bquote_asset\x18\x02 \x01(\tR\nquoteAsset\x12\x12\n\x04name\x18\x03 \x01(\tR\x04name"\x82\x03\n\x06\x46uture\x12)\n\x10settlement_asset\x18\x01 \x01(\tR\x0fsettlementAsset\x12\x1d\n\nquote_name\x18\x02 \x01(\tR\tquoteName\x12\x63\n$data_source_spec_for_settlement_data\x18\x03 \x01(\x0b\x32\x14.vega.DataSourceSpecR\x1f\x64\x61taSourceSpecForSettlementData\x12k\n(data_source_spec_for_trading_termination\x18\x04 \x01(\x0b\x32\x14.vega.DataSourceSpecR#dataSourceSpecForTradingTermination\x12\\\n\x18\x64\x61ta_source_spec_binding\x18\x05 \x01(\x0b\x32#.vega.DataSourceSpecToFutureBindingR\x15\x64\x61taSourceSpecBinding"\xc0\x07\n\tPerpetual\x12)\n\x10settlement_asset\x18\x01 \x01(\tR\x0fsettlementAsset\x12\x1d\n\nquote_name\x18\x02 \x01(\tR\tquoteName\x12\x32\n\x15margin_funding_factor\x18\x03 \x01(\tR\x13marginFundingFactor\x12#\n\rinterest_rate\x18\x04 \x01(\tR\x0cinterestRate\x12*\n\x11\x63lamp_lower_bound\x18\x05 \x01(\tR\x0f\x63lampLowerBound\x12*\n\x11\x63lamp_upper_bound\x18\x06 \x01(\tR\x0f\x63lampUpperBound\x12k\n(data_source_spec_for_settlement_schedule\x18\x07 \x01(\x0b\x32\x14.vega.DataSourceSpecR#dataSourceSpecForSettlementSchedule\x12\x63\n$data_source_spec_for_settlement_data\x18\x08 \x01(\x0b\x32\x14.vega.DataSourceSpecR\x1f\x64\x61taSourceSpecForSettlementData\x12_\n\x18\x64\x61ta_source_spec_binding\x18\t \x01(\x0b\x32&.vega.DataSourceSpecToPerpetualBindingR\x15\x64\x61taSourceSpecBinding\x12\x42\n\x1b\x66unding_rate_scaling_factor\x18\n \x01(\tH\x00R\x18\x66undingRateScalingFactor\x88\x01\x01\x12<\n\x18\x66unding_rate_lower_bound\x18\x0b \x01(\tH\x01R\x15\x66undingRateLowerBound\x88\x01\x01\x12<\n\x18\x66unding_rate_upper_bound\x18\x0c \x01(\tH\x02R\x15\x66undingRateUpperBound\x88\x01\x01\x12T\n\x12index_price_config\x18\r \x01(\x0b\x32!.vega.CompositePriceConfigurationH\x03R\x10indexPriceConfig\x88\x01\x01\x42\x1e\n\x1c_funding_rate_scaling_factorB\x1b\n\x19_funding_rate_lower_boundB\x1b\n\x19_funding_rate_upper_boundB\x15\n\x13_index_price_config"\x9b\x01\n\x1d\x44\x61taSourceSpecToFutureBinding\x12\x38\n\x18settlement_data_property\x18\x01 \x01(\tR\x16settlementDataProperty\x12@\n\x1ctrading_termination_property\x18\x02 \x01(\tR\x1atradingTerminationProperty"\x9e\x01\n DataSourceSpecToPerpetualBinding\x12\x38\n\x18settlement_data_property\x18\x01 \x01(\tR\x16settlementDataProperty\x12@\n\x1csettlement_schedule_property\x18\x02 \x01(\tR\x1asettlementScheduleProperty"(\n\x12InstrumentMetadata\x12\x12\n\x04tags\x18\x01 \x03(\tR\x04tags"\x80\x02\n\nInstrument\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x12\n\x04\x63ode\x18\x02 \x01(\tR\x04\x63ode\x12\x12\n\x04name\x18\x03 \x01(\tR\x04name\x12\x34\n\x08metadata\x18\x04 \x01(\x0b\x32\x18.vega.InstrumentMetadataR\x08metadata\x12&\n\x06\x66uture\x18\x64 \x01(\x0b\x32\x0c.vega.FutureH\x00R\x06\x66uture\x12 \n\x04spot\x18\x65 \x01(\x0b\x32\n.vega.SpotH\x00R\x04spot\x12/\n\tperpetual\x18\x66 \x01(\x0b\x32\x0f.vega.PerpetualH\x00R\tperpetualB\t\n\x07product"\x92\x01\n\x12LogNormalRiskModel\x12\x36\n\x17risk_aversion_parameter\x18\x01 \x01(\x01R\x15riskAversionParameter\x12\x10\n\x03tau\x18\x02 \x01(\x01R\x03tau\x12\x32\n\x06params\x18\x03 \x01(\x0b\x32\x1a.vega.LogNormalModelParamsR\x06params"J\n\x14LogNormalModelParams\x12\x0e\n\x02mu\x18\x01 \x01(\x01R\x02mu\x12\x0c\n\x01r\x18\x02 \x01(\x01R\x01r\x12\x14\n\x05sigma\x18\x03 \x01(\x01R\x05sigma"B\n\x0fSimpleRiskModel\x12/\n\x06params\x18\x01 \x01(\x0b\x32\x17.vega.SimpleModelParamsR\x06params"\xd1\x01\n\x11SimpleModelParams\x12\x1f\n\x0b\x66\x61\x63tor_long\x18\x01 \x01(\x01R\nfactorLong\x12!\n\x0c\x66\x61\x63tor_short\x18\x02 \x01(\x01R\x0b\x66\x61\x63torShort\x12\x1e\n\x0bmax_move_up\x18\x03 \x01(\x01R\tmaxMoveUp\x12"\n\rmin_move_down\x18\x04 \x01(\x01R\x0bminMoveDown\x12\x34\n\x16probability_of_trading\x18\x05 \x01(\x01R\x14probabilityOfTrading"\x89\x01\n\x0eScalingFactors\x12!\n\x0csearch_level\x18\x01 \x01(\x01R\x0bsearchLevel\x12%\n\x0einitial_margin\x18\x02 \x01(\x01R\rinitialMargin\x12-\n\x12\x63ollateral_release\x18\x03 \x01(\x01R\x11\x63ollateralRelease"Q\n\x10MarginCalculator\x12=\n\x0fscaling_factors\x18\x01 \x01(\x0b\x32\x14.vega.ScalingFactorsR\x0escalingFactors"\xad\x02\n\x12TradableInstrument\x12\x30\n\ninstrument\x18\x01 \x01(\x0b\x32\x10.vega.InstrumentR\ninstrument\x12\x43\n\x11margin_calculator\x18\x02 \x01(\x0b\x32\x16.vega.MarginCalculatorR\x10marginCalculator\x12M\n\x15log_normal_risk_model\x18\x64 \x01(\x0b\x32\x18.vega.LogNormalRiskModelH\x00R\x12logNormalRiskModel\x12\x43\n\x11simple_risk_model\x18\x65 \x01(\x0b\x32\x15.vega.SimpleRiskModelH\x00R\x0fsimpleRiskModelB\x0c\n\nrisk_model"}\n\nFeeFactors\x12\x1b\n\tmaker_fee\x18\x01 \x01(\tR\x08makerFee\x12-\n\x12infrastructure_fee\x18\x02 \x01(\tR\x11infrastructureFee\x12#\n\rliquidity_fee\x18\x03 \x01(\tR\x0cliquidityFee"\x84\x01\n\x04\x46\x65\x65s\x12*\n\x07\x66\x61\x63tors\x18\x01 \x01(\x0b\x32\x10.vega.FeeFactorsR\x07\x66\x61\x63tors\x12P\n\x16liquidity_fee_settings\x18\x02 \x01(\x0b\x32\x1a.vega.LiquidityFeeSettingsR\x14liquidityFeeSettings"\x81\x01\n\x16PriceMonitoringTrigger\x12\x18\n\x07horizon\x18\x01 \x01(\x03R\x07horizon\x12 \n\x0bprobability\x18\x02 \x01(\tR\x0bprobability\x12+\n\x11\x61uction_extension\x18\x03 \x01(\x03R\x10\x61uctionExtension"U\n\x19PriceMonitoringParameters\x12\x38\n\x08triggers\x18\x01 \x03(\x0b\x32\x1c.vega.PriceMonitoringTriggerR\x08triggers"Z\n\x17PriceMonitoringSettings\x12?\n\nparameters\x18\x01 \x01(\x0b\x32\x1f.vega.PriceMonitoringParametersR\nparameters"\xcc\x01\n\x1dLiquidityMonitoringParameters\x12S\n\x17target_stake_parameters\x18\x01 \x01(\x0b\x32\x1b.vega.TargetStakeParametersR\x15targetStakeParameters\x12)\n\x10triggering_ratio\x18\x02 \x01(\tR\x0ftriggeringRatio\x12+\n\x11\x61uction_extension\x18\x03 \x01(\x03R\x10\x61uctionExtension"\xfa\x01\n\x16LiquiditySLAParameters\x12\x1f\n\x0bprice_range\x18\x01 \x01(\tR\npriceRange\x12?\n\x1c\x63ommitment_min_time_fraction\x18\x02 \x01(\tR\x19\x63ommitmentMinTimeFraction\x12\x42\n\x1dperformance_hysteresis_epochs\x18\x04 \x01(\x04R\x1bperformanceHysteresisEpochs\x12\x34\n\x16sla_competition_factor\x18\x05 \x01(\tR\x14slaCompetitionFactorJ\x04\x08\x03\x10\x04"\xf8\x01\n\x14LiquidityFeeSettings\x12\x39\n\x06method\x18\x01 \x01(\x0e\x32!.vega.LiquidityFeeSettings.MethodR\x06method\x12&\n\x0c\x66\x65\x65_constant\x18\x02 \x01(\tH\x00R\x0b\x66\x65\x65\x43onstant\x88\x01\x01"l\n\x06Method\x12\x16\n\x12METHOD_UNSPECIFIED\x10\x00\x12\x18\n\x14METHOD_MARGINAL_COST\x10\x01\x12\x1b\n\x17METHOD_WEIGHTED_AVERAGE\x10\x02\x12\x13\n\x0fMETHOD_CONSTANT\x10\x03\x42\x0f\n\r_fee_constant"_\n\x15TargetStakeParameters\x12\x1f\n\x0btime_window\x18\x01 \x01(\x03R\ntimeWindow\x12%\n\x0escaling_factor\x18\x02 \x01(\x01R\rscalingFactor"\xaa\x0e\n\x06Market\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12I\n\x13tradable_instrument\x18\x02 \x01(\x0b\x32\x18.vega.TradableInstrumentR\x12tradableInstrument\x12%\n\x0e\x64\x65\x63imal_places\x18\x03 \x01(\x04R\rdecimalPlaces\x12\x1e\n\x04\x66\x65\x65s\x18\x04 \x01(\x0b\x32\n.vega.FeesR\x04\x66\x65\x65s\x12>\n\x0fopening_auction\x18\x05 \x01(\x0b\x32\x15.vega.AuctionDurationR\x0eopeningAuction\x12Y\n\x19price_monitoring_settings\x18\x06 \x01(\x0b\x32\x1d.vega.PriceMonitoringSettingsR\x17priceMonitoringSettings\x12k\n\x1fliquidity_monitoring_parameters\x18\x07 \x01(\x0b\x32#.vega.LiquidityMonitoringParametersR\x1dliquidityMonitoringParameters\x12;\n\x0ctrading_mode\x18\x08 \x01(\x0e\x32\x18.vega.Market.TradingModeR\x0btradingMode\x12(\n\x05state\x18\t \x01(\x0e\x32\x12.vega.Market.StateR\x05state\x12\x43\n\x11market_timestamps\x18\n \x01(\x0b\x32\x16.vega.MarketTimestampsR\x10marketTimestamps\x12\x36\n\x17position_decimal_places\x18\x0b \x01(\x03R\x15positionDecimalPlaces\x12$\n\x0elp_price_range\x18\x0c \x01(\tR\x0clpPriceRange\x12\x34\n\x16linear_slippage_factor\x18\r \x01(\tR\x14linearSlippageFactor\x12:\n\x19quadratic_slippage_factor\x18\x0e \x01(\tR\x17quadraticSlippageFactor\x12-\n\x10parent_market_id\x18\x0f \x01(\tH\x00R\x0eparentMarketId\x88\x01\x01\x12;\n\x17insurance_pool_fraction\x18\x10 \x01(\tH\x01R\x15insurancePoolFraction\x88\x01\x01\x12\x33\n\x13successor_market_id\x18\x11 \x01(\tH\x02R\x11successorMarketId\x88\x01\x01\x12S\n\x14liquidity_sla_params\x18\x12 \x01(\x0b\x32\x1c.vega.LiquiditySLAParametersH\x03R\x12liquiditySlaParams\x88\x01\x01\x12L\n\x14liquidation_strategy\x18\x13 \x01(\x0b\x32\x19.vega.LiquidationStrategyR\x13liquidationStrategy\x12[\n\x18mark_price_configuration\x18\x14 \x01(\x0b\x32!.vega.CompositePriceConfigurationR\x16markPriceConfiguration"\xfc\x01\n\x05State\x12\x15\n\x11STATE_UNSPECIFIED\x10\x00\x12\x12\n\x0eSTATE_PROPOSED\x10\x01\x12\x12\n\x0eSTATE_REJECTED\x10\x02\x12\x11\n\rSTATE_PENDING\x10\x03\x12\x13\n\x0fSTATE_CANCELLED\x10\x04\x12\x10\n\x0cSTATE_ACTIVE\x10\x05\x12\x13\n\x0fSTATE_SUSPENDED\x10\x06\x12\x10\n\x0cSTATE_CLOSED\x10\x07\x12\x1c\n\x18STATE_TRADING_TERMINATED\x10\x08\x12\x11\n\rSTATE_SETTLED\x10\t\x12"\n\x1eSTATE_SUSPENDED_VIA_GOVERNANCE\x10\n"\xf7\x01\n\x0bTradingMode\x12\x1c\n\x18TRADING_MODE_UNSPECIFIED\x10\x00\x12\x1b\n\x17TRADING_MODE_CONTINUOUS\x10\x01\x12\x1e\n\x1aTRADING_MODE_BATCH_AUCTION\x10\x02\x12 \n\x1cTRADING_MODE_OPENING_AUCTION\x10\x03\x12#\n\x1fTRADING_MODE_MONITORING_AUCTION\x10\x04\x12\x1b\n\x17TRADING_MODE_NO_TRADING\x10\x05\x12)\n%TRADING_MODE_SUSPENDED_VIA_GOVERNANCE\x10\x06\x42\x13\n\x11_parent_market_idB\x1a\n\x18_insurance_pool_fractionB\x16\n\x14_successor_market_idB\x17\n\x15_liquidity_sla_params"r\n\x10MarketTimestamps\x12\x1a\n\x08proposed\x18\x01 \x01(\x03R\x08proposed\x12\x18\n\x07pending\x18\x02 \x01(\x03R\x07pending\x12\x12\n\x04open\x18\x03 \x01(\x03R\x04open\x12\x14\n\x05\x63lose\x18\x04 \x01(\x03R\x05\x63lose"\xd2\x01\n\x13LiquidationStrategy\x12,\n\x12\x64isposal_time_step\x18\x01 \x01(\x03R\x10\x64isposalTimeStep\x12+\n\x11\x64isposal_fraction\x18\x02 \x01(\tR\x10\x64isposalFraction\x12,\n\x12\x66ull_disposal_size\x18\x03 \x01(\x04R\x10\x66ullDisposalSize\x12\x32\n\x15max_fraction_consumed\x18\x04 \x01(\tR\x13maxFractionConsumed"\xb3\x02\n\x1b\x43ompositePriceConfiguration\x12!\n\x0c\x64\x65\x63\x61y_weight\x18\x01 \x01(\tR\x0b\x64\x65\x63\x61yWeight\x12\x1f\n\x0b\x64\x65\x63\x61y_power\x18\x02 \x01(\x04R\ndecayPower\x12\x1f\n\x0b\x63\x61sh_amount\x18\x03 \x01(\tR\ncashAmount\x12%\n\x0esource_weights\x18\x04 \x03(\tR\rsourceWeights\x12<\n\x1asource_staleness_tolerance\x18\x05 \x03(\tR\x18sourceStalenessTolerance\x12J\n\x14\x63omposite_price_type\x18\x06 \x01(\x0e\x32\x18.vega.CompositePriceTypeR\x12\x63ompositePriceType*\xa3\x01\n\x12\x43ompositePriceType\x12$\n COMPOSITE_PRICE_TYPE_UNSPECIFIED\x10\x00\x12!\n\x1d\x43OMPOSITE_PRICE_TYPE_WEIGHTED\x10\x01\x12\x1f\n\x1b\x43OMPOSITE_PRICE_TYPE_MEDIAN\x10\x02\x12#\n\x1f\x43OMPOSITE_PRICE_TYPE_LAST_TRADE\x10\x03\x42\'Z%code.vegaprotocol.io/vega/protos/vegab\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "vega.markets_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals[
        "DESCRIPTOR"
    ]._serialized_options = b"Z%code.vegaprotocol.io/vega/protos/vega"
    _globals["_COMPOSITEPRICETYPE"]._serialized_start = 7077
    _globals["_COMPOSITEPRICETYPE"]._serialized_end = 7240
    _globals["_AUCTIONDURATION"]._serialized_start = 52
    _globals["_AUCTIONDURATION"]._serialized_end = 121
    _globals["_SPOT"]._serialized_start = 123
    _globals["_SPOT"]._serialized_end = 213
    _globals["_FUTURE"]._serialized_start = 216
    _globals["_FUTURE"]._serialized_end = 602
    _globals["_PERPETUAL"]._serialized_start = 605
    _globals["_PERPETUAL"]._serialized_end = 1565
    _globals["_DATASOURCESPECTOFUTUREBINDING"]._serialized_start = 1568
    _globals["_DATASOURCESPECTOFUTUREBINDING"]._serialized_end = 1723
    _globals["_DATASOURCESPECTOPERPETUALBINDING"]._serialized_start = 1726
    _globals["_DATASOURCESPECTOPERPETUALBINDING"]._serialized_end = 1884
    _globals["_INSTRUMENTMETADATA"]._serialized_start = 1886
    _globals["_INSTRUMENTMETADATA"]._serialized_end = 1926
    _globals["_INSTRUMENT"]._serialized_start = 1929
    _globals["_INSTRUMENT"]._serialized_end = 2185
    _globals["_LOGNORMALRISKMODEL"]._serialized_start = 2188
    _globals["_LOGNORMALRISKMODEL"]._serialized_end = 2334
    _globals["_LOGNORMALMODELPARAMS"]._serialized_start = 2336
    _globals["_LOGNORMALMODELPARAMS"]._serialized_end = 2410
    _globals["_SIMPLERISKMODEL"]._serialized_start = 2412
    _globals["_SIMPLERISKMODEL"]._serialized_end = 2478
    _globals["_SIMPLEMODELPARAMS"]._serialized_start = 2481
    _globals["_SIMPLEMODELPARAMS"]._serialized_end = 2690
    _globals["_SCALINGFACTORS"]._serialized_start = 2693
    _globals["_SCALINGFACTORS"]._serialized_end = 2830
    _globals["_MARGINCALCULATOR"]._serialized_start = 2832
    _globals["_MARGINCALCULATOR"]._serialized_end = 2913
    _globals["_TRADABLEINSTRUMENT"]._serialized_start = 2916
    _globals["_TRADABLEINSTRUMENT"]._serialized_end = 3217
    _globals["_FEEFACTORS"]._serialized_start = 3219
    _globals["_FEEFACTORS"]._serialized_end = 3344
    _globals["_FEES"]._serialized_start = 3347
    _globals["_FEES"]._serialized_end = 3479
    _globals["_PRICEMONITORINGTRIGGER"]._serialized_start = 3482
    _globals["_PRICEMONITORINGTRIGGER"]._serialized_end = 3611
    _globals["_PRICEMONITORINGPARAMETERS"]._serialized_start = 3613
    _globals["_PRICEMONITORINGPARAMETERS"]._serialized_end = 3698
    _globals["_PRICEMONITORINGSETTINGS"]._serialized_start = 3700
    _globals["_PRICEMONITORINGSETTINGS"]._serialized_end = 3790
    _globals["_LIQUIDITYMONITORINGPARAMETERS"]._serialized_start = 3793
    _globals["_LIQUIDITYMONITORINGPARAMETERS"]._serialized_end = 3997
    _globals["_LIQUIDITYSLAPARAMETERS"]._serialized_start = 4000
    _globals["_LIQUIDITYSLAPARAMETERS"]._serialized_end = 4250
    _globals["_LIQUIDITYFEESETTINGS"]._serialized_start = 4253
    _globals["_LIQUIDITYFEESETTINGS"]._serialized_end = 4501
    _globals["_LIQUIDITYFEESETTINGS_METHOD"]._serialized_start = 4376
    _globals["_LIQUIDITYFEESETTINGS_METHOD"]._serialized_end = 4484
    _globals["_TARGETSTAKEPARAMETERS"]._serialized_start = 4503
    _globals["_TARGETSTAKEPARAMETERS"]._serialized_end = 4598
    _globals["_MARKET"]._serialized_start = 4601
    _globals["_MARKET"]._serialized_end = 6435
    _globals["_MARKET_STATE"]._serialized_start = 5835
    _globals["_MARKET_STATE"]._serialized_end = 6087
    _globals["_MARKET_TRADINGMODE"]._serialized_start = 6090
    _globals["_MARKET_TRADINGMODE"]._serialized_end = 6337
    _globals["_MARKETTIMESTAMPS"]._serialized_start = 6437
    _globals["_MARKETTIMESTAMPS"]._serialized_end = 6551
    _globals["_LIQUIDATIONSTRATEGY"]._serialized_start = 6554
    _globals["_LIQUIDATIONSTRATEGY"]._serialized_end = 6764
    _globals["_COMPOSITEPRICECONFIGURATION"]._serialized_start = 6767
    _globals["_COMPOSITEPRICECONFIGURATION"]._serialized_end = 7074
# @@protoc_insertion_point(module_scope)
