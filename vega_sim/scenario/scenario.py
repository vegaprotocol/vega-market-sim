import abc
import numpy as np
from typing import Optional, List, Callable, Any, Dict
import logging

from vega_sim.null_service import VegaService
from vega_sim.environment.environment import MarketEnvironment
from vega_sim.scenario.constants import Network
from vega_sim.scenario.common.agents import (
    Snitch,
    StateAgent,
    MarketHistoryData,
    Agent,
    ResourceData,
)
from vega_sim.tools.scenario_output import (
    agents_standard_output,
    resources_standard_output,
    market_data_standard_output,
    agents_standard_output,
    assets_standard_output,
    market_chain_standard_output,
)

import vega_sim.proto.vega as vega_protos

logger = logging.getLogger(__name__)


class Scenario(abc.ABC):
    def __init__(
        self,
        state_extraction_fn: Optional[
            Callable[[VegaService, Dict[str, Agent]], Any]
        ] = None,
        final_extraction_fn: Optional[
            Callable[[VegaService, Dict[str, Agent]], Any]
        ] = None,
        additional_data_output_fns: Optional[Dict[str, Callable]] = None,
    ):
        self.agents = []
        self.env: Optional[MarketEnvironment] = None
        self.state_extraction_fn = state_extraction_fn
        self.final_extraction_fn = final_extraction_fn
        self.additional_data_output_fns = additional_data_output_fns

    def _step_end_callback(self):
        """Called after each set of agent steps before the next loop begins."""
        pass

    @abc.abstractmethod
    def configure_agents(
        self,
        vega: VegaService,
        tag: str,
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> Dict[str, StateAgent]:
        pass

    @abc.abstractmethod
    def configure_environment(
        self,
        vega: VegaService,
        tag: str,
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> MarketEnvironment:
        pass

    def run(
        self,
        pause_at_completion: bool = False,
        run_with_console: bool = False,
    ):
        result = self.env.run(
            pause_at_completion=pause_at_completion,
            run_with_console=run_with_console,
            step_end_callback=self._step_end_callback,
        )
        return result

    def run_iteration(
        self,
        vega: VegaService,
        pause_at_completion: bool = False,
        run_with_console: bool = False,
        random_state: Optional[np.random.RandomState] = None,
        run_with_snitch: bool = True,
        tag: Optional[str] = None,
        output_data: bool = False,
        log_every_n_steps: Optional[int] = None,
        **kwargs,
    ):
        tag = tag if tag is not None else ""
        self.agents = self.configure_agents(
            vega=vega, tag=tag, random_state=random_state, **kwargs
        )

        if run_with_snitch or output_data:
            self.agents["snitch"] = Snitch(
                agents=self.agents,
                additional_state_fn=self.state_extraction_fn,
                additional_finalise_fn=self.final_extraction_fn,
            )

        self.env = self.configure_environment(
            vega=vega, tag=tag, random_state=random_state, **kwargs
        )

        outputs = self.env.run(
            pause_at_completion=pause_at_completion,
            run_with_console=run_with_console,
            log_every_n_steps=log_every_n_steps,
            step_end_callback=self._step_end_callback,
        )
        if output_data:
            logger.info("std")
            agents_standard_output(self.agents)
            logger.info("resource std")
            resources_standard_output(self.get_resource_data())
            logger.info("asset std")
            assets_standard_output(self.get_assets())
            logger.info("mkt_data")
            market_data_standard_output(self.get_run_data())
            logger.info("mkt_chain")
            market_chain_standard_output(self.get_run_data())
            if self.additional_data_output_fns is not None:
                logger.info("additional")
                market_data_standard_output(
                    self.get_additional_run_data(),
                    custom_output_fns=self.additional_data_output_fns,
                )

        return outputs

    def get_snitch(self) -> Optional[Snitch]:
        return self.agents.get("snitch")

    def get_resource_data(self) -> List[ResourceData]:
        snitch = self.get_snitch()
        return snitch.resources if snitch is not None else []

    def get_assets(self) -> List[vega_protos.assets.Asset]:
        snitch = self.get_snitch()
        return snitch.assets if snitch is not None else []

    def get_run_data(self) -> List[MarketHistoryData]:
        snitch = self.get_snitch()
        return snitch.states if snitch is not None else []

    def get_additional_run_data(self) -> List[MarketHistoryData]:
        snitch = self.get_snitch()
        return snitch.additional_states if snitch is not None else []
