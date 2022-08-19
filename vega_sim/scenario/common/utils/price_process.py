from typing import Optional
import numpy as np


def random_walk(
    num_steps: int = 100,
    random_state: Optional[np.random.RandomState] = None,
    sigma: float = 1,
    drift: float = 0,
    starting_price: float = 100,
    decimal_precision: Optional[int] = None,
    trim_to_min: Optional[float] = None,
):
    random_state_set = random_state is not None
    random_state = random_state if random_state_set else np.random.RandomState()

    S = np.zeros(num_steps)
    S[0] = starting_price

    for _ in range(100):
        dW = random_state.randn(num_steps)
        # Simulate external midprice
        for i in range(1, num_steps):
            S[i] = S[i - 1] + drift + sigma * dW[i]

        # market decimal place
        if decimal_precision:
            S = np.round(S, decimal_precision)

        # If random state is passed then error if it generates a negative price
        # Otherwise retry with a new seed

        if trim_to_min is not None:
            S[S < trim_to_min] = trim_to_min

        if (S > 0).all():
            break
        else:
            if random_state_set:
                raise Exception(
                    "Negative price generated with current random seed. Please try"
                    " another or don't specify one"
                )
            random_state = np.random.RandomState()
    if (S < 0).any():
        raise Exception("No valid price series generated after 100 attempts")
    return S
