import numpy as np

from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Dict

from vega_sim.api.market import MarketConfig
from vega_sim.environment.agent import Agent
from vega_sim.scenario.common.utils.price_process import (
    Granularity,
    get_historic_price_series,
)

from vega_sim.scenario.scenario import Scenario
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull

from vega_sim.scenario.configurable_market.agents import (
    ConfigurableMarketManager,
    PROPOSAL_PARTY,
    TERMINATION_PARTY,
    MAKER_PARTY,
    AUCTION_PARTY_A,
    AUCTION_PARTY_B,
    SENSITIVE_PARTY_A,
    SENSITIVE_PARTY_B,
    SENSITIVE_PARTY_C,
    INFORMED_PARTY,
)

from vega_sim.scenario.common.agents import (
    OpenAuctionPass,
    ExponentialShapedMarketMaker,
    PriceSensitiveMarketOrderTrader,
    InformedTrader,
    StateAgent,
    AtTheTouchMarketMaker,
)


class ConfigurableMarket(Scenario):
    def __init__(
        self,
        market_name: Optional[str] = None,
        market_code: Optional[str] = None,
        asset_name: Optional[str] = None,
        asset_dp: Optional[str] = None,
        num_steps: int = 120,
        granularity: Optional[Granularity] = Granularity.MINUTE,
        block_size: int = 1,
        block_length_seconds: int = 1,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, Dict[str, Agent]], Any]
        ] = None,
        settle_at_end: bool = True,
        price_process_fn: Optional[Callable] = None,
        pause_every_n_steps: Optional[int] = None,
    ):
        super().__init__(state_extraction_fn=state_extraction_fn)

        # Simulation settings
        self.num_steps = num_steps
        self.granularity = granularity
        self.block_size = block_size
        self.block_length_seconds = block_length_seconds
        self.settle_at_end = settle_at_end
        self.price_process_fn = price_process_fn
        self.pause_every_n_steps = pause_every_n_steps

        # Asset parameters
        self.asset_name = asset_name
        self.asset_decimal = asset_dp

        # Market parameters
        self.market_name = market_name
        self.market_code = market_code

    def _generate_price_process(
        self,
        random_state,
    ) -> list:
        start = "2021-07-01 00:00:00"

        start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")

        start = start + timedelta(days=int(random_state.choice(range(90))))

        end = start + timedelta(seconds=(self.num_steps * 1.1) * self.granularity.value)

        price_process = get_historic_price_series(
            product_id="ETH-USD",
            granularity=self.granularity,
            start=str(start),
            end=str(end),
            interpolation=f"{self.granularity.value}s",
        )

        return list(price_process)

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: str,
        market_config: Optional[MarketConfig] = None,
        random_state: Optional[np.random.RandomState] = None,
        **kwargs,
    ) -> Dict[str, StateAgent]:
        market_config = market_config if market_config is not None else MarketConfig()

        random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

        market_name = self.market_name
        asset_name = self.asset_name

        price_process = (
            self.price_process_fn()
            if self.price_process_fn is not None
            else self._generate_price_process(random_state=random_state)
        )

        market_manager = ConfigurableMarketManager(
            proposal_wallet_name=PROPOSAL_PARTY.wallet_name,
            proposal_key_name=PROPOSAL_PARTY.key_name,
            termination_wallet_name=TERMINATION_PARTY.wallet_name,
            termination_key_name=TERMINATION_PARTY.key_name,
            market_config=market_config,
            market_name=market_name,
            market_code=self.market_code,
            asset_dp=self.asset_decimal,
            asset_name=asset_name,
            settlement_price=price_process[-1] if self.settle_at_end else None,
        )

        shaped_mm = ExponentialShapedMarketMaker(
            wallet_name=MAKER_PARTY.wallet_name,
            key_name=MAKER_PARTY.key_name,
            price_process_generator=iter(price_process),
            initial_asset_mint=1e9,
            commitment_amount=1e6,
            market_name=market_name,
            asset_name=asset_name,
            market_decimal_places=market_config.decimal_places,
            asset_decimal_places=self.asset_decimal,
            num_steps=self.num_steps,
            kappa=0.3,
            num_levels=25,
            tick_spacing=1,
            inventory_upper_boundary=200,
            inventory_lower_boundary=-200,
            market_kappa=1,
            market_order_arrival_rate=10,
            state_update_freq=10,
        )

        at_the_touch_mm = AtTheTouchMarketMaker(
            key_name="AT_THE_TOUCH_MM",
            wallet_name="MM",
            initial_asset_mint=1e9,
            market_name=self.market_name,
            asset_name=self.asset_name,
            market_decimal_places=market_config.decimal_places,
            position_decimal_places=market_config.position_decimal_places,
            asset_decimal_places=self.asset_decimal,
            peg_offset=30 * 10 ** (-market_config.decimal_places),
            max_position=10 * 10 ** (-market_config.position_decimal_places),
            tag="a",
        )

        sensitive_mo_trader_a = PriceSensitiveMarketOrderTrader(
            wallet_name=SENSITIVE_PARTY_A.wallet_name,
            key_name=SENSITIVE_PARTY_A.key_name,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=1e10,
            buy_intensity=1,
            sell_intensity=1,
            price_half_life=10,
            price_process_generator=iter(price_process),
            base_order_size=1,
            tag="a",
        )

        sensitive_mo_trader_b = PriceSensitiveMarketOrderTrader(
            wallet_name=SENSITIVE_PARTY_B.wallet_name,
            key_name=SENSITIVE_PARTY_B.key_name,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=1e10,
            buy_intensity=10,
            sell_intensity=10,
            price_half_life=1,
            price_process_generator=iter(price_process),
            base_order_size=1,
            tag="b",
        )

        sensitive_mo_trader_c = PriceSensitiveMarketOrderTrader(
            wallet_name=SENSITIVE_PARTY_C.wallet_name,
            key_name=SENSITIVE_PARTY_C.key_name,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=1e10,
            buy_intensity=100,
            sell_intensity=100,
            price_half_life=0.1,
            price_process_generator=iter(price_process),
            base_order_size=1,
            tag="c",
        )

        auctionpass1 = OpenAuctionPass(
            wallet_name=AUCTION_PARTY_A.wallet_name,
            key_name=AUCTION_PARTY_A.key_name,
            side="SIDE_BUY",
            initial_asset_mint=1e9,
            initial_price=price_process[0],
            market_name=market_name,
            asset_name=asset_name,
            opening_auction_trade_amount=1,
            tag="1",
        )

        auctionpass2 = OpenAuctionPass(
            wallet_name=AUCTION_PARTY_B.wallet_name,
            key_name=AUCTION_PARTY_B.key_name,
            side="SIDE_SELL",
            initial_asset_mint=1e9,
            initial_price=price_process[0],
            market_name=market_name,
            asset_name=asset_name,
            opening_auction_trade_amount=1,
            tag="2",
        )

        info_trader = InformedTrader(
            wallet_name=INFORMED_PARTY.wallet_name,
            key_name=INFORMED_PARTY.key_name,
            price_process=price_process,
            market_name=market_name,
            asset_name=asset_name,
            initial_asset_mint=1e10,
            proportion_taken=0.1,
        )

        agents = [
            market_manager,
            shaped_mm,
            sensitive_mo_trader_a,
            sensitive_mo_trader_b,
            sensitive_mo_trader_c,
            auctionpass1,
            auctionpass2,
            info_trader,
            at_the_touch_mm,
        ]
        return {agent.name(): agent for agent in agents}

    def configure_environment(
        self, vega: VegaServiceNull, **kwargs
    ) -> MarketEnvironmentWithState:
        return MarketEnvironmentWithState(
            agents=list(self.agents.values()),
            n_steps=self.num_steps,
            step_length_seconds=self.granularity.value,
            random_agent_ordering=True,
            transactions_per_block=self.block_size,
            vega_service=vega,
            block_length_seconds=self.block_length_seconds,
            pause_every_n_steps=self.pause_every_n_steps,
        )
