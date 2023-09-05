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

import numpy as np

from collections import namedtuple
from typing import Any, Callable, List, Optional

from vega_sim.environment.agent import (
    Agent,
    StateAgent,
    StateAgentWithWallet,
    VegaState,
)
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.null_service import VegaServiceNull
from vega_sim.service import VegaService

from vega_sim.service import VegaFaucetError

logger = logging.getLogger(__name__)

MarketState = namedtuple(
    "MarketState",
    [
        "state",
        "trading_mode",
        "midprice",
        "best_bid_price",
        "best_ask_price",
        "min_valid_price",
        "max_valid_price",
        "orders",
        "depth",
    ],
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
        pause_every_n_steps: Optional[int] = None,
        random_state: Optional[np.random.RandomState] = None,
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
        self._pause_every_n_steps = pause_every_n_steps

        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

    def run(
        self,
        run_with_console: bool = False,
        pause_at_completion: bool = False,
        log_every_n_steps: Optional[int] = None,
        step_end_callback: Optional[Callable[[], None]] = None,
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
            step_end_callback:
                Optional callable, called after each set of agent steps
        """
        if self._vega is None:
            with VegaServiceNull(
                run_with_console=run_with_console,
                warn_on_raw_data_access=False,
                transactions_per_block=self.transactions_per_block,
                block_duration=f"{int(self.block_length_seconds)}s",
                use_full_vega_wallet=False,
            ) as vega:
                return self._run(
                    vega,
                    pause_at_completion=pause_at_completion,
                    log_every_n_steps=log_every_n_steps,
                    step_end_callback=step_end_callback,
                )
        else:
            return self._run(
                self._vega,
                pause_at_completion=pause_at_completion,
                log_every_n_steps=log_every_n_steps,
                step_end_callback=step_end_callback,
            )

    def _start_live_feeds(self, vega: VegaService):
        # Get lists of unique market_ids and party_ids to observe

        market_ids = [
            vega.find_market_id(market_name)
            for market_name in {
                agent.market_name
                for agent in self.agents
                if hasattr(agent, "market_name")
            }
        ]

        party_ids = list(
            {
                vega.wallet.public_key(
                    wallet_name=agent.wallet_name, name=agent.key_name
                )
                for agent in self.agents
                if hasattr(agent, "key_name")
            }
        )
        # Start order monitoring only observing scenario markets and parties
        vega.data_cache.start_live_feeds(market_ids=market_ids, party_ids=party_ids)

    def _run(
        self,
        vega: VegaServiceNull,
        pause_at_completion: bool = False,
        log_every_n_steps: Optional[int] = None,
        step_end_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Run the simulation with specified agents.

        Args:
            pause_at_completion:
                bool, default False, If True will pause with a keypress-prompt
                    once the simulation has completed, allowing the final state
                    to be inspected, either via code or the Console
            log_every_n_steps:
                Optional, int, If passed, will log a progress line every n steps
            step_end_callback:
                Optional callable, called after each set of agent steps
        """
        logger.info(f"Running wallet at: {vega.wallet_url}")
        logger.info(f"Running graphql at: http://localhost:{vega.data_node_rest_port}")

        start = datetime.datetime.now()

        for agent in self.agents:
            agent.initialise(vega=vega)
            if isinstance(agent, StateAgentWithWallet):
                logger.info(
                    f"{agent.name()}: key ="
                    f" {vega.wallet.public_key(name=agent.key_name, wallet_name=agent.wallet_name)}"
                )
            if self.transactions_per_block > 1:
                vega.wait_fn(1)

        # Wait for threads to catchup to ensure newly created market observed
        vega.wait_for_thread_catchup()

        start_time = vega.get_blockchain_time(in_seconds=True)
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

            vega.wait_for_total_catchup()

            if self.step_length_seconds is not None:
                end_time = vega.get_blockchain_time(in_seconds=True)
                to_forward = max(0, self.step_length_seconds - (end_time - start_time))
                if to_forward > 0:
                    logger.debug(
                        f"Forwarding {to_forward}s to round out the epoch, meaning"
                        " there were"
                        f" {(end_time - start_time) / self.block_length_seconds} blocks"
                        " produced this step"
                    )
                    vega.wait_fn(to_forward / self.block_length_seconds)
                start_time = vega.get_blockchain_time(in_seconds=True)
            if log_every_n_steps is not None and i % log_every_n_steps == 0:
                logger.info(f"Completed {i} steps")
            if (
                self._pause_every_n_steps is not None
                and i % self._pause_every_n_steps == 0
            ):
                input(
                    f"Environment run at step {i}. Pausing to allow inspection of"
                    " state. Press Enter to continue"
                )

            if step_end_callback is not None:
                step_end_callback()

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

    def step(self, vega: VegaService) -> None:
        for agent in (
            sorted(self.agents, key=lambda _: self.random_state.random())
            if self.random_agent_ordering
            else self.agents
        ):
            # TODO: Remove this once fauceting error has been investigated
            try:
                agent.step(vega)
            except VegaFaucetError:
                logger.exception(
                    f"Agent {agent.name()} failed to step. Funds from faucet never"
                    " received."
                )
                # Mint forwards blocks, wait for catchup
                vega.wait_for_total_catchup()


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
        pause_every_n_steps: Optional[int] = None,
        random_state: np.random.RandomState = None,
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
            pause_every_n_steps=pause_every_n_steps,
            random_state=random_state,
        )

        self.state_func = (
            state_func if state_func is not None else self._default_state_extraction
        )

    def _default_state_extraction(self, vega: VegaService) -> VegaState:
        if not hasattr(self, "market_decimals_cache"):
            self.market_decimals_cache = {}
        market_state = {}
        order_status = vega.order_status_from_feed(live_only=True)
        for (
            market_id,
            market_data,
        ) in vega.data_cache.market_data_from_feed_store.items():
            if market_id not in self.market_decimals_cache:
                self.market_decimals_cache[market_id] = vega.market_info(
                    market_id=market_id
                ).decimal_places
            market_state[market_id] = MarketState(
                state=market_data.market_state,
                trading_mode=market_data.market_trading_mode,
                midprice=market_data.mid_price,
                best_bid_price=market_data.best_bid_price,
                best_ask_price=market_data.best_offer_price,
                min_valid_price=vega.price_bounds(market_id=market_id)[0],
                max_valid_price=vega.price_bounds(market_id=market_id)[1],
                orders=order_status.get(market_id, {}),
                depth=vega.market_depth(market_id=market_id),
            )

        return VegaState(network_state=(), market_state=market_state)

    def step(self, vega: VegaService) -> None:
        vega.wait_for_thread_catchup()
        state = self.state_func(vega)
        for agent in (
            sorted(self.agents, key=lambda _: self.random_state.random())
            if self.random_agent_ordering
            else self.agents
        ):
            # TODO: Remove this once fauceting error has been investigated
            try:
                agent.step(state)
            except VegaFaucetError:
                logger.exception(
                    f"Agent {agent.name()} failed to step. Funds from faucet never"
                    " received."
                )
                # Mint forwards blocks, wait for catchup
                vega.wait_for_total_catchup()


class NetworkEnvironment(MarketEnvironmentWithState):
    def __init__(
        self,
        agents: List[StateAgent],
        n_steps: int = -1,
        step_length_seconds: int = 5,
        random_agent_ordering: bool = True,
        vega_service: Optional[VegaServiceNetwork] = None,
        state_func: Optional[Callable[[VegaService], VegaState]] = None,
        raise_datanode_errors: Optional[bool] = True,
        raise_step_errors: Optional[bool] = True,
        random_state: np.random.RandomState = None,
        create_keys: Optional[bool] = False,
        mint_keys: Optional[bool] = False,
    ):
        super().__init__(
            agents=agents,
            n_steps=n_steps,
            random_agent_ordering=random_agent_ordering,
            step_length_seconds=step_length_seconds,
            vega_service=vega_service,
            random_state=random_state,
        )
        self.state_func = (
            state_func if state_func is not None else self._default_state_extraction
        )

        self.raise_datanode_errors = raise_datanode_errors
        self.raise_step_errors = raise_step_errors

        self.create_keys = create_keys
        self.mint_keys = mint_keys

    def run(
        self,
        run_with_console: bool = False,
        pause_at_completion: bool = False,
        log_every_n_steps: Optional[int] = None,
    ):
        if self._vega is None:
            with VegaServiceNetwork(
                use_full_vega_wallet=True,
                run_with_wallet=True,
                run_with_console=run_with_console,
            ) as vega:
                return self._run(vega)
        else:
            return self._run(
                self._vega,
                pause_at_completion=pause_at_completion,
                log_every_n_steps=log_every_n_steps,
            )

    def _run(
        self,
        vega: VegaServiceNetwork,
        pause_at_completion: bool = False,
        log_every_n_steps: Optional[int] = None,
    ) -> None:
        # Initial datanode connection check
        vega.check_datanode(raise_on_error=self.raise_datanode_errors)

        # Initialise agents without minting assets
        for agent in self.agents:
            agent.initialise(
                vega=vega, create_key=self.create_keys, mint_key=self.mint_keys
            )

        self._start_live_feeds(vega=vega)

        i = 0
        # A negative self.n_steps will loop indefinitely
        while i != self.n_steps:
            t_start = time.time()

            vega.check_datanode(raise_on_error=self.raise_datanode_errors)

            i += 1
            self.step(vega)

            t_elapsed = time.time() - t_start
            if t_elapsed <= self.step_length_seconds:
                time.sleep(self.step_length_seconds - t_elapsed)
            else:
                logging.warning(
                    f"Environment step, {round(t_elapsed,2)}s, taking longer than"
                    f" defined scenario step length, {self.step_length_seconds}s,"
                )
            if log_every_n_steps is not None and i % log_every_n_steps == 0:
                logger.info(f"Completed {i} steps")

        for agent in self.agents:
            try:
                agent.finalise()
            except Exception as e:
                msg = f"Agent '{agent.key_name}' failed to step. Error: {e}"
                if self.raise_step_errors:
                    raise (e)
                else:
                    logging.warning(msg)
        if pause_at_completion:
            input(
                "Environment run completed. Pausing to allow inspection of state."
                " Press Enter to continue"
            )

    def step(self, vega: VegaServiceNetwork) -> None:
        t = time.time()
        state = self.state_func(vega)
        logging.debug(f"Get state took {time.time() - t} seconds.")
        for agent in (
            sorted(self.agents, key=lambda _: self.random_state.random())
            if self.random_agent_ordering
            else self.agents
        ):
            try:
                agent.step(state)
            except Exception as e:
                msg = f"Agent '{agent.name()}' failed to step. Error: {e}"
                if self.raise_step_errors:
                    raise e(msg)
                else:
                    logging.warning(msg)


class RealtimeMarketEnvironment(MarketEnvironmentWithState):
    def __init__(
        self,
        agents: List[StateAgent],
        random_agent_ordering: bool = True,
        state_func: Optional[Callable[[VegaService], VegaState]] = None,
        transactions_per_block: int = 1,
        block_length_seconds: int = 1,
        step_length_seconds: int = 1,
        vega_service: Optional[VegaServiceNull] = None,
        pause_every_n_steps: Optional[int] = None,
        random_state: np.random.RandomState = None,
    ):
        """Set up a Vega protocol environment with some specified agents.
        Handles the entire Vega setup and environment lifetime process, allowing the
        user to focus on building the Agents themselves.

        Once an environment has been created, calling the 'run' function will
        run a complete simulation of the environment lifecycle. The realtime environment
        aims to progress at a slower state, and so instead of running through all
        actions and steps as fast as possible will sleep a configurable amount of
        time between each block. Runs forever until cancelled.


        Args:
            agents:
                List[StateAgent], a list of instantiated Agent objects which will
                    interact with the environment
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
            pause_every_n_steps:
                Optional[int], default None, If passed, simulation will pause every
                    time the passed number of steps elapses waiting on user to press
                    return. Allows inspection of the simulation at given frequency
        """
        super().__init__(
            agents=agents,
            n_steps=0,
            random_agent_ordering=random_agent_ordering,
            transactions_per_block=transactions_per_block,
            block_length_seconds=block_length_seconds,
            step_length_seconds=step_length_seconds,
            vega_service=vega_service,
            pause_every_n_steps=pause_every_n_steps,
            random_state=random_state,
            state_func=(
                state_func if state_func is not None else self._default_state_extraction
            ),
        )

    def step(self, vega: VegaService) -> None:
        state = self.state_func(vega)
        vega.wait_fn(1)
        for agent in (
            sorted(self.agents, key=lambda _: self.random_state.random())
            if self.random_agent_ordering
            else self.agents
        ):
            agent.step(state)

    def _run(
        self,
        vega: VegaServiceNull,
        pause_at_completion: bool = False,
    ) -> None:
        """Run the simulation with specified agents.

        Args:
            pause_at_completion:
                bool, default False, If True will pause with a keypress-prompt
                    once the simulation has completed, allowing the final state
                    to be inspected, either via code or the Console
        """
        logger.info(f"Running wallet at: {vega.wallet_url}")
        logger.info(f"Running graphql at: http://localhost:{vega.data_node_rest_port}")

        for agent in self.agents:
            agent.initialise(vega=vega)
            if self.transactions_per_block > 1:
                vega.wait_fn(1)

        i = 1
        while True:
            i += 1
            self.step(vega)

            if (
                self._pause_every_n_steps is not None
                and i % self._pause_every_n_steps == 0
            ):
                input(
                    f"Environment run at step {i}. Pausing to allow inspection of"
                    " state. Press Enter to continue"
                )
            time.sleep(self.step_length_seconds)
