import argparse
import logging
from typing import List, Optional, Tuple
import os
import torch
import time

from vega_sim.environment.agent import Agent
from vega_sim.reinforcement.la_market_state import (
    LAMarketState, 
    AbstractAction
)
from vega_sim.reinforcement.learning_agent import (
    LearningAgent,
    WALLET as LEARNING_WALLET,
)
from vega_sim.reinforcement.learning_agent_MO_with_vol import LearningAgentWithVol

from vega_sim.scenario.registry import IdealMarketMakerV2
from vega_sim.scenario.registry import CurveMarketMaker

from vega_sim.reinforcement.helpers import set_seed
from vega_sim.reinforcement.full_market_sim.utils.external_assetprice import RW_model
from vega_sim.reinforcement.full_market_sim.environments import RLMarketEnvironment
from vega_sim.null_service import VegaServiceNull

from vega_sim.reinforcement.plot import plot_learning, plot_pnl, plot_simulation


def state_fn(
    service: VegaServiceNull, agents: List[Agent]
) -> Tuple[LAMarketState, AbstractAction]:
    learner = [a for a in agents if isinstance(a, LearningAgent)][0]
    return (learner.latest_state, learner.latest_action)


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
    parser.add_argument("--device", default=0, type=int)
    parser.add_argument("--results_dir", default="numerical_results", type=str)
    parser.add_argument(
        "--evaluate",
        default=0,
        type=int,
        help="If true, do not train and directly run the chosen number of evaluations",
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
    logfile_pol_imp = os.path.join(args.results_dir, "learning_pol_imp.csv")
    logfile_pol_eval = os.path.join(args.results_dir, "learning_pol_eval.csv")
    logfile_pnl = os.path.join(args.results_dir, "learning_pnl.csv")

    # set seed for results replication
    set_seed(1)

    # set market name
    market_name = "ETH:USD"
    position_decimals=2
    initial_price=1000

    # create the Learning Agent
    learning_agent = LearningAgentWithVol(
        device=device,
        logfile_pol_imp=logfile_pol_imp,
        logfile_pol_eval=logfile_pol_eval,
        logfile_pnl=logfile_pnl,
        discount_factor=0.99,
        num_levels=2,
        wallet_name=LEARNING_WALLET.name,
        wallet_pass=LEARNING_WALLET.passphrase,
        initial_balance=100000,
        market_name=market_name,
        position_decimals=position_decimals,
        exploitation=0.0
    )

    with VegaServiceNull(
            warn_on_raw_data_access=False, run_with_console=False, retain_log_files=False
    ) as vega:
        vega.wait_for_total_catchup()

        if args.evaluate == 0:
        # TRAINING OF AGENT
            for it in range(args.rl_max_it):
                # simulation of market to get some data
                try:
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
                    learning_agent.policy_eval(batch_size=50, n_epochs=10)
                    learning_agent.policy_improvement(batch_size=50, n_epochs=10)
                    learning_agent.lerningIteration += 1
                except:
                    print("Crashed in iteration {}".format(it))
                    raise Exception("crashed")

            learning_agent.save(args.results_dir)
            plot_learning(
                results_dir=args.results_dir, 
                logfile_pol_eval=logfile_pol_eval, 
                logfile_pol_imp=logfile_pol_imp
                )
            
        else: 
            # EVALUATION OF AGENT
            learning_agent.load(args.results_dir)
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
                plot_simulation(simulation=result, results_dir=args.results_dir, tag=it)
        
        plot_pnl(results_dir=args.results_dir, logfile_pnl=logfile_pnl)
                
