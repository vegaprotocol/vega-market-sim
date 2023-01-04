from vega_sim.scenario.common.agents import MarketHistoryData
from typing import List, Callable, Optional, Dict
import pandas as pd
import itertools
import os
import os.path

DEFAULT_PATH = "./run_logs"
DEFAULT_RUN_NAME = "latest"

DATA_FILE_NAME = "market_data.csv"
ORDER_BOOK_FILE_NAME = "depth_data.csv"
TRADES_FILE_NAME = "trades.csv"
ACCOUNTS_FILE_NAME = "accounts.csv"


def history_data_to_row(data: MarketHistoryData) -> List[pd.Series]:
    results = []
    for market_id in data.market_info.keys():
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


def history_data_to_order_book_rows(data: MarketHistoryData) -> List[pd.Series]:
    results = []
    for market_id, depth in data.market_depth.items():
        for side, side_vals in [("BID", depth.buys), ("ASK", depth.sells)]:
            for i, level_data in enumerate(side_vals):
                results.append(
                    {
                        "time": data.at_time,
                        "side": side,
                        "price": level_data.price,
                        "volume": level_data.volume,
                        "level": i,
                        "market_id": market_id,
                    }
                )
    return results


def history_data_to_trade_rows(data: MarketHistoryData) -> List[pd.Series]:
    results = []
    for market_id, trades in data.trades.items():
        for trade in trades:
            results.append(
                {
                    "time": trade.timestamp,
                    "seen_at": data.at_time,
                    "id": trade.id,
                    "price": trade.price,
                    "size": trade.size,
                    "buyer": trade.buyer,
                    "seller": trade.seller,
                    "aggressor": trade.aggressor,
                    "buy_order": trade.buy_order,
                    "sell_order": trade.sell_order,
                    "market_id": market_id,
                    "trade_type": trade.trade_type,
                    "buyer_fee_infrastructure": trade.buyer_fee.infrastructure_fee,
                    "buyer_fee_liquidity": trade.buyer_fee.liquidity_fee,
                    "buyer_fee_maker": trade.buyer_fee.maker_fee,
                    "seller_fee_infrastructure": trade.seller_fee.infrastructure_fee,
                    "seller_fee_liquidity": trade.seller_fee.liquidity_fee,
                    "seller_fee_maker": trade.seller_fee.maker_fee,
                    "buyer_auction_batch": trade.buyer_auction_batch,
                    "seller_auction_batch": trade.seller_auction_batch,
                }
            )
    return results


def history_data_to_account_rows(data: MarketHistoryData) -> List[pd.Series]:
    results = []
    for account in data.accounts:
        results.append(
            {
                "time": data.at_time,
                "party_id": account.owner,
                "balance": account.balance,
                "market_id": account.market_id,
                "asset": account.asset,
                "type": account.type,
            }
        )
    return results


def _market_data_standard_output(
    market_history_data: List[MarketHistoryData],
    file_name: str,
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

    result_df.to_csv(path_or_buf=os.path.join(output_path, file_name))


def market_data_standard_output(
    market_history_data: List[MarketHistoryData],
    run_name: str = DEFAULT_RUN_NAME,
    output_path: str = DEFAULT_PATH,
    custom_output_fns: Optional[
        Dict[str, List[Callable[[MarketHistoryData], pd.Series]]]
    ] = None,
):
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    full_path = os.path.join(output_path, run_name)
    data_fns = (
        custom_output_fns
        if custom_output_fns is not None
        else {
            DATA_FILE_NAME: history_data_to_row,
            ORDER_BOOK_FILE_NAME: history_data_to_order_book_rows,
            TRADES_FILE_NAME: history_data_to_trade_rows,
            ACCOUNTS_FILE_NAME: history_data_to_account_rows,
        }
    )
    for file_name, data_fn in data_fns.items():
        _market_data_standard_output(
            market_history_data=market_history_data,
            file_name=file_name,
            output_path=full_path,
            data_to_row_fn=data_fn,
        )


def load_market_data_df(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> pd.DataFrame:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    df = pd.read_csv(os.path.join(output_path, run_name, DATA_FILE_NAME))
    df["time"] = pd.to_datetime(df.time * 1e9)
    return df.set_index("time")


def load_order_book_df(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> pd.DataFrame:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    depth_df = pd.read_csv(os.path.join(output_path, run_name, ORDER_BOOK_FILE_NAME))
    depth_df["time"] = pd.to_datetime(depth_df.time * 1e9)
    return depth_df[depth_df["time"] != depth_df["time"].min()].set_index("time")


def load_trades_df(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> pd.DataFrame:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    df = pd.read_csv(os.path.join(output_path, run_name, TRADES_FILE_NAME))
    df["time"] = pd.to_datetime(df.time)
    return df.set_index("time")


def load_accounts_df(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> pd.DataFrame:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    df = pd.read_csv(os.path.join(output_path, run_name, ACCOUNTS_FILE_NAME))
    df["time"] = pd.to_datetime(df.time * 1e9)
    return df.set_index("time")
