"""Module contains tests for testing coverage of vega APIs.
"""

import pytest
import re

import vega_python_protos.protos.data_node.api.v2 as data_node_protos_v2
import vega_python_protos.protos.vega as vega_protos
import vega_sim.api.data as data
import vega_sim.api.data_raw as data_raw


def camel_to_snake(camel_case):
    # Use regular expression to split words at capital letters
    words = re.findall("[A-Z][a-z]*", camel_case)
    # Join the words with underscores and convert to lowercase
    snake_case = "_".join(word.lower() for word in words)
    return snake_case


@pytest.mark.api
@pytest.mark.parametrize(
    "item_name",
    [
        item_name
        for item_name in dir(vega_protos.vega)
        if hasattr(getattr(vega_protos.vega, item_name), "DESCRIPTOR")
        and hasattr(getattr(vega_protos.vega, item_name), "SerializeToString")
    ],
)
def test_vega_protos(item_name):
    assert hasattr(data, item_name)


@pytest.mark.api
@pytest.mark.parametrize(
    "item_name",
    [
        item_name
        for item_name in dir(vega_protos.events.v1.events)
        if hasattr(getattr(vega_protos.events.v1.events, item_name), "DESCRIPTOR")
        and hasattr(
            getattr(vega_protos.events.v1.events, item_name), "SerializeToString"
        )
    ],
)
def test_events_protos(item_name):
    assert hasattr(data, item_name)


@pytest.mark.api
@pytest.mark.parametrize(
    "item_name",
    [
        item_name
        for item_name in dir(vega_protos.assets)
        if hasattr(getattr(vega_protos.assets, item_name), "DESCRIPTOR")
        and hasattr(getattr(vega_protos.assets, item_name), "SerializeToString")
    ],
)
def test_assets_protos(item_name):
    assert hasattr(data, item_name)


@pytest.mark.api
@pytest.mark.parametrize(
    "item_name",
    [
        method.name
        for method in data_node_protos_v2.trading_data.DESCRIPTOR.services_by_name[
            "TradingDataService"
        ].methods
    ],
)
def test_trading_data(item_name):
    assert hasattr(data_raw, camel_to_snake(item_name))
