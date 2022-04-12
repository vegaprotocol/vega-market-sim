from __future__ import annotations

from abc import ABC
from typing import Optional, Union

import requests
import vegaapiclient as vac
import vegaapiclient.generated.vega as vega_protos

import vega_sim.api.faucet as faucet
import vega_sim.api.governance as gov
import vega_sim.api.trading as trading
import vega_sim.api.wallet as wallet

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
            **additional_kwargs,
        )
        gov.accept_market_proposal(
            self.login_tokens[proposal_wallet],
            proposal_id,
            self.pub_keys[proposal_wallet],
            self.wallet_url(),
        )
        self.forward("480s")

    def submit_market_order(
        self,
        trading_wallet: str,
        market_id: str,
        side: Union[vega_protos.vega.Side, str],
        volume: int,
        fill_or_kill: bool = True,
    ) -> str:
        """Places a simple Market order, either as Fill-Or-Kill or Immediate-Or-Cancel.

        Args:
            trading_wallet:
                str, the name of the wallet to use for trading
            market_name:
                str, name of the market
            side:
                vega.Side or str, Side of the order (BUY or SELL)
            volume:
                int, The volume to trade in market position decimal places.

        Returns:
            str, The ID of the order
        """
        return self.submit_order(
            trading_wallet=trading_wallet,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_FOK" if fill_or_kill else "TIME_IN_FORCE_IOC",
            order_type="TYPE_MARKET",
            side=side,
            volume=volume,
        )

    def submit_order(
        self,
        trading_wallet: str,
        market_id: str,
        order_type: Union[vega_protos.vega.Order.Type, str],
        time_in_force: Union[vega_protos.vega.Order.TimeInForce, str],
        side: Union[vega_protos.vega.Side, str],
        volume: int,
        price: Optional[int] = None,
        expires_at: Optional[int] = None,
        pegged_order: Optional[vega_protos.vega.PeggedOrder] = None,
        wait: bool = True,
    ) -> Optional[str]:
        """
        Submit orders as specified to required pre-existing market.
        Optionally wait for acceptance of order (raises on non-acceptance)

        Args:
            trading_wallet:
                str, the name of the wallet to use for trading
            market_id:
                str, the ID of the required market on vega
            order_type:
                vega.Order.Type or str, The type of order required (market/limit etc).
                    See API documentation for full list of options
            time_in_force:
                vega.Order.TimeInForce or str, The time in force setting for the order
                    (GTC, GTT, Fill Or Kill etc.)
                    See API documentation for full list of options
            side:
                vega.Side or str, Side of the order (BUY or SELL)
            volume:
                int, volume of the order in market position decimals
                    (e.g. if position decimals is 2 then 1.0 should be passed as 100)
            price:
                str, price of the order in market price decimals
                    (e.g. if price decimals is 2 then 10.00 should be passed as 1000)
            expires_at:
                int, Optional timestamp for when the order will expire,
                    in nanoseconds since the epoch,
                    required field only for [`Order.TimeInForce`].
                    Defaults to 2 minutes
            pegged_order:
                vega.PeggedOrder, Used to specify the details for a pegged order
            wait:
                bool, whether to wait for order acceptance.
                    If true, will raise an error if order is not accepted
        Returns:
            Optional[str], If order acceptance is waited for, returns order ID.
                Otherwise None
        """
        return trading.submit_order(
            login_token=self.login_tokens[trading_wallet],
            data_client=self.trading_data_client(),
            wallet_server_url=self.wallet_url(),
            pub_key=self.pub_keys[trading_wallet],
            market_id=market_id,
            order_type=order_type,
            time_in_force=time_in_force,
            side=side,
            volume=volume,
            price=price,
            expires_at=expires_at,
            pegged_order=pegged_order,
            wait=wait,
        )

    def amend_order(
        self,
        trading_wallet: str,
        market_id: str,
        order_id: str,
        price: Optional[int] = None,
        expires_at: Optional[int] = None,
        pegged_offset: Optional[str] = None,
        pegged_reference: Optional[vega_protos.vega.PeggedReference] = None,
        volume_delta: int = 0,
        time_in_force: Optional[Union[vega_protos.vega.Order.TimeInForce, str]] = None,
    ):
        """
        Amend a Limit order by orderID in the specified market

        Args:
            trading_wallet:
                str, the name of the wallet to use for trading
            market_id:
                str, the ID of the required market on vega
            order_type:
                vega.Order.Type or str, The type of order required (market/limit etc).
                    See API documentation for full list of options
            side:
                vega.Side or str, Side of the order (BUY or SELL)
            volume_delta:
                int, change in volume of the order in market position decimals
                    (e.g. if position decimals is 2 then 1.0 should be passed as 100)
            price:
                int, price of the order in market price decimals
                    (e.g. if price decimals is 2 then 10.00 should be passed as 1000)
            time_in_force:
                vega.Order.TimeInForce or str, The time in force setting for the order
                    (Only valid options for market are TIME_IN_FORCE_IOC and
                        TIME_IN_FORCE_FOK)
                    See API documentation for full list of options
                    Defaults to Fill or Kill
        """
        trading.amend_order(
            login_token=self.login_tokens[trading_wallet],
            wallet_server_url=self.wallet_url(),
            pub_key=self.pub_keys[trading_wallet],
            market_id=market_id,
            order_id=order_id,
            price=price,
            expires_at=expires_at,
            pegged_offset=pegged_offset,
            pegged_reference=pegged_reference,
            volume_delta=volume_delta,
            time_in_force=time_in_force,
        )

    def cancel_order(
        self,
        trading_wallet: str,
        market_id: str,
        order_id: str,
    ):
        """
        Cancel Order

        Args:
            trading_wallet:
                str, the name of the wallet to use for trading
            market_id:
                str, the ID of the required market on vega
            order_id:
                str, Identifier of the order to cancel
        """
        trading.cancel_order(
            login_token=self.login_tokens[trading_wallet],
            wallet_server_url=self.wallet_url(),
            pub_key=self.pub_keys[trading_wallet],
            market_id=market_id,
            order_id=order_id,
        )
