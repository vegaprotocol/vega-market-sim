from __future__ import annotations

import copy
import grpc
import logging
import threading
import traceback
from collections import defaultdict
from itertools import chain, product
from queue import Empty, Queue
from types import GeneratorType
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import vega_sim.api.data as data
import vega_sim.api.data_raw as data_raw
import vega_sim.api.governance as gov
import vega_sim.grpc.client as vac
import vega_protos.protos.vega as vega_protos
import vega_protos.protos.vega.events.v1.events_pb2 as events_protos
from vega_sim.tools.retry import retry

logger = logging.getLogger(__name__)


def _queue_forwarder(
    data_client: vac.VegaCoreClient,
    stream_registry: List[
        Tuple[
            Any,
            Callable[
                [
                    vega_protos.api.v1.core.ObserveEventBusResponse,
                    vac.VegaTradingDataClientV2,
                ],
                Any,
            ],
        ]
    ],
    sink: Queue[Any],
    market_id: Optional[str] = None,
    party_id: Optional[str] = None,
    kill_thread_sig: Optional[threading.Event()] = None,
) -> None:
    obs = data_raw.observe_event_bus(
        data_client=data_client,
        type=list(chain(*[ev[0] for ev in stream_registry])),
        market_id=market_id,
        party_id=party_id,
    )

    handlers = {}
    for evts, handler in stream_registry:
        for evt in evts:
            handlers[evt] = handler
    try:
        for o in obs:
            for event in o.events:
                if (kill_thread_sig is not None) and kill_thread_sig.is_set():
                    return
                output = retry(5, 1.0, lambda: handlers[event.type](event))
                if isinstance(output, (list, GeneratorType)):
                    for elem in output:
                        sink.put(elem)
                else:
                    sink.put(output)
    except grpc._channel._MultiThreadedRendezvous as e:
        if e.details() in ["Channel closed!", "Socket closed"]:
            logging.debug(f"Thread finished as {e.details}")
            logger.info("Data cache event bus closed.")
        else:
            raise e


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
        market_pos_decimals: Optional[Dict[str, int]] = None,
        market_price_decimals: Optional[Dict[str, int]] = None,
        asset_decimals: Optional[Dict[str, int]] = None,
        market_to_asset: Optional[Dict[str, str]] = None,
        market_to_settlement_asset: Optional[Dict[str, str]] = None,
        market_to_base_asset: Optional[Dict[str, str]] = None,
        market_to_quote_asset: Optional[Dict[str, str]] = None,
    ):
        """ """
        self._trading_data_client = trading_data_client
        self._event_bus_client = event_bus_client

        self._market_price_decimals = market_price_decimals
        self._market_pos_decimals = market_pos_decimals
        self._asset_decimals = asset_decimals
        self._market_to_asset = market_to_asset
        self._market_to_settlement_asset = market_to_settlement_asset
        self._market_to_base_asset = market_to_base_asset
        self._market_to_quote_asset = market_to_quote_asset

        self.time_update_lock = threading.RLock()
        self.orders_lock = threading.RLock()
        self.transfers_lock = threading.RLock()
        self.asset_lock = threading.RLock()
        self.account_lock = threading.RLock()
        self.market_lock = threading.RLock()
        self.market_data_lock = threading.RLock()
        self.trades_lock = threading.RLock()
        self.ledger_entries_lock = threading.RLock()
        self.network_parameter_lock = threading.RLock()
        self._time_update_from_feed = 0
        self._live_order_state_from_feed = {}
        self._dead_order_state_from_feed = {}
        self._asset_from_feed = {}
        self._market_from_feed = {}
        self.market_data_from_feed_store = {}
        self._transfer_state_from_feed = {}
        self._accounts_from_feed = {}
        self._account_keys_for_party = {}
        self._account_keys_for_market = {}
        self._trades_from_feed: List[data.Trade] = []
        self._ledger_entries_from_feed: List[data.LedgerEntry] = []
        self._network_parameter_from_feed: Dict[str, data.NetworkParameter] = {}

        self._observation_thread = None
        self._aggregated_observation_feed: Queue[Any] = Queue()
        self._kill_thread_sig = threading.Event()

        self.stream_registry = [
            (
                (events_protos.BUS_EVENT_TYPE_TIME_UPDATE,),
                lambda evt: evt.time_update,
            ),
            (
                (events_protos.BUS_EVENT_TYPE_TRADE,),
                lambda evt: data.trades_subscription_handler(
                    evt,
                    self._market_pos_decimals,
                    self._market_price_decimals,
                    self._market_to_asset,
                    self._asset_decimals,
                ),
            ),
            (
                (events_protos.BUS_EVENT_TYPE_ASSET,),
                lambda evt: evt.asset,
            ),
            (
                (events_protos.BUS_EVENT_TYPE_MARKET_CREATED,),
                lambda evt: evt.market_created,
            ),
            (
                (events_protos.BUS_EVENT_TYPE_ORDER,),
                lambda evt: data.order_subscription_handler(
                    evt,
                    self._market_pos_decimals,
                    self._market_price_decimals,
                    self._market_to_asset,
                    self._asset_decimals,
                ),
            ),
            (
                (events_protos.BUS_EVENT_TYPE_MARKET_DATA,),
                lambda evt: data.market_data_subscription_handler(
                    evt,
                    self._market_pos_decimals,
                    self._market_price_decimals,
                    self._market_to_asset,
                    self._asset_decimals,
                ),
            ),
            (
                (events_protos.BUS_EVENT_TYPE_ACCOUNT,),
                lambda evt: data.accounts_subscription_handler(
                    evt,
                    self._market_pos_decimals,
                    self._market_price_decimals,
                    self._market_to_asset,
                    self._asset_decimals,
                ),
            ),
            (
                (events_protos.BUS_EVENT_TYPE_NETWORK_PARAMETER,),
                lambda evt: data._network_parameter_from_proto(
                    evt.network_parameter,
                ),
            ),
        ]
        self._high_load_stream_registry = [
            (
                (events_protos.BUS_EVENT_TYPE_LEDGER_MOVEMENTS,),
                lambda evt: data.ledger_entries_subscription_handler(
                    evt, self._asset_decimals
                ),
            ),
            (
                (events_protos.BUS_EVENT_TYPE_TRANSFER,),
                lambda evt: data.transfer_subscription_handler(
                    evt,
                    self._market_pos_decimals,
                    self._market_price_decimals,
                    self._market_to_asset,
                    self._asset_decimals,
                ),
            ),
        ]

    def stop(self) -> None:
        self._kill_thread_sig.set()
        self._observation_thread.join()
        self._forwarding_thread.join()

    def time_update_from_feed(
        self,
    ) -> int:
        return self._time_update_from_feed

    def asset_from_feed(
        self,
        asset_id: str,
    ) -> vega_protos.assets.Asset:
        if asset_id not in self._asset_from_feed:
            self.initialise_assets()
        return self._asset_from_feed[asset_id]

    def market_from_feed(
        self,
        market_id: str,
    ) -> vega_protos.markets.Market:
        if market_id not in self._market_from_feed:
            self.initialise_markets()
        return self._market_from_feed[market_id]

    def market_data_from_feed(
        self,
        market_id: str,
    ) -> vega_protos.vega.MarketData:
        """
        Output market info.
        """
        return self.market_data_from_feed_store[market_id]

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

    def network_parameter_from_feed(
        self,
        key: str,
    ) -> data.NetworkParameter:
        if key not in self._network_parameter_from_feed:
            self.initialise_network_parameters()
        return self._network_parameter_from_feed[key]

    def start_live_feeds(
        self,
        market_ids: Optional[Union[str, List[str]]] = None,
        party_ids: Optional[Union[str, List[str]]] = None,
        start_high_load_feeds: bool = False,
    ):
        market_ids = (
            (market_ids if isinstance(market_ids, list) else [market_ids])
            if market_ids is not None
            else None
        )
        party_ids = (
            (party_ids if isinstance(party_ids, list) else [party_ids])
            if party_ids is not None
            else None
        )
        self.initialise_assets()
        self.initialise_markets()
        self.initialise_accounts()
        self.initialise_time_update_monitoring()
        self.initialise_order_monitoring(
            market_ids=market_ids,
            party_ids=party_ids,
        )
        self.initialise_transfer_monitoring()
        self.initialise_market_data(
            market_ids,
        )
        self.initialise_network_parameters()

        self._observation_thread = threading.Thread(
            target=self._monitor_stream, daemon=True
        )
        self._observation_thread.start()

        self._forwarding_thread = threading.Thread(
            target=_queue_forwarder,
            args=(
                self._event_bus_client,
                self.stream_registry
                + (self._high_load_stream_registry if start_high_load_feeds else []),
                self._aggregated_observation_feed,
                (
                    (market_ids[0] if len(market_ids) == 1 else None)
                    if market_ids is not None
                    else None
                ),
                (
                    (party_ids[0] if len(party_ids) == 1 else None)
                    if party_ids is not None
                    else None
                ),
                self._kill_thread_sig,
            ),
            daemon=True,
        )
        self._forwarding_thread.start()

    def initialise_assets(self):
        base_assets = data_raw.list_assets(data_client=self._trading_data_client)

        with self.asset_lock:
            for asset in base_assets:
                self._asset_from_feed[asset.id] = asset

    def initialise_accounts(self):
        base_accounts = data.list_accounts(data_client=self._trading_data_client)

        with self.account_lock:
            for account in base_accounts:
                self._accounts_from_feed[account.account_id] = account
                self._account_keys_for_party.setdefault(account.owner, set()).add(
                    account.account_id
                )
                self._account_keys_for_market.setdefault(account.market_id, set()).add(
                    account.account_id
                )

    def initialise_markets(self):
        base_markets = data_raw.all_markets(self._trading_data_client)

        with self.market_lock:
            for market in base_markets:
                self._market_from_feed[market.id] = market

    def initialise_time_update_monitoring(self):
        base_time_update = gov.get_blockchain_time(
            data_client=self._trading_data_client
        )
        with self.time_update_lock:
            self._time_update_from_feed = base_time_update

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
                    price_decimals=(
                        self._market_price_decimals[market_party_tuple[0]]
                        if market_party_tuple[0] is not None
                        else None
                    ),
                    position_decimals=(
                        self._market_pos_decimals[market_party_tuple[0]]
                        if market_party_tuple[0] is not None
                        else None
                    ),
                )
            )

        with self.orders_lock:
            for order in base_orders:
                self._live_order_state_from_feed.setdefault(
                    order.market_id, {}
                ).setdefault(order.party_id, {})[order.id] = order

    def initialise_market_data(
        self,
        market_ids: Optional[List[str]] = None,
    ):
        if market_ids is None:
            market_ids = [
                market.id for market in data_raw.all_markets(self._trading_data_client)
            ]
        with self.market_data_lock:
            for market_id in market_ids:
                self.market_data_from_feed_store[market_id] = (
                    data.get_latest_market_data(
                        market_id,
                        data_client=self._trading_data_client,
                        market_price_decimals_map=self._market_price_decimals,
                        market_position_decimals_map=self._market_pos_decimals,
                        asset_decimals_map=self._asset_decimals,
                        market_to_asset_map=self._market_to_asset,
                    )
                )

    def initialise_transfer_monitoring(
        self,
    ):
        base_transfers = data.list_transfers(data_client=self._trading_data_client)

        with self.transfers_lock:
            for t in base_transfers:
                if t.status == events_protos.Transfer.Status.STATUS_REJECTED:
                    continue
                self._transfer_state_from_feed.setdefault(t.party_to, {})[t.id] = t

    def initialise_network_parameters(self):
        base_network_parameters = data.list_network_parameters(
            data_client=self._trading_data_client
        )

        with self.transfers_lock:
            for p in base_network_parameters:
                self._network_parameter_from_feed[p.key] = p

    def _monitor_stream(self) -> None:
        while not self._kill_thread_sig.is_set():
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

                elif isinstance(update, data.MarketData):
                    with self.market_data_lock:
                        self.market_data_from_feed_store[update.market_id] = update

                elif isinstance(update, data.LedgerEntry):
                    with self.ledger_entries_lock:
                        self._ledger_entries_from_feed.append(update)

                elif isinstance(update, events_protos.TimeUpdate):
                    with self.time_update_lock:
                        self._time_update_from_feed = int(update.timestamp)

                elif isinstance(update, vega_protos.markets.Market):
                    self._market_from_feed[update.id] = update
                    # Trigger the DecimalCache default factory method by attempting to
                    # get the decimal precision for the market
                    self._market_pos_decimals[update.id]
                    self._market_price_decimals[update.id]
                    self._market_to_asset[update.id]
                    if (
                        update.tradable_instrument.instrument.future
                        != vega_protos.markets.Future()
                        or update.tradable_instrument.instrument.perpetual
                        != vega_protos.markets.Perpetual()
                    ):
                        self._market_to_settlement_asset[update.id]

                    if (
                        update.tradable_instrument.instrument.spot
                        != vega_protos.markets.Spot()
                    ):
                        self._market_to_base_asset[update.id]
                        self._market_to_quote_asset[update.id]

                elif isinstance(update, vega_protos.assets.Asset):
                    self._asset_from_feed[update.id] = update
                    # Trigger the DecimalCache default factory method by attempting to
                    # get the decimal precision for the asset
                    self._asset_decimals[update.id]

                elif isinstance(update, data.AccountData):
                    with self.account_lock:
                        self._accounts_from_feed[update.account_id] = update
                        self._account_keys_for_party.setdefault(
                            update.owner, set()
                        ).add(update.account_id)
                        self._account_keys_for_market.setdefault(
                            update.market_id, set()
                        ).add(update.account_id)

                elif isinstance(update, data.NetworkParameter):
                    with self.network_parameter_lock:
                        self._network_parameter_from_feed[update.key] = update

                elif update is None:
                    logger.debug("Failed to process event into update.")

                else:
                    logger.info(f"Unhandled update {update}")

    def get_ledger_entries_from_stream(
        self,
        party_id_from: Optional[str] = None,
        party_id_to: Optional[str] = None,
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
                party_id_from is not None
                and party_id_from != ledger_entry.from_account.owner
            ):
                continue
            if party_id_to is not None and party_id_to != ledger_entry.to_account.owner:
                continue

            results.append(copy.copy(ledger_entry))

        return results

    def get_trades_from_stream(
        self,
        market_id: Optional[str] = None,
        party_id: Optional[str] = None,
        order_id: Optional[str] = None,
        exclude_trade_ids: Optional[Set[str]] = None,
    ) -> List[data.Trade]:
        """Loads executed trades for a given query of party/market/specific order from
        data node. Converts values to proper decimal output.

        Args:
            market_id:
                optional str, Restrict to trades on a specific market
            party_id:
                optional str, Select only trades with a given id
            order_id:
                optional str, Restrict to trades for a specific order
            exclude_trade_ids:
                optional set[str], Do not return trades with ID in this set

        Returns:
            List[Trade], list of formatted trade objects which match the required
                restrictions.
        """
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

    def get_accounts_from_stream(
        self,
        market_id: Optional[str] = None,
        party_id: Optional[str] = None,
        asset_id: Optional[str] = None,
    ) -> List[data.AccountData]:
        """Loads accounts for either a given party, market or both from stream.

        Args:
            market_id:
                optional str, Restrict to accounts on a specific market
            party_id:
                optional str, Select only accounts with a given party id
            asset_id:
                optional str, Restrict to only accounts for a given asset

        Returns:
            List[AccountData], list of formatted trade objects which match the required
                restrictions.
        """

        with self.account_lock:
            if market_id is None and party_id is None:
                to_check_keys = self._accounts_from_feed.keys()
            else:
                to_check_keys = set()
                if market_id is not None:
                    to_check_keys.update(
                        self._account_keys_for_market.get(market_id, set())
                    )
                if party_id is not None:
                    to_check_keys.update(
                        self._account_keys_for_party.get(party_id, set())
                    )
            results = []
            for key in to_check_keys:
                acct = self._accounts_from_feed[key]
                if party_id is not None and acct.owner != party_id:
                    continue
                if (
                    market_id is not None
                    and acct.market_id != market_id
                    and acct.type != vega_protos.vega.AccountType.ACCOUNT_TYPE_GENERAL
                ):
                    continue
                # TODO: Temporarily remove this to allow from feed to pull all accounts.
                # if market_id is None and acct.market_id != "":
                #     if acct.type == 19:
                #         print("continue 3")
                #     continue
                if asset_id is not None and acct.asset != asset_id:
                    continue
                results.append(acct)

        return results

    def get_all_accounts_from_stream(
        self,
    ) -> List[data.AccountData]:
        """Loads all accounts stored.

        Returns:
            List[AccountData], list of formatted account objects
        """

        with self.account_lock:
            accts = list(self._accounts_from_feed.values())

        return accts
