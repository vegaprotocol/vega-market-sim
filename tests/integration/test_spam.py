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
    A party who has submitted more than spam.protection.max.CreateReferralSet transactions in the current epoch plus in
    the current block, should have their transactions submitted in the current block post-block rejected (0062-SPAM-032).

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

    vega = vega_spam_service_with_market
    # Access the updated value
    # vega.update_network_parameter(
    #     MM_WALLET.name,
    #     parameter="spam.protection.max.CreateReferralSet",
    #     new_value="3",
    # )

    create_and_faucet_wallet(vega=vega, wallet=PARTY_A)
    vega.wait_for_total_catchup()
    referrer_id = vega.wallet.public_key(name=PARTY_A.name)

    # ACT single block 4 tx
    response1 = vega.create_referral_set(key_name=PARTY_A.name)
    response2 = vega.create_referral_set(key_name=PARTY_A.name)
    response3 = vega.create_referral_set(key_name=PARTY_A.name)
    # this one will be pre block rejected
    response4 = vega.create_referral_set(key_name=PARTY_A.name)

    # assert only 3 in block

    vega.wait_fn(1)
    vega.wait_for_total_catchup()
