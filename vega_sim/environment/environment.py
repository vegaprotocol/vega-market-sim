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

import time
import datetime
import logging
import random
from collections import namedtuple
from typing import Any, Callable, Dict, List, Optional

from vega_sim.environment.agent import Agent, StateAgent, VegaState
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.null_service import VegaServiceNull
from vega_sim.service import VegaService

logger = logging.getLogger(__name__)

MarketState = namedtuple(
    "MarketState",
    [
        "state",
        "trading_mode",
        "midprice",
        "orders",
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
        step_length_seconds: Optional[int] = None,
        vega_service: Optional[VegaServiceNull] = None,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, List[Agent]], Any]
        ] = None,
        state_extraction_freq: int = 10,
        pause_every_n_steps: Optional[int] = None,
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
                int, default 1, How many seconds each block on the Vega chain
                    represents
            step_length_seconds:
                Optional[int], default None, How many seconds each step is
                    taken to represent.
                    After each round of actions, if time has not advanced at least
                    this much we will be forwarded to that far in the future
                    (minus however long the actions did take).
                    e.g. for a step_length_seconds = 60 if all actions take up 10s
                    we will forward 50s at the end.
            vega_service:
                optional, VegaServiceNull, If passed will use this precreated vega
                    service instead of creating one internally.
            state_extraction_fn:
                optional, Callable[[VegaServiceNull, List[Agent]], Any],
                    Optional function which takes a Vega service at a given time
                    and returns a summary of interesting state values. If passed,
                    the aggregated result of these will be returned after a run.
            state_extraction_freq:
                int, default 10, If state_extraction_fn is passed, how many steps
                    should be between each call.
            pause_every_n_steps:
                Optional[int], default None, If passed, simulation will pause every
                    time the passed number of steps elapses waiting on user to press
                    return. Allows inspection of the simulation at given frequency
        """
        self.agents = agents
        self.n_steps = n_steps
        self.random_agent_ordering = random_agent_ordering
        self.transactions_per_block = transactions_per_block
        self.block_length_seconds = block_length_seconds
        self.step_length_seconds = step_length_seconds
        self._vega = vega_service
        self._state_extraction_fn = state_extraction_fn
        self._state_extraction_freq = state_extraction_freq
        self._pause_every_n_steps = pause_every_n_steps

    def run(
        self,
        run_with_console: bool = False,
        pause_at_completion: bool = False,
    ) -> Optional[List[Any]]:
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
        if self._vega is None:
            with VegaServiceNull(
                run_with_console=run_with_console,
                warn_on_raw_data_access=False,
                transactions_per_block=self.transactions_per_block,
                block_duration=f"{int(self.block_length_seconds)}s",
                use_full_vega_wallet=False,
            ) as vega:
                return self._run(vega, pause_at_completion=pause_at_completion)
        else:
            return self._run(self._vega, pause_at_completion=pause_at_completion)

    def _run(
        self,
        vega: VegaServiceNull,
        pause_at_completion: bool = False,
    ) -> Optional[List[Any]]:
        """Run the simulation with specified agents.

        Args:
            pause_at_completion:
                bool, default False, If True will pause with a keypress-prompt
                    once the simulation has completed, allowing the final state
                    to be inspected, either via code or the Console
        """
        logger.info(f"Running wallet at: {vega.wallet_url}")
        logger.info(
            f"Running graphql at: http://localhost:{vega.data_node_graphql_port}"
        )

        start = datetime.datetime.now()
        state_values = []

        for agent in self.agents:
            agent.initialise(vega=vega)
            if self.transactions_per_block > 1:
                vega.wait_fn(1)

        start_time = vega.get_blockchain_time()
        for i in range(self.n_steps):
            self.step(vega)

            # Ensure core is caught up
            core_catchup_start = datetime.datetime.now()
            vega.wait_for_core_catchup()
            core_catchup_seconds = (
                datetime.datetime.now() - core_catchup_start
            ).seconds

            if self.transactions_per_block > 1:
                vega.wait_fn(1)
            vega.wait_for_total_catchup()

            if core_catchup_seconds > 1:
                logger.warn(f"Waited {core_catchup_seconds}s for core catchup")

            if (
                self._state_extraction_fn is not None
                and i % self._state_extraction_freq == 0
            ):
                state_values.append(
                    self._state_extraction_fn(
                        vega, self.agents, state_values=state_values
                    )
                )

            vega.wait_for_total_catchup()

            if self.step_length_seconds is not None:
                end_time = vega.get_blockchain_time()
                to_forward = max(0, self.step_length_seconds - (end_time - start_time))
                if to_forward > 0:
                    logger.debug(
                        f"Forwarding {to_forward}s to round out the epoch, meaning"
                        " there were"
                        f" {(end_time - start_time) / self.block_length_seconds} blocks"
                        " produced this step"
                    )
                    vega.wait_fn(to_forward / self.block_length_seconds)
                start_time = vega.get_blockchain_time()

            if (
                self._pause_every_n_steps is not None
                and i % self._pause_every_n_steps == 0
            ):
                input(
                    f"Environment run at step {i}. Pausing to allow inspection of"
                    " state. Press Enter to continue"
                )

        logger.info(f"Run took {(datetime.datetime.now() - start).seconds}s")

        if pause_at_completion:
            input(
                "Environment run completed. Pausing to allow inspection of state."
                " Press Enter to continue"
            )
        for agent in self.agents:
            agent.finalise()
        vega.wait_for_core_catchup()
        vega.wait_for_datanode_sync()

        if self._state_extraction_fn is not None:
            state_values.append(
                self._state_extraction_fn(vega, self.agents, state_values=state_values)
            )
        if self._state_extraction_fn is not None:
            return state_values

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
        step_length_seconds: Optional[int] = None,
        vega_service: Optional[VegaServiceNull] = None,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNull, List[Agent]], Any]
        ] = None,
        state_extraction_freq: int = 10,
        pause_every_n_steps: Optional[int] = None,
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
                int, default 1, How many seconds each block on the Vega chain
                    represents
            step_length_seconds:
                Optional[int], default None, How many seconds each step is
                    taken to represent.
                    After each round of actions, if time has not advanced at least
                    this much we will be forwarded to that far in the future
                    (minus however long the actions did take).
                    e.g. for a step_length_seconds = 60 if all actions take up 10s
                    we will forward 50s at the end.
            vega_service:
                optional, VegaServiceNull, If passed will use this precreated vega
                    service instead of creating one internally.
            state_extraction_fn:
                optional, Callable[[VegaServiceNull, List[Agent]], Any],
                    Optional function which takes a Vega service at a given time
                    and returns a summary of interesting state values. If passed,
                    the aggregated result of these will be returned after a run.
            state_extraction_freq:
                int, default 10, If state_extraction_fn is passed, how many steps
                    should be between each call.
            pause_every_n_steps:
                Optional[int], default None, If passed, simulation will pause every
                    time the passed number of steps elapses waiting on user to press
                    return. Allows inspection of the simulation at given frequency
        """
        super().__init__(
            agents=agents,
            n_steps=n_steps,
            random_agent_ordering=random_agent_ordering,
            transactions_per_block=transactions_per_block,
            block_length_seconds=block_length_seconds,
            step_length_seconds=step_length_seconds,
            vega_service=vega_service,
            state_extraction_fn=state_extraction_fn,
            state_extraction_freq=state_extraction_freq,
            pause_every_n_steps=pause_every_n_steps,
        )
        self.state_func = (
            state_func if state_func is not None else self._default_state_extraction
        )

    # @staticmethod
    def _default_state_extraction(self, vega: VegaService) -> VegaState:
        market_state = {}
        order_status = vega.order_status_from_feed(live_only=True)
        for market in vega.all_markets():
            market_info = vega.market_info(market_id=market.id)
            market_data = vega.market_data(market_id=market.id)
            market_state[market.id] = MarketState(
                state=market_info.state,
                trading_mode=market_info.trading_mode,
                midprice=float(market_data.mid_price)
                / 10 ** int(market_info.decimal_places),
                orders=order_status.get(market.id, {}),
            )

        return VegaState(network_state=(), market_state=market_state)

    def step(self, vega: VegaService) -> None:
        vega.wait_for_datanode_sync()
        state = self.state_func(vega)
        for agent in (
            sorted(self.agents, key=lambda _: random.random())
            if self.random_agent_ordering
            else self.agents
        ):
            agent.step(state)


