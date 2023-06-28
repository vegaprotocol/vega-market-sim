import pytest
import subprocess


@pytest.mark.integration
def test_capsule():
    subprocess.call(["sh", "scripts/run-capsule-test.sh", "100", "vega_sim_test"])
