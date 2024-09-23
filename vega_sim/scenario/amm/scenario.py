import itertools
import numpy as np
import re
from typing import Optional, List, Dict, Any

from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.benchmark.configs import BenchmarkConfig
from vega_sim.scenario.benchmark.scenario import BenchmarkScenario
from vega_sim.scenario.common.agents import (
    StateAgent,
    AutomatedMarketMaker,
    MarketOrderTrader,
    LimitOrderTrader,
    ExponentialShapedMarketMaker,
)

class AMMScenario(BenchmarkScenario):
    def __init__(
        self,
        benchmark_configs: List[BenchmarkConfig],
        num_steps: int = 60 * 24 * 30 * 3,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        step_length_seconds: Optional[float] = None,
        amm_liquidity_fee: float = 0.0001,
        amm_update_frequency: float = 0.1,
        output: bool = True,
        initial_network_parameters: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            benchmark_configs=benchmark_configs,
            num_steps=num_steps,
            transactions_per_block=transactions_per_block,
            block_length_seconds=block_length_seconds,
            step_length_seconds=step_length_seconds,
            output=output,
            initial_network_parameters=initial_network_parameters,
        )

        self.amm_liquidity_fee = amm_liquidity_fee
        self.amm_update_frequency = amm_update_frequency

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
        agents = super().configure_agents(vega, tag, random_state, **kwargs)
        extra_agents = []

        agents = super().configure_agents(vega, tag, random_state, **kwargs)
        for agent in agents.values():
            if isinstance(agent, ExponentialShapedMarketMaker):
                # Set commitment amount to 0 to avoid benchmark market maker from
                # providing liquidity, they should only supply volume through orders.
                agent.fee_amount = self.amm_liquidity_fee
                agent.commitment_amount = 0.000001
                agent.supplied_amount = 0

            # if isinstance(agent, MarketOrderTrader):
            #     # Set commitment amount to 0 to avoid benchmark market maker from
            #     # providing liquidity, they should only supply volume through orders.
            #     agent.fee_amount = self.amm_liquidity_fee
            #     agent.commitment_amount =10
            #     agent.supplied_amount = 50

            # if isinstance(agent, LimitOrderTrader):
            #     # Set commitment amount to 0 to avoid benchmark market maker from
            #     # providing liquidity, they should only supply volume through orders.
            #     agent.spread = 0
            #     agent.mean = -7.5
            #     agent.sigma = 0.3

        # For each market, add an AMM agent.
        for benchmark_config in self.benchmark_configs:
            i_agent = 0
            extra_agents.append(
                AutomatedMarketMaker(
                    wallet_name="AutomatedMarketMaker",
                    key_name=f"AutomatedMarketMaker_{benchmark_config.market_config.instrument.code}_{str(i_agent).zfill(3)}",
                    market_name=benchmark_config.market_config.instrument.name,
                    initial_asset_mint=1e5,
                    commitment_amount=6000,
                    slippage_tolerance=0.05,
                    proposed_fee=self.amm_liquidity_fee,
                    price_process=iter(benchmark_config.price_process),
                    lower_bound_scaling=1 - 0.02,
                    upper_bound_scaling=1 + 0.02,
                    leverage_at_lower_bound=20,
                    leverage_at_upper_bound=20,
                    update_bias=self.amm_update_frequency,
                    tag=f"{benchmark_config.market_config.instrument.code}_{str(i_agent).zfill(3)}",
                    random_state=self.random_state,
                )
            )

        extra_agents = {agent.name(): agent for agent in extra_agents}
        agents.update(extra_agents)
        return agents
