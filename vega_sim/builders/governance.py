"""vega_sim/builders/governance.py

Moule contains functions for building protobuf messages defined in
vega/protos/sources/vega/governance.proto

Attributes:
    logger (logging.Logger): module level logger
"""

import logging
import datetime

import vega_sim.proto.vega as vega_protos

from typing import Optional, Dict, List
from vega_sim.api.helpers import num_to_padded_int
from vega_sim.builders.exceptions import raise_custom_build_errors


logger = logging.getLogger(__name__)


@raise_custom_build_errors
def proposal_terms(
    closing_timestamp: datetime.datetime,
    enactment_timestamp: datetime.datetime,
    validation_timestamp: Optional[datetime.datetime] = None,
    update_market: Optional[vega_protos.governance.UpdateMarket] = None,
    new_market: Optional[vega_protos.governance.NewMarket] = None,
    update_network_parameter: Optional[
        vega_protos.governance.UpdateNetworkParameter
    ] = None,
    new_asset: Optional[vega_protos.governance.NewAsset] = None,
    new_freeform: Optional[vega_protos.governance.NewFreeform] = None,
    update_asset: Optional[vega_protos.governance.UpdateAsset] = None,
    new_spot_market: Optional[vega_protos.governance.NewSpotMarket] = None,
    update_spot_market: Optional[vega_protos.governance.UpdateSpotMarket] = None,
    new_transfer: Optional[vega_protos.governance.NewTransfer] = None,
    cancel_transfer: Optional[vega_protos.governance.CancelTransfer] = None,
    update_market_state: Optional[vega_protos.governance.UpdateMarketState] = None,
    update_referral_program: Optional[
        vega_protos.governance.UpdateReferralProgram
    ] = None,
    update_volume_discount_program: Optional[
        vega_protos.governance.UpdateVolumeDiscountProgram
    ] = None,
):
    proposal_terms = vega_protos.governance.ProposalTerms(
        closing_timestamp=int(closing_timestamp.timestamp()),
        enactment_timestamp=int(enactment_timestamp.timestamp()),
    )
    if validation_timestamp is not None:
        setattr(
            proposal_terms, "validation_timestamp", validation_timestamp.timestamp()
        )
    if update_market is not None:
        proposal_terms.update_market.CopyFrom(update_market)
    if new_market is not None:
        proposal_terms.update_market.CopyFrom(new_market)
    if update_network_parameter is not None:
        proposal_terms.update_network_parameter.CopyFrom(update_network_parameter)
    if update_market is not None:
        proposal_terms.update_market.CopyFrom(update_market)
    if new_asset is not None:
        proposal_terms.new_asset.CopyFrom(new_asset)
    if new_freeform is not None:
        proposal_terms.new_freeform.CopyFrom(new_freeform)
    if update_asset is not None:
        proposal_terms.update_asset.CopyFrom(update_asset)
    if new_spot_market is not None:
        proposal_terms.new_spot_market.CopyFrom(new_spot_market)
    if update_spot_market is not None:
        proposal_terms.update_spot_market.CopyFrom(update_spot_market)
    if new_transfer is not None:
        proposal_terms.new_transfer.CopyFrom(new_transfer)
    if cancel_transfer is not None:
        proposal_terms.cancel_transfer.CopyFrom(cancel_transfer)
    if update_market_state is not None:
        proposal_terms.update_market_state.CopyFrom(update_market_state)
    if update_referral_program is not None:
        proposal_terms.update_referral_program.CopyFrom(update_referral_program)
    if update_volume_discount_program is not None:
        proposal_terms.update_volume_discount_program.CopyFrom(
            update_volume_discount_program
        )
    return proposal_terms


@raise_custom_build_errors
def proposal_rational(
    description: str, title: str
) -> vega_protos.governance.ProposalRationale:
    return vega_protos.governance.ProposalRationale(
        description=description, title=title
    )


@raise_custom_build_errors
def new_transfer(
    changes: vega_protos.governance.NewTransferConfiguration,
) -> vega_protos.governance.NewTransfer:
    return vega_protos.governance.NewTransfer(changes=changes)


