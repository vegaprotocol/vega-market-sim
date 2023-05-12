import pytest
import logging
from collections import namedtuple
import vega_sim.proto.vega as vega_protos
from examples.visualisations.utils import continuous_market,move_market

from tests.integration.utils.fixtures import (
    ASSET_NAME,
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
    assert party_a_accounts_t1.general == 500
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
    assert party_a_accounts_t2.general == 500
    assert party_b_accounts_t2.general == 1000

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
    assert party_a_accounts_t3.general == 1000
    assert party_b_accounts_t3.general == 1000


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
def test_liquidation_and_estimate_position_calculation(vega_service: VegaServiceNull):
    vega = vega_service
    WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

    MM_WALLET = WalletConfig("mm", "pin")
    PARTY_A = WalletConfig("party_a", "party_a")
    PARTY_B = WalletConfig("party_b", "party_b")
    PARTY_C = WalletConfig("party_c", "party_c")
    TERMINATE_WALLET = WalletConfig("TERMINATE", "TERMINATE")
    LIQ_WALLET = WalletConfig("LIQ", "TRADER")
    ASSET_NAME = "tDAI"
    WALLETS = [MM_WALLET, PARTY_B, PARTY_C, TERMINATE_WALLET, LIQ_WALLET]

    mint_amount = 10000
    initial_volume = 10
    initial_commitment = 1000
    collateral_available = 1000

    vega.wait_for_total_catchup()
    for wallet in WALLETS:
        vega.create_key(wallet.name)
    vega.create_key(PARTY_A.name)

    vega.wait_for_total_catchup()
    vega.mint(
        MM_WALLET.name,
        asset="VOTE",
        amount=1e4,
    )
    vega.forward("10s")

    vega.create_asset(
        MM_WALLET.name,
        name=ASSET_NAME,
        symbol=ASSET_NAME,
        decimals=0,
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

    vega.mint(
        PARTY_A.name,
        asset=asset_id,
        amount=619,
    )
    vega.forward("10s")
    vega.create_simple_market(
        market_name="CRYPTO:BTCDAI/DEC22",
        # market_name = vega.find_market_id,
        proposal_key=MM_WALLET.name,
        settlement_asset_id=asset_id,
        termination_key=TERMINATE_WALLET.name,
        market_decimals=0,
    )
    vega.update_network_parameter(
            MM_WALLET.name, parameter="network.markPriceUpdateMaximumFrequency", new_value="0"
        )

    market_id = vega.all_markets()[0].id

    vega.submit_liquidity(
        key_name=MM_WALLET.name,
        market_id=market_id,
        commitment_amount=initial_commitment,
        fee=0.002,
        buy_specs=[("PEGGED_REFERENCE_BEST_BID", 50, 1)],
        sell_specs=[("PEGGED_REFERENCE_BEST_ASK",50, 1)],
        is_amendment=False,
    )
    # Add transactions in the proposed market to pass opening auction at price 1000
    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        order_id="best_bid_id",
        price=800,
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
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=1200,
        volume=initial_volume,
    )
    vega.wait_for_total_catchup()
    vega.wait_fn(1)
    #Check order status/ market state 
    print(vega.get_latest_market_data(market_id=market_id))

    market_info = vega.market_info(market_id=market_id)
    linear_slippage_factor = float(market_info.linear_slippage_factor)
    quadratic_slippage_factor = float(market_info.quadratic_slippage_factor)
    market_data = vega.get_latest_market_data(market_id=market_id)
    markprice = market_data.mark_price

    estimate_margin_open_vol_only, estimate_liquidation_price_open_vol_only = vega.estimate_position(
        market_id,
        open_volume=10,
        side=["SIDE_BUY"],
        price=[800],
        remaining=[1, 1],
        is_market_order=[False, False],
        collateral_available=collateral_available,
    )

    position = namedtuple(
    "position",
    [
        "party_id",
        "market_id",
        "open_volume",
        "realised_pnl",
        "unrealised_pnl",
        "average_entry_price",
        "updated_at",
        "loss_socialisation_amount",
    ],
    )
    position = vega.positions_by_market(
        key_name=PARTY_A.name,
        market_id=market_id,
    )
    open_volume = int(position.open_volume) if position is not None else 0
    risk_factors = vega.get_risk_factors(market_id=market_id)
    risk_factor = (
        risk_factors.long if open_volume > 0 else risk_factors.short
    )
    liquidation_price_open_vol_only_best_case = (collateral_available - open_volume * markprice)/(open_volume * 0 + open_volume**2 * 0 + open_volume * risk_factor - open_volume)
    liquidation_price_open_vol_only_worst_case = (collateral_available - open_volume * markprice)/(open_volume * linear_slippage_factor + open_volume**2 * quadratic_slippage_factor + open_volume * risk_factor - open_volume)
    
    #check the calculation of estimate_liquidation_price_open_vol_only.best_case.open_volume_only
    assert estimate_liquidation_price_open_vol_only.best_case.open_volume_only== liquidation_price_open_vol_only_best_case
    assert estimate_liquidation_price_open_vol_only.worst_case.open_volume_only== liquidation_price_open_vol_only_worst_case
    account_PARTY_A = vega.party_account(key_name=PARTY_A.name,
        asset_id=asset_id,
        market_id=market_id,
    )
    print(f"party_account = {account_PARTY_A}")
    input("wait")

   
@pytest.mark.integration
def test_liquidation_price_witin_estimate_position_bounds_AC002(vega_service: VegaServiceNull):
    vega = vega_service
    PartyConfig = namedtuple("WalletConfig", ["wallet_name", "key_name"])
    WALLET_NAME = "vega"
 
    TRADER_A = PartyConfig(wallet_name=WALLET_NAME, key_name="Trader A Party")
    TRADER_B = PartyConfig(wallet_name=WALLET_NAME, key_name="Trader B Party")
    TRADER_MINT = 20000
    TRADER_POSITION = 100
  
    # Setup a market and move it into a continuous trading state
    market_id, asset_id, best_ask_id, best_bid_id = continuous_market(
        vega=vega, price=500, spread=10
    )

    # Create wallets and keys for traders
    vega.create_key(
        name=TRADER_A.key_name,
        wallet_name=TRADER_A.wallet_name,
    )
    vega.create_key(
        name=TRADER_B.key_name,
        wallet_name=TRADER_B.wallet_name,
    )
    vega.wait_for_total_catchup()
    vega.wait_fn(60)

    # Mint settlement assets for traders
    vega.mint(
        wallet_name=TRADER_A.wallet_name,
        key_name=TRADER_A.key_name,
        asset=asset_id,
        amount=TRADER_MINT,
    )
    vega.mint(
        wallet_name=TRADER_B.wallet_name,
        key_name=TRADER_B.key_name,
        asset=asset_id,
        amount=TRADER_MINT,
    )
    vega.wait_for_total_catchup()
    vega.wait_fn(60)

    logging.info(
        f"Trader A Party: public_key = {vega.wallet.public_key(name=TRADER_A.key_name, wallet_name=TRADER_A.wallet_name)}"
    )
    logging.info(
        f"Trader B Party: public_key = {vega.wallet.public_key(name=TRADER_B.key_name, wallet_name=TRADER_B.wallet_name)}"
    )

    #0012-NP-LIPE-002: An estimate is obtained for a short position with no open orders, mark price keeps going up in small increments and the actual liquidation takes place within the estimated range. 
    vega.submit_order(
        trading_wallet=TRADER_A.wallet_name,
        trading_key=TRADER_A.key_name,
        market_id=market_id,
        time_in_force="TIME_IN_FORCE_GTC",
        order_type="TYPE_LIMIT",
        side="SIDE_BUY",
        volume=TRADER_POSITION,
        price=500,
    )
    vega.submit_order(
        trading_wallet=TRADER_B.wallet_name,
        trading_key=TRADER_B.key_name,
        market_id=market_id,
        time_in_force="TIME_IN_FORCE_GTC",
        order_type="TYPE_LIMIT",
        side="SIDE_SELL",
        volume=TRADER_POSITION,
        price=500,
    )
    vega.wait_for_total_catchup()
    vega.wait_fn(60)

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
        vega.wait_for_total_catchup()
        vega.wait_fn(60)

        trader_a_position = vega.positions_by_market(
            wallet_name=TRADER_A.wallet_name,
            key_name=TRADER_A.key_name,
            market_id=market_id,
        )
        trader_b_position = vega.positions_by_market(
            wallet_name=TRADER_B.wallet_name,
            key_name=TRADER_B.key_name,
            market_id=market_id,
        )
        account_TRADER_B = vega.party_account(
                key_name=TRADER_B.key_name,
                wallet_name=TRADER_B.wallet_name,
                asset_id=asset_id,  
                market_id=market_id,   
        )
        open_orders_TRADER_B = vega.list_orders(
                key_name=TRADER_B.key_name,
                wallet_name=TRADER_B.wallet_name,
                market_id=market_id,   
        )
        print(f"{account_TRADER_B} at price {price} = {account_TRADER_B}") 
        print(f"{account_TRADER_B}'s position at price {price} = {trader_b_position.open_volume}") 
        print(f"{account_TRADER_B}'s orders at price {price} = {open_orders_TRADER_B}") 
        if price == 663:
            collateral_available = account_TRADER_B.general + account_TRADER_B.bond + account_TRADER_B.margin

        if price == 664:
            # Check Trader B closed out and Trader A position still open
            assert trader_a_position.open_volume == TRADER_POSITION
            assert trader_a_position.unrealised_pnl > 0
            assert trader_b_position.open_volume == 0
            assert trader_b_position.unrealised_pnl == 0
            # Check loss socialisation was not required for close out
            assert trader_a_position.loss_socialisation_amount == 0
            assert trader_b_position.loss_socialisation_amount == 0
        else:
            # Check Trader A and Trader B positions are still open
            assert trader_a_position.open_volume == TRADER_POSITION
            assert trader_a_position.unrealised_pnl > 0
            assert trader_b_position.open_volume == -TRADER_POSITION                    
            assert trader_b_position.unrealised_pnl < 0

    market_info = vega.market_info(market_id=market_id)
    market_data = vega.get_latest_market_data(market_id=market_id)

    # print(f"market_info = {market_info}", type(market_info))
    print(f"market_data = {market_data}", type(market_data))
    print(f"market_info = {market_info}", type(market_info))
    print(f"collateral_available = {collateral_available}", type(collateral_available))
    estimate_margin_open_vol_only, estimate_liquidation_price_open_vol_only = vega.estimate_position(
        market_id,
        open_volume=-100,
        side=["SIDE_SELL"],
        price=[market_data.mark_price],
        remaining=[0, 0],
        is_market_order=[False, False],
        collateral_available=collateral_available,
    )
    print(f"estimate_liquidation_price_open_vol_only.best_case.open_volume_only = {estimate_liquidation_price_open_vol_only.best_case.open_volume_only}") 
    print(f"estimate_liquidation_price_open_vol_only.worst_case.open_volume_only = {estimate_liquidation_price_open_vol_only.worst_case.open_volume_only}") 
    assert market_data.mark_price <= round(estimate_liquidation_price_open_vol_only.best_case.open_volume_only/1e5,0)
    assert market_data.mark_price >= round(estimate_liquidation_price_open_vol_only.worst_case.open_volume_only/1e5,0)
    input("wait")