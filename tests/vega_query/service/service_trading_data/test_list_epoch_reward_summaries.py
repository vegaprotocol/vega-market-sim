import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import tds, epoch_reward_summaries

from typing import List

import vega_protos.protos as protos


@pytest.mark.vega_query
def test_epoch_reward_summaries_asset_ids(
    tds: TradingDataService,
    epoch_reward_summaries: List[protos.vega.vega.EpochRewardSummary],
):
    asset_ids = list(
        set(
            [
                epoch_reward_summary.asset_id
                for epoch_reward_summary in epoch_reward_summaries
            ]
        )
    )[:2]
    for epoch_reward_summary in tds.list_epoch_reward_summaries(
        max_pages=1, asset_ids=asset_ids
    ):
        assert epoch_reward_summary.asset_id in asset_ids


@pytest.mark.vega_query
def test_epoch_reward_summaries_market_ids(
    tds: TradingDataService,
    epoch_reward_summaries: List[protos.vega.vega.EpochRewardSummary],
):
    market_ids = list(
        set(
            [
                epoch_reward_summary.market_id
                for epoch_reward_summary in epoch_reward_summaries
            ]
        )
    )[:2]
    for epoch_reward_summary in tds.list_epoch_reward_summaries(
        max_pages=1, market_ids=market_ids
    ):
        assert epoch_reward_summary.market_id in market_ids


@pytest.mark.vega_query
def test_epoch_reward_summaries_from_epoch(
    tds: TradingDataService,
    epoch_reward_summaries: List[protos.vega.vega.EpochRewardSummary],
):
    from_epoch = epoch_reward_summaries[0].epoch
    for epoch_reward_summary in tds.list_epoch_reward_summaries(
        max_pages=1, from_epoch=from_epoch
    ):
        assert epoch_reward_summary.epoch >= from_epoch


@pytest.mark.vega_query
def test_epoch_reward_summaries_to_epoch(
    tds: TradingDataService,
    epoch_reward_summaries: List[protos.vega.vega.EpochRewardSummary],
):
    to_epoch = epoch_reward_summaries[0].epoch
    for epoch_reward_summary in tds.list_epoch_reward_summaries(
        max_pages=1, to_epoch=to_epoch
    ):
        assert epoch_reward_summary.epoch <= to_epoch
