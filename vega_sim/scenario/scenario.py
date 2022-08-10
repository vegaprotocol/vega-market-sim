import abc
import numpy as np
from typing import Optional

from vega_sim.null_service import VegaServiceNull


class Scenario(abc.ABC):
    def run_iteration(
        self,
        vega: VegaServiceNull,
        pause_at_completion: bool = False,
        random_state: Optional[np.random.RandomState] = None,
    ):
        pass
