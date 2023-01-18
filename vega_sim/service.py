from __future__ import annotations

import datetime
import logging
import threading
import time
import copy
from abc import ABC
from collections import defaultdict
from dataclasses import dataclass
from functools import wraps
from queue import Queue, Empty
from typing import Dict, List, Optional, Tuple, Union, Any, Generator
from itertools import product

import grpc
import vega_sim.api.data as data
import vega_sim.api.data_raw as data_raw
import vega_sim.api.faucet as faucet
import vega_sim.api.governance as gov
import vega_sim.api.market as market
import vega_sim.api.trading as trading
import vega_sim.grpc.client as vac
import vega_sim.proto.vega as vega_protos
import vega_sim.proto.vega.data_source_pb2 as data_source_protos
import vega_sim.proto.data_node.api.v2 as data_node_protos_v2

from vega_sim.api.helpers import (
    forward,
    num_to_padded_int,
    wait_for_core_catchup,
    wait_for_datanode_sync,
)
from vega_sim.proto.vega.commands.v1.commands_pb2 import (
    OrderCancellation,
    OrderAmendment,
    OrderSubmission,
)
from vega_sim.proto.vega.governance_pb2 import (
    UpdateFutureProduct,
    UpdateInstrumentConfiguration,
    UpdateMarketConfiguration,
)
from vega_sim.proto.vega.markets_pb2 import (
    LiquidityMonitoringParameters,
    LogNormalRiskModel,
    PriceMonitoringParameters,
    SimpleModelParams,
)
from vega_sim.wallet.base import Wallet

logger = logging.getLogger(__name__)


@dataclass
class PeggedOrder:
    reference: vega_protos.vega.PeggedReference
    offset: float


class LoginError(Exception):
    pass


class DatanodeBehindError(Exception):
    pass


def _queue_forwarder(source: Generator[Any], sink: Queue[Any]) -> None:
    for elem in source:
        sink.put(elem)


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


