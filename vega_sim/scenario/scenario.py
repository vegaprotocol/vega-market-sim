import abc
import numpy as np
from typing import Optional

from vega_sim.null_service import VegaService
from vega_sim.environment.environment import MarketEnvironment


class Scenario(abc.ABC):
    def __init__(self):
        self.agents = []
        self.env: Optional[MarketEnvironment] = None

    @abc.abstractmethod
    def set_up_background_market(
        self, vega: VegaService, tag: str, random_state: Optional[np.random.RandomState]
    ):
        pass

    def run_iteration(
        self,
        vega: VegaService,
        pause_at_completion: bool = False,
        run_with_console: bool = False,
        random_state: Optional[np.random.RandomState] = None,
    ):
        self.set_up_background_market(vega=vega, tag=str(0), random_state=random_state)
        result = self.env.run(
            pause_at_completion=pause_at_completion,
            run_with_console=run_with_console,
        )
        return result
