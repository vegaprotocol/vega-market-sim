from vega_sim.parameter_test.parameter.experiment import SingleParameterExperiment
from vega_sim.parameter_test.parameter.loggers import (
    ideal_market_maker_single_data_extraction,
    target_stake_additional_data,
    v1_ideal_mm_additional_data,
    tau_scaling_additional_data,
    limit_order_book,
)
from vega_sim.scenario.registry import IdealMarketMaker, IdealMarketMakerV2
from vega_sim.parameter_test.parameter.loggers import (
    BASE_IDEAL_MM_CSV_HEADERS,
    LOB_CSV_HEADERS,
)
from vega_sim.parameter_test.parameter.experiment import (
    FILE_PATTERN,
    FILE_PATTERN_LOB,
)

TARGET_STAKE_SCALING_FACTOR_IDEAL = SingleParameterExperiment(
    name="StakeTargetScaling",
    parameter_to_vary="market.stake.target.scalingFactor",
    values=["0.5", "5", "50"],
    scenario=IdealMarketMaker(
        num_steps=288,
        market_decimal=3,
        asset_decimal=5,
        market_position_decimal=2,
        spread=0.002,
        initial_asset_mint=1e8,
        lp_initial_mint=1e8,
        lp_commitamount=50000,
        initial_price=1123.11,
        sigma=0.1,
        kappa=50,
        lambda_val=10,
        q_upper=50,
        q_lower=-50,
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                v1_ideal_mm_additional_data,
                tau_scaling_additional_data,
                target_stake_additional_data,
                limit_order_book,
            ]
        ),
    ),
    runs_per_scenario=2,
    additional_parameters_to_set=[
        ("market.liquidity.targetstake.triggering.ratio", "1")
    ],
    data_extraction=[
        (FILE_PATTERN, BASE_IDEAL_MM_CSV_HEADERS),
        (FILE_PATTERN_LOB, LOB_CSV_HEADERS),
    ],
)

TAU_SCALING_FACTOR_IDEAL = SingleParameterExperiment(
    name="TauScaling",
    parameter_to_vary="market.liquidity.probabilityOfTrading.tau.scaling",
    values=["1", "10", "100"],
    scenario=IdealMarketMaker(
        num_steps=288,
        market_decimal=3,
        asset_decimal=5,
        market_position_decimal=2,
        spread=0.002,
        initial_asset_mint=1e8,
        lp_initial_mint=1e8,
        lp_commitamount=50000,
        initial_price=1123.11,
        sigma=0.1,
        kappa=50,
        lambda_val=10,
        q_upper=50,
        q_lower=-50,
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                v1_ideal_mm_additional_data,
                tau_scaling_additional_data,
                target_stake_additional_data,
                limit_order_book,
            ]
        ),
    ),
    runs_per_scenario=2,
    additional_parameters_to_set=[
        ("market.liquidity.targetstake.triggering.ratio", "1")
    ],
    data_extraction=[
        (FILE_PATTERN, BASE_IDEAL_MM_CSV_HEADERS),
        (FILE_PATTERN_LOB, LOB_CSV_HEADERS),
    ],
)

TARGET_STAKE_SCALING_FACTOR_IDEAL_v2 = SingleParameterExperiment(
    name="StakeTargetScaling_v2",
    parameter_to_vary="market.stake.target.scalingFactor",
    values=["0.5", "5", "50"],
    scenario=IdealMarketMakerV2(
        market_decimal=3,
        asset_decimal=5,
        market_position_decimal=2,
        initial_price=1123.11,
        spread=4,
        lp_commitamount=100000,
        initial_asset_mint=1e8,
        step_length_seconds=60,
        block_length_seconds=1,
        buy_intensity=10,
        sell_intensity=10,
        q_upper=50,
        q_lower=-50,
        kappa=50,
        sigma=0.1,
        num_steps=288,
        backgroundmarket_tick_spacing=0.002,
        backgroundmarket_number_levels_per_side=20,
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                tau_scaling_additional_data,
                target_stake_additional_data,
                limit_order_book,
            ]
        ),
    ),
    runs_per_scenario=2,
    additional_parameters_to_set=[
        ("market.liquidity.targetstake.triggering.ratio", "1")
    ],
    data_extraction=[
        (FILE_PATTERN, BASE_IDEAL_MM_CSV_HEADERS),
        (FILE_PATTERN_LOB, LOB_CSV_HEADERS),
    ],
)

TAU_SCALING_FACTOR_IDEAL_v2 = SingleParameterExperiment(
    name="TauScaling_v2",
    parameter_to_vary="market.liquidity.probabilityOfTrading.tau.scaling",
    values=["1", "10", "100"],
    scenario=IdealMarketMakerV2(
        market_decimal=3,
        asset_decimal=5,
        market_position_decimal=2,
        initial_price=1123.11,
        spread=4,
        lp_commitamount=100000,
        initial_asset_mint=1e8,
        step_length_seconds=60,
        block_length_seconds=1,
        buy_intensity=10,
        sell_intensity=10,
        q_upper=50,
        q_lower=-50,
        kappa=50,
        sigma=0.1,
        num_steps=288,
        backgroundmarket_tick_spacing=0.002,
        backgroundmarket_number_levels_per_side=20,
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                tau_scaling_additional_data,
                target_stake_additional_data,
                limit_order_book,
            ]
        ),
    ),
    runs_per_scenario=2,
    additional_parameters_to_set=[
        ("market.liquidity.targetstake.triggering.ratio", "1")
    ],
    data_extraction=[
        (FILE_PATTERN, BASE_IDEAL_MM_CSV_HEADERS),
        (FILE_PATTERN_LOB, LOB_CSV_HEADERS),
    ],
)

BOND_PENALTY_FACTOR_IDEAL_v2 = SingleParameterExperiment(
    name="BondPenalty_v2",
    parameter_to_vary="market.liquidity.bondPenaltyParameter",
    values=["0.5", "10", "50"],
    scenario=IdealMarketMakerV2(
        market_decimal=3,
        asset_decimal=5,
        market_position_decimal=2,
        initial_price=1123.11,
        spread=0.002,
        lp_commitamount=20000,
        step_length_seconds=60,
        block_length_seconds=1,
        buy_intensity=10,
        sell_intensity=10,
        q_upper=50,
        q_lower=-50,
        kappa=50,
        sigma=0.5,
        num_steps=72,
        state_extraction_fn=ideal_market_maker_single_data_extraction(
            additional_data_fns=[
                tau_scaling_additional_data,
                target_stake_additional_data,
            ]
        ),
    ),
    runs_per_scenario=2,
    additional_parameters_to_set=[
        ("market.liquidity.targetstake.triggering.ratio", "1")
    ],
)


CONFIGS = [
    TARGET_STAKE_SCALING_FACTOR_IDEAL,
    TAU_SCALING_FACTOR_IDEAL,
    TAU_SCALING_FACTOR_IDEAL_v2,
    TARGET_STAKE_SCALING_FACTOR_IDEAL_v2,
    BOND_PENALTY_FACTOR_IDEAL_v2,
]
