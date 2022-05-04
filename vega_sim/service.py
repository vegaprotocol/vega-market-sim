from __future__ import annotations

import logging
from abc import ABC
from functools import wraps
from time import time
from typing import List, Optional, Tuple, Union

import grpc
import requests
import vegaapiclient as vac
import vegaapiclient.generated.vega as vega_protos

import vega_sim.api.data as data
import vega_sim.api.data_raw as data_raw
import vega_sim.api.faucet as faucet
import vega_sim.api.governance as gov
import vega_sim.api.trading as trading
import vega_sim.api.wallet as wallet
from vega_sim.api.helpers import num_to_padded_int

logger = logging.getLogger(__name__)

TIME_FORWARD_URL = "{base_url}/api/v1/forwardtime"


class LoginError(Exception):
    pass


def raw_data(fn):
    @wraps(fn)
    def wrapped_fn(self, *args, **kwargs):
        if self.warn_on_raw_data_access:
            logger.warn(
                f"Using function with raw data from data-node {fn.__qualname__}. Be"
                " wary if prices/positions are not converted from int form"
            )
        return fn(self, *args, **kwargs)

    return wrapped_fn


class VegaService(ABC):
    def __init__(
        self, can_control_time: bool = False, warn_on_raw_data_access: bool = True
    ):
        """A generic service for accessing a set of Vega processes.

        Contains generic methods aimed at working whether the derived class
        is referencing a locally hosted Nullchain version of Vega
        or a fully-fledged remote market.

        Args:
            can_control_time:
                bool, default False, do we have control over the passage of time.
                    Generally this will be True for a nullchain, but False for
                    anything else. When False we sleep when a wait is required,
                    when True we can manually forward instead.
            warn_on_raw_data_access:
                bool, default True, whether to warn on accessing functions containing
                    data straight from a data-node. The main risk here relates to
                    decimal places. On non-raw data functions the 'zero-padded int'
                    version of numbers will be promised to have been converted to a
                    real float version. On raw versions (generally complex objects)
                    they may well be still zero padded integers which must be
                    converted by the user.
                    (e.g. 10.1 with decimal places set to 2 would be 1010)

        """
        self.login_tokens = {}
        self.pub_keys = {}
        self._trading_data_client = None
        self.can_control_time = can_control_time
        self.warn_on_raw_data_access = warn_on_raw_data_access

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

    def _default_wait_fn(self) -> None:
        time.sleep(1)

    def trading_data_client(self) -> vac.VegaTradingDataClient:
        if self._trading_data_client is None:
            channel = grpc.insecure_channel(
                self.data_node_grpc_url(), options=(("grpc.enable_http_proxy", 0),)
            )
            grpc.channel_ready_future(channel).result(timeout=10)
            self._trading_data_client = vac.VegaTradingDataClient(
                self.data_node_grpc_url(),
                channel=channel,
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

    def mint(self, wallet_name: str, asset: str, amount: float) -> None:
        """Mints a given amount of requested asset into the associated wallet

        Args:
            wallet_name:
                str, The name of the wallet
            asset:
                str, The ID of the asset to mint
            amount:
                float, the amount of asset to mint
        """
        self._check_logged_in(wallet_name)
        asset_decimals = data.asset_decimals(
            asset_id=asset, data_client=self.trading_data_client()
        )
        faucet.mint(
            self.pub_keys[wallet_name],
            asset,
            num_to_padded_int(amount, asset_decimals),
            faucet_url=self.faucet_url(),
        )

    def forward(self, time: str) -> None:
        """Steps chain forward a given amount of time, either with an amount of time or
            until a specified time.

        Args:
            time:
                str, time argument to use when stepping forwards. Either an increment
                (e.g. 1s, 10hr etc) or an ISO datetime (e.g. 2021-11-25T14:14:00Z)
        """
        if not self.can_control_time:
            return
        payload = {"forward": time}

        requests.post(
            TIME_FORWARD_URL.format(base_url=self.vega_node_url()), json=payload
        ).raise_for_status()

    def create_asset(
        self,
        wallet_name: str,
        name: str,
        symbol: str,
        total_supply: int = 1,
        decimals: int = 0,
        quantum: int = 1,
        max_faucet_amount: int = 10e9,
    ):
        """Creates a simple asset and automatically approves the proposal (assuming the proposing wallet has sufficient governance tokens).

        Args:
            wallet_name:
                str, The name of the wallet proposing the asset
            name:
                str, The name of the asset
            symbol:
                str, The symbol to use for the asset
            total_supply:
                int, The initial total supply of the asset (will increase when fauceted)
            decimals:
                int, The number of decimals in which to represent the asset. (e.g with 2 then integer value 101 is really 1.01)
            quantum:
                int, The smallest unit of currency it makes sense to talk about
            max_faucet_amount:
                int, The maximum number of tokens which can be fauceted (in asset decimal precision)
        """
        blockchain_time_seconds = gov.get_blockchain_time(self.trading_data_client())
        proposal_id = gov.propose_asset(
            self.login_tokens[wallet_name],
            pub_key=self.pub_keys[wallet_name],
            name=name,
            symbol=symbol,
            total_supply=total_supply,
            decimals=decimals,
            max_faucet_amount=max_faucet_amount,
            quantum=quantum,
            data_client=self.trading_data_client(),
            wallet_server_url=self.wallet_url(),
            closing_time=blockchain_time_seconds + 30,
            enactment_time=blockchain_time_seconds + 360,
            validation_time=blockchain_time_seconds + 10,
        )
        gov.approve_proposal(
            proposal_id=proposal_id,
            login_token=self.login_tokens[wallet_name],
            pub_key=self.pub_keys[wallet_name],
            wallet_server_url=self.wallet_url(),
        )
        self.forward("365s")

    def create_simple_market(
        self,
        market_name: str,
        proposal_wallet: str,
        settlement_asset_id: str,
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
            settlement_asset_id:
                str, the asset id the market will use for settlement
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

        blockchain_time_seconds = gov.get_blockchain_time(self.trading_data_client())
        proposal_id = gov.propose_future_market(
            market_name=market_name,
            pub_key=self.pub_keys[proposal_wallet],
            login_token=self.login_tokens[proposal_wallet],
            settlement_asset_id=settlement_asset_id,
            data_client=self.trading_data_client(),
            termination_pub_key=self.pub_keys[termination_wallet],
            wallet_server_url=self.wallet_url(),
            position_decimals=position_decimals,
            market_decimals=market_decimals,
            closing_time=blockchain_time_seconds + 30,
            enactment_time=blockchain_time_seconds + 360,
            validation_time=blockchain_time_seconds + 10,
            **additional_kwargs,
        )
        gov.approve_proposal(
            proposal_id,
            self.pub_keys[proposal_wallet],
            self.login_tokens[proposal_wallet],
            self.wallet_url(),
        )
        self.forward("360s")

    def submit_market_order(
        self,
        trading_wallet: str,
        market_id: str,
        side: Union[vega_protos.vega.Side, str],
        volume: float,
        fill_or_kill: bool = True,
        wait: bool = True,
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
                float, The volume to trade.
            wait:
                bool, whether to wait for order acceptance.
                    If true, will raise an error if order is not accepted

        Returns:
            str, The ID of the order
        """

        return self.submit_order(
            trading_wallet=trading_wallet,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_FOK" if fill_or_kill else "TIME_IN_FORCE_IOC",
            order_type="TYPE_MARKET",
            side=side,
            volume=num_to_padded_int(
                volume,
                data.market_position_decimals(
                    market_id, data_client=self.trading_data_client()
                ),
            ),
            wait=wait,
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
                float, volume of the order
            price:
                float, price of the order
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
            volume=num_to_padded_int(
                volume,
                data.market_position_decimals(
                    market_id, data_client=self.trading_data_client()
                ),
            ),
            price=num_to_padded_int(
                price,
                data.market_price_decimals(
                    market_id, data_client=self.trading_data_client()
                ),
            ),
            expires_at=expires_at,
            pegged_order=pegged_order,
            wait=wait,
            time_forward_fn=self._default_wait_fn,
        )

    def amend_order(
        self,
        trading_wallet: str,
        market_id: str,
        order_id: str,
        price: Optional[float] = None,
        expires_at: Optional[int] = None,
        pegged_offset: Optional[str] = None,
        pegged_reference: Optional[vega_protos.vega.PeggedReference] = None,
        volume_delta: float = 0,
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
                int, change in volume of the order
            price:
                int, price of the order
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
            price=num_to_padded_int(
                price,
                data.market_price_decimals(
                    market_id, data_client=self.trading_data_client()
                ),
            )
            if price is not None
            else None,
            expires_at=expires_at,
            pegged_offset=pegged_offset,
            pegged_reference=pegged_reference,
            volume_delta=num_to_padded_int(
                volume_delta,
                data.market_position_decimals(
                    market_id, data_client=self.trading_data_client()
                ),
            ),
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

    def update_network_parameter(
        self, proposal_wallet: str, parameter: str, new_value: str
    ):
        """Updates a network parameter by first proposing and then voting to approve
        the change, followed by advancing the network time period forwards.

        If the genesis setup of the market is such that this meets requirements then
        the proposal will be approved. Otherwise others may need to vote too.

        Args:
            proposal_wallet:
                str, the wallet proposing the change
            parameter:
                str, the parameter to change
            new_value:
                str, the new value to set
        Returns:
            str, the ID of the proposal
        """
        blockchain_time_seconds = gov.get_blockchain_time(self.trading_data_client())

        proposal_id = gov.propose_network_parameter_change(
            parameter=parameter,
            value=new_value,
            pub_key=self.pub_keys[proposal_wallet],
            login_token=self.login_tokens[proposal_wallet],
            wallet_server_url=self.wallet_url(),
            data_client=self.trading_data_client(),
            closing_time=blockchain_time_seconds + 30,
            enactment_time=blockchain_time_seconds + 360,
            validation_time=blockchain_time_seconds + 1,
        )
        gov.approve_proposal(
            proposal_id=proposal_id,
            pub_key=self.pub_keys[proposal_wallet],
            login_token=self.login_tokens[proposal_wallet],
            wallet_server_url=self.wallet_url(),
        )
        self.forward("360s")

    def settle_market(
        self,
        settlement_wallet: str,
        settlement_price: float,
        market_id: str,
    ):
        decimals = data.market_price_decimals(
            market_id, data_client=self.trading_data_client()
        )

        oracle_name = (
            data_raw.market_info(market_id)
            .tradable_instrument.instrument.future.oracle_spec_for_settlement_price.filters[
                0
            ]
            .key.name
        )
        gov.settle_oracle(
            login_token=self.login_tokens[settlement_wallet],
            pub_key=self.pub_keys[settlement_wallet],
            wallet_server_url=self.wallet_url(),
            oracle_name=oracle_name,
            settlement_price=num_to_padded_int(settlement_price, decimals=decimals),
        )

    @raw_data
    def party_account(
        self,
        wallet_name: str,
        asset_id: str,
        market_id: str,
    ) -> data_raw.AccountData:
        """Output money in general accounts/margin accounts/bond accounts (if exists)
        of a party."""
        return data_raw.party_account(
            self.pub_keys[wallet_name],
            asset_id=asset_id,
            market_id=market_id,
            data_client=self.trading_data_client(),
        )

    @raw_data
    def positions_by_market(
        self,
        wallet_name: str,
        market_id: str,
    ) -> List[vega_protos.vega.Position]:
        """Output positions of a party."""
        return data_raw.positions_by_market(
            self.pub_keys[wallet_name],
            market_id=market_id,
            data_client=self.trading_data_client(),
        )

    @raw_data
    def all_markets(
        self,
    ) -> List[vega_protos.markets.Market]:
        """
        Output market info.
        """
        return data_raw.all_markets(data_client=self.trading_data_client())

    @raw_data
    def market_info(
        self,
        market_id: str,
    ) -> vega_protos.markets.Market:
        """
        Output market info.
        """
        return data_raw.market_info(
            market_id=market_id, data_client=self.trading_data_client()
        )

    @raw_data
    def market_data(
        self,
        market_id: str,
    ) -> vega_protos.markets.MarketData:
        """
        Output market info.
        """
        return data_raw.market_data(
            market_id=market_id, data_client=self.trading_data_client()
        )

    @raw_data
    def infrastructure_fee_accounts(
        self,
        asset_id: str,
    ) -> List[vega_protos.vega.Account]:
        """
        Output infrastructure fee accounts
        """
        return data_raw.infrastructure_fee_accounts(
            asset_id=asset_id, data_client=self.trading_data_client()
        )

    @raw_data
    def market_accounts(
        self,
        asset_id: str,
        market_id: str,
    ) -> data_raw.MarketAccount:
        """
        Output liquidity fee account/ insurance pool in the market
        """
        return data_raw.market_accounts(
            asset_id=asset_id,
            market_id=market_id,
            data_client=self.trading_data_client(),
        )

    def market_account(
        self,
        market_id: str,
        account_type: vega_protos.vega.AccountType,
    ) -> float:
        """
        Returns the current asset value in the Market's fee account

        Args:
            market_id:
                str, The ID of the market to check
            account_type:
                vega.AccountType, the account type to check for

        Returns:
            float, the current balance in the market's fee asset
        """
        return data.market_account(
            market_id=market_id,
            account_type=account_type,
            data_client=self.trading_data_client(),
        )

    def best_prices(
        self,
        market_id: str,
    ) -> Tuple[int, int]:
        """
        Output the best static bid price and best static ask price in current market.
        """
        return data.best_prices(
            market_id=market_id, data_client=self.trading_data_client()
        )

    def open_orders_by_market(
        self,
        market_id: str,
    ) -> data.OrderBook:
        return data.open_orders_by_market(
            market_id=market_id, data_client=self.trading_data_client()
        )

    def submit_simple_liquidity(
        self,
        wallet_name: str,
        market_id: str,
        commitment_amount: float,
        fee: float,
        reference_buy: str,
        reference_sell: str,
        delta_buy: int,
        delta_sell: int,
        is_amendment: bool = False,
    ):
        """Submit/Amend a simple liquidity commitment (LP) with a single amount on each side.

        Args:
            wallet_name:
                str, The name of the wallet which is placing the order
            market_id:
                str, The ID of the market to place the commitment on
            commitment_amount:
                int, The amount in asset decimals of market asset to commit to
                 liquidity provision
            fee:
                float, The fee level at which to set the LP fee
                 (in %, e.g. 0.01 == 1% and 1 == 100%)
            reference_buy:
                str, the reference point to use for the buy side of LP
            reference_sell:
                str, the reference point to use for the sell side of LP
            delta_buy:
                int, the offset from reference point for the buy side of LP
            delta_sell:
                int, the offset from reference point for the sell side of LP
        """
        asset_id = data_raw.market_info(
            market_id=market_id, data_client=self.trading_data_client()
        ).tradable_instrument.instrument.settlement_asset
        return trading.submit_simple_liquidity(
            market_id=market_id,
            commitment_amount=num_to_padded_int(
                commitment_amount,
                data.asset_decimals(
                    asset_id=asset_id, data_client=self.trading_data_client()
                ),
            ),
            fee=fee,
            reference_buy=reference_buy,
            reference_sell=reference_sell,
            delta_buy=delta_buy,
            delta_sell=delta_sell,
            login_token=self.login_tokens[wallet_name],
            pub_key=self.pub_keys[wallet_name],
            is_amendment=is_amendment,
            wallet_server_url=self.wallet_url(),
        )

    def find_asset_id(self, symbol: str, raise_on_missing: bool = False) -> str:
        """Looks up the Asset ID of a given asset name

        Args:
            symbol:
                str, The symbol of the asset to look up
            raise_on_missing:
                bool, whether to raise an Error or silently return if the asset
                 does not exist

        Returns:
            str, the ID of the asset
        """
        return data.find_asset_id(
            symbol=symbol,
            raise_on_missing=raise_on_missing,
            data_client=self.trading_data_client(),
        )

    @raw_data
    def order_status(
        self, order_id: str, version: int = 0
    ) -> Optional[vega_protos.vega.Order]:
        """Loads information about a specific order identified by the ID.
        Optionally return historic order versions.

        Args:
            order_id:
                str, the order identifier as specified by Vega when originally placed
            version:
                int, Optional, Version of the order:
                    - Set `version` to 0 for most recent version of the order
                    - Set `1` for original version of the order
                    - Set `2` for first amendment, `3` for second amendment, etc
        Returns:
            Optional[vega.Order], the requested Order object or None if nothing found
        """
        return data_raw.order_status(
            order_id=order_id, data_client=self.trading_data_client(), version=version
        )
