import logging

from typing import Callable
from functools import wraps


def raise_custom_build_errors(func):
    @wraps(func)
    def wrapped_fn(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            raise VegaProtoValueError(ve)

    return wrapped_fn


class VegaProtoValueError(ValueError):
    def __init__(self, ve):
        logging.debug(ve)
