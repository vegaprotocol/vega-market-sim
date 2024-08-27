import pytest
from vega_protos import protos
from vega_sim.null_service import VegaServiceNull
from tests.integration.utils.fixtures import (
    ASSET_NAME,
    WalletConfig,
    create_and_faucet_wallet,
    vega_service,
)


PROPOSER = WalletConfig("proposer", "pass")
AUX_1 = WalletConfig("aux1", "pass")
AUX_2 = WalletConfig("aux2", "pass")
TRADER = WalletConfig("TRADER", "pass")

ASSET_NAME = "USDT"
MARKET_NAME = "BTC/USDT"

ASSET_DECIMALS = 0
PRICE_DECIMALS = 0
SIZE_DECIMALS = 0


@pytest.fixture(scope="function")
def test_setup(
    vega_service: VegaServiceNull,
):
    vega = vega_service

    # Create proposer key
    vega.create_key(PROPOSER.name)
    vega.mint(PROPOSER.name, vega.find_asset_id(symbol="VOTE", enabled=True), 1000)

    # Update network parameters so no fees are charged and the mark
    # price is not updated every trade.
    vega.update_network_parameter(
        PROPOSER.name,
        parameter="network.markPriceUpdateMaximumFrequency",
        new_value="0",
    )
    vega.wait_for_total_catchup()
    vega.update_network_parameter(
        PROPOSER.name,
        parameter="market.fee.factors.infrastructureFee",
        new_value="0",
    )
    vega.wait_for_total_catchup()
    vega.update_network_parameter(
        PROPOSER.name,
        parameter="market.fee.factors.makerFee",
        new_value="0",
    )
    vega.wait_for_total_catchup()

    # Create asset and market
    vega.create_asset(PROPOSER.name, ASSET_NAME, ASSET_NAME, ASSET_DECIMALS, quantum=1)
    vega.wait_for_total_catchup()
    asset_id = vega.find_asset_id(symbol=ASSET_NAME)
    vega.create_simple_market(
        market_name=MARKET_NAME,
        proposal_key=PROPOSER.name,
        settlement_asset_id=asset_id,
        termination_key=PROPOSER.name,
        market_decimals=PRICE_DECIMALS,
        position_decimals=SIZE_DECIMALS,
        forward_time_to_enactment=True,
    )
    vega.wait_for_total_catchup()
    market_id = vega.find_market_id(name=MARKET_NAME)

    # Faucet wallets
    create_and_faucet_wallet(vega=vega, wallet=AUX_1, symbol=ASSET_NAME, amount=1e9)
    create_and_faucet_wallet(vega=vega, wallet=AUX_2, symbol=ASSET_NAME, amount=1e9)

    # Exit the opening auction at a price of
    vega.submit_order(
        AUX_1.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=1,
        price=100000,
        wait=True,
    )
    vega.submit_order(
        AUX_2.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=1,
        price=100000,
        wait=True,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    assert (
        vega.get_latest_market_data(market_id=market_id).market_trading_mode
        == protos.vega.markets.Market.TradingMode.TRADING_MODE_CONTINUOUS
    )

    yield vega


@pytest.mark.integration
def test_liquidation_price_AC001(
    test_setup: VegaServiceNull,
):
    """Summary:
    An estimate is obtained for a long position with no open orders, mark price keeps
    going down in small increments and the actual liquidation takes place within the
    estimated range. (0012-NP-LIPE-001)
    """
    vega = test_setup

    # Initialise wallet with 20k USDT - yields initial leverage 5x
    create_and_faucet_wallet(vega=vega, wallet=TRADER, symbol=ASSET_NAME, amount=20e3)
    trader_id = vega.wallet.public_key(TRADER.name)
    market_id = vega.find_market_id(name=MARKET_NAME)

    # Trader enters a LONG position of size 1
    vega.submit_order(
        AUX_1.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=1,
        price=100000,
    )
    vega.submit_order(
        TRADER.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=1,
        price=100000,
        wait=True,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    # CHECK: Request information for the opened position and check it was created
    position = vega.list_all_positions(party_ids=[trader_id])[0]
    accounts = vega.party_account(
        key_name=TRADER.name,
        market_id=market_id,
    )
    assert position.market_id == market_id
    assert position.open_volume == 1

    _, _, liquidation_estimate = vega.estimate_position(
        market_id=market_id,
        open_volume=position.open_volume,
        average_entry_price=position.average_entry_price,
        general_account_balance=accounts.general,
        margin_account_balance=accounts.margin,
        order_margin_account_balance=0,
        margin_mode=protos.vega.vega.MarginMode.MARGIN_MODE_CROSS_MARGIN,
    )

    # Start DECREASING the price from slightly ABOVE the best case liquidation price
    # break the loop once liquidated or the target price is BELOW the worst case.
    target_price = int(liquidation_estimate.worst_case.open_volume_only + 5)
    increment = -1
    while target_price > liquidation_estimate.best_case.open_volume_only:
        # Update the mark price alternating which auxilary is the buyer and seller
        vega.submit_order(
            AUX_1.name,
            market_id=market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY" if target_price % 2 == 0 else "SIDE_SELL",
            volume=1,
            price=target_price,
            wait=True,
        )
        vega.submit_order(
            AUX_2.name,
            market_id=market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY" if target_price % 2 != 0 else "SIDE_SELL",
            volume=1,
            price=target_price,
            wait=True,
        )
        vega.wait_fn(1)
        vega.wait_for_total_catchup()

        # CHECK: the mark price is as expected and we still in continuous trading
        market_data = vega.get_latest_market_data(market_id=market_id)
        assert market_data.mark_price == target_price
        assert (
            market_data.market_trading_mode
            == protos.vega.markets.Market.TradingMode.TRADING_MODE_CONTINUOUS
        )

        # When the trader is liquidated, exit the loop
        position = vega.list_all_positions(party_ids=[trader_id])[0]
        if position.open_volume == 0:
            break
        target_price += increment

    # CHECK: the trader was liquidated and they were liquidated between the worst and
    # best case estimates.
    assert position.open_volume == 0
    assert market_data.mark_price <= liquidation_estimate.worst_case.open_volume_only
    assert market_data.mark_price >= liquidation_estimate.best_case.open_volume_only


@pytest.mark.integration
def test_liquidation_price_AC002(
    test_setup: VegaServiceNull,
):
    """Summary:
    An estimate is obtained for a short position with no open orders, mark price keeps
    going up in small increments and the actual liquidation takes place within the
    estimated range. (0012-NP-LIPE-002)
    """
    vega = test_setup

    # Initialise wallet with 20k USDT - yields initial leverage 5x
    create_and_faucet_wallet(vega=vega, wallet=TRADER, symbol=ASSET_NAME, amount=20e3)
    trader_id = vega.wallet.public_key(TRADER.name)
    market_id = vega.find_market_id(name=MARKET_NAME)

    # Trader enters a SHORT position of size -1
    vega.submit_order(
        AUX_1.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=1,
        price=100000,
    )
    vega.submit_order(
        TRADER.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=1,
        price=100000,
        wait=True,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    # CHECK: Request information for the opened position and check it was created
    position = vega.list_all_positions(party_ids=[trader_id])[0]
    accounts = vega.party_account(
        key_name=TRADER.name,
        market_id=market_id,
    )
    assert position.market_id == market_id
    assert position.open_volume == -1

    _, _, liquidation_estimate = vega.estimate_position(
        market_id=market_id,
        open_volume=position.open_volume,
        average_entry_price=position.average_entry_price,
        general_account_balance=accounts.general,
        margin_account_balance=accounts.margin,
        order_margin_account_balance=0,
        margin_mode=protos.vega.vega.MarginMode.MARGIN_MODE_CROSS_MARGIN,
    )

    # Start INCREASING the price from slightly BELOW the best case liquidation price
    # break the loop once liquidated or the target price is BEYOND the worst case.
    target_price = int(liquidation_estimate.worst_case.open_volume_only - 5)
    increment = +1
    while target_price < liquidation_estimate.best_case.open_volume_only:
        # Update the mark price alternating which auxilary is the buyer and seller
        vega.submit_order(
            AUX_1.name,
            market_id=market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY" if target_price % 2 == 0 else "SIDE_SELL",
            volume=1,
            price=target_price,
            wait=True,
        )
        vega.submit_order(
            AUX_2.name,
            market_id=market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY" if target_price % 2 != 0 else "SIDE_SELL",
            volume=1,
            price=target_price,
            wait=True,
        )
        vega.wait_fn(1)
        vega.wait_for_total_catchup()

        # CHECK: the mark price is as expected and we still in continuous trading
        market_data = vega.get_latest_market_data(market_id=market_id)
        assert market_data.mark_price == target_price
        assert (
            market_data.market_trading_mode
            == protos.vega.markets.Market.TradingMode.TRADING_MODE_CONTINUOUS
        )

        # When the trader is liquidated, exit the loop
        position = vega.list_all_positions(party_ids=[trader_id])[0]
        if position.open_volume == 0:
            break
        target_price += increment

    # CHECK: the trader was liquidated and they were liquidated between the worst
    # and best case estimates.
    assert position.open_volume == 0
    assert market_data.mark_price >= liquidation_estimate.worst_case.open_volume_only
    assert market_data.mark_price <= liquidation_estimate.best_case.open_volume_only


@pytest.mark.integration
def test_liquidation_price_AC003(
    test_setup: VegaServiceNull,
):
    """Summary:
    An estimate is obtained for a position with no open volume and a single limit buy
    order, after the order fills the mark price keeps going down in small increments and
    the actual liquidation takes place within the obtained estimated range.
    (0012-NP-LIPE-003)
    """
    vega = test_setup

    # Initialise wallet with 20k USDT - yields initial leverage 5x
    create_and_faucet_wallet(vega=vega, wallet=TRADER, symbol=ASSET_NAME, amount=20e3)
    trader_id = vega.wallet.public_key(TRADER.name)
    market_id = vega.find_market_id(name=MARKET_NAME)

    # Trader submits a BUY order which is not yet filled
    vega.submit_order(
        TRADER.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=1,
        price=100000,
        wait=True,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    accounts = vega.party_account(
        key_name=TRADER.name,
        market_id=market_id,
    )
    _, _, liquidation_estimate = vega.estimate_position(
        market_id=market_id,
        open_volume=0,
        average_entry_price=0,
        general_account_balance=accounts.general,
        margin_account_balance=accounts.margin,
        order_margin_account_balance=0,
        margin_mode=protos.vega.vega.MarginMode.MARGIN_MODE_CROSS_MARGIN,
        side=["SIDE_BUY"],
        price=[100000],
        remaining=[1],
        is_market_order=[False],
    )

    # Traders order is filled and enters a LONG position of size 1
    vega.submit_order(
        AUX_1.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=1,
        price=100000,
    )
    vega.wait_fn()
    vega.wait_for_total_catchup()

    # CHECK: Request information for the opened position and check it was created
    position = vega.list_all_positions(party_ids=[trader_id])[0]
    assert position.market_id == market_id
    assert position.open_volume == 1

    # Start DECREASING the price from slightly ABOVE the best case liquidation price
    # break the loop once liquidated or the target price is BELOW the worst case.
    target_price = int(liquidation_estimate.worst_case.including_buy_orders + 5)
    increment = -1
    while target_price > liquidation_estimate.best_case.including_buy_orders:
        # Update the mark price alternating which auxilary is the buyer and seller
        vega.submit_order(
            AUX_1.name,
            market_id=market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY" if target_price % 2 == 0 else "SIDE_SELL",
            volume=1,
            price=target_price,
            wait=True,
        )
        vega.submit_order(
            AUX_2.name,
            market_id=market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY" if target_price % 2 != 0 else "SIDE_SELL",
            volume=1,
            price=target_price,
            wait=True,
        )
        vega.wait_fn(1)
        vega.wait_for_total_catchup()

        # CHECK: the mark price is as expected and we still in continuous trading
        market_data = vega.get_latest_market_data(market_id=market_id)
        assert market_data.mark_price == target_price
        assert (
            market_data.market_trading_mode
            == protos.vega.markets.Market.TradingMode.TRADING_MODE_CONTINUOUS
        )

        # When the trader is liquidated, exit the loop
        position = vega.list_all_positions(party_ids=[trader_id])[0]
        if position.open_volume == 0:
            break
        target_price += increment

    # CHECK: the trader was liquidated and they were liquidated between the best and worst case
    assert position.open_volume == 0
    assert market_data.mark_price >= liquidation_estimate.best_case.including_buy_orders
    assert (
        market_data.mark_price <= liquidation_estimate.worst_case.including_buy_orders
    )


@pytest.mark.integration
def test_liquidation_price_AC004(
    test_setup: VegaServiceNull,
):
    """Summary:
    An estimate for cross-margin mode with
    include_collateral_increase_in_available_collateral set to true is obtained for a
    long position with multiple limit sell orders with the absolute value of the total
    remaining size of the orders less than the open volume. The general account balance
    should be set to 0 in the query and the margin account balance should be set to the
    maintenance margin for the chosen position. Orders should be chosen so that the
    liquidation price estimate with sell orders is non-zero (otherwise the party is
    collateralised up to a point that it will never get liquidated if these orders
    fill). The estimated liquidation price with sell orders is lower than that for the
    open volume only. As the limit orders get filled the estimated liquidation price for
    the (updated) open volume converges to the estimate originally obtained with open
    sell orders. (0012-NP-LIPE-004)
    """
    vega = test_setup

    # Initialise wallet with 100k USDT - yields initial leverage 5x
    create_and_faucet_wallet(vega=vega, wallet=TRADER, symbol=ASSET_NAME, amount=100e3)
    trader_id = vega.wallet.public_key(TRADER.name)
    market_id = vega.find_market_id(name=MARKET_NAME)

    # Trader enters a LONG position of size 5
    vega.submit_order(
        AUX_1.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=5,
        price=100000,
    )
    vega.submit_order(
        TRADER.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=5,
        price=100000,
        wait=True,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    # CHECK: Request information for the opened position and check it was created
    original_position = vega.list_all_positions(party_ids=[trader_id])[0]
    accounts = vega.party_account(
        key_name=TRADER.name,
        market_id=market_id,
    )
    assert original_position.market_id == market_id
    assert original_position.open_volume == 5

    # Submit three SELL orders at prices 100100, 100200, 100300 all of size 1
    prices = [100100, 100200, 100300]
    for price in prices:
        vega.submit_order(
            TRADER.name,
            market_id=market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_SELL",
            volume=1,
            price=price,
            wait=True,
        )

    _, _, original_liquidation_estimate = vega.estimate_position(
        market_id=market_id,
        open_volume=original_position.open_volume,
        average_entry_price=original_position.average_entry_price,
        general_account_balance=accounts.general,
        margin_account_balance=accounts.margin,
        order_margin_account_balance=0,
        margin_mode=protos.vega.vega.MarginMode.MARGIN_MODE_CROSS_MARGIN,
        side=["SIDE_SELL", "SIDE_SELL", "SIDE_SELL"],
        price=prices,
        remaining=[1, 1, 1],
        is_market_order=[False, False, False],
        include_required_position_margin_in_available_collateral=True,
    )

    # CHECK: the liquidation price from open volume only is worse than when including
    # the collateral increase from the sell orders.
    assert (
        original_liquidation_estimate.best_case.including_sell_orders
        < original_liquidation_estimate.best_case.open_volume_only
    )
    assert (
        original_liquidation_estimate.worst_case.including_sell_orders
        < original_liquidation_estimate.worst_case.open_volume_only
    )

    last_position = original_position
    last_liquidation_estimate = original_liquidation_estimate
    for i, price in enumerate(prices):
        # Fill each of the orders one by one, checking the open volume only converges to the
        # original including sell orders estimate.
        vega.submit_order(
            AUX_1.name,
            market_id=market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY",
            volume=1,
            price=price,
            wait=True,
        )
        vega.wait_fn(1)
        vega.wait_for_total_catchup()

        # CHECK: Request information for the position and check its size reduced
        new_position = vega.list_all_positions(party_ids=[trader_id])[0]
        accounts = vega.party_account(
            key_name=TRADER.name,
            market_id=market_id,
        )
        assert abs(new_position.open_volume) < abs(last_position.open_volume)

        _, _, new_liquidation_estimate = vega.estimate_position(
            market_id=market_id,
            open_volume=new_position.open_volume,
            average_entry_price=new_position.average_entry_price,
            general_account_balance=accounts.general,
            margin_account_balance=accounts.margin,
            order_margin_account_balance=0,
            margin_mode=protos.vega.vega.MarginMode.MARGIN_MODE_CROSS_MARGIN,
            side=["SIDE_SELL"] * (len(prices) - i),
            price=prices[i + 1 :],
            remaining=[1] * (len(prices) - i),
            is_market_order=[False] * (len(prices) - i),
            include_required_position_margin_in_available_collateral=True,
        )
        # CHECK: liquidation price from open volume only is reducing as the position
        # size decreases converging on the original estimate.
        assert (
            new_liquidation_estimate.best_case.open_volume_only
            < last_liquidation_estimate.best_case.open_volume_only
        )
        last_position = new_position
        last_liquidation_estimate = new_liquidation_estimate

    # CHECK: the final open volume only estimate is equal to the original including
    # sell orders estimate. Do this for the best and worst case estimates.
    assert (
        original_liquidation_estimate.best_case.including_sell_orders
        == last_liquidation_estimate.best_case.open_volume_only
    )
    assert (
        original_liquidation_estimate.worst_case.including_sell_orders
        == last_liquidation_estimate.worst_case.open_volume_only
    )


@pytest.mark.integration
def test_liquidation_price_AC005(
    test_setup: VegaServiceNull,
):
    """Summary:
    An estimate for cross-margin mode with
    include_collateral_increase_in_available_collateral set to true is obtained for a
    short position with multiple limit buy orders with the absolute value of the total
    remaining size of the orders less than the open volume. The general account balance
    should be set to 0 in the query and the margin account balance should be set to the
    maintenance margin for the chosen position. The estimated liquidation price with buy
    orders is higher than that for the open volume only. As the limit orders get filled
    the estimated liquidation price for the (updated) open volume converges to the
    estimate originally obtained with open buy orders. As the price keeps moving in
    small increments the liquidation happens within the originally estimated range
    (with buy orders) (0012-NP-LIPE-005)
    """
    vega = test_setup

    # Initialise wallet with 100k USDT - yields initial leverage 5x
    create_and_faucet_wallet(vega=vega, wallet=TRADER, symbol=ASSET_NAME, amount=100e3)
    trader_id = vega.wallet.public_key(TRADER.name)
    market_id = vega.find_market_id(name=MARKET_NAME)

    # Trader enters a SHORT position of size -5
    vega.submit_order(
        AUX_1.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        volume=5,
        price=100000,
    )
    vega.submit_order(
        TRADER.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        volume=5,
        price=100000,
        wait=True,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    # CHECK: Request information for the opened position and check it was created
    original_position = vega.list_all_positions(party_ids=[trader_id])[0]
    accounts = vega.party_account(
        key_name=TRADER.name,
        market_id=market_id,
    )
    assert original_position.market_id == market_id
    assert original_position.open_volume == -5

    # Submit three BUY orders at prices 99900, 99800, 99700 all of size 1
    prices = [99900, 99800, 99700]
    for price in prices:
        vega.submit_order(
            TRADER.name,
            market_id=market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY",
            volume=1,
            price=price,
            wait=True,
        )

    _, _, original_liquidation_estimate = vega.estimate_position(
        market_id=market_id,
        open_volume=original_position.open_volume,
        average_entry_price=original_position.average_entry_price,
        general_account_balance=accounts.general,
        margin_account_balance=accounts.margin,
        order_margin_account_balance=0,
        margin_mode=protos.vega.vega.MarginMode.MARGIN_MODE_CROSS_MARGIN,
        side=["SIDE_BUY", "SIDE_BUY", "SIDE_BUY"],
        price=prices,
        remaining=[1, 1, 1],
        is_market_order=[False, False, False],
        include_required_position_margin_in_available_collateral=True,
    )

    # CHECK: the liquidation price from open volume only is worse than when including
    # the collateral increase from the buy orders.
    assert (
        original_liquidation_estimate.best_case.including_buy_orders
        > original_liquidation_estimate.best_case.open_volume_only
    )
    assert (
        original_liquidation_estimate.worst_case.including_buy_orders
        > original_liquidation_estimate.worst_case.open_volume_only
    )

    last_position = original_position
    last_liquidation_estimate = original_liquidation_estimate
    for i, price in enumerate(prices):
        # Fill each of the orders one by one, checking the open volume only converges to the
        # original including sell orders estimate.
        vega.submit_order(
            AUX_1.name,
            market_id=market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_SELL",
            volume=1,
            price=price,
            wait=True,
        )
        vega.wait_fn(1)
        vega.wait_for_total_catchup()

        # CHECK: Request information for the position and check its size reduced
        new_position = vega.list_all_positions(party_ids=[trader_id])[0]
        accounts = vega.party_account(
            key_name=TRADER.name,
            market_id=market_id,
        )
        assert abs(new_position.open_volume) < abs(last_position.open_volume)

        _, _, new_liquidation_estimate = vega.estimate_position(
            market_id=market_id,
            open_volume=new_position.open_volume,
            average_entry_price=new_position.average_entry_price,
            general_account_balance=accounts.general,
            margin_account_balance=accounts.margin,
            order_margin_account_balance=0,
            margin_mode=protos.vega.vega.MarginMode.MARGIN_MODE_CROSS_MARGIN,
            side=["SIDE_BUY"] * (len(prices) - i),
            price=prices[i + 1 :],
            remaining=[1] * (len(prices) - i),
            is_market_order=[False] * (len(prices) - i),
            include_required_position_margin_in_available_collateral=True,
        )
        # CHECK: liquidation price from open volume only is increasing as the position
        # size decreases converging on the original estimate.
        assert (
            new_liquidation_estimate.best_case.open_volume_only
            > last_liquidation_estimate.best_case.open_volume_only
        )
        last_position = new_position
        last_liquidation_estimate = new_liquidation_estimate

    # CHECK: the final open volume only estimate is equal to the original including
    # sell orders estimate. Do this for the best and worst case estimates.
    assert (
        original_liquidation_estimate.best_case.including_buy_orders
        == last_liquidation_estimate.best_case.open_volume_only
    )
    assert (
        original_liquidation_estimate.worst_case.including_buy_orders
        == last_liquidation_estimate.worst_case.open_volume_only
    )
