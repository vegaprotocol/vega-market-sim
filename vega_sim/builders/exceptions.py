import logging

from typing import Callable


def raise_custom_build_errors(func: Callable):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            raise VegaProtoValueError(ve)
    return inner


class VegaProtoValueError(ValueError):
    def __init__(self, ve):
        logging.debug(ve)