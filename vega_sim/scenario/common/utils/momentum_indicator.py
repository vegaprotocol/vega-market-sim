from typing import List
import numpy as np


def RSI(
    prices: List,
    period: int = 7,
) -> float:
    """
    Calculate RSI (Relative Strength Index) by a given period.

    RSI calculates a ratio of the recent upward price movements to
    the absolute price movement, which implys an overbought/oversold
    of assets when the value is over/below threshold.
    """
    length = len(prices)

    # No RSI before look back period
    if length <= period:
        return None

    differences = np.diff(prices)
    up_list = [i if i > 0 else 0 for i in differences]
    dn_list = [i if i < 0 else 0 for i in differences]

    upavg = np.mean(up_list[:period])
    dnavg = -np.mean(dn_list[:period])

    # Update upavg/dnavg by exponential weighted average
    for i in range(period, length - 1):
        upavg = ((period - 1) * upavg + up_list[i]) / period
        dnavg = ((period - 1) * dnavg - dn_list[i]) / period

    rsi = 100 * (upavg / (upavg + dnavg))
    return rsi


def CMO(
    prices: List,
    period: int = 14,
) -> float:
    """
    Calculate CMO (Chande Momentum Oscillator) by a given period.

    CMO is a modified RSI, which indicates an overbought/oversold
    condition when the value over/blew certain threshold.
    """
    length = len(prices)
    if period <= length:
        return None

    differences = np.diff(prices)
    up_list = [i if i > 0 else 0 for i in differences]
    dn_list = [i if i < 0 else 0 for i in differences]

    ups = np.sum(up_list)
    dns = -np.sum(dn_list)
    cmo = 100 * (ups - dns) / (ups + dns)
    return cmo


def StochRSI(
    prices: List,
    rsi_period: int = 7,
    signal_period: int = 7,
) -> float:
    """
    Calculate StochRSI (stochatic RSI).

    StochRSI calculates the RSI relative to its range, which indicates
    an overbought/oversold condition when the value crosses above/blow
    certain threshold.
    """
    length = len(prices)

    # No RSI before look back period
    if length <= rsi_period + signal_period:
        return None

    differences = np.diff(prices)
    up_list = [i if i > 0 else 0 for i in differences]
    dn_list = [i if i < 0 else 0 for i in differences]

    upavg = np.mean(up_list[:rsi_period])
    dnavg = -np.mean(dn_list[:rsi_period])

    rsi = []
    rsi.append(100 * (upavg / (upavg + dnavg)))
    for i in range(rsi_period, length - 1):
        # Update upavg/dnavg by exponential weighted average
        upavg = ((rsi_period - 1) * upavg + up_list[i]) / rsi_period
        dnavg = ((rsi_period - 1) * dnavg - dn_list[i]) / rsi_period
        rsi.append(100 * (upavg / (upavg + dnavg)))

    current_rsi = rsi[-1]
    min_rsi = min(rsi[-signal_period:])
    max_rsi = max(rsi[-signal_period:])
    stoch_rsi = (current_rsi - min_rsi) / (max_rsi - min_rsi)
    return stoch_rsi


def APO(
    prices: List,
    fast_period: int = 12,
    slow_period: int = 26,
) -> float:
    """
    Calculate APO (Absolute Price Oscillator) under given fast/slow periods.

    APO shows the difference between two moving averages, which indicates a buy
    signal when the value rises above zero and a sell signal when it falls below zero.
    """
    length = len(prices)

    # No APO before fast/slow periods
    if length <= slow_period:
        return None

    sma = np.mean(prices[length - slow_period :])
    fma = np.mean(prices[length - fast_period :])
    return sma - fma


def MACD(
    prices: List,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
):
    """
    Calculate MACD (Moving Average Convergence Divergence)
    """
    length = len(prices)
    if length <= slow_period + signal_period:
        return None

    fast_sf = 2 / (fast_period + 1)
    slow_sf = 2 / (slow_period + 1)
    signal_sf = 2 / (signal_period + 1)

    fast_ema = []
    slow_ema = []

    fast_ema.append(np.mean(prices[:fast_period]))
    for i in range(fast_period, length):
        fast_ema.append(prices[i] * fast_sf + fast_ema[-1] * (1 - fast_sf))
    fast_ema = fast_ema[slow_period - fast_period :]

    slow_ema.append(np.mean(prices[:slow_period]))
    for i in range(slow_period, length):
        slow_ema.append(prices[i] * slow_sf + slow_ema[-1] * (1 - slow_sf))

    macd = np.array(fast_ema) - np.array(slow_ema)

    signal = []
    signal.append(np.mean(macd[:signal]))
    for i in range(signal_period, len(macd)):
        signal.append(macd[i] * signal_sf + signal[-1] * (1 - signal_sf))

    return signal[-1] - macd[-1]


# Test Indicators
if __name__ == "__main__":
    prices = [
        283.46,
        280.69,
        285.48,
        294.08,
        293.90,
        299.92,
        301.15,
        284.45,
        294.09,
        302.77,
        301.97,
        306.85,
        305.02,
        301.06,
        291.97,
    ]

    assert round(RSI(prices=prices, period=14), 2) == 55.37
    prices.append(284.18)
    assert round(RSI(prices=prices, period=14), 2) == 50.07
    prices.append(286.48)
    assert round(RSI(prices=prices, period=14), 2) == 51.55

    prices = [
        10.4,
        10.5,
        10.1,
        10.48,
        10.51,
        10.8,
        10.8,
        10.71,
        10.79,
        11.21,
        11.42,
        11.84,
    ]
