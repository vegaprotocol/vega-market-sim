import pytest
import vega_sim.proto.vega as vega_protos
from vega_sim.api.market import MarketConfig
import vega_sim.builders as build

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
    )
    vega.wait_fn(10)
    vega.wait_for_total_catchup()

    liq_provis = vega.party_liquidity_provisions(LIQ.name, market_id=market_id)
    assert len(liq_provis) == 1
    assert liq_provis[0].fee == "0.001"

    vega.wait_for_total_catchup()
    vega.submit_liquidity(
        LIQ.name,
        market_id=market_id,
        commitment_amount=200,
        fee=0.005,
    )
    vega.wait_fn(10)
    vega.wait_for_total_catchup()

    liq_provis = vega.party_liquidity_provisions(LIQ.name, market_id=market_id)

    assert len(liq_provis) == 1
    assert liq_provis[0].fee == "0.005"
    assert liq_provis[0].commitment_amount == "20000000"


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
        market_id=market_id,
    )
    party_b_accounts_t1 = vega.party_account(
        key_name=PARTY_B.name,
        market_id=market_id,
    )

    all_transfers_t1 = vega.list_transfers(
        key_name=PARTY_A.name,
    )
    live_transfers_t1 = vega.transfer_status_from_feed(live_only=True)

    assert len(all_transfers_t1) >= 1
    assert len(live_transfers_t1) == 0

    assert party_a_accounts_t1.general == 499.999
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
        market_id=market_id,
    )
    party_b_accounts_t2 = vega.party_account(
        key_name=PARTY_B.name,
        market_id=market_id,
    )

    all_transfers_t2 = vega.list_transfers(
        key_name=PARTY_A.name,
    )
    live_transfers_t2 = vega.transfer_status_from_feed(live_only=True)

    assert len(all_transfers_t2) >= 2
    assert len(live_transfers_t2) == 1
    assert party_a_accounts_t2.general == 499.999
    assert party_b_accounts_t2.general == 999.999

    vega.wait_fn(100)
    vega.wait_for_total_catchup()

    party_a_accounts_t3 = vega.party_account(
        key_name=PARTY_A.name,
        market_id=market_id,
    )
    party_b_accounts_t3 = vega.party_account(
        key_name=PARTY_B.name,
        market_id=market_id,
    )

    all_transfers_t3 = vega.list_transfers(
        key_name=PARTY_A.name,
    )
    live_transfers_t3 = vega.transfer_status_from_feed(live_only=True)

    assert len(all_transfers_t3) >= 2
    assert len(live_transfers_t3) == 0
    assert party_a_accounts_t3.general == 999.999
    assert party_b_accounts_t3.general == 999.999


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

    assert party_a_accounts_t1[0].balance == 499.999
    assert party_b_accounts_t1[0].balance == 1500

    # Forward one epoch
    next_epoch(vega=vega)

    party_a_accounts_t2 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)
    party_b_accounts_t2 = vega.list_accounts(key_name=PARTY_B.name, asset_id=asset_id)

    assert party_a_accounts_t2[0].balance == 249.998
    assert party_b_accounts_t2[0].balance == 1750


@pytest.mark.integration
def test_funding_reward_pool(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    market_id = vega.all_markets()[0].id
    asset_id = vega.find_asset_id(symbol=ASSET_NAME, raise_on_missing=True)

    create_and_faucet_wallet(vega=vega, wallet=PARTY_A, amount=1e3)
    create_and_faucet_wallet(vega=vega, wallet=PARTY_B, amount=1e5)
    create_and_faucet_wallet(vega=vega, wallet=PARTY_C, amount=1e5)
    vega.wait_for_total_catchup()

    # Forward one epoch
    next_epoch(vega=vega)

    vega.recurring_transfer(
        from_key_name=PARTY_A.name,
        from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
        to_account_type=vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_PAID_FEES,
        asset=asset_id,
        asset_for_metric=asset_id,
        metric=vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_PAID,
        amount=100,
        factor=1.0,
        cap_reward_fee_multiple=10,
        lock_period=10,
    )
    # Generate trades for non-zero metrics
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=0.30,
        volume=10000,
    )
    vega.submit_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=0.30,
        volume=10000,
    )
    vega.wait_for_total_catchup()

    party_a_accounts_t0 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)

    assert party_a_accounts_t0[0].balance == 1000

    # Forward one epoch
    next_epoch(vega=vega)

    party_a_accounts_t1 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)
    party_c_vesting_account = [
        account
        for account in vega.list_accounts(key_name=PARTY_C.name, asset_id=asset_id)
        if account.type == vega_protos.vega.AccountType.ACCOUNT_TYPE_VESTING_REWARDS
    ][0]

    assert party_a_accounts_t1[0].balance == 899.999
    assert party_c_vesting_account.balance == 81
    # Forward one epoch
    next_epoch(vega=vega)

    party_a_accounts_t2 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)

    assert party_a_accounts_t2[0].balance == 899.999


