import logging
from vega_sim.reinforcement.agents.learning_agent import (
    WALLET as LEARNING_WALLET,
)

from vega_sim.reinforcement.agents.simple_agent import SimpleAgent

from vega_sim.scenario.registry import CurveMarketMaker
from vega_sim.scenario.common.agents import Snitch

from vega_sim.reinforcement.helpers import set_seed
from vega_sim.null_service import VegaServiceNull


def run_iteration(
    learning_agent: SimpleAgent,
    vega,
    market_name: str,
    asset_name: str,
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
        market_name=market_name,
        asset_name=asset_name,
        num_steps=50,
        random_agent_ordering=False,
        sigma=100,
    )

    scenario.agents = scenario.configure_agents(vega=vega, random_state=None)
    # add the learning agaent to the environment's list of agents
    learning_agent.price_process = scenario.price_process
    scenario.agents["learner"] = learning_agent

    scenario.agents["snitch"] = Snitch(
        agents=scenario.agents, additional_state_fn=scenario.state_extraction_fn
    )

    scenario.env = scenario.configure_environment(vega=vega)

    scenario.env.run(
        run_with_console=run_with_console,
        pause_at_completion=pause_at_completion,
    )

    result = scenario.get_additional_run_data()

    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # set seed for results replication
    set_seed(1)

    # set market name
    market_name = "ETH:USD"
    asset_name = "tDAI"

    # create the Learning Agent
    agent = SimpleAgent(
        wallet_name=LEARNING_WALLET.name,
        wallet_pass=LEARNING_WALLET.passphrase,
        initial_balance=100_000,
        market_name=market_name,
        asset_name=asset_name,
    )

    with VegaServiceNull(
        warn_on_raw_data_access=False, run_with_console=False, retain_log_files=True
    ) as vega:
        _ = run_iteration(
            learning_agent=agent,
            vega=vega,
            market_name=market_name,
            pause_at_completion=True,
            asset_name=asset_name,
        )
