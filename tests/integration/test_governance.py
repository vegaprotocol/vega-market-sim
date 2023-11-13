import pytest

import vega_sim.proto.vega as vega_protos

from vega_sim.null_service import VegaServiceNull
from tests.integration.utils.fixtures import WalletConfig, vega_service


PARTY_A = WalletConfig(name="party_a", passphrase="pass")
PARTY_B = WalletConfig(name="party_b", passphrase="pass")


@pytest.mark.integration
def test_governance_transfer(vega_service: vega_service):
    vega: VegaServiceNull = vega_service

    vega.wallet.create_key(name=PARTY_A.name)

    vega.mint(key_name=PARTY_A.name, asset="VOTE", amount=1000)
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
