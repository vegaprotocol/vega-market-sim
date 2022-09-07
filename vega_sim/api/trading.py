from __future__ import annotations

import logging
import uuid
from time import time
from typing import Callable, List, Optional, Tuple, Union

import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v1 as data_node_protos
import vega_sim.proto.vega as vega_protos
from vega_sim.api.helpers import enum_to_str, get_enum, wait_for_acceptance
from vega_sim.wallet.base import Wallet

logger = logging.getLogger(__name__)


class OrderRejectedError(Exception):
    pass


def submit_order(
    wallet_name: str,
    data_client: vac.VegaTradingDataClient,
    wallet: Wallet,
    market_id: str,
    order_type: Union[vega_protos.vega.Order.Type, str],
    time_in_force: Union[vega_protos.vega.Order.TimeInForce, str],
    side: Union[vega_protos.vega.Side, str],
    volume: float,
    price: Optional[float] = None,
    expires_at: Optional[int] = None,
    pegged_order: Optional[vega_protos.vega.PeggedOrder] = None,
    wait: bool = True,
    time_forward_fn: Optional[Callable[[], None]] = None,
    order_ref: Optional[str] = None,
) -> Optional[str]:
    """
    Submit orders as specified to required pre-existing market.
    Optionally wait for acceptance of order (raises on non-acceptance)

    Args:
        wallet_name:
            str, the wallet name performing the action
        data_client:
            VegaTradingDataClient, a gRPC data client to the vega data node
        wallet:
            Wallet, wallet client
        pub_key:
            str, pub key of the account placing the order
        market_id:
            str, the ID of the required market on vega
        order_type:
            vega.Order.Type or str, The type of order required (market/limit etc).
                See API documentation for full list of options
        time_in_force:
            vega.Order.TimeInForce or str, The time in force setting for the order
                (GTC, GTT, Fill Or Kill etc.)
                See API documentation for full list of options
        side:
            vega.Side or str, Side of the order (BUY or SELL)
        volume:
            float, volume of the order
        price:
            float, price of the order
        expires_at:
            int, Optional timestamp for when the order will expire, in
            nanoseconds since the epoch,
                required field only for [`Order.TimeInForce`].
                Defaults to 2 minutes
        pegged_order:
            vega.PeggedOrder, Used to specify the details for a pegged order
        wait:
            bool, whether to wait for order acceptance.
                If true, will raise an error if order is not accepted
        time_forward_fn:
            optional function, Function which takes no arguments and
            waits or manually forwards the chain when waiting for order acceptance
        order_ref:
            optional str, reference for later identification of order
    Returns:
        Optional[str], Order ID if wait is True, otherwise None
    """
    # Login wallet
    time_in_force = get_enum(time_in_force, vega_protos.vega.Order)
    side = get_enum(side, vega_protos.vega.Side)

    if expires_at is None:
        blockchain_time = data_client.GetVegaTime(
            data_node_protos.trading_data.GetVegaTimeRequest()
        ).timestamp
        expires_at = int(blockchain_time + 120 * 1e9)  # expire in 2 minutes

    order_ref = (
        f"{wallet.public_key(wallet_name)}-{uuid.uuid4()}"
        if order_ref is None
        else order_ref
    )

    order_data = vega_protos.commands.v1.commands.OrderSubmission(
        market_id=market_id,
        # price is an integer. For example 123456 is a price of 1.23456,
        # assuming 5 decimal places.
        side=side,
        size=volume,
        time_in_force=time_in_force,
        type=order_type,
        reference=order_ref,
    )
    if pegged_order is not None:
        order_data.pegged_order.CopyFrom(pegged_order)
    if price is not None:
        order_data.price = str(price)
    if time_in_force == vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_UNSPECIFIED:
        order_data.expires_at = expires_at

    # Sign the transaction with an order submission command
    # Note: Setting propagate to true will also submit to a Vega node
    wallet.submit_transaction(
        transaction=order_data, name=wallet_name, transaction_type="order_submission"
    )

    logger.debug(f"Submitted Order on {side} at price {price}.")

    if wait:

        def _proposal_loader(order_ref: str) -> vega_protos.vega.Order:
            order_ref_request = data_node_protos.trading_data.OrderByReferenceRequest(
                reference=order_ref
            )
            return data_client.OrderByReference(order_ref_request).order

        time_forward_fn()
        # Wait for proposal to be included in a block and to be accepted by Vega network
        logger.debug("Waiting for proposal acceptance")
        response = wait_for_acceptance(
            order_ref,
            _proposal_loader,
        )
        order_status = enum_to_str(vega_protos.vega.Order.Status, response.status)

        logger.debug(
            f"Order processed, ID: {response.id}, Status: {order_status}, Version:"
            f" {response.version}"
        )
        if order_status == "STATUS_REJECTED":
            raise OrderRejectedError(
                "Rejection reason:"
                f" {enum_to_str(vega_protos.vega.OrderError, response.reason)}"
            )
        return response.id


