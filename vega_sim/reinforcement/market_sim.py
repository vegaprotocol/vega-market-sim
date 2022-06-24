import argparse
import logging
from typing import List, Optional, Tuple
import os
import torch
import time


from vega_sim.reinforcement.learning_agent import (
    Action,
    LearningAgent,
    MarketState,
    WALLET as LEARNING_WALLET,
)
from vega_sim.environment.agent import Agent

from vega_sim.reinforcement.helpers import set_seed
from vega_sim.reinforcement.full_market_sim.utils.external_assetprice import RW_model
from vega_sim.reinforcement.full_market_sim.environments import RLMarketEnvironment
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.ideal_market_maker.agents import (
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
from .plot import plot_simulation


def state_fn(
    service: VegaServiceNull, agents: List[Agent]
) -> Tuple[MarketState, Action]:
    learner = [a for a in agents if isinstance(a, LearningAgent)][0]
    return (learner.state(service), learner.latest_action)


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
    step_length_seconds: Optional[int] = None,
) -> RLMarketEnvironment:
    _, price_process = RW_model(
        T=num_steps * dt,
        dt=dt,
        mdp=market_decimal,
        sigma=sigma,
        Midprice=initial_price,
    )

    learning_agent.price_process = price_process

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
        Lambda=Lambda,
        q_upper=q_upper,
        q_lower=q_lower,
        alpha=alpha,
        phi=phi,
        spread=spread,
        block_size=block_size,
        state_extraction_freq=state_extraction_freq,
        step_length_seconds=step_length_seconds,
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num-procs", default=1, type=int)
    parser.add_argument(
        "--rl-max-it",
        default=10,
        type=int,
        help="Number of iterations of policy improvement + policy iterations",
    )
    parser.add_argument("--use_cuda", action="store_true", default=False)
    parser.add_argument("--device", default=0, type=int)
    parser.add_argument("--results_dir", default="numerical_results", type=str)
    parser.add_argument(
        "--evaluate",
        action="store_true",
        default=False,
        help="If true, do not train and directly evaluate",
    )
    args = parser.parse_args()

    # set device
    if torch.cuda.is_available() and args.use_cuda:
        device = "cuda:{}".format(args.device)
    else:
        device = "cpu"

    # create results dir
    if not os.path.exists(args.results_dir):
        os.makedirs(args.results_dir)
    logfile = os.path.join(args.results_dir, "learning_agent.txt")

    # set seed for results replication
    set_seed(1)

    # create the Learning Agent
    learning_agent = LearningAgent(
        device=device,
        discount_factor=0.8,
        logfile=logfile,
        num_levels=5,
        wallet_name=LEARNING_WALLET.name,
        wallet_pass=LEARNING_WALLET.passphrase,
    )

    if not args.evaluate:
        # Agent training / evaluation:
        with VegaServiceNull(
            warn_on_raw_data_access=False, run_with_console=False
        ) as vega:
            time.sleep(2)
            # TRAINING OF AGENT
            for it in range(args.rl_max_it):
                # simulation of market to get some data
                try:
                    learning_agent.move_to_cpu()
                    _ = run_iteration(
                        learning_agent=learning_agent,
                        **{
                            "vega": vega,
                            "pause_at_completion": False,
                            "num_steps": 100,
                            "step_tag": it,
                            "block_size": 50,
                        },
                    )
                    # Policy evaluation + Policy improvement
                    learning_agent.move_to_device()
                    learning_agent.policy_eval(batch_size=50, n_epochs=10)
                    learning_agent.policy_improvement(batch_size=50, n_epochs=10)
                except:
                    print("Crashed in iteration {}".format(it))
                    raise Exception("crashed")

            learning_agent.save(args.results_dir)

    with VegaServiceNull(warn_on_raw_data_access=False, run_with_console=True) as vega:
        time.sleep(2)
        # EVALUATION OF AGENT
        learning_agent.load(args.results_dir)
        for it in range(10):
            learning_agent.clear_memory()
            result = run_iteration(
                learning_agent=learning_agent,
                **{
                    "vega": vega,
                    "pause_at_completion": False,
                    "num_steps": 100,
                    "step_tag": it,
                    "block_size": 1,
                    "step_length_seconds": 60,
                },
            )
            plot_simulation(simulation=result, results_dir=args.results_dir, tag=it)
