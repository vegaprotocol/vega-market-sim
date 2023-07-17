"""ethcc.py

Script launches an example of a market being simply created then working through the 
various steps required to open.

Usage:

    python -m examples.visualisations.ethcc --console --pause

Flags:

    --console   will launch the console
    --debug     will log debug messages 
    --pause     will pause the script after each price movement

"""

import argparse
import logging

from collections import namedtuple

from vega_sim.null_service import VegaServiceNull
from examples.visualisations.utils import (
    continuous_market,
    move_market,
    Visualisation,
    create_auxiliary_parties,
    mint_governance_asset,
    mint_settlement_asset,
)

PartyConfig = namedtuple("WalletConfig", ["wallet_name", "key_name"])

WALLET_NAME = "auxiliary_parties_wallet"

AUX_PARTY_A = PartyConfig(wallet_name=WALLET_NAME, key_name="Market Proposer")
AUX_PARTY_B = PartyConfig(wallet_name=WALLET_NAME, key_name="Market Settler")
AUX_PARTY_C = PartyConfig(wallet_name=WALLET_NAME, key_name="Liquidity Provider")
AUX_PARTY_D = PartyConfig(wallet_name=WALLET_NAME, key_name="Asks Provider")
AUX_PARTY_E = PartyConfig(wallet_name=WALLET_NAME, key_name="Bids Provider")

WALLET_NAME = "vega"

TRADER_A = PartyConfig(wallet_name=WALLET_NAME, key_name="Trader A Party")
TRADER_B = PartyConfig(wallet_name=WALLET_NAME, key_name="Trader B Party")


class BasicOpenMarketVisualisation(Visualisation):
    TRADER_MINT = 20000
    TRADER_POSITION = 100

    def run(self, pause: bool = False, test: bool = False):
        # Setup a market and move it into a continuous trading state
        # market_id, asset_id, best_ask_id, best_bid_id = continuous_market(
        #     vega=self.vega, price=500, spread=10
        # )
        open_price = 100
        open_spread = 1

        create_auxiliary_parties(vega=vega)
        mint_governance_asset(vega=vega)

        # First, we create the asset
        vega.create_asset(
            wallet_name=AUX_PARTY_A.wallet_name,
            key_name=AUX_PARTY_A.key_name,
            name="STABLE_1",
            symbol="STABL",
            decimals=5,
            max_faucet_amount=1e9,
        )
        vega.wait_for_total_catchup()

        asset_id = vega.find_asset_id(symbol="STABL")
        mint_settlement_asset(vega=vega, asset_id=asset_id)

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
            "Trader A Party: public_key ="
            f" {self.vega.wallet.public_key(name=TRADER_A.key_name, wallet_name=TRADER_A.wallet_name)}"
        )
        logging.info(
            "Trader B Party: public_key ="
            f" {self.vega.wallet.public_key(name=TRADER_B.key_name, wallet_name=TRADER_B.wallet_name)}"
        )

        if pause:
            input("Ok, we've created the assets.")

        vega.create_simple_market(
            market_name="XYZ:STABL Dec23",
            wallet_name=AUX_PARTY_A.wallet_name,
            proposal_key=AUX_PARTY_A.key_name,
            termination_wallet_name=AUX_PARTY_A.wallet_name,
            termination_key=AUX_PARTY_A.key_name,
            settlement_asset_id=asset_id,
            market_decimals=3,
        )
        vega.wait_for_total_catchup()
        market_id = vega.all_markets()[0].id

        if pause:
            input("And a market.")

        vega.submit_simple_liquidity(
            wallet_name=AUX_PARTY_C.wallet_name,
            key_name=AUX_PARTY_C.key_name,
            market_id=market_id,
            is_amendment=False,
            commitment_amount=10000,
            fee=0.00,
            reference_buy="PEGGED_REFERENCE_BEST_BID",
            reference_sell="PEGGED_REFERENCE_BEST_ASK",
            delta_buy=1,
            delta_sell=1,
        )

        if pause:
            input("Now the market has an LP.")

        vega.submit_order(
            trading_wallet=AUX_PARTY_D.wallet_name,
            trading_key=AUX_PARTY_D.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=10,
            price=open_price + open_spread / 2,
            order_ref="best-ask",
        )
        vega.submit_order(
            trading_wallet=AUX_PARTY_E.wallet_name,
            trading_key=AUX_PARTY_E.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_BUY",
            volume=10,
            price=open_price - open_spread / 2,
            order_ref="best-bid",
        )
        vega.submit_order(
            trading_wallet=AUX_PARTY_D.wallet_name,
            trading_key=AUX_PARTY_E.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=1,
            price=open_price,
        )
        vega.submit_order(
            trading_wallet=AUX_PARTY_E.wallet_name,
            trading_key=AUX_PARTY_E.key_name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_BUY",
            volume=1,
            price=open_price,
        )

        if pause:
            input("Ready for takeoff!")

        self.vega.wait_fn(1)

        if pause:
            input("And we're open!")

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
                f"Paused at price 500. Trader B should have a short position. Press"
                f" Enter to continue."
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
        vis = BasicOpenMarketVisualisation(vega=vega)
        vis.run(pause=args.pause, test=True)
