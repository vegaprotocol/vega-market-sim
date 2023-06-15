import pytest
import logging
from collections import namedtuple
import vega_sim.proto.vega as vega_protos
from examples.visualisations.utils import continuous_market,move_market
from vega_sim.scenario.configurable_market.agents import ConfigurableMarketManager
from vega_sim.api.market import MarketConfig

from tests.integration.utils.fixtures import (
    ASSET_NAME,
    MM_WALLET,
    WalletConfig,
    create_and_faucet_wallet,
    vega_service,
    vega_service_with_high_volume,
    vega_service_with_high_volume_with_market,
    vega_service_with_market,
)
from vega_sim.null_service import VegaServiceNull

LIQ = WalletConfig("liq", "liq")
PARTY_A = WalletConfig("party_a", "party_a")
PARTY_B = WalletConfig("party_b", "party_b")
PARTY_C = WalletConfig("party_c", "party_c")

def next_epoch(vega: VegaServiceNull):
    forwards = 0
    epoch_seq = vega.statistics().epoch_seq
    while epoch_seq == vega.statistics().epoch_seq:
        vega.wait_fn(1)
        forwards += 1
        if forwards > 2 * 10 * 60:
            raise Exception(
                "Epoch not started after forwarding the duration of two epochs."
            )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()


@pytest.mark.integration
def test_submit_market_order(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    market_id = vega.all_markets()[0].id

    vega.wait_for_total_catchup()

    create_and_faucet_wallet(vega=vega, wallet=LIQ)
    vega.wait_for_total_catchup()
    create_and_faucet_wallet(vega=vega, wallet=PARTY_A)
    vega.wait_for_total_catchup()

    vega.submit_liquidity(
        LIQ.name,
        market_id=market_id,
        commitment_amount=100,
        fee=0.001,
        buy_specs=[("PEGGED_REFERENCE_MID", 0.1, 1)],
        sell_specs=[("PEGGED_REFERENCE_MID", 0.1, 1)],
    )

    vega.submit_market_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        volume=1,
        side="SIDE_BUY",
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    position_pb_t1 = vega.positions_by_market(
        key_name=PARTY_A.name,
        market_id=market_id,
    )

    assert position_pb_t1.open_volume == 1


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
    expected_bid_volumes = [334.0, 192.0, 1.0, 584.0, 0, 0, 0, 0, 0, 0, 0]
    expected_ask_prices = [0.3005, 0.305, 0.35, 0.3502, 0, 0, 0, 0, 0, 0, 0]
    expected_ask_volumes = [333.0, 563.0, 1.0, 82.0, 0, 0, 0, 0, 0, 0, 0]

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
def test_one_off_transfer(vega_service_with_high_volume_with_market: VegaServiceNull):
    vega = vega_service_with_high_volume_with_market
    market_id = vega.all_markets()[0].id

    create_and_faucet_wallet(vega=vega, wallet=PARTY_A, amount=1e3)
    vega.wait_for_total_catchup()
    create_and_faucet_wallet(vega=vega, wallet=PARTY_B, amount=1e3)
    vega.wait_for_total_catchup()

    asset_id = vega.find_asset_id(symbol=ASSET_NAME, raise_on_missing=True)

    vega.one_off_transfer(
        from_key_name=PARTY_A.name,
        from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
        to_key_name=PARTY_B.name,
        to_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
        asset=asset_id,
        amount=500,
    )

    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    party_a_accounts_t1 = vega.party_account(
        key_name=PARTY_A.name,
        asset_id=asset_id,
        market_id=market_id,
    )
    party_b_accounts_t1 = vega.party_account(
        key_name=PARTY_B.name,
        asset_id=asset_id,
        market_id=market_id,
    )

    all_transfers_t1 = vega.list_transfers(
        key_name=PARTY_A.name,
    )
    live_transfers_t1 = vega.transfer_status_from_feed(live_only=True)

    assert len(all_transfers_t1) == 1
    assert len(live_transfers_t1) == 0
    assert party_a_accounts_t1.general == 499.5
    assert party_b_accounts_t1.general == 1500

    vega.one_off_transfer(
        from_key_name=PARTY_B.name,
        from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
        to_key_name=PARTY_A.name,
        to_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
        asset=asset_id,
        amount=500,
        delay=int(100e9),
    )

    vega.wait_fn(10)
    vega.wait_for_total_catchup()

    party_a_accounts_t2 = vega.party_account(
        key_name=PARTY_A.name,
        asset_id=asset_id,
        market_id=market_id,
    )
    party_b_accounts_t2 = vega.party_account(
        key_name=PARTY_B.name,
        asset_id=asset_id,
        market_id=market_id,
    )

    all_transfers_t2 = vega.list_transfers(
        key_name=PARTY_A.name,
    )
    live_transfers_t2 = vega.transfer_status_from_feed(live_only=True)

    assert len(all_transfers_t2) == 2
    assert len(live_transfers_t2) == 1
    assert party_a_accounts_t2.general == 499.5
    assert party_b_accounts_t2.general == 999.5

    vega.wait_fn(100)
    vega.wait_for_total_catchup()

    party_a_accounts_t3 = vega.party_account(
        key_name=PARTY_A.name,
        asset_id=asset_id,
        market_id=market_id,
    )
    party_b_accounts_t3 = vega.party_account(
        key_name=PARTY_B.name,
        asset_id=asset_id,
        market_id=market_id,
    )

    all_transfers_t3 = vega.list_transfers(
        key_name=PARTY_A.name,
    )
    live_transfers_t3 = vega.transfer_status_from_feed(live_only=True)

    assert len(all_transfers_t3) == 2
    assert len(live_transfers_t3) == 0
    assert party_a_accounts_t3.general == 999.5
    assert party_b_accounts_t3.general == 999.5


@pytest.mark.integration
def test_estimate_position(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    market_id = vega.all_markets()[0].id

    margin, liquidation = vega.estimate_position(
        market_id=market_id,
        open_volume=-1,
        side=["SIDE_SELL", "SIDE_SELL"],
        price=[1.01, 1.02],
        remaining=[1, 1],
        is_market_order=[False, False],
        collateral_available=1,
    )


@pytest.mark.integration
def test_recurring_transfer(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market

    vega.wait_for_total_catchup()

    create_and_faucet_wallet(vega=vega, wallet=PARTY_A, amount=1e3)
    vega.wait_for_total_catchup()
    create_and_faucet_wallet(vega=vega, wallet=PARTY_B, amount=1e3)
    vega.wait_for_total_catchup()

    asset_id = vega.find_asset_id(symbol=ASSET_NAME, raise_on_missing=True)

    vega.recurring_transfer(
        from_key_name=PARTY_A.name,
        from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
        to_key_name=PARTY_B.name,
        to_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
        asset=asset_id,
        amount=500,
        factor=0.5,
    )

    party_a_accounts_t0 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)
    party_b_accounts_t0 = vega.list_accounts(key_name=PARTY_B.name, asset_id=asset_id)

    assert party_a_accounts_t0[0].balance == 1000
    assert party_b_accounts_t0[0].balance == 1000

    # Forward one epoch
    next_epoch(vega=vega)

    party_a_accounts_t1 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)
    party_b_accounts_t1 = vega.list_accounts(key_name=PARTY_B.name, asset_id=asset_id)

    assert party_a_accounts_t1[0].balance == 499.5
    assert party_b_accounts_t1[0].balance == 1500

    # Forward one epoch
    next_epoch(vega=vega)

    party_a_accounts_t2 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)
    party_b_accounts_t2 = vega.list_accounts(key_name=PARTY_B.name, asset_id=asset_id)

    assert party_a_accounts_t2[0].balance == 249.25
    assert party_b_accounts_t2[0].balance == 1750


