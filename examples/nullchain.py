import logging
from collections import namedtuple

from vega_sim.null_service import VegaServiceNull


WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Set up parties in the market/ Submit liquidity provision/ Control midprice
MM_WALLET = WalletConfig("mm", "pin")

# The party to send selling/buying MOs to hit LP orders
TRADER_WALLET = WalletConfig("Zl3pLs6Xk6SwIK7Jlp2x", "bJQDDVGAhKkj3PVCc7Rr")

# The party randomly post LOs at buy/sell side to simulate real Market situation
RANDOM_WALLET = WalletConfig("OJpVLvU5fgLJbhNPdESa", "GmJTt9Gk34BHDlovB7AJ")

# The party to terminate the market and send settlment price
TERMINATE_WALLET = WalletConfig("FJMKnwfZdd48C8NqvYrG", "bY3DxwtsCstMIIZdNpKs")

wallets = [MM_WALLET, TRADER_WALLET, RANDOM_WALLET, TERMINATE_WALLET]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with VegaServiceNull(run_wallet_with_console=False) as vega:

        for wallet in wallets:
            vega.create_wallet(wallet.name, wallet.passphrase)

        vega.mint(
            MM_WALLET.name,
            asset="VOTE",
            amount=1e4,
        )

        vega.update_network_parameter(
            MM_WALLET, parameter="market.fee.factors.makerFee", new_value="0.1"
        )

        vega.forward("10s")
        vega.create_asset(
            MM_WALLET.name,
            name="tDAI",
            symbol="tDAI",
            decimals=5,
            max_faucet_amount=1e10,
        )

        tdai_id = vega.find_asset_id(symbol="tDAI")
        print("TDAI: ", tdai_id)

        vega.mint(
            MM_WALLET.name,
            asset=tdai_id,
            amount=1e5,
        )
        vega.forward("10s")
        vega.create_simple_market(
            market_name="BTC:DAI_Mar22",
            proposal_wallet=MM_WALLET.name,
            settlement_asset_id=tdai_id,
            termination_wallet=TERMINATE_WALLET.name,
        )

        market_id = vega.all_markets()[0].id

        vega.submit_simple_liquidity(
            wallet_name=MM_WALLET.name,
            market_id=market_id,
            commitment_amount=1.9,
            fee=0.002,
            reference_buy="PEGGED_REFERENCE_MID",
            reference_sell="PEGGED_REFERENCE_MID",
            delta_buy=0.5,
            delta_sell=0.5,
            is_amendment=True,
        )

        vega.submit_order(
            trading_wallet=MM_WALLET.name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=10,
            price=100.5,
        )

        vega.settle_market(
            settlement_wallet=TERMINATE_WALLET.name,
            settlement_price=100,
            market_id=market_id,
        )
