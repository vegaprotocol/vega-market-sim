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
from typing import Optional, Union

from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.constants import Network
from vega_sim.null_service import VegaServiceNull
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.environment.environment import (
    MarketEnvironmentWithState,
    NetworkEnvironment,
)
from vega_sim.scenario.common.utils.price_process import (
    LivePrice,
    get_historic_price_series,
)
from vega_sim.scenario.common.agents import (
    ExponentialShapedMarketMaker,
    OpenAuctionPass,
    MarketOrderTrader,
    MomentumTrader,
    PriceSensitiveMarketOrderTrader,
)
from vega_sim.scenario.configurable_market.agents import ConfigurableMarketManager
from vega_sim.api.market import MarketConfig
from devops.wallet import (
    MARKET_CREATOR_AGENT,
    MARKET_SETTLER_AGENT,
    MARKET_MAKER_AGENT,
    AUCTION_TRADER_AGENTS,
    RANDOM_TRADER_AGENTS,
    MOMENTUM_TRADER_AGENTS,
    SENSITIVE_TRADER_AGENTS,
)
from devops.classes import (
    MarketMakerArgs,
    MarketManagerArgs,
    AuctionTraderArgs,
    RandomTraderArgs,
    MomentumTraderArgs,
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
        momentum_trader_args: MomentumTraderArgs,
        sensitive_trader_args: SensitiveTraderArgs,
        simulation_args: Optional[SimulationArgs] = None,
    ):

        self.binance_code = binance_code

        self.market_manager_args = market_manager_args
        self.market_maker_args = market_maker_args

        self.auction_trader_args = auction_trader_args
        self.random_trader_args = random_trader_args
        self.momentum_trader_args = momentum_trader_args
        self.sensitive_trader_args = sensitive_trader_args

        self.simulation_args = simulation_args

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
            start=str(start),
            end=str(end),
        )

        return price_process

    def _setup(
        self,
        network: Network,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        random_state: Optional[np.random.RandomState] = None,
    ):

        random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

        if network == Network.NULLCHAIN:
            self.price_process = self._get_historic_price_process(
                random_state=random_state
            )
        else:
            self.price_process = LivePrice(product=self.binance_code)

        # Setup agent for proposing and settling the market
        market_manager = ConfigurableMarketManager(
            proposal_wallet_name=MARKET_CREATOR_AGENT.wallet_name,
            proposal_wallet_pass=MARKET_CREATOR_AGENT.wallet_pass,
            proposal_key_name=MARKET_CREATOR_AGENT.key_name,
            termination_wallet_name=MARKET_SETTLER_AGENT.wallet_name,
            termination_wallet_pass=MARKET_SETTLER_AGENT.wallet_pass,
            termination_key_name=MARKET_SETTLER_AGENT.key_name,
            market_config=MarketConfig(),
            market_name=self.market_manager_args.market_name,
            market_code=self.market_manager_args.market_code,
            asset_name=self.market_manager_args.asset_name,
            asset_dp=self.market_manager_args.adp,
            initial_mint=self.market_manager_args.initial_mint,
            settlement_price=self.price_process[-1],
        )

        # Setup agent for proving a market for traders
        market_maker = ExponentialShapedMarketMaker(
            wallet_name=MARKET_MAKER_AGENT.wallet_name,
            wallet_pass=MARKET_MAKER_AGENT.wallet_pass,
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
        )

        # Setup agents for passing opening auction
        auction_pass_agents = [
            OpenAuctionPass(
                wallet_name=party.wallet_name,
                wallet_pass=party.wallet_pass,
                key_name=party.key_name,
                market_name=self.market_manager_args.market_name,
                asset_name=self.market_manager_args.asset_name,
                initial_asset_mint=self.auction_trader_args.initial_mint,
                initial_price=self.price_process[0],
                side=["SIDE_BUY", "SIDE_SELL"][i],
            )
            for i, party in enumerate(AUCTION_TRADER_AGENTS)
        ]

        # Setup agents for placing random market orders
        random_market_order_traders = [
            MarketOrderTrader(
                wallet_name=party.wallet_name,
                wallet_pass=party.wallet_pass,
                key_name=party.key_name,
                market_name=self.market_manager_args.market_name,
                asset_name=self.market_manager_args.asset_name,
                initial_asset_mint=self.random_trader_args.initial_mint,
                buy_intensity=self.random_trader_args.order_intensity,
                sell_intensity=self.random_trader_args.order_intensity,
                base_order_size=self.random_trader_args.order_volume,
            )
            for i, party in enumerate(RANDOM_TRADER_AGENTS)
        ]

        # Setup agents for placing momentum based market orders
        momentum_market_order_traders = [
            MomentumTrader(
                wallet_name=party.wallet_name,
                wallet_pass=party.wallet_pass,
                key_name=party.key_name,
                market_name=self.market_manager_args.market_name,
                asset_name=self.market_manager_args.asset_name,
                momentum_strategy=["MACD", "APO", "RSI", "STOCHRSI", "CPO"][i],
                initial_asset_mint=self.momentum_trader_args.initial_mint,
                order_intensity=self.momentum_trader_args.order_intensity,
                base_order_size=self.momentum_trader_args.order_volume,
            )
            for i, party in enumerate(MOMENTUM_TRADER_AGENTS)
        ]

        # Setup agents for placing price-sensitive market orders
        sensitive_market_order_traders = [
            PriceSensitiveMarketOrderTrader(
                wallet_name=party.wallet_name,
                wallet_pass=party.wallet_pass,
                key_name=party.key_name,
                market_name=self.market_manager_args.market_name,
                asset_name=self.market_manager_args.asset_name,
                price_process_generator=iter(self.price_process),
                initial_asset_mint=self.sensitive_trader_args.initial_mint,
                buy_intensity=self.sensitive_trader_args.order_intensity[i],
                sell_intensity=self.sensitive_trader_args.order_intensity[i],
                base_order_size=self.sensitive_trader_args.order_volume[i],
                price_half_life=self.sensitive_trader_args.price_half_life[i],
            )
            for i, party in enumerate(SENSITIVE_TRADER_AGENTS)
        ]

        agents = (
            [
                market_manager,
                market_maker,
            ]
            + auction_pass_agents
            + random_market_order_traders
            + momentum_market_order_traders
            + sensitive_market_order_traders
        )

        return agents

    def run_iteration(
        self,
        network: Network,
        vega: Union[VegaServiceNull, VegaServiceNetwork],
        pause_at_completion: bool = False,
        run_with_console: bool = False,
        random_state: Optional[np.random.RandomState] = None,
        raise_datanode_errors: Optional[bool] = False,
        raise_step_errors: Optional[bool] = False,
    ):

        agents = self._setup(network=network, vega=vega, random_state=random_state)

        if network == Network.NULLCHAIN:
            env = MarketEnvironmentWithState(
                agents=agents,
                n_steps=self.simulation_args.n_steps,
                vega_service=vega,
                step_length_seconds=self.simulation_args.granularity.value,
                block_length_seconds=1,
            )
            env.run(
                run_with_console=run_with_console,
                pause_at_completion=pause_at_completion,
            )
        else:
            env = NetworkEnvironment(
                agents=agents,
                n_steps=-1,
                vega_service=vega,
                step_length_seconds=0,
                raise_datanode_errors=raise_datanode_errors,
                raise_step_errors=raise_step_errors,
            )
            env.run()
