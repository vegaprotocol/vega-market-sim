from math import log, sqrt, erf

import vega_sim.proto.vega as vega_protos


def probability_of_trading(
    tau,
    mu,
    sigma,
    lower_bound: float,
    upper_bound: float,
    best_price,
    price,
    side,
):

    stdev = sigma * sqrt(tau)
    m = log(best_price) + (mu - 0.5 * sigma * sigma) * tau

    if price < lower_bound or price > upper_bound:
        return 0

    min = cdf(m, stdev, lower_bound)
    max = cdf(m, stdev, upper_bound)
    z = max - min

    if side == vega_protos.vega.SIDE_BUY:
        return (cdf(m, stdev, price) - min) / z
    else:
        return (max - cdf(m, stdev, price)) / z


def cdf(m: float, stdev: float, x: float) -> float:
    return 0.5 * (1 + erf((log(x) - m) / stdev * sqrt(2)))
