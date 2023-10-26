import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import time

import numpy as np
import pandas as pd
import requests
import json
from websockets.sync.client import connect
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


def _binance_price_listener(iter_obj, symbol):
    ws = websocket.WebSocketApp(
        f"wss://stream.binance.com:9443/ws/{symbol}@kline_1s",
        on_message=lambda _, msg: _on_message(iter_obj, msg),
    )
    ws.run_forever(reconnect=5)


def _xauusd_price_listener(iter_obj):
    url = "https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument/XAU/USD"
    while True:
        try:
            r = requests.get(url)
            if r.status_code != 200:
                print(f"failed to get GOLD price, status code: {r.status_code}", flush=True)
            else:
                data = r.json()
                total_bid = 0
                total_ask = 0
                count = 0
                for item in data:
                    spread_profile_prices = item.get("spreadProfilePrices", [])
                    for spread_profile_price in spread_profile_prices:
                        bid = spread_profile_price.get("bid", 0)
                        ask = spread_profile_price.get("ask", 0)
                        total_bid += bid
                        total_ask += ask
                        count += 1
                average_bid = total_bid / count if count > 0 else 0
                average_ask = total_ask / count if count > 0 else 0

                print("GOLD Average Bid Price:", average_bid, flush=True)
                print("GOLD Average Ask Price:", average_ask, flush=True)

                mid_price = (average_bid + average_ask) / 2
                print("GOLD Mid Price Between Average Bid and Average Ask:", mid_price, flush=True)
                iter_obj.latest_price = mid_price
        except Exception as e:
            print(f"Failed to get price for GOLD {e}", flush=True)
        time.sleep(30)



def _on_message(iter_obj, message):
    iter_obj.latest_price = float(json.loads(message)["k"]["c"])


class LivePrice:
    """Iterator for getting a live product price process.

    Class is to be used when running the scenario on fairground incentives. The
    iterator can be passed to the market-maker agent and the price-sensitive
    agents to give them information regarding the live product price.

    """

    def __init__(self, product: str = "BTCBUSD"):
        self.product = product
        self.latest_price = None

        if product == "XAUUSD":
            self._forwarding_thread = threading.Thread(
                target=_xauusd_price_listener,
                args=(self, self.product.lower()),
                daemon=True,
            )
        else:
            self._forwarding_thread = threading.Thread(
                target=_binance_price_listener,
                args=(self, self.product.lower()),
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
        return self.latest_price

_live_prices = {}
_live_prices_lock = threading.Lock()

def getLivePrice(product: str) -> LivePrice:
    global _live_prices
    global _live_prices_lock
    with _live_prices_lock:
        if not product in _live_prices:
            _live_prices[product] = LivePrice(product=product)
        return _live_prices[product]

if __name__ == "__main__":
    print(
        get_historic_price_series(
            "ETH-USD",
            granularity=Granularity.HOUR,
            start="2022-08-02 01:01:50",
            end="2022-09-05 09:05:20",
        )
    )
