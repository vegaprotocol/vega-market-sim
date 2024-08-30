import yaml
import logging
import logging.config

import datetime


def timestamp_to_datetime(ts: int, nano: bool = True):
    if nano:
        ts = ts / 1e9
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)


def datetime_to_timestamp(dt: datetime.datetime, nano: bool = True) -> int:
    ts = dt.timestamp()
    if nano:
        ts = ts * 1e9
    return int(ts)


def padded_int_to_float(padded_int: int, decimals: int) -> float:
    padded_int = int(padded_int) if isinstance(padded_int, str) else padded_int
    return float(padded_int) * 10**-decimals


def duration_str_to_int(duration_str: str) -> int:
    duration = 0
    if "h" in duration_str:
        duration += int(duration_str.split("h")[0]) * 60 * 60
    if "m" in duration_str:
        duration += int(duration_str.split("m")[0]) * 60
    if "s" in duration_str:
        duration += int(duration_str.split("s")[0])
    return duration
