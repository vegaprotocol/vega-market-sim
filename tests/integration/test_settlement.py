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
        settlement_wallet=TERMINATE_WALLET.name,
        settlement_price=settlement_price,
        market_id=market_id,
    )
    vega.wait_fn(10)
    vega.wait_for_datanode_sync()

    # check bond and margin for all
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
