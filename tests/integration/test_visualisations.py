import pytest

from tests.integration.utils.fixtures import vega_service

from vega_sim.null_service import VegaServiceNull

from examples.visualisations.closed_out import CloseOutVisualisation
from examples.visualisations.loss_socialisation import LossSocialisationVisualisation


@pytest.mark.integration
def test_closed_out(vega_service: VegaServiceNull):
    vis = CloseOutVisualisation(vega_service)
    vis.test()


@pytest.mark.integration
def test_loss_socialisation(vega_service: VegaServiceNull):
    vega = vega_service
    vis = LossSocialisationVisualisation(vega=vega)
    vis.test()
