"""scenario.py

Module contains the HedgedMarket Scenario class which can be used to run a simulation of
a hedged market maker who makes a market on an internal market and hedges its position
on a highly liquid external market. The hedged market maker uses separate keys for each
market to represent the accounts on separate exchanges and uses transfers to balance
each accounts leverage. Transfer delays can be configured to represent the withdrawal
delays on the internal and external markets.

The scenario uses an InformedTrader agent, who has knowledge of all future prices, to
modify whether the hedged market maker makes a profit on the internal or external
market. This is done by modifying the accuracy of the InformedTrader (0.0 causes the
hedged market maker to profit in the internal market and 1.0 causes the hedged market 
maker to profit in the external market).

Agents:

    int_market_manager (MarketManager):
        Proposes and settles the internal market.
    ext_market_manager (MarketManager):
        Proposes and settles the external market.
    int_market_maker (HedgedMarketMaker):
        Makes the market on the internal market.
    ext_market_maker (ExponentialShapedMarketMaker):
        Makes the market on the external market.
    int_auction_pass_bid (OpenAuctionPass):
        Provides a best-bid to exit the auction on the internal market.
    int_auction_pass_bid (OpenAuctionPass):
        Provides a best-ask to exit the auction on the internal market.
    ext_auction_pass_bid (OpenAuctionPass):
        Provides a best-bid to exit the auction on the internal market.
    ext_auction_pass_bid (OpenAuctionPass):
        Provides a best-ask to exit the auction on the internal market.
    int_random_trader (MarketOrderTrader):
        Provides a small volume trade at each step on the internal market.
    ext_random_trader (MarketOrderTrader):
        Provides a small volume trade at each step on the external market.
    int_informed_trader (InformedTrader):
        Places informed orders at each step. Can be configured to cause the hedged
        market maker to have a +ve or -ve PnL in either market.

Examples:

    $ python -m vega_sim.scenario.adhoc -s hedged_market --console --pause

"""

import numpy as np
from typing import Any, Callable, List, Optional
from vega_sim.environment.agent import Agent

from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.common.utils.price_process import random_walk
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.hedged_market_maker.agents import (
    MARKET_CREATOR,
    MARKET_SETTLER,
    INT_MARKET_MAKER_KEY_A,
    INT_MARKET_MAKER_KEY_B,
    EXT_MARKET_MAKER,
    AUCTION_PASS_BID,
    AUCTION_PASS_ASK,
    INT_RANDOM_TRADER,
    EXT_RANDOM_TRADER,
    INT_INFORMED_TRADER,
)
from vega_sim.scenario.common.agents import (
    MarketManager,
    OpenAuctionPass,
    HedgedMarketMaker,
    ExponentialShapedMarketMaker,
    InformedTrader,
    MarketOrderTrader,
)


