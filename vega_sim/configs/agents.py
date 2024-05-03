import re
import datetime

from typing import Optional, Union, Dict, Iterable

from vega_sim.api.market import MarketConfig, SpotMarketConfig
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.null_service import VegaServiceNull

import vega_sim.proto as protos

from numpy.random import RandomState


class ConfigurableMarketManager(StateAgentWithWallet):

    NAME_BASE = "ConfigurableMarketManager"

    def __init__(
        self,
        key_name: str,
        market_config: Union[MarketConfig, SpotMarketConfig],
        oracle_prices: Iterable,
        oracle_difference: float = 0.001,
        oracle_submission: float = 0.1,
        random_state: Optional[RandomState] = None,
        wallet_name: Optional[str] = None,
        tag: Optional[str] = None,
    ):
        super().__init__(
            wallet_name=wallet_name,
            key_name=key_name,
            tag=tag,
        )
        self.market_config = market_config
        self.is_spot = self.market_config.instrument.spot != None
        self.is_future = self.market_config.instrument.future != None
        self.is_perpetual = self.market_config.instrument.perpetual != None

        self.oracle_prices = oracle_prices
        self.oracle_difference = oracle_difference
        self.oracle_submission = oracle_submission

        self.data_oracles = {}
        self.data_oracles.update(self.__extract_settlement_data_oracle())
        self.data_oracles.update(self.__extract_mark_price_oracles())
        self.termination_oracle = self.__extract_termination_data_oracle()

        self.random_state = random_state if random_state is not None else RandomState()

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_key: bool = True,
        mint_key: bool = True,
    ):
        super().initialise(vega, create_key, mint_key)

        # Mint the governance token
        if mint_key:
            self.vega.mint(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                asset=self.vega.find_asset_id(symbol="VOTE", raise_on_missing=True),
                amount=1,
            )

        # Extract asset symbol from config then find or create the relevant assets
        if self.is_spot:
            base_asset_symbol, quote_asset_symbol = re.split(
                r"[^a-zA-Z]+", self.market_config.instrument.code
            )[:2]
            base_asset_id = self.__find_or_create_asset(base_asset_symbol)
            quote_asset_id = self.__find_or_create_asset(quote_asset_symbol)
        if self.is_future:
            settlement_asset_symbol = self.market_config.instrument.future.quote_name
            settlement_asset_id = self.__find_or_create_asset(settlement_asset_symbol)
        if self.is_perpetual:
            settlement_asset_symbol = self.market_config.instrument.perpetual.quote_name
            settlement_asset_id = self.__find_or_create_asset(settlement_asset_symbol)

        # Replace the asset ids in the market_config
        if self.is_future:
            self.market_config.instrument.future.settlement_asset = settlement_asset_id
        if self.is_perpetual:
            self.market_config.instrument.perpetual.settlement_asset = (
                settlement_asset_id
            )
        if self.is_spot:
            self.market_config.instrument.spot.base_asset = base_asset_id
            self.market_config.instrument.spot.quote_asset = quote_asset_id

        # Propose the market
        current_timestamp = self.vega.get_blockchain_time(in_seconds=True)
        closing_datetime = datetime.datetime.fromtimestamp(current_timestamp + 10)
        enactment_datetime = datetime.datetime.fromtimestamp(current_timestamp + 600)
        self.vega.create_market_from_config(
            proposal_wallet_name=self.wallet_name,
            proposal_key_name=self.key_name,
            market_config=self.market_config,
            vote_closing_time=closing_datetime,
            vote_enactment_time=enactment_datetime,
            approve_proposal=True,
            forward_time_to_closing=True,
            forward_time_to_enactment=False,
        )
        self.vega.wait_for_total_catchup()
        self.market_id = self.vega.find_market_id(
            name=self.market_config.instrument.name,
            raise_on_missing=True,
        )

    def step(self, vega_state):
        self.price = next(self.oracle_prices)
        # If not a perpetual no need to send data
        if not self.is_perpetual:
            return

        randomised_price = self.random_state.uniform(
            self.price * (1 - self.oracle_difference),
            self.price * (1 + self.oracle_difference),
        )
        for name, number_decimal_places in self.data_oracles.items():
            if self.random_state.rand() > self.oracle_submission:
                continue
            self.vega.submit_oracle_data(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                name=name,
                type=protos.vega.data.v1.spec.PropertyKey.Type.TYPE_INTEGER,
                value=randomised_price,
                decimals=number_decimal_places,
            )

    def finalise(self):
        if self.is_future:
            self.vega.submit_oracle_data(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                name=self.termination_oracle,
                type=protos.vega.data.v1.spec.PropertyKey.Type.TYPE_BOOLEAN,
                value=True,
            )
        if self.is_future or self.is_perpetual:
            for name, number_decimal_places in self.data_oracles.items():
                self.vega.submit_oracle_data(
                    key_name=self.key_name,
                    wallet_name=self.wallet_name,
                    name=name,
                    type=protos.vega.data.v1.spec.PropertyKey.Type.TYPE_INTEGER,
                    value=self.price,
                    decimals=number_decimal_places,
                )

    def __find_or_create_asset(self, symbol: str):
        # Check if asset exists and create it if not
        asset_id = self.vega.find_asset_id(
            symbol=symbol,
            raise_on_missing=False,
        )
        if asset_id is None:
            self.vega.create_asset(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                symbol=symbol,
                name=symbol,
                decimals=18,
            )
            asset_id = self.vega.find_asset_id(
                symbol=symbol,
                raise_on_missing=True,
            )
        return asset_id

    def __extract_termination_data_oracle(self):
        if self.is_spot:
            return None
        if self.is_perpetual:
            return None
        if self.is_future:
            oracle = (
                self.market_config.instrument.future.data_source_spec_for_trading_termination
            )
        if oracle.external is None:
            return
        if oracle.external.oracle is not None:
            filter = oracle.external.oracle.filters[0]
        if oracle.external.eth_oracle is not None:
            filter = oracle.external.eth_oracle.filters[0]
        return filter["key"]["name"]

    def __extract_settlement_data_oracle(self):
        if self.is_spot:
            return {}
        if self.is_future:
            oracle = (
                self.market_config.instrument.future.data_source_spec_for_settlement_data
            )
        if self.is_perpetual:
            oracle = (
                self.market_config.instrument.perpetual.data_source_spec_for_settlement_data
            )
        if oracle.external is None:
            return
        if oracle.external.oracle is not None:
            filters = oracle.external.oracle
        if oracle.external.eth_oracle is not None:
            filters = oracle.external.eth_oracle
        for filter in filters.filters:
            number_decimal_places = filter["key"].get("number_decimal_places", None)
            if number_decimal_places is not None:
                return {filter["key"]["name"]: int(number_decimal_places)}

    def __extract_mark_price_oracles(self):
        if self.market_config.is_spot:
            return {}
        if self.market_config.mark_price_configuration is None:
            return {}
        if self.market_config.mark_price_configuration.data_sources_spec is None:
            return {}
        oracles = {}
        for oracle in self.market_config.mark_price_configuration.data_sources_spec:
            if oracle.external is None:
                continue
            if oracle.external.oracle is not None:
                filter = oracle.external.oracle.filters[0]
            if oracle.external.eth_oracle is not None:
                filter = oracle.external.eth_oracle.filters[0]
            oracles[filter["key"]["name"]] = int(filter["key"]["number_decimal_places"])
        return oracles
