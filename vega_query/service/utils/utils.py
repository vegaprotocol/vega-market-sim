from vega_query.service.utils.asset import AssetUtils
from vega_query.service.utils.party import PartyUtils
from vega_query.service.utils.market import MarketUtils


class Utils:
    def __init__(self, core_service, data_service):
        self.__asset = AssetUtils(core_service, data_service)
        self.__party = PartyUtils(core_service, data_service)
        self.__market = MarketUtils(core_service, data_service)

    @property
    def asset(self):
        return self.__asset

    @property
    def party(self):
        return self.__party

    @property
    def market(self):
        return self.__market
