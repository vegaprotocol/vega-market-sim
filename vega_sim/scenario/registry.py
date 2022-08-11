from vega_sim.scenario.ideal_market_maker.scenario import IdealMarketMaker
from vega_sim.scenario.ideal_market_maker_v2.scenario import (
    IdealMarketMaker as IdealMarketMakerV2,
)
from vega_sim.scenario.market_crash.scenario import MarketCrash
from vega_sim.scenario.common.utils.price_process import (
    get_historic_price_series,
    Granularity,
)

SCENARIOS = {
    "ideal_market_maker": IdealMarketMaker,
    "ideal_market_maker_v2": lambda: IdealMarketMakerV2(
        num_steps=2000,
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
        kappa=30,
        sigma=0.5,
        backgroundmarket_tick_spacing=0.002,
        backgroundmarket_number_levels_per_side=25,
    ),
    "market_crash": lambda: MarketCrash(
        num_steps=200,
        sigma_pre=1,
        sigma_post=5,
        drift_pre=0,
        drift_post=-10,
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
        trim_to_min=1,
    ),
    "historic_ideal_market_maker_v2": lambda: IdealMarketMakerV2(
        num_steps=2000,
        market_decimal=3,
        asset_decimal=5,
        market_position_decimal=2,
        price_process_fn=lambda: get_historic_price_series(
            product_id="BTC-USD", granularity=Granularity.HOUR
        ).values,
        spread=4,
        lp_commitamount=1000000,
        initial_asset_mint=1e8,
        step_length_seconds=Granularity.HOUR.value,
        block_length_seconds=1,
        buy_intensity=10,
        sell_intensity=10,
        q_upper=50,
        q_lower=-50,
        kappa=30,
        sigma=0.5,
        backgroundmarket_tick_spacing=0.002,
        backgroundmarket_number_levels_per_side=25,
    ),
}
