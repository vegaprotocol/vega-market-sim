import abc
import numpy as np
from typing import Optional, List

from vega_sim.null_service import VegaService
from vega_sim.environment.environment import MarketEnvironment
from vega_sim.scenario.constants import Network
from vega_sim.scenario.common.agents import Snitch, StateAgent, MarketHistoryData
from vega_sim.tools.scenario_output import market_data_standard_output


class Scenario(abc.ABC):
    def __init__(self):
        self.agents = []
        self.env: Optional[MarketEnvironment] = None

    @abc.abstractmethod
    def configure_agents(
        self,
        vega: VegaService,
        tag: str,
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> List[StateAgent]:
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
        network: Optional[Network] = None,
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
            self.agents["snitch"] = Snitch()

        self.env = self.configure_environment(
            vega=vega, tag=tag, random_state=random_state, **kwargs
        )

        outputs = self.env.run(
            pause_at_completion=pause_at_completion,
            run_with_console=run_with_console,
        )
        if output_data:
            market_data_standard_output(self.get_run_data())

        return outputs

    def get_snitch(self) -> Optional[Snitch]:
        return self.agents.get("snitch")

    def get_run_data(self) -> List[MarketHistoryData]:
        snitch = self.get_snitch()
        return snitch.states if snitch is not None else []
