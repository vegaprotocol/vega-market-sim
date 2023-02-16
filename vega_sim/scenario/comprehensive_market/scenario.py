import argparse
import logging
import numpy as np
from typing import Any, Callable, List, Optional, Tuple, Dict
from vega_sim.environment.agent import Agent

from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.common.utils.price_process import random_walk
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull, VegaService
from vega_sim.scenario.comprehensive_market.agents import (
    MM_WALLET,
    AUCTION1_WALLET,
    AUCTION2_WALLET,
    TERMINATE_WALLET,
    create_agent_wallets,
)
from vega_sim.scenario.common.agents import (
    MarketManager,
    SimpleLiquidityProvider,
    MarketOrderTrader,
    LimitOrderTrader,
    MomentumTrader,
    OpenAuctionPass,
    StateAgent,
)


class ComprehensiveMarket(Scenario):
    def __init__(
        self,
        num_steps: int = 1000,
        market_decimal: int = 5,
        asset_decimal: int = 5,
        market_position_decimal: int = 2,
        market_name: str = None,
        asset_name: str = None,
        initial_asset_mint: float = 1000000,
        initial_price: Optional[float] = None,
        sigma: float = 1,
        lp_commitamount: float = 200000,
        spread: int = 2,
        block_size: int = 1,
        block_length_seconds: int = 1,
        step_length_seconds: int = 1,
        opening_auction_trade_amount: float = 1,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, Dict[str, Agent]], Any]
        ] = None,
        pause_every_n_steps: Optional[int] = None,
        price_process_fn: Optional[Callable[[None], List[float]]] = None,
        market_order_trader_order_intensity: int = 10,
        market_order_trader_order_size: float = 0.1,
        settle_at_end: bool = True,
        limit_order_trader_quantity: int = 5,
        limit_order_trader_submit_bias: float = 0.5,
        limit_order_trader_cancel_bias: float = 0.5,
        limit_order_trader_order_intensity: int = 10,
        limit_order_trader_order_size: float = 0.1,
        limit_order_trader_mean: float = -5,
        limit_order_trader_sigma: float = 0.5,
        limit_order_trader_duration: int = 300,
        limit_order_trader_time_in_force_opts: Optional[dict] = None,
        momentum_trader_order_intensity: int = 10,
        momentum_trader_order_size: float = 0.1,
        momentum_trader_strategies: List[str] = None,
        momentum_trader_strategy_args: List[Dict[str, float]] = None,
        momentum_trader_indicator_thresholds: List[Tuple[float, float]] = None,
        num_lp_agents: int = 3,
        num_mo_agents: int = 5,
        num_lo_agents: int = 20,
        num_momentum_agents: int = 1,
    ):
        super().__init__(state_extraction_fn=state_extraction_fn)
        self.num_steps = num_steps
        self.market_decimal = market_decimal
        self.asset_decimal = asset_decimal
        self.market_position_decimal = market_position_decimal
        self.initial_price = initial_price
        self.sigma = sigma
        self.spread = spread / 10**self.market_decimal
        self.block_size = block_size
        self.block_length_seconds = block_length_seconds
        self.step_length_seconds = step_length_seconds
        self.pause_every_n_steps = pause_every_n_steps
        self.lp_commitamount = lp_commitamount
        self.initial_asset_mint = initial_asset_mint
        self.market_name = "ETH:USD" if market_name is None else market_name
        self.asset_name = "tDAI" if asset_name is None else asset_name
        self.price_process_fn = price_process_fn
        self.opening_auction_trade_amount = opening_auction_trade_amount
        self.settle_at_end = settle_at_end

        # MarketOrderTraderOptions
        self.market_order_trader_order_intensity = market_order_trader_order_intensity
        self.market_order_trader_order_size = market_order_trader_order_size

        # LimitOrderTrader Options
        self.limit_order_trader_quantity = limit_order_trader_quantity
        self.limit_order_trader_submit_bias = limit_order_trader_submit_bias
        self.limit_order_trader_cancel_bias = limit_order_trader_cancel_bias
        self.limit_order_trader_order_intensity = limit_order_trader_order_intensity
        self.limit_order_trader_order_size = limit_order_trader_order_size
        self.limit_order_trader_mean = limit_order_trader_mean
        self.limit_order_trader_sigma = limit_order_trader_sigma
        self.limit_order_trader_duration = limit_order_trader_duration
        self.limit_order_trader_time_in_force_opts = (
            limit_order_trader_time_in_force_opts
        )

        # MomentumTrader Options
        self.momentum_trader_order_intensity = momentum_trader_order_intensity
        self.momentum_trader_order_size = momentum_trader_order_size
        self.momentum_trader_strategies = (
            momentum_trader_strategies
            if momentum_trader_strategies is not None
            else ["RSI"] * num_momentum_agents
        )
        self.momentum_trader_strategy_args = momentum_trader_strategy_args
        self.momentum_trader_indicator_thresholds = (
            momentum_trader_indicator_thresholds
            if momentum_trader_indicator_thresholds is not None
            else [(70, 30)] * num_momentum_agents
        )

        # Agent options
        self.lp_wallets = create_agent_wallets(n=num_lp_agents, prefix="lp_agent_")
        self.mo_wallets = create_agent_wallets(n=num_mo_agents, prefix="lo_agent_")
        self.lo_wallets = create_agent_wallets(n=num_lo_agents, prefix="mo_agent_")
        self.momentum_wallets = create_agent_wallets(
            n=num_momentum_agents, prefix="momentum_agent_"
        )

    def _generate_price_process(
        self,
        random_state: Optional[np.random.RandomState] = None,
    ):
        return random_walk(
            num_steps=self.num_steps,
            sigma=self.sigma,
            starting_price=self.initial_price,
            random_state=random_state,
        )

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: str = "",
        random_state: Optional[np.random.RandomState] = None,
    ) -> Dict[str, StateAgent]:
        # Set up market name and settlement asset
        market_name = self.market_name + f"_{tag}"
        asset_name = self.asset_name + f"_{tag}"

        price_process = (
            self.price_process_fn()
            if self.price_process_fn is not None
            else self._generate_price_process(random_state=random_state)
        )

        mm_agent = MarketManager(
            key_name=MM_WALLET.name,
            terminate_key_name=TERMINATE_WALLET.name,
            asset_decimal=self.asset_decimal,
            market_decimal=self.market_decimal,
            market_position_decimal=self.market_position_decimal,
            market_name=market_name,
            asset_name=asset_name,
            commitment_amount=self.lp_commitamount,
            tag=str(tag),
            settlement_price=price_process[-1] if self.settle_at_end else None,
        )

        lp_agents = [
            LiquidityProvider(
                key_name=self.lp_wallets[i].name,
                initial_asset_mint=self.initial_asset_mint,
                market_name=market_name,
                asset_name=asset_name,
                tag=f"{i}_{tag}",
                commitment_amount=self.lp_commitamount,
                fee=0.001,
                offset=self.spread * (i + 1),
            )
            for i in range(len(self.lp_wallets))
        ]

        mo_agents = [
            MarketOrderTrader(
                key_name=self.mo_wallets[i].name,
                initial_asset_mint=self.initial_asset_mint,
                market_name=market_name,
                asset_name=asset_name,
                tag=f"{i}_{tag}",
                buy_intensity=self.market_order_trader_order_intensity,
                sell_intensity=self.market_order_trader_order_intensity,
                base_order_size=self.market_order_trader_order_size,
                random_state=random_state,
            )
            for i in range(len(self.mo_wallets))
        ]

        lo_agents = [
            LimitOrderTrader(
                key_name=self.lo_wallets[i].name,
                initial_asset_mint=self.initial_asset_mint,
                market_name=market_name,
                asset_name=asset_name,
                tag=f"{i}_{tag}",
                spread=self.spread,
                price_process=price_process,
                buy_intensity=self.limit_order_trader_order_intensity,
                sell_intensity=self.limit_order_trader_order_intensity,
                buy_volume=self.limit_order_trader_order_size,
                sell_volume=self.limit_order_trader_order_size,
                submit_bias=self.limit_order_trader_submit_bias,
                cancel_bias=self.limit_order_trader_cancel_bias,
                duration=self.limit_order_trader_duration,
                time_in_force_opts=self.limit_order_trader_time_in_force_opts,
                mean=self.limit_order_trader_mean,
                sigma=self.limit_order_trader_sigma,
                random_state=random_state,
            )
            for i in range(len(self.lo_wallets))
        ]

        momentum_agents = [
            MomentumTrader(
                key_name=self.momentum_wallets[i].name,
                market_name=market_name,
                asset_name=asset_name,
                initial_asset_mint=self.initial_asset_mint,
                order_intensity=self.momentum_trader_order_intensity,
                base_order_size=self.momentum_trader_order_size,
                momentum_strategy=self.momentum_trader_strategies[i],
                momentum_strategy_args=self.momentum_trader_strategy_args[i]
                if self.momentum_trader_strategy_args is not None
                else self.momentum_trader_strategy_args,
                indicator_threshold=self.momentum_trader_indicator_thresholds[i],
                send_limit_order=True,
                offset_levels=20,
                tag=f"{i}_{tag}",
            )
            for i in range(len(self.momentum_wallets))
        ]

        auctionpass1 = OpenAuctionPass(
            key_name=AUCTION1_WALLET.name,
            side="SIDE_BUY",
            initial_asset_mint=self.initial_asset_mint,
            initial_price=self.initial_price
            if self.initial_price is not None
            else price_process[0],
            market_name=market_name,
            asset_name=asset_name,
            opening_auction_trade_amount=self.opening_auction_trade_amount,
            tag=f"1_{tag}",
        )

        auctionpass2 = OpenAuctionPass(
            key_name=AUCTION2_WALLET.name,
            side="SIDE_SELL",
            initial_asset_mint=self.initial_asset_mint,
            initial_price=self.initial_price
            if self.initial_price is not None
            else price_process[0],
            market_name=market_name,
            asset_name=asset_name,
            opening_auction_trade_amount=self.opening_auction_trade_amount,
            tag=f"2_{tag}",
        )

        agents = (
            [
                mm_agent,
                auctionpass1,
                auctionpass2,
            ]
            + lp_agents
            + mo_agents
            + lo_agents
            + momentum_agents
        )
        return {agent.name(): agent for agent in agents}

    def configure_environment(
        self, vega: VegaService, **kwargs
    ) -> MarketEnvironmentWithState:
        self.env = MarketEnvironmentWithState(
            agents=list(self.agents.values()),
            n_steps=self.num_steps,
            transactions_per_block=self.block_size,
            vega_service=vega,
            step_length_seconds=self.step_length_seconds,
            block_length_seconds=self.block_length_seconds,
            pause_every_n_steps=self.pause_every_n_steps,
        )

        return self.env


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

    step_length = 60 * 60

    scenario = ComprehensiveMarket(num_steps=200)

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=True,
        seconds_per_block=40,  # Heuristic
    ) as vega:
        scenario.run_iteration(
            vega=vega,
            pause_at_completion=True,
        )
