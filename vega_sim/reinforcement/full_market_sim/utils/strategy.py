import numpy as np
from scipy.linalg import expm


def A_S_MMmodel(
    T: float,
    dt: float,
    length: int,
    mdp: int,
    q_upper: int,
    q_lower: int,
    kappa: int,
    lmbda: int,
    alpha: float,
    phi: float,
):

    """
    Simulate an Market Making Model and output the optimal strategy
      of posting bid/ask depth based on market parameters.

    Args:
        T:
            int, total simulation time
        dt:
            float, the increment of each time step
        length:
            int, total time steps
        mdp:
            int, market decimal place
        q_upper:
            int, upper bound of the inventory of MM specified in the model
        q_lower:
            int, lower bound of the inventory of MM specified in the model
        kappa:
            int, market parameter to represnet the probability of pegged LOs to be hit
        lmbda:
            int, market parameter to represnet the coming rate of MOs
        alpha:
            float, risk aversion parameter to represnet terminal penalty coefficient
        phi:
            float, risk aversion parameter to represnet running penalty coefficient
    """
    # Unify unit to minute in MM Model
    T *= 60 * 24 * 365.25
    dt *= 60 * 24 * 365.25

    # Initialize 2-d arrays to store optimal strategy
    optimal_depth_bid = np.zeros([length, q_upper - q_lower])
    optimal_depth_ask = np.zeros([length, q_upper - q_lower])

    # Let A be a (q_upper-q_lower+1)-square matrix
    A = np.zeros([q_upper - q_lower + 1, q_upper - q_lower + 1])
    # w, time * (q_upper-q_lower+1)-dim matrix, to store the solution of ODE
    #   row corresponds to time_step, column corresponds to inventory q
    w = np.zeros([length, q_upper - q_lower + 1])

    # A is the coefficient matrix of ODE
    for i in range(q_upper - q_lower + 1):
        for j in range(q_upper - q_lower + 1):
            # i denotes row/ j denotes column
            if j == i:
                A[i, j] = -kappa * phi * (q_upper - i) ** 2
            elif j == i + 1:
                A[i, j] = lmbda * np.e**-1
            elif j == i - 1:
                A[i, j] = lmbda * np.e**-1

    # z, (q_upper-q_lower+1)-dim vector, denotes the terminal condition of ODE
    z = np.array(
        [np.exp(-alpha * kappa * j**2) for j in range(q_upper, q_lower - 1, -1)]
    )

    for i in range(length):
        # at each time_step
        w[i, :] = np.dot(expm(A * (T - i * dt)), z)

    # h is the transformation of solution from ODE
    #   also the key term of value function
    h = np.log(w) / kappa

    # Calculate optimal strategy
    for i in range(q_upper - q_lower):
        # column corresponds to Q, Q-1,..., -Q+1
        optimal_depth_ask[:, i] = 1 / kappa + h[:, i] - h[:, i + 1]

    for i in range(1, q_upper - q_lower + 1):
        # column corresponds to Q-1, Q-2,..., -Q
        optimal_depth_bid[:, i - 1] = 1 / kappa + h[:, i] - h[:, i - 1]

    # In A_S model, optimal depth can be negative, however, in Vega,
    #   offset must be positive and notice the market precision
    optimal_depth_bid = np.round(optimal_depth_bid, mdp)
    optimal_depth_ask = np.round(optimal_depth_ask, mdp)
    # So, if the depth is negative, replace with the minimum tick size
    optimal_depth_bid[optimal_depth_bid <= 0] = 1 / 10**mdp
    optimal_depth_ask[optimal_depth_ask <= 0] = 1 / 10**mdp

    return optimal_depth_bid, optimal_depth_ask, h


def GLFT_approx(
    q_upper: int,
    q_lower: int,
    kappa: int,
    lmbda: int,
    alpha: float,
    phi: float,
):
    """
    One problem of A_S Market Making model is cannot handle large exponential matrix
      when terminal time T, or market parameters kappa/lmbda, are large enough.
      The GLFT formula is to explore the asymptotic behavior of the optimal strategy,
      assuming T -> infty.

     Args:
        q_upper:
            int, upper bound of the inventory of MM specified in the model
        q_lower:
            int, lower bound of the inventory of MM specified in the model
        kappa:
            int, market parameter to represnet the probability of pegged LOs to be hit
        lmbda:
            int, market parameter to represnet the coming rate of MOs
        alpha:
            float, risk aversion parameter to represnet terminal penalty coefficient
        phi:
            float, risk aversion parameter to represnet running penalty coefficient
    """

    # approximation method
    delta_buy_approx = [
        1 / kappa + (2 * i + 1) * np.sqrt(phi * np.e / lmbda / kappa) / 2
        for i in range(q_upper - 1, q_lower - 1, -1)
    ]
    delta_sell_approx = [
        1 / kappa - (2 * i - 1) * np.sqrt(phi * np.e / lmbda / kappa) / 2
        for i in range(q_upper, q_lower, -1)
    ]

    return delta_buy_approx, delta_sell_approx
