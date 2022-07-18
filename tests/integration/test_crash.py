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
        sigma_post=2,
        drift_pre=0,
        drift_post=-10,
        break_point=200,
        initial_price=100,
        initial_asset_mint=100000,
        kappa=1.1,
        position_taker_buy_intensity=3,
        position_taker_sell_intensity=0,
        position_taker_mint=200,
        noise_buy_intensity=2,
        noise_sell_intensity=2,
        num_position_traders=2,
        num_noise_traders=5,
        step_length_seconds=1,
        trim_to_min=1,
        settle_at_end=False,
    )

    scenario.run_iteration(vega=vega, pause_at_completion=True, tag="_iter")

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
        assert general < 100
