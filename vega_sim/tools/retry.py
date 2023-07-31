from typing import TypeVar, Callable
import time
import logging

T = TypeVar("T")


def retry(attempts: int, delay: float, func: Callable[[], T]) -> T:
    for i in range(attempts):
        try:
            if i > 0:
                logging.debug(f"Retrying attempt {i}")
            result = func()

            return result
        except Exception as e:
            time.sleep(delay)
            if i == attempts - 1:
                raise Exception(e)
