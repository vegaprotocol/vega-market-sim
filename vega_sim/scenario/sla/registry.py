"""sla/registry.py
"""

import vega_sim.configs as configs
from vega_sim.scenario.sla.scenario import SLAScenario

# Setup
"""
- 1 aggressive LP with low time on book
- 1 aggressive LP with high time on book
- 1 passive LP with high time on book
- 1 safe LP with high time on book
"""

REGISTRY = {
    "a": SLAScenario(
        block_length_seconds=1,
        step_length_seconds=5,
        market_config=configs.mainnet.BTCUSDT.CONFIG,
        initial_price=70000,
        annualised_volatility=0.5,
        lps_offset=[0.9, 0.9, 1.1],
        lps_target_time_on_book=[0.2, 0.9, 0.9],
        lps_commitment_amount=[500000, 500000, 500000],
        override_price_range=0.0005,
        override_commitment_min_time_fraction=0.1,
        override_sla_competition_factor=1.0,
        initial_network_parameters={
            "validators.epoch.length": "20m",
            "market.liquidity.providersFeeCalculationTimeStep": "2m",
        },
    ),
}
