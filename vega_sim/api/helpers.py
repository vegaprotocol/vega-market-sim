import logging
import random
import string
import time
from typing import Any, TypeVar, Union, Callable

T = TypeVar("T")

logger = logging.getLogger(__name__)


class ProposalNotAcceptedError(Exception):
    pass


def generate_id(n: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + (2 * string.digits), k=n))


def get_enum(value: Union[str, T], enum_class: Any) -> T:
    return value if isinstance(value, type(enum_class)) else getattr(enum_class, value)


def enum_to_str(e: Any, val: int) -> str:
    return e.keys()[e.values().index(val)]


def wait_for_acceptance(
    submission_ref: str,
    submission_load_func: Callable[[str], T],
) -> T:
    logger.debug("Waiting for proposal acceptance")
    submission_accepted = False
    for _ in range(100):
        time.sleep(0.5)
        proposal = submission_load_func(submission_ref)
        if proposal:
            logger.debug("Your proposal has been accepted by the network")
            submission_accepted = True
            break

    if not submission_accepted:
        raise ProposalNotAcceptedError(
            "The market did not accept the proposal within the specified time"
        )
    return proposal
