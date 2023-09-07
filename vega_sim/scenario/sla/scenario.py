import argparse
import logging
import numpy as np
from typing import Optional, List, Dict

from vega_sim.api.market import MarketConfig
from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.constants import Network
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.configurable_market.agents import ConfigurableMarketManager
from vega_sim.scenario.common.utils.price_process import random_walk
from vega_sim.environment.environment import (
    MarketEnvironmentWithState,
    NetworkEnvironment,
)
from vega_sim.scenario.common.agents import (
    StateAgent,
    UncrossAuctionAgent,
    ExponentialShapedMarketMaker,
    MarketOrderTrader,
    SimpleLiquidityProvider,
)


def final_extraction(vega: VegaServiceNull, agents: dict):
    results = []
    for _, agent in agents.items():
        if isinstance(agent, SimpleLiquidityProvider):
            from_ledger_entries = vega.list_ledger_entries(
                from_party_ids=[agent._public_key],
                transfer_types=[14, 20, 30, 31, 32, 33, 34, 35],
            )
            to_ledger_entries = vega.list_ledger_entries(
                to_party_ids=[agent._public_key],
                transfer_types=[14, 20, 30, 31, 32, 33, 34, 35],
            )
            results = results + from_ledger_entries + to_ledger_entries
    return results


def additional_data_to_rows(data) -> List[Dict]:
    results = []
    for ledger_entry in data:
        results.append(
            {
                "time": ledger_entry.timestamp,
                "quantity": ledger_entry.quantity,
                "transfer_type": ledger_entry.transfer_type,
                "asset_id": ledger_entry.asset_id,
                "from_account_type": ledger_entry.from_account_type,
                "to_account_type": ledger_entry.to_account_type,
                "from_account_party_id": ledger_entry.from_account_party_id,
                "to_account_party_id": ledger_entry.to_account_party_id,
                "from_account_market_id": ledger_entry.from_account_market_id,
                "to_account_market_id": ledger_entry.to_account_market_id,
            }
        )
    return results


class SLAScenario(Scenario):
    def __init__(
        self,
        num_steps: int = 3000,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        step_length_seconds: Optional[float] = None,
        market_name: str = "SLA Example Market",
        market_code: str = "SLA",
        asset_name: str = "USDT",
        asset_decimals: int = 18,
        output: bool = True,
        epoch_length: str = "10m",
        price_range: float = "0.5",
        commitment_min_time_fraction: float = "1",
        providers_fee_calculation_time_step: str = "1s",
        performance_hysteresis_epochs: int = 1,
        sla_competition_factor: float = "1",
        lps_offset: List[float] = [0.5, 0.5],
        lps_target_time_on_book: List[float] = [1, 0.95],
        lps_commitment_amount: List[float] = [10000, 10000],
    ):
        super().__init__(
            # state_extraction_fn=lambda vega, agents: state_extraction(vega, agents),
            final_extraction_fn=lambda vega, agents: final_extraction(vega, agents),
            additional_data_output_fns={
                "ledger_entries.csv": lambda data: additional_data_to_rows(data),
            },
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

        # Set market parameters
        self.market_name = market_name
        self.market_code = market_code
        self.asset_name = asset_name
        self.asset_decimals = asset_decimals

        # SLA parameters
        self.price_range = price_range
        self.commitment_min_time_fraction = commitment_min_time_fraction
        self.providers_fee_calculation_time_step = providers_fee_calculation_time_step
        self.performance_hysteresis_epochs = performance_hysteresis_epochs
        self.sla_competition_factor = sla_competition_factor
        self.epoch_length = epoch_length

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
    ) -> List[StateAgent]:
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

        price_process = random_walk(
            num_steps=self.num_steps + 1,
            sigma=0.5,
            starting_price=1500,
            decimal_precision=self.asset_decimals,
        )
        # Add spikes to trigger price monitoring auctions
        for i in self.random_state.randint(0, self.num_steps, size=2):
            price_process[i] = price_process[i] * 10

        market_config = MarketConfig()
        market_config.set("liquidity_sla_parameters.price_range", self.price_range)
        market_config.set(
            "liquidity_sla_parameters.commitment_min_time_fraction",
            self.commitment_min_time_fraction,
        )
        market_config.set(
            "liquidity_sla_parameters.performance_hysteresis_epochs",
            self.performance_hysteresis_epochs,
        )
        market_config.set(
            "liquidity_sla_parameters.sla_competition_factor",
            self.sla_competition_factor,
        )

        agents = []

        agents.append(
            ConfigurableMarketManager(
                proposal_key_name="configurable_market_manager",
                termination_key_name="configurable_market_manager",
                market_config=market_config,
                market_name=self.market_name,
                market_code=self.market_code,
                asset_name=self.asset_name,
                asset_dp=self.asset_decimals,
                settlement_price=price_process[-1],
                network_parameters={
                    "validators.epoch.length": self.epoch_length,
                    "market.liquidity.providersFeeCalculationTimeStep": self.providers_fee_calculation_time_step,
                },
            )
        )
        agents.append(
            ExponentialShapedMarketMaker(
                key_name=f"market_maker",
                price_process_generator=iter(price_process),
                initial_asset_mint=1e9,
                market_name=self.market_name,
                asset_name=self.asset_name,
                commitment_amount=0,
                supplied_amount=1e9,
                market_decimal_places=market_config.decimal_places,
                asset_decimal_places=self.asset_decimals,
                num_steps=self.num_steps,
                kappa=1.2,
                tick_spacing=0.05,
                market_kappa=50,
                state_update_freq=10,
            )
        )
        agents.append(
            UncrossAuctionAgent(
                key_name="uncross_auction_agent_bid",
                side="SIDE_BUY",
                initial_asset_mint=1e9,
                price_process=iter(price_process),
                market_name=self.market_name,
                asset_name=self.asset_name,
                uncrossing_size=1,
                tag="bid",
            )
        )
        agents.append(
            UncrossAuctionAgent(
                key_name="uncross_auction_agent_ask",
                side="SIDE_SELL",
                initial_asset_mint=1e9,
                price_process=iter(price_process),
                market_name=self.market_name,
                asset_name=self.asset_name,
                uncrossing_size=1,
                tag="ask",
            )
        )
        agents.append(
            MarketOrderTrader(
                key_name="market_order_trader",
                market_name=self.market_name,
                asset_name=self.asset_name,
                buy_intensity=10,
                sell_intensity=10,
                base_order_size=1,
                step_bias=1,
            )
        )
        for i in range(len(self.lps_commitment_amount)):
            agents.append(
                SimpleLiquidityProvider(
                    key_name=f"simple_liquidity_provider_{i}",
                    market_name=self.market_name,
                    asset_name=self.asset_name,
                    initial_asset_mint=1e9,
                    offset_proportion=self.lps_offset[i],
                    commitment_amount=self.lps_commitment_amount[i],
                    target_time_on_book=self.lps_target_time_on_book[i],
                    bid_inner_bound_fn=lambda vega_state, market_id: vega_state.market_state[
                        market_id
                    ].best_bid_price,
                    bid_outer_bound_fn=lambda vega_state, market_id: vega_state.market_state[
                        market_id
                    ].min_valid_price,
                    ask_inner_bound_fn=lambda vega_state, market_id: vega_state.market_state[
                        market_id
                    ].best_ask_price,
                    ask_outer_bound_fn=lambda vega_state, market_id: vega_state.market_state[
                        market_id
                    ].max_valid_price,
                    fee=0.0001,
                    tag=str(i),
                    random_state=random_state,
                )
            )

        return {agent.name: agent for agent in agents}

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