@pytest.mark.integration
def test_funding_reward_pool(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    vega.wait_for_total_catchup()

    create_and_faucet_wallet(vega=vega, wallet=PARTY_A, amount=1e3)
    vega.wait_for_total_catchup()

    asset_id = vega.find_asset_id(symbol=ASSET_NAME, raise_on_missing=True)

    vega.recurring_transfer(
        from_key_name=PARTY_A.name,
        from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
        to_account_type=vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_RECEIVED_FEES,
        asset=asset_id,
        amount=100,
        factor=1.0,
    )

    party_a_accounts_t0 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)

    assert party_a_accounts_t0[0].balance == 1000

    # Forward one epoch
    next_epoch(vega=vega)

    party_a_accounts_t1 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)

    assert party_a_accounts_t1[0].balance == 899.9

    # Forward one epoch
    next_epoch(vega=vega)

    party_a_accounts_t2 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)

    assert party_a_accounts_t2[0].balance == 799.8


@pytest.mark.integration
def test_liquidation_and_estimate_position_calculation_AC001(vega_service: VegaServiceNull):
    vega = vega_service
    mm_wallet = WalletConfig("mm", "pin")
    terminate_wallet = WalletConfig("TERMINATE", "TERMINATE")
    liq_wallet = WalletConfig("LIQ", "TRADER")
    wallets = [mm_wallet, PARTY_B, PARTY_C, terminate_wallet, liq_wallet]

    mint_amount = 100000000
    initial_volume = 10
    initial_commitment = 1500
    collateral_available = 252

    vega.wait_for_total_catchup()
    for wallet in wallets:
        vega.create_key(wallet.name)
    vega.create_key(PARTY_A.name)

    vega.wait_for_total_catchup()
    vega.mint(
        MM_WALLET.name,
        asset="VOTE",
        amount=1e4,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    
    configWithSlippage = MarketConfig()
    configWithSlippage.set("linear_slippage_factor", str(1))  # Set the linear_slippage_factor to 1
    configWithSlippage.set("quadratic_slippage_factor", str(1))  # Set the quadratic_slippage_factor to 1
    configWithSlippage.set("decimal_places", int(0))  # Set the market decimal_places to 0
    configWithSlippage.set("lp_price_range", str(1))

    # Initialize the Market Manager
    marketManager = ConfigurableMarketManager(
        proposal_key_name=MM_WALLET.name,
        termination_key_name="TERMINATE_WALLET ",
        market_name="CRYPTO:BTCDAI/DEC22",
        market_code="MARKET",
        asset_name=ASSET_NAME,
        asset_dp=0,
        proposal_wallet_name="MM_WALLET.name",
        termination_wallet_name="termination_wallet",
        market_config=configWithSlippage,
        tag="my_tag",
        settlement_price=1000.0,
        initial_mint=1e6
    )

    # Initialize the manager and create the market
    marketManager.initialise(vega=vega, create_key=True, mint_key=True)
    asset_id = vega.find_asset_id(symbol=ASSET_NAME)

    for wallet in wallets:
        vega.mint(
            wallet.name,
            asset=asset_id,
            amount=mint_amount,
        )
    vega.mint(
        PARTY_A.name,
        asset=asset_id,
        amount=collateral_available,
    )
    # Wait for the market creation to complete
    marketManager.vega.wait_for_total_catchup()
    market_id = vega.all_markets()[0].id

    # Access the updated value
    logging.debug(f"linear slippage factor = {configWithSlippage.linear_slippage_factor}")
    vega.update_network_parameter(
            MM_WALLET.name, parameter="network.markPriceUpdateMaximumFrequency", new_value="0"
        )
    vega.submit_liquidity(
        key_name=MM_WALLET.name,
        market_id=market_id,
        commitment_amount=initial_commitment,
        fee=0.002,
        buy_specs=[("PEGGED_REFERENCE_BEST_BID", 1000, 1)],
        sell_specs=[("PEGGED_REFERENCE_BEST_ASK",1000, 1)],
        is_amendment=False,
    )
    order_id_C=vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        order_ref="best-ask",
        price=990,
        volume=initial_volume,
        wait=True,
    )
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=1200,
        volume=initial_volume,
    )
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=1000,
        volume=initial_volume,
    )

    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=1000,
        volume=initial_volume,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    
    market_info = vega.market_info(market_id=market_id)
    market_data = vega.get_latest_market_data(market_id=market_id)
    #Check order status/ market state 

    linear_slippage_factor = float(market_info.linear_slippage_factor)
    quadratic_slippage_factor = float(market_info.quadratic_slippage_factor)
  
    _, estimate_liquidation_price_open_vol_only = vega.estimate_position(
        market_id,
        open_volume=10,
        side=["SIDE_BUY"],
        price=[1000],
        remaining=[0],
        is_market_order=[False],
        collateral_available=collateral_available,
    )

    PARTY_A_position = vega.positions_by_market(
            key_name=PARTY_A.name,
            market_id=market_id,
        )
 
    open_volume_A = PARTY_A_position.open_volume
    risk_factors = vega.get_risk_factors(market_id=market_id)
    risk_factor = (
        risk_factors.long if open_volume_A > 0 else risk_factors.short
    )

    liquidation_price_open_vol_only_best_case = max((collateral_available - open_volume_A * market_data.mark_price)/(open_volume_A * 0 + open_volume_A**2 * 0 + open_volume_A * risk_factor - open_volume_A),0)
    liquidation_price_open_vol_only_worst_case = max((collateral_available - open_volume_A * market_data.mark_price)/(open_volume_A * linear_slippage_factor + open_volume_A**2 * quadratic_slippage_factor + open_volume_A * risk_factor - open_volume_A),0)
    
    # #check the calculation of estimate_liquidation_price_open_vol_only.best_case.open_volume_only
    assert round(estimate_liquidation_price_open_vol_only.best_case.open_volume_only,12)== round(liquidation_price_open_vol_only_best_case,12)
    assert round(estimate_liquidation_price_open_vol_only.worst_case.open_volume_only,12)== round(liquidation_price_open_vol_only_worst_case,12)

    #amend order in order to set the new mark price 
    vega.amend_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_id=order_id_C,
        price=999,
        volume_delta=0,
    )
    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        order_ref="new_buy_price_to_trade",
        price=999,
        volume=1,
    )
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        order_ref="new_sell_price_to_trade",
        price=999,
        volume=1,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    
    assert vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id).general+vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id).margin !=0

    #amend order in order to set the new mark price 
    vega.amend_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_id=order_id_C,
        price=985,
        volume_delta=0,
    )
    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        order_ref="new_buy_price_to_trade",
        price=985,
        volume=initial_volume,
    )
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        order_ref="new_sell_price_to_trade",
        price=985,
        volume=initial_volume,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    #AC 0012-NP-LIPE-001:Check actual liquidation price is within the estimated price 
    assert vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id).general+vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id).margin ==0
    assert estimate_liquidation_price_open_vol_only.best_case.open_volume_only >= vega.get_latest_market_data(market_id=market_id).mark_price
    assert estimate_liquidation_price_open_vol_only.worst_case.open_volume_only<= vega.get_latest_market_data(market_id=market_id).mark_price
   

