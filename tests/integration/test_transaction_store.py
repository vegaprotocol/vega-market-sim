import pytest
import time

from vega_sim.null_service import VegaServiceNull
from vega_sim.replay import replay

from vega_sim.scenario.registry import SCENARIOS


# @pytest.mark.integration
def _test_transaction_store():
    with VegaServiceNull(
        warn_on_raw_data_access=False,
        start_live_feeds=True,
        retain_log_files=True,
        transactions_per_block=50,
        store_transactions=True,
    ) as vega:
        scenario = SCENARIOS["historic_ideal_market_maker_v2"]()
        scenario.run_iteration(vega=vega)
        log_dir = vega.log_dir

        market_id = vega.all_markets()[0].id
        final_oi = vega.get_latest_market_data(market_id=market_id).open_interest
    time.sleep(1)

    with replay.replay_run_context(replay_path=log_dir) as vega:
        time.sleep(1)
        vega.wait_for_core_catchup()
        final_oi_replay = vega.get_latest_market_data(market_id=market_id).open_interest

    with replay.replay_run_context(replay_path=log_dir) as vega:
        time.sleep(1)
        vega.wait_for_core_catchup()
        final_oi_replay_2 = vega.get_latest_market_data(
            market_id=market_id
        ).open_interest

    assert final_oi == final_oi_replay
    assert final_oi_replay_2 == final_oi_replay
