import gymnasium as gym
import numpy as np


def price_state_with_fees_obs_space(
    num_levels: int = 5,
    min_position: float = -1000,
    max_position: float = 1000,
    max_price: float = 100_000,
    max_volume: float = 10_000,
    max_balance: float = 1e9,
) -> gym.spaces.Box:
    return gym.spaces.Box(
        low=np.array([min_position, 0, 0] + num_levels * 4 * [0] + [0]),
        high=np.array(
            [max_position, max_balance, 1]
            + num_levels * 2 * [max_price]
            + num_levels * 2 * [max_volume]
            + [0.1]
        ),
        dtype=np.float64,
    )


def position_state_with_fees_obs_space(
    min_position: float = -1000,
    max_position: float = 1000,
) -> gym.spaces.Box:
    return gym.spaces.Box(
        low=np.array([min_position]),
        high=np.array([max_position]),
        dtype=np.float64,
    )
