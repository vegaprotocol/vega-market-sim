"""vega_sim/build/commands/commands.py

Moule contains functions for building protobuf messages defined in
vega/protos/sources/vega/commands/v1/commands.proto

Attributes:
    logger (logging.Logger): module level logger
"""

import logging
import datetime

import vega_protos.protos.vega as vega_protos

from typing import Optional, Dict, List
from vega_sim.api.helpers import num_to_padded_int
from vega_sim.builders.exceptions import raise_custom_build_errors


logger = logging.getLogger(__name__)


@raise_custom_build_errors
def proposal_submission(
    reference: str,
    terms: vega_protos.governance.ProposalTerms,
    rationale: vega_protos.governance.ProposalRationale,
) -> vega_protos.commands.v1.commands.ProposalSubmission:
    return vega_protos.commands.v1.commands.ProposalSubmission(
        reference=reference, terms=terms, rationale=rationale
    )


@raise_custom_build_errors
def batch_proposal_submission(
    reference: str,
    rationale: vega_protos.governance.ProposalRationale,
    terms: vega_protos.commands.v1.commands.BatchProposalSubmissionTerms,
) -> vega_protos.commands.v1.commands.BatchProposalSubmission:
    return vega_protos.commands.v1.commands.BatchProposalSubmission(
        reference=reference,
        terms=terms,
        rationale=rationale,
    )


@raise_custom_build_errors
def transfer(
    asset_decimals: Dict[str, int],
    from_account_type: vega_protos.vega.AccountType.Value,
    to: str,
    to_account_type: vega_protos.vega.AccountType.Value,
    asset: str,
    amount: float,
    reference: str,
    one_off: Optional[vega_protos.commands.v1.commands.OneOffTransfer] = None,
    recurring: Optional[vega_protos.commands.v1.commands.RecurringTransfer] = None,
) -> vega_protos.commands.v1.commands.Transfer:
    transfer = vega_protos.commands.v1.commands.Transfer(
        from_account_type=from_account_type,
        to=to,
        to_account_type=to_account_type,
        asset=asset,
        amount=str(num_to_padded_int(amount, asset_decimals[asset])),
        reference=reference,
    )
    if recurring is not None:
        transfer.recurring.CopyFrom(recurring)
    if one_off is not None:
        transfer.one_off.CopyFrom(one_off)
    return transfer


@raise_custom_build_errors
def one_off_transfer(deliver_on: datetime.datetime):
    return vega_protos.commands.v1.commands.OneOffTransfer(
        deliver_on=int(deliver_on.timestamp() * 1e9)
    )


@raise_custom_build_errors
def recurring_transfer(
    start_epoch: int,
    factor: float,
    end_epoch: Optional[int] = None,
    dispatch_strategy: Optional[vega_protos.vega.DispatchStrategy] = None,
) -> vega_protos.commands.v1.commands.RecurringTransfer:
    recurring_transfer = vega_protos.commands.v1.commands.RecurringTransfer(
        start_epoch=start_epoch,
        factor=str(factor),
    )
    if end_epoch is not None:
        setattr(recurring_transfer, "end_epoch", int(end_epoch))
    if dispatch_strategy is not None:
        recurring_transfer.dispatch_strategy.CopyFrom(dispatch_strategy)
    return recurring_transfer


@raise_custom_build_errors
def stop_orders_submission(
    rises_above: Optional[vega_protos.commands.v1.commands.StopOrderSetup] = None,
    falls_below: Optional[vega_protos.commands.v1.commands.StopOrderSetup] = None,
) -> vega_protos.commands.v1.commands.StopOrdersSubmission:
    return vega_protos.commands.v1.commands.StopOrdersSubmission(
        rises_above=rises_above, falls_below=falls_below
    )


