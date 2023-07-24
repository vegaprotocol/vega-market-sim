from vega_sim.environment.agent import Agent, StateAgentWithWallet
from vega_sim.scenario.common.agents import MarketHistoryData, ResourceData
from typing import List, Callable, Optional, Dict
import pandas as pd
import itertools
import os
import os.path
import json

import vega_sim.proto.vega as vega_protos

DEFAULT_PATH = "./run_logs"
DEFAULT_RUN_NAME = "latest"

AGENTS_FILE_NAME = "agents.csv"
DATA_FILE_NAME = "market_data.csv"
ORDER_BOOK_FILE_NAME = "depth_data.csv"
TRADES_FILE_NAME = "trades.csv"
ACCOUNTS_FILE_NAME = "accounts.csv"
FUZZING_FILE_NAME = "additional_data.csv"
RESOURCES_FILE_NAME = "resources.csv"
ASSETS_FILE_NAME = "assets.csv"
MARKET_CHAIN_FILE_NAME = "market_chain.json"


def resource_data_to_row(data: ResourceData):
    return [
        {
            "time": data.at_time,
            "vega_cpu_per": data.vega_cpu_per,
            "vega_mem_rss": data.vega_mem_rss,
            "vega_mem_vms": data.vega_mem_vms,
            "datanode_cpu_per": data.datanode_cpu_per,
            "datanode_mem_rss": data.datanode_mem_rss,
            "datanode_mem_vms": data.datanode_mem_vms,
        }
    ]


