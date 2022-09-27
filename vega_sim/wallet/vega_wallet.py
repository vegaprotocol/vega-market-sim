import time
from typing import Any, Dict, List, Optional, Union

import os
import dotenv
import inflection
import requests
from google.protobuf.json_format import MessageToDict
from vega_sim.wallet.base import Wallet

WALLET_CREATION_URL = "{wallet_server_url}/api/v1/wallets"
WALLET_LOGIN_URL = "{wallet_server_url}/api/v1/auth/token"
WALLET_KEY_URL = "{wallet_server_url}/api/v1/keys"

dotenv.load_dotenv()
DEFAULT_KEY_NAME = os.environ.get("DEFAULT_KEY_NAME")


class VegaWallet(Wallet):
    def __init__(self, wallet_url: str):
        """Creates a wallet to interact with a full running vegawallet instance

        Args:
            wallet_url:
                str, base URL of the wallet service

        """
        self.wallet_url = wallet_url
        self.login_tokens = {}
        self.pub_keys = {}

    def create_wallet(
        self,
        name: str,
        passphrase: str,
    ) -> str:
        """Generates a new wallet from a name - passphrase pair in the given vega service.

        Args:
            name:
                str, The name to use for the wallet
            passphrase:
                str, The passphrase to use when logging in to created wallet in future
        Returns:
            str, login token to use in authenticated requests
        """
        req = {"wallet": name, "passphrase": passphrase}

        # Wallet now requires a connection to a live vega service during startup,
        # which can slow initialisation a little
        for _ in range(5):
            try:
                response = requests.post(
                    WALLET_CREATION_URL.format(wallet_server_url=self.wallet_url),
                    json=req,
                )
                response.raise_for_status()
                break
            except requests.exceptions.ConnectionError:
                time.sleep(1)

        token = response.json()["token"]

        self.login_tokens[name] = token
        self.generate_keypair(
            token,
            passphrase,
            metadata=[{"name": "default_key"}],
        )
        self.pub_keys[name] = self.get_keypairs(wallet_name=name)

    def login(self, name: str, passphrase: str) -> str:
        """Logs in to existing wallet in the given vega service.

        Args:
            name:
                str, The name of the wallet
            passphrase:
                str, The login passphrase used when creating the wallet
        Returns:
            str, login token to use in authenticated requests
        """
        req = {"wallet": name, "passphrase": passphrase}
        response = requests.post(
            WALLET_LOGIN_URL.format(wallet_server_url=self.wallet_url),
            json=req,
        )
        response.raise_for_status()
        self.login_tokens[name] = response.json()["token"]
        self.pub_keys[name] = self.get_keypairs(name)
        return self.login_tokens[name]

    def generate_keypair(
        self,
        token: str,
        passphrase: str,
        metadata: Optional[List[Dict[str, str]]] = None,
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
            WALLET_KEY_URL.format(wallet_server_url=self.wallet_url),
            headers=headers,
            json=req,
        )
        response.raise_for_status()
        return list(response.json()["key"]["pub"])

    def get_keypairs(self, wallet_name: str) -> list:
        headers = {"Authorization": f"Bearer {self.login_tokens[wallet_name]}"}
        response = requests.get(
            WALLET_KEY_URL.format(wallet_server_url=self.wallet_url), headers=headers
        )
        response.raise_for_status()
        return {key["name"]: key["pub"] for key in response.json()["keys"]}

    def submit_transaction(
        self,
        name: str,
        transaction: Any,
        transaction_type: str,
        key_name: Optional[int] = None,
    ):

        pub_key = self.public_key(name=name, key_name=key_name)

        headers = {"Authorization": f"Bearer {self.login_tokens[name]}"}
        submission = {
            inflection.camelize(
                transaction_type, uppercase_first_letter=False
            ): MessageToDict(transaction),
            "pubKey": pub_key,
            "propagate": True,
        }

        url = f"{self.wallet_url}/api/v1/command/sync"

        response = requests.post(url, headers=headers, json=submission)
        response.raise_for_status()

    def public_key(self, name: str, key_name: Optional[str] = None) -> str:
        """Return a public key for the given wallet name and key name.

        Args:
            name (str):
                Name of the wallet.
            key_name (str):
                Name of the key. Defaults to None.

        Returns:
            str, public key
        """

        if key_name is None:
            return self.pub_keys[name][DEFAULT_KEY_NAME]
        else:
            return self.pub_keys[name][key_name]
