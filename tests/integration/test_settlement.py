import pytest

from tests.integration.utils.fixtures import (
    build_basic_market,
    vega_service,
    MM_WALLET,
    AUCTION1 as TRADER_1_WALLET,
    AUCTION2 as TRADER_2_WALLET,
    TERMINATE_WALLET,
)
from vega_sim.null_service import VegaServiceNull
import random

wallets = [MM_WALLET, TRADER_1_WALLET, TRADER_2_WALLET]


@pytest.mark.integration
def test_settlement(vega_service: VegaServiceNull):
    vega = vega_service

    participants_initial_deposit = 10e5

    trade_price = random.randint(80, 120)
    bid_ask_offset = random.randint(1, 11)

    settlement_price = random.randint(80, 120)
    trade_size = random.randint(1, 10)

    build_basic_market(
        vega,
        mint_amount=participants_initial_deposit,
        initial_commitment=0.5 * participants_initial_deposit,
        initial_price=trade_price,
        initial_volume=trade_size,
        initial_spread=bid_ask_offset * 2,
    )

    pnl_long = trade_size * (settlement_price - trade_price)

    tdai_id = vega.find_asset_id(symbol="tDAI")
    market_id = vega.all_markets()[0].id

    vega.wait_fn(1)
    vega.wait_for_datanode_sync()

    vega.settle_market(
        settlement_key=TERMINATE_WALLET.name,
        settlement_price=settlement_price,
        market_id=market_id,
    )
    vega.wait_fn(10)
    vega.wait_for_datanode_sync()

    # check bond and margin for all
    for wallet in wallets:
        general, margin, bond = vega.party_account(
            key_name=wallet.name, asset_id=tdai_id, market_id=market_id
        )
        assert margin == 0
        assert bond == 0

    # LP general
    general, margin, bond = vega.party_account(
        key_name=MM_WALLET.name, asset_id=tdai_id, market_id=market_id
    )
    assert general == participants_initial_deposit

    # Trader 1 who went long
    general, margin, bond = vega.party_account(
        key_name=TRADER_1_WALLET.name, asset_id=tdai_id, market_id=market_id
    )
    assert general == (participants_initial_deposit + pnl_long)

    # Trader 2 who went short
    general, margin, bond = vega.party_account(
        key_name=TRADER_2_WALLET.name, asset_id=tdai_id, market_id=market_id
    )

    assert general == (participants_initial_deposit - pnl_long)


@pytest.mark.integration
def test_settlement_with_successor(vega_service: VegaServiceNull):
    vega = vega_service

    participants_initial_deposit = 10e5

    trade_price = random.randint(80, 120)
    bid_ask_offset = random.randint(1, 11)

    settlement_price = random.randint(80, 120)
    trade_size = random.randint(1, 10)

    build_basic_market(
        vega,
        mint_amount=participants_initial_deposit,
        initial_commitment=0.5 * participants_initial_deposit,
        initial_price=trade_price,
        initial_volume=trade_size,
        initial_spread=bid_ask_offset * 2,
    )

    market_id = vega.all_markets()[0].id
    asset_id = vega.find_asset_id(symbol="tDAI")

    vega.wait_fn(1)
    vega.wait_for_datanode_sync()

    vega.create_key(name="TERMINATE_2")

    vega.create_simple_market(
        market_name="CRYPTO:BTCDAI/Jun23",
        proposal_key=MM_WALLET.name,
        settlement_asset_id=asset_id,
        termination_key="TERMINATE_2",
        market_decimals=5,
        parent_market_id=market_id,
        parent_market_insurance_pool_fraction=0.5,
    )

    market_id_2 = vega.all_markets()[0].id

    vega.settle_market(
        settlement_key=TERMINATE_WALLET.name,
        settlement_price=settlement_price,
        market_id=market_id,
    )

    vega.submit_liquidity(
        key_name=MM_WALLET.name,
        market_id=market_id_2,
        commitment_amount=100,
        fee=0.002,
        is_amendment=False,
    )
    # Add transactions in the proposed market to pass opening auction at price 0.3
    vega.submit_order(
        trading_key=TRADER_1_WALLET.name,
        market_id=market_id_2,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=1,
        price=100,
    )

    vega.submit_order(
        trading_key=TRADER_2_WALLET.name,
        market_id=market_id_2,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=1,
        price=100,
    )

    vega.submit_order(
        trading_key=MM_WALLET.name,
        market_id=market_id_2,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=1,
        price=99,
    )

    vega.submit_order(
        trading_key=MM_WALLET.name,
        market_id=market_id_2,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=1,
        price=101,
    )

    vega.settle_market(
        settlement_key="TERMINATE_2",
        settlement_price=settlement_price,
        market_id=market_id_2,
    )
    vega.wait_fn(10)
    vega.wait_for_datanode_sync()
