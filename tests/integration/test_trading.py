import pytest

from tests.integration.utils.fixtures import (
    vega_service_with_market,
    vega_service,
    create_and_faucet_wallet,
    WalletConfig,
    build_basic_market,
    create_and_mint_assets,
    MM_WALLET,
    WALLETS,
    TERMINATE_WALLET,
)
from vega_sim.null_service import VegaServiceNull
import vega_sim.proto.vega as vega_protos


LIQ = WalletConfig("liq", "liq")

TRADER_1_WALLET = WalletConfig("T1", "pin")

TRADER_2_WALLET = WalletConfig("T2", "pin")


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
        buy_specs=[("PEGGED_REFERENCE_MID", 0.005, 1)],
        sell_specs=[("PEGGED_REFERENCE_MID", 0.005, 1)],
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
        assert provis.offset == "500"
        assert provis.proportion == 1

    buy_specs = [
        vega_protos.vega.LiquidityOrder(
            reference=vega_protos.vega.PeggedReference.PEGGED_REFERENCE_MID,
            offset="100",
            proportion=2,
        ),
        vega_protos.vega.LiquidityOrder(
            reference=vega_protos.vega.PeggedReference.PEGGED_REFERENCE_BEST_BID,
            offset="500",
            proportion=5,
        ),
    ]
    sell_specs = [
        vega_protos.vega.LiquidityOrder(
            reference=vega_protos.vega.PeggedReference.PEGGED_REFERENCE_MID,
            offset="500",
            proportion=6,
        ),
        vega_protos.vega.LiquidityOrder(
            reference=vega_protos.vega.PeggedReference.PEGGED_REFERENCE_BEST_ASK,
            offset="20",
            proportion=1,
        ),
    ]
    vega.wait_for_total_catchup()
    vega.submit_liquidity(
        LIQ.name,
        market_id=market_id,
        commitment_amount=200,
        fee=0.005,
        buy_specs=[
            ("PEGGED_REFERENCE_MID", 0.001, 2),
            ("PEGGED_REFERENCE_BEST_BID", 0.005, 5),
        ],
        sell_specs=[
            ("PEGGED_REFERENCE_MID", 0.005, 6),
            ("PEGGED_REFERENCE_BEST_ASK", 0.0002, 1),
        ],
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
    expected_bid_prices = [0.2995, 0.299, 0.25, 0.245, 0, 0, 0, 0, 0, 0, 0]
    expected_bid_volumes = [668.0, 383.0, 1.0, 19760.0, 0, 0, 0, 0, 0, 0, 0]
    expected_ask_prices = [0.3005, 0.305, 0.35, 0.3502, 0, 0, 0, 0, 0, 0, 0]
    expected_ask_volumes = [666.0, 1125.0, 1.0, 171.0, 0, 0, 0, 0, 0, 0, 0]

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


@pytest.mark.integration
def test_liquidity_fees_distributed(vega_service: VegaServiceNull):
    vega = vega_service

    create_and_mint_assets(vega=vega_service)
    asset_id = vega.find_asset_id(symbol="tDAI")
    create_and_faucet_wallet(vega=vega, wallet=TRADER_1_WALLET)
    create_and_faucet_wallet(vega=vega, wallet=TRADER_2_WALLET)

    vega.wait_for_total_catchup()
    vega.update_network_parameter(
        MM_WALLET.name, "market.liquidity.providers.fee.distributionTimeStep", "6000s"
    )
    vega.wait_for_total_catchup()
    vega.update_network_parameter(
        MM_WALLET.name, "market.fee.factors.infrastructureFee", "0.0"
    )
    vega.wait_for_total_catchup()

    build_basic_market(
        vega_service,
        initial_price=99,
        liquidity_fee=0.1,
        initial_spread=0.5,
        liq_spread=0.6,
    )

    vega.wait_for_total_catchup()

    market_id = vega.all_markets()[0].id

    vega.submit_order(
        trading_wallet=TRADER_1_WALLET.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=2,
        price=99,
    )

    vega.submit_order(
        trading_wallet=TRADER_2_WALLET.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=2,
        price=99,
    )
    vega.wait_for_total_catchup()

    post_trade_liq_fees = vega.market_account(
        market_id, vega_protos.vega.ACCOUNT_TYPE_FEES_LIQUIDITY
    )
    assert post_trade_liq_fees == 19.8

    mm_account_pre_settle = sum(
        vega.party_account(
            wallet_name=MM_WALLET.name, asset_id=asset_id, market_id=market_id
        )
    )

    vega.settle_market(TERMINATE_WALLET.name, settlement_price=99, market_id=market_id)
    vega.wait_for_total_catchup()

    post_settle_liq_fees = vega.market_account(
        market_id, vega_protos.vega.ACCOUNT_TYPE_FEES_LIQUIDITY
    )
    mm_account = sum(
        vega.party_account(
            wallet_name=MM_WALLET.name, asset_id=asset_id, market_id=market_id
        )
    )
    assert mm_account == mm_account_pre_settle + post_settle_liq_fees
    assert post_settle_liq_fees == 0
