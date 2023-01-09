import pytest
import runpy


@pytest.mark.integration
def test_closed_out():
    runpy.run_path("examples/visualisations/closed_out.py")


@pytest.mark.integration
def test_loss_socialisation():
    runpy.run_path("examples/visualisations/loss_socialisation.py")


@pytest.mark.integration
def test_margins():
    runpy.run_path("examples/visualisations/margins.py")


@pytest.mark.integration
def test_multiple_lps():
    runpy.run_path("examples/visualisations/multiple_lps.py")
