import argparse
import logging
from multiprocessing import Pool
import datetime
from typing import List, Optional, Tuple
import os
import torch
import torch.nn as nn
import time


from reinforcement.learning_agent import (
    Action,
    LearningAgent,
    MarketState,
    WALLET as LEARNING_WALLET,
)
from vega_sim.environment.agent import Agent

from reinforcement.full_market_sim.utils.external_assetprice import RW_model
from reinforcement.full_market_sim.environments import MarketEnvironmentforMMsim
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


def main(
    learning_agent: LearningAgent,
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
    )

    tradingbot = MarketOrderTrader(
        wallet_name=TRADER_WALLET.name,
        wallet_pass=TRADER_WALLET.passphrase,
    )

    randomtrader = LimitOrderTrader(
        wallet_name=RANDOM_WALLET.name,
        wallet_pass=RANDOM_WALLET.passphrase,
        price_process=price_process,
        spread=spread,
        initial_price=initial_price,
        asset_decimal=asset_decimal,
        market_decimal=market_decimal,
    )

    auctionpass1 = OpenAuctionPass(
        wallet_name=AUCTION1_WALLET.name,
        wallet_pass=AUCTION1_WALLET.passphrase,
        side="SIDE_BUY",
        initial_price=initial_price,
    )

    auctionpass2 = OpenAuctionPass(
        wallet_name=AUCTION2_WALLET.name,
        wallet_pass=AUCTION2_WALLET.passphrase,
        side="SIDE_SELL",
        initial_price=initial_price,
    )

    #learning_agent = LearningAgent(
    #    wallet_name=LEARNING_WALLET.name, wallet_pass=LEARNING_WALLET.passphrase
    #)

    env = MarketEnvironmentforMMsim(
        agents=[
            market_maker,
            tradingbot,
            randomtrader,
            auctionpass1,
            auctionpass2,
            learning_agent,
        ],
        n_steps=num_steps,
        transactions_per_block=block_size,
        vega_service=vega,
        state_extraction_fn=state_fn,
        state_extraction_freq=state_extraction_freq,
    )
    
    result = env.run(
        run_with_console=run_with_console,
        pause_at_completion=pause_at_completion,
    )
    #sarsa = states_to_sarsa(result)
    # Update the memory of the learning agent with the simulated data
    learning_agent.update_memory(result)
    




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num-procs", default=1, type=int)
    parser.add_argument("--rl-max-it", default=10, type=int, help="Number of iterations of policy improvement + policy iterations")
    parser.add_argument("--use_cuda", action='store_true', default=False)
    parser.add_argument("--device", default=0, type=int)
    parser.add_argument("--results_dir", default='numerical_results', type=str)
    args = parser.parse_args()

    if torch.cuda.is_available() and args.use_cuda:
        device = "cuda:{}".format(args.device)
    else:
        device = "cpu"
    
    if not os.path.exists(args.results_dir):
        os.makedirs(args.results_dir)
    logfile = os.path.join(args.results_dir, "learning_agent.txt")

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
        # create the Learning Agent
        learning_agent = LearningAgent(
            device=device,
            discount_factor=0.8,
            logfile=logfile,
            num_levels=5,
            wallet_name=LEARNING_WALLET.name, 
            wallet_pass=LEARNING_WALLET.passphrase
        )
        # Agent training:
        for it in range(args.rl_max_it):
            # simulation of market to get some data
            learning_agent.move_to_cpu()
            with VegaServiceNull(
                warn_on_raw_data_access=False, run_with_console=False
            ) as vega:
                time.sleep(2)
                main(
                    learning_agent = learning_agent, 
                    **{"vega": vega, "pause_at_completion": False, "num_steps": 10},
                )
            # Policy evaluation + Policy improvement
            learning_agent.move_to_device()
            learning_agent.policy_eval(batch_size = 50, n_epochs = 10)
            learning_agent.policy_improvement(batch_size = 50, n_epochs = 10)
