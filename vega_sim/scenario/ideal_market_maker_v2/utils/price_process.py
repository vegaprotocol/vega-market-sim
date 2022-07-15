from typing import Optional
import numpy as np


def GBM_model(T=0.2, mu=0.05, sigma=0.2, Midprice=100000):
    """
    Given the Midprice at time 0, calculate the asset price based on Geometric Brownian motion Model
    """
    Termination = int(T * 3600)
    t = np.linspace(0, Termination, Termination + 1).astype(int)
    dW = np.random.randn(len(t) - 1)
    W = np.cumsum(dW)
    W = np.insert(W, 0, 0)

    S = Midprice * np.exp((mu - 0.5 * sigma**2) * t + sigma * W)

    return t, S


def RW_model(
    random_state: Optional[np.random.RandomState] = None,
    T: float = 3 / 24 / 365.25,
    dt: float = 1 / 60 / 24 / 365.25,
    mdp: int = 5,
    sigma: float = 1,
    Midprice: float = 0.3,
):
    """
    Given the Midprice at time 0, simulate the asset price based on Random Walk Model
    """
    random_state_set = random_state is not None
    random_state = random_state if random_state_set else np.random.RandomState()

    Termination = int(T / dt)
    time_step = np.linspace(0, Termination, Termination + 1).astype(int)

    S = np.zeros(len(time_step))
    S[0] = Midprice

    while True:
        dW = random_state.randn(len(time_step) - 1)
        # Simulate external midprice
        for i in range(len(time_step) - 1):
            S[i + 1] = S[i] + sigma * dW[i]
        # market decimal place
        S = np.round(S, mdp)

        # If random state is passed then error if it generates a negative price
        # Otherwise retry with a new seed
        if (S > 0).all():
            break
        else:
            if random_state_set:
                raise Exception(
                    "Negative price generated with current random seed. Please try"
                    " another or don't specify one"
                )
            random_state = np.random.RandomState()
    return time_step, S