def history_data_to_row(data: MarketHistoryData) -> List[pd.Series]:
    results = []
    for market_id in data.market_info.keys():
        market_data = data.market_data[market_id]

        results.append(
            {
                "time": data.at_time,
                "mark_price": market_data.mark_price,
                "market_id": market_id,
                "mark_price": market_data.mark_price,
                "mid_price": market_data.mid_price,
                "open_interest": market_data.open_interest,
                "best_bid": market_data.best_bid_price,
                "best_offer": market_data.best_offer_price,
                "best_bid_volume": market_data.best_bid_volume,
                "best_offer_volume": market_data.best_offer_volume,
                "market_state": market_data.market_state,
                "market_trading_mode": market_data.market_trading_mode,
                "target_stake": market_data.target_stake,
                "supplied_stake": market_data.supplied_stake,
                "price_monitoring_bounds": [
                    ((bound.min_valid_price, bound.max_valid_price))
                    for bound in market_data.price_monitoring_bounds
                ],
                "indicative_price": market_data.indicative_price,
                "trigger": market_data.trigger,
                "extension_trigger": market_data.extension_trigger,
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
    results = list(
        itertools.chain.from_iterable(
            [data_to_row_fn(data=step_data) for step_data in market_history_data],
        )
    )
    result_df = pd.DataFrame.from_records(
        results,
        index="time" if len(results) > 0 else None,
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


def resources_standard_output(
    resource_data: List[ResourceData],
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
            RESOURCES_FILE_NAME: resource_data_to_row,
        }
    )
    for file_name, data_fn in data_fns.items():
        _market_data_standard_output(
            market_history_data=resource_data,
            file_name=file_name,
            output_path=full_path,
            data_to_row_fn=data_fn,
        )


def agents_standard_output(
    agents: Dict[str, Agent],
    run_name: str = DEFAULT_RUN_NAME,
    output_path: str = DEFAULT_PATH,
):
    results = {
        key: [] for key in ["agent_name", "agent_type", "agent_tag", "agent_key"]
    }
    for name, agent in agents.items():
        results["agent_name"].append(name)
        results["agent_tag"].append(agent.tag)
        results["agent_type"].append(type(agent).__name__)
        if isinstance(agent, StateAgentWithWallet):
            results["agent_key"].append(agent._public_key)
        else:
            results["agent_key"].append(None)

    full_path = os.path.join(output_path, run_name)
    os.makedirs(full_path, exist_ok=True)
    pd.DataFrame.from_dict(results).set_index(
        "agent_name",
        drop=True,
    ).to_csv(os.path.join(full_path, AGENTS_FILE_NAME))


def assets_standard_output(
    assets: List[vega_protos.assets.Asset],
    run_name: str = DEFAULT_RUN_NAME,
    output_path: str = DEFAULT_PATH,
):
    results = {
        key: []
        for key in [
            "id",
            "name",
            "symbol",
            "decimals",
            "quantum",
            "max_faucet_amount_mint",
            "status",
        ]
    }
    for asset in assets:
        results["id"].append(asset.id)
        results["name"].append(asset.details.name)
        results["symbol"].append(asset.details.symbol)
        results["decimals"].append(asset.details.decimals)
        results["quantum"].append(asset.details.quantum)
        results["max_faucet_amount_mint"].append(
            asset.details.builtin_asset.max_faucet_amount_mint
        )
        results["status"].append(asset.status)

    full_path = os.path.join(output_path, run_name)
    os.makedirs(full_path, exist_ok=True)
    pd.DataFrame.from_dict(results).set_index("id", drop=True).to_csv(
        os.path.join(full_path, ASSETS_FILE_NAME)
    )


def market_chain_standard_output(
    market_history_data: List[MarketHistoryData],
    run_name: str = DEFAULT_RUN_NAME,
    output_path: str = DEFAULT_PATH,
):
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    full_path = os.path.join(output_path, run_name)

    market_chains: Dict[str, List[str]] = {}
    for history_data in market_history_data:
        for market_id, market_info in history_data.market_info.items():
            if not market_info.parent_market_id:
                market_chains.setdefault(market_id, [market_id])
            else:
                for _, market_chain in market_chains.items():
                    if market_chain[-1] == market_info.parent_market_id:
                        market_chain.append(market_id)

    os.makedirs(output_path, exist_ok=True)

    with open(os.path.join(full_path, MARKET_CHAIN_FILE_NAME), "w") as f:
        json.dump(market_chains, f, indent=4)


def load_agents_df(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> pd.DataFrame:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    return pd.read_csv(
        os.path.join(output_path, run_name, AGENTS_FILE_NAME), index_col="agent_name"
    )


def load_assets_df(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> pd.DataFrame:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    return pd.read_csv(
        os.path.join(output_path, run_name, ASSETS_FILE_NAME), index_col="id"
    )


def load_market_data_df(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> pd.DataFrame:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    df = pd.read_csv(os.path.join(output_path, run_name, DATA_FILE_NAME))
    if not df.empty:
        df["time"] = pd.to_datetime(df.time)
        df = df.set_index("time")
    return df


def load_order_book_df(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> pd.DataFrame:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    depth_df = pd.read_csv(os.path.join(output_path, run_name, ORDER_BOOK_FILE_NAME))
    if not depth_df.empty:
        depth_df["time"] = pd.to_datetime(depth_df.time)
        depth_df = depth_df[depth_df["time"] != depth_df["time"].min()].set_index(
            "time"
        )
    return depth_df


def load_trades_df(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> pd.DataFrame:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    df = pd.read_csv(os.path.join(output_path, run_name, TRADES_FILE_NAME))
    if not df.empty:
        df["time"] = pd.to_datetime(df.time)
        df = df.set_index("time")
    return df


def load_accounts_df(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> pd.DataFrame:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    df = pd.read_csv(os.path.join(output_path, run_name, ACCOUNTS_FILE_NAME))
    if not df.empty:
        df["time"] = pd.to_datetime(df.time)
        df = df.set_index("time")
    return df


def load_fuzzing_df(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> pd.DataFrame:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    df = pd.read_csv(os.path.join(output_path, run_name, FUZZING_FILE_NAME))
    if not df.empty:
        df["time"] = pd.to_datetime(df.time)
        df = df.set_index("time")
    return df


def load_resource_df(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> pd.DataFrame:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    df = pd.read_csv(os.path.join(output_path, run_name, RESOURCES_FILE_NAME))
    if not df.empty:
        df["time"] = pd.to_datetime(df.time)
        df = df.set_index("time")
    return df


def load_market_chain(
    run_name: Optional[str] = None,
    output_path: str = DEFAULT_PATH,
) -> Dict[str, List[str]]:
    run_name = run_name if run_name is not None else DEFAULT_RUN_NAME
    file_path = os.path.join(output_path, run_name, MARKET_CHAIN_FILE_NAME)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            market_chain = json.load(fp=f)
    else:
        market_chain = {}
    return market_chain
