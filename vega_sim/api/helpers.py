import logging
import random
import string
import time
from typing import Any, Optional, TypeVar, Union, Callable

import requests
from vega_sim.grpc.client import VegaCoreClient, VegaTradingDataClient
from vega_sim.proto.data_node.api.v1.trading_data_pb2 import GetVegaTimeRequest


T = TypeVar("T")

TIME_FORWARD_URL = "{base_url}/api/v1/forwardtime"

logger = logging.getLogger(__name__)


class DataNodeBehindError(Exception):
    pass


class ProposalNotAcceptedError(Exception):
    pass


def generate_id(n: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + (2 * string.digits), k=n))


def get_enum(value: Union[str, T], enum_class: Any) -> T:
    return value if isinstance(value, type(enum_class)) else getattr(enum_class, value)


def enum_to_str(e: Any, val: int) -> str:
    return e.keys()[e.values().index(val)]


def num_to_padded_int(to_convert: float, decimals: int) -> float:
    return int(to_convert * 10**decimals)


def num_from_padded_int(to_convert: Union[str, int], decimals: int) -> float:
    to_convert = int(to_convert) if isinstance(to_convert, str) else to_convert
    return float(to_convert) / 10**decimals


def wait_for_datanode_sync(
    trading_data_client: VegaTradingDataClient,
    core_data_client: VegaCoreClient,
    max_retries: int = 50,
) -> None:
    """Waits for Datanode to catch up to vega core client.
    Note: Will wait for datanode 'latest' time to catch up to core time when function is called.
    This avoids the case where a datanode consistently slightly behind the core client never returns.

    As such, this ensures that the data node has data from the core *at the time of call* not necessarily the latest
    data when the function returns.
    """
    attempts = 1
    core_time = core_data_client.GetVegaTime(GetVegaTimeRequest()).timestamp
    trading_time = trading_data_client.GetVegaTime(GetVegaTimeRequest()).timestamp
    while core_time > trading_time:
        time.sleep(0.05)
        trading_time = trading_data_client.GetVegaTime(GetVegaTimeRequest()).timestamp
        attempts += 1
        if attempts >= max_retries:
            raise DataNodeBehindError(
                f"Data Node is behind and not catching up after {attempts} retries"
            )


def wait_for_acceptance(
    submission_ref: str,
    submission_load_func: Callable[[str], T],
    time_forward_fn: Optional[Callable[[None], None]] = None,
) -> T:
    logger.debug("Waiting for proposal acceptance")
    submission_accepted = False
    for _ in range(100):
        try:
            proposal = submission_load_func(submission_ref)
        except:
            if time_forward_fn is not None:
                time_forward_fn()
            time.sleep(0.1)
            continue

        if proposal:
            logger.debug("Your proposal has been accepted by the network")
            submission_accepted = True
            break
        if time_forward_fn is not None:
            time_forward_fn()
        time.sleep(0.1)

    if not submission_accepted:
        raise ProposalNotAcceptedError(
            "The market did not accept the proposal within the specified time"
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

    requests.post(
        TIME_FORWARD_URL.format(base_url=vega_node_url), json=payload
    ).raise_for_status()
