import pytest
import subprocess


@pytest.mark.integration
def test_rl_run():
    subprocess.call(["sh", "scripts/run-capsule-test.sh", "100"])