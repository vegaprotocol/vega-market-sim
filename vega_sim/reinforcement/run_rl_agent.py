import argparse
import logging
import os
from logging import getLogger

import torch
from vega_sim.null_service import VegaServiceNull
from vega_sim.reinforcement.agents.learning_agent import WALLET as LEARNING_WALLET
from vega_sim.reinforcement.agents.learning_agent import LearningAgent, state_fn
from vega_sim.reinforcement.agents.learning_agent_heuristic import (
    LearningAgentHeuristic,
)
from vega_sim.reinforcement.agents.learning_agent_MO import LearningAgentFixedVol
from vega_sim.reinforcement.agents.learning_agent_MO_with_vol import (
    LearningAgentWithVol,
)
from vega_sim.reinforcement.helpers import set_seed
from vega_sim.reinforcement.plot import plot_learning, plot_pnl, plot_simulation
from vega_sim.scenario.registry import CurveMarketMaker
from vega_sim.scenario.common.agents import Snitch

logger = getLogger(__name__)


def run_iteration(
    learning_agent: LearningAgent,
    step_tag: int,
    vega: VegaServiceNull,
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

    scenario.agents = scenario.configure_agents(
        vega=vega, tag=str(step_tag), random_state=None
    )
    # add the learning agaent to the environment's list of agents
    learning_agent.set_market_tag(str(step_tag))
    learning_agent.price_process = scenario.price_process
    scenario.agents["learner"] = learning_agent

    scenario.agents["snitch"] = Snitch(
        agents=scenario.agents, additional_state_fn=scenario.state_extraction_fn
    )

    scenario.env = scenario.configure_environment(
        vega=vega,
        tag=str(step_tag),
    )

    scenario.env.run(
        run_with_console=run_with_console,
        pause_at_completion=pause_at_completion,
    )

    result = scenario.get_additional_run_data()

    # Update the memory of the learning agent with the simulated data
    learning_agent.update_memory(result)

    return result


def _run(
    max_iterations: int,
    results_dir: str = "numerical_results",
    resume_training: bool = False,
    evaluate_only: bool = False,
    plot_every_step: bool = False,
    device: str = "cpu",
):
    # set seed for results replication
    set_seed(1)

    # set market name
    market_name = "ETH:USD"
    position_decimals = 2

    logfile_pol_imp = os.path.join(results_dir, "learning_pol_imp.csv")
    logfile_pol_eval = os.path.join(results_dir, "learning_pol_eval.csv")
    logfile_pnl = os.path.join(results_dir, "learning_pnl.csv")

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

        if not evaluate_only:
            logger.info(f"Running training for {max_iterations} iterations")
            # TRAINING OF AGENT
            if resume_training:
                logger.info("Loading neural net weights from: " + results_dir)
                learning_agent.load(results_dir)
            else:
                with open(logfile_pol_imp, "w") as f:
                    f.write("iteration,loss\n")
                with open(logfile_pol_eval, "w") as f:
                    f.write("iteration,loss,kl_coeff_disc,kl_coeff_cont\n")
                with open(logfile_pnl, "w") as f:
                    f.write("iteration,pnl\n")

            for it in range(max_iterations):
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
                learning_agent.save(results_dir)

                if plot_every_step:
                    plot_learning(
                        results_dir=results_dir,
                        logfile_pol_eval=logfile_pol_eval,
                        logfile_pol_imp=logfile_pol_imp,
                    )

        else:
            # EVALUATION OF AGENT
            logger.info("Loading neural net weights from: " + args.results_dir)
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
        logger.warn(
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

    _run(
        max_iterations=args.rl_max_it,
        results_dir=args.results_dir,
        resume_training=args.resume_training,
        evaluate_only=args.evaluate,
        plot_every_step=args.plot_every_step,
        device=device,
    )