@pytest.mark.integration
def test_liquidation_price_witin_estimate_position_bounds_AC002(vega_service: VegaServiceNull):
    vega = vega_service
    partyConfig = namedtuple("WalletConfig", ["wallet_name", "key_name"])
    wallet_name = "vega"
 
    trader_a = partyConfig(wallet_name=wallet_name, key_name="Trader A Party")
    trader_b = partyConfig(wallet_name=wallet_name, key_name="Trader B Party")
    trader_mint = 20000
    trader_position = 100
  
    # Setup a market and move it into a continuous trading state
    market_id, asset_id, best_ask_id, best_bid_id = continuous_market(
        vega=vega, price=500, spread=10
    )

    # Create wallets and keys for traders
    vega.create_key(
        name=trader_a.key_name,
        wallet_name=trader_a.wallet_name,
    )
    vega.create_key(
        name=trader_b.key_name,
        wallet_name=trader_b.wallet_name,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    # Mint settlement assets for traders
    vega.mint(
        wallet_name=trader_a.wallet_name,
        key_name=trader_a.key_name,
        asset=asset_id,
        amount=trader_mint,
    )
    vega.mint(
        wallet_name=trader_b.wallet_name,
        key_name=trader_b.key_name,
        asset=asset_id,
        amount=trader_mint,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    logging.info(
        f"Trader A Party: public_key = {vega.wallet.public_key(name=trader_a.key_name, wallet_name=trader_a.wallet_name)}"
    )
    logging.info(
        f"Trader B Party: public_key = {vega.wallet.public_key(name=trader_b.key_name, wallet_name=trader_b.wallet_name)}"
    )

    #0012-NP-LIPE-002: An estimate is obtained for a short position with no open orders, mark price keeps going up in small increments and the actual liquidation takes place within the estimated range. 
    vega.submit_order(
        trading_wallet=trader_a.wallet_name,
        trading_key=trader_a.key_name,
        market_id=market_id,
        time_in_force="TIME_IN_FORCE_GTC",
        order_type="TYPE_LIMIT",
        side="SIDE_BUY",
        volume=trader_position,
        price=500,
    )
    vega.submit_order(
        trading_wallet=trader_b.wallet_name,
        trading_key=trader_b.key_name,
        market_id=market_id,
        time_in_force="TIME_IN_FORCE_GTC",
        order_type="TYPE_LIMIT",
        side="SIDE_SELL",
        volume=trader_position,
        price=500,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    for price in [550, 600, 650, 660, 662, 663, 664]:
        move_market(
            vega=vega,
            market_id=market_id,
            best_ask_id=best_ask_id,
            best_bid_id=best_bid_id,
            price=price,
            spread=10,
            volume=1,
        )
        vega.wait_fn(1)
        vega.wait_for_total_catchup()

        trader_a_position = vega.positions_by_market(
            wallet_name=trader_a.wallet_name,
            key_name=trader_a.key_name,
            market_id=market_id,
        )
        trader_b_position = vega.positions_by_market(
            wallet_name=trader_b.wallet_name,
            key_name=trader_b.key_name,
            market_id=market_id,
        )
        account_TRADER_B = vega.party_account(
                key_name=trader_b.key_name,
                wallet_name=trader_b.wallet_name,
                asset_id=asset_id,  
                market_id=market_id,   
        )
        open_orders_TRADER_B = vega.list_orders(
                key_name=trader_b.key_name,
                wallet_name=trader_b.wallet_name,
                market_id=market_id,   
        )
        if price == 663:
            collateral_available = account_TRADER_B.general + account_TRADER_B.bond + account_TRADER_B.margin

        if price == 664:
            # Check Trader B closed out and Trader A position still open
            assert trader_a_position.open_volume == trader_position
            assert trader_a_position.unrealised_pnl > 0
            assert trader_b_position.open_volume == 0
            assert trader_b_position.unrealised_pnl == 0
            # Check loss socialisation was not required for close out
            assert trader_a_position.loss_socialisation_amount == 0
            assert trader_b_position.loss_socialisation_amount == 0
        else:
            # Check Trader A and Trader B positions are still open
            assert trader_a_position.open_volume == trader_position
            assert trader_a_position.unrealised_pnl > 0
            assert trader_b_position.open_volume == -trader_position                    
            assert trader_b_position.unrealised_pnl < 0

    market_info = vega.market_info(market_id=market_id)
    market_data = vega.get_latest_market_data(market_id=market_id)
    _, estimate_liquidation_price = vega.estimate_position(
        market_id,
        open_volume=-100,
        side=["SIDE_SELL"],
        price=[market_data.mark_price],
        remaining=[0],
        is_market_order=[False],
        collateral_available=collateral_available,
    )
    assert market_data.mark_price <= round(estimate_liquidation_price.best_case.open_volume_only/1e5,0)
    assert market_data.mark_price >= round(estimate_liquidation_price.worst_case.open_volume_only/1e5,0)

    #0012-NP-LIPE-006:There's no difference in the estimate for an open volume and that with 0 open volume and market order of the same size. 
    _, estimate_liquidation_price_with_MO = vega.estimate_position(
        market_id,
        open_volume=0,
        side=["SIDE_SELL"],
        price=[market_data.mark_price],
        remaining=[100, 100],
        is_market_order=[True, True],
        collateral_available=collateral_available,
    )
    assert estimate_liquidation_price.best_case.open_volume_only == estimate_liquidation_price_with_MO.best_case.including_sell_orders
    assert estimate_liquidation_price.worst_case.open_volume_only == estimate_liquidation_price_with_MO.worst_case.including_sell_orders





@pytest.mark.integration
def test_liquidation_price_witin_estimate_position_bounds_AC005(vega_service: VegaServiceNull):
    #An estimate is obtained for a short position with multiple limit sell order with the absolute value of the total remaining size of the orders less than the open volume
    vega = vega_service
    terminate_wallet = WalletConfig("TERMINATE", "TERMINATE")
    liq_wallet = WalletConfig("LIQ", "TRADER")
    wallets = [MM_WALLET, PARTY_B, PARTY_C, terminate_wallet, liq_wallet]

    mint_amount = 100000000
    initial_volume = 10
    initial_commitment = 150000
    collateral_available = 15000

    vega.wait_for_total_catchup()
    for wallet in wallets:
        vega.create_key(wallet.name)
    vega.create_key(PARTY_A.name)

    vega.wait_for_total_catchup()
    vega.mint(
        MM_WALLET.name,
        asset="VOTE",
        amount=1e4,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    configWithSlippage = MarketConfig()
    configWithSlippage.set("linear_slippage_factor", str(10))  # Set the linear_slippage_factor to 10
    configWithSlippage.set("quadratic_slippage_factor", str(10))  # Set the quadratic_slippage_factor to 10
    configWithSlippage.set("decimal_places", int(0))  # Set the market decimal_places to 0
    configWithSlippage.set("lp_price_range", str(1))
    triggers0=[
         {
                "horizon": 864000,  #10 days
                "probability": "0.90001",
                "auction_extension": 5,
        },
    ]
    configWithSlippage.set("price_monitoring_parameters.triggers", triggers0)
   
    # Initialize the Market Manager
    marketManager = ConfigurableMarketManager(
        proposal_key_name=MM_WALLET.name,
        termination_key_name="TERMINATE_WALLET ",
        market_name="CRYPTO:BTCDAI/DEC22",
        market_code="MARKET",
        asset_name=ASSET_NAME,
        asset_dp=0,
        proposal_wallet_name="MM_WALLET.name",
        termination_wallet_name="termination_wallet",
        market_config=configWithSlippage,
        tag="my_tag",
        settlement_price=1000.0,
        initial_mint=1e6
    )
    # Initialize the manager and create the market
    marketManager.initialise(vega=vega, create_key=True, mint_key=True)
    asset_id = vega.find_asset_id(symbol=ASSET_NAME)
    
    for wallet in wallets:
        vega.mint(
            wallet.name,
            asset=asset_id,
            amount=mint_amount,
        )
    vega.mint(
        PARTY_A.name,
        asset=asset_id,
        amount=collateral_available,
    )
    # Wait for the market creation to complete
    vega.wait_fn(10)
    marketManager.vega.wait_for_total_catchup()
    market_id = vega.all_markets()[0].id

    # Access the updated value
    vega.update_network_parameter(
            MM_WALLET.name, parameter="network.markPriceUpdateMaximumFrequency", new_value="0"
        )

    vega.submit_liquidity(
        key_name=MM_WALLET.name,
        market_id=market_id,
        commitment_amount=initial_commitment,
        fee=0.002,
        buy_specs=[("PEGGED_REFERENCE_BEST_BID", 1000, 1)],
        sell_specs=[("PEGGED_REFERENCE_BEST_ASK",1000, 1)],
        is_amendment=False,
    )
    order_id_C=vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        order_ref="best-ask",
        price=910,
        volume=initial_volume,
        wait=True,
    )
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=1000,
        volume=initial_volume,
    )
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=1000,
        volume=initial_volume,
    )
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=1005,
        volume=2,
    )
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=1010,
        volume=2,
    )
    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=2100,
        volume=initial_volume,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
 
    PARTY_A_account = vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id)
    collateral = PARTY_A_account.general+PARTY_A_account.margin
    
    _, estimate_liquidation_price_1 = vega.estimate_position(
        market_id,
        open_volume=-10,
        side=["SIDE_SELL","SIDE_SELL" ],
        price=[1005,1010],
        remaining=[2,2],
        is_market_order=[False],
        collateral_available=collateral,
    )

    # #AC 0012-NP-LIPE-005: The estimated liquidation price with sell orders is lower than that for the open volume only.
    assert(estimate_liquidation_price_1.best_case.including_sell_orders<=estimate_liquidation_price_1.best_case.open_volume_only)
    assert(estimate_liquidation_price_1.worst_case.including_sell_orders<=estimate_liquidation_price_1.worst_case.open_volume_only)
   
    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=1005,
        volume=2,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    PARTY_A_account = vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id)
    collateral = PARTY_A_account.general+PARTY_A_account.margin
    _, estimate_liquidation_price_2 = vega.estimate_position(   
        market_id,
        open_volume=-12,
        side=["SIDE_SELL"],
        price=[1010],
        remaining=[2],
        is_market_order=[False],
        collateral_available=collateral,
    )
    assert(estimate_liquidation_price_2.best_case.open_volume_only<=estimate_liquidation_price_1.best_case.open_volume_only)
    assert(estimate_liquidation_price_2.worst_case.open_volume_only<=estimate_liquidation_price_1.worst_case.open_volume_only)

    assert(estimate_liquidation_price_2.best_case.including_sell_orders<=estimate_liquidation_price_1.best_case.including_sell_orders)
    assert(estimate_liquidation_price_2.worst_case.including_sell_orders<=estimate_liquidation_price_1.worst_case.including_sell_orders)


    assert(estimate_liquidation_price_2.best_case.including_sell_orders<=estimate_liquidation_price_2.best_case.open_volume_only)
    assert(estimate_liquidation_price_2.worst_case.including_sell_orders<=estimate_liquidation_price_2.worst_case.open_volume_only)

    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=1010,
        volume=1,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    
    PARTY_A_account = vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id)
    collateral = PARTY_A_account.general+PARTY_A_account.margin
    _, estimate_liquidation_price_3 = vega.estimate_position(   
        market_id,
        open_volume=-13,
        side=["SIDE_SELL"],
        price=[1010],
        remaining=[1],
        is_market_order=[False],
        collateral_available=collateral,
    )
    assert(estimate_liquidation_price_3.best_case.open_volume_only<=estimate_liquidation_price_2.best_case.open_volume_only)
    assert(estimate_liquidation_price_3.worst_case.open_volume_only<=estimate_liquidation_price_2.worst_case.open_volume_only)

    assert(estimate_liquidation_price_3.best_case.including_sell_orders<=estimate_liquidation_price_2.best_case.including_sell_orders)
    assert(estimate_liquidation_price_3.worst_case.including_sell_orders<=estimate_liquidation_price_2.worst_case.including_sell_orders)
  
    assert(estimate_liquidation_price_3.best_case.including_sell_orders<=estimate_liquidation_price_3.best_case.open_volume_only)
    assert(estimate_liquidation_price_3.worst_case.including_sell_orders<=estimate_liquidation_price_3.worst_case.open_volume_only)

    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=1010,
        volume=1,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    PARTY_A_account = vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id)
    market_data_closeout = vega.get_latest_market_data(market_id=market_id)
    #check PARTY_A is closed out
    assert(PARTY_A_account.general+PARTY_A_account.margin>=-1e-10)
    assert(PARTY_A_account.general+PARTY_A_account.margin<=1e-10)
    #As the price keeps moving in small increments the liquidation happens within the originally estimated range (with sell orders)
    assert(market_data_closeout.mark_price <= estimate_liquidation_price_1.best_case.including_sell_orders)
    assert(market_data_closeout.mark_price >= estimate_liquidation_price_1.worst_case.including_sell_orders)