class HedgedMarket(Scenario):
    """Class defining a HedgedMarket scenario,

    Scenario simulates a hedged market maker who makes a market on an internal market
    and hedges their position on an external market. An informed trader can exploit
    knowledge of future prices to make profitable trades with the hedged market maker.
    The accuracy of this informed trader is configurable.

    Args:
        num_steps (int, optional):
            Number of simulation steps to run. Defaults to 290.
        step_length_seconds (int, optional):
            Length of each step in seconds. Defaults to 60.
        block_length_seconds (int, optional):
            Length of each block in seconds. Defaults to 1.
        price_process_fn (Optional[Callable[[None], List[float]]], optional):
            Function used to generate a price process. Defaults to None.
        initial_price (Optional[float], optional):
            Initial price for RW if no price_process_fn specified. Defaults to None.
        asset_name (str, optional):
            Name of asset to use in simulation. Defaults to "ETH".
        asset_adp (int, optional):
            Number of decimal places for asset. Defaults to 5.
        int_name (str, optional):
            Name of the internal market. Defaults to "ETHUSD (Internal Market)".
        int_mdp (int, optional):
            Number of decimal places for price on the internal market. Defaults to 3.
        int_pdp (int, optional):
            Number of decimal places for position on the internal market. Defaults to 3.
        int_lock (float, optional):
            Internal market withdrawal delay length in seconds. Defaults to 24*60*60.
        ext_name (str, optional):
            Name of the external market. Defaults to "ETHUSD (External Market)".
        ext_mdp (int, optional):
            Number of decimal places for price on the external market. Defaults to 3.
        ext_pdp (int, optional):
            Number of decimal places for position on the external market. Defaults to 3.
        ext_lock (float, optional):
            External market withdrawal delay length in seconds. Defaults to 5*60.
        int_mm_int_key_mint (float, optional):
            Amount of asset to initially mint to the internal key. Defaults to 2e5.
        int_mm_ext_key_mint (float, optional):
            Amount of asset to initially mint to the external key. Defaults to 1e5.
        int_mm_commitment_amount (float, optional):
            Amount of asset to initially commit as liquidity to the internal market.
            Defaults to 1e5.
        int_mm_profit_margin (float, optional):
            Desired profit margin to make on each trade on the internal market.
            Defaults to 0.0000.
        ext_mm_num_levels (int, optional):
            Number of price levels on the external market. Defaults to 1e10.
        ext_mm_tick_spacing (float, optional):
            Spacing of price levels on the external market. Defaults to 0.1.
        ext_mm_kappa (float, optional):
            Order kappa on the external market. Defaults to 1.
        ext_mm_market_kappa (float, optional):
            Estimated market kappa on the external market. Defaults to 10.
        int_it_proportion (float, optional):
            Proportion of profitable orders taken by the informed trader at each step.
            Defaults to 0.1.
        int_it_accuracy (float, optional):
            Accuracy of informed trader's speculation at each step.
            Defaults to 1.0.
        int_it_lookahead (int, optional):
            Number of steps for informed trader to look ahead. Defaults to 30.
        random_agent_ordering (bool, optional):
            Whether to randomly order each agents step action. Defaults to False.
        transactions_per_block (int, optional):
            Number of transactions allowed per block. Defaults to 1000.
        state_extraction_fn (Optional[ Callable[[VegaServiceNull, List[Agent]], Any] ], optional):
            Defines which states to extract and record. Defaults to None.
        state_extraction_freq (int, optional):
            How often to run the state_extraction_fn. Defaults to 1.
        pause_every_n_steps (Optional[int], optional):
            Number of steps to simulate before pausing the simulation. Defaults to None.
    """

    def __init__(
        self,
        num_steps: int = 290,
        step_length_seconds: int = 60,
        block_length_seconds: int = 1,
        price_process_fn: Optional[Callable[[None], List[float]]] = None,
        initial_price: Optional[float] = None,
        asset_name: str = "ETH",
        asset_adp: int = 5,
        int_name: str = "ETHUSD (Internal Market)",
        int_mdp: int = 3,
        int_pdp: int = 3,
        int_lock: float = 24 * 60 * 60,
        ext_name: str = "ETHUSD (External Market)",
        ext_mdp: int = 3,
        ext_pdp: int = 3,
        ext_lock: float = 5 * 60,
        int_mm_int_key_mint: float = 2e10,
        int_mm_ext_key_mint: float = 1e10,
        int_mm_commitment_amount: float = 1e5,
        int_mm_profit_margin: float = 0.0000,
        ext_mm_num_levels: int = 1e10,
        ext_mm_tick_spacing: float = 0.1,
        ext_mm_kappa: float = 1,
        ext_mm_market_kappa: float = 10,
        int_it_proportion: float = 0.1,
        int_it_accuracy: float = 1.0,
        int_it_lookahead: int = 30,
        random_agent_ordering: bool = False,
        transactions_per_block: int = 1000,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, List[Agent]], Any]
        ] = None,
        state_extraction_freq: int = 1,
        pause_every_n_steps: Optional[int] = None,
    ):
        # Simulation properties
        self.num_steps = num_steps
        self.step_length_seconds = step_length_seconds
        self.block_length_seconds = block_length_seconds
        self.price_process_fn = price_process_fn
        self.initial_price = initial_price
        self.random_agent_ordering = random_agent_ordering
        self.transactions_per_block = transactions_per_block
        self.state_extraction_fn = state_extraction_fn
        self.state_extraction_freq = state_extraction_freq
        self.pause_every_n_steps = pause_every_n_steps

        # Asset properties
        self.asset_name = asset_name
        self.asset_adp = asset_adp

        # Internal market properties
        self.int_name = int_name
        self.int_mdp = int_mdp
        self.int_pdp = int_pdp
        self.int_lock = int_lock

        # External market properties
        self.ext_name = ext_name
        self.ext_pdp = ext_pdp
        self.ext_mdp = ext_mdp
        self.ext_lock = ext_lock

        # Internal market maker properties
        self.int_mm_int_key_mint = int_mm_int_key_mint
        self.int_mm_ext_key_mint = int_mm_ext_key_mint
        self.int_mm_commitment_amount = int_mm_commitment_amount
        self.int_mm_profit_margin = int_mm_profit_margin

        # External market maker properties
        self.ext_mm_num_levels = ext_mm_num_levels
        self.ext_mm_tick_spacing = ext_mm_tick_spacing
        self.ext_mm_kappa = ext_mm_kappa
        self.ext_mm_market_kappa = ext_mm_market_kappa

        # Informed trader properties
        self.int_it_proportion = int_it_proportion
        self.int_it_accuracy = int_it_accuracy
        self.int_it_lookahead = int_it_lookahead

    def _generate_price_process(
        self,
        random_state: Optional[np.random.RandomState] = None,
    ):
        return random_walk(
            num_steps=self.num_steps,
            sigma=0.01,
            starting_price=self.initial_price,
            random_state=random_state,
        )

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: str = "",
        random_state: Optional[np.random.RandomState] = None,
    ) -> MarketEnvironmentWithState:
        price_process = (
            self.price_process_fn()
            if self.price_process_fn is not None
            else self._generate_price_process(random_state=random_state)
        )
        initial_price = (
            self.initial_price if self.initial_price is not None else price_process[0]
        )

        int_market_manager = MarketManager(
            wallet_name=MARKET_CREATOR.wallet_name,
            wallet_pass=MARKET_CREATOR.wallet_pass,
            key_name=MARKET_CREATOR.key_name,
            terminate_wallet_name=MARKET_SETTLER.wallet_name,
            terminate_wallet_pass=MARKET_SETTLER.wallet_pass,
            terminate_key_name=MARKET_SETTLER.key_name,
            asset_name=self.asset_name,
            asset_decimal=self.asset_adp,
            market_decimal=self.int_mdp,
            market_position_decimal=self.int_pdp,
            market_name=self.int_name,
            settlement_price=price_process[-1],
        )

        ext_market_manager = MarketManager(
            wallet_name=MARKET_CREATOR.wallet_name,
            wallet_pass=MARKET_CREATOR.wallet_pass,
            key_name=MARKET_CREATOR.key_name,
            terminate_wallet_name=MARKET_SETTLER.wallet_name,
            terminate_wallet_pass=MARKET_SETTLER.wallet_pass,
            terminate_key_name=MARKET_SETTLER.key_name,
            asset_name=self.asset_name,
            asset_decimal=self.asset_adp,
            market_decimal=self.ext_mdp,
            market_position_decimal=self.ext_pdp,
            market_name=self.ext_name,
            settlement_price=price_process[-1],
        )

        int_market_maker = HedgedMarketMaker(
            wallet_name=INT_MARKET_MAKER_KEY_A.wallet_name,
            wallet_pass=INT_MARKET_MAKER_KEY_A.wallet_pass,
            key_name=INT_MARKET_MAKER_KEY_A.key_name,
            external_key_name=INT_MARKET_MAKER_KEY_B.key_name,
            price_process_generator=iter(price_process),
            internal_key_mint=self.int_mm_int_key_mint,
            external_key_mint=self.int_mm_ext_key_mint,
            commitment_amount=self.int_mm_commitment_amount,
            asset_name=self.asset_name,
            asset_decimal_places=self.asset_adp,
            market_name=self.int_name,
            market_decimal_places=self.int_mdp,
            num_steps=self.num_steps,
            num_levels=25,
            kappa=self.ext_mm_kappa,
            market_kappa=self.ext_mm_market_kappa,
            tick_spacing=self.ext_mm_tick_spacing,
            inventory_upper_boundary=30,
            inventory_lower_boundary=-30,
            state_update_freq=60,
            fee_amount=1e-03,
            profit_margin=self.int_mm_profit_margin,
            external_market_name=self.ext_name,
            internal_delay=self.int_lock,
            external_delay=self.ext_lock,
        )

        ext_market_maker = ExponentialShapedMarketMaker(
            wallet_name=EXT_MARKET_MAKER.wallet_name,
            wallet_pass=EXT_MARKET_MAKER.wallet_pass,
            key_name=EXT_MARKET_MAKER.key_name,
            price_process_generator=iter(price_process),
            initial_asset_mint=1e10,
            commitment_amount=1e6,
            asset_name=self.asset_name,
            asset_decimal_places=self.asset_adp,
            market_name=self.ext_name,
            market_decimal_places=self.ext_mdp,
            num_steps=self.num_steps,
            num_levels=25,
            kappa=self.ext_mm_kappa,
            market_kappa=self.ext_mm_market_kappa,
            tick_spacing=self.ext_mm_tick_spacing,
            inventory_upper_boundary=30,
            inventory_lower_boundary=-30,
            state_update_freq=60,
            fee_amount=1e-03,
        )

        int_auction_pass_bid = OpenAuctionPass(
            wallet_name=AUCTION_PASS_BID.wallet_name,
            wallet_pass=AUCTION_PASS_BID.wallet_pass,
            key_name=AUCTION_PASS_BID.key_name,
            side="SIDE_BUY",
            initial_asset_mint=1e10,
            initial_price=initial_price,
            market_name=self.int_name,
            asset_name=self.asset_name,
            opening_auction_trade_amount=self.int_pdp,
        )
        int_auction_pass_ask = OpenAuctionPass(
            wallet_name=AUCTION_PASS_ASK.wallet_name,
            wallet_pass=AUCTION_PASS_ASK.wallet_pass,
            key_name=AUCTION_PASS_ASK.key_name,
            side="SIDE_SELL",
            initial_asset_mint=1e10,
            initial_price=initial_price,
            market_name=self.int_name,
            asset_name=self.asset_name,
            opening_auction_trade_amount=self.int_pdp,
        )
        ext_auction_pass_bid = OpenAuctionPass(
            wallet_name=AUCTION_PASS_BID.wallet_name,
            wallet_pass=AUCTION_PASS_BID.wallet_pass,
            key_name=AUCTION_PASS_BID.key_name,
            side="SIDE_BUY",
            initial_asset_mint=1e10,
            initial_price=initial_price,
            market_name=self.ext_name,
            asset_name=self.asset_name,
            opening_auction_trade_amount=self.ext_pdp,
        )
        ext_auction_pass_ask = OpenAuctionPass(
            wallet_name=AUCTION_PASS_ASK.wallet_name,
            wallet_pass=AUCTION_PASS_ASK.wallet_pass,
            key_name=AUCTION_PASS_ASK.key_name,
            side="SIDE_SELL",
            initial_asset_mint=1e10,
            initial_price=initial_price,
            market_name=self.ext_name,
            asset_name=self.asset_name,
            opening_auction_trade_amount=self.ext_pdp,
        )

        int_random_trader = MarketOrderTrader(
            wallet_name=INT_RANDOM_TRADER.wallet_name,
            wallet_pass=INT_RANDOM_TRADER.wallet_pass,
            key_name=INT_RANDOM_TRADER.key_name,
            market_name=self.int_name,
            asset_name=self.asset_name,
            initial_asset_mint=1e10,
            buy_intensity=1 * 10 ** (self.int_pdp),
            sell_intensity=1 * 10 ** (self.int_pdp),
            base_order_size=1 * 10 ** -(self.int_pdp),
        )
        ext_random_trader = MarketOrderTrader(
            wallet_name=EXT_RANDOM_TRADER.wallet_name,
            wallet_pass=EXT_RANDOM_TRADER.wallet_pass,
            key_name=EXT_RANDOM_TRADER.key_name,
            market_name=self.ext_name,
            asset_name=self.asset_name,
            initial_asset_mint=1e10,
            buy_intensity=1 * 10 ** (self.ext_pdp),
            sell_intensity=1 * 10 ** (self.ext_pdp),
            base_order_size=1 * 10 ** -(self.ext_pdp),
        )

        int_informed_trader = InformedTrader(
            wallet_name=INT_INFORMED_TRADER.wallet_name,
            wallet_pass=INT_INFORMED_TRADER.wallet_pass,
            key_name=INT_INFORMED_TRADER.key_name,
            asset_name=self.asset_name,
            market_name=self.int_name,
            initial_asset_mint=1e10,
            proportion_taken=self.int_it_proportion,
            price_process=price_process,
            accuracy=self.int_it_accuracy,
            lookahead=self.int_it_lookahead,
        )

        return {
            agent.name(): agent
            for agent in [
                int_market_manager,
                ext_market_manager,
                int_market_maker,
                ext_market_maker,
                int_auction_pass_bid,
                int_auction_pass_ask,
                ext_auction_pass_bid,
                ext_auction_pass_ask,
                int_random_trader,
                ext_random_trader,
                int_informed_trader,
            ]
        }

    def configure_environment(
        self,
        vega: VegaServiceNull,
        **kwargs,
    ) -> MarketEnvironmentWithState:
        return MarketEnvironmentWithState(
            agents=list(self.agents.values()),
            n_steps=self.num_steps,
            random_agent_ordering=self.random_agent_ordering,
            transactions_per_block=self.transactions_per_block,
            vega_service=vega,
            state_extraction_freq=self.state_extraction_freq,
            step_length_seconds=self.step_length_seconds,
            block_length_seconds=self.block_length_seconds,
            state_extraction_fn=self.state_extraction_fn,
            pause_every_n_steps=self.pause_every_n_steps,
        )
