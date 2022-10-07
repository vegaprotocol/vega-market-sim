import abc
import numpy as np
from typing import Optional

from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.constants import Network


class Scenario(abc.ABC):
    def run_iteration(
        self,
        vega: VegaServiceNull,
        network: Optional[Network],
        pause_at_completion: bool = False,
        random_state: Optional[np.random.RandomState] = None,
    ):
        pass
