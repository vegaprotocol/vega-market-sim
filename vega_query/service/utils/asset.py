import vega_protos.protos as protos

from typing import List
from logging import getLogger
from vega_query.service.service_core import CoreService
from vega_query.service.service_trading_data import TradingDataService

logger = getLogger(__name__)


class AssetUtils:
    def __init__(self, core_service: CoreService, data_service: TradingDataService):
        self.__core = core_service
        self.__data = data_service

    def find_asset(
        self, substrings: List[str], include_disabled: bool = False
    ) -> protos.vega.assets.Asset:
        assets = self.__data.list_assets()
        for asset in assets:
            if (not include_disabled) and (
                asset.status != protos.vega.assets.Asset.Status.STATUS_ENABLED
            ):
                continue
            symbol = asset.details.symbol
            match = True
            for substring in substrings:
                if substring not in asset.details.symbol:
                    logger.debug(f"{substring} not found in asset {symbol}")
                    match = False
                    break
            if match:
                return asset
        raise Exception(f"Matching asset not found.")
