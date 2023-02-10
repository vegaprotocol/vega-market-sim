from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto
from io import BufferedWriter
from typing import Any
from logging import getLogger

import os
import dotenv
import numpy as np
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
from typing import Optional
from vega_sim.grpc.client import VegaCoreClient
from vega_sim.wallet.base import Wallet

import vega_sim.proto.vega.api.v1.core_pb2 as core_proto
import vega_sim.proto.vega.commands.v1.transaction_pb2 as transaction_proto
import vega_sim.proto.vega.commands.v1.signature_pb2 as signature_proto
from vega_sim.wallet.vega_wallet import VegaWallet
from vega_sim.wallet.base import DEFAULT_WALLET_NAME

logger = getLogger(__name__)


class SlimWallet(Wallet):
    def __init__(
        self,
        core_client: VegaCoreClient,
        height_update_frequency: int = 500,
        full_wallet: Optional[VegaWallet] = None,
        full_wallet_default_pass: str = "passwd",
        store_transactions: bool = False,
        log_dir: Optional[str] = None,
    ):
        """Creates a wallet to running key generation internally
        and directly sending transactions to the Core node

        Args:
            core_client:
                VegaCoreClient, client for vega core interaction
            height_update_frequency:
                int, default 500, how frequently to update the block height parameter
                    for transactions (e.g. 500 will update every 500 calls to
                    submit_transaction).
            full_wallet:
                Optional[VegaWallet], optional full wallet backing. This will be used
                    for creating keypairs instead of generating them locally, making it
                    possible to connect to the Console
            full_wallet_default_pass:
                str, default 'passwd', If full wallet is passed, the password used
                    when creating dummy accounts if none are passed.
                    Use this password to log in to the Vega Console
            store_transactions:
                bool, default False, If True will store every transaction sent into
                    a file, allowing replay of the chain without going through full
                    logic of actors etc
        """
        self.core_client = core_client
        self.keys = {}
        self.pub_keys = {}
        self.idx = 0
        self.nonce_idx = 0
        self.pool = ThreadPoolExecutor(max_workers=5)

        self.height_update_frequency = 500
        self.remaining_until_height_update = 0
        self.block_height = None

        self.vega_wallet = full_wallet
        self.full_wallet_default_pass = full_wallet_default_pass

        self.store_transactions = store_transactions
        self.log_dir = log_dir

        # If it turns out that customising these is useful it's trivial to
        # make a parameter
        self.num_sigs_to_create = 1000000
        self.num_nonces_to_create = 1000000

        self._create_nonces()
        self._create_sigs()

        dotenv.load_dotenv()
        self.vega_default_wallet_name = os.environ.get(
            "VEGA_DEFAULT_WALLET_NAME", DEFAULT_WALLET_NAME
        )

    def _create_sigs(self):
        self.sigs = [os.urandom(6).hex() for _ in range(self.num_sigs_to_create)]

    def _create_nonces(self):
        self.nonces = np.random.randint(0, 100000, size=self.num_nonces_to_create)

    def _next_sig(self) -> bytes:
        self.idx += 1
        if self.idx >= self.num_sigs_to_create:
            self.idx = 0
            self._create_sigs()
        return self.sigs[self.idx]

    def _next_nonce(self) -> int:
        self.nonce_idx += 1
        if self.nonce_idx >= self.num_nonces_to_create:
            self.nonce_idx = 0
            self._create_nonces()
        return self.nonces[self.nonce_idx]

    def create_key(
        self,
        name: str,
        passphrase: str,
        wallet_name: Optional[str] = None,
    ) -> str:
        """Generates a new wallet key from a name - passphrase pair in the given vega service.

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
        passphrase = (
            passphrase if passphrase is not None else self.full_wallet_default_pass
        )
        wallet_name = (
            wallet_name if wallet_name is not None else self.vega_default_wallet_name
        )

        if wallet_name not in self.keys:
            self.keys[wallet_name] = {}
        if wallet_name not in self.pub_keys:
            self.pub_keys[wallet_name] = {}

        if self.vega_wallet is None:
            self.keys[wallet_name][name] = SigningKey.generate()
            self.pub_keys[wallet_name][name] = (
                self.keys[wallet_name][name]
                .verify_key.encode(encoder=HexEncoder)
                .decode()
            )

        else:
            self.vega_wallet.create_key(
                name=name,
                passphrase=passphrase,
                wallet_name=wallet_name,
            )
            self.pub_keys[wallet_name][name] = self.vega_wallet.public_key(
                name, wallet_name
            )

    def submit_transaction(
        self,
        key_name: str,
        transaction: Any,
        transaction_type: str,
        wallet_name: Optional[str] = None,
    ):
        # if self.remaining_until_height_update <= 0:
        #     self.block_height = self.core_client.LastBlockHeight(
        #         core_proto.LastBlockHeightRequest()
        #     ).height
        #     self.remaining_until_height_update = self.height_update_frequency

        pub_key = self.public_key(name=key_name, wallet_name=wallet_name)

        transaction_info = {transaction_type: transaction}
        input_data = transaction_proto.InputData(
            nonce=self._next_nonce(),  # block_height=self.block_height,
            **transaction_info
        )

        serialised = input_data.SerializeToString()

        trans = transaction_proto.Transaction(
            input_data=serialised,
            signature=signature_proto.Signature(
                value=self._next_sig(),
                algo="vega/ed25519",
                version=1,
            ),
            pub_key=pub_key,
            version=3,
            pow=transaction_proto.ProofOfWork(
                tid=None,
                nonce=0,
            ),
        )
        request = core_proto.SubmitTransactionRequest(
            tx=trans, type=core_proto.SubmitTransactionRequest.Type.TYPE_ASYNC
        )

        submit_future = self.core_client.SubmitTransaction.future(request)
        self.pool.submit(lambda: submit_future.result())
        self.remaining_until_height_update -= 1

    def submit_raw_transaction(self, transaction: core_proto.SubmitTransactionRequest):
        submit_future = self.core_client.SubmitTransaction.future(transaction)
        self.pool.submit(lambda: submit_future.result())

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
