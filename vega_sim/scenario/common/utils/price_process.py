import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from vega_sim.api.helpers import num_from_padded_int
import time
import os
import logging

import numpy as np
import pandas as pd
import requests
import json
import threading
import websocket

COINBASE_REQUEST_BASE = "https://api.exchange.coinbase.com/products"
COINBASE_CANDLE_BASE = COINBASE_REQUEST_BASE + "/{product_id}/candles"


class Granularity(Enum):
    MINUTE = 60
    FIVE_MINUTE = 300
    FIFTEEN_MINUTE = 900
    HOUR = 3600
    SIX_HOUR = 21600
    DAY = 86400


# Represents positions in the returned array
class CoinbaseCandle(Enum):
    TIME = 0
    LOW = 1
    HIGH = 2
    OPEN = 3
    CLOSE = 4
    VOLUME = 5


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

    S = np.zeros(num_steps + 1)
    S[0] = starting_price

    for _ in range(100):
        dW = random_state.randn(num_steps + 1)
        # Simulate external midprice
        for i in range(1, len(S)):
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


def get_trading_pairs() -> List[Dict[str, Any]]:
    headers = {"Accept": "application/json"}
    return requests.get(COINBASE_REQUEST_BASE, headers=headers).json()


def get_historic_candles(
    product_id: str,
    granularity: Optional[Granularity] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> List[List[Union[int, float]]]:
    headers = {"Accept": "application/json"}
    params = {}
    if granularity is not None:
        params["granularity"] = granularity.value
    if (start is not None) or (end is not None):
        if end is None or start is None:
            raise Exception(
                "Both start and end must be specified or the specified one is ignored"
            )
        params["start"] = start
        params["end"] = end

    if start is None and end is None:
        response = requests.get(
            COINBASE_CANDLE_BASE.format(product_id=product_id),
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        return response.json()

    endtime = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    starttime = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    res = []

    while (endtime - starttime).total_seconds() / granularity.value > 300:
        inter = starttime + datetime.timedelta(seconds=300 * granularity.value)
        params["start"] = starttime.strftime("%Y-%m-%d %H:%M:%S")
        params["end"] = inter.strftime("%Y-%m-%d %H:%M:%S")
        response = requests.get(
            COINBASE_CANDLE_BASE.format(product_id=product_id),
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        res += response.json()
        starttime = inter

    params["start"] = starttime.strftime("%Y-%m-%d %H:%M:%S")
    params["end"] = endtime.strftime("%Y-%m-%d %H:%M:%S")
    response = requests.get(
        COINBASE_CANDLE_BASE.format(product_id=product_id),
        headers=headers,
        params=params,
    )
    response.raise_for_status()
    res += response.json()
    return res


def get_historic_price_series(
    product_id: str,
    price_component: CoinbaseCandle = CoinbaseCandle.CLOSE,
    granularity: Optional[Granularity] = None,
    interpolation: str = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.Series:
    ohlcv = get_historic_candles(
        product_id=product_id,
        granularity=granularity,
        start=start,
        end=end,
    )
    s = (
        pd.Series(
            data=[o[price_component.value] for o in ohlcv],
            index=pd.DatetimeIndex(
                [pd.to_datetime(o[CoinbaseCandle.TIME.value], unit="s") for o in ohlcv],
            ),
        )
        .sort_index()
        .drop_duplicates()
    )

    if interpolation is not None:
        s_interpolated = pd.Series(
            index=pd.date_range(start=s.index[0], end=s.index[-1], freq=interpolation)
        )
        s_interpolated.update(s)
        s_interpolated = s_interpolated.interpolate(method="linear")
        return s_interpolated
    else:
        return s


def _price_listener(iter_obj, symbol):
    ws = websocket.WebSocketApp(
        f"wss://stream.binance.com:9443/ws/{symbol}@kline_1s",
        on_message=lambda _, msg: _on_message(iter_obj, msg, symbol),
    )
    ws.run_forever(reconnect=5)


def _on_message(iter_obj, message, symbol):
    iter_obj.latest_price = float(json.loads(message)["k"]["c"])


def _kc_price_listener(iter_obj, symbol):
    token = requests.post("https://api.kucoin.com/api/v1/bullet-public").json()["data"][
        "token"
    ]
    ws = websocket.WebSocketApp(
        f"wss://ws-api-spot.kucoin.com/?token={token}&[connectId=]",
        on_open=lambda ws: _kc_on_open(ws, symbol),
        on_message=lambda _, msg: _kc_on_message(iter_obj, msg, symbol),
    )
    ws.run_forever(reconnect=5, ping_interval=10, ping_timeout=5)


def _py_price_listener(iter_obj, symbol, update_freq=5):
    api_url = os.environ.get("PYTH_PRICE_PULL_API_URL", "http://localhost:8080")
    while True:
        try:

            res = requests.get(f"{api_url}/avgPrice", params={"symbol": symbol})
            iter_obj.latest_price = num_from_padded_int(res.json()["price"], 18)
        except requests.RequestException as e:
            logging.warning(e)
        time.sleep(update_freq)


def _kc_on_open(ws: websocket.WebSocketApp, symbol):
    ws.send(
        json.dumps(
            {
                "id": 1545910660739,
                "type": "subscribe",
                "topic": f"/market/ticker:{symbol}",
                "response": True,
            }
        ),
    )


def _kc_on_message(iter_obj, message, symbol):
    iter_obj.latest_price = float(json.loads(message)["data"]["price"])


class LivePrice:
    """Iterator for getting a live product price process.

    Class is to be used when running the scenario on fairground incentives. The
    iterator can be passed to the market-maker agent and the price-sensitive
    agents to give them information regarding the live product price.

    """

    def __init__(
        self,
        product: str = "BTCBUSD",
        multiplier: int = 1,
        price_source: Optional[str] = "binance",
        update_frequency: Optional[int] = 5,
    ):
        self.product = product
        self.latest_price = None
        self.multiplier = multiplier

        match price_source:
            case "binance":
                target = _price_listener
                product = self.product.lower()

            case "kucoin":
                target = _kc_price_listener
                product = self.product

            case "pyth":
                target = _py_price_listener
                product = self.product

            case _:
                raise ValueError("Unimplemented price source")

        self._forwarding_thread = threading.Thread(
            target=target,
            args=(self, product),
            daemon=True,
        )
        self._forwarding_thread.start()

    def __iter__(self):
        return self

    def __getitem__(self, index):
        return self._get_price()

    def __next__(self):
        return self._get_price()

    def _get_price(self):
        while self.latest_price is None:
            time.sleep(0.33)
        return self.latest_price * self.multiplier


_live_prices = {}
_live_prices_lock = threading.Lock()


def get_live_price(
    product: str,
    multiplier: int,
    price_source: Optional[str] = None,
    update_frequency: int = 5,
) -> LivePrice:
    global _live_prices
    global _live_prices_lock

    feed_key = f"{product}_{multiplier}"

    with _live_prices_lock:
        if not feed_key in _live_prices:
            _live_prices[feed_key] = LivePrice(
                product=product,
                multiplier=multiplier,
                price_source=price_source,
                update_frequency=update_frequency,
            )
        return _live_prices[feed_key]


def ou_price_process(n, theta=0.15, mu=0.0, sigma=0.2, x0=1.0, drift=0.0):
    """
    Generates a mean-reverting price series using the Ornstein–Uhlenbeck
    process with an optional drift term.

    Parameters:
        n (int): Length of the time series.
        theta (float): Speed of reversion to the mean.
        mu (float): Long-term mean level.
        sigma (float): Volatility of the process.
        x0 (float): Initial value of the series.
        drift (float): Optional drift term to model a constant trend.

    Returns:
        np.ndarray: Mean-reverting price series of length n.
    """
    dt = 1.0  # Assuming a time step of 1
    x = np.zeros(n)
    x[0] = x0
    for t in range(1, n):
        dx = (
            theta * ((mu + t * drift) - x[t - 1]) * dt
            + sigma * np.sqrt(dt) * np.random.normal()
        )
        x[t] = x[t - 1] + dx
    return x


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    bn_stream = get_live_price(
        "btcusdt",
        1,
        price_source="binance",
    )
    kc_stream = get_live_price(
        "BTC-USDT",
        1,
        price_source="kucoin",
    )
    py_stream = get_live_price(
        "BTC/USD",
        1,
        price_source="pyth",
    )

    for _ in range(300):
        print(
            f"Prices: bn={next(bn_stream):.2f} kc={next(kc_stream):.2f}, py={next(py_stream):.2f}"
        )
        time.sleep(1)
