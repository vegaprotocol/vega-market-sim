from vega_sim.api.market import MarketConfig

import argparse
import logging
import numpy as np
from typing import Optional, List
from vega_sim.scenario.common.utils.price_process import random_walk

from vega_sim.scenario.scenario import Scenario
from vega_sim.environment.agent import (
    StateAgentWithWallet,
)
from vega_sim.environment.environment import (
    MarketEnvironmentWithState,
    NetworkEnvironment,
)
from vega_sim.scenario.constants import Network
from vega_sim.null_service import VegaServiceNull

from vega_sim.scenario.common.agents import (
    StateAgent,
    UncrossAuctionAgent,
    ExponentialShapedMarketMaker,
    MarketOrderTrader,
    LimitOrderTrader,
    RewardFunder,
    AtTheTouchMarketMaker,
    ReferralAgentWrapper,
)
from vega_sim.scenario.fuzzed_markets.agents import (
    FuzzySuccessorConfigurableMarketManager,
    FuzzingAgent,
    RiskyMarketOrderTrader,
    RiskySimpleLiquidityProvider,
    FuzzyLiquidityProvider,
    FuzzyReferralProgramManager,
    FuzzyVolumeDiscountProgramManager,
    FuzzyRewardFunder,
    FuzzyGovernanceTransferAgent,
)
import itertools

import vega_sim.proto.vega as vega_protos

import datetime
from typing import Optional, Dict
from dataclasses import dataclass
from vega_sim.scenario.common.agents import ExponentialShapedMarketMaker
import pandas as pd


@dataclass
class MarketHistoryAdditionalData:
    at_time: datetime.datetime
    external_prices: Dict[str, float]
    trader_close_outs: Dict[str, int]
    liquidity_provider_close_outs: Dict[str, int]


def state_extraction_fn(vega: VegaServiceNull, agents: dict):
    at_time = vega.get_blockchain_time()

    external_prices = {}
    trader_close_outs = {}
    liquidity_provider_close_outs = {}

    for _, agent in agents.items():
        if isinstance(agent, ExponentialShapedMarketMaker):
            external_prices[agent.market_id] = agent.curr_price
        if isinstance(agent, RiskyMarketOrderTrader):
            trader_close_outs[agent.market_id] = (
                trader_close_outs.get(agent.market_id, 0) + agent.close_outs
            )
        if isinstance(agent, RiskySimpleLiquidityProvider):
            liquidity_provider_close_outs[agent.market_id] = (
                liquidity_provider_close_outs.get(agent.market_id, 0) + agent.close_outs
            )

    return MarketHistoryAdditionalData(
        at_time=at_time,
        external_prices=external_prices,
        trader_close_outs=trader_close_outs,
        liquidity_provider_close_outs=liquidity_provider_close_outs,
    )


def additional_data_to_rows(data) -> List[pd.Series]:
    for market_id in data.external_prices.keys():
        yield {
            "time": data.at_time,
            "market_id": market_id,
            "external_price": data.external_prices.get(market_id, np.NaN),
            "trader_close_outs": data.trader_close_outs.get(market_id, 0),
            "liquidity_provider_close_outs": data.liquidity_provider_close_outs.get(
                market_id, 0
            ),
        }


def _create_price_process(
    random_state: np.random.RandomState, num_steps, decimal_places
):
    price_process = [1500]

    while len(price_process) < num_steps + 1:
        # Add a stable price-process with a random duration of 5-20% of the sim
        price_process = np.concatenate(
            (
                price_process,
                random_walk(
                    num_steps=random_state.randint(
                        int(0.05 * num_steps), int(0.20 * num_steps)
                    ),
                    sigma=2,
                    starting_price=price_process[-1],
                    decimal_precision=decimal_places,
                ),
            )
        )
        # Add an unstable price-process with a random duration of 5-10% of the sim
        price_process = np.concatenate(
            (
                price_process,
                random_walk(
                    num_steps=random_state.randint(
                        int(0.05 * num_steps), int(0.10 * num_steps)
                    ),
                    sigma=2,
                    drift=random_state.uniform(-1, 1),
                    starting_price=price_process[-1],
                    decimal_precision=decimal_places,
                ),
            )
        )

    # Add spikes to the price monitoring auction
    spike_at = random_state.randint(0, num_steps, size=3)
    for i in spike_at:
        price_process[i] = price_process[i] * random_state.choice([0.95, 1.05])

    return price_process


