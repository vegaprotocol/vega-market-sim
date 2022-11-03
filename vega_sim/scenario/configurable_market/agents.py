from typing import Optional, Union

from collections import namedtuple

from vega_sim.api.market import MarketConfig
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.null_service import VegaServiceNull

WALLET_NAME = "research"
WALLET_PASS = "pass"

PartyConfig = namedtuple("PartyConfig", ["wallet_name", "wallet_pass", "key_name"])

PROPOSAL_PARTY = PartyConfig(WALLET_NAME, WALLET_PASS, "proposal_party")
TERMINATION_PARTY = PartyConfig(WALLET_NAME, WALLET_PASS, "termination_party")
MAKER_PARTY = PartyConfig(WALLET_NAME, WALLET_PASS, "maker_party")
AUCTION_PARTY_A = PartyConfig(WALLET_NAME, WALLET_PASS, "auction_party_a")
AUCTION_PARTY_B = PartyConfig(WALLET_NAME, WALLET_PASS, "auction_party_b")
SENSITIVE_PARTY_A = PartyConfig(WALLET_NAME, WALLET_PASS, "sensitive_party_a")
SENSITIVE_PARTY_B = PartyConfig(WALLET_NAME, WALLET_PASS, "sensitive_party_b")
SENSITIVE_PARTY_C = PartyConfig(WALLET_NAME, WALLET_PASS, "sensitive_party_c")
INFORMED_PARTY = PartyConfig(WALLET_NAME, WALLET_PASS, "informed_party")


class ConfigurableMarketManager(StateAgentWithWallet):
    def __init__(
        self,
        proposal_wallet_name: str,
        proposal_wallet_pass: str,
        termination_wallet_name: str,
        termination_wallet_pass: str,
        market_name: str,
        market_code: str,
        asset_name: str,
        asset_dp: int,
        proposal_key_name: Optional[str] = None,
        termination_key_name: Optional[str] = None,
        market_config: Optional[MarketConfig] = None,
        tag: Optional[str] = None,
        settlement_price: Optional[float] = None,
    ):

        self.wallet_name = proposal_wallet_name
        self.wallet_pass = proposal_wallet_pass
        self.key_name = proposal_key_name

        self.termination_wallet_name = termination_wallet_name
        self.termination_wallet_pass = termination_wallet_pass
        self.termination_key_name = termination_key_name

        self.market_name = market_name
        self.market_code = market_code

        self.asset_dp = asset_dp
        self.asset_name = asset_name

        self.initial_mint = 1e09

        self.market_config = (
            market_config if market_config is not None else MarketConfig()
        )

        self.tag = tag
        self.settlement_price = settlement_price

    def initialise(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        create_wallet: bool = True,
        mint_wallet: bool = True,
    ):

        super().initialise(vega=vega, create_wallet=create_wallet)
        self.vega.create_wallet(
            self.termination_wallet_name,
            self.termination_wallet_pass,
            self.termination_key_name,
        )

        self.vega.wait_for_total_catchup()
        self.vega.mint(
            self.wallet_name, asset="VOTE", amount=1e4, key_name=self.key_name
        )

        self.vega.wait_for_total_catchup()
        if mint_wallet:
            self.vega.create_asset(
                self.wallet_name,
                name=self.asset_name,
                symbol=self.asset_name,
                decimals=self.asset_dp,
                max_faucet_amount=5e10,
                key_name=self.key_name,
            )

        self.vega.wait_for_total_catchup()
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)

        self.vega.wait_for_total_catchup()
        if mint_wallet:
            self.vega.mint(
                self.wallet_name,
                asset=self.asset_id,
                amount=self.initial_mint,
                key_name=self.key_name,
            )

        # Add market information and asset information to market config
        self.market_config.set("instrument.name", self.market_name)
        self.market_config.set("instrument.code", self.market_code)
        self.market_config.set("instrument.future.settlement_asset", self.asset_id)
        self.market_config.set("instrument.future.quote_name", self.asset_name)
        self.market_config.set(
            "instrument.future.settlement_data_decimals", self.asset_dp
        )
        self.market_config.set(
            "instrument.future.terminating_key",
            self.vega.wallet.public_key(
                self.termination_wallet_name, self.termination_key_name
            ),
        )

        self.vega.wait_for_total_catchup()
        self.vega.create_market_from_config(
            proposal_wallet_name=self.wallet_name,
            proposal_key_name=self.key_name,
            market_config=self.market_config,
        )

        self.vega.wait_for_total_catchup()
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]

    def finalise(self):
        if self.settlement_price is not None:
            self.vega.settle_market(
                self.termination_wallet_name,
                self.settlement_price,
                self.market_id,
                self.termination_key_name,
            )
            self.vega.wait_for_total_catchup()
