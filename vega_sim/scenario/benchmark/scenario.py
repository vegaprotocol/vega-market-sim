import numpy as np
from typing import Optional, Dict, Any

from vega_sim.api.market import MarketConfig
from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.common.utils.price_process import random_walk
from vega_sim.scenario.constants import Network
from vega_sim.null_service import VegaServiceNull
from vega_sim.environment.environment import (
    MarketEnvironmentWithState,
    NetworkEnvironment,
)

from vega_sim.configs.agents import ConfigurableMarketManager
from vega_sim.scenario.common.agents import (
    StateAgent,
    NetworkParameterManager,
    UncrossAuctionAgent,
    ExponentialShapedMarketMaker,
    MarketOrderTrader,
    LimitOrderTrader,
)
from vega_sim.scenario.fuzzed_markets.agents import (
    RiskyMarketOrderTrader,
)


def _create_price_process(
    random_state: np.random.RandomState,
    num_steps,
    decimal_places,
    initial_price,
    price_sigma,
):
    price_process = [initial_price]

    while len(price_process) < num_steps + 1:
        price_process = np.concatenate(
            (
                price_process,
                random_walk(
                    num_steps=random_state.randint(
                        int(0.05 * num_steps), int(0.20 * num_steps)
                    ),
                    sigma=price_sigma,
                    starting_price=price_process[-1],
                    decimal_precision=decimal_places,
                ),
            )
        )
        price_process = np.concatenate(
            (
                price_process,
                random_walk(
                    num_steps=random_state.randint(
                        int(0.05 * num_steps), int(0.10 * num_steps)
                    ),
                    sigma=price_sigma,
                    drift=random_state.uniform(-price_sigma / 10, price_sigma / 10),
                    starting_price=price_process[-1],
                    decimal_precision=decimal_places,
                ),
            )
        )
    return price_process


