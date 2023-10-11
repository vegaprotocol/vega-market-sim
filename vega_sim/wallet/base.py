from abc import ABC, abstractmethod
from typing import Any, Optional

VEGA_DEFAULT_KEY_NAME = "foo"
DEFAULT_WALLET_NAME = "MarketSim"


class Wallet(ABC):
    @abstractmethod
    def create_key(
        self,
        name: str,
        wallet_name: Optional[str] = None,
    ) -> str:
        """Generates a new wallet key in the given vega service.

        Args:
            name:
                str, The name to use for the wallet key
            wallet_name:
                str, The wallet to use if not the default
        Returns:
            str, login token to use in authenticated requests
        """
        pass

    @abstractmethod
    def submit_transaction(
        self,
        transaction: Any,
        key_name: str,
        transaction_type: str,
        wallet_name: Optional[str],
        check_tx_fail: bool = True,
    ):
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

    @abstractmethod
    def public_key(
        self,
        name: str,
        wallet_name: Optional[str] = None,
    ) -> str:
        """Return the public key associated with a given key name.

        Args:
            name:
                str, The name to use for the wallet

        Returns:
            str, public key
        """
        pass
