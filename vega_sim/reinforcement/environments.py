from typing import List, Optional, Tuple

from vega_sim.environment.agent import Agent
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull
from vega_sim.reinforcement.agents.learning_agent import (
    LearningAgent,
    MarketState,
    Action,
)
from vega_sim.scenario.common.agents import (
    AUCTION1_WALLET,
    AUCTION2_WALLET,
    BACKGROUND_MARKET,
    TERMINATE_WALLET,
    TRADER_WALLET,
    BackgroundMarket,
    MarketManager,
    MarketOrderTrader,
    OpenAuctionPass,
    WalletConfig,
)
from vega_sim.scenario.common.price_process import random_walk
from vega_sim.service import VegaService

MANAGER_WALLET = WalletConfig("manager", "manager")


def state_fn(
    service: VegaServiceNull, agents: List[Agent]
) -> Tuple[MarketState, Action]:
    learner = [a for a in agents if isinstance(a, LearningAgent)][0]
    return (learner.state(service), learner.latest_action)


class RLMarketEnvironment(MarketEnvironmentWithState):
    def __init__(self, agents: List[Agent], *args, **kwargs):
        super().__init__(agents, *args, **kwargs)
        self._base_agents = agents

    def add_learning_agent(self, agent: LearningAgent):
        self.learning_agent = agent
        self.agents = self._base_agents + [agent]

    def step(self, vega: VegaService):
        super().step(vega=vega)

        state = self.state_func(vega)
        # Learning agent
        self.learning_agent.step(state, random=False)


def set_up_background_market(
    vega: VegaServiceNull,
    learning_agent: LearningAgent,
    tag: str = "",
    num_steps: int = 120,
    dt: float = 1 / 60 / 24 / 365.25,
    market_decimal: int = 5,
    asset_decimal: int = 5,
    initial_price: float = 100,
    sigma: float = 1,
    kappa: float = 1.01,
    spread: float = 0.1,
    block_size: int = 1,
    state_extraction_freq: int = 1,
    step_length_seconds: Optional[int] = None,
) -> RLMarketEnvironment:
    price_process = random_walk(
        num_steps=num_steps + 1,
        sigma=sigma,
        drift=0,
        starting_price=initial_price,
        decimal_precision=market_decimal,
        trim_to_min=0.1,
    )

    market_name = f"BTC:DAI_{tag}"
    asset_name = f"tDAI{tag}"

    learning_agent.price_process = price_process

    market_manager = MarketManager(
        wallet_name=MANAGER_WALLET.name,
        wallet_pass=MANAGER_WALLET.passphrase,
        terminate_wallet_name=TERMINATE_WALLET.name,
        terminate_wallet_pass=TERMINATE_WALLET.passphrase,
        market_name=market_name,
        market_decimal=market_decimal,
        asset_decimal=asset_decimal,
        asset_name=asset_name,
        market_position_decimal=2,
        commitment_amount=10000,
        tag=str(tag),
    )

    background_market = BackgroundMarket(
        BACKGROUND_MARKET.name,
        BACKGROUND_MARKET.passphrase,
        market_name=market_name,
        asset_name=asset_name,
        price_process=price_process,
        spread=spread,
        order_distribution_kappa=kappa,
        tag=str(tag),
    )

    tradingbot = MarketOrderTrader(
        market_name=market_name,
        asset_name=asset_name,
        wallet_name=TRADER_WALLET.name,
        wallet_pass=TRADER_WALLET.passphrase,
        tag=str(tag),
    )

    auctionpass1 = OpenAuctionPass(
        wallet_name=AUCTION1_WALLET.name,
        wallet_pass=AUCTION1_WALLET.passphrase,
        market_name=market_name,
        asset_name=asset_name,
        side="SIDE_BUY",
        initial_price=initial_price,
        tag=str(tag),
    )

    auctionpass2 = OpenAuctionPass(
        wallet_name=AUCTION2_WALLET.name,
        wallet_pass=AUCTION2_WALLET.passphrase,
        market_name=market_name,
        asset_name=asset_name,
        side="SIDE_SELL",
        initial_price=initial_price,
        tag=str(tag),
    )

    env = RLMarketEnvironment(
        agents=[
            market_manager,
            background_market,
            tradingbot,
            auctionpass1,
            auctionpass2,
        ],
        n_steps=num_steps,
        transactions_per_block=block_size,
        vega_service=vega,
        state_extraction_fn=state_fn,
        state_extraction_freq=state_extraction_freq,
        step_length_seconds=step_length_seconds,
    )
    return env


def run_iteration(
    learning_agent: LearningAgent,
    step_tag: int,
    num_steps: int = 120,
    dt: float = 1 / 60 / 24 / 365.25,
    market_decimal: int = 5,
    asset_decimal: int = 5,
    initial_price: float = 100,
    sigma: float = 20,
    kappa: float = 1.01,
    spread: float = 0.1,
    block_size: int = 1,
    state_extraction_freq: int = 1,
    run_with_console: bool = False,
    pause_at_completion: bool = False,
    step_length_seconds: Optional[int] = None,
    vega: Optional[VegaServiceNull] = None,
):
    env = set_up_background_market(
        vega=vega,
        tag=str(step_tag),
        num_steps=num_steps,
        dt=dt,
        market_decimal=market_decimal,
        asset_decimal=asset_decimal,
        initial_price=initial_price,
        sigma=sigma,
        kappa=kappa,
        spread=spread,
        block_size=block_size,
        state_extraction_freq=state_extraction_freq,
        step_length_seconds=step_length_seconds,
        learning_agent=learning_agent,
    )

    learning_agent.set_market_tag(str(step_tag))
    env.add_learning_agent(learning_agent)

    result = env.run(
        run_with_console=run_with_console,
        pause_at_completion=pause_at_completion,
    )
    # Update the memory of the learning agent with the simulated data
    learning_agent.update_memory(result)
    return result
