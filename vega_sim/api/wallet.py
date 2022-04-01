from typing import Dict, List
import requests

WALLET_CREATION_URL = "{wallet_server_url}/api/v1/wallets"
WALLET_LOGIN_URL = "{wallet_server_url}/api/v1/auth/token"
WALLET_KEY_URL = "{wallet_server_url}/api/v1/keys"


def create_wallet(name: str, passphrase: str, wallet_url: str) -> str:
    """Generates a new wallet from a name - passphrase pair in the given vega service.

    Args:
        name:
            str, The name to use for the wallet
        passphrase:
            str, The passphrase to use when logging in to created wallet in future
        wallet_url:
            str, base URL of the wallet service
    Returns:
        str, login token to use in authenticated requests
    """
    req = {"wallet": name, "passphrase": passphrase}
    response = requests.post(
        WALLET_CREATION_URL.format(wallet_server_url=wallet_url),
        json=req,
    )
    response.raise_for_status()
    return response.json()["token"]


def login(name: str, passphrase: str, wallet_url: str) -> str:
    """Logs in to existing wallet in the given vega service.

    Args:
        name:
            str, The name of the wallet
        passphrase:
            str, The login passphrase used when creating the wallet
        wallet_url:
            str, base URL of the wallet service
    Returns:
        str, login token to use in authenticated requests
    """
    req = {"wallet": name, "passphrase": passphrase}
    response = requests.post(
        WALLET_LOGIN_URL.format(wallet_server_url=wallet_url),
        json=req,
    )
    response.raise_for_status()
    return response.json()["token"]


def generate_keypair(
    token: str,
    passphrase: str,
    wallet_url: str,
    metadata: List[Dict[str, str]],
) -> str:
    """Generates a keypair for given token validated wallet.

    Args:
        token:
            str, token returned from login to wallet
        passphrase:
            str, passphrase used for login to corresponding wallet
        wallet_url:
            str, base URL of the wallet service
        metadata:
            list[dict], metadata which is stored alongside keys to identify them
    Returns:
        str, public key generated
    """
    headers = {"Authorization": f"Bearer {token}"}
    req = {
        "passphrase": passphrase,
        "meta": metadata,
    }
    response = requests.post(
        WALLET_KEY_URL.format(wallet_server_url=wallet_url), headers=headers, json=req
    )
    response.raise_for_status()
    return response.json()["key"]["pub"]


def get_keypairs(token: str, wallet_url: str) -> Dict:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        WALLET_KEY_URL.format(wallet_server_url=wallet_url), headers=headers
    )
    response.raise_for_status()
    return response.json()["keys"]
