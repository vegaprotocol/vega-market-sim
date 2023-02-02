"""loss_socialisation.py

Script launches an example of a market moving against a party with a short-position
whom is eventually closed out. When the party is closed out they do not have sufficient
collateral in their margin account to cover their losses and loss-socialisation is
required.

When running the example with the --console flag, the user will be able to inspect the
positions of the following parties:

    • TRADER_A: party with long position
    • TRADER_B: party with short position (closed out)

Usage:

    python -m examples.visualisations.loss_socialisation --console --pause

Flags:

    --console   will launch the console
    --debug     will log debug messages 
    --pause     will pause the script after each price movement

"""

import argparse
import logging

from typing import Optional
from collections import namedtuple

from vega_sim.null_service import VegaServiceNull
from examples.visualisations.utils import continuous_market, move_market

PartyConfig = namedtuple("WalletConfig", ["wallet_name", "wallet_pass", "key_name"])

WALLET_NAME = "vega"
WALLET_PASS = "pass"

TRADER_A = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="Trader A Party"
)
TRADER_B = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="Trader B Party"
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--console", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--pause", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    with VegaServiceNull(
        run_with_console=args.console,
        warn_on_raw_data_access=False,
    ) as vega:
        # Setup a market and move it into a continuous trading state
        market_id, asset_id, best_ask_id, best_bid_id = continuous_market(
            vega=vega, price=500, spread=10
        )

        # Create wallets and keys for traders
        vega.create_wallet(
            name=TRADER_A.wallet_name,
            passphrase=TRADER_A.wallet_pass,
            key_name=TRADER_A.key_name,
        )
        vega.create_wallet(
            name=TRADER_B.wallet_name,
            passphrase=TRADER_B.wallet_pass,
            key_name=TRADER_B.key_name,
        )
        vega.wait_for_total_catchup()
        vega.wait_fn(60)

        # Mint settlement assets for traders
        vega.mint(
            wallet_name=TRADER_A.wallet_name,
            key_name=TRADER_A.key_name,
            asset=asset_id,
            amount=20000,
        )
        vega.mint(
            wallet_name=TRADER_B.wallet_name,
            key_name=TRADER_B.key_name,
            asset=asset_id,
            amount=20000,
        )
        vega.wait_for_total_catchup()
        vega.wait_fn(60)

        # Open positions for traders
        vega.submit_order(
            trading_wallet=TRADER_A.wallet_name,
            key_name=TRADER_A.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_BUY",
            volume=100,
            price=500,
        )
        vega.submit_order(
            trading_wallet=TRADER_B.wallet_name,
            key_name=TRADER_B.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=100,
            price=500,
        )
        vega.wait_for_total_catchup()
        vega.wait_fn(60)

        # Pause to allow user to login to wallet on console
        if args.pause:
            input(f"Paused at price 500. Press Enter to continue.")

        # Go through market movements
        for price in [550, 600, 650, 710]:
            move_market(
                vega=vega,
                market_id=market_id,
                best_ask_id=best_ask_id,
                best_bid_id=best_bid_id,
                price=price,
                spread=10,
                volume=1,
            )
            vega.wait_for_total_catchup()
            vega.wait_fn(60)
            if args.pause:
                input(f"Paused at price {price}. Press Enter to continue.")
