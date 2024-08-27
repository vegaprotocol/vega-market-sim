import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, rewards

from typing import List

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_list_rewards_party_id(
    tds: TradingDataService, rewards: List[protos.vega.vega.Reward]
):
    party_id = rewards[0].party_id
    for reward in tds.list_rewards(max_pages=1, party_id=party_id):
        assert reward.party_id == party_id


@pytest.mark.vega_query
def test_list_rewards_asset_id(
    tds: TradingDataService, rewards: List[protos.vega.vega.Reward]
):
    asset_id = rewards[0].asset_id
    for reward in tds.list_rewards(max_pages=1, asset_id=asset_id):
        assert reward.asset_id == asset_id


@pytest.mark.vega_query
def test_list_rewards_from_epoch(
    tds: TradingDataService, rewards: List[protos.vega.vega.Reward]
):
    from_epoch = rewards[0].epoch
    for reward in tds.list_rewards(max_pages=1, from_epoch=from_epoch):
        assert reward.epoch >= from_epoch


@pytest.mark.vega_query
def test_list_rewards_to_epoch(
    tds: TradingDataService, rewards: List[protos.vega.vega.Reward]
):
    to_epoch = rewards[0].epoch
    for reward in tds.list_rewards(max_pages=1, to_epoch=to_epoch):
        assert reward.epoch <= to_epoch


@pytest.mark.vega_query
def test_list_rewards_team_id(
    tds: TradingDataService, rewards: List[protos.vega.vega.Reward]
):
    team_id = rewards[0].team_id
    for reward in tds.list_rewards(max_pages=1, team_id=team_id):
        assert reward.team_id == team_id


@pytest.mark.vega_query
def test_list_rewards_team_id(
    tds: TradingDataService, rewards: List[protos.vega.vega.Reward]
):
    game_id = rewards[0].game_id
    for reward in tds.list_rewards(max_pages=1, game_id=game_id):
        assert reward.game_id == game_id