class NetworkEnvironment(MarketEnvironmentWithState):
    def __init__(
        self,
        agents: List[StateAgent],
        n_steps: int = -1,
        step_length_seconds: int = 5,
        random_agent_ordering: bool = True,
        vega_service: Optional[VegaServiceNetwork] = None,
        state_func: Optional[Callable[[VegaService], VegaState]] = None,
        state_extraction_fn: Optional[
            Callable[[VegaServiceNetwork, List[Agent]], Any]
        ] = None,
        state_extraction_freq: int = 10,
    ):
        super().__init__(
            agents=agents,
            n_steps=n_steps,
            random_agent_ordering=random_agent_ordering,
            step_length_seconds=step_length_seconds,
            vega_service=vega_service,
            state_extraction_fn=state_extraction_fn,
            state_extraction_freq=state_extraction_freq,
        )
        self.state_func = (
            state_func if state_func is not None else self._default_state_extraction
        )

    def run(self):
        if self._vega is None:
            with VegaServiceNetwork(
                use_full_vega_wallet=True,
            ) as vega:
                return self._run(vega)
        else:
            return self._run(self._vega)

    def _run(self, vega):
        state_values = []

        # Initialise agents without minting assets
        for agent in self.agents:
            agent.initialise(vega=vega, create_wallet=False, mint_wallet=False)

        i = 0
        # A negative self.n_steps will loop indefinitely
        while i != self.n_steps:
            i += 1
            self.step(vega)

            if (
                self._state_extraction_fn is not None
                and i % self._state_extraction_freq == 0
            ):
                state_values.append(self._state_extraction_fn(vega, self.agents))

            time.sleep(self.step_length_seconds)

        for agent in self.agents:
            agent.finalise()

        if self._state_extraction_fn is not None:
            state_values.append(self._state_extraction_fn(vega, self.agents))
            return state_values

    def step(self, vega: VegaServiceNetwork) -> None:
        t = time.time()
        state = self.state_func(vega)
        logging.debug(f"Get state took {time.time() - t} seconds.")
        for agent in (
            sorted(self.agents, key=lambda _: random.random())
            if self.random_agent_ordering
            else self.agents
        ):
            agent.step(state)