@pytest.mark.integration
def test_iceberg_order(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    vega.wait_for_total_catchup()

    create_and_faucet_wallet(vega=vega, wallet=PARTY_A, amount=1e5)
    create_and_faucet_wallet(vega=vega, wallet=PARTY_B, amount=1e5)
    create_and_faucet_wallet(vega=vega, wallet=PARTY_C, amount=1e5)
    vega.wait_for_total_catchup()

    market_id = vega.all_markets()[0].id

    vega.submit_liquidity(
        MM_WALLET.name,
        market_id=market_id,
        commitment_amount=100,
        fee=0.001,
        is_amendment=True,
    )

    with pytest.raises(ValueError):
        vega.submit_order(
            trading_key=PARTY_A.name,
            market_id=market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY",
            price=0.29,
            volume=10,
            peak_size=5,
        )
    with pytest.raises(ValueError):
        vega.submit_order(
            trading_key=PARTY_A.name,
            market_id=market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY",
            price=0.29,
            volume=10,
            minimum_visible_size=2,
        )

    # Place icebergs orders
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=0.29,
        volume=10,
        peak_size=5,
        minimum_visible_size=2,
    )
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=0.31,
        volume=10,
        peak_size=5,
        minimum_visible_size=2,
    )

    # Place limit order at same price levels
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=0.29,
        volume=1000,
    )
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=0.31,
        volume=1000,
    )
    vega.wait_for_total_catchup()

    # Place market orders and check only the displayed volume is filled
    vega.submit_market_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        fill_or_kill=False,
        side="SIDE_SELL",
        volume=10,
    )
    vega.wait_for_total_catchup()

    position = vega.positions_by_market(key_name=PARTY_A.name, market_id=market_id)
    assert position.open_volume == 5

    # Place market orders and check only the displayed volume is filled
    vega.submit_market_order(
        trading_key=PARTY_C.name,
        market_id=market_id,
        fill_or_kill=False,
        side="SIDE_BUY",
        volume=10,
    )
    vega.wait_for_total_catchup()

    position = vega.positions_by_market(key_name=PARTY_A.name, market_id=market_id)
    assert position.open_volume == 0


