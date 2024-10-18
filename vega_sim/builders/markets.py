"""vega_sim/builders/markets.py

Moule contains functions for building protobuf messages defined in
vega/protos/sources/vega/markets.proto

Attributes:
    logger (logging.Logger): module level logger
"""

import logging
import datetime

import vega_protos.protos.vega as vega_protos

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
    cap: Optional[vega_protos.markets.FutureCap] = None,
) -> vega_protos.markets.Future:
    return vega_protos.markets.Future(
        settlement_asset=settlement_asset,
        quote_name=quote_name,
        data_source_spec_for_settlement_data=data_source_spec_for_settlement_data,
        data_source_spec_for_trading_termination=data_source_spec_for_trading_termination,
        data_source_spec_binding=data_source_spec_binding,
        cap=cap,
    )


@raise_custom_build_errors
def data_source_spec_to_future_binding(
    settlement_data_property: str, trading_termination_property: str
) -> vega_protos.markets.DataSourceSpecToFutureBinding:
    return vega_protos.markets.DataSourceSpecToFutureBinding(
        settlement_data_property=settlement_data_property,
        trading_termination_property=trading_termination_property,
    )


@raise_custom_build_errors
def future_cap(
    max_price: float,
    binary_settlement: bool,
    fully_collateralised: bool,
) -> vega_protos.markets.FutureCap:
    return vega_protos.markets.FutureCap(
        max_price=str(max_price),
        binary_settlement=binary_settlement,
        fully_collateralised=fully_collateralised,
    )


# TODO: Implement build methods for spot markets
@raise_custom_build_errors
def spot() -> vega_protos.markets.Spot:
    pass


# TODO: Implement build methods for perpetual markets
@raise_custom_build_errors
def perpetual(
    settlement_asset: str,
    quote_name: str,
    margin_funding_factor: float,
    interest_rate: float,
    clamp_lower_bound: float,
    clamp_upper_bound: float,
    data_source_spec_for_settlement_schedule: vega_protos.data_source.DataSourceSpec,
    data_source_spec_for_settlement_data: vega_protos.data_source.DataSourceSpec,
    data_source_spec_for_perpetual_binding: vega_protos.markets.DataSourceSpecToPerpetualBinding,
    funding_rate_scaling_factor: float,
    funding_rate_upper_bound: float,
    funding_Rate_lower_bound: float,
) -> vega_protos.markets.Perpetual:
    return vega_protos.markets.Perpetual(
        settlement_asset=settlement_asset,
        quote_name=quote_name,
        margin_funding_factor=str(margin_funding_factor),
        interest_rate=str(interest_rate),
        clamp_lower_bound=str(clamp_lower_bound),
        clamp_upper_bound=str(clamp_upper_bound),
        data_source_spec_for_settlement_schedule=data_source_spec_for_settlement_schedule,
        data_source_spec_for_settlement_data=data_source_spec_for_settlement_data,
        data_source_spec_for_perpetual_binding=data_source_spec_for_perpetual_binding,
        funding_rate_scaling_factor=str(funding_rate_scaling_factor),
        funding_Rate_lower_bound=str(funding_Rate_lower_bound),
        funding_rate_upper_bound=str(funding_rate_upper_bound),
    )


@raise_custom_build_errors
def data_source_spec_to_perpetual_binding(
    settlement_data_property: str, settlement_schedule_property: str
) -> vega_protos.markets.DataSourceSpecToPerpetualBinding:
    return vega_protos.markets.DataSourceSpecToPerpetualBinding(
        settlement_data_property=settlement_data_property,
        settlement_schedule_property=settlement_schedule_property,
    )


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
        time_window=int(time_window), scaling_factor=float(scaling_factor)
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
        performance_hysteresis_epochs=int(performance_hysteresis_epochs),
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
    disposal_slippage_range: float,
) -> vega_protos.markets.LiquidationStrategy:
    return vega_protos.markets.LiquidationStrategy(
        disposal_time_step=int(disposal_time_step),
        disposal_fraction=str(disposal_fraction),
        full_disposal_size=num_to_padded_int(full_disposal_size, 1),
        max_fraction_consumed=str(max_fraction_consumed),
        disposal_slippage_range=str(disposal_slippage_range),
    )


@raise_custom_build_errors
def composite_price_configuration(
    composite_price_type: vega_protos.markets.CompositePriceType.Value,
    decay_weight: Optional[float] = None,
    decay_power: Optional[int] = None,
    cash_amount: Optional[int] = None,
    source_weights: Optional[List[float]] = None,
    source_staleness_tolerance: Optional[List[int]] = None,
    data_sources_spec: List[vega_protos.data_source.DataSourceDefinition] = None,
    data_sources_spec_binding: List[
        vega_protos.data_source.SpecBindingForCompositePrice
    ] = None,
) -> vega_protos.markets.CompositePriceConfiguration:
    proto = vega_protos.markets.CompositePriceConfiguration(
        composite_price_type=composite_price_type,
        decay_weight=str(decay_weight) if decay_weight is not None else None,
        decay_power=int(decay_power) if decay_power is not None else None,
        cash_amount=str(cash_amount) if cash_amount is not None else None,
    )
    if source_weights is not None:
        proto.source_weights.extend([str(weight) for weight in source_weights])
    if source_staleness_tolerance is not None:
        proto.source_staleness_tolerance.extend(
            [f"{tolerance}s" for tolerance in source_staleness_tolerance]
        )
    if data_sources_spec is not None:
        proto.data_sources_spec.extend(data_sources_spec)
    if data_sources_spec_binding is not None:
        proto.data_sources_spec_binding.extend(data_sources_spec_binding)
    return proto


@raise_custom_build_errors
def data_source_spec_to_automated_purchase_binding(
    auction_schedule_property: str, auction_volume_snapshot_schedule_property
) -> vega_protos.markets.DataSourceSpecToAutomatedPurchaseBinding:
    return vega_protos.markets.DataSourceSpecToAutomatedPurchaseBinding(
        auction_schedule_property=auction_schedule_property,
        auction_volume_snapshot_schedule_property=auction_volume_snapshot_schedule_property,
    )
