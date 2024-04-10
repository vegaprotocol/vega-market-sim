import pytest
import datetime

import vega_sim.proto.vega as vega_protos

from vega_sim.null_service import VegaServiceNull
from tests.integration.utils.fixtures import WalletConfig, vega_service


MARKET_PROPOSER = WalletConfig(name="proposer", passphrase="pass")
PARTY_A = WalletConfig(name="party_a", passphrase="pass")
PARTY_B = WalletConfig(name="party_b", passphrase="pass")


@pytest.mark.integration
def test_governance_transfer(vega_service: vega_service):
    vega: VegaServiceNull = vega_service

    vega.wallet.create_key(name=PARTY_A.name)

    vega.mint(
        key_name=PARTY_A.name,
        asset=vega.find_asset_id(symbol="VOTE", enabled=True),
        amount=1000,
    )
    vega.wait_for_total_catchup()

    vega.create_asset(key_name=PARTY_A.name, name="USDT", symbol="USDT")
    vega.wait_for_total_catchup()
    asset_id = vega.find_asset_id(symbol="USDT", raise_on_missing=True)

    vega.mint(key_name=PARTY_A.name, asset=asset_id, amount=1000)
    vega.wait_for_total_catchup()

    # Get and check party account balance
    party_a_account_t0 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)
    assert party_a_account_t0[0].balance == 1000

    # Transfer funds to a
    vega.one_off_transfer(
        from_key_name=PARTY_A.name,
        from_account_type=vega_protos.vega.ACCOUNT_TYPE_GENERAL,
        to_account_type=vega_protos.vega.ACCOUNT_TYPE_NETWORK_TREASURY,
        asset=asset_id,
        amount=500,
    )
    vega.wait_fn(5)
    vega.wait_for_total_catchup()

    # Get and check party account balance
    party_a_account_t1 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)
    assert party_a_account_t1[0].balance == 500

    # Propose returning funds to the party
    party_a_public_key = vega.wallet.public_key(name=PARTY_A.name)
    vega.propose_transfer(
        key_name=PARTY_A.name,
        source_type=vega_protos.vega.ACCOUNT_TYPE_NETWORK_TREASURY,
        transfer_type=vega_protos.governance.GOVERNANCE_TRANSFER_TYPE_ALL_OR_NOTHING,
        amount=500,
        fraction_of_balance=1.0,
        asset=asset_id,
        destination_type="ACCOUNT_TYPE_GENERAL",
        destination=party_a_public_key,
    )
    vega.wait_fn(5)
    vega.wait_for_total_catchup()

    # Get and check party account balance
    party_a_account_t1 = vega.list_accounts(key_name=PARTY_A.name, asset_id=asset_id)
    assert party_a_account_t1[0].balance == 1000


@pytest.mark.integration
def test_create_simple_spot_market(vega_service: vega_service):
    vega: VegaServiceNull = vega_service

    vega.wallet.create_key(name=PARTY_A.name)

    vega.create_key(name=MARKET_PROPOSER.name)
    vega.wait_for_total_catchup()

    asset_id = vega.find_asset_id("VOTE")
    vega.mint(MARKET_PROPOSER.name, asset=asset_id, amount=1000)
    vega.wait_for_total_catchup()

    vega.create_asset(MARKET_PROPOSER.name, "Bitcoin", "BTC", 6, 1)
    vega.create_asset(MARKET_PROPOSER.name, "Tether", "USDT", 6, 1)
    vega.wait_for_total_catchup()

    base_asset_id = vega.find_asset_id("BTC")
    quote_asset_id = vega.find_asset_id("USDT")

    vega.create_simple_spot_market(
        proposal_key_name=MARKET_PROPOSER.name,
        market_name="Bitcoin / Tether USD (Spot)",
        market_code="BTC/USDT-SPOT",
        base_asset_id=base_asset_id,
        quote_asset_id=quote_asset_id,
        market_decimal_places=1,
        position_decimal_places=2,
        tick_size=10,
    )
    vega.wait_for_total_catchup()
    assert (
        vega.find_market_id("Bitcoin / Tether USD (Spot)", raise_on_missing=True)
        is not None
    )


def test_market_termination_time(vega_service: VegaServiceNull):
    vega = vega_service

    # Initialise the proposer
    vega.create_key(name=MARKET_PROPOSER.name)
    vega.wait_for_total_catchup()
    asset_id = vega.find_asset_id("VOTE")
    vega.mint(MARKET_PROPOSER.name, asset=asset_id, amount=1000)
    vega.wait_for_total_catchup()

    # Create the settlement asset and mint for auxiliary parties
    vega.create_asset(MARKET_PROPOSER.name, "Tether", "USDT", 6, 1)
    vega.wait_for_total_catchup()
    asset_id = vega.find_asset_id("USDT")

    # Create the market
    current_timestamp = vega.get_blockchain_time(in_seconds=True)
    vote_closing_time = datetime.datetime.fromtimestamp(current_timestamp + 60)
    vote_enactment_time = datetime.datetime.fromtimestamp(current_timestamp + 120)
    termination_time = datetime.datetime.fromtimestamp(current_timestamp + 180)
    market_id = vega.create_simple_market(
        proposal_key=MARKET_PROPOSER.name,
        termination_key=MARKET_PROPOSER.name,
        market_name="Bitcoin / Tether USD",
        settlement_asset_id=asset_id,
        market_decimals=1,
        position_decimals=2,
        vote_closing_time=vote_closing_time,
        vote_enactment_time=vote_enactment_time,
        termination_time=termination_time,
    )

    # Check the market was created and termination time not reached
    vega.wait_for_total_catchup()
    market_info = vega.market_info(market_id=market_id)
    blockchain_time = vega.get_blockchain_time(in_seconds=True)
    assert blockchain_time > vote_enactment_time.timestamp()
    assert blockchain_time < termination_time.timestamp()
    assert market_info.state == vega_protos.markets.Market.State.STATE_PENDING

    # Advance time to termination (with a healthy buffer)
    vega.wait_fn(71)
    vega.wait_for_total_catchup()
    market_info = vega.market_info(market_id=market_id)
    blockchain_time = vega.get_blockchain_time(in_seconds=True)
    assert blockchain_time > vote_enactment_time.timestamp()
    assert blockchain_time > termination_time.timestamp()
    assert market_info.state == vega_protos.markets.Market.State.STATE_CANCELLED
