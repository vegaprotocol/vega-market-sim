import pytest

from vega_sim.api.market import MarketConfig


@pytest.mark.api
def test_market_config_instrument():

    config = MarketConfig()
    assert not config.is_future()
    assert not config.is_perp()

    config = MarketConfig("future")
    assert config.is_future()
    assert not config.is_perp()

    config = MarketConfig("perpetual")
    assert not config.is_future()
    assert config.is_perp()
