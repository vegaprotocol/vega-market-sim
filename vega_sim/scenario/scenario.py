import abc

from vega_sim.null_service import VegaServiceNull


class Scenario(abc.ABC):
    def run_iteration(self, vega: VegaServiceNull):
        pass
