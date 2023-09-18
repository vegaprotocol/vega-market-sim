from collections import namedtuple
import logging
from typing import Optional

import pytest
from vega_sim.null_service import VegaServiceNull
from vega_sim.service import PeggedOrder

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

MM_WALLET = WalletConfig("mm", "pin")

AUCTION1 = WalletConfig("auction1", "auction1")
AUCTION2 = WalletConfig("auction2", "auction2")

TERMINATE_WALLET = WalletConfig("TERMINATE", "TERMINATE")

TRADER_WALLET = WalletConfig("TRADER", "TRADER")

ASSET_NAME = "tDAI"

WALLETS = [MM_WALLET, AUCTION1, AUCTION2, TERMINATE_WALLET, TRADER_WALLET]


def create_and_faucet_wallet(
    vega: VegaServiceNull, wallet: WalletConfig, symbol: Optional[str] = None, amount: float = 1e4
):
    asset_id = vega.find_asset_id(symbol=symbol if symbol is not None else ASSET_NAME)
    vega.create_key(wallet.name)
    vega.mint(wallet.name, asset_id, amount)


def build_basic_market(
    vega: VegaServiceNull,
    mint_amount: float = 10000,
    initial_price: float = 1,
    initial_volume: float = 1,
    initial_spread: float = 0.1,
    initial_commitment: float = 100,
    parent_market_id: Optional[str] = None,
    parent_market_insurance_pool_fraction: float = 1,
    asset_id: Optional[str] = None,
):
    vega.wait_for_total_catchup()
    for wallet in WALLETS:
        vega.create_key(wallet.name)

    vega.wait_for_total_catchup()
    vega.mint(
        MM_WALLET.name,
        asset="VOTE",
        amount=1e4,
    )
    vega.forward("10s")

    if asset_id is None:
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
        market_name="CRYPTO:BTCDAI/Jun23",
        proposal_key=MM_WALLET.name,
        settlement_asset_id=asset_id,
        termination_key=TERMINATE_WALLET.name,
        market_decimals=5,
        parent_market_id=parent_market_id,
        parent_market_insurance_pool_fraction=parent_market_insurance_pool_fraction,
    )

    market_id = vega.all_markets()[0].id

    vega.submit_liquidity(
        key_name=MM_WALLET.name,
        market_id=market_id,
        commitment_amount=initial_commitment,
        fee=0.002,
        is_amendment=False,
    )
    vega.submit_order(
        trading_key=MM_WALLET.name,
        market_id=market_id,
        side="SIDE_BUY",
        order_type="TYPE_LIMIT",
        pegged_order=PeggedOrder(reference="PEGGED_REFERENCE_BEST_BID", offset=5),
        time_in_force="TIME_IN_FORCE_GTC",
        volume=1.5 * initial_commitment / initial_price,
    )
    vega.submit_order(
        trading_key=MM_WALLET.name,
        market_id=market_id,
        side="SIDE_SELL",
        order_type="TYPE_LIMIT",
        pegged_order=PeggedOrder(reference="PEGGED_REFERENCE_BEST_ASK", offset=5),
        time_in_force="TIME_IN_FORCE_GTC",
        volume=1.5 * initial_commitment / initial_price,
    )

    # Add transactions in the proposed market to pass opening auction at price 0.3
    vega.submit_order(
        trading_key=AUCTION1.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=initial_volume,
        price=initial_price,
    )

    vega.submit_order(
        trading_key=AUCTION2.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=initial_volume,
        price=initial_price,
    )

    vega.submit_order(
        trading_key=TRADER_WALLET.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=initial_volume,
        price=initial_price - initial_spread / 2,
    )

    vega.submit_order(
        trading_key=TRADER_WALLET.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=initial_volume,
        price=initial_price + initial_spread / 2,
    )
    vega.wait_for_total_catchup()


@pytest.fixture(scope="function")
def vega_service():
    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=False,
        retain_log_files=True,
        transactions_per_block=1,
        listen_for_high_volume_stream_updates=False,
        use_full_vega_wallet=False,
    ) as vega:
        yield vega
    logging.debug("vega_service teardown")


@pytest.fixture(scope="function")
def vega_service_with_market(vega_service):
    build_basic_market(vega_service, initial_price=0.3)
    return vega_service


@pytest.fixture(scope="function")
def vega_service_with_high_volume():
    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=False,
        retain_log_files=True,
        transactions_per_block=1,
        listen_for_high_volume_stream_updates=True,
        use_full_vega_wallet=False,
    ) as vega:
        yield vega
    logging.debug("vega_service_with_high_volume teardown")


@pytest.fixture(scope="function")
def vega_service_with_high_volume_with_market(vega_service_with_high_volume):
    build_basic_market(vega_service_with_high_volume, initial_price=0.3)
    return vega_service_with_high_volume
