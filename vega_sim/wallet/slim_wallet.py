from concurrent.futures import ThreadPoolExecutor
from typing import Any
from logging import getLogger

import os
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

logger = getLogger(__name__)


class SlimWallet(Wallet):
    def __init__(
        self,
        core_client: VegaCoreClient,
        height_update_frequency: int = 500,
        full_wallet: Optional[VegaWallet] = None,
        full_wallet_default_pass: str = "passwd",
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

        # If it turns out that customising these is useful it's trivial to
        # make a parameter
        self.num_sigs_to_create = 1000000
        self.num_nonces_to_create = 1000000

        self._create_nonces()
        self._create_sigs()

        self.chain_id_bytes = bytes("CUSTOM", "utf-8") + b"\0"

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

    def create_wallet(self, name: str, **kwargs) -> None:
        """Generates a new wallet from a name - passphrase pair in the given vega service.

        Args:
            name:
                str, The name to use for the wallet
        """
        if self.vega_wallet is None:
            self.keys[name] = SigningKey.generate()
            self.pub_keys[name] = (
                self.keys[name].verify_key.encode(encoder=HexEncoder).decode()
            )
        else:
            self.vega_wallet.create_wallet(
                name=name,
                passphrase=kwargs.get("passphrase", self.full_wallet_default_pass),
            )
            self.pub_keys[name] = self.vega_wallet.public_key(name)

    def login(self, name: str, **kwargs) -> None:
        """Logs in to existing wallet in the given vega service.

        Args:
            name:
                str, The name of the wallet
        """
        if name not in self.keys:
            self.create_wallet(name=name)

    def submit_transaction(self, name: str, transaction: Any, transaction_type: str):
        # if self.remaining_until_height_update <= 0:
        #     self.block_height = self.core_client.LastBlockHeight(
        #         core_proto.LastBlockHeightRequest()
        #     ).height
        #     self.remaining_until_height_update = self.height_update_frequency

        transaction_info = {transaction_type: transaction}
        input_data = transaction_proto.InputData(
            nonce=self._next_nonce(),  # block_height=self.block_height,
            **transaction_info
        )

        serialised = self.chain_id_bytes + input_data.SerializeToString()

        trans = transaction_proto.Transaction(
            input_data=serialised,
            signature=signature_proto.Signature(
                value=self._next_sig(),
                algo="vega/ed25519",
                version=1,
            ),
            pub_key=self.pub_keys[name],
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

    def public_key(self, name: str) -> str:
        """Return the public key associated with a given wallet name.

        Args:
            name:
                str, The name to use for the wallet

        Returns:
            str, public key
        """
        return self.pub_keys[name]
