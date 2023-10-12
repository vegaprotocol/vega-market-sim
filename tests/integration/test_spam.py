import json
import time
import pytest
import logging
from collections import namedtuple

from requests import Response
import vega_sim.proto.vega as vega_protos
from google.protobuf.json_format import MessageToDict
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
        if forwards > 6 * 10 * 60:
            raise Exception(
                "Epoch not started after forwarding the duration of two epochs."
            )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()


def blocks_from_next_epoch(vega: VegaServiceNull, blocks_from_next_epoch: int = 0):
    forwards = 0

    vega_stats = vega.statistics()
    epoch_expiry = time_in_epoch(vega_stats.epoch_expiry_time, False)
    current_vega_time = time_in_epoch(vega_stats.vega_time, False)
    time_till_next_epoch = epoch_expiry - current_vega_time - blocks_from_next_epoch

    if time_till_next_epoch < 0:
        next_epoch(vega)
        epoch_expiry = time_in_epoch(vega_stats.epoch_expiry_time)
        current_vega_time = time_in_epoch(vega_stats.vega_time)
        time_till_next_epoch = epoch_expiry - current_vega_time - blocks_from_next_epoch

    epoch_seq = vega.statistics().epoch_seq

    while epoch_seq == vega.statistics().epoch_seq:
        vega.wait_fn(1)
        forwards += 1
        # next epoch will occur when forwards=122
        if forwards == time_till_next_epoch:
            break
        if forwards > 6 * 10 * 60:
            raise Exception(
                "Epoch not started after forwarding the duration of two epochs."
            )
    vega.wait_for_total_catchup()


def time_in_epoch(value: str, return_in_nanoseconds: bool = True):
    pattern = "%Y-%m-%dT%H:%M:%SZ %Z"
    epoch = int(time.mktime(time.strptime(value + " UTC", pattern)))
    if return_in_nanoseconds:
        epoch = epoch * 1000000000
    return epoch