@raise_custom_build_errors
def new_transfer_configuration(
    asset_decimals: Dict[str, int],
    source_type: vega_protos.vega.AccountType,
    transfer_type: vega_protos.governance.GovernanceTransferType.Value,
    amount: float,
    asset: str,
    fraction_of_balance: float,
    destination_type: vega_protos.vega.AccountType.Value,
    source: Optional[str] = None,
    destination: Optional[str] = None,
    one_off: Optional[vega_protos.governance.OneOffTransfer] = None,
    recurring: Optional[vega_protos.governance.RecurringTransfer] = None,
) -> vega_protos.governance.NewTransferConfiguration:
    new_transfer_configuration = vega_protos.governance.NewTransferConfiguration(
        source_type=source_type,
        transfer_type=transfer_type,
        amount=str(
            num_to_padded_int(to_convert=amount, decimals=asset_decimals[asset])
        ),
        asset=asset,
        fraction_of_balance=str(fraction_of_balance),
        destination_type=destination_type,
    )
    if source is not None:
        setattr(new_transfer_configuration, "source", source)
    if destination is not None:
        setattr(new_transfer_configuration, "destination", destination)
    if one_off is not None:
        new_transfer_configuration.one_off.CopyFrom(one_off)
    if recurring is not None:
        new_transfer_configuration.recurring.CopyFrom(recurring)
    return new_transfer_configuration


@raise_custom_build_errors
def one_off_transfer(
    deliver_on: Optional[datetime.datetime] = None,
) -> vega_protos.governance.OneOffTransfer:
    one_off_transfer = vega_protos.governance.OneOffTransfer()
    if deliver_on is not None:
        setattr(one_off_transfer, "deliver_on", int(deliver_on.timestamp() * 1e9))
    return one_off_transfer


@raise_custom_build_errors
def recurring_transfer(
    start_epoch: int,
    end_epoch: Optional[int] = None,
    dispatch_strategy: Optional[vega_protos.vega.DispatchStrategy] = None,
) -> vega_protos.governance.RecurringTransfer:
    recurring_transfer = vega_protos.governance.RecurringTransfer(
        start_epoch=int(start_epoch)
    )
    if end_epoch is not None:
        setattr(recurring_transfer, "end_epoch", int(end_epoch))
    if dispatch_strategy is not None:
        recurring_transfer.dispatch_strategy.CopyFrom(dispatch_strategy)
    return recurring_transfer


@raise_custom_build_errors
def vote_submission(proposal_id: str, value: vega_protos.governance.Vote.Value.Value):
    return vega_protos.commands.v1.commands.VoteSubmission(
        proposal_id=proposal_id, value=value
    )


@raise_custom_build_errors
def future_product(
    settlement_asset: str,
    quote_name: str,
    data_source_spec_for_settlement_data: vega_protos.data_source.DataSourceDefinition,
    data_source_spec_for_trading_termination: vega_protos.data_source.DataSourceDefinition,
    data_source_spec_binding: vega_protos.markets.DataSourceSpecToFutureBinding,
) -> vega_protos.governance.FutureProduct:
    return vega_protos.governance.FutureProduct(
        settlement_asset=settlement_asset,
        quote_name=quote_name,
        data_source_spec_for_settlement_data=data_source_spec_for_settlement_data,
        data_source_spec_for_trading_termination=data_source_spec_for_trading_termination,
        data_source_spec_binding=data_source_spec_binding,
    )


