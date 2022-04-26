import logging
from collections import namedtuple

from vega_sim.null_service import VegaServiceNull


WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Set up parties in the market/ Submit liquidity provision/ Control midprice
MM_WALLET = WalletConfig("wwestgarth", "pin")

# The party to send selling/buying MOs to hit LP orders
TRADER_WALLET = WalletConfig("Zl3pLs6Xk6SwIK7Jlp2x", "bJQDDVGAhKkj3PVCc7Rr")

# The party randomly post LOs at buy/sell side to simulate real Market situation
RANDOM_WALLET = WalletConfig("OJpVLvU5fgLJbhNPdESa", "GmJTt9Gk34BHDlovB7AJ")

# The party to terminate the market and send settlment price
TERMINATE_WALLET = WalletConfig("FJMKnwfZdd48C8NqvYrG", "bY3DxwtsCstMIIZdNpKs")

wallets = [MM_WALLET, TRADER_WALLET, RANDOM_WALLET, TERMINATE_WALLET]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    vega = VegaServiceNull(run_wallet_with_console=True)
    vega.start()

    for wallet in wallets:
        vega.create_wallet(wallet.name, wallet.passphrase)

    # for wallet in wallets:
    #     vega.login(wallet.name, wallet.passphrase)
    vega.mint(
        MM_WALLET.name,
        asset="VOTE",
        amount=10000000000,
    )

    vega.create_asset(
        MM_WALLET.name,
        name="tDAI",
        symbol="tDAI",
        decimals=5,
        max_faucet_amount=1e10,
    )

    tdai_id = vega.find_asset_id(symbol="tDAI")
    vega.mint(
        MM_WALLET.name,
        asset=tdai_id,
        amount=10000000000,
    )

    vega.create_simple_market(
        market_name="BTC:DAI_Mar22",
        proposal_wallet=MM_WALLET.name,
        settlement_asset_id=tdai_id,
        termination_wallet=TERMINATE_WALLET.name,
    )
