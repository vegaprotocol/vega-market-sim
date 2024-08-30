import vega_sim.configs as configs
from vega_sim.scenario.benchmark.configs import BenchmarkConfig
from vega_sim.scenario.amm.scenario import AMMScenario


REGISTRY = {
    "static": AMMScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.mainnet.BTCUSDT.CONFIG,
                initial_price=70000,
                annualised_volatility=0.5,
                notional_trade_volume=100,
                process_theta=0.02,
                process_drift=-0.1,
            ),
        ],
        amm_liquidity_fee=0.001,
        amm_update_frequency=0,
        initial_network_parameters={
            "validators.epoch.length": "1h",
        },
    ),
}
