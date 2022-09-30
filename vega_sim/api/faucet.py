import requests
from logging import getLogger

BASE_MINT_URL = "{faucet_url}/api/v1/mint"

logger = getLogger(__name__)


def mint(pub_key: str, asset: str, amount: int, faucet_url: str) -> None:
    url = BASE_MINT_URL.format(faucet_url=faucet_url)
    payload = {
        "party": pub_key,
        "amount": str(int(amount)),
        "asset": asset,
    }
    req = requests.post(url, json=payload)
    try:
        req.raise_for_status()
    except Exception as e:
        logger.exception(f"Exception in minting: {req.json()}")
        raise e
