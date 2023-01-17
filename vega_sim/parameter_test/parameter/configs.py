from vega_sim.parameter_test.parameter.experiment import SingleParameterExperiment
from vega_sim.parameter_test.parameter.loggers import (
    ideal_market_maker_single_data_extraction,
    target_stake_additional_data,
    tau_scaling_additional_data,
    limit_order_book,
)
from vega_sim.scenario.parameter_experiment.scenario import ParameterExperiment
from vega_sim.parameter_test.parameter.loggers import (
    BASE_IDEAL_MM_CSV_HEADERS,
    LOB_CSV_HEADERS,
)
from vega_sim.parameter_test.parameter.experiment import (
    FILE_PATTERN,
    FILE_PATTERN_LOB,
)

TARGET_STAKE_SCALING_FACTOR = SingleParameterExperiment(
    name="TargetStakeScalingFactor",
    parameter_type="market",
    parameter_to_vary="liquidity_monitoring_parameters.target_stake_parameters.scaling_factor",
    values=[0.5, 5, 50],
    scenario=ParameterExperiment(
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                tau_scaling_additional_data,
                target_stake_additional_data,
                limit_order_book,
            ]
        ),
    ),
    runs_per_scenario=2,
    additional_market_parameters_to_set={
        "liquidity_monitoring_parameters.triggering_ratio": "1",
    },
    data_extraction=[
        (FILE_PATTERN, BASE_IDEAL_MM_CSV_HEADERS),
        (FILE_PATTERN_LOB, LOB_CSV_HEADERS),
    ],
)

TAU_SCALING_FACTOR = SingleParameterExperiment(
    name="TauScalingFactor",
    parameter_type="network",
    parameter_to_vary="market.liquidity.probabilityOfTrading.tau.scaling",
    values=["1", "10", "100"],
    scenario=ParameterExperiment(
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                tau_scaling_additional_data,
                target_stake_additional_data,
                limit_order_book,
            ]
        ),
    ),
    runs_per_scenario=2,
    additional_market_parameters_to_set={
        "liquidity_monitoring_parameters.triggering_ratio": "1",
    },
    data_extraction=[
        (FILE_PATTERN, BASE_IDEAL_MM_CSV_HEADERS),
        (FILE_PATTERN_LOB, LOB_CSV_HEADERS),
    ],
)

BOND_PENALTY_PARAMETER = SingleParameterExperiment(
    name="BondPenaltyFactor",
    parameter_type="network",
    parameter_to_vary="market.liquidity.bondPenaltyParameter",
    values=["0.0", "0.5", "1.0"],
    scenario=ParameterExperiment(
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                tau_scaling_additional_data,
                target_stake_additional_data,
                limit_order_book,
            ]
        ),
    ),
    runs_per_scenario=2,
    additional_market_parameters_to_set={
        "liquidity_monitoring_parameters.triggering_ratio": "1",
    },
    data_extraction=[
        (FILE_PATTERN, BASE_IDEAL_MM_CSV_HEADERS),
        (FILE_PATTERN_LOB, LOB_CSV_HEADERS),
    ],
)


CONFIGS = [
    TARGET_STAKE_SCALING_FACTOR,
    TAU_SCALING_FACTOR,
    BOND_PENALTY_PARAMETER,
]
