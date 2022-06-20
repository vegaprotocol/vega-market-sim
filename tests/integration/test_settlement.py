import pytest

from tests.integration.utils.fixtures import (
    vega_service,
    MM_WALLET,
    AUCTION1 as TRADER_1_WALLET,
    AUCTION2 as TRADER_2_WALLET,
)
from vega_sim.null_service import VegaServiceNull
import random

wallets = [MM_WALLET, TRADER_1_WALLET, TRADER_2_WALLET]


@pytest.mark.integration
def test_settlement(vega_service: VegaServiceNull):
    vega = vega_service

    participants_initial_deposit = 10e5

    trade_price = random.randint(80, 120)
    bid_ask_offest = random.randint(1, 11)

    settlement_price = random.randint(80, 120)
    trade_size = random.randint(1, 10)

    pnl_long = trade_size * (settlement_price - trade_price)

    for wallet in wallets:
        vega.create_wallet(wallet.name, passphrase=wallet.passphrase)
    vega.forward("1s")

    vega.mint(
        MM_WALLET.name,
        asset="VOTE",
        amount=10000,
    )

    vega.forward("1s")
    vega.create_asset(
        MM_WALLET.name,
        name="tDAI",
        symbol="tDAI",
        decimals=5,
        max_faucet_amount=10e10,
    )
    tdai_id = vega.find_asset_id(symbol="tDAI")

    for wallet in wallets:
        vega.mint(wallet.name, tdai_id, amount=participants_initial_deposit)

    vega.create_simple_market(
        market_name="BTC:DAI_Mar22",
        proposal_wallet=MM_WALLET.name,
        settlement_asset_id=tdai_id,
        termination_wallet=MM_WALLET.name,
        position_decimals=2,
        market_decimals=3,
    )

    market_id = vega.all_markets()[0].id

    vega.submit_simple_liquidity(
        wallet_name=MM_WALLET.name,
        market_id=market_id,
        commitment_amount=participants_initial_deposit / 10,
        fee=0.0049,
        reference_buy="PEGGED_REFERENCE_MID",
        reference_sell="PEGGED_REFERENCE_MID",
        delta_buy=2,
        delta_sell=2,
        is_amendment=True,
    )

    vega.forward("5s")

    # Submit orders which will stay on the book and create best bid / ask
    vega.submit_order(
        trading_wallet=MM_WALLET.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=1,
        price=(trade_price - bid_ask_offest),
        wait=False,
    )

    vega.submit_order(
        trading_wallet=MM_WALLET.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=1,
        price=(trade_price + bid_ask_offest),
        wait=False,
    )

    # Do a trade which will cross
    vega.submit_order(
        trading_wallet=TRADER_1_WALLET.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=trade_size,
        price=trade_price,
        wait=False,
    )

    vega.submit_order(
        trading_wallet=TRADER_2_WALLET.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=trade_size,
        price=trade_price,
        wait=False,
    )
    vega.forward("1s")
    vega.settle_market(
        settlement_wallet=MM_WALLET.name,
        settlement_price=settlement_price,
        market_id=market_id,
    )
    vega.forward("1s")

    # check bond and magin for all
    for wallet in wallets:
        general, margin, bond = vega.party_account(
            wallet_name=wallet.name, asset_id=tdai_id, market_id=market_id
        )
        assert margin == 0
        assert bond == 0

    # LP general
    general, margin, bond = vega.party_account(
        wallet_name=MM_WALLET.name, asset_id=tdai_id, market_id=market_id
    )
    assert general == participants_initial_deposit

    # Trader 1 who went long
    general, margin, bond = vega.party_account(
        wallet_name=TRADER_1_WALLET.name, asset_id=tdai_id, market_id=market_id
    )
    assert general == (participants_initial_deposit + pnl_long)

    # Trader 2 who went short
    general, margin, bond = vega.party_account(
        wallet_name=TRADER_2_WALLET.name, asset_id=tdai_id, market_id=market_id
    )
    assert general == (participants_initial_deposit - pnl_long)
