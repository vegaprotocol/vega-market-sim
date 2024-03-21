"""scenario.py
 
Module contains the DevOpsScenario class which defines a configurable trading scenario
which can be tested on a nullchain service and deployed to an existing network. The
scenario consists of the following agents.

    • 1x market manager
    • 1x market maker 
    • 2x auction traders
    • 3x random traders
    • 5x momentum traders
    • 3x sensitive traders
 
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Callable, Any

from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.constants import Network
from vega_sim.null_service import VegaServiceNull
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.environment.environment import (
    MarketEnvironmentWithState,
    NetworkEnvironment,
    Agent,
)
from vega_sim.scenario.common.utils.price_process import (
    get_live_price,
    get_historic_price_series,
)
from vega_sim.scenario.common.agents import (
    ExponentialShapedMarketMaker,
    OpenAuctionPass,
    MarketOrderTrader,
    PriceSensitiveLimitOrderTrader,
)
from vega_sim.configs.agents import ConfigurableMarketManager
from vega_sim.api.market import MarketConfig
from vega_sim.devops.wallet import ScenarioWallet, default_scenario_wallet

from vega_sim.devops.classes import (
    MarketMakerArgs,
    MarketManagerArgs,
    AuctionTraderArgs,
    RandomTraderArgs,
    SensitiveTraderArgs,
    SimulationArgs,
)


class DevOpsScenario(Scenario):
    def __init__(
        self,
        binance_code: str,
        market_manager_args: MarketManagerArgs,
        market_maker_args: MarketMakerArgs,
        auction_trader_args: AuctionTraderArgs,
        random_trader_args: RandomTraderArgs,
        sensitive_trader_args: SensitiveTraderArgs,
        feed_price_multiplier: int = 1,
        simulation_args: Optional[SimulationArgs] = None,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, Dict[str, Agent]], Any]
        ] = None,
        scenario_wallet: Optional[ScenarioWallet] = None,
        step_length_seconds: float = 10,
        market_name: Optional[str] = None,
    ):
        super().__init__(state_extraction_fn=state_extraction_fn)

        self.binance_code = binance_code
        self.feed_price_multiplier = feed_price_multiplier

        self.market_manager_args = market_manager_args
        self.market_maker_args = market_maker_args

        self.auction_trader_args = auction_trader_args
        self.random_trader_args = random_trader_args
        self.sensitive_trader_args = sensitive_trader_args
        self.simulation_args = simulation_args

        self.step_length_seconds = step_length_seconds
        self.market_name = market_name
        self.scenario_wallet = (
            scenario_wallet
            if scenario_wallet is not None
            else default_scenario_wallet()
        )

    def _get_historic_price_process(
        self,
        random_state,
    ) -> list:
        start = datetime.strptime(self.simulation_args.start_date, "%Y-%m-%d %H:%M:%S")

        if self.simulation_args.randomise_history:
            start = start + timedelta(days=int(random_state.choice(range(30))))

        end = start + timedelta(
            seconds=(self.simulation_args.n_steps)
            * self.simulation_args.granularity.value
        )

        price_process = get_historic_price_series(
            product_id=self.simulation_args.coinbase_code,
            granularity=self.simulation_args.granularity,
            interpolation=(
                f"{self.step_length_seconds}S"
                if self.step_length_seconds < self.simulation_args.granularity.value
                else self.simulation_args.granularity.value
            ),
            start=str(start),
            end=str(end),
        )

        return price_process

    def configure_agents(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        tag: str,
        random_state: Optional[np.random.RandomState] = None,
        **kwargs,
    ) -> Dict[str, Agent]:
        random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

        if kwargs.get("network", Network.FAIRGROUND) == Network.NULLCHAIN:
            self.price_process = self._get_historic_price_process(
                random_state=random_state
            )
        else:
            self.price_process = get_live_price(
                product=self.binance_code, multiplier=self.feed_price_multiplier
            )

        if self.scenario_wallet.market_creator_agent is None:
            raise ValueError(
                f"Missing market_creator wallet for the {self.market_name} devops scenario"
            )

        if self.scenario_wallet.market_maker_agent is None:
            raise ValueError(
                f"Missing market_maker wallet for the {self.market_name} devops scenario"
            )

        if kwargs.get("run_background", True):
            market_manager = None

            if kwargs.get("network", Network.FAIRGROUND) == Network.NULLCHAIN:
                market_manager = ConfigurableMarketManager(
                    wallet_name=self.scenario_wallet.market_creator_agent.wallet_name,
                    key_name=self.scenario_wallet.market_creator_agent.key_name,
                    market_config=self.market_manager_args.market_config,
                    oracle_prices=iter(self.price_process),
                    oracle_submission=0.1,
                    oracle_difference=0.001,
                    tag=self.market_manager_args.market_config.instrument.code,
                    random_state=random_state,
                )

            # Setup agent for proving a market for traders
            market_maker = ExponentialShapedMarketMaker(
                wallet_name=self.scenario_wallet.market_maker_agent.wallet_name,
                key_name=self.scenario_wallet.market_maker_agent.key_name,
                market_name=(
                    self.market_name
                    if self.market_name is not None
                    else self.market_manager_args.market_config.instrument.name
                ),
                initial_asset_mint=self.market_maker_args.initial_mint,
                commitment_amount=self.market_maker_args.commitment_amount,
                market_kappa=self.market_maker_args.market_kappa,
                kappa=self.market_maker_args.order_kappa,
                num_levels=self.market_maker_args.order_levels,
                tick_spacing=self.market_maker_args.order_spacing,
                inventory_lower_boundary=self.market_maker_args.inventory_lower_boundary,
                inventory_upper_boundary=self.market_maker_args.inventory_upper_boundary,
                fee_amount=self.market_maker_args.fee_amount,
                num_steps=60 * 60 * 24 * 365,
                price_process_generator=iter(self.price_process),
                orders_from_stream=False,
                state_update_freq=10,
                tag=None,
                isolated_margin_factor=self.market_maker_args.isolated_margin_factor,
            )

            # Setup agents for passing opening auction
            auction_pass_agents = [
                OpenAuctionPass(
                    wallet_name=party.wallet_name,
                    key_name=party.key_name,
                    market_name=(
                        self.market_name
                        if self.market_name is not None
                        else self.market_manager_args.market_config.instrument.name
                    ),
                    opening_auction_trade_amount=self.auction_trader_args.initial_volume,
                    initial_asset_mint=self.auction_trader_args.initial_mint,
                    initial_price=self.price_process[0],
                    side=["SIDE_BUY", "SIDE_SELL"][i],
                    tag=i,
                )
                for i, party in enumerate(self.scenario_wallet.auction_trader_agents)
            ]

            # Setup agents for placing random market orders
            random_market_order_traders = [
                MarketOrderTrader(
                    wallet_name=party.wallet_name,
                    key_name=party.key_name,
                    market_name=(
                        self.market_name
                        if self.market_name is not None
                        else self.market_manager_args.market_config.instrument.name
                    ),
                    initial_asset_mint=self.random_trader_args.initial_mint,
                    buy_intensity=self.random_trader_args.order_intensity[i],
                    sell_intensity=self.random_trader_args.order_intensity[i],
                    base_order_size=self.random_trader_args.order_volume[i],
                    step_bias=self.random_trader_args.step_bias[i],
                    tag=i,
                )
                for i, party in enumerate(self.scenario_wallet.random_trader_agents)
            ]

            # Setup agents for placing price-sensitive limit orders
            sensitive_limit_order_traders = [
                PriceSensitiveLimitOrderTrader(
                    wallet_name=party.wallet_name,
                    key_name=party.key_name,
                    market_name=(
                        self.market_name
                        if self.market_name is not None
                        else self.market_manager_args.market_config.instrument.name
                    ),
                    price_process_generator=iter(self.price_process),
                    initial_asset_mint=self.sensitive_trader_args.initial_mint,
                    scale=self.sensitive_trader_args.scale[i],
                    max_order_size=self.sensitive_trader_args.max_order_size[i],
                    tag=i,
                )
                for i, party in enumerate(self.scenario_wallet.sensitive_trader_agents)
            ]



            agents = list(filter(lambda x: not x is None, (
                [market_manager, market_maker]
                + auction_pass_agents
                + random_market_order_traders
                + sensitive_limit_order_traders
            )))

        else:
            agents = []

        if kwargs.get("agent", None) is not None:
            # If a market and asset were not specified, use scenario config values
            if kwargs["agent"].market_name is None:
                kwargs["agent"].market_name = (
                    self.market_manager_args.market_config.instrument.name
                )
            if kwargs["agent"].asset_name is None:
                kwargs["agent"].asset_name = self.market_manager_args.asset_name
            # If a sim, overwrite price process
            if kwargs.get("network", Network.FAIRGROUND) == Network.NULLCHAIN:
                kwargs["agent"].price_process_generator = iter(self.price_process)

            kwargs["agent"].order_validity_length = self.step_length_seconds

            agents.append(kwargs.get("agent", None))

        return {agent.name(): agent for agent in agents}

    def configure_environment(
        self,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        tag: Optional[str] = None,
        random_state: Optional[np.random.RandomState] = None,
        **kwargs,
    ) -> Union[MarketEnvironmentWithState, NetworkEnvironment]:
        if kwargs.get("network", Network.FAIRGROUND) == Network.NULLCHAIN:
            env = MarketEnvironmentWithState(
                agents=list(self.agents.values()),
                n_steps=self.simulation_args.n_steps,
                vega_service=vega,
                step_length_seconds=self.step_length_seconds,
                block_length_seconds=1,
                random_state=random_state,
                transactions_per_block=100,
            )
        else:
            env = NetworkEnvironment(
                agents=list(self.agents.values()),
                n_steps=-1,
                vega_service=vega,
                step_length_seconds=self.step_length_seconds,
                raise_datanode_errors=kwargs.get("raise_datanode_errors", False),
                raise_step_errors=kwargs.get("raise_step_errors", False),
                random_state=random_state,
            )
        return env
