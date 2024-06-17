import numpy as np
from typing import Optional, Dict, Any, List

from vega_sim.api.market import MarketConfig
from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.benchmark.configs import BenchmarkConfig
from vega_sim.scenario.common.utils.price_process import ou_price_process
from vega_sim.scenario.constants import Network
from vega_sim.null_service import VegaServiceNull
from vega_sim.environment.environment import (
    MarketEnvironmentWithState,
    NetworkEnvironment,
)

from vega_sim.configs.agents import ConfigurableMarketManager
from vega_sim.scenario.common.agents import (
    StateAgent,
    NetworkParameterManager,
    UncrossAuctionAgent,
    ExponentialShapedMarketMaker,
    MarketOrderTrader,
    LimitOrderTrader,
)
from vega_sim.scenario.fuzzed_markets.agents import (
    RiskyMarketOrderTrader,
)


class BenchmarkScenario(Scenario):
    def __init__(
        self,
        benchmark_configs: List[BenchmarkConfig],
        num_steps: int = 60 * 24 * 30 * 3,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        step_length_seconds: Optional[float] = None,
        initial_network_parameters: Dict[str, Any] = None,
        output: bool = True,
    ):
        super().__init__()

        self.num_steps = num_steps
        self.step_length_seconds = (
            step_length_seconds
            if step_length_seconds is not None
            else block_length_seconds
        )
        self.block_length_seconds = block_length_seconds
        self.transactions_per_block = transactions_per_block

        self.output = output
        self.benchmark_configs = benchmark_configs

        self.initial_network_parameters = (
            initial_network_parameters if initial_network_parameters is not None else {}
        )

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: str,
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> Dict[str, StateAgent]:
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

        self.agents = []
        self.agents.append(
            NetworkParameterManager(
                wallet_name="NetworkParameterManager",
                key_name="NetworkParameterManager",
                network_parameters=self.initial_network_parameters,
            )
        )
        for _, benchmark_config in enumerate(self.benchmark_configs):

            market_name = benchmark_config.market_config.instrument.name
            market_decimal_places = int(
                benchmark_config.market_config.price_decimal_places
                if benchmark_config.market_config.is_spot()
                else benchmark_config.market_config.decimal_places
            )
            # Create fuzzed price process
            benchmark_config.price_process = ou_price_process(
                self.num_steps + 1,
                x0=benchmark_config.initial_price,
                mu=benchmark_config.initial_price,
                theta=benchmark_config.process_theta,
                sigma=benchmark_config.annualised_volatility
                * np.sqrt(self.step_length_seconds / (365.25 * 24 * 60 * 60))
                * benchmark_config.initial_price,
                drift=0,
            )
            self.agents.append(
                ConfigurableMarketManager(
                    wallet_name="ConfigurableMarketManager",
                    key_name=f"ConfigurableMarketManager_{benchmark_config.market_config.instrument.code}",
                    market_config=benchmark_config.market_config,
                    oracle_prices=iter(benchmark_config.price_process),
                    oracle_submission=0.5,
                    oracle_difference=0.001,
                    random_state=self.random_state,
                    tag=f"{benchmark_config.market_config.instrument.code}",
                ),
            )

            self.agents.append(
                ExponentialShapedMarketMaker(
                    wallet_name="ExponentialShapedMarketMaker",
                    key_name="ExponentialShapedMarketMaker",
                    price_process_generator=iter(benchmark_config.price_process),
                    initial_asset_mint=1e9,
                    market_name=market_name,
                    commitment_amount=1e6,
                    market_decimal_places=market_decimal_places,
                    num_steps=self.num_steps,
                    kappa=2.4,
                    tick_spacing=10**-market_decimal_places
                    * benchmark_config.market_config.tick_size,
                    num_levels=10,
                    market_kappa=1000,
                    state_update_freq=10,
                    tag=f"{benchmark_config.market_config.instrument.code}",
                    fee_amount=0.0001,
                )
            )

            self.agents.extend(
                [
                    UncrossAuctionAgent(
                        wallet_name="UncrossAuctionAgent",
                        key_name=f"{benchmark_config.market_config.instrument.code}_{side}",
                        side=side,
                        initial_asset_mint=1e8,
                        price_process=iter(benchmark_config.price_process),
                        market_name=market_name,
                        uncrossing_size=1e6 / benchmark_config.initial_price,
                        tag=(
                            f"{benchmark_config.market_config.instrument.code}_{str(i_agent).zfill(3)}"
                        ),
                        leave_opening_auction_prob=1.0,
                    )
                    for i_agent, side in enumerate(["SIDE_BUY", "SIDE_SELL"])
                ]
            )
            self.agents.extend(
                [
                    MarketOrderTrader(
                        wallet_name="MarketOrderTrader",
                        key_name=f"MarketOrderTrader_{str(i_agent).zfill(3)}",
                        market_name=market_name,
                        buy_intensity=100,
                        sell_intensity=100,
                        base_order_size=benchmark_config.notional_trade_volume
                        / benchmark_config.initial_price
                        / 100,
                        step_bias=1,
                        initial_asset_mint=1e8,
                        tag=f"{benchmark_config.market_config.instrument.code}_{str(i_agent).zfill(3)}",
                    )
                    for i_agent in range(1)
                ]
            )
            self.agents.extend(
                [
                    LimitOrderTrader(
                        wallet_name=f"LimitOrderTrader",
                        key_name=f"LimitOrderTrader_{str(i_agent).zfill(3)}",
                        market_name=market_name,
                        time_in_force_opts={"TIME_IN_FORCE_GTT": 1},
                        buy_volume=benchmark_config.notional_trade_volume
                        / benchmark_config.initial_price
                        / 100,
                        sell_volume=benchmark_config.notional_trade_volume
                        / benchmark_config.initial_price
                        / 100,
                        buy_intensity=100,
                        sell_intensity=100,
                        submit_bias=1,
                        cancel_bias=0,
                        duration=120,
                        price_process=benchmark_config.price_process,
                        spread=0,
                        mean=-3,
                        sigma=0.5,
                        initial_asset_mint=1e8,
                        tag=f"{benchmark_config.market_config.instrument.code}_{str(i_agent).zfill(3)}",
                    )
                    for i_agent in range(1)
                ]
            )

            if (
                benchmark_config.market_config.is_future()
                or benchmark_config.market_config.is_perp()
            ):
                self.agents.extend(
                    [
                        RiskyMarketOrderTrader(
                            wallet_name="RiskyMarketOrderTrader",
                            key_name=f"RiskyMarketOrderTrader_{benchmark_config.market_config.instrument.code}_{str(i_agent).zfill(3)}",
                            market_name=market_name,
                            side=side,
                            initial_asset_mint=benchmark_config.risky_trader_funds,
                            leverage_factor=0.5,
                            step_bias=0.1,
                            tag=f"{benchmark_config.market_config.instrument.code}_{side}_{str(i_agent).zfill(3)}",
                        )
                        for side in ["SIDE_BUY", "SIDE_SELL"]
                        for i_agent in range(5)
                    ]
                )

        return {agent.name(): agent for agent in self.agents}

    def configure_environment(
        self,
        vega: VegaServiceNull,
        **kwargs,
    ) -> MarketEnvironmentWithState:
        if kwargs.get("network", Network.NULLCHAIN) == Network.NULLCHAIN:
            return MarketEnvironmentWithState(
                agents=list(self.agents.values()),
                n_steps=self.num_steps,
                random_agent_ordering=False,
                transactions_per_block=self.transactions_per_block,
                vega_service=vega,
                step_length_seconds=self.step_length_seconds,
                block_length_seconds=vega.seconds_per_block,
            )
        else:
            return NetworkEnvironment(
                agents=list(self.agents.values()),
                n_steps=self.num_steps,
                vega_service=vega,
                step_length_seconds=self.step_length_seconds,
                raise_datanode_errors=kwargs.get("raise_datanode_errors", False),
                raise_step_errors=kwargs.get("raise_step_errors", False),
                random_state=self.random_state,
                create_keys=True,
                mint_keys=True,
            )
