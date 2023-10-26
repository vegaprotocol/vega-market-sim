"""registry.py

Module contains preconfigured scenarios.

"""

from vega_sim.devops.scenario import DevOpsScenario

from vega_sim.scenario.common.agents import (
    ArbitrageLiquidityProvider,
    ExponentialShapedMarketMaker,
)

from vega_sim.devops.classes import (
    MarketMakerArgs,
    MarketManagerArgs,
    AuctionTraderArgs,
    RandomTraderArgs,
    SensitiveTraderArgs,
    SimulationArgs,
)

from vega_sim.scenario.common.utils.price_process import Granularity, LivePrice

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
            market_kappa=10,
            market_order_arrival_rate=100,
            order_kappa=0.3,
            order_size=1,
            order_levels=25,
            order_spacing=0.5,
            order_clipping=10000,
            inventory_lower_boundary=-30,
            inventory_upper_boundary=30,
            fee_amount=0.001,
            commitment_amount=1e5,
            initial_mint=2e5,
        ),
        auction_trader_args=AuctionTraderArgs(
            initial_volume=0.001,
            initial_mint=1e4,
        ),
        random_trader_args=RandomTraderArgs(
            order_intensity=[5, 5, 5],
            order_volume=[0.01, 0.1, 1],
            step_bias=[0.333, 0.012, 0.003],
            initial_mint=1e6,
        ),
        sensitive_trader_args=SensitiveTraderArgs(
            scale=[10, 10, 10],
            max_order_size=[0.001, 0.01, 0.1],
            initial_mint=1e4,
        ),
        simulation_args=SimulationArgs(
            n_steps=60 * 6,
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
            order_intensity=[5, 5, 5],
            order_volume=[0.01, 0.1, 1],
            step_bias=[0.333, 0.012, 0.003],
            initial_mint=1e6,
        ),
        sensitive_trader_args=SensitiveTraderArgs(
            scale=[10, 10, 10],
            max_order_size=[0.001, 0.01, 0.1],
            initial_mint=1e4,
        ),
        simulation_args=SimulationArgs(
            n_steps=60 * 6,
            granularity=Granularity.MINUTE,
            coinbase_code="BTC-USDT",
            start_date="2022-11-01 00:00:00",
            randomise_history=False,
        ),
    ),
    "ADAUSDT": lambda: DevOpsScenario(
        binance_code="ADAUSDT",
        market_manager_args=MarketManagerArgs(
            market_name="Cardano USD",
            market_code="ADA/USD",
            asset_name="tDAI",
            adp=18,
            mdp=4,
            pdp=0,
        ),
        market_maker_args=MarketMakerArgs(
            market_kappa=10000,
            market_order_arrival_rate=5000,
            order_kappa=350,
            order_size=1,
            order_levels=25,
            order_spacing=0.0002,
            order_clipping=200000,
            inventory_lower_boundary=-5000,
            inventory_upper_boundary=5000,
            fee_amount=0.0001,
            commitment_amount=3e5,
            initial_mint=15e5,
        ),
        auction_trader_args=AuctionTraderArgs(
            initial_volume=1,
            initial_mint=5e4,
        ),
        random_trader_args=RandomTraderArgs(
            order_intensity=[100, 100, 100],
            order_volume=[1, 1, 1],
            step_bias=[1, 1, 1],
            initial_mint=5e4,
        ),
        sensitive_trader_args=SensitiveTraderArgs(
            scale=[10, 10, 10],
            max_order_size=[0.001, 0.01, 0.1],
            initial_mint=1e4,
        ),
        simulation_args=SimulationArgs(
            n_steps=6 * 60,
            granularity=Granularity.MINUTE,
            coinbase_code="ADA-USDT",
            start_date="2022-11-01 00:00:00",
            randomise_history=False,
        ),
    ),
    "XRPUSDT": lambda: DevOpsScenario(
        binance_code="XRPUSDT",
        market_manager_args=MarketManagerArgs(
            market_name="XRP USD",
            market_code="XRP USD",
            asset_name="tDAI",
            adp=18,
            mdp=4,
            pdp=0,
        ),
        market_maker_args=MarketMakerArgs(
            market_kappa=10000,
            market_order_arrival_rate=5000,
            order_kappa=350,
            order_size=1,
            order_levels=25,
            order_spacing=0.0002,
            order_clipping=200000,
            inventory_lower_boundary=-5000,
            inventory_upper_boundary=5000,
            fee_amount=0.0001,
            commitment_amount=3e5,
            initial_mint=15e5,
        ),
        auction_trader_args=AuctionTraderArgs(
            initial_volume=1,
            initial_mint=5e4,
        ),
        random_trader_args=RandomTraderArgs(
            order_intensity=[100, 100, 100],
            order_volume=[1, 1, 1],
            step_bias=[1, 1, 1],
            initial_mint=5e4,
        ),
        sensitive_trader_args=SensitiveTraderArgs(
            scale=[10, 10, 10],
            max_order_size=[0.001, 0.01, 0.1],
            initial_mint=1e4,
        ),
        simulation_args=SimulationArgs(
            n_steps=6 * 60,
            granularity=Granularity.MINUTE,
            coinbase_code="ADA-USDT",
            start_date="2023-01-01 00:00:00",
            randomise_history=False,
        ),
    ),
}

AGENTS = {
    "arbitrage_liquidity_provider": lambda: ArbitrageLiquidityProvider(
        wallet_name=None,
        key_name=None,
        market_name=None,
        asset_name=None,
        initial_asset_mint=500,
        commitment_ratio=0.5,
        safety_factor=0.1,
        fee=0.001,
        tag="agent",
    ),
    "shaped_market_maker_ethusd": lambda: ExponentialShapedMarketMaker(
        wallet_name=None,
        key_name=None,
        market_name=None,
        asset_name=None,
        initial_asset_mint=1e9,
        commitment_amount=20000,
        market_kappa=10,
        kappa=0.3,
        num_levels=25,
        tick_spacing=0.5,
        max_order_size=10000,
        inventory_lower_boundary=-30,
        inventory_upper_boundary=30,
        market_order_arrival_rate=100,
        fee_amount=0.0005,
        num_steps=60 * 60 * 24 * 365,
        price_process_generator=iter(LivePrice(product="ETHDAI")),
        orders_from_stream=False,
        state_update_freq=10,
        tag="agent",
    ),
}
