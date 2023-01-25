from __future__ import annotations

import copy
import datetime
import logging
import threading
import time
from abc import ABC
from collections import defaultdict
from dataclasses import dataclass
from functools import wraps
from queue import Queue, Empty
from itertools import product
from typing import Any, Dict, Generator, List, Optional, Set, Tuple, Union

import grpc

import vega_sim.api.data as data
import vega_sim.api.data_raw as data_raw
import vega_sim.api.faucet as faucet
import vega_sim.api.governance as gov
import vega_sim.api.market as market
import vega_sim.api.trading as trading
import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v2 as data_node_protos_v2
import vega_sim.proto.vega as vega_protos
import vega_sim.proto.vega.data_source_pb2 as data_source_protos
import vega_sim.proto.vega.events.v1.events_pb2 as events_protos
from vega_sim.api.helpers import (
    forward,
    num_to_padded_int,
    wait_for_core_catchup,
    wait_for_datanode_sync,
)
from vega_sim.proto.vega.commands.v1.commands_pb2 import (
    OrderAmendment,
    OrderCancellation,
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


class LocalDataCache:
    def __init__(
        self,
        event_bus_client: Union[vac.VegaTradingDataClientV2, vac.VegaCoreClient],
        trading_data_client: vac.VegaTradingDataClientV2,
    ):
        """ """
        self._core_client = None
        self._core_state_client = None
        self._trading_data_client_v2 = None

        self._market_price_decimals = None
        self._market_pos_decimals = None
        self._asset_decimals = None
        self._market_to_asset = None

        self.orders_lock = threading.RLock()
        self.transfers_lock = threading.RLock()
        self.market_data_lock = threading.RLock()
        self.trades_lock = threading.RLock()
        self.ledger_entries_lock = threading.RLock()
        self._live_order_state_from_feed = {}
        self._dead_order_state_from_feed = {}
        self.market_data_from_feed_store = {}
        self._transfer_state_from_feed = {}
        self._trades_from_feed: List[data.Trade] = []
        self._ledger_entries_from_feed: List[data.LedgerEntry] = []

        self._observation_feeds: List[Queue[Any]] = []
        self._observation_thread = None
        self._aggregated_observation_feed: Queue[Any] = Queue()
        self._kill_thread_sig = threading.Event()

        self._event_bus_client = event_bus_client
        self._trading_data_client = trading_data_client

        self.stream_registry = [
            (
                (events_protos.BUS_EVENT_TYPE_LEDGER_MOVEMENTS,),
                data.ledger_entries_subscription_handler,
            ),
            (
                (events_protos.BUS_EVENT_TYPE_TRADE,),
                data.trades_subscription_handler,
            ),
            (
                (events_protos.BUS_EVENT_TYPE_ORDER,),
                data.order_subscription_handler,
            ),
            (
                (events_protos.BUS_EVENT_TYPE_TRANSFER,),
                data.transfer_subscription_handler,
            ),
        ]

    def stop(self) -> None:
        self._kill_thread_sig.set()

    @raw_data
    def market_data_from_feed(
        self,
        market_id: str,
    ) -> vega_protos.vega.MarketData:
        """
        Output market info.
        """
        return self.market_data_from_feed_store.get(market_id, None)

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
            order_dict = copy.copy(self._live_order_state_from_feed)
            if not live_only:
                order_dict.update(self._dead_order_state_from_feed)
        return order_dict

    def orders_for_party_from_feed(
        self,
        party_id: str,
        market_id: str,
        live_only: bool = True,
    ) -> Dict[str, data.Order]:
        return (
            self.order_status_from_feed(live_only=live_only)
            .get(market_id, {})
            .get(party_id, {})
        )

    def transfer_status_from_feed(
        self, live_only: bool = True, blockchain_time: Optional[int] = None
    ):
        with self.transfers_lock:
            transfers_dict = {}
            for party_id, party_transfers in self._transfer_state_from_feed.items():
                for transfer_id, transfer in party_transfers.items():
                    deliver_on = int(transfer.one_off.deliver_on)
                    if not live_only or (
                        deliver_on != 0 and blockchain_time < deliver_on
                    ):
                        transfers_dict.setdefault(party_id, {})[transfer_id] = transfer
        return transfers_dict

    def start_live_feeds(self):
        self._observation_thread = threading.Thread(target=self._monitor_stream)
        self._observation_thread.start()

    def initialise_order_monitoring(
        self,
        market_ids: Optional[List[str]] = None,
        party_ids: Optional[List[str]] = None,
    ):
        base_orders = []
        for market_party_tuple in list(
            product(
                (market_ids if market_ids is not None else [None]),
                (party_ids if party_ids is not None else [None]),
            )
        ):
            base_orders.extend(
                data.list_orders(
                    data_client=self._trading_data_client,
                    market_id=market_party_tuple[0],
                    party_id=market_party_tuple[1],
                    live_only=True,
                )
            )

        with self.orders_lock:
            for order in base_orders:
                self._live_order_state_from_feed.setdefault(
                    order.market_id, {}
                ).setdefault(order.party_id, {})[order.id] = order

    def initialise_transfer_monitoring(
        self,
    ):
        base_transfers = []

        base_transfers.extend(
            data.list_transfers(data_client=self._trading_data_client)
        )

        with self.transfers_lock:
            for t in base_transfers:
                self._transfer_state_from_feed.setdefault(t.party_to, {})[t.id] = t

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
                            self._live_order_state_from_feed.setdefault(
                                update.market_id, {}
                            )
                            .setdefault(update.party_id, {})
                            .get(update.id, None),
                            "version",
                            0,
                        ):
                            if (
                                not update.status
                                == vega_protos.vega.Order.Status.STATUS_ACTIVE
                            ):
                                # If the order is dead, pop any we've seen from
                                # live state
                                self._live_order_state_from_feed[update.market_id][
                                    update.party_id
                                ].pop(update.id, None)

                                # And add to dead instead
                                self._dead_order_state_from_feed.setdefault(
                                    update.market_id, {}
                                ).setdefault(update.party_id, {})[update.id] = update
                            else:
                                self._live_order_state_from_feed[update.market_id][
                                    update.party_id
                                ][update.id] = update

                elif isinstance(update, data.Transfer):
                    with self.transfers_lock:
                        self._transfer_state_from_feed.setdefault(update.party_to, {})[
                            update.id
                        ] = update

                elif isinstance(update, data.Trade):
                    with self.trades_lock:
                        self._trades_from_feed.append(update)

                elif isinstance(update, vega_protos.vega.MarketData):
                    with self.market_data_lock:
                        self.market_data_from_feed_store[update.market] = update

                elif isinstance(update, data.LedgerEntry):
                    with self.ledger_entries_lock:
                        self._ledger_entries_from_feed.append(update)

    def get_ledger_entries_from_stream(
        self,
        wallet_name_from: Optional[str] = None,
        key_name_from: Optional[str] = None,
        wallet_name_to: Optional[str] = None,
        key_name_to: Optional[str] = None,
        transfer_type: Optional[str] = None,
    ) -> List[data.LedgerEntry]:
        results = []

        for ledger_entry in self._ledger_entries_from_feed:
            if (
                transfer_type is not None
                and transfer_type != ledger_entry.transfer_type
            ):
                continue
            if (
                wallet_name_from is not None
                and self.wallet.public_key(
                    name=wallet_name_from, key_name=key_name_from
                )
                != ledger_entry.from_account.owner
            ):
                continue
            if (
                wallet_name_to is not None
                and self.wallet.public_key(name=wallet_name_to, key_name=key_name_to)
                != ledger_entry.to_account.owner
            ):
                continue

            results.append(copy.copy(ledger_entry))

        return results

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
                if exclude_trade_ids is not None and trade.id in exclude_trade_ids:
                    continue
                results.append(trade)
        return results
