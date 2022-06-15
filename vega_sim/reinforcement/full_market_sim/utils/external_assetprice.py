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
    random_state=np.random.RandomState(seed=1),
    T=3 / 24 / 365.25,
    dt=1 / 60 / 24 / 365.25,
    mdp=5,
    sigma=1,
    Midprice=0.3,
):
    """
    Given the Midprice at time 0, simulate the asset price based on Random Walk Model
    """

    Termination = int(T / dt)
    time_step = np.linspace(0, Termination, Termination + 1).astype(int)
    # use seed to make sure gernerate same random number (use to compare different strategy)
    # random_state = np.random.RandomState()

    dW = np.sqrt(dt) * random_state.randn(len(time_step) - 1)
    S = np.zeros(len(time_step))
    S[0] = Midprice
    # for i in range(len(time_step)-1):
    #     S[i+1] = S[i] + sigma*dW[i]

    for i in range(len(time_step) - 1):
        S[i + 1] = S[i] * np.exp(-0.5 * sigma * sigma * dt + sigma * dW[i])

    # market decimal place
    S = np.round(S, mdp)

    # make sure the simulated external price is larger than 0
    while True:
        random_state = np.random.RandomState()
        # use seed to make sure gernerate same random number (use to compare different strategy)
        # random_state = np.random.RandomState(seed=123)
        dW = np.sqrt(dt) * random_state.randn(len(time_step) - 1)
        # Simulate external midprice
        for i in range(len(time_step) - 1):
            S[i + 1] = S[i] + sigma * dW[i]
        # market decimal place
        S = np.round(S, mdp)

        if (S > 0).all():
            break
    return time_step, S
