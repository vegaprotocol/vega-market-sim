import logging
import random
import string
import time
import math
import sys
from decimal import Decimal
from typing import Any, Callable, Optional, TypeVar, Union
import requests

from vega_sim.grpc.client import VegaCoreClient, VegaTradingDataClientV2
from vega_protos.protos.data_node.api.v2.trading_data_pb2 import (
    GetVegaTimeRequest,
)
from vega_protos.protos.vega.api.v1.core_pb2 import StatisticsRequest
from vega_protos.protos.vega.markets_pb2 import Market, Spot, Future, Perpetual
from vega_protos.protos.vega.vega_pb2 import Side
from vega_sim.tools.retry import retry

T = TypeVar("T")
TIME_FORWARD_URL = "{base_url}/api/v1/forwardtime"

logger = logging.getLogger(__name__)


class DataNodeBehindError(Exception):
    pass


class ProposalNotAcceptedError(Exception):
    pass


def generate_id(n: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + (2 * string.digits), k=n))


def get_enum(value: Union[str, T, int], enum_class: Any) -> T:
    return getattr(enum_class, value) if isinstance(value, str) else value


def enum_to_str(e: Any, val: int) -> str:
    return e.keys()[e.values().index(val)]


def num_to_padded_int(to_convert: float, decimals: int) -> int:
    return int(Decimal(str(to_convert)) * Decimal(10**decimals))


def num_from_padded_int(to_convert: Union[str, int], decimals: int) -> float:
    if not to_convert:
        return 0
    to_convert = int(to_convert) if isinstance(to_convert, str) else to_convert
    return float(to_convert) / 10**decimals


def round_to_tick(
    price: float, tick_size: int, side: Optional[Side.Value] = None
) -> float:
    ticks = int(tick_size)
    if side == Side.SIDE_BUY:
        return int(math.floor(price / ticks) * ticks)
    if side == Side.SIDE_SELL:
        return int(math.ceil(price / ticks) * ticks)
    # To avoid having to pass the side of the order for amendments
    return int(round(price / ticks) * ticks)


def wait_for_datanode_sync(
    trading_data_client: VegaTradingDataClientV2,
    core_data_client: VegaCoreClient,
    max_retries: int = 100,
) -> None:
    """Waits for Datanode to catch up to vega core client.
    Note: Will wait for datanode 'latest' time to catch up to core time
    when function is called. This avoids the case where a datanode
    consistently slightly behind the core client never returns.

    As such, this ensures that the data node has data from the core
    *at the time of call* not necessarily the latest data when the function returns.

    Wait time is exponential with increasing retries
    (each attempt waits 0.05 * 1.03^attempt_num seconds).
    """
    attempts = 1
    core_time = retry(
        10, 0.5, lambda: core_data_client.GetVegaTime(GetVegaTimeRequest()).timestamp
    )
    trading_time = retry(
        10, 0.5, lambda: trading_data_client.GetVegaTime(GetVegaTimeRequest()).timestamp
    )
    while core_time > trading_time:
        logging.debug(f"Sleeping in wait_for_datanode_sync for {0.005 * 1.1**attempts}")
        time.sleep(0.0005 * 1.1**attempts)
        try:
            trading_time = retry(
                10,
                2.0,
                lambda: trading_data_client.GetVegaTime(GetVegaTimeRequest()).timestamp,
            )
        except Exception as e:
            logging.warn(e)
            trading_time = sys.maxsize

        attempts += 1
        if attempts >= max_retries:
            raise DataNodeBehindError(
                f"Data Node is behind and not catching up after {attempts} retries"
            )


def wait_for_core_catchup(
    core_data_client: VegaCoreClient,
    max_retries: int = 200,
) -> None:
    """Waits for core node to fully execute everything in it's backlog.
    Note that this operates by a rough cut of requesting time twice and checking for it
    being unchanged, so only works on nullchain where we control time. May wait forever
    in a standard tendermint chain
    """
    attempts = 1

    core_time = retry(
        10, 0.5, lambda: core_data_client.GetVegaTime(GetVegaTimeRequest()).timestamp
    )
    time.sleep(0.0001)
    core_time_two = retry(
        10, 0.5, lambda: core_data_client.GetVegaTime(GetVegaTimeRequest()).timestamp
    )

    while core_time != core_time_two:
        logging.debug(f"Sleeping in wait_for_core_catchup for {0.05 * 1.03**attempts}")

        core_time = retry(
            10,
            0.5,
            lambda: core_data_client.GetVegaTime(GetVegaTimeRequest()).timestamp,
        )
        time.sleep(0.0001 * 1.03**attempts)
        core_time_two = retry(
            10,
            0.5,
            lambda: core_data_client.GetVegaTime(GetVegaTimeRequest()).timestamp,
        )
        attempts += 1
        if attempts >= max_retries:
            raise DataNodeBehindError(
                f"Core Node is behind and not catching up after {attempts} retries"
            )


def wait_for_acceptance(
    submission_ref: str,
    submission_load_func: Callable[[str], T],
) -> T:
    logger.debug("Waiting for proposal acceptance")
    submission_accepted = False
    for i in range(50):
        try:
            proposal = submission_load_func(submission_ref)
        except:
            time.sleep(0.001 * 1.1**i)
            continue

        if proposal:
            logger.debug("Your proposal has been accepted by the network")
            submission_accepted = True
            break
        time.sleep(0.001 * 1.1**i)

    if not submission_accepted:
        raise ProposalNotAcceptedError(
            "The network did not accept the proposal within the specified time"
        )
    return proposal


def forward(time: str, vega_node_url: str) -> None:
    """Steps chain forward a given amount of time, either with an amount of time or
        until a specified time.

    Args:
        time:
            str, time argument to use when stepping forwards. Either an increment
            (e.g. 1s, 10hr etc) or an ISO datetime (e.g. 2021-11-25T14:14:00Z)
        vega_node_url:
            str, url for a Vega nullchain node
    """
    payload = {"forward": time}

    req = requests.post(TIME_FORWARD_URL.format(base_url=vega_node_url), json=payload)
    req.raise_for_status()


def statistics(core_data_client: VegaCoreClient):
    return retry(
        10, 0.5, lambda: core_data_client.Statistics(StatisticsRequest()).statistics
    )


def get_market_asset(market: Market) -> str:
    product = get_product(market)
    if isinstance(product, Spot):
        return product.quote_asset
    if isinstance(product, Future):
        return product.settlement_asset
    if isinstance(product, Perpetual):
        return product.settlement_asset


def get_settlement_asset(market: Market) -> str:
    product = get_product(market)
    if isinstance(product, Spot):
        return None
    if isinstance(product, Future):
        return product.settlement_asset
    if isinstance(product, Perpetual):
        return product.settlement_asset


def get_base_asset(market: Market) -> str:
    product = get_product(market)
    if isinstance(product, Spot):
        return product.base_asset
    if isinstance(product, Future):
        return None
    if isinstance(product, Perpetual):
        return None


def get_quote_asset(market: Market) -> str:
    product = get_product(market)
    if isinstance(product, Spot):
        return product.quote_asset
    if isinstance(product, Future):
        return None
    if isinstance(product, Perpetual):
        return None


def get_product(market: Market) -> Any:
    product = market.tradable_instrument.instrument.WhichOneof("product")
    if product is None:
        raise Exception(f"product not set for market '{market.id}'")
    return getattr(market.tradable_instrument.instrument, product)
