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
import vega_protos.protos as protos


class SLAScenario(BenchmarkScenario):
    def __init__(
        self,
        market_config: MarketConfig,
        initial_price: int,
        annualised_volatility: float = 1.5,
        notional_trade_volume: int = 100,
        num_steps: int = 60 * 24 * 30 * 3,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        step_length_seconds: Optional[float] = None,
        output: bool = True,
        lps_offset: List[float] = [0.5, 0.5],
        lps_target_time_on_book: List[float] = [1, 0.95],
        lps_commitment_amount: List[float] = [10000, 10000],
        override_price_range: Optional[float] = None,
        override_sla_competition_factor: Optional[float] = None,
        override_commitment_min_time_fraction: Optional[float] = None,
        override_performance_hysteresis_epochs: Optional[int] = None,
        initial_network_parameters: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            market_config=market_config,
            initial_price=initial_price,
            annualised_volatility=annualised_volatility,
            notional_trade_volume=notional_trade_volume,
            num_steps=num_steps,
            transactions_per_block=transactions_per_block,
            block_length_seconds=block_length_seconds,
            step_length_seconds=step_length_seconds,
            output=output,
            initial_network_parameters=initial_network_parameters,
        )

        # Set simulation parameters
        self.num_steps = num_steps
        self.step_length_seconds = (
            step_length_seconds
            if step_length_seconds is not None
            else block_length_seconds
        )
        self.block_length_seconds = block_length_seconds
        self.transactions_per_block = transactions_per_block

        # Set market config parameters
        self.market_config = (
            MarketConfig("future") if market_config is None else market_config
        )
        if override_price_range is not None:
            self.market_config.liquidity_sla_parameters.price_range = (
                override_price_range
            )
        if override_sla_competition_factor is not None:
            self.market_config.liquidity_sla_parameters.sla_competition_factor = (
                override_sla_competition_factor
            )
        if override_commitment_min_time_fraction is not None:
            self.market_config.liquidity_sla_parameters.commitment_min_time_fraction = (
                override_commitment_min_time_fraction
            )
        if override_performance_hysteresis_epochs is not None:
            self.market_config.liquidity_sla_parameters.performance_hysteresis_epochs = (
                override_performance_hysteresis_epochs
            )

        # Validate and set LP parameters
        lengths = [
            len(var)
            for var in [lps_offset, lps_target_time_on_book, lps_commitment_amount]
        ]
        if lengths[:-1] != lengths[1:]:
            raise ValueError(
                "The lengths of 'lps_offset', 'lps_target_time_on_book', and "
                + "'lps_commitment_amount' must all be the same."
            )
        self.lps_offset = lps_offset
        self.lps_target_time_on_book = lps_target_time_on_book
        self.lps_commitment_amount = lps_commitment_amount

        self.output = output

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