@pytest.mark.integration
def test_estimated_liquidation_price_AC004(vega_service: VegaServiceNull):
    vega = vega_service
    terminate_wallet = WalletConfig("TERMINATE", "TERMINATE")
    liq_wallet = WalletConfig("LIQ", "TRADER")
    wallets = [MM_WALLET, PARTY_B, PARTY_C, terminate_wallet, liq_wallet]

    mint_amount = 100000000
    initial_volume = 10
    initial_commitment = 1500
    collateral_available = 732

    vega.wait_for_total_catchup()
    for wallet in wallets:
        vega.create_key(wallet.name)
    vega.create_key(PARTY_A.name)

    vega.wait_for_total_catchup()
    vega.mint(
        MM_WALLET.name,
        asset="VOTE",
        amount=1e4,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    configWithSlippage = MarketConfig()
    configWithSlippage.set("linear_slippage_factor", str(10000))  # Set the linear_slippage_factor to 10000
    configWithSlippage.set("quadratic_slippage_factor", str(10000))  # Set the quadratic_slippage_factor to 10000
    configWithSlippage.set("decimal_places", int(0))  # Set the market decimal_places to 0
    configWithSlippage.set("lp_price_range", str(1))
    triggers0=[
         {
                "horizon": 8640000,  # 100 days
                "probability": "0.90001",
                "auction_extension": 5,
        },
    ]
    configWithSlippage.set("price_monitoring_parameters.triggers", triggers0)
   
    # Initialize the Market Manager
    marketManager = ConfigurableMarketManager(
        proposal_key_name=MM_WALLET.name,
        termination_key_name="TERMINATE_WALLET ",
        market_name="CRYPTO:BTCDAI/DEC22",
        market_code="MARKET",
        asset_name=ASSET_NAME,
        asset_dp=0,
        proposal_wallet_name="MM_WALLET.name",
        termination_wallet_name="termination_wallet",
        market_config=configWithSlippage,
        tag="my_tag",
        settlement_price=1000.0,
        initial_mint=1e6
    )
    # Initialize the manager and create the market
    marketManager.initialise(vega=vega, create_key=True, mint_key=True)
    asset_id = vega.find_asset_id(symbol=ASSET_NAME)
    
    for wallet in wallets:
        vega.mint(
            wallet.name,
            asset=asset_id,
            amount=mint_amount,
        )
    vega.mint(
        PARTY_A.name,
        asset=asset_id,
        amount=collateral_available,
    )
    # Wait for the market creation to complete
    vega.wait_fn(10)
    marketManager.vega.wait_for_total_catchup()
    market_id = vega.all_markets()[0].id

    # Access the updated value
    vega.update_network_parameter(
            MM_WALLET.name, parameter="network.markPriceUpdateMaximumFrequency", new_value="0"
        )

    vega.submit_liquidity(
        key_name=MM_WALLET.name,
        market_id=market_id,
        commitment_amount=initial_commitment,
        fee=0.002,
        buy_specs=[("PEGGED_REFERENCE_BEST_BID", 1000, 1)],
        sell_specs=[("PEGGED_REFERENCE_BEST_ASK",1000, 1)],
        is_amendment=False,
    )
    order_id_C=vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        order_ref="best-ask",
        price=950,
        volume=initial_volume,
        wait=True,
    )
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=2000,
        volume=initial_volume,
    )
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=1000,
        volume=initial_volume,
    )
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=1000,
        volume=initial_volume,
    )
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=1001,
        volume=1,
    )
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=1002,
        volume=2,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    
    PARTY_A_account = vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id)
    collateral = PARTY_A_account.general+PARTY_A_account.margin
    _, estimate_liquidation_price_1 = vega.estimate_position(
        market_id,
        open_volume=10,
        side=["SIDE_SELL"],
        price=[1001,1002],
        remaining=[1,2],
        is_market_order=[False, False],
        collateral_available=collateral,
    )
    # AC 0012-NP-LIPE-004: An estimate is obtained for a long position with multiple limit sell order with the absolute value of the total remaining size of the orders less than the open volume. The estimated liquidation price with sell orders is lower than that for the open volume only.
    assert estimate_liquidation_price_1.best_case.including_sell_orders <= estimate_liquidation_price_1.best_case.open_volume_only
    assert estimate_liquidation_price_1.worst_case.including_sell_orders <= estimate_liquidation_price_1.worst_case.open_volume_only
  
    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=1001,
        volume=1,
    )

    PARTY_A_account = vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id)
    collateral = PARTY_A_account.general+PARTY_A_account.margin

    _, estimate_liquidation_price_2 = vega.estimate_position(
        market_id,
        open_volume=9,
        side=["SIDE_SELL"],
        price=[1002],
        remaining=[2],
        is_market_order=[False],
        collateral_available=collateral,
    )
    assert estimate_liquidation_price_2.best_case.including_sell_orders <= estimate_liquidation_price_2.best_case.open_volume_only
    assert estimate_liquidation_price_2.worst_case.including_sell_orders <= estimate_liquidation_price_2.worst_case.open_volume_only

    assert(estimate_liquidation_price_1.best_case.open_volume_only>=estimate_liquidation_price_2.best_case.open_volume_only)
    assert(estimate_liquidation_price_1.worst_case.open_volume_only>=estimate_liquidation_price_2.worst_case.open_volume_only)
    assert(estimate_liquidation_price_1.best_case.including_sell_orders>=estimate_liquidation_price_2.best_case.including_sell_orders)
    assert(estimate_liquidation_price_1.worst_case.including_sell_orders>=estimate_liquidation_price_2.worst_case.including_sell_orders)

    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=1002,
        volume=2,
    )

    PARTY_A_account = vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id)
    collateral = PARTY_A_account.general+PARTY_A_account.margin
    _, estimate_liquidation_price_3 = vega.estimate_position(
        market_id,
        open_volume=7,
        side=["SIDE_SELL"],
        price=[1002],
        remaining=[0],
        is_market_order=[False],
        collateral_available=collateral,
    )
    assert(estimate_liquidation_price_2.best_case.open_volume_only>=estimate_liquidation_price_3.best_case.open_volume_only)
    assert(estimate_liquidation_price_2.worst_case.open_volume_only>=estimate_liquidation_price_3.worst_case.open_volume_only)
    assert(estimate_liquidation_price_2.best_case.including_sell_orders>=estimate_liquidation_price_3.best_case.including_sell_orders)
    assert(estimate_liquidation_price_2.worst_case.including_sell_orders>=estimate_liquidation_price_3.worst_case.including_sell_orders)

    assert estimate_liquidation_price_3.best_case.including_sell_orders <= estimate_liquidation_price_3.best_case.open_volume_only
    assert estimate_liquidation_price_3.worst_case.including_sell_orders <= estimate_liquidation_price_3.worst_case.open_volume_only
   
