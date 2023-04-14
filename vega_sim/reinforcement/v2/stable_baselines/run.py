from stable_baselines3 import PPO

import vega_sim.reinforcement.v2.stable_baselines.environment as env

if __name__ == "__main__":
    e = env.SingleAgentVegaEnv(steps_per_trading_session=200)
    model = PPO(
        "MlpPolicy",
        e,
        verbose=1,
        tensorboard_log="./ppo_tensorboard/",
        n_steps=200,
        batch_size=100,
    ).learn(total_timesteps=1_000_000)
