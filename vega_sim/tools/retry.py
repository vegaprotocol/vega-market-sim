from typing import TypeVar, Callable
import time

T = TypeVar('T')

def retry(attempts: int, delay: float, func: Callable[[], T]) -> T:
    for i in range(attempts):
        try:
            return func()
        except Exception as e:
            time.sleep(delay)
            if i == attempts-1:
                raise Exception(e)
