from vega_sim.scenario.ideal_market_maker.scenario import IdealMarketMaker
from vega_sim.scenario.ideal_market_maker_v2.scenario import (
    IdealMarketMaker as IdealMarketMakerV2,
)

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
}