@pytest.mark.integration
def test_referral_sets(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market

    create_and_faucet_wallet(vega=vega, wallet=PARTY_A)
    vega.wait_for_total_catchup()
    create_and_faucet_wallet(vega=vega, wallet=PARTY_B)
    vega.wait_for_total_catchup()
    referrer_id = vega.wallet.public_key(name=PARTY_A.name)
    referee_id = vega.wallet.public_key(name=PARTY_B.name)

    vega.create_referral_set(key_name=PARTY_A.name)
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    referral_set_id = list(vega.list_referral_sets().keys())[0]
    vega.apply_referral_code(key_name=PARTY_B.name, id=referral_set_id)
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    # Check we can request a referral set by referral set id
    referral_set = vega.list_referral_sets(referral_set_id=referral_set_id)
    assert referral_set[referral_set_id].id == referral_set_id
    assert referral_set[referral_set_id].referrer == referrer_id

    # Check we can request a referral set by referrer
    referral_set = vega.list_referral_sets(referrer=referrer_id)
    assert referral_set[referral_set_id].id == referral_set_id
    assert referral_set[referral_set_id].referrer == referrer_id

    # Check we can request a referral set by referee
    referral_set = vega.list_referral_sets(referee=referee_id)
    assert referral_set[referral_set_id].id == referral_set_id
    assert referral_set[referral_set_id].referrer == referrer_id

    # Check we can request all referral set referees
    referees = vega.list_referral_set_referees()
    assert referees[referral_set_id][referee_id].referee == referee_id
    assert referees[referral_set_id][referee_id].referral_set_id == referral_set_id

    # Check we can request referral set referees by referral set id
    referees = vega.list_referral_set_referees(referral_set_id=referral_set_id)
    assert referees[referral_set_id][referee_id].referee == referee_id
    assert referees[referral_set_id][referee_id].referral_set_id == referral_set_id

    # Check we can request referral set referees by referrer id
    referees = vega.list_referral_set_referees(referrer=referrer_id)
    assert referees[referral_set_id][referee_id].referee == referee_id
    assert referees[referral_set_id][referee_id].referral_set_id == referral_set_id

    # Check we can request referral set referees by referee id
    referees = vega.list_referral_set_referees(referee=referee_id)
    assert referees[referral_set_id][referee_id].referee == referee_id
    assert referees[referral_set_id][referee_id].referral_set_id == referral_set_id


@pytest.mark.integration
def test_referral_program(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    vega.update_referral_program(
        proposal_key=MM_WALLET.name,
        benefit_tiers=[
            {
                "minimum_running_notional_taker_volume": 10000,
                "minimum_epochs": 1,
                "referral_reward_factor": 0.01,
                "referral_discount_factor": 0.01,
            },
            {
                "minimum_running_notional_taker_volume": 20000,
                "minimum_epochs": 2,
                "referral_reward_factor": 0.02,
                "referral_discount_factor": 0.02,
            },
            {
                "minimum_running_notional_taker_volume": 30000,
                "minimum_epochs": 3,
                "referral_reward_factor": 0.03,
                "referral_discount_factor": 0.03,
            },
        ],
        staking_tiers=[
            {"minimum_staked_tokens": 100, "referral_reward_multiplier": 1},
            {"minimum_staked_tokens": 1000, "referral_reward_multiplier": 2},
            {"minimum_staked_tokens": 10000, "referral_reward_multiplier": 2},
        ],
        window_length=1,
    )
    next_epoch(vega=vega)
    referral_program = vega.get_current_referral_program()
    assert referral_program is not None


@pytest.mark.integration
def test_volume_discount_program(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    market_id = vega.all_markets()[0].id
    create_and_faucet_wallet(vega=vega, wallet=PARTY_A, amount=1e9)
    vega.wait_for_total_catchup()
    create_and_faucet_wallet(vega=vega, wallet=PARTY_B, amount=1e9)
    vega.wait_for_total_catchup()
    vega.update_volume_discount_program(
        proposal_key=MM_WALLET.name,
        benefit_tiers=[
            {
                "minimum_running_notional_taker_volume": 1,
                "volume_discount_factor": 0.01,
            },
        ],
        window_length=7,
    )
    next_epoch(vega=vega)
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=0.30,
        volume=100,
    )
    vega.wait_fn(1)
    non_discounted_order_id = vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=0.30,
        volume=100,
        wait=True,
    )
    non_discounted_trades = vega.get_trades(
        market_id=market_id, order_id=non_discounted_order_id
    )
    assert vega.get_current_volume_discount_program() is not None
    assert non_discounted_trades[0].seller_fee.maker_fee_volume_discount == 0
    assert non_discounted_trades[0].seller_fee.liquidity_fee_volume_discount == 0
    assert non_discounted_trades[0].seller_fee.infrastructure_fee_volume_discount == 0
    next_epoch(vega=vega)
    assert vega.get_volume_discount_stats(key_name=PARTY_B.name) is not None
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=0.30,
        volume=10000,
    )
    vega.wait_fn(1)
    discounted_order_id = vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=0.30,
        volume=10000,
        wait=True,
    )
    discounted_trades = vega.get_trades(
        market_id=market_id, order_id=discounted_order_id
    )
    assert discounted_trades[0].buyer_fee.maker_fee_volume_discount != 0
    assert discounted_trades[0].buyer_fee.liquidity_fee_volume_discount != 0
    assert discounted_trades[0].buyer_fee.infrastructure_fee_volume_discount != 0


