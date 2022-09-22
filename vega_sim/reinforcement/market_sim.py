import argparse
import logging
from typing import List, Optional, Tuple
import os
import torch
import time

from vega_sim.environment.agent import Agent
from vega_sim.reinforcement.learning_agent import (
    Action,
    LearningAgent,
    LAMarketState,
    WALLET as LEARNING_WALLET,
)

from vega_sim.scenario.registry import IdealMarketMakerV2

from vega_sim.reinforcement.helpers import set_seed
from vega_sim.reinforcement.full_market_sim.utils.external_assetprice import RW_model
from vega_sim.reinforcement.full_market_sim.environments import RLMarketEnvironment
from vega_sim.null_service import VegaServiceNull

from vega_sim.reinforcement.plot import plot_simulation


def state_fn(
    service: VegaServiceNull, agents: List[Agent]
) -> Tuple[LAMarketState, Action]:
    learner = [a for a in agents if isinstance(a, LearningAgent)][0]
    return (learner.state(service), learner.latest_action)


def run_iteration(
    learning_agent: LearningAgent,
    step_tag: int,
    vega,
    market_name: str,
    run_with_console=False,
    pause_at_completion=False,
):
    scenario = IdealMarketMakerV2(
        market_decimal=3,
        asset_decimal=5,
        market_position_decimal=2,
        initial_price=1123.11,
        spread=0.002,
        lp_commitamount=20000,
        step_length_seconds=60,
        block_length_seconds=1,
        market_name=market_name,
        state_extraction_fn=state_fn,
    )
    env = scenario.set_up_background_market(
        vega=vega,
        tag=str(step_tag),
    )
    # env.agents.append[learning_agent]
    env.agents = env.agents + [learning_agent]

    learning_agent.set_market_tag(str(step_tag))

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
        default=2,
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

    # set market name
    market_name = "ETH:USD"

    # create the Learning Agent
    learning_agent = LearningAgent(
        device=device,
        discount_factor=0.8,
        logfile=logfile,
        num_levels=5,
        wallet_name=LEARNING_WALLET.name,
        wallet_pass=LEARNING_WALLET.passphrase,
        market_name=market_name,
    )

    if not args.evaluate:
        # Agent training / evaluation:
        with VegaServiceNull(
            warn_on_raw_data_access=False, run_with_console=False
        ) as vega:
            vega.wait_for_total_catchup()
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
                except:
                    print("Crashed in iteration {}".format(it))
                    raise Exception("crashed")

            learning_agent.save(args.results_dir)

    with VegaServiceNull(warn_on_raw_data_access=False, run_with_console=False) as vega:
        time.sleep(2)
        # EVALUATION OF AGENT
        learning_agent.load(args.results_dir)
        for it in range(10):
            learning_agent.clear_memory()
            result = run_iteration(
                learning_agent=learning_agent,
                step_tag=it,
                vega=vega,
                market_name=market_name,
                run_with_console=False,
                pause_at_completion=False,
            )
            plot_simulation(simulation=result, results_dir=args.results_dir, tag=it)
