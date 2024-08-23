"""
Test Cases

- a party can create a referral set without creating a team
- a party can create a team without creating a referral set
- a party can create a referral set and create a team

- a party who has applied a referral code, but could not join a team
    - cannot create their own referral set
    - can create their own team

- a party who has applied a referral code, and joined the team
    - cannot create their own referral set
    - can create their own team

- a party who has applied a referral code, and optionally not joined the team
    - cannot create their own referral set
    - can create their own team
"""

import pytest

from vega_sim.null_service import VegaServiceNull
from tests.integration.utils.fixtures import (
    vega_service,
)


PARTY_A = "a"
PARTY_B = "b"
PARTY_C = "c"


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
def test_party_can_create_a_referral_set_without_creating_a_team(
    vega_service: VegaServiceNull,
):
    vega = vega_service
    vega.create_key(PARTY_A)
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    vega.create_referral_set(
        PARTY_A,
        do_not_create_referral_set=False,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    sets = vega.list_referral_sets()
    teams = vega.list_teams()
    assert len(sets) == 1
    assert len(teams) == 0
    assert list(sets.values())[0].referrer == vega.wallet.public_key(PARTY_A)


@pytest.mark.integration
def test_party_can_create_a_team_without_creating_a_referral_set(
    vega_service: VegaServiceNull,
):
    vega = vega_service
    vega.create_key(PARTY_A)
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    vega.create_referral_set(
        PARTY_A,
        do_not_create_referral_set=True,
        name="team_a",
        team_url="url_a",
        avatar_url="avatar_a",
        closed=False,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    sets = vega.list_referral_sets()
    teams = vega.list_teams()
    assert len(sets) == 0
    assert len(teams) == 1
    assert list(teams.values())[0].referrer == vega.wallet.public_key(PARTY_A)


@pytest.mark.integration
def test_party_can_create_a_referral_set_and_create_a_team(
    vega_service: VegaServiceNull,
):
    vega = vega_service
    vega.create_key(PARTY_A)
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    vega.create_referral_set(
        PARTY_A,
        do_not_create_referral_set=False,
        name="team_a",
        team_url="url_a",
        avatar_url="avatar_a",
        closed=False,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    sets = vega.list_referral_sets()
    teams = vega.list_teams()
    assert len(sets) == 1
    assert len(teams) == 1
    assert list(sets.values())[0].referrer == vega.wallet.public_key(PARTY_A)
    assert list(teams.values())[0].referrer == vega.wallet.public_key(PARTY_A)


@pytest.mark.integration
def test_party_who_applied_referral_code_and_who_could_not_join_team(
    vega_service: VegaServiceNull,
):
    vega = vega_service

    vega.create_key(PARTY_A)
    vega.create_key(PARTY_B)

    vega.create_referral_set(PARTY_A)
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    sets = vega.list_referral_sets()
    teams = vega.list_teams()
    assert len(sets) == 1
    assert len(teams) == 0
    set_a_id = list(sets.keys())[0]

    vega.apply_referral_code(PARTY_B, set_a_id)
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    set_a_referees = vega.list_referral_set_referees(referral_set_id=set_a_id)
    assert vega.wallet.public_key(PARTY_B) in [
        referee.referee for referee in set_a_referees[set_a_id].values()
    ]

    # Party B cannot create their own referral set
    vega.create_referral_set(PARTY_B)
    vega.wait_fn(1)
    sets = vega.list_referral_sets()
    assert len(vega.list_referral_sets()) == 1
    assert all(
        [set.referrer != vega.wallet.public_key(PARTY_B) for set in sets.values()]
    )

    # Party B can create their own team
    vega.create_referral_set(
        PARTY_B,
        do_not_create_referral_set=True,
        name="team_b",
        team_url="url_b",
        avatar_url="avatar_b",
        closed=False,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    sets = vega.list_referral_sets()
    assert len(vega.list_referral_sets()) == 1
    assert all(
        [set.referrer != vega.wallet.public_key(PARTY_B) for set in sets.values()]
    )
    teams = vega.list_teams()
    assert len(teams) == 1
    assert any(
        [team.referrer == vega.wallet.public_key(PARTY_B) for team in teams.values()]
    )


@pytest.mark.integration
def test_party_who_applied_referral_code_and_who_joined_the_team(
    vega_service: VegaServiceNull,
):
    vega = vega_service

    vega.create_key(PARTY_A)
    vega.create_key(PARTY_B)

    vega.create_referral_set(
        PARTY_A, name="team_a", team_url="url_a", avatar_url="avatar_a", closed=False
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    sets = vega.list_referral_sets()
    teams = vega.list_teams()
    assert len(sets) == 1
    assert len(teams) == 1
    set_a_id = list(sets.keys())[0]
    team_a_id = list(teams.keys())[0]

    vega.apply_referral_code(PARTY_B, set_a_id)
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    set_a_referees = vega.list_referral_set_referees(referral_set_id=set_a_id)
    team_a_members = vega.list_team_referees(team_id=team_a_id)
    assert vega.wallet.public_key(PARTY_B) in [
        referee.referee for referee in set_a_referees[set_a_id].values()
    ]
    assert vega.wallet.public_key(PARTY_B) in [
        member.referee for member in team_a_members
    ]

    # Party B cannot create their own referral set
    vega.create_referral_set(PARTY_B)
    vega.wait_fn(1)
    sets = vega.list_referral_sets()
    assert len(vega.list_referral_sets()) == 1
    assert all(
        [set.referrer != vega.wallet.public_key(PARTY_B) for set in sets.values()]
    )

    # Party B can create their own team
    vega.create_referral_set(
        PARTY_B,
        do_not_create_referral_set=True,
        name="team_b",
        team_url="url_b",
        avatar_url="avatar_b",
        closed=False,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    sets = vega.list_referral_sets()
    teams = vega.list_teams()
    assert len(teams) == 2
    assert any(
        [team.referrer == vega.wallet.public_key(PARTY_B) for team in teams.values()]
    )


@pytest.mark.integration
def test_party_who_applied_referral_code_and_who_optionally_did_not_join_the_team(
    vega_service: VegaServiceNull,
):
    vega = vega_service

    vega.create_key(PARTY_A)
    vega.create_key(PARTY_B)

    vega.create_referral_set(
        PARTY_A, name="team_a", team_url="url_a", avatar_url="avatar_a", closed=False
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    sets = vega.list_referral_sets()
    teams = vega.list_teams()
    assert len(sets) == 1
    assert len(teams) == 1
    set_a_id = list(sets.keys())[0]
    team_a_id = list(teams.keys())[0]

    vega.apply_referral_code(PARTY_B, set_a_id, do_not_join_team=True)
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    set_a_referees = vega.list_referral_set_referees(referral_set_id=set_a_id)
    team_a_members = vega.list_team_referees(team_id=team_a_id)
    assert vega.wallet.public_key(PARTY_B) in [
        referee.referee for referee in set_a_referees[set_a_id].values()
    ]
    assert vega.wallet.public_key(PARTY_B) not in [
        member.referee for member in team_a_members
    ]

    # Party B cannot create their own referral set
    vega.create_referral_set(PARTY_B)
    vega.wait_fn(1)
    sets = vega.list_referral_sets()
    assert len(vega.list_referral_sets()) == 1
    assert all(
        [set.referrer != vega.wallet.public_key(PARTY_B) for set in sets.values()]
    )

    # Party B can create their own team
    vega.create_referral_set(
        PARTY_B,
        do_not_create_referral_set=True,
        name="team_b",
        team_url="url_b",
        avatar_url="avatar_b",
        closed=False,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    sets = vega.list_referral_sets()
    assert len(vega.list_referral_sets()) == 1
    assert all(
        [set.referrer != vega.wallet.public_key(PARTY_B) for set in sets.values()]
    )
    teams = vega.list_teams()
    assert len(teams) == 2
    assert any(
        [team.referrer == vega.wallet.public_key(PARTY_B) for team in teams.values()]
    )
