from typing import Optional
import numpy as np

from typing import Any, Dict, List, Optional, Union
import requests
import pandas as pd
from enum import Enum
import datetime

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


def get_historic_temp_series(
    latitude: float,
    longitude: float,
    hours: int = 24,
    interpolation: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> list:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m&start_date={start_date}&end_date={end_date}"
    response = requests.get(url)
    data = response.json()
    s = (
        pd.Series(
            data=data["hourly"]["temperature_2m"],
            index=pd.DatetimeIndex(
                data["hourly"]["time"],
            ),
        )
        .sort_index()
        .drop_duplicates()
        .rolling(hours)
        .mean()
        .dropna()
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


class LivePrice:
    """Iterator for getting a live product price process.

    Class is to be used when running the scenario on fairground incentives. The
    iterator can be passed to the market-maker agent and the price-sensitive
    agents to give them information regarding the live product price.

    """

    def __init__(self, product: str = "ADAUSDT"):
        self.product = product

    def __iter__(self):
        return self

    def __getitem__(self, index):
        return self._get_price()

    def __next__(self):
        return self._get_price()

    def _get_price(self):
        url = f"https://api.binance.com/api/v3/avgPrice?symbol={self.product}"
        return float(requests.get(url).json()["price"])


class AverageWeather:
    """Iterator for getting the average temperature.

    Class is to be used when running the scenario on fairground incentives. The
    iterator can be passed to the market-maker agent and the price-sensitive
    agents to give them information regarding the live average temperature.

    """

    LOCATIONS = {
        "athens": {"latitude": 37.983810, "longitude": 23.7278},
        "new_york": {"latitude": 40.7143, "longitude": -74.006},
    }

    def __init__(
        self,
        hours: Optional[int] = 24,
        location: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ):
        if location is not None:
            if location not in self.LOCATIONS:
                raise ValueError("Invalid location specified.")
            self.latitude = self.LOCATIONS[location]["latitude"]
            self.longitude = self.LOCATIONS[location]["longitude"]
        else:
            self.latitude = latitude if latitude is not None else 0
            self.longitude = longitude if longitude is not None else 0
        self.hours = hours

    def __iter__(self):
        return self

    def __getitem__(self, index):
        return self._get_temp()

    def __next__(self):
        return self._get_temp()

    def _get_temp(self):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={self.latitude}&longitude={self.longitude}&hourly=temperature_2m&past_days={int(np.ceil(self.hours/24))}&forecast_days=0"
        response = requests.get(url)
        data = response.json()
        hourly_temperatures = data["hourly"]["temperature_2m"]
        past_week_temperatures = hourly_temperatures[-self.hours :]
        return sum(past_week_temperatures) / len(past_week_temperatures)


if __name__ == "__main__":
    s = get_historic_temp_series(
        longitude=37.983810,
        latitude=23.7278,
        interpolation="5s",
        start_date="2023-06-01",
        end_date="2023-07-01",
    )
    print(s)
