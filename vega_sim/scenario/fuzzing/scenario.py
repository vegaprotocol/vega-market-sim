import itertools
import numpy as np
import re
from typing import Optional, List, Dict, Any

import vega_protos.protos as protos
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.benchmark.configs import BenchmarkConfig
from vega_sim.scenario.benchmark.scenario import BenchmarkScenario
from vega_sim.environment.agent import (
    StateAgentWithWallet,
)
from vega_sim.scenario.common.agents import (
    StateAgent,
    RewardFunder,
    ReferralAgentWrapper,
    TransactionDelayChecker,
)
from vega_sim.scenario.fuzzed_markets.agents import (
    FuzzingAgent,
    FuzzyLiquidityProvider,
    FuzzedAutomatedMarketMaker,
    FuzzyReferralProgramManager,
    FuzzyVolumeRebateProgramManager,
    FuzzyVolumeDiscountProgramManager,
)


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
        fuzz_lps: bool = False,
        fuzz_amms: bool = False,
        fuzz_traders: bool = False,
        fuzz_rewards: bool = False,
        fuzz_rebates: bool = False,
        fuzz_referrals: bool = False,
        fuzz_discounts: bool = False,
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

        # Party fuzzing options
        self.__fuzz_lps = fuzz_lps
        self.__fuzz_amms = fuzz_amms
        self.__fuzz_traders = fuzz_traders

        # Program fuzzing options
        self.__fuzz_rebates = fuzz_rebates
        self.__fuzz_referrals = fuzz_referrals
        self.__fuzz_discounts = fuzz_discounts

        # Reward fuzzing options
        self.__fuzz_rewards = fuzz_rewards

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

        # Add a fuzzed volume discount program
        if self.__fuzz_discounts:
            extra_agents.append(
                FuzzyVolumeDiscountProgramManager(
                    wallet_name="FuzzyVolumeDiscountProgramManager",
                    key_name=f"FuzzyVolumeDiscountProgramManager",
                    step_bias=0.01,
                    attempts_per_step=10,
                )
            )
        # Add a fuzzed referral program
        if self.__fuzz_rebates:
            extra_agents.append(
                FuzzyVolumeRebateProgramManager(
                    wallet_name="FuzzyReferralProgramManager",
                    key_name=f"FuzzyReferralProgramManager",
                    step_bias=0.01,
                    attempts_per_step=10,
                )
            )
        # Add a fuzzed referral program
        if self.__fuzz_referrals:
            extra_agents.append(
                FuzzyReferralProgramManager(
                    wallet_name="FuzzyReferralProgramManager",
                    key_name=f"FuzzyReferralProgramManager",
                    step_bias=0.01,
                    attempts_per_step=10,
                )
            )

        # Add simple blank agents as team creators, team members will be added later
        if self.__fuzz_referrals:
            extra_agents.extend(
                [
                    ReferralAgentWrapper(
                        agent=StateAgentWithWallet(
                            wallet_name="ReferralAgentWrapper",
                            key_name=f"ReferralAgentWrapper_{str(i_agent).zfill(3)}",
                            tag=f"{str(i_agent).zfill(3)}",
                        ),
                        is_referrer=True,
                        team_name=f"teamName_{str(i_agent).zfill(3)}",
                        team_url=f"teamUrl_{str(i_agent).zfill(3)}",
                        avatar_url=f"avatarUrl_{str(i_agent).zfill(3)}",
                        closed=False,
                    )
                    for i_agent in range(3)
                ]
            )

        # For each market, add a fuzzing agent and a fuzzy liquidity provider to each
        # team. Agents share keys across markets.
        for benchmark_config in self.benchmark_configs:
            market_name = benchmark_config.market_config.instrument.name
            market_code = benchmark_config.market_config.instrument.code
            if self.__fuzz_traders:
                extra_agents.extend(
                    [
                        ReferralAgentWrapper(
                            agent=FuzzingAgent(
                                wallet_name="FuzzingAgent",
                                key_name=(
                                    f"FuzzingAgent_{str(i_referrer).zfill(3)}_{str(i_agent).zfill(3)}"
                                ),
                                market_name=market_name,
                                settlement_asset_mint=benchmark_config.initial_price
                                / 100,
                                quote_asset_mint=benchmark_config.initial_price / 100,
                                base_asset_mint=1 / 100,
                                tag=f"{market_code}_{str(i_referrer).zfill(3)}_{str(i_agent).zfill(3)}",
                            ),
                            referrer_wallet_name="ReferralAgentWrapper",
                            referrer_key_name=f"ReferralAgentWrapper_{str(i_referrer).zfill(3)}",
                        )
                        for i_referrer, i_agent in itertools.product(range(2), range(2))
                    ]
                )
            if self.__fuzz_lps:
                extra_agents.extend(
                    [
                        ReferralAgentWrapper(
                            agent=FuzzyLiquidityProvider(
                                wallet_name="FuzzyLiquidityProvider",
                                key_name=(
                                    f"FuzzyLiquidityProvider_{str(i_referrer).zfill(3)}_{str(i_agent).zfill(3)}"
                                ),
                                market_name=market_name,
                                initial_asset_mint=5_000,
                                tag=f"{market_code}_{str(i_referrer).zfill(3)}_{str(i_agent).zfill(3)}",
                            ),
                            referrer_wallet_name="ReferralAgentWrapper",
                            referrer_key_name=f"ReferralAgentWrapper_{str(i_referrer).zfill(3)}",
                        )
                        for i_referrer, i_agent in itertools.product(range(2), range(2))
                    ]
                )
            if self.__fuzz_amms:
                extra_agents.extend(
                    [
                        ReferralAgentWrapper(
                            agent=FuzzedAutomatedMarketMaker(
                                wallet_name="FuzzedAutomatedMarketMaker",
                                key_name=(
                                    f"FuzzedAutomatedMarketMaker{str(i_referrer).zfill(3)}_{str(i_agent).zfill(3)}"
                                ),
                                market_name=market_name,
                                submit_probability=0.5,
                                amend_probability=0.5,
                                cancel_probability=0.1,
                                initial_asset_mint=1e6,
                                tag=f"{market_code}_{str(i_referrer).zfill(3)}_{str(i_agent).zfill(3)}",
                            ),
                            referrer_wallet_name="ReferralAgentWrapper",
                            referrer_key_name=f"ReferralAgentWrapper_{str(i_referrer).zfill(3)}",
                        )
                        for i_referrer, i_agent in itertools.product(range(2), range(2))
                    ]
                )
            extra_agents.append(
                TransactionDelayChecker(
                    wallet_name="TransactionDelayChecker",
                    key_name=(f"TransactionDelayChecker_{market_code}"),
                    market_name=market_name,
                    initial_asset_mint=1e6,
                    tag=f"{market_code}",
                    transaction_reordering_enabled=benchmark_config.market_config.enable_transaction_reordering,
                )
            )

        # Create a reward funder for each asset and each reward type
        asset_names = set()
        for benchmark_config in self.benchmark_configs:
            if benchmark_config.market_config.is_spot():
                _, quote_asset_symbol = re.split(
                    r"[^a-zA-Z]+", benchmark_config.market_config.instrument.code
                )[:2]
                asset_names.add(quote_asset_symbol)
            if benchmark_config.market_config.is_future():
                asset_names.add(
                    benchmark_config.market_config.instrument.future.quote_name
                )
            if benchmark_config.market_config.is_perp():
                asset_names.add(
                    benchmark_config.market_config.instrument.perpetual.quote_name
                )
        for i_agent, (account_type, metric, distribution_strategy) in enumerate(
            [
                (
                    protos.vega.vega.ACCOUNT_TYPE_REWARD_MAKER_PAID_FEES,
                    protos.vega.vega.DISPATCH_METRIC_MAKER_FEES_PAID,
                    protos.vega.vega.DistributionStrategy.DISTRIBUTION_STRATEGY_PRO_RATA,
                ),
                (
                    protos.vega.vega.ACCOUNT_TYPE_REWARD_MAKER_RECEIVED_FEES,
                    protos.vega.vega.DISPATCH_METRIC_MAKER_FEES_RECEIVED,
                    protos.vega.vega.DistributionStrategy.DISTRIBUTION_STRATEGY_PRO_RATA,
                ),
                (
                    protos.vega.vega.ACCOUNT_TYPE_REWARD_LP_RECEIVED_FEES,
                    protos.vega.vega.DISPATCH_METRIC_LP_FEES_RECEIVED,
                    protos.vega.vega.DistributionStrategy.DISTRIBUTION_STRATEGY_PRO_RATA,
                ),
                (
                    protos.vega.vega.ACCOUNT_TYPE_REWARD_MARKET_PROPOSERS,
                    protos.vega.vega.DISPATCH_METRIC_MARKET_VALUE,
                    protos.vega.vega.DistributionStrategy.DISTRIBUTION_STRATEGY_PRO_RATA,
                ),
                (
                    protos.vega.vega.ACCOUNT_TYPE_REWARD_AVERAGE_NOTIONAL,
                    protos.vega.vega.DISPATCH_METRIC_AVERAGE_NOTIONAL,
                    protos.vega.vega.DistributionStrategy.DISTRIBUTION_STRATEGY_RANK,
                ),
                (
                    protos.vega.vega.ACCOUNT_TYPE_REWARD_RELATIVE_RETURN,
                    protos.vega.vega.DISPATCH_METRIC_RELATIVE_RETURN,
                    protos.vega.vega.DistributionStrategy.DISTRIBUTION_STRATEGY_RANK,
                ),
                (
                    protos.vega.vega.ACCOUNT_TYPE_REWARD_RETURN_VOLATILITY,
                    protos.vega.vega.DISPATCH_METRIC_RETURN_VOLATILITY,
                    protos.vega.vega.DistributionStrategy.DISTRIBUTION_STRATEGY_RANK,
                ),
                (
                    protos.vega.vega.ACCOUNT_TYPE_REWARD_VALIDATOR_RANKING,
                    protos.vega.vega.DISPATCH_METRIC_VALIDATOR_RANKING,
                    protos.vega.vega.DistributionStrategy.DISTRIBUTION_STRATEGY_RANK,
                ),
                (
                    protos.vega.vega.ACCOUNT_TYPE_REWARD_REALISED_RETURN,
                    protos.vega.vega.DISPATCH_METRIC_REALISED_RETURN,
                    protos.vega.vega.DistributionStrategy.DISTRIBUTION_STRATEGY_RANK,
                ),
                (
                    protos.vega.vega.ACCOUNT_TYPE_REWARD_ELIGIBLE_ENTITIES,
                    protos.vega.vega.DISPATCH_METRIC_ELIGIBLE_ENTITIES,
                    protos.vega.vega.DistributionStrategy.DISTRIBUTION_STRATEGY_RANK_LOTTERY,
                ),
            ]
        ):
            if self.__fuzz_rewards:
                extra_agents.extend(
                    [
                        RewardFunder(
                            wallet_name=f"RewardFunder",
                            key_name=f"RewardFunder_{asset_for_metric_name}_{str(i_agent).zfill(3)}",
                            reward_asset_name="VEGA",
                            account_type=account_type,
                            transfer_amount=100,
                            asset_for_metric_name=asset_for_metric_name,
                            metric=metric,
                            market_names=[market_name],
                            initial_mint=1e9,
                            entity_scope=entity_scope,
                            distribution_strategy=distribution_strategy,
                            tag=(f"{entity_scope}_{asset_for_metric_name}_{metric}"),
                        )
                        for asset_for_metric_name, entity_scope in itertools.product(
                            list(asset_names),
                            [
                                protos.vega.vega.ENTITY_SCOPE_INDIVIDUALS,
                                protos.vega.vega.ENTITY_SCOPE_TEAMS,
                            ],
                        )
                    ]
                )
        extra_agents = {agent.name(): agent for agent in extra_agents}
        agents.update(extra_agents)
        return agents
