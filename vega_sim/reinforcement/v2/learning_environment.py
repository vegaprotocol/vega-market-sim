from typing import Dict, Type, Optional
from dataclasses import dataclass
from vega_sim.reinforcement.v2.agents.puppets import (
    AGENT_TYPE_TO_AGENT,
    AgentType,
    MarketOrderAction,
    Action,
    Side,
    Puppet,
)
from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.common.agents import MarketManager
from vega_sim.reinforcement.v2.rewards import BaseRewarder, REWARD_ENUM_TO_CLASS, Reward
from vega_sim.reinforcement.v2.states import State, SimpleState
from vega_sim.null_service import VegaServiceNull


@dataclass
class StepResult:
    observation: State
    reward: float


class Environment:
    def __init__(
        self,
        agents: Dict[str, Type[AgentType]],
        agent_to_reward: Dict[str, Type[BaseRewarder]],
        agent_to_state: Dict[str, Type[State]],
        scenario: Scenario,
        reset_vega_every_n_runs: int = 100,
        funds_per_run: float = 10_000,
    ):
        self._agents = agents
        self._agent_to_reward_enum = agent_to_reward
        self._agent_to_state = agent_to_state
        self._agent_to_reward: Dict[str, BaseRewarder] = {}

        self._scenario = scenario
        self._vega = VegaServiceNull(
            warn_on_raw_data_access=False,
            run_with_console=False,
            retain_log_files=True,
            store_transactions=True,
            transactions_per_block=1000,
        )
        self._loop_tag = 0

        self._runs_since_reset = 0
        self._reset_vega_every_n_runs = reset_vega_every_n_runs
        self._funds_per_run = funds_per_run

        self._vega.start()

    def stop(self):
        self._vega.stop()

    def _extract_observation(self, agent_name: str) -> State:
        return self._agent_to_state[agent_name].from_vega(
            self._vega,
            for_key_name=agent_name,
            market_id=self._market_id,
            asset_id=self._asset_id,
        )

    def step(self, actions: Dict[str, Optional[Action]]) -> Dict[str, StepResult]:
        for agent_name, action in actions.items():
            if action is not None:
                self._puppets[agent_name].set_next_action(action=action)

        self._scenario.env.step(self._vega)
        self._vega.wait_fn(1)
        step_res = {}
        for agent_name, reward_gen in self._agent_to_reward.items():
            step_res[agent_name] = StepResult(
                observation=self._extract_observation(agent_name),
                reward=self.calculate_reward(reward_gen),
            )
        return step_res

    def calculate_reward(self, rewarder: Type[BaseRewarder]) -> float:
        return rewarder.get_reward(vega=self._vega)

    def _reset_vega(self) -> None:
        self._vega.stop()
        self._vega = VegaServiceNull(
            warn_on_raw_data_access=False,
            run_with_console=False,
            retain_log_files=True,
            store_transactions=True,
            transactions_per_block=1000,
        )
        self._vega.start()

    def reset(self) -> None:
        if self._runs_since_reset > self._reset_vega_every_n_runs:
            self._reset_vega()
            self._runs_since_reset = 0
        self._runs_since_reset += 1

        self._scenario.agents = self._scenario.configure_agents(
            vega=self._vega, tag=str(self._loop_tag), random_state=None
        )
        manager = self._scenario.agents[
            MarketManager.name_from_tag(str(self._loop_tag))
        ]

        self._puppets: Dict[str, Puppet] = {
            agent_name: AGENT_TYPE_TO_AGENT[agent_type](
                key_name=agent_name,
                market_name=manager.market_name,
                tag=str(self._loop_tag),
            )
            for agent_name, agent_type in self._agents.items()
        }
        self._scenario.agents.update(self._puppets)

        self._scenario.env = self._scenario.configure_environment(
            vega=self._vega,
            tag=str(self._loop_tag),
        )

        for agent in self._scenario.env.agents:
            agent.initialise(vega=self._vega)
            self._vega.wait_fn(1)

        for agent_name in self._agents.keys():
            self._vega.mint(
                key_name=agent_name,
                asset=manager.asset_id,
                amount=self._funds_per_run,
            )

        self._agent_to_reward = {}

        for agent, reward in self._agent_to_reward_enum.items():
            self._agent_to_reward[agent] = REWARD_ENUM_TO_CLASS[reward](
                agent_key=agent, asset_id=manager.asset_id, market_id=manager.market_id
            )
        self._market_id = manager.market_id
        self._asset_id = manager.asset_id


if __name__ == "__main__":
    from vega_sim.scenario.registry import CurveMarketMaker

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
        num_steps=50,
        random_agent_ordering=False,
        sigma=100,
        asset_name="DAI",
    )

    env = Environment(
        agents={"test_agent_learner": AgentType.MARKET_ORDER},
        agent_to_reward={"test_agent_learner": Reward.PNL},
        agent_to_state={"test_agent_learner": SimpleState},
        scenario=scenario,
    )
    env.reset()
    for _ in range(10):
        print(env.step({"test_agent_learner": MarketOrderAction(Side.BUY, 1)}))

    env.stop()
