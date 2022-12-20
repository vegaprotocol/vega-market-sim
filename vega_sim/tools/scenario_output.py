from vega_sim.scenario.common.agents import MarketHistoryData
from typing import List, Callable
import pandas as pd
import itertools
import os

DEFAULT_FILE_NAME = "market_data.csv"
DEFAULT_PATH = "./run_logs"


def history_data_to_row(data: MarketHistoryData) -> List[pd.Series]:
    results = []
    for market_id, _ in data.market_info.items():
        market_data = data.market_data[market_id]

        results.append(
            {
                "time": data.at_time,
                "market_id": market_id,
                "open_interest": market_data.open_interest,
                "best_bid": market_data.best_bid_price,
                "best_offer": market_data.best_offer_price,
                "best_bid_volume": market_data.best_bid_volume,
                "best_offer_volume": market_data.best_offer_volume,
                "market_state": market_data.market_state,
                "market_trading_mode": market_data.market_trading_mode,
                "target_stake": market_data.target_stake,
                "supplied_stake": market_data.supplied_stake,
            },
        )
    return results


def market_data_standard_output(
    market_history_data: List[MarketHistoryData],
    file_name: str = DEFAULT_FILE_NAME,
    output_path: str = DEFAULT_PATH,
    data_to_row_fn: Callable[[MarketHistoryData], pd.Series] = history_data_to_row,
):
    result_df = pd.DataFrame.from_records(
        itertools.chain.from_iterable(
            [data_to_row_fn(data=step_data) for step_data in market_history_data],
        ),
        index="time",
    )
    os.makedirs(output_path, exist_ok=True)
    result_df.to_csv(path_or_buf=output_path + "/" + file_name)
