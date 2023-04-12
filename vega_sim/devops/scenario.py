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
    LivePrice,
    get_historic_price_series,
)
from vega_sim.scenario.common.agents import (
    ExponentialShapedMarketMaker,
    OpenAuctionPass,
    MarketOrderTrader,
    PriceSensitiveLimitOrderTrader,
)
from vega_sim.scenario.configurable_market.agents import ConfigurableMarketManager
from vega_sim.api.market import MarketConfig
from vega_sim.devops.wallet import (
    MARKET_CREATOR_AGENT,
    MARKET_SETTLER_AGENT,
    MARKET_MAKER_AGENT,
    AUCTION_TRADER_AGENTS,
    RANDOM_TRADER_AGENTS,
    SENSITIVE_TRADER_AGENTS,
)
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
        simulation_args: Optional[SimulationArgs] = None,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, Dict[str, Agent]], Any]
        ] = None,
        step_length_seconds: float = 10,
        market_name: Optional[str] = None,
    ):
        super().__init__(state_extraction_fn=state_extraction_fn)

        self.binance_code = binance_code

        self.market_manager_args = market_manager_args
        self.market_maker_args = market_maker_args

        self.auction_trader_args = auction_trader_args
        self.random_trader_args = random_trader_args
        self.sensitive_trader_args = sensitive_trader_args
        self.simulation_args = simulation_args

        self.step_length_seconds = step_length_seconds
        self.market_name = market_name

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
            self.price_process = LivePrice(product=self.binance_code)

        if kwargs.get("run_background", True):
            # Setup agent for proposing and settling the market
            market_manager = ConfigurableMarketManager(
                proposal_wallet_name=MARKET_CREATOR_AGENT.wallet_name,
                proposal_key_name=MARKET_CREATOR_AGENT.key_name,
                termination_wallet_name=MARKET_SETTLER_AGENT.wallet_name,
                termination_key_name=MARKET_SETTLER_AGENT.key_name,
                market_config=MarketConfig(),
                market_name=self.market_name
                if self.market_name is not None
                else self.market_manager_args.market_name,
                market_code=self.market_manager_args.market_code,
                asset_name=self.market_manager_args.asset_name,
                asset_dp=self.market_manager_args.adp,
                initial_mint=self.market_manager_args.initial_mint,
                settlement_price=self.price_process[-1],
                tag=None,
            )

            # Setup agent for proving a market for traders
            market_maker = ExponentialShapedMarketMaker(
                wallet_name=MARKET_MAKER_AGENT.wallet_name,
                key_name=MARKET_MAKER_AGENT.key_name,
                market_name=self.market_manager_args.market_name,
                asset_name=self.market_manager_args.asset_name,
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
            )

            # Setup agents for passing opening auction
            auction_pass_agents = [
                OpenAuctionPass(
                    wallet_name=party.wallet_name,
                    key_name=party.key_name,
                    market_name=self.market_name
                    if self.market_name is not None
                    else self.market_manager_args.market_name,
                    asset_name=self.market_manager_args.asset_name,
                    initial_asset_mint=self.auction_trader_args.initial_mint,
                    initial_price=self.price_process[0],
                    side=["SIDE_BUY", "SIDE_SELL"][i],
                    tag=i,
                )
                for i, party in enumerate(AUCTION_TRADER_AGENTS)
            ]

            # Setup agents for placing random market orders
            random_market_order_traders = [
                MarketOrderTrader(
                    wallet_name=party.wallet_name,
                    key_name=party.key_name,
                    market_name=self.market_name
                    if self.market_name is not None
                    else self.market_manager_args.market_name,
                    asset_name=self.market_manager_args.asset_name,
                    initial_asset_mint=self.random_trader_args.initial_mint,
                    buy_intensity=self.random_trader_args.order_intensity[i],
                    sell_intensity=self.random_trader_args.order_intensity[i],
                    base_order_size=self.random_trader_args.order_volume[i],
                    step_bias=self.random_trader_args.step_bias[i],
                    tag=i,
                )
                for i, party in enumerate(RANDOM_TRADER_AGENTS)
            ]

            # Setup agents for placing price-sensitive limit orders
            sensitive_limit_order_traders = [
                PriceSensitiveLimitOrderTrader(
                    wallet_name=party.wallet_name,
                    key_name=party.key_name,
                    market_name=self.market_name
                    if self.market_name is not None
                    else self.market_manager_args.market_name,
                    asset_name=self.market_manager_args.asset_name,
                    price_process_generator=iter(self.price_process),
                    initial_asset_mint=self.sensitive_trader_args.initial_mint,
                    scale=self.sensitive_trader_args.scale[i],
                    max_order_size=self.sensitive_trader_args.max_order_size[i],
                    tag=i,
                )
                for i, party in enumerate(SENSITIVE_TRADER_AGENTS)
            ]

            agents = (
                [market_manager, market_maker]
                + auction_pass_agents
                + random_market_order_traders
                + sensitive_limit_order_traders
            )

        else:
            agents = []

        if kwargs.get("agent", None) is not None:
            # If a market and asset were not specified, use scenario config values
            if kwargs["agent"].market_name is None:
                kwargs["agent"].market_name = self.market_manager_args.market_name
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
