import abc
import numpy as np
from typing import Optional, List, Callable, Any, Dict

from vega_sim.null_service import VegaService
from vega_sim.environment.environment import MarketEnvironment
from vega_sim.scenario.constants import Network
from vega_sim.scenario.common.agents import Snitch, StateAgent, MarketHistoryData, Agent
from vega_sim.tools.scenario_output import market_data_standard_output


class Scenario(abc.ABC):
    def __init__(
        self,
        state_extraction_fn: Optional[
            Callable[[VegaService, Dict[str, Agent]], Any]
        ] = None,
        additional_data_output_fns: Optional[Dict[str, Callable]] = None,
    ):
        self.agents = []
        self.env: Optional[MarketEnvironment] = None
        self.state_extraction_fn = state_extraction_fn
        self.additional_data_output_fns = additional_data_output_fns

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
        **kwargs,
    ):
        tag = tag if tag is not None else ""
        self.agents = self.configure_agents(
            vega=vega, tag=tag, random_state=random_state, **kwargs
        )

        if run_with_snitch or output_data:
            self.agents["snitch"] = Snitch(
                agents=self.agents, additional_state_fn=self.state_extraction_fn
            )

        self.env = self.configure_environment(
            vega=vega, tag=tag, random_state=random_state, **kwargs
        )

        outputs = self.env.run(
            pause_at_completion=pause_at_completion,
            run_with_console=run_with_console,
        )
        if output_data:
            market_data_standard_output(self.get_run_data())
            if self.additional_data_output_fns is not None:
                market_data_standard_output(
                    self.get_additional_run_data(),
                    custom_output_fns=self.additional_data_output_fns,
                )

        return outputs

    def get_snitch(self) -> Optional[Snitch]:
        return self.agents.get("snitch")

    def get_run_data(self) -> List[MarketHistoryData]:
        snitch = self.get_snitch()
        return snitch.states if snitch is not None else []

    def get_additional_run_data(self) -> List[MarketHistoryData]:
        snitch = self.get_snitch()
        return snitch.additional_states if snitch is not None else []
