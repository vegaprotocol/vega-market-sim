import argparse
import datetime
import logging
import numpy as np
from typing import Any, Callable, List, Optional, Dict
from vega_sim.environment.agent import Agent
from vega_sim.scenario.scenario import Scenario
from vega_sim.environment.environment import RealtimeMarketEnvironment
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.ideal_market_maker_v2.agents import (
    MM_WALLET,
    TERMINATE_WALLET,
)
from vega_sim.scenario.common.agents import MarketManager, StateAgent, KeyFunder

logger = logging.getLogger(__name__)


class RealtimeMarket(Scenario):
    def __init__(
        self,
        market_decimal: int = 5,
        asset_decimal: int = 5,
        market_position_decimal: int = 2,
        market_names: Optional[list[str]] = None,
        asset_names: Optional[list[str]] = None,
        block_size: int = 1,
        block_length_seconds: int = 1,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, Dict[str, Agent]], Any]
        ] = None,
        pubkeys_to_faucet: Optional[list[str]] = None,
        amount_to_faucet: float = 100_000,
    ):
        super().__init__(state_extraction_fn=state_extraction_fn)
        if len(market_names) != len(asset_names):
            raise Exception("Must provide equal numbers of markets and assets")
        self.market_decimal = market_decimal
        self.asset_decimal = asset_decimal
        self.market_position_decimal = market_position_decimal

        self.block_size = block_size
        self.block_length_seconds = block_length_seconds
        self.market_names = ["ETH:USD"] if market_names is None else market_names
        self.asset_names = ["tDAI"] if asset_names is None else asset_names
        self.pubkeys_to_faucet = (
            pubkeys_to_faucet if pubkeys_to_faucet is not None else []
        )
        self.amount_to_faucet = amount_to_faucet

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: Optional[str],
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> List[StateAgent]:
        # Set up market name and settlement asset

        agents = []
        for i, market_name in enumerate(self.market_names):
            agents.append(
                MarketManager(
                    wallet_name=MM_WALLET.name,
                    wallet_pass=MM_WALLET.passphrase,
                    terminate_wallet_name=TERMINATE_WALLET.name,
                    terminate_wallet_pass=TERMINATE_WALLET.passphrase,
                    asset_decimal=self.asset_decimal,
                    market_decimal=self.market_decimal,
                    market_position_decimal=self.market_position_decimal,
                    market_name=market_name,
                    asset_name=self.asset_names[i],
                    tag=market_name,
                )
            )

        for asset in self.asset_names:
            agents.append(
                KeyFunder(
                    self.pubkeys_to_faucet,
                    asset_to_fund=asset,
                    amount_to_fund=self.amount_to_faucet,
                    tag=asset,
                )
            )

        return {agent.name(): agent for agent in agents}

    def configure_environment(
        self,
        vega: VegaServiceNull,
        **kwargs,
    ) -> RealtimeMarketEnvironment:
        return RealtimeMarketEnvironment(
            agents=list(self.agents.values()),
            random_agent_ordering=True,
            transactions_per_block=self.block_size,
            vega_service=vega,
            block_length_seconds=self.block_length_seconds,
            pause_every_n_steps=None,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

    scenario = RealtimeMarket(
        market_names=[
            "ETH",
        ],
        asset_names=["USD"],
        pubkeys_to_faucet=[
            "520C6B790113062BA29B6E689694766E3A0DBCBCC4D79E3A43E3F9D21FC3EC7B",
            "6001C9B8CE0B8577E2D407EC1584FF6E2CCCF84E36404D8274B9DA1B86D31022",
        ],
        market_decimal=2,
        asset_decimal=4,
        market_position_decimal=4,
    )

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=True,
        use_full_vega_wallet=False,
        retain_log_files=True,
        launch_graphql=False,
        seconds_per_block=1,  # Heuristic
    ) as vega:
        scenario.run_iteration(
            vega=vega,
            pause_at_completion=True,
        )
