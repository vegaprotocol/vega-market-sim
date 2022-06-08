import argparse
import logging
from multiprocessing import Pool
import datetime
from typing import List, Optional, Tuple
from reinforcement.helpers import states_to_sarsa

from reinforcement.learning_agent import (
    Action,
    LearningAgent,
    MarketState,
    WALLET as LEARNING_WALLET,
)
from vega_sim.environment.agent import Agent

from reinforcement.full_market_sim.utils.external_assetprice import RW_model
from reinforcement.full_market_sim.environments import RLMarketEnvironment
from vega_sim.null_service import VegaServiceNull
from reinforcement.full_market_sim.agents import (
    MM_WALLET,
    TERMINATE_WALLET,
    TRADER_WALLET,
    RANDOM_WALLET,
    AUCTION1_WALLET,
    AUCTION2_WALLET,
    OptimalMarketMaker,
    MarketOrderTrader,
    LimitOrderTrader,
    OpenAuctionPass,
)


def state_fn(
    service: VegaServiceNull, agents: List[Agent]
) -> Tuple[MarketState, Action]:
    learner = [a for a in agents if isinstance(a, LearningAgent)][0]
    return (learner.latest_state, learner.latest_action)


def set_up_background_market(
    vega: VegaServiceNull,
    tag: str = "",
    num_steps: int = 120,
    dt: float = 1 / 60 / 24 / 365.25,
    market_decimal: int = 5,
    asset_decimal: int = 5,
    initial_price: float = 0.3,
    sigma: float = 1,
    kappa: float = 500,
    Lambda: float = 5,
    q_upper: int = 20,
    q_lower: int = -20,
    alpha: float = 10**-4,
    phi: float = 5 * 10**-6,
    spread: float = 0.00002,
    block_size: int = 1,
    state_extraction_freq: int = 1,
) -> RLMarketEnvironment:
    _, price_process = RW_model(
        T=num_steps * dt,
        dt=dt,
        mdp=market_decimal,
        sigma=sigma,
        Midprice=initial_price,
    )

    market_maker = OptimalMarketMaker(
        wallet_name=MM_WALLET.name,
        wallet_pass=MM_WALLET.passphrase,
        terminate_wallet_name=TERMINATE_WALLET.name,
        terminate_wallet_pass=TERMINATE_WALLET.passphrase,
        price_processs=price_process,
        spread=spread,
        num_steps=num_steps,
        market_order_arrival_rate=Lambda,
        pegged_order_fill_rate=kappa,
        inventory_upper_boundary=q_upper,
        inventory_lower_boundary=q_lower,
        terminal_penalty_parameter=alpha,
        running_penalty_parameter=phi,
        asset_decimal=asset_decimal,
        market_decimal=market_decimal,
        tag=str(tag),
    )

    tradingbot = MarketOrderTrader(
        wallet_name=TRADER_WALLET.name,
        wallet_pass=TRADER_WALLET.passphrase,
        tag=str(tag),
    )

    randomtrader = LimitOrderTrader(
        wallet_name=RANDOM_WALLET.name,
        wallet_pass=RANDOM_WALLET.passphrase,
        price_process=price_process,
        spread=spread,
        initial_price=initial_price,
        asset_decimal=asset_decimal,
        market_decimal=market_decimal,
        tag=str(tag),
    )

    auctionpass1 = OpenAuctionPass(
        wallet_name=AUCTION1_WALLET.name,
        wallet_pass=AUCTION1_WALLET.passphrase,
        side="SIDE_BUY",
        initial_price=initial_price,
        tag=str(tag),
    )

    auctionpass2 = OpenAuctionPass(
        wallet_name=AUCTION2_WALLET.name,
        wallet_pass=AUCTION2_WALLET.passphrase,
        side="SIDE_SELL",
        initial_price=initial_price,
        tag=str(tag),
    )

    env = RLMarketEnvironment(
        base_agents=[
            market_maker,
            tradingbot,
            randomtrader,
            auctionpass1,
            auctionpass2,
        ],
        n_steps=num_steps,
        transactions_per_block=block_size,
        vega_service=vega,
        state_extraction_fn=state_fn,
        state_extraction_freq=state_extraction_freq,
    )
    return env


def main(
    num_steps: int = 120,
    dt: float = 1 / 60 / 24 / 365.25,
    market_decimal: int = 5,
    asset_decimal: int = 5,
    initial_price: float = 0.3,
    sigma: float = 1,
    kappa: float = 500,
    Lambda: float = 5,
    q_upper: int = 20,
    q_lower: int = -20,
    alpha: float = 10**-4,
    phi: float = 5 * 10**-6,
    spread: float = 0.00002,
    block_size: int = 1,
    state_extraction_freq: int = 1,
    run_with_console: bool = False,
    pause_at_completion: bool = False,
    vega: Optional[VegaServiceNull] = None,
):

    learning_agent = LearningAgent(
        wallet_name=LEARNING_WALLET.name, wallet_pass=LEARNING_WALLET.passphrase
    )

    for i in range(50):
        env = set_up_background_market(
            vega=vega,
            tag=i,
            num_steps=num_steps,
            dt=dt,
            market_decimal=market_decimal,
            asset_decimal=asset_decimal,
            initial_price=initial_price,
            sigma=sigma,
            kappa=kappa,
            Lambda=Lambda,
            q_upper=q_upper,
            q_lower=q_lower,
            alpha=alpha,
            phi=phi,
            spread=spread,
            block_size=block_size,
            state_extraction_freq=state_extraction_freq,
        )

        learning_agent.set_market_tag(str(i))
        env.add_learning_agent(learning_agent)

        result = env.run(
            run_with_console=run_with_console,
            pause_at_completion=pause_at_completion,
        )
    sarsa = states_to_sarsa(result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num-procs", default=1, type=int)
    args = parser.parse_args()

    if args.num_procs > 1:
        ress = []
        vega_services: List[VegaServiceNull] = []
        with Pool(args.num_procs) as p:
            start = datetime.datetime.now()
            for _ in range(args.num_procs):
                vega_service = VegaServiceNull(warn_on_raw_data_access=False)
                vega_service.start(block_on_startup=True)
                vega_services.append(vega_service)
                ress.append(
                    p.apply_async(
                        main,
                        kwds={
                            "vega": vega_service.clone(),
                        },
                    )
                )

            [res.get() for res in ress]
            print(f"Run took {(datetime.datetime.now() - start).seconds}s")
            for vega_service in vega_services:
                vega_service.stop()
    else:
        with VegaServiceNull(
            warn_on_raw_data_access=False,
            run_with_console=True,
            use_full_vega_wallet=False,
            block_duration="1s",
        ) as vega:
            main(
                **{"vega": vega, "pause_at_completion": False, "num_steps": 120},
            )
