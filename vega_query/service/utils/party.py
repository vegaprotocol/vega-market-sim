import vega_protos.protos as protos

from typing import List, Optional
from logging import getLogger
from collections import defaultdict
from vega_query.service.service_core import CoreService
from vega_query.service.service_trading_data import TradingDataService

import pandas as pd

from vega_query.utils import timestamp_to_datetime

logger = getLogger(__name__)


class PartyUtils:
    def __init__(self, core_service: CoreService, data_service: TradingDataService):
        self.__core = core_service
        self.__data = data_service

    def historic_positions(
        self, party_id: str, market_id: Optional[str] = None
    ) -> pd.DataFrame:
        """Returns the historic positions for the specified party.

        User can optionally filter by market and daterange. Note the end
        timestamp must be the current time.
        """

        vega_time = self.__data.get_vega_time()

        positions = {
            position.market_id: position.open_volume
            for position in self.__data.list_positions(
                party_id=party_id, market_id=market_id
            )
        }
        trades = self.__data.list_trades(
            party_ids=[party_id],
            market_ids=[market_id] if market_id is not None else None,
            date_range_end_timestamp=int(vega_time),
            date_range_start_timestamp=0,
        )
        data = defaultdict(lambda: defaultdict(int))
        for trade in trades:
            position_after_trade = positions.get(trade.market_id, 0)
            data[timestamp_to_datetime(trade.timestamp)][
                trade.market_id
            ] = position_after_trade
            match party_id:
                case trade.buyer:
                    positions[trade.market_id] -= trade.size
                case trade.seller:
                    positions[trade.market_id] += trade.size
                case _:
                    raise Exception("Trade not associated with party.")
        return pd.DataFrame.from_dict(data, orient="index").sort_index().ffill()

    def historic_balances(
        self,
        party_id: str,
        asset_id: str,
        market_id: Optional[str] = None,
        account_types: Optional[List[protos.vega.vega.AccountType.Value]] = None,
        date_range_start_timestamp: Optional[int] = None,
        date_range_end_timestamp: Optional[int] = None,
    ) -> pd.DataFrame:
        """Returns the historic balances for the specified party.

        User can optionally filter by market, asset, account types and
        date range.
        """
        vega_time = self.__data.get_vega_time()
        aggregated_balances = self.__data.list_balance_changes(
            asset_id=asset_id,
            party_ids=[party_id],
            market_ids=[market_id] if market_id is not None else None,
            account_types=account_types,
            date_range_start_timestamp=(
                date_range_start_timestamp
                if date_range_start_timestamp is not None
                else int(vega_time - 6 * 60 * 60 * 1e9)
            ),
            date_range_end_timestamp=(
                date_range_end_timestamp
                if date_range_end_timestamp is not None
                else int(vega_time)
            ),
        )
        data = defaultdict(lambda: dict())
        for aggregated_balance in aggregated_balances:
            account_key = "_".join(
                protos.vega.vega.AccountType.Name(
                    aggregated_balance.account_type
                ).split("_")[2:]
            )
            if aggregated_balance.market_id is not "":
                account_key += f" | {aggregated_balance.market_id[:7]}"
            data[timestamp_to_datetime(aggregated_balance.timestamp)][account_key] = (
                int(aggregated_balance.balance)
            )

        df = pd.DataFrame.from_dict(data, orient="index").sort_index().ffill()
        df["total"] = df.sum(axis=1)
        return df