@pytest.mark.integration
@pytest.mark.parametrize(
    "epoch_boundary",
    [
        (False),
        (True),
    ],
)
def test_spam_referral_sets_max_epoch(
    vega_spam_service_with_market: VegaServiceNull, epoch_boundary
):
    """
    A party who has more than 50% of their CreateReferralSet transactions post-block rejected should be banned for 1/48th of an
    epoch or untill the end of the current epoch (whichever comes first). When banned for the above reason,
    CreateReferralSet transactions should be pre-block rejected (0062-SPAM-033).
    """
    #
    # ARRANGE
    #

    vega = vega_spam_service_with_market
    max_spam = 3
    # in minutes
    epoch_length=60

    assert (
        vega.spam_protection == True
    ), "test pre-requisite, need to enable spam protection"

    create_and_faucet_wallet(vega=vega, wallet=MM_WALLET, symbol="VOTE")
    create_and_faucet_wallet(vega=vega, wallet=PARTY_A)
    referrer_id = vega.wallet.public_key(name=PARTY_A.name)
    vega.wait_for_total_catchup()

    # Access the updated value
    vega.update_network_parameter(
        MM_WALLET.name,
        parameter="spam.protection.max.createReferralSet",
        new_value=str(max_spam),
    )

    vega.update_network_parameter(
        MM_WALLET.name,
        parameter="validators.epoch.length",
        new_value=f"{epoch_length}m",
    )
    # nanoseconds
    epoch_duration = epoch_length * 60 * 1000000000

    vega.wait_fn(1)
    spam_stats = vega.get_spam_statistics(referrer_id)
    spam_stats = MessageToDict(spam_stats)
    assert (
        int(spam_stats["statistics"]["createReferralSet"]["maxForEpoch"]) == max_spam
    ), "test-prerequisite net param change did not take place"
    assert (
        "countForEpoch" not in spam_stats["statistics"]["createReferralSet"]
    ), f"should not have submitted any create referral sets {spam_stats}"

    next_epoch(vega)

    if epoch_boundary:
        blocks_from_next_epoch(vega, max_spam + 3)

    #
    # ACT
    #

    start_epoch = vega.statistics().epoch_seq

    # submit create referral set up to max_spam
    for i in range(max_spam):
        vega.create_referral_set(
            key_name=PARTY_A.name,
            name=f"name_{i}",
            team_url="team_url_a",
            avatar_url="avatar_url_a",
            closed=False,
        )
        vega.wait_fn(1)

    spam_stats_at_max = vega.get_spam_statistics(referrer_id)
    spam_stats_at_max = MessageToDict(spam_stats_at_max)

    # submit one more tx to trigger ban
    vega.create_referral_set(
        key_name=PARTY_A.name,
        name="name_x",
        team_url="team_url_x",
        avatar_url="avatar_url_x",
        closed=False,
    )
    vega.wait_fn(1)

    #
    # ASSERT
    #

    spam_stats_at_ban = vega.get_spam_statistics(referrer_id)
    spam_stats_at_ban = MessageToDict(spam_stats_at_ban)

    vega_stats = vega.statistics()
    current_epoch = vega_stats.epoch_seq

    # Assert - test took place in one epoch
    assert (
        start_epoch == current_epoch
    ), "test prerequisite not met, need to be in one epoch"

    # Assert - at max_spam, no ban
    assert (
        "countForEpoch" in spam_stats_at_max["statistics"]["createReferralSet"]
    ), f"should have submitted max create referral sets {spam_stats_at_max}"
    assert (
        int(spam_stats_at_max["statistics"]["createReferralSet"]["countForEpoch"])
        == max_spam
    ), f"expected to have {max_spam} tx for create referral sets in epoch"
    assert (
        "bannedUntil" not in spam_stats_at_max["statistics"]["createReferralSet"]
    ), f"party should not be banned yet {spam_stats_at_max}"

    # Assert - at max_spam + 1, ban is invoked
    assert (
        "bannedUntil" in spam_stats_at_ban["statistics"]["createReferralSet"]
    ), f"party should be banned {spam_stats_at_ban}"

    banned_until = int(
        spam_stats_at_ban["statistics"]["createReferralSet"]["bannedUntil"]
    )
    epoch_expiry_time = time_in_epoch(vega_stats.epoch_expiry_time)

    # assert the team only 1 team
    team_a = vega.list_teams(key_name=PARTY_A.name)
    assert (
        len(team_a) == 1
    ), "party is banned, and did not expect changes to referral set"

    # assert the created team is first submission
    assert team_a[list(team_a.keys())[0]].name == "name_0"

    if epoch_boundary:
        # Assert ban will not be lifted in current epoch
        assert banned_until > epoch_expiry_time

        # wait for next epoch
        if vega.statistics().epoch_seq <= current_epoch:
            next_epoch(vega)

        # Assert ban is lifted start of next epoch
        spam_stats_at_ban_lifted = MessageToDict(vega.get_spam_statistics(referrer_id))
        assert (
            "bannedUntil"
            not in spam_stats_at_ban_lifted["statistics"]["createReferralSet"]
        ), f"party should have ban lifted next epoch {spam_stats_at_ban_lifted}"

        # Assert counter for spam statistics is reset
        assert (
            "countForEpoch"
            not in spam_stats_at_ban_lifted["statistics"]["createReferralSet"]
        ), f"party should have create referral sets count, reset {spam_stats_at_ban_lifted}"
    else:
        # Assert ban is within current epoch
        assert banned_until < epoch_expiry_time

        # Assert ban is 1/48 of epoch
        ban_start_time = time_in_epoch(vega_stats.vega_time)
        actual_ban_duration = banned_until - ban_start_time
        expected_ban_duration = int(epoch_duration / 48)
        assert expected_ban_duration == actual_ban_duration

        # move forward until the band is lifted and ensure we still in same epoch
        actual_ban_duration_in_sec = actual_ban_duration / 1000000000
        blocks_from_next_epoch(vega, actual_ban_duration_in_sec + 1)
        vega_stats2 = vega.statistics()
        assert current_epoch == vega_stats2.epoch_seq, "expected to be in same epoch"

        # Assert ban is lifted
        assert time_in_epoch(vega_stats2.vega_time) > banned_until
        spam_stats_at_ban_lifted = MessageToDict(vega.get_spam_statistics(referrer_id))
        assert (
            "bannedUntil"
            not in spam_stats_at_ban_lifted["statistics"]["createReferralSet"]
        ), f"party should have ban lifted next epoch {spam_stats_at_ban_lifted}"

        # spam stats will not reset
        assert (
            int(spam_stats_at_max["statistics"]["createReferralSet"]["countForEpoch"])
            == max_spam
        ), f"expected to have {max_spam} tx for create referral sets in epoch"