@pytest.mark.integration
@pytest.mark.skip(reason="Skipping as team features currently disabled.")
def test_teams(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market

    # Initialise parties
    create_and_faucet_wallet(vega=vega, wallet=PARTY_A)
    vega.wait_for_total_catchup()
    create_and_faucet_wallet(vega=vega, wallet=PARTY_B)
    vega.wait_for_total_catchup()
    create_and_faucet_wallet(vega=vega, wallet=PARTY_C)
    vega.wait_for_total_catchup()

    # Create referral sets, teams from sets, then get team ids
    vega.create_referral_set(
        key_name=PARTY_A.name,
        name="name_a",
        team_url="team_url_a",
        avatar_url="avatar_url_a",
        closed=False,
    )
    vega.create_referral_set(
        key_name=PARTY_B.name,
        name="name_b",
        team_url="team_url_b",
        avatar_url="avatar_url_b",
        closed=False,
    )
    vega.wait_fn((1))
    vega.wait_for_total_catchup()
    team_a_id = list(vega.list_teams(key_name=PARTY_A.name).keys())[0]
    team_b_id = list(vega.list_teams(key_name=PARTY_B.name).keys())[0]

    # Apply code and check the party has joined team
    vega.apply_referral_code(key_name=PARTY_C.name, id=team_a_id)
    next_epoch(vega)
    assert len(vega.list_team_referees(team_id=team_a_id)) > 0
    assert len(vega.list_team_referees(team_id=team_b_id)) == 0

    # Apply code and check the party has moved team
    vega.apply_referral_code(key_name=PARTY_C.name, id=team_b_id)
    next_epoch(vega)
    assert len(vega.list_team_referees(team_id=team_a_id)) == 0
    assert len(vega.list_team_referees(team_id=team_b_id)) > 0

    # Check the history is consistent
    team_referee_history = [
        team_referee_history.team_id
        for team_referee_history in vega.list_team_referee_history(
            key_name=PARTY_C.name
        )
    ]
    assert team_a_id in team_referee_history
    assert team_b_id in team_referee_history


@pytest.mark.integration
def test_stop_order(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    # Party A places the stop order
    create_and_faucet_wallet(vega=vega, wallet=PARTY_A, amount=1e9)
    vega.wait_for_total_catchup()
    # Parties B and C move the mark price, triggering the stop
    create_and_faucet_wallet(vega=vega, wallet=PARTY_B, amount=1e9)
    vega.wait_for_total_catchup()
    create_and_faucet_wallet(vega=vega, wallet=PARTY_C, amount=1e9)
    vega.wait_for_total_catchup()
    market_id = vega.all_markets()[0].id

    # Party A opens a position
    vega.submit_order(
        trading_key=PARTY_A.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_BUY",
        price=0.30,
        volume=1,
    )
    vega.submit_order(
        trading_key=PARTY_B.name,
        market_id=market_id,
        order_type="TYPE_LIMIT",
        time_in_force="TIME_IN_FORCE_GTC",
        side="SIDE_SELL",
        price=0.30,
        volume=1,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    # Build a stop order and submit it
    order_submission = vega.build_order_submission(
        market_id=market_id,
        size=1,
        side=vega_protos.vega.SIDE_SELL,
        order_type=vega_protos.vega.Order.TYPE_LIMIT,
        price=5.0,
        time_in_force=vega_protos.vega.Order.TIME_IN_FORCE_IOC,
        reduce_only=True,
    )
    stop_order_setup = build.commands.commands.stop_order_setup(
        market_price_decimals=vega.market_price_decimals,
        market_id=market_id,
        order_submission=order_submission,
        price=0.4,
    )
    stop_orders_submission = build.commands.commands.stop_orders_submission(
        rises_above=stop_order_setup,
        falls_below=None,
    )
    vega.submit_stop_order(
        stop_orders_submission=stop_orders_submission, key_name=PARTY_A.name
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()

    assert (
        len(
            vega.list_stop_orders(
                statuses=[vega_protos.vega.StopOrder.STATUS_PENDING],
            )
        )
        > 0
    )
