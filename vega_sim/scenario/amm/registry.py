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
                initial_price=60000,
                annualised_volatility=0.28,
                notional_trade_volume=10,
                process_theta=0.0001,
                process_drift=-5,
                risky_trader_funds=1,
            ),
        ],
        amm_liquidity_fee=0.0001,
        amm_update_frequency=0,
        initial_network_parameters={
            "validators.epoch.length": "1h",
            "market.fee.factors.makerFee": "0",
        },
    ),
}
