import logging

from typing import Callable
from functools import wraps


def raise_custom_build_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            raise VegaProtoValueError(ve)

    return wrapper


class VegaProtoValueError(ValueError):
    def __init__(self, ve):
        logging.debug(ve)
