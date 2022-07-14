from vega_sim.parameter_test.parameter.experiment import SingleParameterExperiment
from vega_sim.parameter_test.parameter.loggers import (
    ideal_market_maker_single_data_extraction,
    target_stake_additional_data,
    v1_ideal_mm_additional_data,
    tau_scaling_additional_data,
)
from vega_sim.scenario.registry import IdealMarketMaker, IdealMarketMakerV2

TARGET_STAKE_SCALING_FACTOR_IDEAL = SingleParameterExperiment(
    name="StakeTargetScaling",
    parameter_to_vary="market.stake.target.scalingFactor",
    values=["0.5", "5", "50"],
    scenario=IdealMarketMaker(
        num_steps=100,
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                v1_ideal_mm_additional_data,
                target_stake_additional_data,
            ]
        ),
    ),
    runs_per_scenario=3,
    additional_parameters_to_set=[
        ("market.liquidity.targetstake.triggering.ratio", "1")
    ],
)

TAU_SCALING_FACTOR_IDEAL = SingleParameterExperiment(
    name="TauScaling",
    parameter_to_vary="market.liquidity.probabilityOfTrading.tau.scaling",
    values=["1", "10", "100"],
    scenario=IdealMarketMaker(
        num_steps=100,
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                v1_ideal_mm_additional_data,
                tau_scaling_additional_data,
            ]
        ),
    ),
    runs_per_scenario=3,
    additional_parameters_to_set=[
        ("market.liquidity.targetstake.triggering.ratio", "1")
    ],
)

TARGET_STAKE_SCALING_FACTOR_IDEAL_v2 = SingleParameterExperiment(
    name="StakeTargetScaling_v2",
    parameter_to_vary="market.stake.target.scalingFactor",
    values=["0.5", "5", "50"],
    scenario=IdealMarketMakerV2(
        initial_price=10,
        step_length_seconds=60,
        block_length_seconds=1,
        buy_intensity=2,
        sell_intensity=2,
        kappa=1,
        sigma=200,
        num_steps=200,
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                target_stake_additional_data,
            ]
        ),
    ),
    runs_per_scenario=20,
    additional_parameters_to_set=[
        ("market.liquidity.targetstake.triggering.ratio", "1")
    ],
)

TAU_SCALING_FACTOR_IDEAL_v2 = SingleParameterExperiment(
    name="TauScaling_v2",
    parameter_to_vary="market.liquidity.probabilityOfTrading.tau.scaling",
    values=["1", "10", "100"],
    scenario=IdealMarketMakerV2(
        initial_price=10,
        step_length_seconds=60,
        block_length_seconds=1,
        buy_intensity=2,
        sell_intensity=2,
        kappa=1,
        sigma=200,
        num_steps=200,
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[tau_scaling_additional_data]
        ),
    ),
    runs_per_scenario=3,
    additional_parameters_to_set=[
        ("market.liquidity.targetstake.triggering.ratio", "1")
    ],
)

CONFIGS = [
    TARGET_STAKE_SCALING_FACTOR_IDEAL,
    TAU_SCALING_FACTOR_IDEAL,
    TAU_SCALING_FACTOR_IDEAL_v2,
    TARGET_STAKE_SCALING_FACTOR_IDEAL_v2,
]
