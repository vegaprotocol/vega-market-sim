"""vega_sim/builders/markets.py

Moule contains functions for building protobuf messages defined in
vega/protos/sources/vega/markets.proto

Attributes:
    logger (logging.Logger): module level logger
"""

import logging
import datetime

import vega_sim.proto.vega as vega_protos

from typing import Optional, Dict, List
from vega_sim.builders.exceptions import raise_custom_build_errors
from vega_sim.api.helpers import num_to_padded_int


logger = logging.getLogger(__name__)


@raise_custom_build_errors
def future_product(
    settlement_asset: str,
    quote_name: str,
    data_source_spec_for_settlement_data: vega_protos.data_source.DataSourceDefinition,
    data_source_spec_for_trading_termination: vega_protos.data_source.DataSourceDefinition,
    data_source_spec_binding: vega_protos.markets.DataSourceSpecToFutureBinding,
) -> vega_protos.markets.Future:
    return vega_protos.markets.Future(
        settlement_asset=settlement_asset,
        quote_name=quote_name,
        data_source_spec_for_settlement_data=data_source_spec_for_settlement_data,
        data_source_spec_for_trading_termination=data_source_spec_for_trading_termination,
        data_source_spec_binding=data_source_spec_binding,
    )


@raise_custom_build_errors
def data_source_spec_to_future_binding(
    settlement_data_property: str, trading_termination_property: str
) -> vega_protos.markets.DataSourceSpecToFutureBinding:
    return vega_protos.markets.DataSourceSpecToFutureBinding(
        settlement_data_property=settlement_data_property,
        trading_termination_property=trading_termination_property,
    )


# TODO: Implement build methods for spot markets
@raise_custom_build_errors
def spot() -> vega_protos.markets.Spot:
    pass


# TODO: Implement build methods for perpetual markets
@raise_custom_build_errors
def perpetual() -> vega_protos.markets.Perpetual:
    pass


@raise_custom_build_errors
def price_monitoring_parameters(
    triggers: List[vega_protos.markets.PriceMonitoringTrigger],
) -> vega_protos.markets.PriceMonitoringParameters:
    return vega_protos.markets.PriceMonitoringParameters(triggers=triggers)


@raise_custom_build_errors
def price_monitoring_trigger(
    horizon: float, probability: float, auction_extension: float
) -> vega_protos.markets.PriceMonitoringTrigger:
    return vega_protos.markets.PriceMonitoringTrigger(
        horizon=int(horizon),
        probability=str(probability),
        auction_extension=int(auction_extension),
    )


@raise_custom_build_errors
def liquidity_monitoring_parameters(
    target_stake_parameters: vega_protos.markets.TargetStakeParameters,
) -> vega_protos.markets.LiquidityMonitoringParameters:
    return vega_protos.markets.LiquidityMonitoringParameters(
        target_stake_parameters=target_stake_parameters,
    )


@raise_custom_build_errors
def target_stake_parameters(
    time_window: float, scaling_factor: float
) -> vega_protos.markets.TargetStakeParameters:
    return vega_protos.markets.TargetStakeParameters(
        time_window=int(time_window), scaling_factor=scaling_factor
    )


@raise_custom_build_errors
def log_normal_risk_model(
    risk_aversion_parameter: float,
    tau: float,
    params: vega_protos.markets.LogNormalModelParams,
) -> vega_protos.markets.LogNormalRiskModel:
    return vega_protos.markets.LogNormalRiskModel(
        risk_aversion_parameter=risk_aversion_parameter, tau=tau, params=params
    )


@raise_custom_build_errors
def log_normal_model_params(
    mu: float, r: float, sigma: float
) -> vega_protos.markets.LogNormalModelParams:
    return vega_protos.markets.LogNormalModelParams(mu=mu, r=r, sigma=sigma)


@raise_custom_build_errors
def liquidity_sla_parameters(
    price_range: float,
    commitment_min_time_fraction: float,
    performance_hysteresis_epochs: int,
    sla_competition_factor: float,
) -> vega_protos.markets.LiquiditySLAParameters:
    return vega_protos.markets.LiquiditySLAParameters(
        price_range=str(price_range),
        commitment_min_time_fraction=str(commitment_min_time_fraction),
        performance_hysteresis_epochs=performance_hysteresis_epochs,
        sla_competition_factor=str(sla_competition_factor),
    )


@raise_custom_build_errors
def liquidity_fee_settings(
    method: vega_protos.markets.LiquidityFeeSettings.Method.Value, fee_constant: float
) -> vega_protos.markets.LiquidityFeeSettings:
    liquidity_fee_settings = vega_protos.markets.LiquidityFeeSettings(
        method=method,
    )
    if fee_constant is not None:
        setattr(liquidity_fee_settings, "fee_constant", str(fee_constant))
    return liquidity_fee_settings


@raise_custom_build_errors
def liquidation_strategy(
    disposal_time_step: int,
    disposal_fraction: float,
    full_disposal_size: float,
    max_fraction_consumed: float,
) -> vega_protos.markets.LiquidationStrategy:
    return vega_protos.markets.LiquidationStrategy(
        disposal_time_step=disposal_time_step,
        disposal_fraction=str(disposal_fraction),
        full_disposal_size=num_to_padded_int(full_disposal_size, 1),
        max_fraction_consumed=str(max_fraction_consumed),
    )


@raise_custom_build_errors
def composite_price_process(
    decay_weight: float,
    decay_power: int,
    cash_amount: int,
    source_weights: List[float],
    source_staleness_tolerance: List[int],
    composite_price_type: vega_protos.markets.CompositePriceType.Value,
    data_source_spec: List[vega_protos.data_source.DataSourceDefinition] = None,
    data_source_spec_binding: List[
        vega_protos.data_source.SpecBindingForCompositePrice
    ] = None,
) -> vega_protos.markets.CompositePriceConfiguration:
    return vega_protos.markets.CompositePriceConfiguration(
        decay_weight=str(decay_weight),
        decay_power=int(decay_power),
        cash_amount=str(cash_amount),
        source_weights=[str(weight) for weight in source_weights],
        source_staleness_tolerance=[
            f"{tolerance}s" for tolerance in source_staleness_tolerance
        ],
        composite_price_type=composite_price_type,
        data_sources_spec=data_source_spec,
        data_sources_spec_binding=data_source_spec_binding,
    )
