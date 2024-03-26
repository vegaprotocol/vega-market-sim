import numpy as np
from typing import Optional, List, Dict, Any

from vega_sim.api.market import MarketConfig
from vega_sim.null_service import VegaServiceNull

from vega_sim.scenario.benchmark.scenario import BenchmarkScenario
from vega_sim.configs.agents import ConfigurableMarketManager
from vega_sim.scenario.common.agents import (
    StateAgent,
    ExponentialShapedMarketMaker,
    SimpleLiquidityProvider,
    RewardFunder,
)
import vega_sim.proto as protos

from vega_sim.scenario.benchmark.configs import BenchmarkConfig


class FuzzingScenario(BenchmarkScenario):
    def __init__(
        self,
        benchmark_configs: List[BenchmarkConfig],
        num_steps: int = 60 * 24 * 30 * 3,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        step_length_seconds: Optional[float] = None,
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
        for agent in agents.values():
            if isinstance(agent, ExponentialShapedMarketMaker):
                # Set commitment amount to 0 to avoid benchmark market maker from
                # providing liquidity, they should only supply volume through orders.
                agent.commitment_amount = 0

        market_name = self.market_config.instrument.name
        if self.market_config.is_future():
            asset_name = self.market_config.instrument.future.quote_name
        if self.market_config.is_perp():
            asset_name = self.market_config.instrument.perpetual.quote_name

        extra_agents = []
        for i in range(len(self.lps_commitment_amount)):
            extra_agents.append(
                SimpleLiquidityProvider(
                    key_name=f"simple_liquidity_provider_{i}",
                    market_name=market_name,
                    initial_asset_mint=1e9,
                    offset_proportion=self.lps_offset[i],
                    commitment_amount=self.lps_commitment_amount[i],
                    target_time_on_book=self.lps_target_time_on_book[i],
                    bid_inner_bound_fn=lambda vega_state, market_id: vega_state.market_state[
                        market_id
                    ].midprice,
                    bid_outer_bound_fn=lambda vega_state, market_id: vega_state.market_state[
                        market_id
                    ].midprice
                    * (1 - self.market_config.liquidity_sla_parameters.price_range),
                    ask_inner_bound_fn=lambda vega_state, market_id: vega_state.market_state[
                        market_id
                    ].midprice,
                    ask_outer_bound_fn=lambda vega_state, market_id: vega_state.market_state[
                        market_id
                    ].midprice
                    * (1 + self.market_config.liquidity_sla_parameters.price_range),
                    fee=0.0001,
                    tag=str(i),
                    random_state=random_state,
                    commitment_amount_to_minimum_weighting=2,
                    commitment_amount_to_peak_weighting=3,
                    commitment_amount_to_size_weighting=5,
                )
            )
        extra_agents.append(
            RewardFunder(
                key_name=f"reward_funder",
                reward_asset_name="VEGA",
                account_type=protos.vega.vega.AccountType.ACCOUNT_TYPE_REWARD_LP_RECEIVED_FEES,
                transfer_amount=100,
                asset_for_metric_name=asset_name,
                metric=protos.vega.vega.DispatchMetric.DISPATCH_METRIC_LP_FEES_RECEIVED,
                market_names=[market_name],
                initial_mint=1e9,
            )
        )
        extra_agents = {agent.name(): agent for agent in extra_agents}
        agents.update(extra_agents)
        return agents
