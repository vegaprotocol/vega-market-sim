from typing import Any, Dict, List, Optional, Union

import os
import inflection

import json
import logging
import subprocess
import requests
import multiprocessing

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
        wallet_path: str | list[str],
        vega_home_dir: str,
        passphrase_file_path: Optional[str] = None,
        mutex: Optional[multiprocessing.Lock] = None,
    ):
        """Creates a wallet to interact with a full running vegawallet instance

        Args:
            wallet_url:
                str, base URL of the wallet service
            wallet_path:
                str | list[str], path to a wallet binary to call CLI functions from, you can pass vegawallet if you have dedicated wallet binary or ["vega", "wallet"] if you have a vega binary which contains a wallet implementation
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
        self._mutex = mutex

        self.vega_default_wallet_name = os.environ.get(
            "VEGA_DEFAULT_WALLET_NAME", DEFAULT_WALLET_NAME
        )

    @classmethod
    def from_json(
        cls,
        json_path: str,
        wallet_url: str,
        wallet_path: str | list[str],
        vega_home_dir: str,
        passphrase_file_path: Optional[str] = None,
        mutex: Optional[multiprocessing.Lock] = None,
    ) -> "VegaWallet":
        """Creates a wallet to interact with a full running vegawallet instance.
            Loads tokens from a given json file in the form
                {
                    wallet_name_1: token,
                    wallet_name_2: token
                }
            instead of requiring a wallet password

        Args:
            json_path:
                str, File containing v2 wallet tokens
            wallet_url:
                str, base URL of the wallet service
            wallet_path:
                str, path to a wallet binary to call CLI functions from, you can pass vegawallet if you have dedicated wallet binary or ["vega", "wallet"] if you have a vega binary which contains a wallet implementation
            vega_home_dir:
                str, dir of vega home configuration files
        """
        base = cls(
            wallet_url=wallet_url,
            wallet_path=wallet_path,
            vega_home_dir=vega_home_dir,
            passphrase_file_path=passphrase_file_path,
            mutex=mutex,
        )

        with open(json_path, "r") as f:
            base.login_tokens = json.load(f)
        return base

    def _load_token(self, wallet_name: str):
        if self._passphrase_file is None:
            raise Exception("Must set wallet passphrase file path to load tokens")

        wallet_args = [
            self._wallet_path,
            "wallet",
            "api-token",
            "list",
            "--passphrase-file",
            self._passphrase_file,
            "--output",
            "json",
        ]

        if not self._wallet_home is None:
            wallet_args += ["--home", self._wallet_home]

        cmd = subprocess.run(
            wallet_args,
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
        if self._passphrase_file is None:
            raise Exception("Must set wallet passphrase file path to generate keys")

        wallet = (
            wallet_name if wallet_name is not None else self.vega_default_wallet_name
        )

        if wallet not in self.pub_keys:
            self.create_wallet(name=wallet)

        cmd = subprocess.run(
            [
                self._wallet_path,
                "wallet",
                "key",
                "generate",
                "--wallet",
                wallet,
                "--home",
                self._wallet_home,
                "--passphrase-file",
                self._passphrase_file,
                "--meta",
                f"name:{name}",
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
        if self._passphrase_file is None:
            raise Exception("Must set wallet passphrase file path to generate wallets")

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
                "wallet",
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
                "--output",
                "json",
            ],
            capture_output=True,
            universal_newlines=True,
            encoding="UTF-8",
        ).stdout

        self.login_tokens[name] = json.loads(cmd)["token"]

    def get_keypairs(self, wallet_name: str) -> dict:
        if wallet_name not in self.login_tokens:
            self._load_token(wallet_name=wallet_name)

        headers = {
            "Origin": "MarketSim",
            "Authorization": f"VWT {self.login_tokens[wallet_name]}",
        }

        submission = {
            "jsonrpc": "2.0",
            "method": "client.list_keys",
            "params": [],
            "id": "request",
        }

        url = f"{self.wallet_url}/api/v2/requests"

        self._lock()
        response = requests.post(url, headers=headers, json=submission)
        self._release()

        try:
            response.raise_for_status()
        except Exception as e:
            logging.warning(f"Request failed, response={response.json()}")
            raise e

        return {
            key["name"]: key["publicKey"] for key in response.json()["result"]["keys"]
        }

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

        self._lock()
        response = requests.post(url, headers=headers, json=submission)
        self._release()
        try:
            response.raise_for_status()
        except Exception as e:
            logging.warning(f"Submission failed, response={response.json()}")
            raise e

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
        wallet_name = (
            self.vega_default_wallet_name if wallet_name is None else wallet_name
        )

        if wallet_name not in self.pub_keys or name not in self.pub_keys[wallet_name]:
            self.pub_keys.setdefault(wallet_name, {}).update(
                self.get_keypairs(wallet_name=wallet_name)
            )

        return self.pub_keys[wallet_name][name]

    def _lock(self):
        """
        Lock if mutex is available
        """
        if self._mutex is None:
            return
        self._mutex.acquire()

    def _release(self):
        """
        Release the lock if mutex is available
        """
        if self._mutex is None:
            return

        self._mutex.release()
