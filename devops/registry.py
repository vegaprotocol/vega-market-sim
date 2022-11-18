"""registry.py

Module contains preconfigured scenarios.

"""

from devops.scenario import DevOpsScenario
from devops.classes import (
    MarketMakerArgs,
    MarketManagerArgs,
    AuctionTraderArgs,
    RandomTraderArgs,
    MomentumTraderArgs,
    SensitiveTraderArgs,
    SimulationArgs,
)

from vega_sim.scenario.common.utils.price_process import Granularity

SCENARIOS = {
    "ETHUSD": lambda: DevOpsScenario(
        binance_code="ETHDAI",
        market_manager_args=MarketManagerArgs(
            market_name="ETHUSD",
            market_code="ETHUSD",
            asset_name="tDAI",
            adp=5,
            mdp=5,
            pdp=3,
        ),
        market_maker_args=MarketMakerArgs(
            market_kappa=1,
            market_order_arrival_rate=100,
            order_kappa=2,
            order_size=1,
            order_levels=25,
            order_spacing=0.1,
            order_clipping=10000,
            inventory_lower_boundary=-30,
            inventory_upper_boundary=30,
            fee_amount=0.0001,
            commitment_amount=1e5,
            initial_mint=2e5,
        ),
        auction_trader_args=AuctionTraderArgs(
            initial_volume=0.001,
            initial_mint=1e4,
        ),
        random_trader_args=RandomTraderArgs(
            order_intensity=10,
            order_volume=0.01,
            initial_mint=1e4,
        ),
        momentum_trader_args=MomentumTraderArgs(
            order_intensity=10,
            order_volume=0.05,
            initial_mint=1e4,
        ),
        sensitive_trader_args=SensitiveTraderArgs(
            order_intensity=[10, 10, 10],
            order_volume=[0.001, 0.01, 0.1],
            price_half_life=[1, 0.1, 0.01],
            initial_mint=1e4,
        ),
        simulation_args=SimulationArgs(
            n_steps=60 * 24,
            granularity=Granularity.MINUTE,
            coinbase_code="ETH-USD",
            start_date="2022-11-01 00:00:00",
            randomise_history=False,
        ),
    ),
    "BTCUSD": lambda: DevOpsScenario(
        binance_code="BTCDAI",
        market_manager_args=MarketManagerArgs(
            market_name="BTCUSD Monthly (Dec 2022)",
            market_code="BTCUSD",
            asset_name="tDAI",
            adp=5,
            mdp=5,
            pdp=3,
        ),
        market_maker_args=MarketMakerArgs(
            market_kappa=0.15,
            market_order_arrival_rate=100,
            order_kappa=0.15,
            order_size=1,
            order_levels=25,
            order_spacing=1,
            order_clipping=10000,
            inventory_lower_boundary=-3,
            inventory_upper_boundary=3,
            fee_amount=0.0001,
            commitment_amount=1e5,
            initial_mint=2e5,
        ),
        auction_trader_args=AuctionTraderArgs(
            initial_volume=0.001,
            initial_mint=1e4,
        ),
        random_trader_args=RandomTraderArgs(
            order_intensity=5,
            order_volume=0.001,
            initial_mint=1e4,
        ),
        momentum_trader_args=MomentumTraderArgs(
            order_intensity=10,
            order_volume=0.005,
            initial_mint=1e4,
        ),
        sensitive_trader_args=SensitiveTraderArgs(
            order_intensity=[10, 10, 10],
            order_volume=[0.0001, 0.001, 0.01],
            price_half_life=[10, 1, 0.1],
            initial_mint=1e4,
        ),
        simulation_args=SimulationArgs(
            n_steps=60 * 24,
            granularity=Granularity.MINUTE,
            coinbase_code="BTC-USDT",
            start_date="2022-11-01 00:00:00",
            randomise_history=False,
        ),
    ),
}
