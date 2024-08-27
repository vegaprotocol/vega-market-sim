import vega_protos.protos as protos

from typing import List
from logging import getLogger
from vega_query.service.service_core import CoreService
from vega_query.service.service_trading_data import TradingDataService

logger = getLogger(__name__)


class MarketUtils:
    def __init__(self, core_service: CoreService, data_service: TradingDataService):
        self.__core = core_service
        self.__data = data_service

    def find_market(
        self, substrings: List[str], include_settled: bool = False
    ) -> protos.vega.markets.Market:
        markets = self.__data.list_markets(include_settled=include_settled)
        for market in markets:
            code = market.tradable_instrument.instrument.code
            match = True
            for substring in substrings:
                if substring not in code:
                    logger.debug(f"{substring} not found in market {code}")
                    match = False
                    break
            if match:
                return market
        raise Exception(f"Matching market not found.")

    def find_asset(self, substrings: List[str]) -> protos.vega.assets.Asset:
        instrument = self.find_market(
            substrings=substrings
        ).tradable_instrument.instrument
        if instrument.spot != protos.vega.markets.Spot():
            return self.find_quote_asset(substrings)
        if instrument.spot != protos.vega.markets.Future():
            return self.find_settlement_asset(substrings)
        if instrument.spot != protos.vega.markets.Perpetual():
            return self.find_settlement_asset(substrings)

    def find_base_asset(self, substrings: List[str]) -> protos.vega.assets.Asset:
        instrument = self.find_market(
            substrings=substrings
        ).tradable_instrument.instrument
        asset_id = None
        if instrument.spot != protos.vega.markets.Spot():
            return instrument.spot.base_asset
        if asset_id is not None:
            return self.__data.get_asset(asset_id)
        raise Exception("Market is not a spot market.")

    def find_quote_asset(self, substrings: List[str]) -> protos.vega.assets.Asset:
        instrument = self.find_market(
            substrings=substrings
        ).tradable_instrument.instrument
        asset_id = None
        if instrument.spot != protos.vega.markets.Spot():
            asset_id = instrument.spot.quote_asset
        if asset_id is not None:
            return self.__data.get_asset(asset_id)
        raise Exception("Market is not a spot market.")

    def find_settlement_asset(
        self,
        substrings: List[str],
        include_settled: bool = False,
    ) -> protos.vega.assets.Asset:
        instrument = self.find_market(
            substrings=substrings,
            include_settled=include_settled,
        ).tradable_instrument.instrument
        asset_id = None
        if instrument.future != protos.vega.markets.Future():
            asset_id = instrument.future.settlement_asset
        if instrument.perpetual != protos.vega.markets.Perpetual():
            asset_id = instrument.perpetual.settlement_asset
        if asset_id is not None:
            return self.__data.get_asset(asset_id)
        raise Exception("Market is not a future or perpetual market.")

    def find_size_decimals(self, substrings: List[str]) -> int:
        return self.find_market(substrings=substrings).position_decimal_places

    def find_price_decimals(self, substrings: List[str]) -> int:
        return self.find_market(substrings=substrings).decimal_places
