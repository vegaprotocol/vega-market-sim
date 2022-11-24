import pytest

from vega_sim.quant.quant import probability_of_trading

import vega_sim.proto.vega as vega_protos


def test_probability_of_trading_for_buy_order_below_min_valid_price():

    result = probability_of_trading(
        price=1030,
        side=vega_protos.vega.SIDE_BUY,
        best_bid_price=1045,
        best_ask_price=1055,
        min_valid_price=1035,
        max_valid_price=1175,
        mu=0,
        tau=1 / 365.25,
        sigma=1.2,
        min_probability_of_trading=0.001,
    )

    assert result == 0.001


def test_probability_of_trading_for_buy_order_at_min_valid_price():

    # Test at limit
    result = probability_of_trading(
        price=1035,
        side=vega_protos.vega.SIDE_BUY,
        best_bid_price=1045,
        best_ask_price=1055,
        min_valid_price=1035,
        max_valid_price=1175,
        mu=0,
        tau=1 / 365.25,
        sigma=1.2,
        min_probability_of_trading=0.001,
    )

    assert result == 0.001


def test_probability_of_trading_for_buy_order_at_best_bid_price():

    result = probability_of_trading(
        price=1045,
        side=vega_protos.vega.SIDE_BUY,
        best_bid_price=1045,
        best_ask_price=1055,
        min_valid_price=1035,
        max_valid_price=1175,
        mu=0,
        tau=1 / 365.25,
        sigma=1.2,
        min_probability_of_trading=0.001,
    )

    assert result == 0.5


def test_probability_of_trading_for_buy_order_above_best_bid_price():

    result = probability_of_trading(
        price=1050,
        side=vega_protos.vega.SIDE_SELL,
        best_bid_price=1045,
        best_ask_price=1055,
        min_valid_price=1035,
        max_valid_price=1175,
        mu=0,
        tau=1 / 365.25,
        sigma=1.2,
        min_probability_of_trading=0.001,
    )

    assert result == 0.5


def test_probability_of_trading_for_sell_order_above_best_ask_price():

    result = probability_of_trading(
        price=1050,
        side=vega_protos.vega.SIDE_SELL,
        best_bid_price=1045,
        best_ask_price=1055,
        min_valid_price=1035,
        max_valid_price=1175,
        mu=0,
        tau=1 / 365.25,
        sigma=1.2,
        min_probability_of_trading=0.001,
    )

    assert result == 0.5


def test_probability_of_trading_for_sell_order_at_best_ask_price():

    result = probability_of_trading(
        price=1055,
        side=vega_protos.vega.SIDE_SELL,
        best_bid_price=1045,
        best_ask_price=1055,
        min_valid_price=1035,
        max_valid_price=1175,
        mu=0,
        tau=1 / 365.25,
        sigma=1.2,
        min_probability_of_trading=0.001,
    )

    assert result == 0.5


def test_probability_of_trading_for_sell_order_at_max_valid_price():

    result = probability_of_trading(
        price=1175,
        side=vega_protos.vega.SIDE_SELL,
        best_bid_price=1045,
        best_ask_price=1055,
        min_valid_price=1035,
        max_valid_price=1175,
        mu=0,
        tau=1 / 365.25,
        sigma=1.2,
        min_probability_of_trading=0.001,
    )

    assert result == 0.001


def test_probability_of_trading_for_sell_order_above_max_valid_price():

    result = probability_of_trading(
        price=1180,
        side=vega_protos.vega.SIDE_SELL,
        best_bid_price=1045,
        best_ask_price=1055,
        min_valid_price=1035,
        max_valid_price=1175,
        mu=0,
        tau=1 / 365.25,
        sigma=1.2,
        min_probability_of_trading=0.001,
    )

    assert result == 0.001
