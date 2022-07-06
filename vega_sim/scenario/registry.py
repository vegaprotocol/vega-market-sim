from vega_sim.scenario.ideal_market_maker.scenario import IdealMarketMaker
from vega_sim.scenario.ideal_market_maker_v2.scenario import (
    IdealMarketMaker as IdealMarketMakerV2,
)
from vega_sim.scenario.market_crash.scenario import MarketCrash

SCENARIOS = {
    "ideal_market_maker": IdealMarketMaker,
    "ideal_market_maker_v2": lambda: IdealMarketMakerV2(
        num_steps=1000,
        initial_price=10,
        step_length_seconds=60,
        block_length_seconds=1,
        buy_intensity=1,
        sell_intensity=1,
        kappa=1.1,
        sigma=20,
    ),
    "market_crash": lambda: MarketCrash(
        num_steps=200,
        sigma_pre=1,
        sigma_post=5,
        drift_pre=0,
        drift_post=-8,
        break_point=100,
        initial_price=100,
        kappa=1.1,
        position_taker_buy_intensity=5,
        position_taker_sell_intensity=0,
        noise_buy_intensity=2,
        noise_sell_intensity=2,
        num_position_traders=5,
        num_noise_traders=5,
        step_length_seconds=120,
        block_length_seconds=1,
        trim_to_min=0.01,
    ),
}
