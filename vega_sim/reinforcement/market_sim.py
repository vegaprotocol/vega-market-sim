import argparse
import cProfile
import logging
import os
from typing import List, Tuple

import torch
from vega_sim.environment.agent import Agent
from vega_sim.null_service import VegaServiceNull
from vega_sim.reinforcement.environments import run_iteration
from vega_sim.reinforcement.helpers import set_seed
from vega_sim.reinforcement.agents.market_order_agent import (
    WALLET as LEARNING_WALLET,
    Action,
    MarketOrderLearningAgent,
    LearningAgent,
    MarketState,
)
from vega_sim.reinforcement.plot import plot_simulation


def main(
    results_dir: str,
    evaluate_only: bool = False,
    max_learning_iterations: int = 10,
):
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    logfile = os.path.join(results_dir, "learning_agent.txt")

    # create the Learning Agent
    learning_agent = MarketOrderLearningAgent(
        device=device,
        discount_factor=0.8,
        logfile=logfile,
        num_levels=5,
        wallet_name=LEARNING_WALLET.name,
        wallet_pass=LEARNING_WALLET.passphrase,
    )

    if not evaluate_only:
        # Agent training / evaluation:
        with VegaServiceNull(
            warn_on_raw_data_access=False,
            run_with_console=False,
            retain_log_files=True,
            use_full_vega_wallet=False,
        ) as vega:
            # TRAINING OF AGENT
            for it in range(max_learning_iterations):
                # simulation of market to get some data
                with cProfile.Profile() as pr:
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
                                "initial_price": 100,
                                "sigma": 1,
                                "kappa": 10,
                                "spread": 0.1,
                            },
                        )
                        # Policy evaluation + Policy improvement
                        learning_agent.move_to_device()
                        learning_agent.policy_eval(batch_size=50, n_epochs=10)
                        learning_agent.policy_improvement(batch_size=50, n_epochs=10)
                    except Exception as e:
                        print("Crashed in iteration {}".format(it))
                        raise e
                    pr.dump_stats(f"rl{it}.prof")

            learning_agent.save(results_dir)

    with VegaServiceNull(warn_on_raw_data_access=False, run_with_console=False) as vega:
        # EVALUATION OF AGENT
        learning_agent.load(results_dir)
        for it in range(10):
            learning_agent.clear_memory()
            result = run_iteration(
                learning_agent=learning_agent,
                **{
                    "vega": vega,
                    "pause_at_completion": False,
                    "num_steps": 500,
                    "step_tag": it,
                    "block_size": 1,
                    "step_length_seconds": 1,
                    "initial_price": 100,
                    "sigma": 1,
                    "kappa": 10,
                    "spread": 0.1,
                },
            )
            plot_simulation(simulation=result, results_dir=results_dir, tag=it)


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
    main(
        results_dir=args.results_dir,
        evaluate_only=args.evaluate,
        max_learning_iterations=args.rl_max_it,
    )
