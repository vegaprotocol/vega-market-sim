from stable_baselines3 import PPO, DQN

import vega_sim.reinforcement.v2.stable_baselines.environment as env
from vega_sim.reinforcement.v2.states import PriceStateWithFees, PositionOnly

if __name__ == "__main__":
    e = env.SingleAgentVegaEnv(
        action_type=env.ActionType.AT_TOUCH_ONE_SIDE,
        steps_per_trading_session=200,
        reward_type=env.Reward.PNL,
        terminal_reward_type=env.Reward.SQ_INVENTORY_PENALTY,
        state_type=PriceStateWithFees,
    )
    model = PPO(
        "MlpPolicy",
        e,
        verbose=1,
        tensorboard_log="./ppo_tensorboard/",
        n_steps=600,
        batch_size=50,
    ).learn(total_timesteps=1_000_000)
