from typing import Optional
import requests

import vegaapiclient as vac
import vega_sim.api.wallet as wallet
import vega_sim.api.faucet as faucet
import vega_sim.api.governance as gov

from abc import ABC

TIME_FORWARD_URL = "{base_url}/api/v1/forwardtime"


class LoginError(Exception):
    pass


class VegaService(ABC):
    def __init__(self):
        self.login_tokens = {}
        self.pub_keys = {}
        self._trading_data_client = None

    def wallet_url(self) -> str:
        pass

    def data_node_rest_url(self) -> str:
        pass

    def faucet_url(self) -> str:
        pass

    def vega_node_url(self) -> str:
        pass

    def data_node_grpc_url(self) -> str:
        pass

    def trading_data_client(self) -> vac.VegaTradingDataClient:
        if self._trading_data_client is None:
            self._trading_data_client = vac.VegaTradingDataClient(
                self.data_node_grpc_url()
            )
        return self._trading_data_client

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

    def forward(self, time: str) -> None:
        """Steps chain forward a given amount of time, either with an amount of time or
            until a specified time.

        Args:
            time:
                str, time argument to use when stepping forwards. Either an increment
                (e.g. 1s, 10hr etc) or an ISO datetime (e.g. 2021-11-25T14:14:00Z)
        """
        payload = {"forward": time}

        requests.post(
            TIME_FORWARD_URL.format(base_url=self.vega_node_url()), json=payload
        ).raise_for_status()

    def create_simple_market(
        self,
        market_name: str,
        proposal_wallet: str,
        settlement_asset: str,
        termination_wallet: str,
        future_asset: Optional[str] = None,
        position_decimals: Optional[int] = None,
        market_decimals: Optional[int] = None,
    ) -> None:
        """Creates a simple futures market with a predefined reasonable set of parameters.

        Args:
            market_name:c
                str, name of the market
            proposal_wallet:
                str, the name of the wallet to use for proposing the market
            settlement_asset:
                str, the asset the market will use for settlement
            termination_wallet:
                str, the name of the wallet which will be used to send termination data
            position_decimals:
                int, the decimal place precision to use for positions
                    (e.g. 2 means 2dp, so 200 => 2.00, 3 would mean 200 => 0.2)
           market_decimals:
                int, the decimal place precision to use for market prices
                    (e.g. 2 means 2dp, so 200 => 2.00, 3 would mean 200 => 0.2)

        """
        additional_kwargs = {}
        if future_asset is not None:
            additional_kwargs["future_asset"] = future_asset

        proposal_id = gov.propose_future_market(
            market_name=market_name,
            pub_key=self.pub_keys[proposal_wallet],
            login_token=self.login_tokens[proposal_wallet],
            settlement_asset=settlement_asset,
            data_client=self.trading_data_client(),
            termination_pub_key=self.pub_keys[termination_wallet],
            wallet_server_url=self.wallet_url(),
            position_decimals=position_decimals,
            market_decimals=market_decimals,
            **additional_kwargs
        )
        gov.accept_market_proposal(
            self.login_tokens[proposal_wallet],
            proposal_id,
            self.pub_keys[proposal_wallet],
            self.wallet_url(),
        )
        self.forward("480s")
