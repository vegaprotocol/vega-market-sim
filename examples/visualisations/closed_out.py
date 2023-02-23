"""closed_out.py

Script launches an example of a market moving against a party with a short-position
whom is eventually closed out. When the party is closed out they have sufficient
collateral in their margin account to cover their losses and loss-socialisation is not
required.

When running the example with the --console flag, the user will be able to inspect the
positions of the following parties:

    • TRADER_A: party with long position
    • TRADER_B: party with short position (closed out)

Usage:

    python -m examples.visualisations.closed_out --console --pause

Flags:

    --console   will launch the console
    --debug     will log debug messages 
    --pause     will pause the script after each price movement

"""

import argparse
import logging

from collections import namedtuple

from vega_sim.null_service import VegaServiceNull
from examples.visualisations.utils import continuous_market, move_market, Visualisation

PartyConfig = namedtuple("WalletConfig", ["wallet_name", "key_name"])

WALLET_NAME = "vega"

TRADER_A = PartyConfig(wallet_name=WALLET_NAME, key_name="Trader A Party")
TRADER_B = PartyConfig(wallet_name=WALLET_NAME, key_name="Trader B Party")


class CloseOutVisualisation(Visualisation):
    TRADER_MINT = 20000
    TRADER_POSITION = 100

    def run(self, pause: bool = False, test: bool = False):
        # Setup a market and move it into a continuous trading state
        market_id, asset_id, best_ask_id, best_bid_id = continuous_market(
            vega=self.vega, price=500, spread=10
        )

        # Create wallets and keys for traders
        self.vega.create_key(
            name=TRADER_A.key_name,
            wallet_name=TRADER_A.wallet_name,
        )
        self.vega.create_key(
            name=TRADER_B.key_name,
            wallet_name=TRADER_B.wallet_name,
        )
        self.vega.wait_for_total_catchup()
        self.vega.wait_fn(60)

        # Mint settlement assets for traders
        self.vega.mint(
            wallet_name=TRADER_A.wallet_name,
            key_name=TRADER_A.key_name,
            asset=asset_id,
            amount=self.TRADER_MINT,
        )
        self.vega.mint(
            wallet_name=TRADER_B.wallet_name,
            key_name=TRADER_B.key_name,
            asset=asset_id,
            amount=self.TRADER_MINT,
        )
        self.vega.wait_for_total_catchup()
        self.vega.wait_fn(60)

        logging.info(
            f"Trader A Party: public_key = {self.vega.wallet.public_key(name=TRADER_A.key_name, wallet_name=TRADER_A.wallet_name)}"
        )
        logging.info(
            f"Trader B Party: public_key = {self.vega.wallet.public_key(name=TRADER_B.key_name, wallet_name=TRADER_B.wallet_name)}"
        )

        if pause:
            input(f"Paused after trader initialisation. View a public key.")

        # Open positions for traders
        self.vega.submit_order(
            trading_wallet=TRADER_A.wallet_name,
            trading_key=TRADER_A.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_BUY",
            volume=self.TRADER_POSITION,
            price=500,
        )
        self.vega.submit_order(
            trading_wallet=TRADER_B.wallet_name,
            trading_key=TRADER_B.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=self.TRADER_POSITION,
            price=500,
        )
        self.vega.wait_for_total_catchup()
        self.vega.wait_fn(60)

        # Pause to allow user to login to wallet on console
        if pause:
            input(
                f"Paused at price 500. Trader B should have a short position. Press Enter to continue."
            )

        # Go through market movements
        for price in [550, 600, 650, 700]:
            move_market(
                vega=self.vega,
                market_id=market_id,
                best_ask_id=best_ask_id,
                best_bid_id=best_bid_id,
                price=price,
                spread=10,
                volume=1,
            )
            self.vega.wait_for_total_catchup()
            self.vega.wait_fn(60)

            if pause:
                if price == 700:
                    input(
                        f"Paused at price {price}. Trader B should have been closed out. Press Enter to continue."
                    )
                else:
                    input(
                        f"Paused at price {price}. Trader B margin should have increased. Press Enter to continue."
                    )

            if test:
                trader_a_position = self.vega.positions_by_market(
                    wallet_name=TRADER_A.wallet_name,
                    key_name=TRADER_A.key_name,
                    market_id=market_id,
                )
                trader_b_position = self.vega.positions_by_market(
                    wallet_name=TRADER_B.wallet_name,
                    key_name=TRADER_B.key_name,
                    market_id=market_id,
                )
                if price == 700:
                    # Check Trader B closed out and Trader A position still open
                    assert trader_a_position.open_volume == self.TRADER_POSITION
                    assert trader_a_position.unrealised_pnl > 0
                    assert trader_b_position.open_volume == 0
                    assert trader_b_position.unrealised_pnl == 0
                    # Check loss socialisation was not required for close out
                    assert trader_a_position.loss_socialisation_amount == 0
                    assert trader_b_position.loss_socialisation_amount == 0
                else:
                    # Check Trader A and Trader B positions are still open
                    assert trader_a_position.open_volume == self.TRADER_POSITION
                    assert trader_a_position.unrealised_pnl > 0
                    assert trader_b_position.open_volume == -self.TRADER_POSITION
                    assert trader_b_position.unrealised_pnl < 0


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
        vis = CloseOutVisualisation(vega=vega)
        vis.run(pause=args.pause, test=True)
