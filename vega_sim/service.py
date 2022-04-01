import vega_sim.api.wallet as wallet
import vega_sim.api.faucet as faucet

from abc import ABC


class LoginError(Exception):
    pass


class VegaService(ABC):
    def __init__(self):
        self.login_tokens = {}
        self.pub_keys = {}

    def wallet_url(self) -> str:
        pass

    def data_node_rest_url(self) -> str:
        pass

    def faucet_url(self) -> str:
        pass

    # def node_rest_url(self):
    #     pass

    def _check_logged_in(self, wallet_name: str):
        if wallet_name not in self.login_tokens:
            raise LoginError("Wallet not yet logged into")

    def login(self, name: str, passphrase: str) -> str:
        """Logs in to existing wallet in the given vega service.

        Args:
            name:
                str, The name of the wallet
            passphrase:
                str, The login passphrase used when creating the wallet
        Returns:
            str, public key associated to this waller
        """
        self.login_tokens[name] = wallet.login(name, passphrase, self.wallet_url())
        self.pub_keys[name] = wallet.generate_keypair(
            self.login_tokens[name],
            passphrase,
            self.wallet_url(),
            metadata=[{"name": "default_key"}],
        )
        return self.pub_keys[name]

    def create_wallet(self, name: str, passphrase: str) -> str:
        """Logs in to existing wallet in the given vega service.

        Args:
            name:
                str, The name of the wallet
            passphrase:
                str, The login passphrase used when creating the wallet
        Returns:
            str, public key associated to this waller
        """
        token = wallet.create_wallet(name, passphrase, self.wallet_url())
        self.login_tokens[name] = token
        self.pub_keys[name] = wallet.generate_keypair(
            self.login_tokens[name],
            passphrase,
            self.wallet_url(),
            metadata=[{"name": "default_key"}],
        )

    def mint(self, wallet_name: str, asset: str, amount: int) -> None:
        """Mints a given amount of requested asset into the associated wallet

        Args:
            wallet_name:
                str, The name of the wallet
            asset:
                str, The name of the asset to mint
            amount:
                int, the amount of asset to mint
        """
        self._check_logged_in(wallet_name)
        faucet.mint(
            self.pub_keys[wallet_name], asset, amount, faucet_url=self.faucet_url()
        )
