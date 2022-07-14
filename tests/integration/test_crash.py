import pytest

from tests.integration.utils.fixtures import vega_service_with_order_feed
from vega_sim.null_service import VegaServiceNull


from vega_sim.scenario.market_crash.scenario import MarketCrash


@pytest.mark.integration
def test_crash(vega_service_with_order_feed: VegaServiceNull):
    vega = vega_service_with_order_feed

    scenario = MarketCrash(
        num_steps=400,
        sigma_pre=1,
        sigma_post=5,
        drift_pre=0,
        drift_post=-16,
        break_point=300,
        initial_price=200,
        kappa=1.1,
        position_taker_buy_intensity=50,
        position_taker_sell_intensity=0,
        noise_buy_intensity=2,
        noise_sell_intensity=2,
        num_position_traders=2,
        num_noise_traders=5,
        step_length_seconds=1,
        trim_to_min=1,
    )

    scenario.run_iteration(vega=vega, pause_at_completion=False, tag="_iter")

    asset_id = vega.find_asset_id(symbol="tDAI_iter")
    market_id = vega.all_markets()[0].id

    vega.wait_for_datanode_sync()
    # check bond and margin for all
    for wallet_name in [f"trader_iter_pos_{i}" for i in range(2)]:
        general, margin, bond = vega.party_account(
            wallet_name=wallet_name,
            asset_id=asset_id,
            market_id=market_id,
        )
        assert margin == 0
        assert bond == 0
        assert general < 1
