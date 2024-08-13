"""vega_sim/build/vega.py

Moule contains functions for building protobuf messages defined in
vega/protos/sources/vega/vega.proto

Attributes:
    logger (logging.Logger): module level logger
"""

import logging

import vega_python_protos.protos.vega as vega_protos

from typing import Optional, List
from vega_sim.builders.exceptions import raise_custom_build_errors


logger = logging.getLogger(__name__)


@raise_custom_build_errors
def dispatch_strategy(
    asset_for_metric: str,
    metric: vega_protos.vega.DispatchMetric.Value,
    entity_scope: vega_protos.vega.EntityScope.Value,
    window_length: int,
    lock_period: int,
    distribution_strategy: vega_protos.vega.DistributionStrategy.Value,
    markets: Optional[List[str]] = None,
    individual_scope: Optional[vega_protos.vega.IndividualScope.Value] = None,
    team_scope: Optional[List[str]] = None,
    n_top_performers: Optional[float] = None,
    staking_requirement: Optional[float] = None,
    notional_time_weighted_average_position_requirement: Optional[float] = None,
    rank_table: Optional[List[vega_protos.vega.Rank]] = None,
) -> vega_protos.vega.DispatchStrategy:
    dispatch_strategy = vega_protos.vega.DispatchStrategy(
        asset_for_metric=asset_for_metric,
        entity_scope=entity_scope,
        individual_scope=individual_scope,
        window_length=window_length,
        lock_period=lock_period,
        distribution_strategy=distribution_strategy,
    )
    if metric is not None:
        setattr(dispatch_strategy, "metric", metric)
    if staking_requirement is not None:
        setattr(dispatch_strategy, "staking_requirement", str(staking_requirement))
    if notional_time_weighted_average_position_requirement is not None:
        setattr(
            dispatch_strategy,
            "notional_time_weighted_average_position_requirement",
            str(notional_time_weighted_average_position_requirement),
        )
    if n_top_performers is not None:
        setattr(
            dispatch_strategy,
            "n_top_performers",
            str(n_top_performers),
        )
    if markets is not None:
        dispatch_strategy.markets.extend(markets)
    if team_scope is not None:
        dispatch_strategy.team_scope.extend(team_scope)
    if rank_table is not None:
        dispatch_strategy.rank_table.extend(rank_table)
    return dispatch_strategy


@raise_custom_build_errors
def rank(start_rank: int, share_ratio: int) -> vega_protos.vega.Rank:
    return vega_protos.vega.Rank(start_rank=start_rank, share_ratio=share_ratio)


@raise_custom_build_errors
def reward_factors(
    infrastructure_reward_factor: float,
    liquidity_reward_factor: float,
    maker_reward_factor: float,
) -> vega_protos.vega.RewardFactors:
    return vega_protos.vega.RewardFactors(
        infrastructure_reward_factor=str(infrastructure_reward_factor),
        liquidity_reward_factor=str(liquidity_reward_factor),
        maker_reward_factor=str(maker_reward_factor),
    )


@raise_custom_build_errors
def discount_factors(
    infrastructure_discount_factor: float,
    liquidity_discount_factor: float,
    maker_discount_factor: float,
) -> vega_protos.vega.DiscountFactors:
    return vega_protos.vega.DiscountFactors(
        infrastructure_discount_factor=str(infrastructure_discount_factor),
        liquidity_discount_factor=str(liquidity_discount_factor),
        maker_discount_factor=str(maker_discount_factor),
    )
