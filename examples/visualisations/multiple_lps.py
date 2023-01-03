import argparse
import logging

from collections import namedtuple

from vega_sim.null_service import VegaServiceNull
import examples.visualisations.utils as utils

PartyConfig = namedtuple("WalletConfig", ["wallet_name", "wallet_pass", "key_name"])

WALLET_NAME = "vega"
WALLET_PASS = "pass"


LP_A = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="LP A Party"
)
LP_B = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="LP B Party"
)
LP_C = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="LP C Party"
)


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
        launch_graphql=True,
    ) as vega:

        # Create wallets for auxiliary and example specific parties
        utils.create_auxiliary_parties(vega=vega)
        vega.create_wallet(
            name=LP_A.wallet_name, key_name=LP_A.key_name, passphrase=LP_A.wallet_pass
        )
        vega.create_wallet(
            name=LP_B.wallet_name, key_name=LP_B.key_name, passphrase=LP_B.wallet_pass
        )
        vega.create_wallet(
            name=LP_C.wallet_name, key_name=LP_C.key_name, passphrase=LP_C.wallet_pass
        )

        # Mint governance asset for auxiliary parties and create settlement asset
        utils.mint_governance_asset(vega=vega)
        asset_id = utils.propose_asset(vega=vega)

        # Mint assets for auxiliary and example specific parties
        utils.mint_settlement_asset(vega=vega, asset_id=asset_id)
        vega.mint(
            wallet_name=LP_A.wallet_name,
            key_name=LP_A.key_name,
            asset=asset_id,
            amount=1e9,
        )
        vega.mint(
            wallet_name=LP_B.wallet_name,
            key_name=LP_B.key_name,
            asset=asset_id,
            amount=1e9,
        )
        vega.mint(
            wallet_name=LP_C.wallet_name,
            key_name=LP_C.key_name,
            asset=asset_id,
            amount=1e9,
        )

        # Create the market
        market_id = utils.propose_market(vega=vega, asset_id=asset_id)

        # Each LP party submits a liquidity provision at different fees
        vega.submit_simple_liquidity(
            wallet_name=LP_A.wallet_name,
            key_name=LP_A.key_name,
            market_id=market_id,
            commitment_amount=15000,
            fee=0.01,
            reference_buy="PEGGED_REFERENCE_MID",
            reference_sell="PEGGED_REFERENCE_MID",
            delta_buy=1,
            delta_sell=1,
            is_amendment=False,
        )
        vega.submit_simple_liquidity(
            wallet_name=LP_B.wallet_name,
            key_name=LP_B.key_name,
            market_id=market_id,
            commitment_amount=15000,
            fee=0.02,
            reference_buy="PEGGED_REFERENCE_MID",
            reference_sell="PEGGED_REFERENCE_MID",
            delta_buy=5,
            delta_sell=5,
            is_amendment=False,
        )
        vega.submit_simple_liquidity(
            wallet_name=LP_C.wallet_name,
            key_name=LP_C.key_name,
            market_id=market_id,
            commitment_amount=15000,
            fee=0.03,
            reference_buy="PEGGED_REFERENCE_MID",
            reference_sell="PEGGED_REFERENCE_MID",
            delta_buy=10,
            delta_sell=10,
            is_amendment=False,
        )

        # Exit auction
        best_bid_id, best_ask_id = utils.exit_auction(
            vega=vega, market_id=market_id, price=1000, spread=1, volume=10
        )
        vega.wait_fn(120)

        # Place trades so open interest is ~200 and target stake is >10000
        utils.move_market(
            vega=vega,
            market_id=market_id,
            best_bid_id=best_bid_id,
            best_ask_id=best_ask_id,
            price=1000,
            spread=1,
            volume=200,
        )
        vega.wait_for_total_catchup()
        input(
            "Pause simulation to allow UI to be inspected. "
            + "Fee should be updated to 0.01 (1.00%)"
        )

        # Place trades so open interest is ~400 and target stake is >20000
        utils.move_market(
            vega=vega,
            market_id=market_id,
            best_bid_id=best_bid_id,
            best_ask_id=best_ask_id,
            price=1000,
            spread=1,
            volume=200,
        )
        vega.wait_for_total_catchup()
        input(
            "Pause simulation to allow UI to be inspected. "
            + "Fee should be updated to 0.02 (2.00%)."
        )

        # Place trades so open interest is ~600 and target stake is >30000
        utils.move_market(
            vega=vega,
            market_id=market_id,
            best_bid_id=best_bid_id,
            best_ask_id=best_ask_id,
            price=1000,
            spread=1,
            volume=200,
        )
        vega.wait_for_total_catchup()
        input(
            "Pause simulation to allow UI to be inspected. "
            + "Fee should be updated to 0.03 (3.00%)"
        )
