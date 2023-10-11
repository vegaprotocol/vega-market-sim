import pytest
import logging
from collections import namedtuple
import vega_sim.proto.vega as vega_protos
from examples.visualisations.utils import continuous_market, move_market
from vega_sim.scenario.configurable_market.agents import ConfigurableMarketManager
from vega_sim.api.market import MarketConfig

from tests.integration.utils.fixtures import (
    ASSET_NAME,
    MM_WALLET,
    WalletConfig,
    create_and_faucet_wallet,
    vega_spam_service,
    vega_service_with_high_volume,
    vega_service_with_high_volume_with_market,
    vega_spam_service_with_market,
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
def test_spam_referral_sets_max_block(vega_spam_service_with_market: VegaServiceNull):
    """
    A party who has more than 50% of their CreateReferralSet transactions post-block rejected should be banned for 1/48th of an
    epoch or untill the end of the current epoch (whichever comes first). When banned for the above reason,
    CreateReferralSet transactions should be pre-block rejected (0062-SPAM-033).

    Test1
    spam.protection.max.CreateReferralSet=3
    epoch1
    block1 = 1
    block2 = 1
    block3 = 1 - (2nd tx is post block rejected)

    Test2
    spam.protection.max.CreateReferralSet=3
    epoch1
      block1 = 3 (4th tx is rejected)
      block2 = 1 (tx is rejected)
    """
    # Arrange
    vega = vega_spam_service_with_market

    assert (
        vega.spam_protection == True
    ), "test pre-requisite, need to enable spam protection"

    create_and_faucet_wallet(vega=vega, wallet=MM_WALLET, symbol="VOTE")
    vega.wait_for_total_catchup()
    # Access the updated value
    vega.update_network_parameter(
        MM_WALLET.name,
        parameter="spam.protection.max.createReferralSet",
        new_value="3",
    )
    vega.update_network_parameter(
        MM_WALLET.name,
        parameter="spam.pow.numberOfTxPerBlock",
        new_value="3",
    )

    create_and_faucet_wallet(vega=vega, wallet=PARTY_A)
    vega.wait_for_total_catchup()
    referrer_id = vega.wallet.public_key(name=PARTY_A.name)

    # ACT single block 4 tx
    vega.wait_fn(1)
    response1 = vega.create_referral_set(key_name=PARTY_A.name, check_tx_fail=False)
    vega.wait_fn(1)
    response2 = vega.create_referral_set(key_name=PARTY_A.name, check_tx_fail=False)
    vega.wait_fn(1)
    response3 = vega.create_referral_set(key_name=PARTY_A.name, check_tx_fail=False)
    vega.wait_fn(1)
    response4 = vega.create_referral_set(key_name=PARTY_A.name, check_tx_fail=False)
    vega.wait_fn(1)
    response5 = vega.create_referral_set(key_name=PARTY_A.name, check_tx_fail=False)
    vega.wait_fn(1)
    response6 = vega.create_referral_set(key_name=PARTY_A.name, check_tx_fail=False)

    vega.wait_fn(1)

    # submit goverance transfer
    market_id = vega.all_markets()[0].id

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
