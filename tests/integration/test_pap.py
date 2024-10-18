"""Tests the Vega Protocol Automated Purchase program feature.
"""

import pytest
import logging
import datetime


import vega_protos as protos
from vega_sim.null_service import VegaServiceNull
from tests.integration.utils.fixtures import vega_service

logger = logging.getLogger(__name__)

PROPOSER = "proposer"
FUNDER = "funder"
AUX_BID = "bid"
AUX_ASK = "ask"
BASE = "base"
QUOTE = "quote"


@pytest.mark.integration
@pytest.fixture(scope="function")
def init_tests(vega_service):
    # Create a key for proposals.
    vega: VegaServiceNull = vega_service

    # Create proposer key and initialise network and market
    vega.create_key(PROPOSER)
    vega.mint(PROPOSER, vega.find_asset_id(symbol="VOTE", enabled=True), 1000)
    vega.update_network_parameter(
        PROPOSER,
        parameter="market.fee.factors.infrastructureFee",
        new_value="0",
    )
    vega.wait_for_total_catchup()
    vega.update_network_parameter(
        PROPOSER,
        parameter="market.fee.factors.makerFee",
        new_value="0",
    )
    vega.wait_for_total_catchup()
    vega.update_network_parameter(
        PROPOSER,
        parameter="market.fee.factors.buybackFee",
        new_value="0.1",
    )
    vega.wait_for_total_catchup()
    vega.update_network_parameter(
        PROPOSER,
        parameter="market.fee.factors.treasuryFee",
        new_value="0",
    )
    vega.wait_for_total_catchup()
    vega.create_asset(PROPOSER, BASE, BASE, 18, quantum=1)
    vega.wait_for_total_catchup()
    vega.create_asset(PROPOSER, QUOTE, QUOTE, 18, quantum=1)
    vega.wait_for_total_catchup()
    base_asset_id = vega.find_asset_id(symbol=BASE, raise_on_missing=True)
    quote_asset_id = vega.find_asset_id(symbol=QUOTE, raise_on_missing=True)
    vega.create_simple_spot_market(
        proposal_key_name=PROPOSER,
        base_asset_id=base_asset_id,
        quote_asset_id=quote_asset_id,
        market_name="spotName",
        market_code="spotCode",
        price_decimal_places=0,
        size_decimal_places=0,
    )
    vega.wait_for_total_catchup()
    market_id = vega.find_market_id(name="spotName")

    # Create test keys
    vega.create_key(FUNDER)
    vega.mint(FUNDER, quote_asset_id, 10_000)
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    vega.create_key(AUX_BID)
    vega.mint(AUX_BID, base_asset_id, 1_000_000_000)
    vega.mint(AUX_BID, quote_asset_id, 1_000_000_000)
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    vega.create_key(AUX_ASK)
    vega.mint(AUX_ASK, base_asset_id, 1_000_000_000)
    vega.mint(AUX_ASK, quote_asset_id, 1_000_000_000)
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    # Exit the opening auction
    vega.submit_order(
        AUX_BID,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=1,
        price=100,
    )
    vega.submit_order(
        AUX_ASK,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=1,
        price=100,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    assert (
        vega.get_latest_market_data(market_id=market_id).market_trading_mode
        == protos.vega.markets.Market.TradingMode.TRADING_MODE_CONTINUOUS
    )
    # Exit the opening auction
    vega.submit_order(
        AUX_BID,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=1000,
        price=100,
    )
    vega.submit_order(
        AUX_ASK,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=1000,
        price=100,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    vega.update_network_parameter(
        PROPOSER,
        parameter="market.fee.factors.buybackFee",
        new_value="0",
    )
    vega.wait_for_total_catchup()
    yield vega, market_id, base_asset_id, quote_asset_id


def test_new_pap(init_tests):
    vega: VegaServiceNull
    vega, market_id, base_asset_id, quote_asset_id = init_tests

    vega.new_protocol_automated_purchase_program(
        proposal_key=PROPOSER,
        market_id=market_id,
        asset_id=quote_asset_id,
        from_account_type=protos.vega.vega.AccountType.ACCOUNT_TYPE_BUY_BACK_FEES,
        to_account_type=protos.vega.vega.AccountType.ACCOUNT_TYPE_NETWORK_TREASURY,
        oracle_offset_factor=1,
        price_oracle_name="priceOracle",
        price_oracle_signer=vega.wallet.public_key(PROPOSER),
        price_oracle_decimals=0,
        snapshot_frequency=datetime.timedelta(seconds=10),
        auction_frequency=datetime.timedelta(seconds=10),
        auction_duration=datetime.timedelta(seconds=60),
        minimum_auction_size=1,
        maximum_auction_size=1_000,
        oracle_price_staleness_tolerance=datetime.timedelta(minutes=1),
    )
    vega.wait_fn(1)
    vega.submit_oracle_data(
        key_name=PROPOSER,
        name="priceOracle",
        type=protos.vega.data.v1.spec.PropertyKey.Type.TYPE_INTEGER,
        value=100,
        decimals=0,
    )

    for i in range(20):
        vega.wait_fn(1)
        vega.wait_for_total_catchup()
        market = vega.get_latest_market_data(market_id=market_id)
        if (
            market.market_trading_mode
            == protos.vega.markets.Market.TradingMode.TRADING_MODE_PROTOCOL_AUTOMATED_PURCHASE_AUCTION
        ):
            break
    if (
        market.market_trading_mode
        != protos.vega.markets.Market.TradingMode.TRADING_MODE_PROTOCOL_AUTOMATED_PURCHASE_AUCTION
    ):
        raise Exception("market did not enter automated auction")

    vega.submit_order(
        AUX_ASK,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=1000,
        price=100,
    )
    vega.wait_fn(60)
    vega.wait_for_total_catchup()

    market = vega.get_latest_market_data(market_id=market_id)
    if (
        market.market_trading_mode
        != protos.vega.markets.Market.TradingMode.TRADING_MODE_CONTINUOUS
    ):
        assert (
            market.market_trading_mode
            == protos.vega.markets.Market.TradingMode.TRADING_MODE_CONTINUOUS
        )
    assert (
        len(
            vega.list_accounts(
                asset_id=base_asset_id,
                account_types=[
                    protos.vega.vega.AccountType.ACCOUNT_TYPE_NETWORK_TREASURY
                ],
            )
        )
        > 0
    )