class BenchmarkScenario(Scenario):
    def __init__(
        self,
        market_config: MarketConfig,
        initial_price: int,
        annualised_volatility: float = 1.5,
        notional_trade_volume: int = 100,
        num_steps: int = 60 * 24 * 30 * 3,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        step_length_seconds: Optional[float] = None,
        initial_network_parameters: Dict[str, Any] = None,
        output: bool = True,
    ):
        super().__init__()

        self.num_steps = num_steps
        self.step_length_seconds = (
            step_length_seconds
            if step_length_seconds is not None
            else block_length_seconds
        )
        self.block_length_seconds = block_length_seconds
        self.transactions_per_block = transactions_per_block

        self.output = output
        self.market_config = market_config

        self.initial_price = initial_price
        self.annualised_volatility = annualised_volatility
        self.notional_trade_volume = notional_trade_volume

        self.initial_network_parameters = (
            initial_network_parameters if initial_network_parameters is not None else {}
        )

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: str,
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> Dict[str, StateAgent]:
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

        market_name = self.market_config.instrument.name
        if self.market_config.is_future():
            asset_name = self.market_config.instrument.future.quote_name
            asset_dp = self.market_config.instrument.future.number_decimal_places
        if self.market_config.is_perp():
            asset_name = self.market_config.instrument.perpetual.quote_name
            asset_dp = self.market_config.instrument.perpetual.number_decimal_places

        # Create fuzzed price process
        price_process = _create_price_process(
            random_state=self.random_state,
            num_steps=self.num_steps,
            decimal_places=int(int(self.market_config.decimal_places)),
            initial_price=self.initial_price,
            price_sigma=self.annualised_volatility
            * np.sqrt(self.step_length_seconds / (365.25 * 24 * 60 * 60))
            * self.initial_price,
        )

        self.agents = []
        self.agents.append(
            NetworkParameterManager(
                wallet_name="NETWORK_PARAMETER_MANAGER",
                key_name="network_parameter_manager",
                network_parameters=self.initial_network_parameters,
            )
        )
        self.agents.append(
            ConfigurableMarketManager(
                wallet_name="MARKET_MANAGER",
                key_name="market_manager",
                market_config=self.market_config,
                oracle_prices=iter(price_process),
                oracle_submission=0.1,
                oracle_difference=0.001,
                tag=f"{self.market_config.instrument.code}",
                random_state=self.random_state,
            ),
        )

        self.agents.append(
            ExponentialShapedMarketMaker(
                wallet_name="MARKET_MAKERS",
                key_name=f"MARKET_{self.market_config.instrument.code}",
                price_process_generator=iter(price_process),
                initial_asset_mint=1e9,
                market_name=market_name,
                asset_name=asset_name,
                commitment_amount=1e6,
                market_decimal_places=int(self.market_config.decimal_places),
                asset_decimal_places=asset_dp,
                num_steps=self.num_steps,
                kappa=2.4,
                tick_spacing=10**-self.market_config.decimal_places
                * self.market_config.tick_size,
                num_levels=10,
                market_kappa=1000,
                state_update_freq=10,
                tag=f"MARKET_{self.market_config.instrument.code}",
            )
        )

        self.agents.extend(
            [
                UncrossAuctionAgent(
                    wallet_name="AUCTION_TRADERS",
                    key_name=f"MARKET_{self.market_config.instrument.code}_{side}",
                    side=side,
                    initial_asset_mint=1e8,
                    price_process=iter(price_process),
                    market_name=market_name,
                    asset_name=asset_name,
                    uncrossing_size=100,
                    tag=(
                        f"MARKET_{self.market_config.instrument.code}_AGENT_{str(i_agent).zfill(3)}"
                    ),
                    leave_opening_auction_prob=1.0,
                )
                for i_agent, side in enumerate(["SIDE_BUY", "SIDE_SELL"])
            ]
        )
        self.agents.extend(
            [
                MarketOrderTrader(
                    wallet_name="RANDOM_TRADERS",
                    key_name=f"MARKET_{self.market_config.instrument.code}_AGENT_{str(i_agent).zfill(3)}",
                    market_name=market_name,
                    asset_name=asset_name,
                    buy_intensity=100,
                    sell_intensity=100,
                    base_order_size=self.notional_trade_volume
                    / self.initial_price
                    / 100,
                    step_bias=1,
                    initial_asset_mint=1e8,
                    tag=f"MARKET_{self.market_config.instrument.code}_AGENT_{str(i_agent).zfill(3)}",
                )
                for i_agent in range(1)
            ]
        )
        self.agents.extend(
            [
                LimitOrderTrader(
                    wallet_name=f"RANDOM_TRADERS",
                    key_name=f"LIMIT_{self.market_config.instrument.code}_AGENT_{str(i_agent).zfill(3)}",
                    market_name=market_name,
                    asset_name=asset_name,
                    time_in_force_opts={"TIME_IN_FORCE_GTT": 1},
                    buy_volume=self.notional_trade_volume / self.initial_price / 100,
                    sell_volume=self.notional_trade_volume / self.initial_price / 100,
                    buy_intensity=100,
                    sell_intensity=100,
                    submit_bias=1,
                    cancel_bias=0,
                    duration=120,
                    price_process=price_process,
                    spread=0,
                    mean=-3,
                    sigma=0.5,
                    tag=f"MARKET_{self.market_config.instrument.code}_AGENT_{str(i_agent).zfill(3)}",
                    initial_asset_mint=1e8,
                )
                for i_agent in range(1)
            ]
        )

        self.agents.extend(
            [
                RiskyMarketOrderTrader(
                    wallet_name="risky_traders",
                    key_name=f"MARKET_{self.market_config.instrument.code}_SIDE_{side}_AGENT_{str(i_agent).zfill(3)}",
                    market_name=market_name,
                    asset_name=asset_name,
                    side=side,
                    initial_asset_mint=1_000,
                    leverage_factor=0.5,
                    step_bias=0.1,
                    tag=f"MARKET_{self.market_config.instrument.code}_SIDE_{side}_AGENT_{str(i_agent).zfill(3)}",
                )
                for side in ["SIDE_BUY", "SIDE_SELL"]
                for i_agent in range(5)
            ]
        )

        return {agent.name(): agent for agent in self.agents}

    def configure_environment(
        self,
        vega: VegaServiceNull,
        **kwargs,
    ) -> MarketEnvironmentWithState:
        if kwargs.get("network", Network.NULLCHAIN) == Network.NULLCHAIN:
            return MarketEnvironmentWithState(
                agents=list(self.agents.values()),
                n_steps=self.num_steps,
                random_agent_ordering=False,
                transactions_per_block=self.transactions_per_block,
                vega_service=vega,
                step_length_seconds=self.step_length_seconds,
                block_length_seconds=vega.seconds_per_block,
            )
        else:
            return NetworkEnvironment(
                agents=list(self.agents.values()),
                n_steps=self.num_steps,
                vega_service=vega,
                step_length_seconds=self.step_length_seconds,
                raise_datanode_errors=kwargs.get("raise_datanode_errors", False),
                raise_step_errors=kwargs.get("raise_step_errors", False),
                random_state=self.random_state,
                create_keys=True,
                mint_keys=True,
            )
