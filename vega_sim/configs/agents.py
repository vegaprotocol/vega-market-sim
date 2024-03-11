from typing import Optional, Union, Dict, Iterable

from vega_sim.api.market import MarketConfig
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.null_service import VegaServiceNull

import vega_sim.proto as protos

from numpy.random import RandomState


class ConfigurableMarketManager(StateAgentWithWallet):
    def __init__(
        self,
        key_name: str,
        market_config: MarketConfig,
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
        self.is_future = self.market_config.instrument.future != None
        self.is_perpetual = self.market_config.instrument.perpetual != None

        self.oracle_prices = oracle_prices
        self.oracle_difference = oracle_difference
        self.oracle_submission = oracle_submission

        self.random_state = random_state if random_state is not None else RandomState()

    def initialise(
        self,
        vega: VegaServiceNull | VegaServiceNetwork,
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

        # Extract asset symbol from config
        if self.is_future:
            asset_symbol = self.market_config.instrument.future.quote_name
        if self.is_perpetual:
            asset_symbol = self.market_config.instrument.perpetual.quote_name

        # Check if asset exists and create it if not
        asset_id = self.vega.find_asset_id(
            symbol=asset_symbol,
            raise_on_missing=False,
        )
        if asset_id is None:
            self.vega.create_asset(
                key_name=self.key_name,
                wallet_name=self.wallet_name,
                symbol=asset_symbol,
                name=asset_symbol,
                decimals=18,
            )
            asset_id = self.vega.find_asset_id(
                symbol=asset_symbol,
                raise_on_missing=True,
            )

        # Replace the asset id in the market_config
        if self.is_future:
            self.market_config.instrument.future.settlement_asset = asset_id
            self.market_config.instrument.future.terminating_key = (
                self.vega.wallet.public_key(
                    wallet_name=self.wallet_name,
                    name=self.key_name,
                )
            )
        if self.is_perpetual:
            self.market_config.instrument.perpetual.settlement_asset = asset_id
            self.market_config.instrument.perpetual.settlement_key = (
                self.vega.wallet.public_key(
                    wallet_name=self.wallet_name,
                    name=self.key_name,
                )
            )

        # Propose the market
        self.vega.create_market_from_config(
            proposal_wallet_name=self.wallet_name,
            proposal_key_name=self.key_name,
            market_config=self.market_config,
            approve_proposal=True,
        )
        self.market_id = self.vega.find_market_id(
            name=self.market_config.instrument.name,
            raise_on_missing=True,
        )

    def step(self, vega_state):
        self.price = next(self.oracle_prices)
        # If not a perpetual no need to send data
        if not self.is_perpetual:
            return

        if self.random_state.rand() < self.oracle_submission:

            randomised_price = self.random_state.uniform(
                self.price * (1 - self.oracle_difference),
                self.price * (1 + self.oracle_difference),
            )
            self.vega.submit_settlement_data(
                settlement_key=self.key_name,
                wallet_name=self.wallet_name,
                settlement_price=randomised_price,
                market_id=self.market_id,
            )

    def finalise(self):
        self.vega.submit_termination_and_settlement_data(
            settlement_key=self.key_name,
            settlement_price=self.price,
            market_id=self.market_id,
            wallet_name=self.wallet_name,
        )
        self.vega.wait_for_total_catchup()
