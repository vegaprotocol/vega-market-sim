import argparse
import logging
from typing import List, Optional, Tuple
import os
import torch
import time


from vega_sim.reinforcement.la_market_state import LAMarketState, AbstractAction
from vega_sim.reinforcement.agents.learning_agent import (
    LearningAgent,
    WALLET as LEARNING_WALLET,
    state_fn,
)
from vega_sim.reinforcement.agents.learning_agent_MO_with_vol import (
    LearningAgentWithVol,
)
from vega_sim.reinforcement.agents.learning_agent_MO import LearningAgentFixedVol
from vega_sim.reinforcement.agents.learning_agent_heuristic import (
    LearningAgentHeuristic,
)

from vega_sim.scenario.registry import IdealMarketMakerV2
from vega_sim.scenario.registry import CurveMarketMaker

from vega_sim.reinforcement.helpers import set_seed
from vega_sim.null_service import VegaServiceNull

from vega_sim.reinforcement.plot import plot_learning, plot_pnl, plot_simulation


def run_iteration(
    learning_agent: LearningAgent,
    step_tag: int,
    vega,
    market_name: str,
    run_with_console=False,
    pause_at_completion=False,
):
    scenario = CurveMarketMaker(
        market_decimal=3,
        asset_decimal=5,
        market_position_decimal=2,
        initial_price=1000.0,
        lp_commitamount=100000,
        initial_asset_mint=1e8,
        step_length_seconds=1,
        block_length_seconds=1,
        buy_intensity=5,
        sell_intensity=5,
        state_extraction_fn=state_fn,
        market_name=market_name,
        num_steps=50,
        random_agent_ordering=False,
        sigma=100,
    )
    env = scenario.set_up_background_market(
        vega=vega,
        tag=str(step_tag),
    )
    # add the learning agaent to the environement's list of agents
    env.agents = env.agents + [learning_agent]

    learning_agent.set_market_tag(str(step_tag))
    learning_agent.price_process = scenario.price_process

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
    parser.add_argument("-n", "--num-procs", default=6, type=int)
    parser.add_argument(
        "--rl-max-it",
        default=1,
        type=int,
        help="Number of iterations of policy improvement + policy iterations",
    )
    parser.add_argument("--use_cuda", action="store_true", default=False)
    parser.add_argument("--use_mps", action="store_true", default=False)
    parser.add_argument("--device", default=0, type=int)
    parser.add_argument("--results_dir", default="numerical_results", type=str)
    parser.add_argument(
        "--evaluate",
        default=0,
        type=int,
        help="If true, do not train and directly run the chosen number of evaluations",
    )
    parser.add_argument("--resume_training", action="store_true")
    parser.add_argument("--plot_every_step", action="store_true")
    parser.add_argument("--plot_only", action="store_true")

    args = parser.parse_args()

    # set device
    if torch.cuda.is_available() and args.use_cuda:
        device = "cuda:{}".format(args.device)
    elif torch.backends.mps.is_available() and args.use_mps:
        device = torch.device("mps")
        print(
            "WARNING: as of today this will likely crash due to mps not implementing"
            " all required functionality."
        )
    else:
        device = "cpu"

    # create results dir
    if not os.path.exists(args.results_dir):
        os.makedirs(args.results_dir)
    logfile_pol_imp = os.path.join(args.results_dir, "learning_pol_imp.csv")
    logfile_pol_eval = os.path.join(args.results_dir, "learning_pol_eval.csv")
    logfile_pnl = os.path.join(args.results_dir, "learning_pnl.csv")

    if args.plot_only:
        plot_learning(
            results_dir=args.results_dir,
            logfile_pol_eval=logfile_pol_eval,
            logfile_pol_imp=logfile_pol_imp,
        )
        plot_pnl(results_dir=args.results_dir, logfile_pnl=logfile_pnl)
        exit(0)

    # set seed for results replication
    set_seed(1)

    # set market name
    market_name = "ETH:USD"
    position_decimals = 2
    initial_price = 1000

    # create the Learning Agent
    learning_agent = LearningAgentFixedVol(
        device=device,
        logfile_pol_imp=logfile_pol_imp,
        logfile_pol_eval=logfile_pol_eval,
        logfile_pnl=logfile_pnl,
        discount_factor=0.8,
        num_levels=1,
        wallet_name=LEARNING_WALLET.name,
        wallet_pass=LEARNING_WALLET.passphrase,
        initial_balance=100000,
        market_name=market_name,
        position_decimals=position_decimals,
        inventory_penalty=0.1,
    )

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=False,
        retain_log_files=True,
        store_transactions=True,
    ) as vega:
        vega.wait_for_total_catchup()

        if args.evaluate == 0:
            # TRAINING OF AGENT
            if args.resume_training == True:
                print("Loading neural net weights from: " + args.results_dir)
                learning_agent.load(args.results_dir)
            else:
                with open(logfile_pol_imp, "w") as f:
                    f.write("iteration,loss\n")
                with open(logfile_pol_eval, "w") as f:
                    f.write("iteration,loss,kl_coeff_disc,kl_coeff_cont\n")
                with open(logfile_pnl, "w") as f:
                    f.write("iteration,pnl\n")

            for it in range(args.rl_max_it):
                # simulation of market to get some data

                learning_agent.move_to_cpu()
                _ = run_iteration(
                    learning_agent=learning_agent,
                    step_tag=it,
                    vega=vega,
                    market_name=market_name,
                    run_with_console=False,
                    pause_at_completion=False,
                )

                # Policy evaluation + Policy improvement
                learning_agent.move_to_device()
                learning_agent.policy_eval(batch_size=20000, n_epochs=10)
                learning_agent.policy_improvement(batch_size=100_000, n_epochs=10)

                # save in case environment chooses to crash
                learning_agent.save(args.results_dir)

                if args.plot_every_step:
                    plot_learning(
                        results_dir=args.results_dir,
                        logfile_pol_eval=logfile_pol_eval,
                        logfile_pol_imp=logfile_pol_imp,
                    )

        else:
            # EVALUATION OF AGENT
            print("Loading neural net weights from: " + args.results_dir)
            learning_agent.load(args.results_dir)
            learning_agent.lerningIteration = 0
            with open(logfile_pnl, "w") as f:
                f.write("iteration,pnl\n")

            for it in range(args.evaluate):
                learning_agent.clear_memory()
                learning_agent.exploitation = 1.0

                result = run_iteration(
                    learning_agent=learning_agent,
                    step_tag=it,
                    vega=vega,
                    market_name=market_name,
                    run_with_console=False,
                    pause_at_completion=False,
                )
                if args.plot_every_step:
                    plot_simulation(
                        simulation=result, results_dir=args.results_dir, tag=it
                    )

                learning_agent.lerningIteration += 1
