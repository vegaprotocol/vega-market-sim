from abc import ABC
from typing import Any

VEGA_DEFAULT_KEY_NAME = "foo"


class Wallet(ABC):
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
        pass

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
        pass

    def submit_transaction(self, transaction: Any, name: str, transaction_type: str):
        """Submits a transaction to Vega core via wallet

        Args:
            transaction:
                Any, The transaction object which will be submitted
            name:
                str, The name to use for the wallet executing the transaction
            transaction_type:
                str, The name, in underscore case, of the transaction
        """
        pass

    def public_key(self, name: str) -> str:
        """Return the public key associated with a given wallet name.

        Args:
            name:
                str, The name to use for the wallet

        Returns:
            str, public key
        """
        pass
