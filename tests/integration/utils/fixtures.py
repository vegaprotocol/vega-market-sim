from collections import namedtuple

import pytest
from vega_sim.null_service import VegaServiceNull

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

MM_WALLET = WalletConfig("mm", "pin")

AUCTION1 = WalletConfig("auction1", "auction1")
AUCTION2 = WalletConfig("auction2", "auction2")

TERMINATE_WALLET = WalletConfig("TERMINATE", "TERMINATE")

TRADER_WALLET = WalletConfig("TRADER", "TRADER")

ASSET_NAME = "tDAI"

WALLETS = [MM_WALLET, AUCTION1, AUCTION2, TERMINATE_WALLET, TRADER_WALLET]


def create_and_faucet_wallet(
    vega: VegaServiceNull, wallet: WalletConfig, amount: float = 1e4
):
    asset_id = vega.find_asset_id(symbol=ASSET_NAME)
    vega.create_wallet(wallet.name, wallet.passphrase)
    vega.mint(wallet.name, asset_id, amount)


def build_basic_market(
    vega: VegaServiceNull,
    mint_amount: float = 10000,
    initial_price: float = 1,
    initial_volume: float = 1,
    initial_spread: float = 0.1,
    initial_commitment: float = 100,
):
    vega.wait_for_total_catchup()
    for wallet in WALLETS:
        vega.create_wallet(wallet.name, wallet.passphrase)

    vega.wait_for_total_catchup()
    vega.mint(
        MM_WALLET.name,
        asset="VOTE",
        amount=1e4,
    )
    vega.forward("10s")

    # Create asset
    vega.create_asset(
        MM_WALLET.name,
        name=ASSET_NAME,
        symbol=ASSET_NAME,
        decimals=5,
        max_faucet_amount=10 * mint_amount * 1e5,
    )
    vega.forward("10s")
    vega.wait_for_total_catchup()

    asset_id = vega.find_asset_id(symbol=ASSET_NAME)

    for wallet in WALLETS:
        vega.mint(
            wallet.name,
            asset=asset_id,
            amount=mint_amount,
        )
    vega.forward("10s")
    vega.create_simple_market(
        market_name="CRYPTO:BTCDAI/DEC22",
        proposal_wallet=MM_WALLET.name,
        settlement_asset_id=asset_id,
        termination_wallet=TERMINATE_WALLET.name,
        market_decimals=5,
    )

    market_id = vega.all_markets()[0].id

    vega.submit_liquidity(
        wallet_name=MM_WALLET.name,
        market_id=market_id,
        commitment_amount=initial_commitment,
        fee=0.002,
        buy_specs=[("PEGGED_REFERENCE_MID", 0.0005, 1)],
        sell_specs=[("PEGGED_REFERENCE_MID", 0.0005, 1)],
        is_amendment=False,
    )
    # Add transactions in the proposed market to pass opening auction at price 0.3
    vega.submit_order(
        trading_wallet=AUCTION1.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=initial_volume,
        price=initial_price,
    )

    vega.submit_order(
        trading_wallet=AUCTION2.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=initial_volume,
        price=initial_price,
    )

    vega.submit_order(
        trading_wallet=TRADER_WALLET.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=initial_volume,
        price=initial_price - initial_spread / 2,
    )

    vega.submit_order(
        trading_wallet=TRADER_WALLET.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=initial_volume,
        price=initial_price + initial_spread / 2,
    )
    vega.wait_for_total_catchup()


@pytest.fixture
def vega_service():
    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=False,
        start_order_feed=False,
        retain_log_files=True,
        transactions_per_block=1,
    ) as vega:
        yield vega


@pytest.fixture
def vega_service_with_order_feed():
    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=False,
        start_order_feed=True,
        retain_log_files=True,
        transactions_per_block=1,
    ) as vega:
        yield vega


@pytest.fixture
def vega_service_with_market(vega_service):
    build_basic_market(vega_service, initial_price=0.3)
    return vega_service