@raise_custom_build_errors
def perpetual_product(
    settlement_asset: str,
    quote_name: str,
    margin_funding_factor: float,
    interest_rate: float,
    clamp_lower_bound: float,
    clamp_upper_bound: float,
    data_source_spec_for_settlement_data: vega_protos.data_source.DataSourceDefinition,
    data_source_spec_for_settlement_schedule: vega_protos.data_source.DataSourceDefinition,
    data_source_spec_binding: vega_protos.markets.DataSourceSpecToPerpetualBinding,
    funding_rate_scaling_factor: Optional[float] = None,
    funding_rate_lower_bound: Optional[float] = None,
    funding_rate_upper_bound: Optional[float] = None,
) -> vega_protos.governance.PerpetualProduct:
    perpetual_product = vega_protos.governance.PerpetualProduct(
        settlement_asset=settlement_asset,
        quote_name=quote_name,
        margin_funding_factor=str(margin_funding_factor),
        interest_rate=str(interest_rate),
        clamp_lower_bound=str(clamp_lower_bound),
        clamp_upper_bound=str(clamp_upper_bound),
        data_source_spec_for_settlement_data=data_source_spec_for_settlement_data,
        data_source_spec_for_settlement_schedule=data_source_spec_for_settlement_schedule,
        data_source_spec_binding=data_source_spec_binding,
    )
    if funding_rate_scaling_factor is not None:
        setattr(
            perpetual_product,
            "funding_rate_scaling_factor",
            str(funding_rate_scaling_factor),
        )
    if funding_rate_lower_bound is not None:
        setattr(
            perpetual_product, "funding_rate_lower_bound", str(funding_rate_lower_bound)
        )
    if funding_rate_upper_bound is not None:
        setattr(
            perpetual_product, "funding_rate_upper_bound", str(funding_rate_upper_bound)
        )
    return perpetual_product


@raise_custom_build_errors
def instrument_configuration(
    name: str,
    code: str,
    future: Optional[vega_protos.governance.FutureProduct] = None,
    spot: Optional[vega_protos.governance.SpotProduct] = None,
    perpetual: Optional[vega_protos.governance.SpotProduct] = None,
) -> vega_protos.governance.InstrumentConfiguration:
    proto = vega_protos.governance.InstrumentConfiguration(
        name=name,
        code=code,
    )
    if future is not None:
        proto.future.CopyFrom(future)
    if spot is not None:
        proto.spot.CopyFrom(spot)
    if perpetual is not None:
        proto.perpetual.CopyFrom(perpetual)
    return proto


@raise_custom_build_errors
def successor_configuration(
    parent_market_id: str, insurance_pool_fraction: float
) -> vega_protos.governance.SuccessorConfiguration:
    vega_protos.governance.SuccessorConfiguration(
        parent_market_id=parent_market_id,
        insurance_pool_fraction=str(insurance_pool_fraction),
    )


@raise_custom_build_errors
def new_market_configuration(
    instrument: vega_protos.governance.InstrumentConfiguration,
    decimal_places: int,
    price_monitoring_parameters: vega_protos.markets.PriceMonitoringParameters,
    liquidity_monitoring_parameters: vega_protos.markets.LiquidityMonitoringParameters,
    log_normal: vega_protos.markets.LogNormalRiskModel,
    position_decimal_places: int,
    linear_slippage_factor: float,
    quadratic_slippage_factor: float,
    liquidity_sla_parameters: vega_protos.markets.LiquiditySLAParameters,
    liquidity_fee_settings: vega_protos.markets.LiquidityFeeSettings,
    liquidation_strategy: vega_protos.markets.LiquidationStrategy,
    mark_price_configuration: vega_protos.markets.CompositePriceConfiguration,
    metadata: Optional[List[str]] = None,
    lp_price_range: Optional[float] = None,
    successor: Optional[vega_protos.governance.SuccessorConfiguration] = None,
) -> vega_protos.governance.NewMarketConfiguration:
    proto = vega_protos.governance.NewMarketConfiguration(
        instrument=instrument,
        decimal_places=int(decimal_places),
        price_monitoring_parameters=price_monitoring_parameters,
        liquidity_monitoring_parameters=liquidity_monitoring_parameters,
        log_normal=log_normal,
        position_decimal_places=int(position_decimal_places),
        linear_slippage_factor=str(linear_slippage_factor),
        quadratic_slippage_factor=str(quadratic_slippage_factor),
        successor=successor,
        liquidity_sla_parameters=liquidity_sla_parameters,
        liquidity_fee_settings=liquidity_fee_settings,
        liquidation_strategy=liquidation_strategy,
        mark_price_configuration=mark_price_configuration,
    )
    if lp_price_range is not None:
        setattr(proto, "lp_price_range", str(lp_price_range))
    if successor is not None:
        proto.successor.CopyFrom(successor)
    if metadata is not None:
        proto.metadata.extend(metadata)
    return proto
