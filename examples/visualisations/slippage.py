import argparse
import logging

from collections import namedtuple

from vega_sim.null_service import VegaServiceNull
from examples.visualisations.utils import continuous_market, move_market

PartyConfig = namedtuple("WalletConfig", ["wallet_name", "wallet_pass", "key_name"])

WALLET_NAME = "vega"
WALLET_PASS = "pass"


SHORT_TRADER = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="Short Trader"
)
LONG_TRADER = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="Long Trader"
)
TOXIC_TRADER = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="Toxic Trader"
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--console", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--pause", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    initial_price = 500
    final_price = 1000

    spread = 10

    with VegaServiceNull(
        run_with_console=args.console,
        warn_on_raw_data_access=False,
    ) as vega:
        # Setup a market and move it into a continuous trading state
        market_id, asset_id, best_ask_id, best_bid_id = continuous_market(
            vega=vega, price=initial_price, spread=spread
        )

        # Create wallets and keys for traders
        vega.create_wallet(
            name=SHORT_TRADER.wallet_name,
            passphrase=SHORT_TRADER.wallet_pass,
            key_name=SHORT_TRADER.key_name,
        )
        vega.create_wallet(
            name=LONG_TRADER.wallet_name,
            passphrase=LONG_TRADER.wallet_pass,
            key_name=LONG_TRADER.key_name,
        )
        vega.create_wallet(
            name=TOXIC_TRADER.wallet_name,
            passphrase=TOXIC_TRADER.wallet_pass,
            key_name=TOXIC_TRADER.key_name,
        )
        vega.wait_for_total_catchup()
        vega.wait_fn(60)

        # Mint settlement assets for traders
        vega.mint(
            wallet_name=SHORT_TRADER.wallet_name,
            key_name=SHORT_TRADER.key_name,
            asset=asset_id,
            amount=1e5,
        )
        vega.mint(
            wallet_name=LONG_TRADER.wallet_name,
            key_name=LONG_TRADER.key_name,
            asset=asset_id,
            amount=1e9,
        )
        vega.mint(
            wallet_name=TOXIC_TRADER.wallet_name,
            key_name=TOXIC_TRADER.key_name,
            asset=asset_id,
            amount=1e9,
        )

        input(
            f"Paused. Use console 'View As' feature with public_key = {vega.wallet.public_key(name=SHORT_TRADER.wallet_name, key_name=SHORT_TRADER.key_name)}"
        )

        vega.wait_fn(60)
        vega.wait_for_total_catchup()

        # Open positions for traders
        vega.submit_order(
            trading_wallet=SHORT_TRADER.wallet_name,
            key_name=SHORT_TRADER.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=200,
            price=500,
        )
        vega.submit_order(
            trading_wallet=LONG_TRADER.wallet_name,
            key_name=LONG_TRADER.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_BUY",
            volume=200,
            price=500,
        )

        vega.wait_fn(60)
        vega.wait_for_total_catchup()

        if args.pause:
            input(f"Paused. Trader takes a short position.")

        move_market(
            vega,
            market_id=market_id,
            best_ask_id=best_ask_id,
            best_bid_id=best_bid_id,
            price=499,
            spread=spread,
            volume=1,
        )
        vega.wait_fn(60)
        vega.wait_for_total_catchup()

        if args.pause:
            input(f"Paused. Market moves in traders favour.")

        vega.submit_order(
            trading_wallet=TOXIC_TRADER.wallet_name,
            key_name=TOXIC_TRADER.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=1,
            price=10e6,
        )
        vega.wait_fn(60)
        vega.wait_for_total_catchup()

        if args.pause:
            input(
                f"Paused. Toxic trader places an order at high price, check the order book."
            )

        move_market(
            vega,
            market_id=market_id,
            best_ask_id=best_ask_id,
            best_bid_id=best_bid_id,
            price=498,
            spread=spread,
            volume=1,
        )
        vega.wait_fn(60)
        vega.wait_for_total_catchup()

        if args.pause:
            input(
                f"Paused. Market moves triggering margin recalculations, margin spikes."
            )

        vega.submit_order(
            trading_wallet=LONG_TRADER.wallet_name,
            key_name=LONG_TRADER.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=29,
            price=505,
        )
        vega.wait_fn(60)
        vega.wait_for_total_catchup()

        if args.pause:
            input(
                f"Paused. Sufficient orders placed on book for short trader to be closed out if necessary."
            )

        move_market(
            vega,
            market_id=market_id,
            best_ask_id=best_ask_id,
            best_bid_id=best_bid_id,
            price=497,
            spread=spread,
            volume=1,
        )
        vega.wait_fn(60)
        vega.wait_for_total_catchup()

        print(
            vega.margin_levels(
                wallet_name=SHORT_TRADER.wallet_name,
                key_name=SHORT_TRADER.key_name,
                market_id=market_id,
            )
        )

        if args.pause:
            input(f"Paused. Party should be closed out.")
