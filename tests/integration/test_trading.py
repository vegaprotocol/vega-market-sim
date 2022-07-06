import pytest

from tests.integration.utils.fixtures import (
    vega_service_with_market,
    vega_service,
    create_and_faucet_wallet,
    WalletConfig,
)
from vega_sim.null_service import VegaServiceNull
import vega_sim.proto.vega as vega_protos


LIQ = WalletConfig("liq", "liq")


@pytest.mark.integration
def test_submit_amend_liquidity(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    market_id = vega.all_markets()[0].id

    vega.wait_for_total_catchup()

    create_and_faucet_wallet(vega=vega, wallet=LIQ)
    vega.wait_fn(10)
    vega.wait_for_total_catchup()
    vega.submit_liquidity(
        LIQ.name,
        market_id=market_id,
        commitment_amount=100,
        fee=0.001,
        buy_specs=[("PEGGED_REFERENCE_MID", 0.5, 1)],
        sell_specs=[("PEGGED_REFERENCE_MID", 0.5, 1)],
        is_amendment=False,
    )
    vega.wait_fn(10)
    vega.wait_for_total_catchup()

    liq_provis = vega.party_liquidity_provisions(LIQ.name, market_id=market_id)

    assert len(liq_provis) == 1
    for provis in [
        liq_provis[0].sells[0].liquidity_order,
        liq_provis[0].buys[0].liquidity_order,
    ]:
        assert provis.reference == vega_protos.vega.PeggedReference.PEGGED_REFERENCE_MID
        assert provis.offset == "50000"
        assert provis.proportion == 1

    buy_specs = [
        vega_protos.vega.LiquidityOrder(
            reference=vega_protos.vega.PeggedReference.PEGGED_REFERENCE_MID,
            offset="100000",
            proportion=2,
        ),
        vega_protos.vega.LiquidityOrder(
            reference=vega_protos.vega.PeggedReference.PEGGED_REFERENCE_BEST_BID,
            offset="500000",
            proportion=5,
        ),
    ]
    sell_specs = [
        vega_protos.vega.LiquidityOrder(
            reference=vega_protos.vega.PeggedReference.PEGGED_REFERENCE_MID,
            offset="500000",
            proportion=6,
        ),
        vega_protos.vega.LiquidityOrder(
            reference=vega_protos.vega.PeggedReference.PEGGED_REFERENCE_BEST_ASK,
            offset="20000",
            proportion=1,
        ),
    ]
    vega.wait_for_total_catchup()
    vega.submit_liquidity(
        LIQ.name,
        market_id=market_id,
        commitment_amount=200,
        fee=0.005,
        buy_specs=[("PEGGED_REFERENCE_MID", 1, 2), ("PEGGED_REFERENCE_BEST_BID", 5, 5)],
        sell_specs=[
            ("PEGGED_REFERENCE_MID", 5, 6),
            ("PEGGED_REFERENCE_BEST_ASK", 0.2, 1),
        ],
        is_amendment=True,
    )

    vega.wait_fn(10)
    vega.wait_for_total_catchup()

    liq_provis = vega.party_liquidity_provisions(LIQ.name, market_id=market_id)

    assert len(liq_provis) == 1

    for provis, exp_provis in zip(liq_provis[0].sells, sell_specs):
        assert provis.liquidity_order.reference == exp_provis.reference
        assert provis.liquidity_order.offset == exp_provis.offset
        assert provis.liquidity_order.proportion == exp_provis.proportion

    for provis, exp_provis in zip(liq_provis[0].buys, buy_specs):
        assert provis.liquidity_order.reference == exp_provis.reference
        assert provis.liquidity_order.offset == exp_provis.offset
        assert provis.liquidity_order.proportion == exp_provis.proportion

    num_levels = 11
    expected_bid_prices = [0.2995, 0.25, 0.23194, 0, 0, 0, 0, 0, 0, 0, 0]
    expected_bid_volumes = [668.0, 1.0, 1757.0, 0, 0, 0, 0, 0, 0, 0, 0]
    expected_ask_prices = [0.3005, 0.35, 0.38697, 0, 0, 0, 0, 0, 0, 0, 0]
    expected_ask_volumes = [666.0, 1.0, 1075.0, 0, 0, 0, 0, 0, 0, 0, 0]

    book_state = vega.market_depth(market_id, num_levels=num_levels)
    bid_prices = [level.price for level in book_state.buys] + [0] * max(
        0, num_levels - len(book_state.buys)
    )
    bid_volumes = [level.volume for level in book_state.buys] + [0] * max(
        0, num_levels - len(book_state.buys)
    )
    ask_prices = [level.price for level in book_state.sells] + [0] * max(
        0, num_levels - len(book_state.sells)
    )
    ask_volumes = [level.volume for level in book_state.sells] + [0] * max(
        0, num_levels - len(book_state.sells)
    )

    for price, exp_price in zip(bid_prices, expected_bid_prices):
        assert price == exp_price

    for vol, exp_vol in zip(bid_volumes, expected_bid_volumes):
        assert vol == exp_vol

    for price, exp_price in zip(ask_prices, expected_ask_prices):
        assert price == exp_price

    for vol, exp_vol in zip(ask_volumes, expected_ask_volumes):
        assert vol == exp_vol
