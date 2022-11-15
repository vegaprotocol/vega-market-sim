from __future__ import annotations
from asyncio import wait_for

import logging
import uuid
from time import time
from typing import Callable, List, Optional, Tuple, Union

import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v2 as data_node_protos_v2

import vega_sim.api.data as data
import vega_sim.api.data_raw as data_raw


import vega_sim.proto.vega as vega_protos
from vega_sim.proto.vega.commands.v1.commands_pb2 import (
    OrderCancellation,
    OrderAmendment,
    OrderSubmission,
)
from vega_sim.api.helpers import (
    ProposalNotAcceptedError,
    enum_to_str,
    get_enum,
    wait_for_acceptance,
    wait_for_core_catchup,
)
from vega_sim.wallet.base import Wallet

logger = logging.getLogger(__name__)


class OrderRejectedError(Exception):
    pass


def submit_order(
    wallet_name: str,
    data_client: vac.VegaTradingDataClientV2,
    wallet: Wallet,
    market_id: str,
    order_type: Union[vega_protos.vega.Order.Type, str],
    time_in_force: Union[vega_protos.vega.Order.TimeInForce, str],
    side: Union[vega_protos.vega.Side, str],
    volume: float,
    price: Optional[str] = None,
    expires_at: Optional[int] = None,
    pegged_order: Optional[vega_protos.vega.PeggedOrder] = None,
    wait: bool = True,
    time_forward_fn: Optional[Callable[[], None]] = None,
    order_ref: Optional[str] = None,
    key_name: Optional[str] = None,
) -> Optional[str]:
    """
    Submit orders as specified to required pre-existing market.
    Optionally wait for acceptance of order (raises on non-acceptance)

    Args:
        wallet_name:
            str, the wallet name performing the action
        data_client:
            VegaTradingDataClientV2, a gRPC data client to the vega data node
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
            str, price of the order
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
        key_name:
            Optional[str], key name stored in metadata. Defaults to None.

    Returns:
        Optional[str], Order ID if wait is True, otherwise None
    """

    order_data = order_submission(
        data_client=data_client,
        market_id=market_id,
        size=volume,
        side=side,
        time_in_force=time_in_force,
        order_type=order_type,
        expires_at=expires_at,
        reference=order_ref,
        price=price,
        pegged_order=pegged_order,
    )

    # Sign the transaction with an order submission command
    # Note: Setting propagate to true will also submit to a Vega node
    wallet.submit_transaction(
        transaction=order_data,
        name=wallet_name,
        transaction_type="order_submission",
        key_name=key_name,
    )

    logger.debug(f"Submitted Order on {side} at price {price}.")

    if wait:

        def _proposal_loader(
            order_ref: str, market_id: str, data_client: vac.VegaTradingDataClientV2
        ) -> vega_protos.vega.Order:
            orders = data_raw.list_orders(
                market_id=market_id,
                reference=order_ref,
                data_client=data_client,
                live_only=False,
            )
            return orders[0]

        try:
            time_forward_fn()
            logger.debug("Waiting for proposal acceptance")
            response = wait_for_acceptance(
                order_data.reference,
                lambda r: _proposal_loader(r, market_id, data_client),
            )
        except ProposalNotAcceptedError:
            time_forward_fn()
            response = wait_for_acceptance(
                order_data.reference,
                lambda r: _proposal_loader(r, market_id, data_client),
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
    price: Optional[str] = None,
    expires_at: Optional[int] = None,
    pegged_offset: Optional[str] = None,
    pegged_reference: Optional[vega_protos.vega.PeggedReference] = None,
    volume_delta: float = 0,
    time_in_force: Optional[Union[vega_protos.vega.Order.TimeInForce, str]] = None,
    key_name: Optional[str] = None,
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
            str, price of the order
        time_in_force:
            vega.Order.TimeInForce or str, The time in force setting for the order
                (Only valid options for market are TIME_IN_FORCE_IOC and
                    TIME_IN_FORCE_FOK)
                See API documentation for full list of options
                Defaults to Fill or Kill
        key_name:
            Optional[str], key name stored in metadata. Defaults to None.
    """

    order_data = order_amendment(
        order_id=order_id,
        market_id=market_id,
        price=price,
        size_delta=volume_delta,
        expires_at=expires_at,
        time_in_force=time_in_force,
        pegged_offset=pegged_offset,
        pegged_reference=pegged_reference,
    )

    wallet.submit_transaction(
        transaction=order_data,
        name=wallet_name,
        transaction_type="order_amendment",
        key_name=key_name,
    )
    logger.debug(f"Submitted Order amendment for {order_id}.")


def cancel_order(
    wallet_name: str,
    wallet: Wallet,
    market_id: str,
    order_id: str,
    key_name: Optional[str] = None,
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

    order_data = order_cancellation(
        order_id=order_id,
        market_id=market_id,
    )

    wallet.submit_transaction(
        transaction=order_data,
        name=wallet_name,
        transaction_type="order_cancellation",
        key_name=key_name,
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
    key_name: Optional[str] = None,
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
        key_name=key_name,
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
    key_name: Optional[str] = None,
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
        key_name:
            Optional[str], key name stored in metadata. Defaults to None.
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
        transaction=submission,
        name=wallet_name,
        transaction_type=submission_name,
        key_name=key_name,
    )
    logger.debug(f"Submitted liquidity on market {market_id}")


def pegged_order(
    reference: vega_protos.vega.PeggedReference,
    offset: str,
) -> vega_protos.vega.PeggedOrder:
    """Creates a Vega PeggedOrder object.

    Args:
        reference (vega_protos.vega.PeggedReference):
            Reference to offset price from.
        offset (str):
            Value to offset price from reference.

    Returns:
        vega_protos.vega.PeggedOrder:
            The created Vega PeggedOrder object.
    """
    return vega_protos.vega.PeggedOrder(
        reference=reference,
        offset=offset,
    )


def order_amendment(
    order_id: str,
    market_id: str,
    price: str,
    size_delta: int,
    expires_at: Optional[int] = None,
    time_in_force: Optional[vega_protos.vega.Order.TimeInForce] = None,
    pegged_offset: Optional[str] = None,
    pegged_reference: Optional[vega_protos.vega.PeggedReference] = None,
) -> OrderAmendment:
    """Creates a Vega OrderAmendment object.

    Args:
        order_id (str):
            Id of order to amend.
        market_id (str):
            Id of market containing order to amend.
        price (str):
            New price of the order.
        size_delta (int):
            Amount to change the order size by.
        expires_at (Optional[int]):
            Timestamp of order expiry. Defaults to None.
        time_in_force (Optional[vega_protos.vega.Order.TimeInForce]):
            New time_in_force option for order. Defaults to None.
        pegged_offset (Optional[str]):
            New amount to offset order price by from reference. Defaults to None.
        pegged_reference (Optional[vega_protos.vega.PeggedReference]):
            New reference to offset order price from. Defaults to None.

    Returns:
        OrderAmendment:
            The created Vega OrderAmendment object.
    """

    time_in_force = (
        time_in_force
        if time_in_force is not None
        else vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_UNSPECIFIED
    )

    time_in_force = get_enum(time_in_force, vega_protos.vega.Order.TimeInForce)

    if pegged_reference is not None:
        pegged_reference = get_enum(pegged_reference, vega_protos.vega.PeggedReference)

    command = OrderAmendment(
        order_id=order_id,
        market_id=market_id,
        size_delta=size_delta,
        time_in_force=time_in_force,
    )

    # Update OrderSubmission object with optional fields if specified
    for attr, val in [
        ("price", price),
        ("expires_at", expires_at),
        ("pegged_offset", pegged_offset),
        ("pegged_reference", pegged_reference),
    ]:
        if val is not None:
            setattr(command, attr, val)

    # Return the created and updated OrderSubmission object
    return command


def order_cancellation(
    order_id: str,
    market_id: str,
) -> OrderCancellation:
    """Creates a Vega OrderCancellation object.

    Args:
        order_id (str):
            Id of order to cancel.
        market_id (str):
            Id of market containing order to cancel.

    Returns:
        OrderCancellation:
            The created Vega OrderCancellation object.
    """
    return OrderCancellation(
        order_id=order_id,
        market_id=market_id,
    )


def order_submission(
    data_client: vac.VegaTradingDataClient,
    market_id: str,
    size: int,
    side: Union[vega_protos.vega.Side, str],
    time_in_force: Union[vega_protos.vega.Order.TimeInForce, str],
    order_type: Union[vega_protos.vega.Order.Type, str],
    expires_at: Optional[int] = None,
    reference: Optional[str] = None,
    price: Optional[str] = None,
    pegged_order: Optional[Union[vega_protos.PeggedOrder, str]] = None,
) -> OrderSubmission:
    """Creates a Vega OrderSubmission object.

    Args:
        data_client (vac.VegaTradingDataClient):
            Client for trading data api.
        market_id (str):
            Id of market to place order in.
        size (int):
            Size of order to be placed.
        side (Union[vega_protos.vega.Side, str]):
            Side of order to be placed, "SIDE_BUY" or "SIDE_SELL".
        time_in_force (Union[vega_protos.vega.Order.TimeInForce, str]):
            Time in force option for order.
        order_type (Union[vega_protos.vega.Order.Type, str]):
            Type of order, "TYPE_LIMIT" or "TYPE_MARKET".
        expires_at (Optional[int]):
            Determines timestamp at which order expires, only required for orders of
            "TYPE_LIMIT" and "TIME_IN_FORCE_GTT". Defaults to None.
        reference (Optional[str]):
            Reference id to use for order. Defaults to None.
        price (Optional[str]):
            Price to place order at, only required for "TYPE_LIMIT". Defaults to None.
        pegged_order (Optional[Union[vega_protos.PeggedOrder, str]]):
            PeggedOrder object defining whether order is pegged. Defaults to None.

    Returns:
        OrderSubmission:
            The created Vega OrderSubmission object.
    """

    side = get_enum(side, vega_protos.vega.Side)
    order_type = get_enum(order_type, vega_protos.vega.Order.Type)
    time_in_force = get_enum(time_in_force, vega_protos.vega.Order.TimeInForce)

    # Ensure no expires_at field set if TIF is not TIME_IN_FORCE_GTT
    if time_in_force != vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_GTT:
        expires_at = None
    # Ensure an expires_at field set if TIF is TIME_IN_FORCE_GTT
    elif expires_at is None:
        blockchain_time = data_client.GetVegaTime(
            data_node_protos_v2.trading_data.GetVegaTimeRequest()
        ).timestamp
        expires_at = int(blockchain_time + 120 * 1e9)  # expire in 2 minutes

    reference = str(uuid.uuid4()) if reference is None else reference

    # Create OrderSubmission object with required fields
    command = OrderSubmission(
        market_id=market_id,
        size=size,
        side=side,
        time_in_force=time_in_force,
        type=order_type,
    )

    # Update OrderSubmission object with optional fields if specified
    for attr, val in [
        ("price", price),
        ("expires_at", expires_at),
        ("reference", reference),
    ]:
        if val is not None:
            setattr(command, attr, val)

    if pegged_order is not None:
        command.pegged_order.CopyFrom(pegged_order)

    # Return the created and updated OrderSubmission object
    return command


def batch_market_instructions(
    wallet: Wallet,
    wallet_name: str,
    key_name: Optional[str] = None,
    amendments: Optional[List[OrderAmendment]] = [],
    submissions: Optional[List[OrderSubmission]] = [],
    cancellations: Optional[List[OrderCancellation]] = [],
):
    """Submits a batch of market instructions.

    Args:
        wallet (Wallet):
            Wallet client used to submit transaction.
        wallet_name (str):
            Name of wallet to submit transaction.
        key_name (Optional[str], optional):
            Name of key to submit transaction. Defaults to None.
        amendments (Optional[List[OrderAmendment]]):
            List of OrderAmendment objects to process sequentially. Defaults to [].
        submissions (Optional[List[OrderSubmission]]):
            List of OrderSubmission objects to process sequentially. Defaults to [].
        cancellations (Optional[ List[OrderCancellation] ]):
            List of OrderCancellation objects to process sequentially. Defaults to [].
    """

    command = vega_protos.commands.v1.commands.BatchMarketInstructions(
        submissions=submissions, amendments=amendments, cancellations=cancellations
    )

    wallet.submit_transaction(
        transaction=command,
        name=wallet_name,
        transaction_type="batch_market_instructions",
        key_name=key_name,
    )
    logger.debug(
        f"Submitted a batch of {len(cancellations)} cancellation, {len(amendments)} amendment, and {len(submissions)} submission instructions."
    )
