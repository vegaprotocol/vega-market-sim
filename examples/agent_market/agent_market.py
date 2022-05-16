from vega_sim.environment import MarketEnvironmentWithState

from examples.agent_market.agents import (
    TRADER_WALLET,
    MarketMaker,
    MM_WALLET,
    TERMINATE_WALLET,
    MarketOrderTraders,
)


def main():
    market_maker = MarketMaker(
        wallet_name=MM_WALLET.name,
        wallet_pass=MM_WALLET.passphrase,
        terminate_wallet_name=TERMINATE_WALLET.name,
        terminate_wallet_pass=TERMINATE_WALLET.passphrase,
    )
    mo_traders = MarketOrderTraders(
        wallet_name=TRADER_WALLET.name, wallet_pass=TRADER_WALLET.passphrase
    )
    env = MarketEnvironmentWithState(
        agents=[market_maker, mo_traders], n_steps=1000, run_with_console=True
    )
    env.run()


if __name__ == "__main__":
    main()
