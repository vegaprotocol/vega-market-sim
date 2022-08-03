from vega_sim.scenario.ideal_market_maker.scenario import IdealMarketMaker
from vega_sim.scenario.ideal_market_maker_v2.scenario import (
    IdealMarketMaker as IdealMarketMakerV2,
)
from vega_sim.scenario.market_crash.scenario import MarketCrash

SCENARIOS = {
    "ideal_market_maker": IdealMarketMaker,
    "ideal_market_maker_v2": lambda: IdealMarketMakerV2(
        market_decimal=3,
        asset_decimal=5,
        market_position_decimal=2,
        initial_price=1123.11,
        spread=4,
        lp_commitamount=1000000,
        initial_asset_mint=1e8,
        step_length_seconds=60,
        block_length_seconds=1,
        buy_intensity=10,
        sell_intensity=10,
        q_upper=50,
        q_lower=-50,
        kappa=50,
        sigma=5,
        num_steps=288,
        backgroundmarket_tick_spacing=0.002,
        backgroundmarket_number_levels_per_side=25,
        settle_at_end=False,
    ),
    "market_crash": lambda: MarketCrash(
        num_steps=500,
        sigma_pre=1,
        sigma_post=4,
        drift_pre=0.1,
        drift_post=-0.5,
        break_point=200,
        initial_price=100,
        kappa=1.1,
        position_taker_buy_intensity=3,
        position_taker_sell_intensity=0,
        noise_buy_intensity=3,
        noise_sell_intensity=3,
        num_position_traders=5,
        num_noise_traders=20,
        step_length_seconds=60,
        block_length_seconds=1,
        trim_to_min=1,
    ),
}
