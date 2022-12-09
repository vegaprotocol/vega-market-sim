import time
from typing import Any, Dict, List, Optional, Union

import os
import dotenv
import inflection

import pjrpc
import requests
from pjrpc.client.backend import requests as pjrpc_client

from google.protobuf.json_format import MessageToDict
from vega_sim.wallet.base import Wallet, DEFAULT_WALLET_NAME

WALLET_JSON_RPC_URL = "{wallet_server_url}/api/v2/requests"
WALLET_CREATION_URL = "{wallet_server_url}/api/v2/wallets"
WALLET_LOGIN_URL = "{wallet_server_url}/api/v2/auth/token"
WALLET_KEY_URL = "{wallet_server_url}/api/v2/keys"


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

        self._session = requests.Session()
        self._session.headers.update({"Origin": "https://vega.xyz"})

        self._client = pjrpc_client.Client(
            WALLET_JSON_RPC_URL.format(wallet_server_url=self.wallet_url),
            session=self._session,
            id_gen_impl=lambda: iter("1"),
        )

        dotenv.load_dotenv()
        self.vega_default_wallet_name = os.environ.get(
            "VEGA_DEFAULT_WALLET_NAME", DEFAULT_WALLET_NAME
        )

    def create_key(
        self, name: str, passphrase: str, wallet_name: Optional[str] = None
    ) -> None:
        """Generates a new wallet from a name - passphrase pair in the given vega service.

        Args:
            name:
                str, The name to use for the wallet key
            passphrase:
                str, The passphrase to use when logging in to created wallet in future
            wallet_name:
                str, The wallet to use if not the default
        Returns:
            str, login token to use in authenticated requests
        """
        req = {"wallet": name, "passphrase": passphrase}

        if name not in self.pub_keys:
            # Wallet now requires a connection to a live vega service during startup,
            # which can slow initialisation a little
            for _ in range(5):
                try:
                    response = requests.post(
                        WALLET_CREATION_URL.format(wallet_server_url=self.wallet_url),
                        json=req,
                    )
                    response.raise_for_status()
                    self.login_tokens[name] = response.json()["token"]
                    break
                except requests.exceptions.ConnectionError:
                    time.sleep(1)

        self.generate_keypair(
            token=self.login_tokens[name],
            passphrase=passphrase,
            metadata=[
                {
                    "key": "name",
                    "value": name
                    if name is not None
                    else self.vega_default_wallet_name,
                }
            ],
        )
        self.pub_keys[name] = self.get_keypairs(wallet_name=name)

    def login(self, passphrase: str, wallet_name: Optional[str] = None) -> str:
        """Logs in to existing wallet in the given vega service.

        Args:
            name:
                str, The name of the wallet
            passphrase:
                str, The login passphrase used when creating the wallet
        Returns:
            str, login token to use in authenticated requests
        """
        wallet_name = (
            wallet_name if wallet_name is not None else self.vega_default_wallet_name
        )
        req = {
            "wallet": wallet_name,
            "passphrase": passphrase,
        }
        response = requests.post(
            WALLET_LOGIN_URL.format(wallet_server_url=self.wallet_url),
            json=req,
        )
        response.raise_for_status()
        self.login_tokens[wallet_name] = response.json()["token"]
        self.pub_keys[wallet_name] = self.get_keypairs(wallet_name)
        return self.login_tokens[wallet_name]

    def generate_keypair(
        self,
        passphrase: str,
        metadata: Optional[List[Dict[str, str]]] = None,
        wallet_name: Optional[str] = None,
    ) -> None:
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
        response = self._client(
            "admin.generate_key",
            wallet=wallet_name if wallet_name is not None else DEFAULT_WALLET_NAME,
            passphrase=passphrase,
            metadata=metadata,
        )
        import pdb

        pdb.set_trace()
        return list(response.json()["key"]["pub"])

    def get_keypairs(self, wallet_name: str) -> dict:
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
        wallet_name: Optional[int] = None,
    ):
        wallet_name = (
            wallet_name if wallet_name is not None else self.vega_default_wallet_name
        )
        pub_key = self.public_key(wallet_name=wallet_name, name=name)

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

    def public_key(self, name: str, wallet_name: Optional[str] = None) -> str:
        """Return a public key for the given wallet name and key name.

        Args:
            name (str):
                Name of the key.
            wallet_name (str):
                Name of the wallet. Defaults to None.

        Returns:
            str, public key
        """

        if wallet_name is None:
            return self.pub_keys[self.vega_default_wallet_name][name]
        else:
            return self.pub_keys[wallet_name][name]