def amend_order(
    wallet_name: str,
    wallet: Wallet,
    market_id: str,
    order_id: str,
    price: Optional[float] = None,
    expires_at: Optional[int] = None,
    pegged_offset: Optional[str] = None,
    pegged_reference: Optional[vega_protos.vega.PeggedReference] = None,
    volume_delta: float = 0,
    time_in_force: Optional[Union[vega_protos.vega.Order.TimeInForce, str]] = None,
):
    """
    Amend a Limit order by orderID in the specified market

    Args:
        wallet_name:
            str, the wallet name performing the action
        wallet:
            Wallet, wallet client
        market_id:
            str, the ID of the required market on vega
        order_type:
            vega.Order.Type or str, The type of order required (market/limit etc).
                See API documentation for full list of options
        side:
            vega.Side or str, Side of the order (BUY or SELL)
        volume_delta:
            float, change in volume of the order
        price:
            float, price of the order
        time_in_force:
            vega.Order.TimeInForce or str, The time in force setting for the order
                (Only valid options for market are TIME_IN_FORCE_IOC and
                    TIME_IN_FORCE_FOK)
                See API documentation for full list of options
                Defaults to Fill or Kill
    """
    # Login wallet
    time_in_force = (
        time_in_force
        if time_in_force is not None
        else vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_UNSPECIFIED
    )

    order_data = vega_protos.commands.v1.commands.OrderAmendment(
        market_id=market_id,
        order_id=order_id,
        # price is an integer. For example 123456 is a price of 1.23456,
        # assuming 5 decimal places.
        size_delta=volume_delta,
        time_in_force=time_in_force,
    )
    for name, val in [
        ("expires_at", expires_at),
        ("pegged_offset", pegged_offset),
        ("pegged_reference", pegged_reference),
        ("price", str(price) if price is not None else None),
    ]:
        if val is not None:
            setattr(order_data, name, val)

    wallet.submit_transaction(
        transaction=order_data, name=wallet_name, transaction_type="order_amendment"
    )
    logger.debug(f"Submitted Order amendment for {order_id}.")


def cancel_order(
    wallet_name: str,
    wallet: Wallet,
    market_id: str,
    order_id: str,
):
    """
    Cancel Order

    Args:
        wallet_name:
            str, the wallet name performing the action
        wallet:
            Wallet, wallet client
        market_id:
            str, the ID of the required market on vega
        order_id:
            str, Identifier of the order to cancel
    """
    wallet.submit_transaction(
        transaction=vega_protos.commands.v1.commands.OrderCancellation(
            order_id=order_id,
            market_id=market_id,
        ),
        name=wallet_name,
        transaction_type="order_cancellation",
    )

    logger.debug(f"Cancelled order {order_id} on market {market_id}")


def submit_simple_liquidity(
    wallet_name: str,
    wallet: Wallet,
    market_id: str,
    commitment_amount: int,
    fee: float,
    reference_buy: str,
    reference_sell: str,
    delta_buy: int,
    delta_sell: int,
    is_amendment: bool = False,
):
    """Submit/Amend a simple liquidity commitment (LP) with a single amount on each side.

    Args:
        wallet_name:
            str, the wallet name performing the action
        wallet:
            Wallet, wallet client
        market_id:
            str, The ID of the market to place the commitment on
        commitment_amount:
            int, The amount in asset decimals of market asset to commit to liquidity provision
        fee:
            float, The fee level at which to set the LP fee (in %, e.g. 0.01 == 1% and 1 == 100%)
        reference_buy:
            str, the reference point to use for the buy side of LP
        reference_sell:
            str, the reference point to use for the sell side of LP
        delta_buy:
            int, the offset from reference point for the buy side of LP
        delta_sell:
            int, the offset from reference point for the sell side of LP
    """
    return submit_liquidity(
        wallet_name=wallet_name,
        wallet=wallet,
        market_id=market_id,
        commitment_amount=commitment_amount,
        fee=fee,
        buy_specs=[(reference_buy, delta_buy, 1)],
        sell_specs=[(reference_sell, delta_sell, 1)],
        is_amendment=is_amendment,
    )


def submit_liquidity(
    wallet_name: str,
    wallet: Wallet,
    market_id: str,
    commitment_amount: int,
    fee: float,
    buy_specs: List[Tuple[str, int, int]],
    sell_specs: List[Tuple[str, int, int]],
    is_amendment: bool = False,
):
    """Submit/Amend a custom liquidity profile.

    Args:
        wallet_name:
            str, the wallet name performing the action
        wallet:
            Wallet, wallet client
        market_id:
            str, The ID of the market to place the commitment on
        commitment_amount:
            int, The amount in asset decimals of market asset to commit
            to liquidity provision
        fee:
            float, The fee level at which to set the LP fee
             (in %, e.g. 0.01 == 1% and 1 == 100%)
        buy_specs:
            List[Tuple[str, int, int]], List of tuples, each containing a reference
            point in their first position, a desired offset in their second and
            a proportion in third
        sell_specs:
            List[Tuple[str, int, int]], List of tuples, each containing a reference
            point in their first position, a desired offset in their second and
            a proportion in third
    """

    if is_amendment:
        command = vega_protos.commands.v1.commands.LiquidityProvisionAmendment
        submission_name = "liquidity_provision_amendment"
    else:
        command = vega_protos.commands.v1.commands.LiquidityProvisionSubmission
        submission_name = "liquidity_provision_submission"

    submission = command(
        market_id=market_id,
        commitment_amount=str(commitment_amount),
        fee=str(fee),
        buys=[
            vega_protos.vega.LiquidityOrder(
                reference=spec[0],
                offset=str(spec[1]),
                proportion=spec[2],
            )
            for spec in buy_specs
        ],
        sells=[
            vega_protos.vega.LiquidityOrder(
                reference=spec[0],
                offset=str(spec[1]),
                proportion=spec[2],
            )
            for spec in sell_specs
        ],
    )
    wallet.submit_transaction(
        transaction=submission, name=wallet_name, transaction_type=submission_name
    )
    logger.debug(f"Submitted liquidity on market {market_id}")