class FuzzingScenario(Scenario):
    def __init__(
        self,
        num_steps: int = 60 * 24 * 30 * 3,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        n_markets: int = 2,
        step_length_seconds: Optional[float] = None,
        fuzz_market_config: Optional[dict] = None,
        output: bool = True,
    ):
        super().__init__(
            state_extraction_fn=lambda vega, agents: state_extraction_fn(vega, agents),
            additional_data_output_fns={
                "additional_data.csv": lambda data: additional_data_to_rows(data),
            },
        )

        self.n_markets = n_markets
        self.fuzz_market_config = fuzz_market_config

        self.num_steps = num_steps
        self.step_length_seconds = (
            step_length_seconds
            if step_length_seconds is not None
            else block_length_seconds
        )

        self.block_length_seconds = block_length_seconds
        self.transactions_per_block = transactions_per_block

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

        self.agents = []
        self.initial_asset_mint = 10e9

        self.agents.append(
            FuzzyReferralProgramManager(
                wallet_name="REFERRAL_PROGRAM_MANAGERS",
                key_name=f"REFERRAL_PROGRAM_MANAGER",
                step_bias=0.2,
                attempts_per_step=100,
            )
        )
        self.agents.append(
            FuzzyVolumeDiscountProgramManager(
                wallet_name="REFERRAL_PROGRAM_MANAGERS",
                key_name=f"REFERRAL_PROGRAM_MANAGER",
                step_bias=0.2,
                attempts_per_step=100,
            )
        )

        for i_market in range(self.n_markets):
            # Define the market and the asset:
            market_name = f"ASSET_{str(i_market).zfill(3)}"
            asset_name = f"ASSET_{str(i_market).zfill(3)}"
            asset_dp = 18

            market_agents = {}
            # Create fuzzed market config
            market_config = MarketConfig()
            market_config.set(
                "liquidity_monitoring_parameters.target_stake_parameters.scaling_factor",
                1e-4,
            )
            if self.fuzz_market_config is not None:
                for param in self.fuzz_market_config:
                    market_config.set(param=self.fuzz_market_config[param])

            # Create fuzzed price process
            price_process = _create_price_process(
                random_state=self.random_state,
                num_steps=self.num_steps,
                decimal_places=int(market_config.decimal_places),
            )

            # Create fuzzed market managers
            market_agents["market_managers"] = [
                FuzzySuccessorConfigurableMarketManager(
                    proposal_wallet_name="MARKET_MANAGER",
                    proposal_key_name="PROPOSAL_KEY",
                    termination_wallet_name="MARKET_MANAGER",
                    termination_key_name="TERMINATION_KEY",
                    market_config=market_config,
                    market_name=market_name,
                    market_code=market_name,
                    asset_dp=asset_dp,
                    asset_name=asset_name,
                    settlement_price=price_process[-1],
                    stake_key=True if kwargs["network"] == Network.CAPSULE else False,
                    tag=f"MARKET_{str(i_market).zfill(3)}",
                    market_agents=market_agents,
                    successor_probability=0.01,
                )
            ]

            market_agents["market_makers"] = [
                ExponentialShapedMarketMaker(
                    wallet_name="MARKET_MAKERS",
                    key_name=f"MARKET_{str(i_market).zfill(3)}",
                    price_process_generator=iter(price_process),
                    initial_asset_mint=self.initial_asset_mint,
                    market_name=market_name,
                    asset_name=asset_name,
                    commitment_amount=1e6,
                    market_decimal_places=market_config.decimal_places,
                    asset_decimal_places=asset_dp,
                    num_steps=self.num_steps,
                    kappa=2.4,
                    tick_spacing=0.05,
                    market_kappa=50,
                    state_update_freq=10,
                    tag=f"MARKET_{str(i_market).zfill(3)}",
                )
            ]

            market_agents["at_touch_market_makers"] = [
                AtTheTouchMarketMaker(
                    wallet_name=f"AT_THE_TOUCH_MM",
                    key_name=f"MARKET_{str(i_market).zfill(3)}",
                    initial_asset_mint=1e5,
                    market_name=market_name,
                    asset_name=asset_name,
                    order_size=1,
                    peg_offset=0,
                    max_position=5,
                    tag=f"MARKET_{str(i_market).zfill(3)}",
                )
            ]

            market_agents["auction_traders"] = [
                UncrossAuctionAgent(
                    wallet_name="AUCTION_TRADERS",
                    key_name=f"MARKET_{str(i_market).zfill(3)}_{side}",
                    side=side,
                    initial_asset_mint=self.initial_asset_mint,
                    price_process=iter(price_process),
                    market_name=market_name,
                    asset_name=asset_name,
                    uncrossing_size=20,
                    tag=(
                        f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
                    ),
                )
                for i_agent, side in enumerate(["SIDE_BUY", "SIDE_SELL"])
            ]

            num_referrers = 2
            market_agents["referrers"] = [
                ReferralAgentWrapper(
                    agent=StateAgentWithWallet(
                        key_name=f"MARKET_{str(i_market).zfill(3)}_REFERRER_{str(i_agent).zfill(3)}",
                        wallet_name="REFERRERS",
                        tag=str(i_agent),
                    ),
                    is_referrer=True,
                    # team_name=f"TEAM_{i_agent}",
                    # team_url=f"URL_{i_agent}",
                    # avatar_url=f"AVATAR_{i_agent}",
                    # closed=False,
                )
                for i_agent in range(num_referrers)
            ]
            market_agents["random_traders"] = [
                ReferralAgentWrapper(
                    agent=MarketOrderTrader(
                        wallet_name="RANDOM_TRADERS",
                        key_name=f"MARKET_{str(i_market).zfill(3)}_REFERRER_{str(i_referrer).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                        market_name=market_name,
                        asset_name=asset_name,
                        buy_intensity=10,
                        sell_intensity=10,
                        base_order_size=1,
                        step_bias=1,
                        tag=f"MARKET_{str(i_market).zfill(3)}_REFERRER_{str(i_referrer).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                    ),
                    referrer_key_name=market_agents["referrers"][0]._agent.key_name,
                    referrer_wallet_name="REFERRERS",
                )
                for i_agent, i_referrer in itertools.product(
                    range(5), range(num_referrers)
                )
            ]

            for i_agent in range(5):
                market_agents["random_traders"].append(
                    LimitOrderTrader(
                        wallet_name=f"RANDOM_TRADERS",
                        key_name=f"LIMIT_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                        market_name=market_name,
                        asset_name=asset_name,
                        time_in_force_opts={"TIME_IN_FORCE_GTT": 1},
                        buy_volume=1,
                        sell_volume=1,
                        buy_intensity=10,
                        sell_intensity=10,
                        submit_bias=1,
                        cancel_bias=0,
                        duration=120,
                        price_process=price_process,
                        spread=0,
                        mean=-3,
                        sigma=0.5,
                        tag=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                    )
                )

            market_agents["fuzz_traders"] = [
                FuzzingAgent(
                    wallet_name="FUZZING_TRADERS",
                    key_name=(
                        f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
                    ),
                    market_name=market_name,
                    asset_name=asset_name,
                    output_plot_on_finalise=self.output,
                    tag=(
                        f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
                    ),
                )
                for i_agent in range(10)
            ]

            market_agents["risky_traders"] = [
                RiskyMarketOrderTrader(
                    wallet_name="risky_traders",
                    key_name=f"MARKET_{str(i_market).zfill(3)}_SIDE_{side}_AGENT_{str(i_agent).zfill(3)}",
                    market_name=market_name,
                    asset_name=asset_name,
                    side=side,
                    initial_asset_mint=1_000,
                    size_factor=0.5,
                    step_bias=0.1,
                    tag=f"MARKET_{str(i_market).zfill(3)}_SIDE_{side}_AGENT_{str(i_agent).zfill(3)}",
                )
                for side in ["SIDE_BUY", "SIDE_SELL"]
                for i_agent in range(10)
            ]

            market_agents["risky_liquidity_providers"] = [
                RiskySimpleLiquidityProvider(
                    wallet_name="risky_liquidity_providers",
                    key_name=f"HIGH_RISK_LPS_MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                    market_name=market_name,
                    asset_name=asset_name,
                    initial_asset_mint=20_000,
                    commitment_factor=0.5,
                    step_bias=0.1,
                    tag=f"HIGH_RISK_LPS_MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                )
                for i_agent in range(5)
            ]

            for i_agent in range(45):
                market_agents["risky_liquidity_providers"].append(
                    RiskySimpleLiquidityProvider(
                        wallet_name="risky_liquidity_providers",
                        key_name=f"LOW_RISK_LPS_MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                        market_name=market_name,
                        asset_name=asset_name,
                        initial_asset_mint=20_000,
                        commitment_factor=0.3,
                        step_bias=0.1,
                        tag=f"LOW_RISK_LPS_MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
                    )
                )

            market_agents["fuzz_liquidity_providers"] = [
                FuzzyLiquidityProvider(
                    wallet_name="FUZZY_LIQUIDITY_PROVIDERS",
                    key_name=(
                        f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
                    ),
                    market_name=market_name,
                    asset_name=asset_name,
                    initial_asset_mint=5_000,
                    tag=(
                        f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
                    ),
                )
            ]

            market_agents["reward_funders"] = [
                RewardFunder(
                    wallet_name="REWARD_FUNDERS",
                    key_name=(
                        f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
                    ),
                    reward_asset_name=vega_protos.vega.DispatchMetric.Name(metric),
                    initial_mint=1e9,
                    account_type=account_type,
                    transfer_amount=100,
                    asset_for_metric_name=asset_name,
                    metric=metric,
                    market_names=[market_name],
                    stake_key=True,
                    tag=(
                        f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
                    ),
                )
                for i_agent, (account_type, metric) in enumerate(
                    [
                        (
                            vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_PAID_FEES,
                            vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_PAID,
                        ),
                        (
                            vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_RECEIVED_FEES,
                            vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_RECEIVED,
                        ),
                        (
                            vega_protos.vega.ACCOUNT_TYPE_REWARD_LP_RECEIVED_FEES,
                            vega_protos.vega.DISPATCH_METRIC_LP_FEES_RECEIVED,
                        ),
                        (
                            vega_protos.vega.ACCOUNT_TYPE_REWARD_MARKET_PROPOSERS,
                            vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE,
                        ),
                        (
                            vega_protos.vega.ACCOUNT_TYPE_REWARD_AVERAGE_POSITION,
                            vega_protos.vega.DISPATCH_METRIC_AVERAGE_POSITION,
                        ),
                        (
                            vega_protos.vega.ACCOUNT_TYPE_REWARD_RELATIVE_RETURN,
                            vega_protos.vega.DISPATCH_METRIC_RELATIVE_RETURN,
                        ),
                        (
                            vega_protos.vega.ACCOUNT_TYPE_REWARD_RETURN_VOLATILITY,
                            vega_protos.vega.DISPATCH_METRIC_RETURN_VOLATILITY,
                        ),
                        (
                            vega_protos.vega.ACCOUNT_TYPE_REWARD_VALIDATOR_RANKING,
                            vega_protos.vega.DISPATCH_METRIC_VALIDATOR_RANKING,
                        ),
                    ]
                )
            ]
            market_agents["fuzzy_reward_funders"] = [
                FuzzyRewardFunder(
                    wallet_name="REWARD_FUNDERS",
                    key_name=f"MARKET_{str(i_market).zfill(3)}",
                    asset_name=asset_name,
                    step_bias=1,
                    validity_bias=0.8,
                    attempts_per_step=10,
                    tag=f"MARKET_{str(i_market).zfill(3)}",
                )
            ]
            market_agents["fuzzy_governance_transfer_agents"] = [
                FuzzyGovernanceTransferAgent(
                    wallet_name="REWARD_FUNDERS",
                    key_name=f"MARKET_{str(i_market).zfill(3)}",
                    asset_name=asset_name,
                    step_bias=1,
                    validity_bias=0.99,
                    attempts_per_step=10,
                    tag=f"MARKET_{str(i_market).zfill(3)}",
                )
            ]
            for _, agent_list in market_agents.items():
                self.agents.extend(agent_list)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

    scenario = FuzzingScenario(
        num_steps=10000,
        step_length_seconds=5,
        block_length_seconds=1,
        transactions_per_block=4096,
    )

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=True,
        use_full_vega_wallet=False,
        retain_log_files=True,
        launch_graphql=True,
        seconds_per_block=scenario.block_length_seconds,
        transactions_per_block=scenario.transactions_per_block,
    ) as vega:
        scenario.run_iteration(
            vega=vega,
            pause_at_completion=False,
        )
