import pytest

from vega_sim.api.helpers import num_from_padded_int, num_to_padded_int


@pytest.mark.parametrize(
    ["input", "decimals", "expected_output"],
    [(100, 2, 1), (6999900, 5, 69.999), (100, 0, 100)],
)
def test_num_from_padded_int(input, decimals, expected_output):
    assert num_from_padded_int(input, decimals=decimals) == expected_output


@pytest.mark.parametrize(
    ["input", "decimals", "expected_output"],
    [(1, 2, 100), (69.999, 5, 6999900), (100, 0, 100)],
)
def test_num_to_padded_int(input, decimals, expected_output):
    assert num_to_padded_int(input, decimals=decimals) == expected_output