@raise_custom_build_errors
def stop_order_setup(
    market_price_decimals: Dict[str, int],
    market_id: str,
    order_submission: vega_protos.commands.v1.commands.OrderSubmission,
    expires_at: Optional[datetime.datetime] = None,
    expiry_strategy: Optional[vega_protos.vega.StopOrder.ExpiryStrategy.Value] = None,
    price: Optional[float] = None,
    trailing_percent_offset: Optional[float] = None,
) -> vega_protos.commands.v1.commands.StopOrderSetup:
    stop_order_setup = vega_protos.commands.v1.commands.StopOrderSetup(
        order_submission=order_submission,
        expiry_strategy=expiry_strategy,
    )
    if expires_at is not None:
        setattr(stop_order_setup, "expires_at", int(expires_at.timestamp()))
    if price is not None:
        setattr(
            stop_order_setup,
            "price",
            str(num_to_padded_int(price, market_price_decimals[market_id])),
        )
    if trailing_percent_offset is not None:
        setattr(
            stop_order_setup,
            "trailing_percent_offset",
            str(trailing_percent_offset),
        )
    return stop_order_setup


@raise_custom_build_errors
def iceberg_opts(
    market_pos_decimals: Dict[str, int],
    market_id: str,
    peak_size: float,
    minimum_visible_size: float,
) -> vega_protos.commands.v1.commands.IcebergOpts:
    return vega_protos.commands.v1.commands.IcebergOpts(
        peak_size=num_to_padded_int(peak_size, market_pos_decimals[market_id]),
        minimum_visible_size=num_to_padded_int(
            minimum_visible_size, market_pos_decimals[market_id]
        ),
    )


@raise_custom_build_errors
def pegged_order(
    market_price_decimals: Dict[str, int],
    market_id: str,
    reference: vega_protos.vega.PeggedReference.Value,
    offset: float,
) -> vega_protos.vega.PeggedOrder:
    return vega_protos.vega.PeggedOrder(
        reference=reference,
        offset=str(num_to_padded_int(offset, market_price_decimals[market_id])),
    )


@raise_custom_build_errors
def order_submission(
    market_size_decimals: Dict[str, int],
    market_price_decimals: Dict[str, int],
    market_id: str,
    size: float,
    side: vega_protos.vega.Side.Value,
    time_in_force: vega_protos.vega.Order.TimeInForce.Value,
    type: vega_protos.vega.Order.Type.Value,
    post_only: bool,
    reduce_only: bool,
    expires_at: Optional[datetime.datetime] = None,
    price: Optional[float] = None,
    reference: Optional[str] = None,
    pegged_order: Optional[vega_protos.vega.PeggedOrder] = None,
    iceberg_opts: Optional[vega_protos.commands.v1.commands.IcebergOpts] = None,
) -> vega_protos.commands.v1.commands.OrderSubmission:
    return vega_protos.commands.v1.commands.OrderSubmission(
        market_id=market_id,
        price=(
            str(num_to_padded_int(price, market_price_decimals[market_id]))
            if price is not None
            else None
        ),
        size=num_to_padded_int(size, market_size_decimals[market_id]),
        side=side,
        time_in_force=time_in_force,
        expires_at=(
            int(expires_at.timestamp() * 1e9) if expires_at is not None else None
        ),
        type=type,
        reference=reference,
        pegged_order=pegged_order,
        post_only=post_only,
        reduce_only=reduce_only,
        iceberg_opts=iceberg_opts,
    )


@raise_custom_build_errors
def order_amendment(
    market_size_decimals: Dict[str, int],
    market_price_decimals: Dict[str, int],
    order_id: str,
    market_id: str,
    time_in_force: Optional[vega_protos.vega.Order.TimeInForce.Value] = None,
    size: Optional[float] = None,
    size_delta: Optional[float] = None,
    expires_at: Optional[datetime.datetime] = None,
    price: Optional[float] = None,
    pegged_offset: Optional[float] = None,
    pegged_reference: Optional[vega_protos.vega.PeggedReference.Value] = None,
) -> vega_protos.commands.v1.commands.OrderSubmission:
    return vega_protos.commands.v1.commands.OrderAmendment(
        order_id=order_id,
        market_id=market_id,
        price=(
            str(num_to_padded_int(price, market_price_decimals[market_id]))
            if price is not None
            else None
        ),
        size_delta=(
            num_to_padded_int(size_delta, market_size_decimals[market_id])
            if size_delta is not None
            else None
        ),
        expires_at=(
            int(expires_at.timestamp() * 1e9) if expires_at is not None else None
        ),
        time_in_force=time_in_force,
        pegged_offset=(
            str(num_to_padded_int(pegged_offset, market_price_decimals[market_id]))
            if pegged_offset is not None
            else None
        ),
        pegged_reference=pegged_reference,
        size=(
            num_to_padded_int(size, market_size_decimals[market_id])
            if size is not None
            else None
        ),
    )


