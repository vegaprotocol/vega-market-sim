import time
import requests
from logging import getLogger

BASE_MINT_URL = "{faucet_url}/api/v1/mint"

logger = getLogger(__name__)


def mint(pub_key: str, asset: str, amount: int, faucet_url: str) -> None:
    url = BASE_MINT_URL.format(faucet_url=faucet_url)
    # Request a proportion of the maximum faucet amount - this allows for
    # cases where requesting the maximum amount would have floating point
    # imprecision and the request rejected.
    payload = {
        "party": pub_key,
        "amount": str(int(0.99 * amount)),
        "asset": asset,
    }
    for i in range(20):
        try:
            req = requests.post(url, json=payload)
            req.raise_for_status()
            return
        except Exception as e:
            time.sleep(0.1 * 1.2**i)

    logger.exception(f"Exception in minting with payload {payload}: {req.json()}")
    raise e
