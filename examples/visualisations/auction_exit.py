"""auction_exit.py

Script launches an example of a market which is suspended and put into a monitoring
auction after price monitoring bounds are breached. When the auction ends the trades
causing the auction to exist should incur no maker fee.

When running the example with the --console flag, the user will be able to inspect the
positions of the following parties:

    • TRADER_A: buyer when exiting auction
    • TRADER_B: seller when exiting auction

Usage:

    python -m examples.visualisations.auction_exit --console --pause

Flags:

    --console   will launch the console
    --debug     will log debug messages 
    --pause     will pause the script after each price movement

"""

import argparse
import logging

from collections import namedtuple
from numpy.random import RandomState

from vega_sim.null_service import VegaServiceNull
from examples.visualisations.utils import continuous_market, move_market, Visualisation

from vega_sim.scenario.common.utils.price_process import random_walk


PartyConfig = namedtuple("WalletConfig", ["wallet_name", "key_name"])

WALLET_NAME = "vega"

TRADER_A = PartyConfig(wallet_name=WALLET_NAME, key_name="Trader A Party")
TRADER_B = PartyConfig(wallet_name=WALLET_NAME, key_name="Trader B Party")


class AuctionExitVisualisation(Visualisation):
    START_PRICE = 500

    SEED = None

    def run(self, pause: bool = False, test: bool = False):
        # Setup a market and move it into a continuous trading state
        market_id, asset_id, best_ask_id, best_bid_id = continuous_market(
            vega=self.vega,
            price=self.START_PRICE,
            spread=10,
            maker_fee=0.001,
            liquidity_fee=0.001,
            infrastructure_fee=0.001,
            simple_price_monitoring=False,
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
            amount=1e9,
        )
        self.vega.mint(
            wallet_name=TRADER_B.wallet_name,
            key_name=TRADER_B.key_name,
            asset=asset_id,
            amount=1e9,
        )
        self.vega.wait_fn(1)
        self.vega.wait_for_total_catchup()

        logging.info(
            "Trader A Party: public_key ="
            f" {self.vega.wallet.public_key(name=TRADER_A.key_name, wallet_name=TRADER_A.wallet_name)}"
        )
        logging.info(
            "Trader B Party: public_key ="
            f" {self.vega.wallet.public_key(name=TRADER_B.key_name, wallet_name=TRADER_B.wallet_name)}"
        )

        if pause:
            input(f"Paused after trader initialisation. View a public key.")

        # Go through market movements
        price_process = random_walk(
            num_steps=60,
            random_state=RandomState(self.SEED),
            sigma=1,
            starting_price=self.START_PRICE,
        )
        for price in price_process:
            move_market(
                vega=self.vega,
                market_id=market_id,
                best_ask_id=best_ask_id,
                best_bid_id=best_bid_id,
                price=price,
                spread=10,
                volume=1,
            )
            self.vega.wait_fn(30)
            self.vega.wait_for_total_catchup()
        if pause:
            input("Pausing before triggering auction.")

        # Trigger a price monitoring auction
        move_market(
            vega=self.vega,
            market_id=market_id,
            best_ask_id=best_ask_id,
            best_bid_id=best_bid_id,
            price=10000,
            spread=10,
            volume=1,
        )
        self.vega.wait_fn(1)
        if pause:
            input("Pausing after triggering auction.")

        # Return market to sensible price
        move_market(
            vega=self.vega,
            market_id=market_id,
            best_ask_id=best_ask_id,
            best_bid_id=best_bid_id,
            price=price_process[-1],
            spread=10,
            volume=1,
        )
        self.vega.wait_fn(1)
        self.vega.submit_order(
            trading_wallet=TRADER_A.wallet_name,
            trading_key=TRADER_A.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_BUY",
            volume=100,
            price=price_process[-1],
        )
        self.vega.wait_fn(1)
        self.vega.submit_order(
            trading_wallet=TRADER_B.wallet_name,
            trading_key=TRADER_B.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=100,
            price=price_process[-1],
        )
        self.vega.wait_fn(1)
        self.vega.wait_fn(60)
        self.vega.wait_for_total_catchup()

        if pause:
            input("Pausing after exiting auction.")

        if test:
            trader_a_trades = self.vega.get_trades(
                market_id=market_id,
                wallet_name=TRADER_A.wallet_name,
                key_name=TRADER_A.key_name,
            )
            trader_b_trades = self.vega.get_trades(
                market_id=market_id,
                wallet_name=TRADER_B.wallet_name,
                key_name=TRADER_B.key_name,
            )
            for trade in trader_a_trades:
                assert trade.buyer_fee.maker_fee == 0
                assert trade.seller_fee.maker_fee == 0
            for trade in trader_b_trades:
                assert trade.buyer_fee.maker_fee == 0
                assert trade.seller_fee.maker_fee == 0


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
        vis = AuctionExitVisualisation(vega=vega)
        vis.run(pause=args.pause, test=True)