@pytest.mark.integration
def test_estimated_liquidation_price_AC003(vega_service: VegaServiceNull):
    vega = vega_service
    terminate_wallet = WalletConfig("TERMINATE", "TERMINATE")
    liq_wallet = WalletConfig("LIQ", "TRADER")
    wallets = [MM_WALLET, PARTY_B, PARTY_C, terminate_wallet, liq_wallet]

    mint_amount = 1000000000
    initial_volume = 10
    initial_commitment = 1500000
    collateral_available = 9000

    vega.wait_for_total_catchup()
    for wallet in wallets:
        vega.create_key(wallet.name)
    vega.create_key(PARTY_A.name)

    vega.wait_for_total_catchup()
    vega.mint(
        MM_WALLET.name,
        asset="VOTE",
        amount=1e4,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    configWithSlippage = MarketConfig()
    configWithSlippage.set("linear_slippage_factor", str(10))  # Set the linear_slippage_factor to 10
    configWithSlippage.set("quadratic_slippage_factor", str(10))  # Set the quadratic_slippage_factor to 10
    configWithSlippage.set("decimal_places", int(0))  # Set the market decimal_places to 0
    configWithSlippage.set("lp_price_range", str(1))
    triggers0=[
         {
                "horizon": 8640000,  # 100 days
                "probability": "0.90001",
                "auction_extension": 5,
        },
    ]
    configWithSlippage.set("price_monitoring_parameters.triggers", triggers0)
   
    # Initialize the Market Manager
    marketManager = ConfigurableMarketManager(
        proposal_key_name=MM_WALLET.name,
        termination_key_name="TERMINATE_WALLET ",
        market_name="CRYPTO:BTCDAI/DEC22",
        market_code="MARKET",
        asset_name=ASSET_NAME,
        asset_dp=0,
        proposal_wallet_name="MM_WALLET.name",
        termination_wallet_name="termination_wallet",
        market_config=configWithSlippage,
        tag="my_tag",
        settlement_price=1000.0,
        initial_mint=1e6
    )
    # Initialize the manager and create the market
    marketManager.initialise(vega=vega, create_key=True, mint_key=True)
    asset_id = vega.find_asset_id(symbol=ASSET_NAME)
    
    for wallet in wallets:
        vega.mint(
            wallet.name,
            asset=asset_id,
            amount=mint_amount,
        )
    vega.mint(
        PARTY_A.name,
        asset=asset_id,
        amount=collateral_available,
    )
    # Wait for the market creation to complete
    vega.wait_fn(1)
    marketManager.vega.wait_for_total_catchup()
    market_id = vega.all_markets()[0].id

    # Access the updated value
    vega.update_network_parameter(
            MM_WALLET.name, parameter="network.markPriceUpdateMaximumFrequency", new_value="0"
        )

    vega.submit_liquidity(
        key_name=MM_WALLET.name,
        market_id=market_id,
        commitment_amount=initial_commitment,
        fee=0.001,
        buy_specs=[("PEGGED_REFERENCE_BEST_BID", 1000, 1)],
        sell_specs=[("PEGGED_REFERENCE_BEST_ASK",1000, 1)],
        is_amendment=False,
    )
    order_id_C=vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        order_ref="best-ask",
        price=950,
        volume=1,
        wait=True,
    )

    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=4000,
        volume=initial_volume,
    )
    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=1000,
        volume=initial_volume,
    )
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=1000,
        volume=initial_volume,
    )
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        order_ref="best-ask",
        price=970,
        volume=initial_volume,
    )

    vega.wait_fn(10)
    vega.wait_for_total_catchup()
    PARTY_A_account = vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id)
    collateral = PARTY_A_account.general+PARTY_A_account.margin
    _, estimate_liquidation_price_1 = vega.estimate_position(
        market_id,
        open_volume=0,
        side=["SIDE_BUY"],
        price=[970],
        remaining=[initial_volume],
        is_market_order=[False],
        collateral_available=collateral,
    )
 
    #AC 0012-NP-LIPE-003: An estimate is obtained for a position with no open volume and a single limit buy order, after the order fills the mark price keeps going down in small increments and the actual liquidation takes place within the obtained estimated range. 
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=970,
        volume=10,
    )
    vega.wait_fn(10)
    vega.wait_for_total_catchup()
   
    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        order_ref="best-ask-50",
        price=50,
        volume=10,
        wait=True,
    )
    #closeout
    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=200,
        volume=initial_volume,
    )
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=200,
        volume=initial_volume,
    )
    vega.wait_fn(10)
    vega.wait_for_total_catchup()
    market_data = vega.get_latest_market_data(market_id=market_id)
    PARTY_A_account = vega.party_account(key_name=PARTY_A.name, asset_id=asset_id, market_id=market_id)
   
    if PARTY_A_account.general+PARTY_A_account.margin==0:
        closeout_price  = market_data.mark_price
 
    assert(closeout_price >= estimate_liquidation_price_1.best_case.including_buy_orders)
    assert(closeout_price <= estimate_liquidation_price_1.worst_case.including_buy_orders)
   