@raise_custom_build_errors
def submit_amm(
    market_price_decimals: Dict[str, int],
    market_asset_map: Dict[str, str],
    asset_decimals: Dict[str, int],
    market_id: str,
    commitment_amount: float,
    slippage_tolerance: float,
    proposed_fee: float,
    base: float,
    lower_bound: Optional[float] = None,
    upper_bound: Optional[float] = None,
    leverage_at_lower_bound: Optional[float] = None,
    leverage_at_upper_bound: Optional[float] = None,
) -> vega_protos.commands.v1.commands.SubmitAMM:
    # Note ConcentratedLiquidityParameters does not have a stand alone
    # function as message is nested specifically with SubmitAmm.
    return vega_protos.commands.v1.commands.SubmitAMM(
        market_id=market_id,
        commitment_amount=str(
            num_to_padded_int(
                commitment_amount, asset_decimals[market_asset_map[market_id]]
            )
        ),
        slippage_tolerance=str(slippage_tolerance),
        concentrated_liquidity_parameters=vega_protos.commands.v1.commands.SubmitAMM.ConcentratedLiquidityParameters(
            base=str(num_to_padded_int(base, market_price_decimals[market_id])),
            lower_bound=(
                str(num_to_padded_int(lower_bound, market_price_decimals[market_id]))
                if lower_bound is not None
                else None
            ),
            upper_bound=(
                str(num_to_padded_int(upper_bound, market_price_decimals[market_id]))
                if upper_bound is not None
                else None
            ),
            leverage_at_lower_bound=(
                str(leverage_at_lower_bound)
                if leverage_at_lower_bound is not None
                else None
            ),
            leverage_at_upper_bound=(
                str(leverage_at_upper_bound)
                if leverage_at_upper_bound is not None
                else None
            ),
        ),
        proposed_fee=str(proposed_fee),
    )


@raise_custom_build_errors
def amend_amm(
    market_price_decimals: Dict[str, int],
    market_asset_map: Dict[str, str],
    asset_decimals: Dict[str, int],
    market_id: str,
    commitment_amount: float,
    slippage_tolerance: float,
    proposed_fee: float,
    base: float,
    lower_bound: Optional[float] = None,
    upper_bound: Optional[float] = None,
    leverage_at_lower_bound: Optional[float] = None,
    leverage_at_upper_bound: Optional[float] = None,
) -> vega_protos.commands.v1.commands.AmendAMM:
    # Note ConcentratedLiquidityParameters does not have a stand alone
    # function as message is nested specifically with AmendAMM.
    return vega_protos.commands.v1.commands.AmendAMM(
        market_id=market_id,
        commitment_amount=str(
            num_to_padded_int(
                commitment_amount, asset_decimals[market_asset_map[market_id]]
            )
        ),
        slippage_tolerance=str(slippage_tolerance),
        concentrated_liquidity_parameters=vega_protos.commands.v1.commands.AmendAMM.ConcentratedLiquidityParameters(
            base=str(num_to_padded_int(base, market_price_decimals[market_id])),
            lower_bound=(
                str(num_to_padded_int(lower_bound, market_price_decimals[market_id]))
                if lower_bound is not None
                else None
            ),
            upper_bound=(
                str(num_to_padded_int(upper_bound, market_price_decimals[market_id]))
                if upper_bound is not None
                else None
            ),
            leverage_at_lower_bound=(
                str(leverage_at_lower_bound)
                if leverage_at_lower_bound is not None
                else None
            ),
            leverage_at_upper_bound=(
                str(leverage_at_upper_bound)
                if leverage_at_upper_bound is not None
                else None
            ),
        ),
        proposed_fee=str(proposed_fee),
    )


@raise_custom_build_errors
def cancel_amm(
    market_id: str, method: vega_protos.commands.v1.commands.CancelAMM.Method.Value
) -> vega_protos.commands.v1.commands.CancelAMM:
    return vega_protos.commands.v1.commands.CancelAMM(
        market_id=market_id, method=method
    )
