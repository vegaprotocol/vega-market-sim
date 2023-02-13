from typing import Any, Dict, List, Optional, Union

import os
import inflection

import json
import subprocess
import requests

from google.protobuf.json_format import MessageToDict
from vega_sim.wallet.base import Wallet, DEFAULT_WALLET_NAME

WALLET_JSON_RPC_URL = "{wallet_server_url}/api/v2/requests"
WALLET_CREATION_URL = "{wallet_server_url}/api/v2/wallets"
WALLET_LOGIN_URL = "{wallet_server_url}/api/v2/auth/token"
WALLET_KEY_URL = "{wallet_server_url}/api/v2/keys"


class VegaWallet(Wallet):
    def __init__(
        self,
        wallet_url: str,
        wallet_path: str,
        vega_home_dir: str,
        passphrase_file_path: str,
    ):
        """Creates a wallet to interact with a full running vegawallet instance

        Args:
            wallet_url:
                str, base URL of the wallet service
            wallet_path:
                str, path to a wallet binary to call CLI functions from
            vega_home_dir:
                str, dir of vega home configuration files
            passphrase_file_path:
                str, File containing login passphrase for wallet

        """
        self.wallet_url = wallet_url
        self.login_tokens = {}
        self.pub_keys = {}

        self._wallet_path = wallet_path
        self._wallet_home = vega_home_dir
        self._passphrase_file = passphrase_file_path

        self.vega_default_wallet_name = os.environ.get(
            "VEGA_DEFAULT_WALLET_NAME", DEFAULT_WALLET_NAME
        )

    def _load_token(self, wallet_name: str):
        cmd = subprocess.run(
            [
                self._wallet_path,
                "api-token",
                "list",
                "--home",
                self._wallet_home,
                "--passphrase-file",
                self._passphrase_file,
                "--output",
                "json",
            ],
            capture_output=True,
            universal_newlines=True,
            encoding="UTF-8",
        ).stdout

        for data in json.loads(cmd)["tokens"]:
            if data["description"] == wallet_name:
                self.login_tokens[wallet_name] = data["token"]

    def create_key(self, name: str, wallet_name: Optional[str] = None) -> None:
        """Generates a new key in the given vega service.

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
        wallet = (
            wallet_name if wallet_name is not None else self.vega_default_wallet_name
        )
        cmd = subprocess.run(
            [
                self._wallet_path,
                "key",
                "generate",
                "--wallet",
                wallet,
                "--home",
                self._wallet_home,
                "--passphrase-file",
                self._passphrase_file,
                "--output",
                "json",
            ],
            capture_output=True,
            universal_newlines=True,
            encoding="UTF-8",
        ).stdout
        self.pub_keys.setdefault(wallet, {})[name] = json.loads(cmd)["publicKey"]

    def create_wallet(self, name: str) -> None:
        """Generates a new wallet in the given vega service.

        Args:
            name:
                str, The name to use for the wallet
        """

        # First generate the wallet itself
        subprocess.run(
            [
                self._wallet_path,
                "wallet",
                "create",
                "--wallet",
                name,
                "--home",
                self._wallet_home,
                "--passphrase-file",
                self._passphrase_file,
                "--output",
                "json",
            ],
            capture_output=True,
            universal_newlines=True,
            encoding="UTF-8",
        )

        # Then create a token for it
        cmd = subprocess.run(
            [
                self._wallet_path,
                "api-token",
                "generate",
                "--home",
                self._wallet_home,
                "--tokens-passphrase-file",
                self._passphrase_file,
                "--wallet-passphrase-file",
                self._passphrase_file,
                "--wallet-name",
                name,
                "--description",
                name,
            ],
            capture_output=True,
            universal_newlines=True,
            encoding="UTF-8",
        ).stdout

        self.login_tokens[name] = json.loads(cmd)["token"]

    def get_keypairs(self, wallet_name: str) -> dict:
        headers = {"Authorization": f"Bearer {self.login_tokens[wallet_name]}"}
        response = requests.get(
            WALLET_KEY_URL.format(wallet_server_url=self.wallet_url), headers=headers
        )
        response.raise_for_status()
        return {key["name"]: key["pub"] for key in response.json()["keys"]}

    def submit_transaction(
        self,
        key_name: str,
        transaction: Any,
        transaction_type: str,
        wallet_name: Optional[int] = None,
    ):
        wallet_name = (
            wallet_name if wallet_name is not None else self.vega_default_wallet_name
        )
        if wallet_name not in self.login_tokens:
            self._load_token(wallet_name=wallet_name)

        pub_key = self.public_key(wallet_name=wallet_name, name=key_name)

        headers = {
            "Origin": "MarketSim",
            "Authorization": f"VWT {self.login_tokens[wallet_name]}",
        }

        submission = {
            "jsonrpc": "2.0",
            "method": "client.send_transaction",
            "params": {
                "transaction": {
                    inflection.camelize(
                        transaction_type, uppercase_first_letter=False
                    ): MessageToDict(transaction)
                },
                "sendingMode": "TYPE_ASYNC",
                "publicKey": pub_key,
            },
            "id": "request",
        }

        url = f"{self.wallet_url}/api/v2/requests"

        response = requests.post(url, headers=headers, json=submission)
        import pdb

        pdb.set_trace()
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
