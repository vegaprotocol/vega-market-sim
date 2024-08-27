import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import (
    logger,
    tds,
    markets,
    assets,
    parties,
    orders,
    start_timestamp,
    end_timestamp,
)

import vega_protos.protos as protos
import datetime


@pytest.mark.vega_query
def test_list_orders(tds: TradingDataService):
    tds.list_orders(max_pages=1)


@pytest.mark.vega_query
def test_list_orders_statuses(tds: TradingDataService):
    statuses_filter = protos.vega.vega.Order.Status.values()[:2]
    for order in tds.list_orders(statuses=statuses_filter, live_only=True, max_pages=1):
        assert order.status in statuses_filter


@pytest.mark.vega_query
def test_list_orders_types(tds: TradingDataService):
    types_filter = protos.vega.vega.Order.Type.values()[:2]
    for order in tds.list_orders(types=types_filter, live_only=True, max_pages=1):
        assert order.type in types_filter


@pytest.mark.vega_query
def test_list_orders_time_in_forces(tds: TradingDataService):
    time_in_forces_filter = protos.vega.vega.Order.TimeInForce.values()[:2]
    for order in tds.list_orders(
        time_in_forces=time_in_forces_filter, live_only=True, max_pages=1
    ):
        assert order.time_in_force in time_in_forces_filter


@pytest.mark.vega_query
def test_list_orders_exclude_liquidity(tds: TradingDataService):
    for order in tds.list_orders(exclude_liquidity=True, live_only=True, max_pages=1):
        assert order.liquidity_provision_id is not None


@pytest.mark.vega_query
def test_list_orders_party_ids(tds: TradingDataService, parties):
    party_ids_filter = parties[:2]
    for order in tds.list_orders(
        party_ids=party_ids_filter, live_only=True, max_pages=1
    ):
        assert order.party_id in party_ids_filter


@pytest.mark.vega_query
def test_list_orders_reference(tds: TradingDataService, orders):
    reference_filter = orders[0].reference
    for order in tds.list_orders(reference=reference_filter, max_pages=1):
        assert order.reference == reference_filter


@pytest.mark.vega_query
def test_list_orders_start_timestamp(tds: TradingDataService, start_timestamp):
    for order in tds.list_orders(
        start_timestamp=start_timestamp, live_only=True, max_pages=1
    ):
        assert max(order.created_at, order.updated_at) > start_timestamp


@pytest.mark.vega_query
def test_list_orders_end_timestamp(tds: TradingDataService, end_timestamp):
    for order in tds.list_orders(
        end_timestamp=end_timestamp, live_only=True, max_pages=1
    ):
        assert max(order.created_at, order.updated_at) < end_timestamp


@pytest.mark.vega_query
def test_list_orders_live_only(tds: TradingDataService):
    for order in tds.list_orders(live_only=True, max_pages=1):
        assert order.status in [
            protos.vega.vega.Order.Status.STATUS_PARKED,
            protos.vega.vega.Order.Status.STATUS_ACTIVE,
            protos.vega.vega.Order.Status.STATUS_PARTIALLY_FILLED,
        ]
