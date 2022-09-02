import argparse
import logging
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.ideal_market_maker_v2.scenario import IdealMarketMaker
from vega_sim.scenario.common.utils.price_process import (
    get_historic_price_series,
    Granularity,
)
from vega_sim.parameter_test.parameter.loggers import (
    ideal_market_maker_single_data_extraction,
    target_stake_additional_data,
    tau_scaling_additional_data,
)

scenario = IdealMarketMaker(
    num_steps=288,
    market_decimal=2,
    asset_decimal=4,
    market_position_decimal=4,
    market_name="ETH:USD",
    asset_name="USD",
    price_process_fn=lambda: get_historic_price_series(
            product_id="ETH-USD", 
            granularity=Granularity.HOUR,
            # start="2022-08-15 00:00:00",
            # end="2022-09-01 00:00:00",
    ).values,
    step_length_seconds=60,
    block_length_seconds=1,
    buy_intensity=100,
    sell_intensity=100,
    q_upper=10,
    q_lower=-10,
    kappa=0.5,
    opening_auction_trade_amount=0.0001,
    backgroundmarket_tick_spacing=0.02,
    backgroundmarket_number_levels_per_side=40,
    market_order_trader_base_order_size=0.001,
    state_extraction_fn=ideal_market_maker_single_data_extraction(
        additional_data_fns=[
            tau_scaling_additional_data,
            target_stake_additional_data,
    ]
),
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=True,
        retain_log_files=True,
    ) as vega:

        results = scenario.run_iteration(
            vega=vega,
            pause_at_completion=True,
        )