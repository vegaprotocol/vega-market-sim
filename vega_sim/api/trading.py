from __future__ import annotations

import logging
from time import time
import requests
import uuid
from google.protobuf.json_format import MessageToDict
from typing import Callable, Optional, Union

import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v1 as data_node_protos
import vega_sim.proto.vega as vega_protos
from vega_sim.api.helpers import get_enum, enum_to_str, wait_for_acceptance

logger = logging.getLogger(__name__)


class OrderRejectedError(Exception):
    pass


def submit_order(
    login_token: str,
    data_client: vac.VegaTradingDataClient,
    wallet_server_url: str,
    pub_key: str,
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
):
    """
    Submit orders as specified to required pre-existing market.
    Optionally wait for acceptance of order (raises on non-acceptance)

    Args:
        login_token:
            str, the login token returned from logging in to wallet
        data_client:
            VegaTradingDataClient, a gRPC data client to the vega data node
        wallet_server_url:
            str, URL path of the required wallet server
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
    """
    # Login wallet
    time_in_force = get_enum(time_in_force, vega_protos.vega.Order)
    side = get_enum(side, vega_protos.vega.Side)

    headers = {"Authorization": f"Bearer {login_token}"}

    if expires_at is None:
        blockchain_time = data_client.GetVegaTime(
            data_node_protos.trading_data.GetVegaTimeRequest()
        ).timestamp
        expires_at = int(blockchain_time + 120 * 1e9)  # expire in 2 minutes

    order_ref = f"{pub_key}-{uuid.uuid4()}"

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
        order_data.pegged_order = pegged_order
    if price is not None:
        order_data.price = str(price)
    if time_in_force == vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_UNSPECIFIED:
        order_data.expires_at = expires_at

    # Sign the transaction with an order submission command
    # Note: Setting propagate to true will also submit to a Vega node
    submission = {
        "orderSubmission": MessageToDict(order_data),
        "pubKey": pub_key,
        "propagate": True,
    }

    url = f"{wallet_server_url}/api/v1/command/sync"

    response = requests.post(url, headers=headers, json=submission)
    response.raise_for_status()

    logger.debug(f"Submitted Order on {side} at price {price}.")

    if wait:

        def _proposal_loader(order_ref: str) -> vega_protos.vega.Order:
            order_ref_request = data_node_protos.trading_data.OrderByReferenceRequest(
                reference=order_ref
            )
            return data_client.OrderByReference(order_ref_request).order

        # Wait for proposal to be included in a block and to be accepted by Vega network
        logger.debug("Waiting for proposal acceptance")
        try:
            response = wait_for_acceptance(order_ref, _proposal_loader)
        except Exception as e:
            logger.debug(
                "Order wasn't immediately valid, waiting before trying again,"
                f" raised {e}"
            )
            wait_fn = (
                time_forward_fn
                if time_forward_fn is not None
                else lambda: time.sleep(1)
            )
            wait_fn()
            response = wait_for_acceptance(order_ref, _proposal_loader)

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
    login_token: str,
    wallet_server_url: str,
    pub_key: str,
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
        login_token:
            str, the login token returned from logging in to wallet
        wallet_server_url:
            str, URL path of the required wallet server
        pub_key:
            str, pub key of the account placing the order
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
    headers = {"Authorization": f"Bearer {login_token}"}

    order_data = vega_protos.commands.v1.commands.OrderAmendment(
        market_id=market_id,
        order_id=order_id,
        # price is an integer. For example 123456 is a price of 1.23456,
        # assuming 5 decimal places.
        size_delta=volume_delta,
        time_in_force=time_in_force,
    )
    for name, val in [
        ("price", vega_protos.vega.Price(value=str(price))),
        ("pegged_reference", pegged_reference),
    ]:
        if val is not None:
            getattr(order_data, name).CopyFrom(val)

    for name, val in [
        ("expires_at", expires_at),
        ("pegged_offset", pegged_offset),
    ]:
        if val is not None:
            setattr(order_data, name, val)

    amendment = {
        "orderAmendment": MessageToDict(order_data),
        "pubKey": pub_key,
        "propagate": True,
    }
    # Sign the transaction with an order amendment command
    url = f"{wallet_server_url}/api/v1/command/sync"
    response = requests.post(url, headers=headers, json=amendment)
    response.raise_for_status()
    logger.debug(f"Submitted Order amendment for {order_id}.")


def cancel_order(
    login_token: str,
    wallet_server_url: str,
    pub_key: str,
    market_id: str,
    order_id: str,
):
    """
    Cancel Order

    Args:
        login_token:
            str, the login token returned from logging in to wallet
        wallet_server_url:
            str, URL path of the required wallet server
        pub_key:
            str, pub key of the account placing the order
        market_id:
            str, the ID of the required market on vega
        order_id:
            str, Identifier of the order to cancel
    """
    headers = {"Authorization": f"Bearer {login_token}"}

    cancellation = {
        "orderCancellation": MessageToDict(
            vega_protos.commands.v1.commands.OrderCancellation(
                order_id=order_id,
                market_id=market_id,
            )
        ),
        "pubKey": pub_key,
        "propagate": True,
    }

    url = f"{wallet_server_url}/api/v1/command/sync"
    response = requests.post(url, headers=headers, json=cancellation)
    response.raise_for_status()
    logger.debug(f"Cancelled order {order_id} on market {market_id}")


def submit_simple_liquidity(
    login_token: str,
    wallet_server_url: str,
    pub_key: str,
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
        login_token:
            str, the login token returned from logging in to wallet
        wallet_server_url:
            str, URL path of the required wallet server
        pub_key:
            str, pub key of the account placing the order
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
    headers = {"Authorization": f"Bearer {login_token}"}

    submission_name = (
        "liquidityProvisionSubmission"
        if not is_amendment
        else "liquidityProvisionAmendment"
    )

    submission = {
        submission_name: MessageToDict(
            vega_protos.commands.v1.commands.LiquidityProvisionSubmission(
                market_id=market_id,
                commitment_amount=str(commitment_amount),
                fee=str(fee),
                buys=[
                    vega_protos.vega.LiquidityOrder(
                        reference=reference_buy,
                        offset=str(delta_buy),
                        proportion=1,
                    )
                ],
                sells=[
                    vega_protos.vega.LiquidityOrder(
                        reference=reference_sell,
                        offset=str(delta_sell),
                        proportion=1,
                    )
                ],
            )
        ),
        "pubKey": pub_key,
        "propagate": True,
    }

    url = f"{wallet_server_url}/api/v1/command/sync"
    response = requests.post(url, headers=headers, json=submission)
    response.raise_for_status()
    logger.debug(f"Submitted liquidity on market {market_id}")
