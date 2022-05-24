import logging

from examples.agent_market.agents import (
    MM_WALLET,
    TERMINATE_WALLET,
    TRADER_WALLET,
    MarketMaker,
    MarketOrderTraders,
    random_walk_price,
)
from vega_sim.environment import MarketEnvironmentWithState


def main(
    num_steps: int = 60,
    block_size: int = 1,
    run_with_console: bool = False,
    pause_at_completion: bool = False,
    order_arrival_rate: float = 2,
):
    market_maker = MarketMaker(
        wallet_name=MM_WALLET.name,
        wallet_pass=MM_WALLET.passphrase,
        terminate_wallet_name=TERMINATE_WALLET.name,
        terminate_wallet_pass=TERMINATE_WALLET.passphrase,
        price_process=random_walk_price(
            terminal_time_seconds=num_steps + 10, sigma=0.1, initial_price=100
        ),
    )
    mo_traders = MarketOrderTraders(
        wallet_name=TRADER_WALLET.name,
        wallet_pass=TRADER_WALLET.passphrase,
        buy_order_arrival_rate=order_arrival_rate,
    )
    env = MarketEnvironmentWithState(
        agents=[market_maker, mo_traders],
        n_steps=num_steps,
        transactions_per_block=block_size,
    )
    env.run(run_with_console=run_with_console, pause_at_completion=pause_at_completion)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(
        num_steps=int(1 * 60 * 60 * 5),
        block_size=10,
        pause_at_completion=True,
        run_with_console=True,
    )
