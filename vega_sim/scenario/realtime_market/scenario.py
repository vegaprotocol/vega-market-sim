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
from vega_sim.scenario.common.agents import (
    MarketManager,
    StateAgent,
)

logger = logging.getLogger(__name__)


class RealtimeMarket(Scenario):
    def __init__(
        self,
        market_decimal: int = 5,
        asset_decimal: int = 5,
        market_position_decimal: int = 2,
        market_name: str = None,
        asset_name: str = None,
        block_size: int = 1,
        block_length_seconds: int = 1,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, Dict[str, Agent]], Any]
        ] = None,
    ):
        super().__init__(state_extraction_fn=state_extraction_fn)
        self.market_decimal = market_decimal
        self.asset_decimal = asset_decimal
        self.market_position_decimal = market_position_decimal

        self.block_size = block_size
        self.block_length_seconds = block_length_seconds
        self.market_name = "ETH:USD" if market_name is None else market_name
        self.asset_name = "tDAI" if asset_name is None else asset_name

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: Optional[str],
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> List[StateAgent]:
        # Set up market name and settlement asset
        market_name = self.market_name + (f"_{tag}" if tag else "")
        asset_name = self.asset_name

        market_manager = MarketManager(
            wallet_name=MM_WALLET.name,
            wallet_pass=MM_WALLET.passphrase,
            terminate_wallet_name=TERMINATE_WALLET.name,
            terminate_wallet_pass=TERMINATE_WALLET.passphrase,
            asset_decimal=self.asset_decimal,
            market_decimal=self.market_decimal,
            market_position_decimal=self.market_position_decimal,
            market_name=market_name,
            asset_name=asset_name,
            tag=str(tag) if tag is not None else None,
        )

        agents = [
            market_manager,
        ]
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
        market_name="ETH",
        asset_name="USD",
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
