import argparse
import logging
import pathlib
import csv
import pandas as pd

from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.comprehensive_market.scenario import ComprehensiveMarket
from vega_sim.scenario.common.utils.price_process import (
    get_historic_price_series,
    Granularity,
)
from vega_sim.parameter_test.parameter.loggers import (
    momentum_trader_data_extraction,
)

scenario = ComprehensiveMarket(
    num_steps=670,
    market_decimal=2,
    asset_decimal=4,
    market_position_decimal=4,
    market_name="ETH:USD",
    asset_name="USD",
    price_process_fn=lambda: pd.concat(
        (
            get_historic_price_series(
                product_id="ETH-USD",
                granularity=Granularity.HOUR,
                start="2022-08-08 12:00:00",
                end="2022-08-11 12:00:00",
            ),
            get_historic_price_series(
                product_id="ETH-USD",
                granularity=Granularity.HOUR,
                start="2022-08-11 12:00:00",
                end="2022-08-23 21:00:00",
            ),
            get_historic_price_series(
                product_id="ETH-USD",
                granularity=Granularity.HOUR,
                start="2022-08-23 22:00:00",
                end="2022-09-05 09:00:00",
            ),
        )
    ).values,
    step_length_seconds=60,
    block_length_seconds=1,
    opening_auction_trade_amount=0.0001,
    num_mo_agents=0,
    momentum_trader_order_intensity=100,
    momentum_trader_order_size=0.01,
    momentum_trader_strategies=['RSI'],
    momentum_trader_strategy_args=[{'timeperiod': 7}],
    momentum_trader_indicator_thresholds=[(70,30)], 
    state_extraction_fn=momentum_trader_data_extraction,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=False,
        retain_log_files=True,
    ) as vega:
        results = scenario.run_iteration(
            vega=vega,
            pause_at_completion=False,
        )

    file_path = file_path = (
        pathlib.Path(__file__).parent.resolve() / "MomentumAgent.csv"
    )
    with open(file_path, "w") as f:
        csv_writer = csv.writer(f, delimiter=",")
        headers = ["Time Step"] + list(results[0].keys())
        csv_writer.writerow(headers)
        for step, result in enumerate(results):
            headers = list(result.keys())
            csv_writer.writerow([step] + [result[c] for c in headers])
