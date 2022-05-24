"""
Module defining environments in which the Vega market sim can be interacted with by
prespecified Agent classes. This enables a modular approach to simulating a
market behaviour, be that with Agents with pre-specified strategies or
those which learn through interaction with Vega itself.

Currently there are two major formats of Environment, the MarketEnvironment
and the MarketEnvironmentWithState. The crucial difference between these
two is that in the *WithState version each agent recieves, at each timestep, a
summary object representing the network's state at that time. This is
intended to eventually speed up the step process overall as individual agents
do not each need to gather state. Currently this 'state' object is a work-in-progress.

The alternative environment, plain MarketEnvironment, passes the VegaService
itself to agents at each timestep, allowing them to gather their own
information. This allows more 'custom' agents but may be ultimately slower
if the same information is retrieved multiple times.

For examples of this setup, see examples/agent_market.

"""


import datetime
import logging
import random
from collections import namedtuple
from typing import Callable, List, Optional

from vega_sim.environment.agent import Agent, StateAgent, VegaState
from vega_sim.null_service import VegaServiceNull
from vega_sim.service import VegaService

logger = logging.getLogger(__name__)

MarketState = namedtuple(
    "MarketState",
    [
        "state",
        "trading_mode",
        # "orders",
    ],  # "order_book"]
)


class MarketEnvironment:
    def __init__(
        self,
        agents: List[Agent],
        n_steps: int,
        random_agent_ordering: bool = True,
        transactions_per_block: int = 1,
        block_length_seconds: int = 1,
    ):
        """Set up a Vega protocol environment with some specified agents.
        Handles the entire Vega setup and environment lifetime process, allowing the
        user to focus on building the Agents themselves.

        Once an environment has been created, calling the 'run' function will
        run a complete simulation of the environment lifecycle then shut down
        the various Vega processes.

        Args:
            agents:
                List[Agent], a list of instantiated Agent objects which will
                    interact with the environment
            n_steps:
                int, The number of steps for the environment to run
            random_agent_ordering:
                bool, default True, In each step, whether the order of agent
                    steps should be randomised. If False, the order of agents
                    passed in will be used
            transactions_per_block:
                int, default 1, How many transactions should be contained
                    for each block in the Vega chain. Often this is best set
                    as the maximum number of actions agents can take per step
                    to ensure they all happen 'at the same time' per step.
            block_length_seconds:
                int, default 1, How many seconds each block in the Vega chain
                    is taken to represent.
        """
        self.agents = agents
        self.n_steps = n_steps
        self.random_agent_ordering = random_agent_ordering
        self.transactions_per_block = transactions_per_block
        self.block_length_seconds = block_length_seconds

    def run(
        self,
        run_with_console: bool = False,
        pause_at_completion: bool = False,
    ) -> None:
        """Run the simulation with specified agents.

        Args:
            run_with_console:
                bool, default False, Whether the environment should attempt
                    to spin up a full Vega console with which to observe
                    the market behaviour
            pause_at_completion:
                bool, default False, If True will pause with a keypress-prompt
                    once the simulation has completed, allowing the final state
                    to be inspected, either via code or the Console
        """
        with VegaServiceNull(
            run_wallet_with_console=run_with_console,
            warn_on_raw_data_access=False,
            transactions_per_block=self.transactions_per_block,
            block_duration=f"{self.block_length_seconds}s",
        ) as vega:
            logger.info(f"Running wallet at: {vega.wallet_url()}")
            logger.info(
                f"Running graphql at: http://localhost:{vega.data_node_graphql_port}"
            )

            start = datetime.datetime.now()
            for agent in self.agents:
                agent.initialise(vega=vega)
                if self.transactions_per_block > 1 and self.block_length_seconds > 1:
                    vega.forward(f"{self.block_length_seconds + 1}s")
            for _ in range(self.n_steps):
                self.step(vega)
                if self.transactions_per_block > 1 and self.block_length_seconds > 1:
                    vega.forward(f"{self.block_length_seconds + 1}s")
                vega.wait_for_datanode_sync()
            logger.info(f"Run took {(datetime.datetime.now() - start).seconds}s")

            if pause_at_completion:
                input(
                    "Environment run completed. Pausing to allow inspection of state."
                    " Press Enter to continue"
                )

    def step(self, vega: VegaService) -> None:
        for agent in (
            sorted(self.agents, key=lambda _: random.random())
            if self.random_agent_ordering
            else self.agents
        ):
            agent.step(vega)


class MarketEnvironmentWithState(MarketEnvironment):
    def __init__(
        self,
        agents: List[StateAgent],
        n_steps: int,
        random_agent_ordering: bool = True,
        state_func: Optional[Callable[[VegaService], VegaState]] = None,
        transactions_per_block: int = 1,
        block_length_seconds: int = 1,
    ):
        """Set up a Vega protocol environment with some specified agents.
        Handles the entire Vega setup and environment lifetime process, allowing the
        user to focus on building the Agents themselves.

        Once an environment has been created, calling the 'run' function will
        run a complete simulation of the environment lifecycle then shut down
        the various Vega processes.

        This class differs from MarketEnvironment in that each agent will only
        receive a state representation object rather than a full VegaService.

        Args:
            agents:
                List[StateAgent], a list of instantiated Agent objects which will
                    interact with the environment
            n_steps:
                int, The number of steps for the environment to run
            random_agent_ordering:
                bool, default True, In each step, whether the order of agent
                    steps should be randomised. If False, the order of agents
                    passed in will be used
            transactions_per_block:
                int, default 1, How many transactions should be contained
                    for each block in the Vega chain. Often this is best set
                    as the maximum number of actions agents can take per step
                    to ensure they all happen 'at the same time' per step.
            block_length_seconds:
                int, default 1, How many seconds each block in the Vega chain
                    is taken to represent.
        """
        super().__init__(
            agents=agents,
            n_steps=n_steps,
            random_agent_ordering=random_agent_ordering,
            transactions_per_block=transactions_per_block,
            block_length_seconds=block_length_seconds,
        )
        self.state_func = (
            state_func if state_func is not None else self._default_state_extraction
        )

    @staticmethod
    def _default_state_extraction(vega: VegaService) -> VegaState:
        market_state = {}
        for market in vega.all_markets():
            market_info = vega.market_info(market_id=market.id)
            market_state[market.id] = MarketState(
                state=market_info.state,
                trading_mode=market_info.trading_mode,
                # order_book=vega.order_book_by_market(market.id),
                # orders=vega.open_orders_by_market(market.id),
            )

        return VegaState(network_state=(), market_state=market_state)

    def step(self, vega: VegaService) -> None:
        state = self.state_func(vega)
        for agent in (
            sorted(self.agents, key=lambda _: random.random())
            if self.random_agent_ordering
            else self.agents
        ):
            agent.step(state)
