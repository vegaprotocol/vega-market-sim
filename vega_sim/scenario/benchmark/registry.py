import datetime

import vega_sim.configs as configs
from vega_sim.scenario.benchmark.configs import BenchmarkConfig
from vega_sim.scenario.benchmark.scenario import BenchmarkScenario


REGISTRY = {
    "mainnet": BenchmarkScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.mainnet.BTCUSDT.CONFIG,
                initial_price=70000,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.mainnet.ETHUSDT.CONFIG,
                initial_price=4000,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.mainnet.SOLUSDT.CONFIG,
                initial_price=130,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.mainnet.INJUSDT.CONFIG,
                initial_price=3,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.mainnet.SNXUSDT.CONFIG,
                initial_price=5,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.mainnet.LDOUSDT.CONFIG,
                initial_price=40,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.mainnet.EGLPUSDT.CONFIG,
                initial_price=0.06,
                annualised_volatility=10,
                notional_trade_volume=100,
            ),
        ],
        initial_network_parameters={"validators.epoch.length": "1h"},
    ),
    "mainnet-BTCUSDT": BenchmarkScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.mainnet.BTCUSDT.CONFIG,
                initial_price=70000,
                annualised_volatility=2,
                notional_trade_volume=100,
                historic_data_code="BTC-USD",
            )
        ],
    ),
    "mainnet-EGLPUSDT": BenchmarkScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.mainnet.EGLPUSDT.CONFIG,
                initial_price=0.06,
                annualised_volatility=10,
                notional_trade_volume=100,
            )
        ],
    ),
    "mainnet-ETHUSDT": BenchmarkScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.mainnet.ETHUSDT.CONFIG,
                initial_price=4000,
                annualised_volatility=2,
                notional_trade_volume=100,
                historic_data_code="ETH-USD",
            )
        ],
    ),
    "mainnet-INJUSDT": BenchmarkScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.mainnet.INJUSDT.CONFIG,
                initial_price=3,
                annualised_volatility=2,
                notional_trade_volume=100,
            )
        ],
    ),
    "mainnet-LDOUSDT": BenchmarkScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.mainnet.LDOUSDT.CONFIG,
                initial_price=40,
                annualised_volatility=2,
                notional_trade_volume=100,
            )
        ],
    ),
    "mainnet-SNXUSDT": BenchmarkScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.mainnet.SNXUSDT.CONFIG,
                initial_price=5,
                annualised_volatility=2,
                notional_trade_volume=100,
            )
        ],
    ),
    "mainnet-SOLUSDT": BenchmarkScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.mainnet.SOLUSDT.CONFIG,
                initial_price=130,
                annualised_volatility=2,
                notional_trade_volume=100,
            )
        ],
    ),
    "research-ESHRUSDT": BenchmarkScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.research.ESHRUSDT.CONFIG,
                initial_price=1,
                annualised_volatility=10,
                notional_trade_volume=100,
            )
        ],
    ),
    "research": BenchmarkScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.research.SPOT.CONFIG,
                initial_price=70000,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
            BenchmarkConfig(
                market_config=configs.mainnet.EGLPUSDT.CONFIG,
                initial_price=70000,
                annualised_volatility=2,
                notional_trade_volume=100,
            ),
        ],
    ),
    "research-HLPUSDT": BenchmarkScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.research.HLPUSDT.CONFIG,
                initial_price=1,
                annualised_volatility=10,
                notional_trade_volume=100,
            )
        ],
    ),
    "research-SPOT": BenchmarkScenario(
        block_length_seconds=1,
        step_length_seconds=30,
        benchmark_configs=[
            BenchmarkConfig(
                market_config=configs.research.SPOT.CONFIG,
                initial_price=70000,
                annualised_volatility=2,
                notional_trade_volume=100,
            )
        ],
    ),
}
