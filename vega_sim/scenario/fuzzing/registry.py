import vega_sim.configs as configs
from vega_sim.scenario.benchmark.configs import BenchmarkConfig
from vega_sim.scenario.fuzzing.scenario import FuzzingScenario


REGISTRY = {
    "overnight": FuzzingScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.research.spot.ETHUSDT.CONFIG,
                initial_price=4000,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.research.spot.BTCUSDT.CONFIG,
                initial_price=80000,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.research.spot.BTCETH.CONFIG,
                initial_price=20,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.research.future.ETHUSDT.CONFIG,
                initial_price=4000,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.research.future.BTCUSDT.CONFIG,
                initial_price=80000,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.research.perpetual.ETHUSDT.CONFIG,
                initial_price=4000,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.research.perpetual.BTCUSDT.CONFIG,
                initial_price=80000,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
        ],
        initial_network_parameters={"validators.epoch.length": "1h"},
    ),
}