class DecimalsCache(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret


class VegaService(ABC):
    def __init__(
        self,
        can_control_time: bool = False,
        warn_on_raw_data_access: bool = True,
        seconds_per_block: int = 1,
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
            seconds_per_block:
                int, default 1, How long each block represents in seconds. For a nullchain
                    service this can be known exactly, for anything else it will be an
                    estimate. Used for waiting/forwarding time and determining how far
                    forwards to place proposals starting/ending.

        """
        self._core_client = None
        self._core_state_client = None
        self._trading_data_client_v2 = None
        self.can_control_time = can_control_time
        self.warn_on_raw_data_access = warn_on_raw_data_access

        self._market_price_decimals = None
        self._market_pos_decimals = None
        self._asset_decimals = None
        self._market_to_asset = None
        self.seconds_per_block = seconds_per_block

        self.orders_lock = threading.RLock()
        self.transfers_lock = threading.RLock()
        self.trades_lock = threading.RLock()
        self._order_state_from_feed = {}
        self._transfer_state_from_feed = {}
        self._trades_from_feed: List[data.Trade] = []

        self._observation_feeds: List[Queue[Any]] = []
        self._observation_thread = None
        self._aggregated_observation_feed: Queue[Any] = Queue()
        self._kill_thread_sig = threading.Event()

    @property
    def market_price_decimals(self) -> int:
        if self._market_price_decimals is None:
            self._market_price_decimals = DecimalsCache(
                lambda market_id: data.market_price_decimals(
                    market_id=market_id, data_client=self.trading_data_client_v2
                )
            )
        return self._market_price_decimals

    @property
    def market_pos_decimals(self) -> int:
        if self._market_pos_decimals is None:
            self._market_pos_decimals = DecimalsCache(
                lambda market_id: data.market_position_decimals(
                    market_id=market_id, data_client=self.trading_data_client_v2
                )
            )
        return self._market_pos_decimals

    @property
    def asset_decimals(self) -> int:
        if self._asset_decimals is None:
            self._asset_decimals = DecimalsCache(
                lambda asset_id: data.get_asset_decimals(
                    asset_id=asset_id, data_client=self.trading_data_client_v2
                )
            )
        return self._asset_decimals

    @property
    def market_to_asset(self) -> str:
        if self._market_to_asset is None:
            self._market_to_asset = DecimalsCache(
                lambda market_id: data_raw.market_info(
                    market_id=market_id, data_client=self.trading_data_client_v2
                ).tradable_instrument.instrument.future.settlement_asset
            )
        return self._market_to_asset

    @property
    def data_node_rest_url(self) -> str:
        pass

    @property
    def faucet_url(self) -> str:
        pass

    @property
    def vega_node_url(self) -> str:
        pass

    @property
    def vega_node_grpc_url(self) -> str:
        pass

    @property
    def data_node_grpc_url(self) -> str:
        pass

    @property
    def wallet(self) -> Wallet:
        pass

    def wait_fn(self, wait_multiple: float = 1) -> None:
        time.sleep(1 * wait_multiple)

    @property
    def trading_data_client_v2(self) -> vac.VegaTradingDataClientV2:
        if self._trading_data_client_v2 is None:
            channel = grpc.insecure_channel(
                self.data_node_grpc_url, options=(("grpc.enable_http_proxy", 0),)
            )
            grpc.channel_ready_future(channel).result(timeout=30)
            self._trading_data_client_v2 = vac.VegaTradingDataClientV2(
                self.data_node_grpc_url,
                channel=channel,
            )
        return self._trading_data_client_v2

    @property
    def core_state_client(self) -> vac.VegaCoreStateClient:
        if self._core_state_client is None:
            channel = grpc.insecure_channel(self.vega_node_grpc_url)

            grpc.channel_ready_future(channel).result(timeout=10)
            self._core_state_client = vac.VegaCoreStateClient(
                self.vega_node_grpc_url,
                channel=channel,
            )
        return self._core_state_client

    @property
    def core_client(self) -> vac.VegaCoreClient:
        if self._core_client is None:
            channel = grpc.insecure_channel(self.vega_node_grpc_url)

            grpc.channel_ready_future(channel).result(timeout=10)
            self._core_client = vac.VegaCoreClient(
                self.vega_node_grpc_url,
                channel=channel,
            )
        return self._core_client

    def wait_for_datanode_sync(self) -> None:
        wait_for_datanode_sync(self.trading_data_client_v2, self.core_client)

    def wait_for_core_catchup(self) -> None:
        wait_for_core_catchup(self.core_client)

    def wait_for_total_catchup(self) -> None:
        self.wait_for_core_catchup()
        self.wait_for_datanode_sync()

    def stop(self) -> None:
        self._kill_thread_sig.set()

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
        return self.wallet.login(name=name, passphrase=passphrase)

    def create_wallet(
        self, name: str, passphrase: str, key_name: Optional[str] = None
    ) -> str:
        """Logs in to existing wallet in the given vega service.

        Args:
            name:
                str, The name of the wallet
            passphrase:
                str, The login passphrase used when creating the wallet
             key_name:
                str, optional, Name of key in wallet for agent to use. Defaults
                to value in the environment variable "VEGA_DEFAULT_KEY_NAME".
        Returns:
            str, public key associated to this waller
        """
        return self.wallet.create_wallet(
            name=name, passphrase=passphrase, key_name=key_name
        )

    def mint(
        self,
        wallet_name: str,
        asset: str,
        amount: float,
        key_name: Optional[str] = None,
    ) -> None:
        """Mints a given amount of requested asset into the associated wallet

        Args:
            wallet_name:
                str, The name of the wallet
            asset:
                str, The ID of the asset to mint
            amount:
                float, the amount of asset to mint
            key_name:
                Optional[str], key name stored in metadata. Defaults to None.
        """
        asset_decimals = self.asset_decimals[asset]
        curr_acct = self.party_account(
            wallet_name=wallet_name, asset_id=asset, market_id=None, key_name=key_name
        ).general

        faucet.mint(
            self.wallet.public_key(wallet_name, key_name),
            asset,
            num_to_padded_int(amount, asset_decimals),
            faucet_url=self.faucet_url,
        )

        self.wait_fn(1)
        self.wait_for_core_catchup()
        for i in range(500):
            self.wait_fn(1)
            time.sleep(0.0005 * 1.01**i)
            post_acct = self.party_account(
                wallet_name=wallet_name,
                asset_id=asset,
                market_id=None,
                key_name=key_name,
            ).general
            if post_acct > curr_acct:
                return

        raise Exception(
            f"Failure minting asset {asset} for party {wallet_name}. Funds never"
            " appeared in party account"
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
        forward(time=time, vega_node_url=self.vega_node_url)

    def create_asset(
        self,
        wallet_name: str,
        name: str,
        symbol: str,
        decimals: int = 0,
        quantum: int = 1,
        max_faucet_amount: int = 10e9,
        key_name: Optional[str] = None,
    ):
        """Creates a simple asset and automatically approves the proposal (assuming the
         proposing wallet has sufficient governance tokens).

        Args:
            wallet_name:
                str, The name of the wallet proposing the asset
            name:
                str, The name of the asset
            symbol:
                str, The symbol to use for the asset
            decimals:
                int, The number of decimals in which to represent the asset.
                    (e.g with 2 then integer value 101 is really 1.01)
            quantum:
                int, The smallest unit of currency it makes sense to talk about
            max_faucet_amount:
                int, The maximum number of tokens which can be fauceted
                    (in full decimal numbers, rather than asset decimal)
            key_name:
                optionaL, str, name of key in wallet to use
        """
        blockchain_time_seconds = gov.get_blockchain_time(self.trading_data_client_v2)

        proposal_id = gov.propose_asset(
            wallet=self.wallet,
            wallet_name=wallet_name,
            name=name,
            symbol=symbol,
            decimals=decimals,
            max_faucet_amount=max_faucet_amount * 10**decimals,
            quantum=quantum,
            data_client=self.trading_data_client_v2,
            closing_time=blockchain_time_seconds + self.seconds_per_block * 90,
            enactment_time=blockchain_time_seconds + self.seconds_per_block * 100,
            validation_time=blockchain_time_seconds + self.seconds_per_block * 30,
            time_forward_fn=lambda: self.wait_fn(2),
            key_name=key_name,
        )
        self.wait_fn(1)
        gov.approve_proposal(
            proposal_id=proposal_id,
            wallet_name=wallet_name,
            wallet=self.wallet,
            key_name=key_name,
        )
        self.wait_fn(110)

    def create_market_from_config(
        self,
        proposal_wallet_name: str,
        market_config: market.MarketConfig,
        proposal_key_name: Optional[str] = None,
    ):
        blockchain_time_seconds = gov.get_blockchain_time(self.trading_data_client_v2)

        proposal_id = gov.propose_market_from_config(
            wallet=self.wallet,
            data_client=self.trading_data_client_v2,
            proposal_wallet_name=proposal_wallet_name,
            proposal_key_name=proposal_key_name,
            market_config=market_config,
            closing_time=blockchain_time_seconds + self.seconds_per_block * 90,
            enactment_time=blockchain_time_seconds + self.seconds_per_block * 90,
            time_forward_fn=lambda: self.wait_fn(2),
        )

        gov.approve_proposal(
            proposal_id=proposal_id,
            wallet=self.wallet,
            wallet_name=proposal_wallet_name,
            key_name=proposal_key_name,
        )
        self.wait_fn(110)

    def create_simple_market(
        self,
        market_name: str,
        proposal_wallet: str,
        settlement_asset_id: str,
        termination_wallet: str,
        future_asset: Optional[str] = None,
        position_decimals: Optional[int] = None,
        market_decimals: Optional[int] = None,
        risk_aversion: Optional[float] = 1e-6,
        tau: Optional[float] = 1.0 / 365.25 / 24,
        sigma: Optional[float] = 1.0,
        price_monitoring_parameters: Optional[
            vega_protos.markets.PriceMonitoringParameters
        ] = None,
        key_name: Optional[str] = None,
        termination_key: Optional[str] = None,
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
            price_monitoring_parameters:
                PriceMonitoringParameters, A set of parameters determining when the
                    market will drop into a price auction. If not passed defaults
                    to a very permissive setup
            key_name:
                Optional[str], name of key proposing market. Defaults to None.
            termination_key:
                Optional[str], name of key settling market. Defaults to None.

        """
        additional_kwargs = {}
        if future_asset is not None:
            additional_kwargs["future_asset"] = future_asset

        blockchain_time_seconds = gov.get_blockchain_time(self.trading_data_client_v2)

        risk_model = vega_protos.markets.LogNormalRiskModel(
            risk_aversion_parameter=risk_aversion,
            tau=tau,
            params=vega_protos.markets.LogNormalModelParams(mu=0, r=0.0, sigma=sigma),
        )
        proposal_id = gov.propose_future_market(
            market_name=market_name,
            wallet=self.wallet,
            wallet_name=proposal_wallet,
            key_name=key_name,
            settlement_asset_id=settlement_asset_id,
            data_client=self.trading_data_client_v2,
            termination_pub_key=self.wallet.public_key(
                termination_wallet, termination_key
            ),
            position_decimals=position_decimals,
            market_decimals=market_decimals,
            closing_time=blockchain_time_seconds + self.seconds_per_block * 90,
            enactment_time=blockchain_time_seconds + self.seconds_per_block * 100,
            risk_model=risk_model,
            time_forward_fn=lambda: self.wait_fn(2),
            price_monitoring_parameters=price_monitoring_parameters,
            **additional_kwargs,
        )
        gov.approve_proposal(
            proposal_id=proposal_id,
            wallet=self.wallet,
            wallet_name=proposal_wallet,
            key_name=key_name,
        )
        self.wait_fn(110)

    def submit_market_order(
        self,
        trading_wallet: str,
        market_id: str,
        side: Union[vega_protos.vega.Side, str],
        volume: float,
        fill_or_kill: bool = True,
        wait: bool = True,
        order_ref: Optional[str] = None,
        key_name: Optional[str] = None,
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
            order_ref:
                optional str, reference for later identification of order
            key_name:
                optional str, name of key in wallet to use

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
            wait=wait,
            order_ref=order_ref,
            key_name=key_name,
        )

    def submit_order(
        self,
        trading_wallet: str,
        market_id: str,
        order_type: Union[vega_protos.vega.Order.Type, str],
        time_in_force: Union[vega_protos.vega.Order.TimeInForce, str],
        side: Union[vega_protos.vega.Side, str],
        volume: float,
        price: Optional[float] = None,
        expires_at: Optional[float] = None,
        pegged_order: Optional[PeggedOrder] = None,
        wait: bool = True,
        order_ref: Optional[str] = None,
        key_name: Optional[str] = None,
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
                PeggedOrder, Used to specify the details for a pegged order
            wait:
                bool, whether to wait for order acceptance.
                    If true, will raise an error if order is not accepted
            order_ref:
                optional str, reference for later identification of order
            key_name:
                optional str, name of key in wallet to use

        Returns:
            Optional[str], If order acceptance is waited for, returns order ID.
                Otherwise None
        """
        submit_volume = num_to_padded_int(
            volume,
            self.market_pos_decimals[market_id],
        )
        if submit_volume <= 0:
            msg = "Not submitting order as volume is 0 or less."
            if wait:
                raise Exception(msg)
            else:
                logger.debug(msg)
                return

        submit_price = (
            num_to_padded_int(
                price,
                self.market_price_decimals[market_id],
            )
            if price is not None
            else None
        )
        if submit_price is not None and submit_price <= 0:
            msg = "Not submitting order as price is 0 or less."
            if wait:
                raise Exception(msg)
            else:
                logger.debug(msg)
                return

        return trading.submit_order(
            wallet=self.wallet,
            wallet_name=trading_wallet,
            data_client=self.trading_data_client_v2,
            market_id=market_id,
            order_type=order_type,
            time_in_force=time_in_force,
            side=side,
            volume=submit_volume,
            price=str(submit_price) if submit_price is not None else None,
            expires_at=int(expires_at) if expires_at is not None else None,
            pegged_order=vega_protos.vega.PeggedOrder(
                reference=pegged_order.reference,
                offset=str(
                    num_to_padded_int(
                        pegged_order.offset, self.market_price_decimals[market_id]
                    )
                ),
            )
            if pegged_order is not None
            else None,
            wait=wait,
            time_forward_fn=lambda: self.wait_fn(2),
            order_ref=order_ref,
            key_name=key_name,
        )

    def get_blockchain_time(self) -> int:
        """Returns blockchain time in seconds since the epoch"""
        return gov.get_blockchain_time(self.trading_data_client_v2)

    def amend_order(
        self,
        trading_wallet: str,
        market_id: str,
        order_id: str,
        price: Optional[float] = None,
        expires_at: Optional[int] = None,
        pegged_offset: Optional[float] = None,
        pegged_reference: Optional[vega_protos.vega.PeggedReference] = None,
        volume_delta: float = 0,
        time_in_force: Optional[Union[vega_protos.vega.Order.TimeInForce, str]] = None,
        key_name: Optional[str] = None,
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
            key_name:
                optional str, name of key in wallet to use
        """
        trading.amend_order(
            wallet=self.wallet,
            wallet_name=trading_wallet,
            market_id=market_id,
            order_id=order_id,
            price=str(
                num_to_padded_int(
                    price,
                    self.market_price_decimals[market_id],
                )
            )
            if price is not None
            else None,
            expires_at=expires_at,
            pegged_offset=str(
                num_to_padded_int(
                    pegged_offset,
                    self.market_price_decimals[market_id],
                )
            )
            if pegged_offset is not None
            else None,
            pegged_reference=pegged_reference,
            volume_delta=num_to_padded_int(
                volume_delta,
                self.market_pos_decimals[market_id],
            ),
            time_in_force=time_in_force,
            key_name=key_name,
        )

    def cancel_order(
        self,
        trading_wallet: str,
        market_id: str,
        order_id: str,
        key_name: Optional[str] = None,
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
            wallet=self.wallet,
            wallet_name=trading_wallet,
            market_id=market_id,
            order_id=order_id,
            key_name=key_name,
        )

    def update_network_parameter(
        self, proposal_wallet: str, parameter: str, new_value: str, key_name: str = None
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
            key_name:
                str, optional, the wallet key proposing the change
        Returns:
            str, the ID of the proposal
        """
        blockchain_time_seconds = gov.get_blockchain_time(self.trading_data_client_v2)

        proposal_id = gov.propose_network_parameter_change(
            parameter=parameter,
            value=new_value,
            wallet=self.wallet,
            wallet_name=proposal_wallet,
            data_client=self.trading_data_client_v2,
            closing_time=blockchain_time_seconds + self.seconds_per_block * 90,
            enactment_time=blockchain_time_seconds + self.seconds_per_block * 100,
            time_forward_fn=lambda: self.wait_fn(2),
            key_name=key_name,
        )
        gov.approve_proposal(
            proposal_id=proposal_id,
            wallet=self.wallet,
            wallet_name=proposal_wallet,
            key_name=key_name,
        )
        self.wait_fn(110)

    def update_market(
        self,
        proposal_wallet: str,
        market_id: str,
        updated_instrument: Optional[UpdateInstrumentConfiguration] = None,
        updated_metadata: Optional[str] = None,
        updated_price_monitoring_parameters: Optional[PriceMonitoringParameters] = None,
        updated_liquidity_monitoring_parameters: Optional[
            LiquidityMonitoringParameters
        ] = None,
        updated_simple_model_params: Optional[SimpleModelParams] = None,
        updated_log_normal_risk_model: Optional[LogNormalRiskModel] = None,
        updated_lp_price_range: Optional[float] = None,
        key_name: Optional[int] = None,
    ):
        """Updates a market based on proposal parameters. Will attempt to propose
        and then immediately vote on the market change before forwarding time for
        the enactment to also take effect

        Args:
            proposal_wallet:
                str, the wallet proposing the change
            market_id:
                str, the market to change
            new_value:
                str, the new value to set
        Returns:
            str, the ID of the proposal
        """
        if (
            updated_simple_model_params is not None
            and updated_log_normal_risk_model is not None
        ):
            raise Exception(
                "Only one of simple and log normal risk models can be valid on a single"
                " market"
            )

        blockchain_time_seconds = gov.get_blockchain_time(self.trading_data_client_v2)

        current_market = self.market_info(market_id=market_id)

        if updated_instrument is None:
            curr_inst = current_market.tradable_instrument.instrument
            curr_fut = curr_inst.future
            oracle_spec_for_settlement_data = data_source_protos.DataSourceDefinition(
                external=data_source_protos.DataSourceDefinitionExternal(
                    oracle=data_source_protos.DataSourceSpecConfiguration(
                        signers=curr_fut.data_source_spec_for_settlement_data.data.external.oracle.signers,
                        filters=curr_fut.data_source_spec_for_settlement_data.data.external.oracle.filters,
                    )
                )
            )

            oracle_spec_for_trading_termination = data_source_protos.DataSourceDefinition(
                external=data_source_protos.DataSourceDefinitionExternal(
                    oracle=data_source_protos.DataSourceSpecConfiguration(
                        signers=curr_fut.data_source_spec_for_trading_termination.data.external.oracle.signers,
                        filters=curr_fut.data_source_spec_for_trading_termination.data.external.oracle.filters,
                    )
                )
            )
            curr_fut_prod = UpdateFutureProduct(
                quote_name=curr_fut.quote_name,
                data_source_spec_for_settlement_data=oracle_spec_for_settlement_data,
                data_source_spec_for_trading_termination=oracle_spec_for_trading_termination,
                data_source_spec_binding=curr_fut.data_source_spec_binding,
            )
            updated_instrument = UpdateInstrumentConfiguration(
                code=curr_inst.code,
                future=curr_fut_prod,
            )
        if updated_simple_model_params is None:
            curr_simple_model = current_market.tradable_instrument.simple_risk_model
            updated_simple_model_params = (
                curr_simple_model.params if curr_simple_model is not None else None
            )

        if updated_log_normal_risk_model is None:
            updated_log_normal_risk_model = (
                current_market.tradable_instrument.log_normal_risk_model
            )

        update_configuration = UpdateMarketConfiguration(
            instrument=updated_instrument,
            price_monitoring_parameters=updated_price_monitoring_parameters
            if updated_price_monitoring_parameters is not None
            else current_market.price_monitoring_settings.parameters,
            liquidity_monitoring_parameters=updated_liquidity_monitoring_parameters
            if updated_liquidity_monitoring_parameters is not None
            else current_market.liquidity_monitoring_parameters,
            simple=updated_simple_model_params,
            log_normal=updated_log_normal_risk_model,
            metadata=updated_metadata,
            lp_price_range=str(updated_lp_price_range)
            if updated_lp_price_range is not None
            else current_market.lp_price_range,
        )

        proposal_id = gov.propose_market_update(
            market_update=update_configuration,
            market_id=market_id,
            wallet=self.wallet,
            wallet_name=proposal_wallet,
            data_client=self.trading_data_client_v2,
            closing_time=blockchain_time_seconds + self.seconds_per_block * 90,
            enactment_time=blockchain_time_seconds + self.seconds_per_block * 100,
            time_forward_fn=lambda: self.wait_fn(2),
        )
        gov.approve_proposal(
            proposal_id=proposal_id,
            wallet=self.wallet,
            wallet_name=proposal_wallet,
        )
        self.wait_fn(110)

    def settle_market(
        self,
        settlement_wallet: str,
        settlement_price: float,
        market_id: str,
        key_name: Optional[str] = None,
    ):
        future_inst = data_raw.market_info(
            market_id, data_client=self.trading_data_client_v2
        ).tradable_instrument.instrument.future

        filter_key = future_inst.data_source_spec_for_settlement_data.data.external.oracle.filters[
            0
        ].key
        oracle_name = filter_key.name

        logger.info(f"Settling market at price {settlement_price} for {oracle_name}")

        gov.settle_oracle(
            wallet=self.wallet,
            wallet_name=settlement_wallet,
            oracle_name=oracle_name,
            settlement_price=num_to_padded_int(
                settlement_price, decimals=filter_key.number_decimal_places
            ),
            key_name=key_name,
        )

    def party_account(
        self,
        wallet_name: str,
        asset_id: str,
        market_id: str,
        key_name: Optional[str] = None,
    ) -> data.PartyMarketAccount:
        """Output money in general accounts/margin accounts/bond accounts (if exists)
        of a party."""
        return data.party_account(
            self.wallet.public_key(wallet_name, key_name),
            asset_id=asset_id,
            market_id=market_id,
            data_client=self.trading_data_client_v2,
        )

    def list_accounts(
        self,
        wallet_name: Optional[str] = None,
        asset_id: Optional[str] = None,
        market_id: Optional[str] = None,
        key_name: Optional[str] = None,
    ) -> List[data.AccountData]:
        """Return all accounts across markets matching the supplied filter options

        Args:
            wallet_name:
                Optional, default None, Filter down to a specific key from this wallet
            asset_id:
                Optional, default None, Filter down to only accounts on this asset
            market_id:
                Optional, default None, Filter down to only accounts from this market
            key_name:
                Optional, default None, Select non-default key from the selected wallet

        Returns:
            List[AccountData], cleaned account data for each account

        """
        return data.list_accounts(
            data_client=self.trading_data_client_v2,
            pub_key=self.wallet.public_key(wallet_name, key_name)
            if wallet_name is not None
            else None,
            asset_id=asset_id,
            market_id=market_id,
            asset_decimals_map=self.asset_decimals,
        )

    def positions_by_market(
        self,
        wallet_name: str,
        market_id: Optional[str] = None,
        key_name: Optional[str] = None,
    ) -> List[vega_protos.vega.Position]:
        """Output positions of a party."""
        return data.positions_by_market(
            pub_key=self.wallet.public_key(wallet_name, key_name),
            market_id=market_id,
            data_client=self.trading_data_client_v2,
            market_price_decimals_map=self.market_price_decimals,
            market_position_decimals_map=self.market_pos_decimals,
            market_to_asset_map=self.market_to_asset,
            asset_decimals_map=self.asset_decimals,
        )

    @raw_data
    def all_markets(
        self,
    ) -> List[vega_protos.markets.Market]:
        """
        Output market info.
        """
        return data_raw.all_markets(data_client=self.trading_data_client_v2)

    @raw_data
    def market_info(
        self,
        market_id: str,
    ) -> vega_protos.markets.Market:
        """
        Output market info.
        """
        return data_raw.market_info(
            market_id=market_id, data_client=self.trading_data_client_v2
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
            market_id=market_id, data_client=self.trading_data_client_v2
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
            asset_id=asset_id, data_client=self.trading_data_client_v2
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
            data_client=self.trading_data_client_v2,
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
            data_client=self.trading_data_client_v2,
        )

    def best_prices(
        self,
        market_id: str,
    ) -> Tuple[int, int]:
        """
        Output the best static bid price and best static ask price in current market.
        """
        return data.best_prices(
            market_id=market_id, data_client=self.trading_data_client_v2
        )

    def price_bounds(
        self,
        market_id: str,
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Output the tightest price bounds in the current market.
        """
        return data.price_bounds(
            market_id=market_id, data_client=self.trading_data_client_v2
        )

    def order_book_by_market(
        self,
        market_id: str,
    ) -> data.OrderBook:
        return data.order_book_by_market(
            market_id=market_id, data_client=self.trading_data_client_v2
        )

    def market_depth(self, market_id: str, num_levels: int = 5) -> data.MarketDepth:
        return data.market_depth(
            market_id=market_id,
            data_client=self.trading_data_client_v2,
            max_depth=num_levels,
            price_decimals=self.market_price_decimals[market_id],
            position_decimals=self.market_pos_decimals[market_id],
        )

    def open_orders_by_market(
        self,
        market_id: str,
    ) -> data.OrderBook:
        return data.open_orders_by_market(
            market_id=market_id,
            data_client=self.trading_data_client_v2,
            price_decimals=self.market_price_decimals[market_id],
            position_decimals=self.market_pos_decimals[market_id],
        )

    def submit_simple_liquidity(
        self,
        wallet_name: str,
        market_id: str,
        commitment_amount: float,
        fee: float,
        reference_buy: str,
        reference_sell: str,
        delta_buy: float,
        delta_sell: float,
        is_amendment: Optional[bool] = None,
        key_name: Optional[str] = None,
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
                float, the offset from reference point for the buy side of LP
            delta_sell:
                float, the offset from reference point for the sell side of LP
        """
        asset_id = data_raw.market_info(
            market_id=market_id, data_client=self.trading_data_client_v2
        ).tradable_instrument.instrument.future.settlement_asset

        market_decimals = data.market_price_decimals(
            market_id=market_id, data_client=self.trading_data_client_v2
        )
        is_amendment = (
            is_amendment
            if is_amendment is not None
            else self.has_liquidity_provision(
                market_id=market_id,
                wallet_name=wallet_name,
                key_name=key_name,
            )
        )
        return trading.submit_simple_liquidity(
            market_id=market_id,
            commitment_amount=num_to_padded_int(
                commitment_amount, self.asset_decimals[asset_id]
            ),
            fee=fee,
            reference_buy=reference_buy,
            reference_sell=reference_sell,
            delta_buy=num_to_padded_int(delta_buy, market_decimals),
            delta_sell=num_to_padded_int(delta_sell, market_decimals),
            wallet=self.wallet,
            wallet_name=wallet_name,
            is_amendment=is_amendment,
            key_name=key_name,
        )

    def has_liquidity_provision(
        self,
        wallet_name: str,
        market_id: str,
        key_name: Optional[str] = None,
    ):
        return data.has_liquidity_provision(
            self.trading_data_client_v2,
            market_id,
            party_id=self.wallet.public_key(wallet_name, key_name),
        )

    def submit_liquidity(
        self,
        wallet_name: str,
        market_id: str,
        commitment_amount: float,
        fee: float,
        buy_specs: List[Tuple[str, float, int]],
        sell_specs: List[Tuple[str, float, int]],
        is_amendment: Optional[bool] = None,
        key_name: Optional[str] = None,
    ):
        """Submit/Amend a custom liquidity profile.

        Args:
            wallet_name:
                str, the wallet name performing the action
            wallet:
                Wallet, wallet client
            market_id:
                str, The ID of the market to place the commitment on
            commitment_amount:
                int, The amount in asset decimals of market asset to commit
                to liquidity provision
            fee:
                float, The fee level at which to set the LP fee
                 (in %, e.g. 0.01 == 1% and 1 == 100%)
            buy_specs:
                List[Tuple[str, int, int]], List of tuples, each containing a reference
                point in their first position, a desired offset in their second and
                a proportion in third
            sell_specs:
                List[Tuple[str, int, int]], List of tuples, each containing a reference
                point in their first position, a desired offset in their second and
                a proportion in third
            key_name:
                optional, str name of key in wallet to use
        """
        asset_id = data_raw.market_info(
            market_id=market_id, data_client=self.trading_data_client_v2
        ).tradable_instrument.instrument.future.settlement_asset

        market_decimals = data.market_price_decimals(
            market_id=market_id, data_client=self.trading_data_client_v2
        )

        buy_specs = [
            (s[0], num_to_padded_int(s[1], market_decimals), s[2]) for s in buy_specs
        ]
        sell_specs = [
            (s[0], num_to_padded_int(s[1], market_decimals), s[2]) for s in sell_specs
        ]
        is_amendment = (
            is_amendment
            if is_amendment is not None
            else self.has_liquidity_provision(
                market_id=market_id,
                wallet_name=wallet_name,
                key_name=key_name,
            )
        )

        return trading.submit_liquidity(
            market_id=market_id,
            commitment_amount=num_to_padded_int(
                commitment_amount, self.asset_decimals[asset_id]
            ),
            fee=fee,
            buy_specs=buy_specs,
            sell_specs=sell_specs,
            wallet=self.wallet,
            wallet_name=wallet_name,
            is_amendment=is_amendment,
            key_name=key_name,
        )

    def find_market_id(self, name: str, raise_on_missing: bool = False) -> str:
        """Looks up the Market ID of a given market name

        Args:
            name:
                str, the name of the market to look for
            raise_on_missing:
                bool, whether to raise an Error or silently return if the market does
                not exist

        Returns:
            str, the ID of the market
        """
        return data.find_market_id(
            name=name,
            raise_on_missing=raise_on_missing,
            data_client=self.trading_data_client_v2,
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
            data_client=self.trading_data_client_v2,
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
            order_id=order_id, data_client=self.trading_data_client_v2, version=version
        )

    def order_status_from_feed(
        self, live_only: bool = True
    ) -> Dict[str, Dict[str, Dict[str, data.Order]]]:
        """Returns a copy of current order status based on Order feed if started.
        If order feed has not been started, dict will be empty

        Args:
            live_only:
                bool, default True, whether to filter out dead/cancelled deals
                    from result

        Returns:
            Dictionary mapping market ID -> Party ID -> Order ID -> Order detaails"""
        with self.orders_lock:
            order_dict = {}
            for market_id, party_orders in self._order_state_from_feed.items():
                for party_id, orders in party_orders.items():
                    for order_id, order in orders.items():
                        if not live_only or (
                            order.status == vega_protos.vega.Order.Status.STATUS_ACTIVE
                        ):
                            order_dict.setdefault(market_id, {}).setdefault(
                                party_id, {}
                            )[order_id] = order
        return order_dict

    def orders_for_party_from_feed(
        self,
        wallet_name: str,
        market_id: str,
        live_only: bool = True,
        key_name: Optional[str] = None,
    ) -> Dict[str, data.Order]:
        party_id = self.wallet.public_key(wallet_name, key_name)
        return (
            self.order_status_from_feed(live_only=live_only)
            .get(market_id, {})
            .get(party_id, {})
        )

    def transfer_status_from_feed(self, live_only: bool = True):
        datetime = self.get_blockchain_time()

        with self.transfers_lock:
            transfers_dict = {}
            for party_id, party_transfers in self._transfer_state_from_feed.items():
                for transfer_id, transfer in party_transfers.items():
                    deliver_on = int(transfer.one_off.deliver_on)
                    if not live_only or (deliver_on != 0 and datetime < deliver_on):
                        transfers_dict.setdefault(party_id, {})[transfer_id] = transfer
        return transfers_dict

    @raw_data
    def liquidity_provisions(
        self,
        market_id: Optional[str] = None,
        party_id: Optional[str] = None,
    ) -> Optional[List[vega_protos.vega.LiquidityProvision]]:
        """Loads the current liquidity provision(s) for a given market and/or party.

        Args:
            market_id:
                Optional[str], the ID of the market from which to
                    pull liquidity provisions
            party_id:
                Optional[str], the ID of the party from which to
                    pull liquidity provisions

        Returns:
            List[LiquidityProvision], list of liquidity provisions (if any exist)
        """
        return data_raw.liquidity_provisions(
            self.trading_data_client_v2, market_id=market_id, party_id=party_id
        )

    def party_liquidity_provisions(
        self,
        wallet_name: str,
        market_id: Optional[str] = None,
        key_name: Optional[str] = None,
    ) -> Optional[List[vega_protos.vega.LiquidityProvision]]:
        """Loads the current liquidity provision(s) for a given market and/or party.

        Args:
            market_id:
                Optional[str], the ID of the market from which to
                    pull liquidity provisions
            party_id:
                Optional[str], the ID of the party from which to
                    pull liquidity provisions
            key_name:
                Optional[str], key name stored in metadata. Defaults to None.

        Returns:
            List[LiquidityProvision], list of liquidity provisions (if any exist)
        """
        return self.liquidity_provisions(
            market_id=market_id, party_id=self.wallet.public_key(wallet_name, key_name)
        )

    def start_live_feeds(self):
        self.start_order_monitoring()
        self.start_transfer_monitoring()
        self.start_trade_monitoring()

        self._merge_streams()
        self._observation_thread = threading.Thread(target=self._monitor_stream)
        self._observation_thread.start()

    def start_order_monitoring(
        self,
        market_ids: Optional[List[str]] = None,
        party_ids: Optional[List[str]] = None,
        use_core_client: bool = False,
    ):
        if use_core_client:
            data_client = self.core_client
        else:
            data_client = self.trading_data_client_v2

        order_queue = data.order_subscription(
            data_client,
            self.trading_data_client_v2,
        )

        base_orders = []
        for market_party_tuple in list(
            product(
                (market_ids if market_ids is not None else [None]),
                (party_ids if party_ids is not None else [None]),
            )
        ):
            base_orders.extend(
                data.list_orders(
                    data_client=self.trading_data_client_v2,
                    market_id=market_party_tuple[0],
                    party_id=market_party_tuple[1],
                    live_only=True,
                )
            )

        with self.orders_lock:
            for order in base_orders:
                self._order_state_from_feed.setdefault(order.market_id, {}).setdefault(
                    order.party_id, {}
                )[order.id] = order

        self._observation_feeds.append(order_queue)

    def start_transfer_monitoring(
        self,
    ):
        transfer_queue = data.transfer_subscription(
            self.core_client,
            self.trading_data_client_v2,
        )

        base_transfers = []

        base_transfers.extend(
            data.list_transfers(data_client=self.trading_data_client_v2)
        )

        with self.transfers_lock:
            for t in base_transfers:
                self._transfer_state_from_feed.setdefault(t.party_to, {})[t.id] = t
        self._observation_feeds.append(transfer_queue)

    def start_trade_monitoring(
        self,
    ):
        trade_queue = data.trades_subscription(
            self.core_client,
            self.trading_data_client_v2,
        )

        base_trades = []

        with self.trades_lock:
            self._trades_from_feed = base_trades
        self._observation_feeds.append(trade_queue)

    def _merge_streams(self) -> None:
        self._merge_threads = []
        for feed in self._observation_feeds:
            merger = threading.Thread(
                target=_queue_forwarder,
                args=(feed, self._aggregated_observation_feed),
                daemon=True,
            )
            self._merge_threads.append(merger)
            merger.start()

    def _monitor_stream(self) -> None:
        while True:
            if self._kill_thread_sig.is_set():
                return
            try:
                update = self._aggregated_observation_feed.get(timeout=1)
            except Empty:
                continue
            else:
                if isinstance(update, data.Order):
                    with self.orders_lock:
                        if update.version >= getattr(
                            self._order_state_from_feed.setdefault(update.market_id, {})
                            .setdefault(update.party_id, {})
                            .get(update.id, None),
                            "version",
                            0,
                        ):
                            self._order_state_from_feed[update.market_id][
                                update.party_id
                            ][update.id] = update

                if isinstance(update, data.Transfer):
                    with self.transfers_lock:
                        self._transfer_state_from_feed.setdefault(update.party_to, {})[
                            update.id
                        ] = update

                elif isinstance(update, data.Trade):
                    with self.trades_lock:
                        self._trades_from_feed.append(update)

    def margin_levels(
        self,
        wallet_name: str,
        market_id: Optional[str] = None,
        key_name: Optional[str] = None,
    ) -> List[data.MarginLevels]:
        return data.margin_levels(
            self.trading_data_client_v2,
            party_id=self.wallet.public_key(wallet_name, key_name),
            market_id=market_id,
        )

    def list_orders(
        self,
        wallet_name: str,
        key_name: str,
        market_id: str,
        reference: Optional[str] = None,
        live_only: Optional[bool] = True,
    ) -> List[data.Order]:
        """Return a list of orders for the specified market and party.

        Args:
            wallet_name (str):
                Name of wallet to return orders for.
            key_name (str):
                Name of key to return orders for.
            market_id (str):
                Id of market to return orders from.
            reference (Optional[str]):
                Reference of matching orders to return.
            live_only (Optional[bool]):
                Whether to return only live orders. Defaults to True.

        Returns:
            List[data.Order]:
                List of orders for the specified market and party.
        """
        return data.list_orders(
            data_client=self.trading_data_client_v2,
            market_id=market_id,
            party_id=self.wallet.public_key(name=wallet_name, key_name=key_name),
            reference=reference,
            live_only=live_only,
        )

    def get_trades_from_stream(
        self,
        market_id: Optional[str] = None,
        wallet_name: Optional[str] = None,
        key_name: Optional[str] = None,
        order_id: Optional[str] = None,
    ) -> List[data.Trade]:
        """Loads executed trades for a given query of party/market/specific order from
        data node. Converts values to proper decimal output.

        Args:
            market_id:
                optional str, Restrict to trades on a specific market
            wallet_name:
                optional str, Restrict to trades for a specific wallet
            key_name:
                optional str, Select a different key to the default within a given wallet
            order_id:
                optional str, Restrict to trades for a specific order

        Returns:
            List[Trade], list of formatted trade objects which match the required
                restrictions.
        """
        party_id = (
            self.wallet.public_key(wallet_name, key_name)
            if key_name is not None
            else None
        )
        with self.trades_lock:
            results = []
            for trade in self._trades_from_feed:
                if party_id is not None and party_id not in (trade.buyer, trade.seller):
                    continue
                if market_id is not None and trade.market_id != market_id:
                    continue
                if order_id is not None and order_id not in (
                    trade.buy_order,
                    trade.sell_order,
                ):
                    continue
                results.append(copy.copy(trade))
        return results

    def get_trades(
        self,
        market_id: str,
        wallet_name: Optional[str] = None,
        key_name: Optional[str] = None,
        order_id: Optional[str] = None,
    ) -> List[data.Trade]:
        """Loads executed trades for a given query of party/market/specific order from
        data node. Converts values to proper decimal output.

        Args:
            market_id:
                str, Restrict to trades on a specific market
            wallet_name:
                optional str, Restrict to trades for a specific wallet
            key_name:
                optional str, Select a different key to the default within a given wallet
            order_id:
                optional str, Restrict to trades for a specific order

        Returns:
            List[Trade], list of formatted trade objects which match the required
                restrictions.
        """
        if market_id is not None:
            self.market_pos_decimals[market_id]
            self.market_price_decimals[market_id]
            asset_dp = self.asset_decimals[self.market_to_asset[market_id]]
        return data.get_trades(
            self.trading_data_client_v2,
            party_id=self.wallet.public_key(wallet_name, key_name)
            if key_name is not None
            else None,
            market_id=market_id,
            order_id=order_id,
            market_asset_decimals_map={market_id: asset_dp}
            if market_id is not None
            else None,
            market_position_decimals_map=self.market_pos_decimals,
            market_price_decimals_map=self.market_price_decimals,
        )

    def create_order_amendment(
        self,
        order_id: str,
        market_id: str,
        price: Optional[float] = None,
        size_delta: Optional[float] = None,
        expires_at: Optional[int] = None,
        time_in_force: Optional[Union[vega_protos.vega.Order.TimeInForce, str]] = None,
        pegged_offset: Optional[float] = None,
        pegged_reference: Optional[Union[vega_protos.vega.PeggedReference, str]] = None,
    ) -> OrderAmendment:
        """Creates a Vega OrderAmendment object.

        Method can be used to create a Vega OrderCancellation object of which multiples
        can be passed in a list to submit batch market instructions.

        Args:
            order_id (str):
                Id of order to amend.
            market_id (str):
                Id of market containing order to amend.
            price (Optional[float], optional):
                New price of order. Defaults to None (no change).
            size_delta (Optional[float]):
                Amount to amend order size by. Defaults to None (no change).
            expires_at (Optional[int]):
                New expiry timestamp for order. Defaults to None (no change).
            time_in_force (Optional[Union[vega_protos.vega.Order.TimeInForce, str]]):
                New time_in_force for order. Defaults to None (no change).
            pegged_offset (Optional[float]):
                New value to offset price by for order. Defaults to None (no change).
            pegged_reference (Optional[Union[vega_protos.vega.PeggedReference, str]]):
                New reference for offset for order. Defaults to None (no change).

        Returns:
            OrderAmendment:
                The created Vega OrderAmendment object
        """

        price = (
            price
            if price is None
            else num_to_padded_int(
                to_convert=price, decimals=self.market_price_decimals[market_id]
            )
        )

        pegged_offset = (
            pegged_offset
            if pegged_offset is None
            else num_to_padded_int(
                to_convert=pegged_offset,
                decimals=self.market_price_decimals[market_id],
            )
        )

        size_delta = (
            size_delta
            if size_delta is None
            else num_to_padded_int(
                to_convert=size_delta, decimals=self.market_pos_decimals[market_id]
            )
        )

        if price is not None and price <= 0:
            msg = "Not submitting order as price is 0 or less."
            logger.debug(msg)
            return

        return trading.order_amendment(
            order_id=order_id,
            market_id=market_id,
            price=str(price) if price is not None else price,
            size_delta=size_delta,
            expires_at=expires_at,
            time_in_force=time_in_force,
            pegged_offset=str(pegged_offset)
            if pegged_offset is not None
            else pegged_offset,
            pegged_reference=pegged_reference,
        )

    def create_order_cancellation(
        self,
        order_id: str,
        market_id: str,
    ) -> OrderCancellation:
        """Returns a Vega OrderCancellation object

        Method can be used to create a Vega OrderCancellation object of which multiples
        can be passed in a list to submit batch market instructions.

        Args:
            order_id (str):
                Id of order to cancel.
            market_id (str):
                Id of market containing order to cancel.

        Returns:
            OrderCancellation:
                The created OrderCancellation object
        """
        return trading.order_cancellation(
            order_id=order_id,
            market_id=market_id,
        )

    def create_order_submission(
        self,
        market_id: str,
        size: float,
        side: Union[vega_protos.vega.Side, str],
        order_type: Optional[Union[vega_protos.vega.Order.Type, str]],
        time_in_force: Optional[Union[vega_protos.vega.Order.TimeInForce, str]],
        price: Optional[float] = None,
        expires_at: Optional[int] = None,
        reference: Optional[str] = None,
        pegged_reference: Optional[str] = None,
        pegged_offset: Optional[float] = None,
    ) -> OrderSubmission:
        """Returns a Vega OrderSubmission object

        Method can be used to create a Vega OrderSubmission object of which multiples
        can be combined in a list to submit batch market instructions.

        Args:
            market_id (str):
                Id of market to place order in.
            size (float):
                Size of order.
            side (Union[vega_protos.vega.Side, str]):
                Side of order, "SIDE_BUY" or "SIDE_SELL".
            order_type (Optional[Union[vega_protos.vega.Order.Type, str]]):
                Type of order, "TYPE_MARKET" or "TYPE_LIMIT".
            time_in_force (Optional[Union[vega_protos.vega.Order.TimeInForce, str]]):
                Time in force of order, determines how long order remains active.
            price (Optional[float]):
                Price of order, not required for "TYPE_LIMIT" orders. Defaults to None.
            expires_at (Optional[int]):
                Determines timestamp at which order expires, only required for orders of
                "TYPE_LIMIT" and "TIME_IN_FORCE_GTT". Defaults to None.
            reference (Optional[str]):
                Reference to assign to order. Defaults to None.
            pegged_reference (Optional[str]):
                Reference for price offset for order. Defaults to None.
            pegged_offset (Optional[float]):
                Value for price offset from reference for order. Defaults to None.

        Returns:
            OrderSubmission:
                The created Vega OrderSubmission object
        """

        price = (
            price
            if price is None
            else (
                num_to_padded_int(
                    to_convert=price, decimals=self.market_price_decimals[market_id]
                )
            )
        )
        pegged_offset = (
            pegged_offset
            if pegged_offset is None
            else (
                num_to_padded_int(
                    to_convert=pegged_offset,
                    decimals=self.market_price_decimals[market_id],
                )
            )
        )
        size = (
            size
            if size is None
            else num_to_padded_int(
                to_convert=size, decimals=self.market_pos_decimals[market_id]
            )
        )
        if (pegged_offset is not None) and (pegged_reference is not None):
            pegged_order = trading.build_pegged_order(
                pegged_offset=pegged_offset,
                pegged_reference=pegged_reference,
            )
        else:
            pegged_order = None

        if price is not None and price <= 0:
            msg = "Not submitting order as price is 0 or less."
            logger.debug(msg)
            return
        if size is not None and size <= 0:
            msg = "Not submitting order as size is 0 or less."
            logger.debug(msg)
            return

        return trading.order_submission(
            data_client=self.trading_data_client_v2,
            market_id=market_id,
            price=str(price) if price is not None else None,
            size=size,
            side=side,
            time_in_force=time_in_force,
            expires_at=expires_at,
            order_type=order_type,
            reference=reference,
            pegged_order=pegged_order,
        )

    def submit_instructions(
        self,
        wallet_name: str,
        key_name: Optional[str] = None,
        cancellations: Optional[List[OrderCancellation]] = None,
        amendments: Optional[List[OrderAmendment]] = None,
        submissions: Optional[List[OrderSubmission]] = None,
    ):
        """Submits a batch of market instructions to be processed sequentially.

        Method allows lists of order cancellations, order amendments, and order
        submissions to be submitted as a batch and processed sequentially in the
        order cancellations, amendments, then submissions.

        If the number of cancellation, amendment, and submission instructions exceed
        the network parameter spam.protection.max.batchSize, the function will submit
        the instructions in multiple batches adhering to the above rules.

        Args:
            wallet_name (str):
                Name of wallet to submit transaction from.
            key_name (Optional[str], optional):
                Name of key to submit transaction from. Defaults to None.
            cancellations (Optional[ List[OrderCancellation] ]):
                List of OrderCancellation objects to submit. Defaults to None.
            amendments (Optional[ List[OrderAmendment] ]):
                List of OrderAmendment objects to submit. Defaults to None.
            submissions (Optional[ List[OrderSubmission] ]):
                List of OrderSubmission objects to submit. Defaults to None.
        """

        max_batch_size = self.get_network_parameter(
            key="spam.protection.max.batchSize", to_type="int"
        )

        instructions = cancellations + amendments + submissions

        batch_size = 0

        batch_of_cancellations = []
        batch_of_amendments = []
        batch_of_submissions = []

        for i, instruction in enumerate(instructions):
            if instruction is None:
                continue
            elif isinstance(instruction, OrderCancellation):
                batch_of_cancellations.append(instruction)
            elif isinstance(instruction, OrderAmendment):
                batch_of_amendments.append(instruction)
            elif isinstance(instruction, OrderSubmission):
                batch_of_submissions.append(instruction)
            else:
                batch_size += -1
                raise ValueError(f"Invalid instruction type {type(instruction)}.")

            batch_size += 1

            if (batch_size >= max_batch_size) or (i == len(instructions) - 1):
                trading.batch_market_instructions(
                    wallet=self.wallet,
                    wallet_name=wallet_name,
                    key_name=key_name,
                    cancellations=batch_of_cancellations,
                    amendments=batch_of_amendments,
                    submissions=batch_of_submissions,
                )

                batch_size = 0

                batch_of_cancellations = []
                batch_of_amendments = []
                batch_of_submissions = []

    def get_network_parameter(
        self, key: str, to_type: Optional[Union[str, int, float]] = None
    ) -> Union[str, int, float]:
        """Returns the value of the specified network parameter.

        Args:
            key (str):
                The key identifying the network parameter.
            to_type (str, float, int, optional):
                Type to convert raw value to. Defaults to type of raw value.

        Returns:
            Any:
                The value of the specified network parameter in the specified type.

        Raises:
            ValueError:
                If an invalid to_type arg is specified (i.e. not str, int, or float).
        """

        raw_val = data_raw.get_network_parameter(
            data_client=self.trading_data_client_v2,
            key=key,
        ).value

        if to_type is None:
            return raw_val
        elif to_type == "str":
            return str(raw_val)
        elif to_type == "int":
            return int(raw_val)
        elif to_type == "float":
            return float(raw_val)
        else:
            raise ValueError(f"Invalid value '{to_type}' specified for 'to_type' arg.")

    def ping_datanode(self, max_time_diff: int = 30):
        """Ping datanode endpoint to check health of connection

        Args:
            max_time_diff (int, optional):
                The maximum allowable deviation between the time reported by datanode
                and the time reported by the system in seconds. Defaults to 30

        """

        # Ping datanode then check if it is behind
        data.ping(data_client=self.trading_data_client_v2)
        if abs(self.get_blockchain_time() - time.time()) > max_time_diff:
            raise DatanodeBehindError

    def one_off_transfer(
        self,
        from_wallet_name: str,
        to_wallet_name: str,
        from_account_type: vega_protos.vega.AccountType,
        to_account_type: vega_protos.vega.AccountType,
        asset: str,
        amount: float,
        reference: Optional[str] = None,
        from_key_name: Optional[str] = None,
        to_key_name: Optional[str] = None,
        delay: Optional[int] = None,
    ):
        """Submit a one off transfer command.

        Args:
            from_wallet_name (str):
                Name of wallet to transfer from.
            to_wallet_name (str):
                Name of wallet to transfer to.
            from_account_type (vega_protos.vega.AccountType):
                Type of Vega account to transfer from.
            to_account_type (vega_protos.vega.AccountType):
                Type of Vega account to transfer to.
            asset (str):
                Id of asset to transfer.
            amount (float):
                Amount of asset to transfer.
            reference (Optional[str], optional):
                Reference to assign to transfer. Defaults to None.
            from_key_name (Optional[str], optional):
                Name of key in wallet to send from. Defaults to None.
            to_key_name (Optional[str], optional):
                Name of key in wallet to send to. Defaults to None.
            delay (Optional[int], optional):
                Delay in seconds to add before transfer is sent. Defaults to None.
        """

        adp = self.asset_decimals[asset]

        one_off = vega_protos.commands.v1.commands.OneOffTransfer()
        if delay is not None:
            setattr(one_off, "deliver_on", self.get_blockchain_time() + delay)

        trading.transfer(
            wallet=self.wallet,
            wallet_name=from_wallet_name,
            key_name=from_key_name,
            from_account_type=from_account_type,
            to=self.wallet.public_key(name=to_wallet_name, key_name=to_key_name),
            to_account_type=to_account_type,
            asset=asset,
            amount=str(num_to_padded_int(amount, adp)),
            reference=reference,
            one_off=one_off,
        )

    def list_transfers(
        self,
        wallet_name: Optional[str] = None,
        key_name: Optional[str] = None,
        direction: Optional[data_node_protos_v2.trading_data.TransferDirection] = None,
    ) -> List[data.Transfer]:
        """Returns a list of processed transfers.

        Args:
            wallet_name (Optional[str], optional):
                Name of wallet to return transfers for. Defaults to None.
            key_name (Optional[str], optional):
                Name of key to return transfers for. Defaults to None.
            direction (Optional[data_node_protos_v2.trading_data.TransferDirection], optional):
                Direction of transfers to return. Defaults to None.

        Returns:
            List[Transfer]:
                A list of processed Transfer objects for the specified party and direction.
        """

        party_id = (
            self.wallet.public_key(name=wallet_name, key_name=key_name)
            if wallet_name is not None
            else None
        )

        return data.list_transfers(
            data_client=self.trading_data_client_v2,
            party_id=party_id,
            direction=direction,
        )

    def get_liquidity_fee_shares(
        self,
        market_id: str,
        wallet_name: Optional[str] = None,
        key_name: Optional[str] = None,
    ) -> Union[Dict, float]:
        """Gets the current liquidity fee share for each party or a specified party.

        Args:
            market_id (str):
                Id of market.
            wallet_name (Optional[str] = None):
                Name of wallet to get public key from.
            key_name (Optional[str], optional):
                Name of specific key in wallet to get public key for. Defaults to None.
        """

        return data.get_liquidity_fee_shares(
            data_client=self.trading_data_client_v2,
            market_id=market_id,
            party_id=(
                self.wallet.public_key(name=wallet_name, key_name=key_name)
                if wallet_name is not None
                else None
            ),
        )

    def list_ledger_entries(
        self,
        close_on_account_filters: bool = False,
        asset_id: Optional[str] = None,
        from_party_ids: Optional[List[str]] = None,
        to_party_ids: Optional[List[str]] = None,
        from_account_types: Optional[list[vega_protos.vega.AccountType]] = None,
        from_market_ids: Optional[List[str]] = None,
        to_market_ids: Optional[List[str]] = None,
        to_account_types: Optional[list[vega_protos.vega.AccountType]] = None,
        transfer_types: Optional[list[vega_protos.vega.TransferType]] = None,
        from_datetime: Optional[datetime.datetime] = None,
        to_datetime: Optional[datetime.datetime] = None,
    ) -> List[data.AggregatedLedgerEntry]:
        """Returns a list of ledger entries matching specific filters as provided.
        These detail every transfer of funds between accounts within the Vega system,
        including fee/rewards payments and transfers between user margin/general/bond
        accounts.

        Note: At least one of the from_*/to_* filters, or asset ID, must be specified.

        Args:
            data_client:
                vac.VegaTradingDataClientV2, An instantiated gRPC trading data client
            close_on_account_filters:
                bool, default False, Whether both 'from' and 'to' filters must both match
                    a given transfer for inclusion. If False, entries matching either
                    'from' or 'to' will also be included.
            asset_id:
                Optional[str], filter to only transfers of specific asset ID
            from_party_ids:
                Optional[List[str]], Only include transfers from specified parties
            from_market_ids:
                Optional[List[str]], Only include transfers from specified markets
            from_account_types:
                Optional[List[str]], Only include transfers from specified account types
            to_party_ids:
                Optional[List[str]], Only include transfers to specified parties
            to_market_ids:
                Optional[List[str]], Only include transfers to specified markets
            to_account_types:
                Optional[List[str]], Only include transfers to specified account types
            transfer_types:
                Optional[List[vega_protos.vega.AccountType]], Only include transfers
                    of specified types
            from_datetime:
                Optional[datetime.datetime], Only include transfers occurring after
                    this time
            to_datetime:
                Optional[datetime.datetime], Only include transfers occurring before
                    this time
        Returns:
            List[data.AggregatedLedgerEntry]
                A list of all transfers matching the requested criteria
        """

        return data.list_ledger_entries(
            data_client=self.trading_data_client_v2,
            asset_id=asset_id,
            close_on_account_filters=close_on_account_filters,
            from_party_ids=from_party_ids,
            from_market_ids=from_market_ids,
            from_account_types=from_account_types,
            to_party_ids=to_party_ids,
            to_market_ids=to_market_ids,
            to_account_types=to_account_types,
            transfer_types=transfer_types,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            asset_decimals_map=self.asset_decimals,
        )
