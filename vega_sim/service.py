from __future__ import annotations

import copy
import datetime
import logging
import time
from abc import ABC
from collections import defaultdict
from dataclasses import dataclass
from functools import wraps
from itertools import product
from queue import Empty, Queue
from typing import Any, Callable, Dict, Generator, List, Optional, Set, Tuple, Union
from enum import Enum

import grpc

import vega_sim.api.data as data
import vega_sim.api.data_raw as data_raw
import vega_sim.api.faucet as faucet
import vega_sim.api.governance as gov
import vega_sim.api.market as market
import vega_sim.api.trading as trading
import vega_sim.api.helpers as helpers
import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v2 as data_node_protos_v2
import vega_sim.proto.vega as vega_protos
import vega_sim.proto.vega.data_source_pb2 as data_source_protos
from vega_sim.api.helpers import (
    get_enum,
    forward,
    statistics,
    num_to_padded_int,
    wait_for_core_catchup,
    wait_for_datanode_sync,
)
from vega_sim.local_data_cache import LocalDataCache
from vega_sim.proto.vega.commands.v1.commands_pb2 import (
    OrderAmendment,
    OrderCancellation,
    OrderSubmission,
    StopOrdersCancellation,
    StopOrdersSubmission,
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
    LiquiditySLAParameters,
    SimpleModelParams,
    LiquidationStrategy,
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


class DatanodeSlowResponseError(Exception):
    pass


class VegaFaucetError(Exception):
    pass


class MarketStateUpdateType(Enum):
    Unspecified = (
        vega_protos.governance.MarketStateUpdateType.MARKET_STATE_UPDATE_TYPE_UNSPECIFIED
    )
    Terminate = (
        vega_protos.governance.MarketStateUpdateType.MARKET_STATE_UPDATE_TYPE_TERMINATE
    )
    Suspend = (
        vega_protos.governance.MarketStateUpdateType.MARKET_STATE_UPDATE_TYPE_SUSPEND
    )
    Resume = (
        vega_protos.governance.MarketStateUpdateType.MARKET_STATE_UPDATE_TYPE_RESUME
    )


def raw_data(fn):
    @wraps(fn)
    def wrapped_fn(self, *args, **kwargs):
        if self.warn_on_raw_data_access:
            logger.warning(
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
        listen_for_high_volume_stream_updates: bool = False,
        governance_symbol: Optional[str] = "VOTE",
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
                int, default 1, How long each block represents in seconds. For a
                    nullchain service this can be known exactly, for anything
                    else it will be an estimate. Used for waiting/forwarding time
                    and determining how far forwards to place proposals
                    starting/ending.
            listen_for_high_volume_stream_updates:
                bool, default False, Whether to listen for high volume stream updates.
                    These are generally less necessary, but contain large numbers of
                    updates per block, such as all ledger transactions. For a network
                    running at ~1s/block these are likely to be fine, but can be a
                    hindrance working at full nullchain speed.
            governance_symbol:
                str, default "VOTE", allows the symbol of the governance asset to be
                    defined. This defaults to "VOTE" for nullchain networks but should
                    be changed (most likely to "VEGA") for other networks.

        """
        self._core_client = None
        self._core_state_client = None
        self._trading_data_client_v2 = None
        self._local_data_cache = None
        self.can_control_time = can_control_time
        self.warn_on_raw_data_access = warn_on_raw_data_access

        self._market_price_decimals = None
        self._market_pos_decimals = None
        self._asset_decimals = None
        self._market_to_asset = None
        self._listen_for_high_volume_stream_updates = (
            listen_for_high_volume_stream_updates
        )
        self.seconds_per_block = seconds_per_block

        self.governance_symbol = governance_symbol
        self.asset_mint_map = defaultdict(lambda: 0)

    @property
    def market_price_decimals(self) -> int:
        if self._market_price_decimals is None:
            self._market_price_decimals = DecimalsCache(
                lambda market_id: self.data_cache.market_from_feed(
                    market_id=market_id
                ).decimal_places
            )
        return self._market_price_decimals

    @property
    def market_pos_decimals(self) -> int:
        if self._market_pos_decimals is None:
            self._market_pos_decimals = DecimalsCache(
                lambda market_id: self.data_cache.market_from_feed(
                    market_id=market_id
                ).position_decimal_places
            )
        return self._market_pos_decimals

    @property
    def asset_decimals(self) -> int:
        if self._asset_decimals is None:
            self._asset_decimals = DecimalsCache(
                lambda asset_id: self.data_cache.asset_from_feed(
                    asset_id=asset_id
                ).details.decimals
            )
        return self._asset_decimals

    @property
    def market_to_asset(self) -> str:
        if self._market_to_asset is None:
            self._market_to_asset = DecimalsCache(
                lambda market_id: helpers.get_product(
                    self.data_cache.market_from_feed(market_id=market_id)
                ).settlement_asset
            )
        return self._market_to_asset

    @property
    def data_cache(self) -> LocalDataCache:
        if self._local_data_cache is None:
            self.wait_for_total_catchup()
            self._local_data_cache = LocalDataCache(
                self.trading_data_client_v2,
                self.trading_data_client_v2,
                self.market_pos_decimals,
                self.market_price_decimals,
                self.asset_decimals,
                self.market_to_asset,
            )
            self._local_data_cache.start_live_feeds(
                start_high_load_feeds=self._listen_for_high_volume_stream_updates
            )
        return self._local_data_cache

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
                self.data_node_grpc_url,
                options=(
                    ("grpc.enable_http_proxy", 0),
                    ("grpc.max_send_message_length", 1024 * 1024 * 20),
                    ("grpc.max_receive_message_length", 1024 * 1024 * 20),
                ),
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
            channel = grpc.insecure_channel(
                self.vega_node_grpc_url,
                options=(
                    ("grpc.enable_http_proxy", 0),
                    ("grpc.max_send_message_length", 1024 * 1024 * 20),
                    ("grpc.max_receive_message_length", 1024 * 1024 * 20),
                ),
            )

            grpc.channel_ready_future(channel).result(timeout=10)
            self._core_state_client = vac.VegaCoreStateClient(
                self.vega_node_grpc_url,
                channel=channel,
            )
        return self._core_state_client

    @property
    def core_client(self) -> vac.VegaCoreClient:
        if self._core_client is None:
            channel = grpc.insecure_channel(
                self.vega_node_grpc_url,
                options=(
                    ("grpc.enable_http_proxy", 0),
                    ("grpc.max_send_message_length", 1024 * 1024 * 20),
                    ("grpc.max_receive_message_length", 1024 * 1024 * 20),
                ),
            )

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

    def wait_for_thread_catchup(self, max_retries: int = 1000, threshold: float = 0.5):
        self.wait_for_datanode_sync()
        t0 = time.time()
        attempts = 0
        while attempts < max_retries:
            attempts += 1
            if self.get_blockchain_time() <= self.get_blockchain_time_from_feed():
                break
            time.sleep(0.001)
        t_catchup = time.time() - t0
        if t_catchup > threshold:
            logging.warning(f"Thread catchup took {round(t_catchup, 2)}s.")
        else:
            logging.debug(f"Thread catchup took {round(t_catchup, 2)}s.")

    def wait_for_total_catchup(self) -> None:
        self.wait_for_core_catchup()
        self.wait_for_datanode_sync()

    def stop(self) -> None:
        if self._local_data_cache is not None:
            self._local_data_cache.stop()

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

    def create_key(self, name: str, wallet_name: Optional[str] = None) -> str:
        """Creates a key within the default wallet.

        Args:
            name:
                str, The name of the key to use
             wallet_name:
                str, optional, Name of wallet containing key for agent to use. Defaults
                to value in the environment variable "VEGA_DEFAULT_KEY_NAME".
        Returns:
            str, public key associated to this wallet
        """
        return self.wallet.create_key(wallet_name=wallet_name, name=name)

    def mint(
        self,
        key_name: Optional[str],
        asset: str,
        amount: float,
        wallet_name: Optional[str] = None,
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
            wallet_name=wallet_name, asset_id=asset, key_name=key_name
        ).general

        padded_amount = num_to_padded_int(amount, asset_decimals)
        faucet.mint(
            self.wallet.public_key(wallet_name=wallet_name, name=key_name),
            asset,
            padded_amount,
            faucet_url=self.faucet_url,
        )

        self.wait_fn(1)
        self.wait_for_total_catchup()

        for i in range(100):
            time.sleep(0.05 * 1.03**i)
            self.data_cache.initialise_accounts()
            post_acct = self.party_account(
                wallet_name=wallet_name,
                asset_id=asset,
                key_name=key_name,
            ).general
            if post_acct > curr_acct:
                self.asset_mint_map[asset] += padded_amount
                return
            self.wait_fn(1)

        raise VegaFaucetError(
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
        key_name: str,
        name: str,
        symbol: str,
        decimals: int = 0,
        quantum: int = 1,
        max_faucet_amount: int = 10e9,
        wallet_name: Optional[str] = None,
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
        blockchain_time_seconds = self.get_blockchain_time(in_seconds=True)

        proposal_id = gov.propose_asset(
            wallet=self.wallet,
            wallet_name=wallet_name,
            name=name,
            symbol=symbol,
            decimals=decimals,
            max_faucet_amount=num_to_padded_int(max_faucet_amount, decimals),
            quantum=quantum,
            data_client=self.trading_data_client_v2,
            validation_time=blockchain_time_seconds + self.seconds_per_block * 30,
            closing_time=blockchain_time_seconds + self.seconds_per_block * 40,
            enactment_time=blockchain_time_seconds + self.seconds_per_block * 50,
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
        self.wait_fn(60)
        self.wait_for_thread_catchup()

    def create_market_from_config(
        self,
        proposal_key_name: str,
        market_config: market.MarketConfig,
        proposal_wallet_name: Optional[str] = None,
        vote_closing_time: Optional[datetime.datetime] = None,
        vote_enactment_time: Optional[datetime.datetime] = None,
        approve_proposal: bool = True,
        forward_time_to_enactment: bool = True,
    ) -> str:
        blockchain_time_seconds = self.get_blockchain_time(in_seconds=True)

        enactment_time = (
            blockchain_time_seconds + self.seconds_per_block * 50
            if vote_enactment_time is None
            else int(vote_enactment_time.timestamp())
        )

        proposal_id = gov.propose_market_from_config(
            wallet=self.wallet,
            data_client=self.trading_data_client_v2,
            proposal_wallet_name=proposal_wallet_name,
            proposal_key_name=proposal_key_name,
            market_config=market_config,
            closing_time=(
                blockchain_time_seconds + self.seconds_per_block * 40
                if vote_closing_time is None
                else int(vote_closing_time.timestamp())
            ),
            enactment_time=enactment_time,
            time_forward_fn=lambda: self.wait_fn(2),
        )
        if approve_proposal:
            gov.approve_proposal(
                proposal_id=proposal_id,
                wallet=self.wallet,
                wallet_name=proposal_wallet_name,
                key_name=proposal_key_name,
            )

        if forward_time_to_enactment:
            time_to_enactment = enactment_time - self.get_blockchain_time(
                in_seconds=True
            )
            self.wait_fn(int(time_to_enactment / self.seconds_per_block) + 1)

        self.wait_for_thread_catchup()
        return proposal_id

    def try_enable_perp_markets(
        self, proposal_key: str, wallet_name: str = None, raise_on_failure: bool = False
    ):
        perps_netparam = "limits.markets.proposePerpetualEnabled"
        desired_value = "1"
        if (
            self.get_network_parameter(key=perps_netparam, to_type="str")
            != desired_value
        ):
            logger.info(f"Submitting proposal to enable perpetual markets")
            self.update_network_parameter(
                proposal_key=proposal_key,
                parameter=perps_netparam,
                new_value=desired_value,
                wallet_name=wallet_name,
            )
            self.wait_for_total_catchup()
            if not self.get_network_parameter(key=perps_netparam, to_type="int"):
                if raise_on_failure:
                    raise ValueError(
                        "perps market proposals not allowed by default, allowing via"
                        " network parameter change failed"
                    )
            else:
                logger.info(
                    f"successfully updated network parameter '{perps_netparam}' to"
                    f" '{desired_value}'"
                )

    def create_simple_perps_market(
        self,
        market_name: str,
        proposal_key: str,
        settlement_asset_id: str,
        settlement_data_key: str,
        funding_payment_frequency_in_seconds: Optional[int] = None,
        asset: Optional[str] = None,
        position_decimals: Optional[int] = None,
        market_decimals: Optional[int] = None,
        risk_aversion: Optional[float] = 1e-6,
        tau: Optional[float] = 1.0 / 365.25 / 24,
        sigma: Optional[float] = 1.0,
        price_monitoring_parameters: Optional[
            vega_protos.markets.PriceMonitoringParameters
        ] = None,
        wallet_name: Optional[str] = None,
        settlement_data_wallet_name: Optional[str] = None,
        vote_closing_time: Optional[datetime.datetime] = None,
        vote_enactment_time: Optional[datetime.datetime] = None,
        approve_proposal: bool = True,
        forward_time_to_enactment: bool = True,
        parent_market_id: Optional[str] = None,
        parent_market_insurance_pool_fraction: float = 1,
    ) -> str:
        """Creates a simple perpetual futures market with a predefined reasonable set of parameters.

                Args:
                    market_name:
                        str, name of the market
                    proposal_key:
                        str, the name of the key to use for proposing the market
                    settlement_asset_id:
                        str, the asset id the market will use for settlement
                    termination_key:
                        str, the name of the key which will be used to send termination data
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
                            wallet_name: Optional[str] = None,
        :
                        Optional[str], name of wallet proposing market. Defaults to None.
                    termination_wallet_name:
                        Optional[str], name of wallet settling market. Defaults to None.
                    vote_closing_time:
                        Optional[datetime.datetime]: If set, decides at what time the vote will be set to
                            close. Defaults to Now + 40 blocks
                    vote_enactment_time:
                        Optional[datetime.datetime]: If set, decides at what time the vote will be set to
                            enact. Defaults to Now + 50 blocks
                    approve_proposal:
                        bool, default True, whether to automatically approve the proposal
                    forward_time_to_enactment:
                        bool, default True, whether to forward time until this proposal has already
                            been enacted
                    parent_market_id:
                        Optional[str], Market to set as the parent market on the proposal
                    parent_market_insurance_pool_fraction:
                        float, Fraction of parent market insurance pool to carry over.
                            defaults to 1. No-op if parent_market_id is not set.
        """
        additional_kwargs = {}
        if asset is not None:
            additional_kwargs["perp_asset"] = asset

        blockchain_time_seconds = self.get_blockchain_time(in_seconds=True)

        risk_model = vega_protos.markets.LogNormalRiskModel(
            risk_aversion_parameter=risk_aversion,
            tau=tau,
            params=vega_protos.markets.LogNormalModelParams(mu=0, r=0.0, sigma=sigma),
        )

        enactment_time = (
            blockchain_time_seconds + self.seconds_per_block * 50
            if vote_enactment_time is None
            else int(vote_enactment_time.timestamp())
        )

        proposal_id = gov.propose_perps_market(
            market_name=market_name,
            wallet=self.wallet,
            wallet_name=wallet_name,
            key_name=proposal_key,
            settlement_asset_id=settlement_asset_id,
            data_client=self.trading_data_client_v2,
            settlement_data_pub_key=self.wallet.public_key(
                wallet_name=settlement_data_wallet_name, name=settlement_data_key
            ),
            funding_payment_frequency_in_seconds=funding_payment_frequency_in_seconds,
            position_decimals=position_decimals,
            market_decimals=market_decimals,
            closing_time=(
                blockchain_time_seconds + self.seconds_per_block * 40
                if vote_closing_time is None
                else int(vote_closing_time.timestamp())
            ),
            enactment_time=enactment_time,
            risk_model=risk_model,
            time_forward_fn=lambda: self.wait_fn(2),
            price_monitoring_parameters=price_monitoring_parameters,
            parent_market_id=parent_market_id,
            parent_market_insurance_pool_fraction=parent_market_insurance_pool_fraction,
            **additional_kwargs,
        )
        if approve_proposal:
            gov.approve_proposal(
                proposal_id=proposal_id,
                wallet=self.wallet,
                wallet_name=wallet_name,
                key_name=proposal_key,
            )

        if forward_time_to_enactment:
            time_to_enactment = enactment_time - self.get_blockchain_time(
                in_seconds=True
            )
            self.wait_fn(int(time_to_enactment / self.seconds_per_block) + 1)

        self.wait_for_thread_catchup()
        return proposal_id

    def create_simple_market(
        self,
        market_name: str,
        proposal_key: str,
        settlement_asset_id: str,
        termination_key: str,
        future_asset: Optional[str] = None,
        position_decimals: Optional[int] = None,
        market_decimals: Optional[int] = None,
        risk_aversion: Optional[float] = 1e-6,
        tau: Optional[float] = 1.0 / 365.25 / 24,
        sigma: Optional[float] = 1.0,
        price_monitoring_parameters: Optional[
            vega_protos.markets.PriceMonitoringParameters
        ] = None,
        wallet_name: Optional[str] = None,
        termination_wallet_name: Optional[str] = None,
        vote_closing_time: Optional[datetime.datetime] = None,
        vote_enactment_time: Optional[datetime.datetime] = None,
        approve_proposal: bool = True,
        forward_time_to_enactment: bool = True,
        parent_market_id: Optional[str] = None,
        parent_market_insurance_pool_fraction: float = 1,
    ) -> str:
        """Creates a simple fixed-expiry futures market with a predefined reasonable set of parameters.

                Args:
                    market_name:
                        str, name of the market
                    proposal_key:
                        str, the name of the key to use for proposing the market
                    settlement_asset_id:
                        str, the asset id the market will use for settlement
                    termination_key:
                        str, the name of the key which will be used to send termination data
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
                            wallet_name: Optional[str] = None,
        :
                        Optional[str], name of wallet proposing market. Defaults to None.
                    termination_wallet_name:
                        Optional[str], name of wallet settling market. Defaults to None.
                    vote_closing_time:
                        Optional[datetime.datetime]: If set, decides at what time the vote will be set to
                            close. Defaults to Now + 40 blocks
                    vote_enactment_time:
                        Optional[datetime.datetime]: If set, decides at what time the vote will be set to
                            enact. Defaults to Now + 50 blocks
                    approve_proposal:
                        bool, default True, whether to automatically approve the proposal
                    forward_time_to_enactment:
                        bool, default True, whether to forward time until this proposal has already
                            been enacted
                    parent_market_id:
                        Optional[str], Market to set as the parent market on the proposal
                    parent_market_insurance_pool_fraction:
                        float, Fraction of parent market insurance pool to carry over.
                            defaults to 1. No-op if parent_market_id is not set.
        """
        additional_kwargs = {}
        if future_asset is not None:
            additional_kwargs["future_asset"] = future_asset

        blockchain_time_seconds = self.get_blockchain_time(in_seconds=True)

        risk_model = vega_protos.markets.LogNormalRiskModel(
            risk_aversion_parameter=risk_aversion,
            tau=tau,
            params=vega_protos.markets.LogNormalModelParams(mu=0, r=0.0, sigma=sigma),
        )

        enactment_time = (
            blockchain_time_seconds + self.seconds_per_block * 50
            if vote_enactment_time is None
            else int(vote_enactment_time.timestamp())
        )

        proposal_id = gov.propose_future_market(
            market_name=market_name,
            wallet=self.wallet,
            wallet_name=wallet_name,
            key_name=proposal_key,
            settlement_asset_id=settlement_asset_id,
            data_client=self.trading_data_client_v2,
            termination_pub_key=self.wallet.public_key(
                wallet_name=termination_wallet_name, name=termination_key
            ),
            position_decimals=position_decimals,
            market_decimals=market_decimals,
            closing_time=(
                blockchain_time_seconds + self.seconds_per_block * 40
                if vote_closing_time is None
                else int(vote_closing_time.timestamp())
            ),
            enactment_time=enactment_time,
            risk_model=risk_model,
            time_forward_fn=lambda: self.wait_fn(2),
            price_monitoring_parameters=price_monitoring_parameters,
            parent_market_id=parent_market_id,
            parent_market_insurance_pool_fraction=parent_market_insurance_pool_fraction,
            **additional_kwargs,
        )
        if approve_proposal:
            gov.approve_proposal(
                proposal_id=proposal_id,
                wallet=self.wallet,
                wallet_name=wallet_name,
                key_name=proposal_key,
            )

        if forward_time_to_enactment:
            time_to_enactment = enactment_time - self.get_blockchain_time(
                in_seconds=True
            )
            self.wait_fn(int(time_to_enactment / self.seconds_per_block) + 1)

        self.wait_for_thread_catchup()
        return proposal_id

    def submit_market_order(
        self,
        trading_key: str,
        market_id: str,
        side: Union[vega_protos.vega.Side, str],
        volume: float,
        fill_or_kill: bool = True,
        wait: bool = True,
        order_ref: Optional[str] = None,
        trading_wallet: Optional[str] = None,
        reduce_only: bool = False,
        post_only: bool = False,
    ) -> str:
        """Places a simple Market order, either as Fill-Or-Kill or Immediate-Or-Cancel.

        Args:
            trading_key:
                str, the name of the key to use for trading
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
            wallet_name:
                optional str, name of wallet to use
            reduce_only (bool):
                Whether the order should only reduce a parties position. Defaults to
                False.
            post_only (bool):
                Whether order should be prevented from trading immediately. Defaults to
                False.

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
            trading_key=trading_key,
            reduce_only=reduce_only,
            post_only=post_only,
        )

    def submit_order(
        self,
        trading_key: str,
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
        trading_wallet: Optional[str] = None,
        reduce_only: bool = False,
        post_only: bool = False,
        peak_size: Optional[float] = None,
        minimum_visible_size: Optional[float] = None,
    ) -> Optional[str]:
        """
        Submit orders as specified to required pre-existing market.
        Optionally wait for acceptance of order (raises on non-acceptance)

        Args:
            trading_key:
                str, the name of the key to use for trading
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
            reduce_only (bool):
                Whether the order should only reduce a parties position. Defaults to
                False.
            post_only (bool):
                Whether order should be prevented from trading immediately. Defaults to
                False.
            peak_size:
                optional float, size of the order that is made visible and can be traded with during the execution of a single order.
            minimum_visible_size:
                optional float, minimum allowed remaining size of the order before it is replenished back to its peak size

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
        if (peak_size is None and minimum_visible_size is not None) or (
            peak_size is not None and minimum_visible_size is None
        ):
            raise ValueError(
                "Both 'peak_size' and 'minimum_visible_size' must be specified or none"
                " at all."
            )

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
            pegged_order=(
                vega_protos.vega.PeggedOrder(
                    reference=pegged_order.reference,
                    offset=str(
                        num_to_padded_int(
                            pegged_order.offset, self.market_price_decimals[market_id]
                        )
                    ),
                )
                if pegged_order is not None
                else None
            ),
            wait=wait,
            time_forward_fn=lambda: self.wait_fn(2),
            order_ref=order_ref,
            key_name=trading_key,
            reduce_only=reduce_only,
            post_only=post_only,
            iceberg_opts=(
                vega_protos.commands.v1.commands.IcebergOpts(
                    peak_size=num_to_padded_int(
                        peak_size, self.market_pos_decimals[market_id]
                    ),
                    minimum_visible_size=num_to_padded_int(
                        minimum_visible_size, self.market_pos_decimals[market_id]
                    ),
                )
                if (peak_size is not None and minimum_visible_size is not None)
                else None
            ),
        )

    def get_blockchain_time(self, in_seconds: bool = False) -> int:
        """Returns blockchain time in seconds or nanoseconds since the epoch"""
        return gov.get_blockchain_time(
            self.trading_data_client_v2, in_seconds=in_seconds
        )

    def amend_order(
        self,
        trading_key: str,
        market_id: str,
        order_id: str,
        price: Optional[float] = None,
        expires_at: Optional[int] = None,
        pegged_offset: Optional[float] = None,
        pegged_reference: Optional[vega_protos.vega.PeggedReference] = None,
        volume_delta: float = 0,
        time_in_force: Optional[Union[vega_protos.vega.Order.TimeInForce, str]] = None,
        wallet_name: Optional[str] = None,
    ):
        """
        Amend a Limit order by orderID in the specified market

        Args:
            trading_key:
                str, the name of the key to use for trading
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
            wallet_name:
                optional str, name of wallet to use
        """
        trading.amend_order(
            wallet=self.wallet,
            key_name=trading_key,
            wallet_name=wallet_name,
            market_id=market_id,
            order_id=order_id,
            price=(
                str(
                    num_to_padded_int(
                        price,
                        self.market_price_decimals[market_id],
                    )
                )
                if price is not None
                else None
            ),
            expires_at=expires_at,
            pegged_offset=(
                str(
                    num_to_padded_int(
                        pegged_offset,
                        self.market_price_decimals[market_id],
                    )
                )
                if pegged_offset is not None
                else None
            ),
            pegged_reference=pegged_reference,
            volume_delta=num_to_padded_int(
                volume_delta,
                self.market_pos_decimals[market_id],
            ),
            time_in_force=time_in_force,
        )

    def cancel_order(
        self,
        trading_key: str,
        market_id: str,
        order_id: Optional[str] = None,
        wallet_name: Optional[str] = None,
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
            wallet_name=wallet_name,
            market_id=market_id,
            order_id=order_id,
            key_name=trading_key,
        )

    def update_network_parameter(
        self, proposal_key: str, parameter: str, new_value: str, wallet_name: str = None
    ):
        """Updates a network parameter by first proposing and then voting to approve
        the change, followed by advancing the network time period forwards.

        If the genesis setup of the market is such that this meets requirements then
        the proposal will be approved. Otherwise others may need to vote too.

        Args:
            proposal_key:
                str, the key proposing the change
            parameter:
                str, the parameter to change
            new_value:
                str, the new value to set
            wallet_name:
                str, optional, the wallet proposing the change
        Returns:
            str, the ID of the proposal
        """
        blockchain_time_seconds = self.get_blockchain_time(in_seconds=True)

        proposal_id = gov.propose_network_parameter_change(
            parameter=parameter,
            value=new_value,
            wallet=self.wallet,
            wallet_name=wallet_name,
            data_client=self.trading_data_client_v2,
            closing_time=blockchain_time_seconds + self.seconds_per_block * 40,
            enactment_time=blockchain_time_seconds + self.seconds_per_block * 50,
            time_forward_fn=lambda: self.wait_fn(2),
            key_name=proposal_key,
        )
        gov.approve_proposal(
            proposal_id=proposal_id,
            wallet=self.wallet,
            wallet_name=wallet_name,
            key_name=proposal_key,
        )
        self.wait_fn(60)
        self.wait_for_thread_catchup()

    def update_market_state(
        self,
        market_id: str,
        proposal_key: str,
        market_state: MarketStateUpdateType,
        price: Optional[float] = None,
        wallet_name: Optional[str] = None,
        vote_closing_time: Optional[datetime.datetime] = None,
        vote_enactment_time: Optional[datetime.datetime] = None,
        approve_proposal: bool = True,
        forward_time_to_enactment: bool = True,
    ) -> str:
        """Update the state of a market using a governance proposal. Optionally
        automatically approves the proposal and forwards time to the enactment.

        Args:
            market_id:
                str, The ID of the market to update
            proposal_key:
                str, The name of the key proposing the change. If automatically
                    approving this key should have enough governance tokens to
                    approve by itself
            market_state:
                MarketStateUpdateType, The value of the market state to set
            price:
                Optional[float], If setting a termination state, the value at
                    which to terminate (last mark price)
            wallet_name:
                Optional[str], If using a non-default wallet name, the wallet
                    containing the proposal key name
            vote_closing_time:
                Optional[datetime], The time at which the vote should close
            vote_enactment_time:
                Optional[datetime], The time at which the vote should enact
            approve_proposal:
                bool, default True, Whether to automatically approve the proposal
            forward_time_to_enactment:
                bool, default True, Whether to forward time to enactment of the
                    proposal

        Returns:
            str, The proposal ID
        """
        conv_price = (
            str(num_to_padded_int(price, self.market_price_decimals[market_id]))
            if price is not None
            else None
        )

        blockchain_time_seconds = self.get_blockchain_time(in_seconds=True)

        enactment_time = (
            blockchain_time_seconds + self.seconds_per_block * 50
            if vote_enactment_time is None
            else int(vote_enactment_time.timestamp())
        )
        proposal_id = gov.propose_market_state_update(
            market_state=market_state.value,
            market_id=market_id,
            price=conv_price,
            closing_time=(
                blockchain_time_seconds + self.seconds_per_block * 40
                if vote_closing_time is None
                else int(vote_closing_time.timestamp())
            ),
            enactment_time=enactment_time,
            time_forward_fn=lambda: self.wait_fn(2),
            data_client=self.trading_data_client_v2,
            wallet=self.wallet,
            key_name=proposal_key,
            wallet_name=wallet_name,
        )
        if approve_proposal:
            gov.approve_proposal(
                proposal_id=proposal_id,
                wallet=self.wallet,
                key_name=proposal_key,
                wallet_name=wallet_name,
            )

        if forward_time_to_enactment:
            time_to_enactment = enactment_time - self.get_blockchain_time(
                in_seconds=True
            )
            self.wait_fn(int(time_to_enactment / self.seconds_per_block) + 1)
        return proposal_id

    def update_market(
        self,
        proposal_key: str,
        market_id: str,
        updated_instrument: Optional[UpdateInstrumentConfiguration] = None,
        updated_metadata: Optional[str] = None,
        updated_price_monitoring_parameters: Optional[PriceMonitoringParameters] = None,
        updated_liquidity_monitoring_parameters: Optional[
            LiquidityMonitoringParameters
        ] = None,
        updated_simple_model_params: Optional[SimpleModelParams] = None,
        updated_log_normal_risk_model: Optional[LogNormalRiskModel] = None,
        wallet_name: Optional[int] = None,
        updated_sla_parameters: Optional[LiquiditySLAParameters] = None,
        updated_liquidation_strategy: Optional[LiquidationStrategy] = None,
    ):
        """Updates a market based on proposal parameters. Will attempt to propose
        and then immediately vote on the market change before forwarding time for
        the enactment to also take effect

        Args:
            proposal_key:
                str, the key proposing the change
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

        blockchain_time_seconds = self.get_blockchain_time(in_seconds=True)

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
            price_monitoring_parameters=(
                updated_price_monitoring_parameters
                if updated_price_monitoring_parameters is not None
                else current_market.price_monitoring_settings.parameters
            ),
            liquidity_monitoring_parameters=(
                updated_liquidity_monitoring_parameters
                if updated_liquidity_monitoring_parameters is not None
                else current_market.liquidity_monitoring_parameters
            ),
            simple=updated_simple_model_params,
            log_normal=updated_log_normal_risk_model,
            metadata=updated_metadata,
            liquidity_sla_parameters=(
                updated_sla_parameters
                if updated_sla_parameters is not None
                else current_market.liquidity_sla_params
            ),
            linear_slippage_factor=current_market.linear_slippage_factor,
            quadratic_slippage_factor=current_market.quadratic_slippage_factor,
            liquidation_strategy=(
                updated_liquidation_strategy
                if updated_liquidation_strategy is not None
                else vega_protos.markets.LiquidationStrategy(
                    disposal_time_step=1,
                    disposal_fraction="1",
                    full_disposal_size=1000000000,
                    max_fraction_consumed="0.5",
                )
            ),
        )

        proposal_id = gov.propose_market_update(
            market_update=update_configuration,
            market_id=market_id,
            wallet=self.wallet,
            key_name=proposal_key,
            wallet_name=wallet_name,
            data_client=self.trading_data_client_v2,
            closing_time=blockchain_time_seconds + self.seconds_per_block * 40,
            enactment_time=blockchain_time_seconds + self.seconds_per_block * 50,
            time_forward_fn=lambda: self.wait_fn(2),
        )
        gov.approve_proposal(
            proposal_id=proposal_id,
            wallet=self.wallet,
            key_name=proposal_key,
            wallet_name=wallet_name,
        )
        self.wait_fn(60)
        self.wait_for_thread_catchup()

    def submit_termination_and_settlement_data(
        self,
        settlement_key: str,
        settlement_price: float,
        market_id: str,
        wallet_name: Optional[str] = None,
    ):
        product = helpers.get_product(
            self._local_data_cache.market_from_feed(market_id)
        )

        filter_key = (
            product.data_source_spec_for_settlement_data.data.external.oracle.filters[
                0
            ].key
        )
        oracle_name = filter_key.name

        logger.info(
            "Submitting market termination signal and settlement price"
            f" {settlement_price} for {oracle_name}"
        )

        gov.submit_termination_and_settlement_data(
            wallet=self.wallet,
            wallet_name=wallet_name,
            oracle_name=oracle_name,
            settlement_price=num_to_padded_int(
                settlement_price, decimals=filter_key.number_decimal_places
            ),
            key_name=settlement_key,
        )

    def submit_settlement_data(
        self,
        settlement_key: str,
        settlement_price: float,
        market_id: str,
        wallet_name: Optional[str] = None,
        additional_payload: Optional[dict[str, str]] = None,
    ):
        product = helpers.get_product(
            self._local_data_cache.market_from_feed(market_id)
        )

        filter_key = (
            product.data_source_spec_for_settlement_data.data.external.oracle.filters[
                0
            ].key
        )
        oracle_name = filter_key.name

        msg = f"Submitting settlement price {settlement_price} for {oracle_name}"
        if additional_payload != None:
            msg += f" with additional payload: {additional_payload}"
        logger.info(msg)

        gov.submit_settlement_data(
            wallet=self.wallet,
            wallet_name=wallet_name,
            oracle_name=oracle_name,
            settlement_price=num_to_padded_int(
                settlement_price, decimals=filter_key.number_decimal_places
            ),
            key_name=settlement_key,
            additional_payload=additional_payload,
        )

    def party_account(
        self,
        key_name: str,
        market_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        wallet_name: Optional[str] = None,
    ) -> data.PartyMarketAccount:
        """Output money in general accounts/margin accounts/bond accounts (if exists)
        of a party."""
        if market_id is None and asset_id is None:
            raise Exception("Either market or asset must be passed")
        if market_id is not None and asset_id is not None:
            raise Exception("Only one of market or asset can be passed")

        if market_id is not None:
            asset_id = self._market_to_asset[market_id]

        accounts = self.get_accounts_from_stream(
            key_name=key_name,
            market_id=market_id,
            wallet_name=wallet_name,
            asset_id=asset_id,
        )
        return data.account_list_to_party_account(
            accounts=accounts,
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
            pub_key=(
                self.wallet.public_key(wallet_name=wallet_name, name=key_name)
                if key_name is not None
                else None
            ),
            asset_id=asset_id,
            market_id=market_id,
            asset_decimals_map=self.asset_decimals,
        )

    def get_accounts_from_stream(
        self,
        key_name: Optional[str] = None,
        market_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        wallet_name: Optional[str] = None,
    ) -> List[data.AccountData]:
        """Loads accounts for either a given party, market or both from stream.
        Must pass one or the other

        Args:
            market_id:
                optional str, Restrict to accounts on a specific market
            asset_id:
                optional str, Restrict to accounts on a specific asset
            party_id:
                optional str, Select only accounts for a given party

        Returns:
            List[AccountData], list of formatted trade objects which match the required
                restrictions.
        """
        return self.data_cache.get_accounts_from_stream(
            market_id=market_id,
            party_id=(
                self.wallet.public_key(wallet_name=wallet_name, name=key_name)
                if key_name is not None
                else None
            ),
            asset_id=asset_id,
        )

    def positions_by_market(
        self,
        key_name: str,
        market_id: Optional[str] = None,
        wallet_name: Optional[str] = None,
    ) -> List[vega_protos.vega.Position]:
        """Output positions of a party."""
        return data.positions_by_market(
            pub_key=self.wallet.public_key(wallet_name=wallet_name, name=key_name),
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
    def market_data_from_feed(
        self,
        market_id: str,
    ) -> vega_protos.vega.MarketData:
        """
        Output market info.
        """
        return self.data_cache.market_data_from_feed(market_id)

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

    def get_latest_market_data(
        self,
        market_id: str,
    ) -> vega_protos.vega.MarketData:
        """
        Output market info.
        """
        return data.get_latest_market_data(
            market_id=market_id,
            data_client=self.trading_data_client_v2,
            market_price_decimals_map=self.market_price_decimals,
            market_position_decimals_map=self.market_pos_decimals,
            market_to_asset_map=self.market_to_asset,
            asset_decimals_map=self.asset_decimals,
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
    ) -> Tuple[float, float]:
        """
        Output the best static bid price and best static ask price in current market.
        """
        market_data = self.get_latest_market_data(
            market_id=market_id,
        )

        return (
            market_data.best_static_bid_price,
            market_data.best_static_offer_price,
        )

    def price_bounds(
        self,
        market_id: str,
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Output the tightest price bounds in the current market.
        """
        market_data = self.get_latest_market_data(
            market_id=market_id,
        )

        lower_bounds = [
            price_monitoring_bound.min_valid_price
            for price_monitoring_bound in market_data.price_monitoring_bounds
        ]
        upper_bounds = [
            price_monitoring_bound.max_valid_price
            for price_monitoring_bound in market_data.price_monitoring_bounds
        ]

        return (
            max(lower_bounds) if lower_bounds else None,
            min(upper_bounds) if upper_bounds else None,
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
        key_name: str,
        market_id: str,
        commitment_amount: float,
        fee: float,
        is_amendment: Optional[bool] = None,
        wallet_name: Optional[str] = None,
    ):
        """Submit/Amend a simple liquidity commitment (LP) with a single amount on each side.

        Args:
            key_name:
                str, The name of the key which is placing the order
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
            wallet_name:
                str, The name of the wallet which is placing the order
        """
        asset_id = self.market_to_asset[market_id]

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
            wallet=self.wallet,
            wallet_name=wallet_name,
            is_amendment=is_amendment,
            key_name=key_name,
        )

    def has_liquidity_provision(
        self,
        key_name: str,
        market_id: str,
        wallet_name: Optional[str] = None,
    ):
        return data.has_liquidity_provision(
            self.trading_data_client_v2,
            market_id,
            party_id=self.wallet.public_key(wallet_name=wallet_name, name=key_name),
        )

    def submit_liquidity(
        self,
        key_name: str,
        market_id: str,
        commitment_amount: float,
        fee: float,
        is_amendment: Optional[bool] = None,
        wallet_name: Optional[str] = None,
    ):
        """Submit/Amend a custom liquidity profile.

        Args:
            key_name:
                str, the key name performing the action
            market_id:
                str, The ID of the market to place the commitment on
            commitment_amount:
                int, The amount in asset decimals of market asset to commit
                to liquidity provision
            fee:
                float, The fee level at which to set the LP fee
                 (in %, e.g. 0.01 == 1% and 1 == 100%)
            is_amendment:
                Optional bool, Is the submission an amendment to an existing provision
                    If None, will query the network to check.
            wallet_name:
                optional, str name of wallet to use
        """
        asset_id = self.market_to_asset[market_id]

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
            wallet=self.wallet,
            wallet_name=wallet_name,
            is_amendment=is_amendment,
            key_name=key_name,
        )

    def cancel_liquidity(
        self,
        key_name: str,
        market_id: str,
        wallet_name: Optional[str] = None,
    ):
        """Cancel a custom liquidity profile.

        Args:
            key_name:
                str, the key name performing the action
            market_id:
                str, The ID of the market to place the commitment on
            commitment_amount:
                int, The amount in asset decimals of market asset to commit
                to liquidity provision
            fee:
                float, The fee level at which to set the LP fee
                 (in %, e.g. 0.01 == 1% and 1 == 100%)
            is_amendment:
                Optional bool, Is the submission an amendment to an existing provision
                    If None, will query the network to check.
            wallet_name:
                optional, str name of wallet to use
        """
        return trading.cancel_liquidity(
            market_id=market_id,
            wallet=self.wallet,
            wallet_name=wallet_name,
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

    def find_asset_id(
        self, symbol: str, enabled: bool = True, raise_on_missing: bool = False
    ) -> str:
        """Looks up the Asset ID of a given asset name

        Args:
            symbol:
                str, The symbol of the asset to look up
            enabled:
                bool, whether the asset must be enabled for the id to be returned
            raise_on_missing:
                bool, whether to raise an Error or silently return if the asset
                 does not exist

        Returns:
            str, the ID of the asset
        """
        return data.find_asset_id(
            symbol=symbol,
            raise_on_missing=raise_on_missing,
            enabled=enabled,
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

    def get_blockchain_time_from_feed(self):
        return self.data_cache.time_update_from_feed()

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
        return self.data_cache.order_status_from_feed(live_only=live_only)

    def orders_for_party_from_feed(
        self,
        key_name: str,
        market_id: str,
        live_only: bool = True,
        wallet_name: Optional[str] = None,
    ) -> Dict[str, data.Order]:
        party_id = self.wallet.public_key(wallet_name=wallet_name, name=key_name)
        return self.data_cache.orders_for_party_from_feed(
            party_id=party_id, market_id=market_id, live_only=live_only
        )

    def transfer_status_from_feed(
        self, live_only: bool = True, blockchain_time: Optional[int] = None
    ):
        blockchain_time = (
            blockchain_time
            if blockchain_time is not None or not live_only
            else self.get_blockchain_time()
        )
        return self.data_cache.transfer_status_from_feed(
            live_only=live_only, blockchain_time=blockchain_time
        )

    def network_parameter_from_feed(self, key: str) -> data.NetworkParameter:
        return self.data_cache.network_parameter_from_feed(key=key)

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
        key_name: str,
        market_id: Optional[str] = None,
        wallet_name: Optional[str] = None,
    ) -> Optional[List[vega_protos.vega.LiquidityProvision]]:
        """Loads the current liquidity provision(s) for a given market and/or party.

        Args:
            key_name:
                str, key name stored in metadata.
            market_id:
                Optional[str], the ID of the market from which to
                    pull liquidity provisions
            party_id:
                Optional[str], the ID of the party from which to
                    pull liquidity provisions
            wallet_name:
                Optional[str], Specify a different wallet name to default

        Returns:
            List[LiquidityProvision], list of liquidity provisions (if any exist)
        """
        return self.liquidity_provisions(
            market_id=market_id,
            party_id=self.wallet.public_key(wallet_name=wallet_name, name=key_name),
        )

    def margin_levels(
        self,
        key_name: str = None,
        market_id: Optional[str] = None,
        wallet_name: Optional[str] = None,
    ) -> List[data.MarginLevels]:
        return data.margin_levels(
            self.trading_data_client_v2,
            party_id=self.wallet.public_key(wallet_name=wallet_name, name=key_name),
            market_id=market_id,
        )

    def list_orders(
        self,
        key_name: str,
        market_id: str,
        wallet_name: Optional[str] = None,
        reference: Optional[str] = None,
        live_only: Optional[bool] = True,
    ) -> List[data.Order]:
        """Return a list of orders for the specified market and party.

        Args:
            key_name (str):
                Name of key to return orders for.
            wallet_name (str):
                Name of wallet to return orders for.
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
            party_id=self.wallet.public_key(wallet_name=wallet_name, name=key_name),
            reference=reference,
            live_only=live_only,
        )

    def get_ledger_entries_from_stream(
        self,
        wallet_name_from: Optional[str] = None,
        key_name_from: Optional[str] = None,
        wallet_name_to: Optional[str] = None,
        key_name_to: Optional[str] = None,
        transfer_type: Optional[str] = None,
    ) -> List[data.LedgerEntry]:
        return self.data_cache.get_ledger_entries_from_stream(
            party_id_from=(
                self.wallet.public_key(wallet_name=wallet_name_from, name=key_name_from)
                if wallet_name_from is not None
                else None
            ),
            party_id_to=(
                self.wallet.public_key(wallet_name=wallet_name_to, name=key_name_to)
                if wallet_name_to is not None
                else None
            ),
            transfer_type=transfer_type,
        )

    def get_trades_from_stream(
        self,
        market_id: Optional[str] = None,
        wallet_name: Optional[str] = None,
        key_name: Optional[str] = None,
        order_id: Optional[str] = None,
        exclude_trade_ids: Optional[Set[str]] = None,
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
            exclude_trade_ids:
                optional set[str], Do not return trades with ID in this set

        Returns:
            List[Trade], list of formatted trade objects which match the required
                restrictions.
        """
        party_id = (
            self.wallet.public_key(wallet_name=wallet_name, name=key_name)
            if key_name is not None
            else None
        )
        return self.data_cache.get_trades_from_stream(
            market_id=market_id,
            party_id=party_id,
            order_id=order_id,
            exclude_trade_ids=exclude_trade_ids,
        )

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
            party_id=(
                self.wallet.public_key(wallet_name=wallet_name, name=key_name)
                if key_name is not None
                else None
            ),
            market_id=market_id,
            order_id=order_id,
            market_asset_decimals_map=(
                {market_id: asset_dp} if market_id is not None else None
            ),
            market_position_decimals_map=self.market_pos_decimals,
            market_price_decimals_map=self.market_price_decimals,
        )

    def build_order_amendment(
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
            pegged_offset=(
                str(pegged_offset) if pegged_offset is not None else pegged_offset
            ),
            pegged_reference=pegged_reference,
        )

    def build_order_cancellation(
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

    def build_order_submission(
        self,
        market_id: str,
        size: float,
        side: Union[vega_protos.vega.Side, str],
        order_type: Optional[Union[vega_protos.vega.Order.Type, str]],
        time_in_force: Optional[Union[vega_protos.vega.Order.TimeInForce, str]],
        price: Optional[float] = None,
        expires_at: Optional[int] = None,
        reference: Optional[str] = None,
        reduce_only: bool = False,
        post_only: bool = False,
        pegged_order: Optional[vega_protos.vega.PeggedOrder] = None,
        iceberg_opts: Optional[vega_protos.commands.v1.commands.IcebergOpts] = None,
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
            reduce_only (bool):
                Whether the order should only reduce a parties position. Defaults to
                False.
            post_only (bool):
                Whether order should be prevented from trading immediately. Defaults to
                False.

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
        size = (
            size
            if size is None
            else num_to_padded_int(
                to_convert=size, decimals=self.market_pos_decimals[market_id]
            )
        )
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
            reduce_only=reduce_only,
            post_only=post_only,
            iceberg_opts=iceberg_opts,
        )

    def submit_instructions(
        self,
        key_name: str,
        wallet_name: Optional[str] = None,
        cancellations: Optional[List[OrderCancellation]] = None,
        amendments: Optional[List[OrderAmendment]] = None,
        submissions: Optional[List[OrderSubmission]] = None,
        stop_orders_cancellation: Optional[List[StopOrdersCancellation]] = None,
        stop_orders_submission: Optional[List[StopOrdersSubmission]] = None,
    ):
        """Submits a batch of market instructions to be processed sequentially.

        Method allows lists of order cancellations, order amendments, and order
        submissions to be submitted as a batch and processed sequentially in the
        order cancellations, amendments, then submissions.

        If the number of cancellation, amendment, and submission instructions exceed
        the network parameter spam.protection.max.batchSize, the function will submit
        the instructions in multiple batches adhering to the above rules.

        Args:
            key_name (str):
                Name of key to submit transaction from.
            wallet_name (Optional str):
                Name of wallet to submit transaction from.
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

        instructions = (
            (cancellations if cancellations is not None else [])
            + (amendments if amendments is not None else [])
            + (submissions if submissions is not None else [])
            + (stop_orders_cancellation if stop_orders_cancellation is not None else [])
            + (stop_orders_submission if stop_orders_submission is not None else [])
        )

        batch_size = 0

        batch_of_cancellations = []
        batch_of_amendments = []
        batch_of_submissions = []
        batch_of_stop_orders_cancellation = []
        batch_of_stop_orders_submission = []

        for i, instruction in enumerate(instructions):
            if instruction is None:
                continue
            elif isinstance(instruction, OrderCancellation):
                batch_of_cancellations.append(instruction)
            elif isinstance(instruction, OrderAmendment):
                batch_of_amendments.append(instruction)
            elif isinstance(instruction, OrderSubmission):
                batch_of_submissions.append(instruction)
            elif isinstance(instruction, StopOrdersCancellation):
                batch_of_stop_orders_cancellation.append(instruction)
            elif isinstance(instruction, StopOrdersSubmission):
                batch_of_stop_orders_submission.append(instruction)
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
                    stop_orders_submission=batch_of_stop_orders_submission,
                    stop_orders_cancellation=batch_of_stop_orders_cancellation,
                )

                batch_size = 0

                batch_of_cancellations = []
                batch_of_amendments = []
                batch_of_submissions = []
                batch_of_stop_orders_submission = []
                batch_of_stop_orders_cancellation = []

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

    def ping_datanode(self, max_time_diff: float = 30, max_response_time: float = 0.5):
        """Ping datanode endpoint to check health of connection

        Args:
            max_time_diff (int, optional):
                The maximum allowable deviation between the time reported by datanode
                and the time reported by the system in seconds. Defaults to 30

        """

        t = time.time()
        data.ping(data_client=self.trading_data_client_v2)

        t_response = abs(time.time() - t)
        t_delay = abs(self.get_blockchain_time(in_seconds=True) - t)

        if t_response > max_response_time:
            raise DatanodeSlowResponseError

        if t_delay > max_time_diff:
            raise DatanodeBehindError

    def one_off_transfer(
        self,
        from_key_name: str,
        from_account_type: vega_protos.vega.AccountType,
        to_account_type: vega_protos.vega.AccountType,
        asset: str,
        amount: float,
        to_key_name: Optional[str] = None,
        reference: Optional[str] = None,
        from_wallet_name: Optional[str] = None,
        to_wallet_name: Optional[str] = None,
        delay: Optional[int] = None,
    ):
        """Submit a one off transfer command.

        Args:
            from_key_name (str):
                Name of key in wallet to send from.
            to_key_name (str):
                Name of key in wallet to send to.
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
            from_wallet_name (Optional[str], optional):
                Name of wallet to transfer from.
            to_wallet_name (Optional[str], optional):
                Name of wallet to transfer to.
            delay (Optional[int], optional):
                Delay in nanoseconds to add before transfer is sent. Defaults to None.
        """

        adp = self.asset_decimals[asset]

        one_off = vega_protos.commands.v1.commands.OneOffTransfer()
        if delay is not None:
            setattr(one_off, "deliver_on", int(self.get_blockchain_time() + delay))

        trading.transfer(
            wallet=self.wallet,
            wallet_name=from_wallet_name,
            key_name=from_key_name,
            from_account_type=from_account_type,
            to=(
                self.wallet.public_key(wallet_name=to_wallet_name, name=to_key_name)
                if to_key_name is not None
                else "0000000000000000000000000000000000000000000000000000000000000000"
            ),
            to_account_type=to_account_type,
            asset=asset,
            amount=str(num_to_padded_int(amount, adp)),
            reference=reference,
            one_off=one_off,
        )

    def recurring_transfer(
        self,
        from_key_name: str,
        from_account_type: vega_protos.vega.AccountType,
        to_account_type: vega_protos.vega.AccountType,
        asset: str,
        amount: float,
        to_key_name: Optional[str] = None,
        reference: Optional[str] = None,
        from_wallet_name: Optional[str] = None,
        to_wallet_name: Optional[str] = None,
        start_epoch: Optional[int] = None,
        end_epoch: Optional[int] = None,
        factor: float = 1,
        asset_for_metric: Optional[str] = None,
        metric: Optional[vega_protos.vega.DispatchMetric] = None,
        markets: Optional[List[str]] = None,
        entity_scope: Optional[vega_protos.vega.EntityScope] = None,
        individual_scope: Optional[vega_protos.vega.IndividualScope] = None,
        team_scope: Optional[List[str]] = None,
        n_top_performers: Optional[float] = None,
        staking_requirement: Optional[float] = None,
        notional_time_weighted_average_position_requirement: Optional[float] = None,
        window_length: Optional[int] = None,
        lock_period: Optional[int] = None,
        distribution_strategy: Optional[vega_protos.vega.DistributionStrategy] = None,
        rank_table: Optional[List[vega_protos.vega.Rank]] = None,
    ):
        """Create a recurring transfer of funds.

        Function can be used to setup a recurring transfer of funds between two keys or
        between a key and a network reward pool. If funding a reward pool, a dispatch
        strategy can be specified to fund a specific pool.

        Args:
            from_key_name (str):
                The key name of the source account.
            from_account_type (vega_protos.vega.AccountType):
                The account type of the source account.
            to_account_type (vega_protos.vega.AccountType):
                The account type of the destination account.
            asset (str):
                The id of the asset to transfer.
            amount (float):
                The amount of the asset to transfer.
            to_key_name (Optional[str], optional):
                The key name of the destination account. Defaults to None.
            reference (Optional[str], optional):
                A reference string for the transfer. Defaults to None.
            from_wallet_name (Optional[str], optional):
                The name of the source wallet. Defaults to None.
            to_wallet_name (Optional[str], optional):
                The name of the destination wallet. Defaults to None.
            start_epoch (Optional[int], optional):
                The epoch to start the transfer. Defaults to None (next epoch).
            end_epoch (Optional[int], optional):
                The epoch to end the transfer. Defaults to None (never ends).
            factor (float, optional):
                The factor to adjust the transfer amount by each epoch. Defaults to 1.
            asset_for_metric (Optional[str], optional):
                The asset to use for the dispatch metric. Defaults to None.
            metric (Optional[vega_protos.vega.DispatchMetric], optional):
                The dispatch metric. Defaults to None.
            markets (Optional[List[str]], optional):
                The list of markets to apply the dispatch strategy. Defaults to None.

        Raises:
            Exception:
                If a value is provided for one but not all non-optional
                DispatchStrategy fields.

        Returns:
            None
        """

        # Set the mandatory RecurringTransfer fields
        recurring_transfer = vega_protos.commands.v1.commands.RecurringTransfer(
            start_epoch=(
                start_epoch
                if start_epoch is not None
                else int(self.statistics().epoch_seq)
            )
        )
        # Set the optional RecurringTransfer fields
        if end_epoch is not None:
            setattr(recurring_transfer, "end_epoch", int(end_epoch))
        if factor is not None:
            setattr(recurring_transfer, "factor", str(factor))

        # If any dispatch strategy field is set, try and create a dispatch strategy
        if any(
            [
                arg is not None
                for arg in [
                    entity_scope,
                    window_length,
                    lock_period,
                    distribution_strategy,
                    metric,
                    asset_for_metric,
                    individual_scope,
                    n_top_performers,
                    staking_requirement,
                    notional_time_weighted_average_position_requirement,
                    markets,
                    team_scope,
                    rank_table,
                ]
            ]
        ):
            dispatch_strategy = data.dispatch_strategy(
                asset_for_metric=asset_for_metric,
                metric=metric,
                markets=markets,
                entity_scope=entity_scope,
                individual_scope=individual_scope,
                team_scope=team_scope,
                n_top_performers=n_top_performers,
                staking_requirement=staking_requirement,
                notional_time_weighted_average_position_requirement=notional_time_weighted_average_position_requirement,
                window_length=window_length,
                lock_period=lock_period,
                distribution_strategy=distribution_strategy,
                rank_table=rank_table,
            )
            recurring_transfer.dispatch_strategy.CopyFrom(dispatch_strategy)

        trading.transfer(
            wallet=self.wallet,
            wallet_name=from_wallet_name,
            key_name=from_key_name,
            from_account_type=from_account_type,
            to=(
                self.wallet.public_key(wallet_name=to_wallet_name, name=to_key_name)
                if to_key_name is not None
                else "0000000000000000000000000000000000000000000000000000000000000000"
            ),
            to_account_type=to_account_type,
            asset=asset,
            amount=str(num_to_padded_int(amount, self.asset_decimals[asset])),
            reference=reference,
            recurring=recurring_transfer,
        )

    def list_transfers(
        self,
        wallet_name: Optional[str] = None,
        key_name: Optional[str] = None,
        direction: Optional[data_node_protos_v2.trading_data.TransferDirection] = None,
        is_reward: Optional[bool] = None,
        from_epoch: Optional[int] = None,
        to_epoch: Optional[int] = None,
        status: Optional[vega_protos.events.v1.events.Transfer.Status] = None,
        scope: Optional[
            data_node_protos_v2.trading_data.ListTransfersRequest.Scope
        ] = None,
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
            self.wallet.public_key(wallet_name=wallet_name, name=key_name)
            if wallet_name is not None
            else None
        )

        return data.list_transfers(
            data_client=self.trading_data_client_v2,
            party_id=party_id,
            direction=direction,
            is_reward=is_reward,
            from_epoch=from_epoch,
            to_epoch=to_epoch,
            status=status,
            scope=scope,
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

        market_data = self.get_latest_market_data(market_id=market_id)

        # Calculate share of fees for each LP
        shares = {
            lp.party: float(lp.equity_like_share) * float(lp.average_score)
            for lp in market_data.liquidity_provider_fee_share
        }
        total_shares = sum(shares.values())

        # Scale share of fees for each LP pro rata
        if total_shares != 0:
            pro_rata_shares = {key: val / total_shares for key, val in shares.items()}
        else:
            pro_rata_shares = {key: 1 / len(shares) for key, val in shares.items()}

        if key_name is None:
            return pro_rata_shares
        else:
            return pro_rata_shares[
                self.wallet.public_key(name=key_name, wallet_name=wallet_name)
            ]

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

    def get_risk_factors(self, market_id: str):
        return data.get_risk_factors(
            data_client=self.trading_data_client_v2, market_id=market_id
        )

    def estimate_position(
        self,
        market_id: str,
        open_volume: float,
        side: List[str] = None,
        price: List[float] = None,
        remaining: List[float] = None,
        is_market_order: List[bool] = None,
        collateral_available: float = None,
    ) -> Tuple[data.MarginEstimate, data.LiquidationEstimate]:
        """
        Estimates the best and worst case margin requirements and liquidation prices.

        For a given market, position size, and optional list of open orders; method
        will return a best-case and worst-case estimate for the margin requirements. If
        the optional collateral_available field is specified, the method will also
        return a best-case and worst-case estimate for the liquidation price.

        Args:
            self: The object instance.
            market_id (str): The ID of the market.
            open_volume (float): The open volume to estimate the position for.
            side (List[str], optional): List of order sides. Defaults to None.
            price (List[float], optional): List of order prices. Defaults to None.
            remaining (List[float], optional): List of order sizes. Defaults to None.
            is_market_order (List[bool], optional): List of flags defining whether an
                order is a market order. Defaults to None.
            collateral_available (float, optional): The amount of available collateral.
                Defaults to None.

        Returns:
            Tuple[data.MarginEstimate, data.LiquidationEstimate]: A tuple containing a
                MarginEstimate dataclass and a LiquidationEstimate dataclass. If no
                available collateral was specified the LiquidationEstimate fields will
                all be zero.

        Raises:
            ValueError: If any of the order info fields are given, all order info fields
                must be given.
        """

        # If any order info field is given, all order info fields must be given
        if any([field is not None for field in [price, remaining, is_market_order]]):
            if any([field is None for field in [price, remaining, is_market_order]]):
                raise ValueError(
                    "All order info fields must be given if at least one is given"
                )
            # No exception so handle conversion
            padded_int_prices = [
                str(
                    num_to_padded_int(
                        individual_price, self.market_price_decimals[market_id]
                    )
                )
                for individual_price in price
            ]
            padded_int_remaining = [
                num_to_padded_int(
                    individual_remaining, self.market_price_decimals[market_id]
                )
                for individual_remaining in remaining
            ]
            enum_side = [
                get_enum(individual_side, vega_protos.vega.Side)
                for individual_side in side
            ]
            orders = list(
                zip(enum_side, padded_int_prices, padded_int_remaining, is_market_order)
            )
        else:
            orders = None

        return data.estimate_position(
            data_client=self.trading_data_client_v2,
            market_id=market_id,
            open_volume=num_to_padded_int(
                open_volume, decimals=self.market_pos_decimals[market_id]
            ),
            orders=orders,
            collateral_available=(
                str(
                    num_to_padded_int(
                        collateral_available,
                        self.asset_decimals[self.market_to_asset[market_id]],
                    )
                )
                if collateral_available is not None
                else None
            ),
            asset_decimals=self.asset_decimals,
        )

    def get_stake(
        self,
        party_id: Optional[str] = None,
    ):
        asset_id = self.find_asset_id(symbol=self.governance_symbol)
        return data.get_stake(
            data_client=self.trading_data_client_v2,
            party_id=party_id,
            asset_decimals=self.asset_decimals[asset_id],
        )

    def get_asset(self, asset_id: str):
        return data.get_asset(
            data_client=self.trading_data_client_v2, asset_id=asset_id
        )

    def list_all_network_history_segments(self):
        return data_raw.list_all_network_history_segments(
            data_client=self.trading_data_client_v2
        )

    def statistics(self) -> vega_protos.api.v1.core.Statistics:
        return statistics(core_data_client=self.core_client)

    def list_assets(self):
        return self.data_cache._asset_from_feed.values()

    def stake(self, **kwargs):
        pass

    def update_referral_program(
        self,
        proposal_key: str,
        benefit_tiers: Optional[list[dict]] = None,
        staking_tiers: Optional[list[dict]] = None,
        end_of_program_timestamp: Optional[int] = None,
        window_length: Optional[int] = None,
        wallet_name: Optional[str] = None,
        vote_closing_time: Optional[int] = None,
        vote_enactment_time: Optional[int] = None,
        approve_proposal: bool = True,
        forward_time_to_enactment: bool = True,
    ):
        blockchain_time_seconds = self.get_blockchain_time(in_seconds=True)
        closing_time = (
            blockchain_time_seconds + self.seconds_per_block * 40
            if vote_closing_time is None
            else int(vote_closing_time.timestamp())
        )
        enactment_time = (
            blockchain_time_seconds + self.seconds_per_block * 50
            if vote_enactment_time is None
            else int(vote_enactment_time.timestamp())
        )
        end_of_program_timestamp = (
            enactment_time + self.seconds_per_block * 60 * 60 * 24 * 7 * 52
            if end_of_program_timestamp is None
            else int(end_of_program_timestamp.timestamp())
        )
        proposal_id = gov.update_referral_program(
            key_name=proposal_key,
            wallet=self.wallet,
            data_client=self.trading_data_client_v2,
            benefit_tiers=benefit_tiers,
            staking_tiers=staking_tiers,
            end_of_program_timestamp=end_of_program_timestamp,
            window_length=window_length,
            wallet_name=wallet_name,
            closing_time=closing_time,
            enactment_time=enactment_time,
            time_forward_fn=lambda: self.wait_fn(2),
        )
        if approve_proposal:
            gov.approve_proposal(
                proposal_id=proposal_id,
                wallet=self.wallet,
                wallet_name=wallet_name,
                key_name=proposal_key,
            )

        if forward_time_to_enactment:
            time_to_enactment = enactment_time - self.get_blockchain_time(
                in_seconds=True
            )
            self.wait_fn(int(time_to_enactment / self.seconds_per_block) + 1)
        self.wait_for_thread_catchup()
        return proposal_id

    def create_referral_set(
        self,
        key_name: str,
        name: Optional[str] = None,
        team_url: Optional[str] = None,
        avatar_url: Optional[str] = None,
        closed: Optional[bool] = None,
        wallet_name: Optional[str] = None,
    ):
        trading.create_referral_set(
            wallet=self.wallet,
            key_name=key_name,
            wallet_name=wallet_name,
            name=name,
            team_url=team_url,
            avatar_url=avatar_url,
            closed=closed,
        )

    def update_referral_set(
        self,
        key_name: str,
        name: Optional[str] = None,
        team_url: Optional[str] = None,
        avatar_url: Optional[str] = None,
        closed: Optional[bool] = None,
        wallet_name: Optional[str] = None,
    ):
        trading.update_referral_set(
            wallet=self.wallet,
            key_name=key_name,
            wallet_name=wallet_name,
            name=name,
            team_url=team_url,
            avatar_url=avatar_url,
            closed=closed,
        )

    def apply_referral_code(
        self, key_name: str, id: str, wallet_name: Optional[str] = None
    ):
        trading.apply_referral_code(
            wallet=self.wallet, key_name=key_name, id=id, wallet_name=wallet_name
        )

    def list_referral_sets(
        self,
        referral_set_id: Optional[str] = None,
        referrer: Optional[str] = None,
        referee: Optional[str] = None,
    ) -> Dict[str : data.ReferralSet]:
        return data.list_referral_sets(
            data_client=self.trading_data_client_v2,
            referral_set_id=referral_set_id,
            referrer=referrer,
            referee=referee,
        )

    def list_referral_set_referees(
        self,
        referral_set_id: Optional[str] = None,
        referrer: Optional[str] = None,
        referee: Optional[str] = None,
    ) -> Dict[str : data.ReferralSetReferee]:
        return data.list_referral_set_referees(
            data_client=self.trading_data_client_v2,
            referral_set_id=referral_set_id,
            referrer=referrer,
            referee=referee,
        )

    def get_current_referral_program(
        self,
    ) -> data.ReferralProgram:
        return data.get_current_referral_program(
            data_client=self.trading_data_client_v2
        )

    def get_referral_set_stats(
        self,
        at_epoch: Optional[int] = None,
        key_name: Optional[str] = None,
        wallet_name: Optional[str] = None,
    ) -> List[data.ReferralSetStats]:
        return data.get_referral_set_stats(
            data_client=self.trading_data_client_v2,
            at_epoch=at_epoch,
            referee=self.wallet.public_key(name=key_name, wallet_name=wallet_name),
        )

    def get_fees_stats(
        self,
        market_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        epoch_seq: Optional[int] = None,
        key_name: Optional[str] = None,
        wallet_name: Optional[str] = None,
    ) -> List[data.FeesStats]:
        return data.get_fees_stats(
            data_client=self.trading_data_client_v2,
            market_id=market_id,
            asset_id=asset_id,
            epoch_seq=epoch_seq,
            party_id=(
                self.wallet.public_key(key_name, wallet_name)
                if key_name is not None
                else None
            ),
            asset_decimals=self.asset_decimals,
        )

    def update_volume_discount_program(
        self,
        proposal_key: str,
        benefit_tiers: Optional[list[dict]] = None,
        end_of_program_timestamp: Optional[int] = None,
        window_length: Optional[int] = None,
        wallet_name: Optional[str] = None,
        vote_closing_time: Optional[int] = None,
        vote_enactment_time: Optional[int] = None,
        approve_proposal: bool = True,
        forward_time_to_enactment: bool = True,
    ):
        blockchain_time_seconds = self.get_blockchain_time(in_seconds=True)
        closing_time = (
            blockchain_time_seconds + self.seconds_per_block * 40
            if vote_closing_time is None
            else int(vote_closing_time.timestamp())
        )
        enactment_time = (
            blockchain_time_seconds + self.seconds_per_block * 50
            if vote_enactment_time is None
            else int(vote_enactment_time.timestamp())
        )
        end_of_program_timestamp = (
            enactment_time + self.seconds_per_block * 60 * 60 * 24 * 7 * 52
            if end_of_program_timestamp is None
            else int(end_of_program_timestamp.timestamp())
        )
        proposal_id = gov.update_volume_discount_program(
            key_name=proposal_key,
            wallet=self.wallet,
            data_client=self.trading_data_client_v2,
            benefit_tiers=benefit_tiers,
            end_of_program_timestamp=end_of_program_timestamp,
            window_length=window_length,
            wallet_name=wallet_name,
            closing_time=closing_time,
            enactment_time=enactment_time,
            time_forward_fn=lambda: self.wait_fn(2),
        )
        if approve_proposal:
            gov.approve_proposal(
                proposal_id=proposal_id,
                wallet=self.wallet,
                wallet_name=wallet_name,
                key_name=proposal_key,
            )

        if forward_time_to_enactment:
            time_to_enactment = enactment_time - self.get_blockchain_time(
                in_seconds=True
            )
            self.wait_fn(int(time_to_enactment / self.seconds_per_block) + 1)
        self.wait_for_thread_catchup()
        return proposal_id

    def get_current_volume_discount_program(
        self,
    ) -> data.VolumeDiscountProgram:
        return data.get_current_volume_discount_program(
            data_client=self.trading_data_client_v2
        )

    def get_volume_discount_stats(
        self,
        at_epoch: Optional[str] = None,
        key_name: Optional[str] = None,
        wallet_name: Optional[str] = None,
    ) -> List[data.VolumeDiscountStats]:
        return data.get_volume_discount_stats(
            data_client=self.trading_data_client_v2,
            at_epoch=at_epoch,
            party_id=self.wallet.public_key(name=key_name, wallet_name=wallet_name),
        )

    def list_teams(
        self,
        key_name: Optional[str] = None,
        wallet_name: Optional[str] = None,
        team_id: Optional[str] = None,
    ) -> List[data.Team]:
        return data.list_teams(
            data_client=self.trading_data_client_v2,
            team_id=team_id,
            party_id=(
                None
                if key_name is None
                else self.wallet.public_key(name=key_name, wallet_name=wallet_name)
            ),
        )

    def list_team_referees(
        self,
        team_id: Optional[str] = None,
    ) -> List[data.TeamReferee]:
        return data.list_team_referees(
            data_client=self.trading_data_client_v2, team_id=team_id
        )

    def list_team_referee_history(
        self,
        key_name: str,
        wallet_name: Optional[str] = None,
    ) -> List[data.TeamRefereeHistory]:
        return data.list_team_referee_history(
            data_client=self.trading_data_client_v2,
            referee=self.wallet.public_key(name=key_name, wallet_name=wallet_name),
        )

    def submit_stop_order(
        self,
        stop_orders_submission: StopOrdersSubmission,
        key_name: str,
        wallet_name: Optional[str] = None,
    ):
        trading.submit_stop_orders(
            wallet=self.wallet,
            stop_orders_submission=stop_orders_submission,
            key_name=key_name,
            wallet_name=wallet_name,
        )

    def list_stop_orders(
        self,
        statuses: Optional[List[vega_protos.vega.StopOrder.Status]] = None,
        expiry_strategies: Optional[
            List[vega_protos.vega.StopOrder.ExpiryStrategies]
        ] = None,
        date_range: Optional[vega_protos.vega.DateRange] = None,
        party_ids: Optional[List[str]] = None,
        market_ids: Optional[List[str]] = None,
        live_only: Optional[bool] = None,
    ):
        return data.list_stop_orders(
            data_client=self.trading_data_client_v2,
            statuses=statuses,
            expiry_strategies=expiry_strategies,
            date_range=date_range,
            party_ids=party_ids,
            market_ids=market_ids,
            live_only=live_only,
            market_price_decimals_map=self.market_price_decimals,
            market_position_decimals_map=self.market_pos_decimals,
        )

    def propose_transfer(
        self,
        key_name: str,
        source_type: vega_protos.vega.AccountType,
        transfer_type: vega_protos.governance.GovernanceTransferType,
        amount: float,
        asset: str,
        fraction_of_balance: float,
        destination_type: vega_protos.vega.AccountType,
        source: Optional[str] = None,
        destination: Optional[str] = None,
        closing_time: Optional[datetime.datetime] = None,
        enactment_time: Optional[datetime.datetime] = None,
        wallet_name: Optional[str] = None,
        approve_proposal: bool = True,
        forward_time_to_enactment: bool = True,
    ):
        """
        Method does not support delayed one off transfers or recurring transfers.
        """
        blockchain_time = self.get_blockchain_time(in_seconds=True)

        if closing_time is None:
            closing_time = datetime.datetime.fromtimestamp(blockchain_time + 50)
        if enactment_time is None:
            enactment_time = datetime.datetime.fromtimestamp(blockchain_time + 60)

        proposal_id = gov.new_transfer(
            asset_decimals=self.asset_decimals,
            source_type=source_type,
            transfer_type=transfer_type,
            amount=amount,
            asset=asset,
            fraction_of_balance=fraction_of_balance,
            destination_type=destination_type,
            source=source,
            destination=destination,
            key_name=key_name,
            wallet=self.wallet,
            data_client=self.trading_data_client_v2,
            wallet_name=wallet_name,
            closing_time=closing_time,
            enactment_time=enactment_time,
            time_forward_fn=lambda: self.wait_fn(2),
        )

        if approve_proposal:
            gov.approve_proposal(
                proposal_id=proposal_id,
                wallet=self.wallet,
                wallet_name=wallet_name,
                key_name=key_name,
            )

        if forward_time_to_enactment:
            time_to_enactment = enactment_time.timestamp() - self.get_blockchain_time(
                in_seconds=True
            )
            self.wait_fn(int(time_to_enactment / self.seconds_per_block) + 1)

        self.wait_for_thread_catchup()
        return proposal_id

    def submit_proposal(
        self,
        key_name: str,
        proposal_submission: vega_protos.commands.v1.commands.ProposalSubmission,
        approve_proposal: Optional[bool] = False,
        enact_proposal: Optional[bool] = False,
        wallet_name: Optional[str] = None,
    ):
        proposal_id = gov.submit_proposal(
            key_name=key_name,
            wallet_name=wallet_name,
            wallet=self.wallet,
            proposal=proposal_submission,
            data_client=self.trading_data_client_v2,
            time_forward_fn=lambda: self.wait_fn((2)),
        )
        if proposal_id is None:
            return

        if approve_proposal:
            gov.approve_proposal(
                proposal_id=proposal_id,
                wallet=self.wallet,
                wallet_name=wallet_name,
                key_name=key_name,
            )

        if enact_proposal:
            time_to_enactment = (
                proposal_submission.terms.enactment_time
                - self.get_blockchain_time(in_seconds=True)
            )
            self.wait_fn(int(time_to_enactment / self.seconds_per_block) + 1)

        self.wait_for_thread_catchup()

    def check_balances_equal_deposits(self, asset: Optional[str] = None):
        accounts = data_raw.list_accounts(
            data_client=self.trading_data_client_v2,
            asset_id=asset,
        )

        class BalanceDepositInequity(Exception):
            def __init__(self, asset, minted, balance):
                super().__init__(
                    f"Funds in accounts ({balance}) do not match deposited/minted funds ({minted}) for asset {asset}"
                )

        asset_balance_map = {key: 0 for key in self.asset_mint_map.keys()}
        for account in accounts:
            asset_balance_map[account.asset] += int(account.balance)

        try:
            for asset in self.asset_mint_map:
                assert self.asset_mint_map[asset] == asset_balance_map[asset]
        except AssertionError:
            raise BalanceDepositInequity(
                asset,
                minted=self.asset_mint_map[asset],
                balance=asset_balance_map[asset],
            )
