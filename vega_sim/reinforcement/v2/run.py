import os
import logging
import json

from vega_sim.reinforcement.v2.agents.learning_agent import LearningAgent
from vega_sim.reinforcement.v2.agents.learning_agent_MO import LearningAgentFixedVol
from vega_sim.reinforcement.v2.agents.puppets import AgentType, NoAction
from vega_sim.reinforcement.v2.learning_environment import Environment
from vega_sim.reinforcement.v2.rewards import Reward
from vega_sim.reinforcement.v2.states import State, PriceStateWithFees
from vega_sim.scenario.registry import CurveMarketMaker

logger = logging.getLogger(__name__)


def run_training(
    agent_map: dict[str, LearningAgent],
    agent_type_map: dict[str, AgentType],
    agent_to_reward: dict[str, Reward],
    agent_to_state: dict[str, State],
    steps_per_iteration: int = 100,
    num_training_iterations: int = 1000,
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
        market_name="ETH",
        num_steps=500,
        random_agent_ordering=False,
        sigma=100,
        asset_name="DAI",
    )

    env = Environment(
        agents=agent_type_map,
        agent_to_reward=agent_to_reward,
        agent_to_state=agent_to_state,
        scenario=scenario,
    )
    env.reset()
    result_dict = env.step({name: NoAction for name in agent_map.keys()})
    pas = []
    for i in range(num_training_iterations):
        for _ in range(steps_per_iteration):
            actions = {
                name: agent_map[name].step(result.observation)
                for (name, result) in result_dict.items()
            }
            result_dict = env.step(actions)
            for agent_name, agent in agent_map.items():
                result_val = result_dict[agent_name]
                agent.update_memory(
                    state=result_val.observation,
                    action=actions[agent_name],
                    reward=result_val.reward,
                )
        for agent in agent_map.values():
            agent.learning_step()

        logger.info(f"Completed training iteration {i}")

        pa = env._vega.party_account(
            key_name="test_agent_learner",
            market_id=env._market_id,
        )
        pa2 = env._vega.party_account(
            key_name="test_agent_learner_2",
            market_id=env._market_id,
        )
        pas.append(sum(pa))
        with open("bals.json", "w") as f:
            json.dump(pas, f)

        logger.info(f"Learner ended with {sum(pa)}")
        logger.info(f"Learner 2 ended with {sum(pa2)}")

        env.reset()

    env.stop()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",
    )
    logfile_pol_imp = os.path.join("learning_pol_imp.csv")
    logfile_pol_eval = os.path.join("learning_pol_eval.csv")
    logfile_pnl = os.path.join("learning_pnl.csv")

    # set device
    device = "cpu"

    # create the Learning Agents
    agent_map = {
        "test_agent_learner": LearningAgentFixedVol(
            device=device,
            logfile_pol_imp=logfile_pol_imp,
            logfile_pol_eval=logfile_pol_eval,
            logfile_pnl=logfile_pnl,
            discount_factor=0.8,
            num_levels=5,
            inventory_penalty=0.1,
        ),
        "test_agent_learner_2": LearningAgentFixedVol(
            device=device,
            logfile_pol_imp=logfile_pol_imp + "_2",
            logfile_pol_eval=logfile_pol_eval + "_2",
            logfile_pnl=logfile_pnl,
            discount_factor=0.8,
            num_levels=5,
            inventory_penalty=0.1,
        ),
    }

    agents = {}
    agent_to_reward = {}
    agent_to_state = {}

    for tal in agent_map.keys():
        agents[tal] = AgentType.MARKET_ORDER
        agent_to_reward[tal] = Reward.PNL
        agent_to_state[tal] = PriceStateWithFees

    run_training(
        agent_map=agent_map,
        agent_type_map=agents,
        agent_to_reward=agent_to_reward,
        agent_to_state=agent_to_state,
    )


if __name__ == "__main__":
    main()
