import requests
import pandas as pd
from enum import Enum


COIN_GECKO_REQUEST_BASE = 'https://api.coingecko.com/api/v3/'


class CoinGeckoCoin(Enum):
    BTC = "bitcoin"
    ETH = "ethereum"
    DAI = "dai"



def get_