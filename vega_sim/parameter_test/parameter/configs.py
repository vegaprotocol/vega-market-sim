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

MARGIN_SCALING_FACTORS = SingleParameterExperiment(
    name="MarginScalingFactors",
    parameter_type="network",
    parameter_to_vary=("market.margin.scalingFactors"),
    values=[
        """{"search_level": 1.050, "initial_margin": 1.100, "collateral_release": 1.150}""",
        """{"search_level": 1.001, "initial_margin": 2.000, "collateral_release": 4.000}""",
    ],
    scenario=ParameterExperiment(
        num_steps=60 * 20,
        step_length_seconds=1,
        block_length_seconds=1,
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                tau_scaling_additional_data,
                target_stake_additional_data,
                limit_order_book,
            ]
        ),
        run_with_degen_agents=False,
    ),
    runs_per_scenario=1,
    additional_market_parameters_to_set={
        "liquidity_monitoring_parameters.triggering_ratio": "1",
    },
    data_extraction=[
        (FILE_PATTERN, BASE_IDEAL_MM_CSV_HEADERS),
        (FILE_PATTERN_LOB, LOB_CSV_HEADERS),
    ],
)

MARK_PRICE_UPDATE_FREQUENCY = SingleParameterExperiment(
    name="MarkPriceUpdateFrequency",
    parameter_type="network",
    parameter_to_vary=("network.markPriceUpdateMaximumFrequency"),
    values=["2s", "10s", "30s", "60s"],
    scenario=ParameterExperiment(
        num_steps=60 * 20,
        step_length_seconds=1,
        block_length_seconds=1,
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                tau_scaling_additional_data,
                target_stake_additional_data,
                limit_order_book,
            ]
        ),
        run_with_degen_agents=False,
    ),
    runs_per_scenario=1,
    additional_market_parameters_to_set={
        "liquidity_monitoring_parameters.triggering_ratio": "1",
    },
    data_extraction=[
        (FILE_PATTERN, BASE_IDEAL_MM_CSV_HEADERS),
        (FILE_PATTERN_LOB, LOB_CSV_HEADERS),
    ],
)

TARGET_STAKE_SCALING_FACTOR = SingleParameterExperiment(
    name="TargetStakeScalingFactor",
    parameter_type="market",
    parameter_to_vary=(
        "liquidity_monitoring_parameters.target_stake_parameters.scaling_factor"
    ),
    values=[0.5, 5, 50],
    scenario=ParameterExperiment(
        num_steps=60 * 20,
        step_length_seconds=1,
        block_length_seconds=1,
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
    values=["10", "100", "1000"],
    scenario=ParameterExperiment(
        num_steps=60 * 20,
        step_length_seconds=1,
        block_length_seconds=1,
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
        num_steps=60 * 20,
        step_length_seconds=1,
        block_length_seconds=1,
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
    MARGIN_SCALING_FACTORS,
    MARK_PRICE_UPDATE_FREQUENCY,
]
