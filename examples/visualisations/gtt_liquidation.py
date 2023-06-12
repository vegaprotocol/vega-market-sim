"""gtt_liquidation.py

Script visualises an example where a large expired GTT order causes a party to
be closed out as margin levels are not recalculated after a GTT order expires.

Method:

1. PARTY A takes on a short position in MARKET A - this is the position to be liquidated
2. PARTY A takes on a short position in MARKET B
3. PARTY A places a large GTT sell order in MARKET B which we immediately expire

At this point PARTY A wil have a large proportion of their funds locked in the margin
account for MARKET B as a result of the expired GTT short order. No funds were released
from this account when the order expired as margin levels were not recalculated and
PARTY A had an open position in MARKET B. As long as margin calculations are not
triggered for PARTY A in MARKET B, the funds will not be released.

4. Gradually increase the mark price in MARKET B

Eventually PARTY A will not have enough funds left in there general account to support
their position in MARKET A. The funds currently locked in the margin account of MARKET B
will also not be used to support their position in MARKET A despite the fact they have
no position and no open orders in MARKET B.
"""

import argparse
import logging

from typing import Optional
from vega_sim.null_service import VegaServiceNull
from vega_sim.api.market import MarketConfig
from vega_sim.scenario.configurable_market.agents import ConfigurableMarketManager
from examples.visualisations.utils import (
    create_auxiliary_parties,
    mint_settlement_asset,
    provide_liquidity,
    exit_auction,
    move_market,
)
from vega_sim.scenario.common.agents import (
    ExponentialShapedMarketMaker,
    MarketOrderTrader,
)

# Global variables
PARTY_A = "party_a"
PARTY_B = "party_b"

ASSET = "asset"
MARKET_A = "MKT_A"
MARKET_B = "MKT_B"

STEPS = 20
PRICE_PROCESS = [1000 + i * 10 for i in range(STEPS)]


def main(console: Optional[bool] = False):
    with VegaServiceNull(
        run_with_console=console, warn_on_raw_data_access=False
    ) as vega:
        ConfigurableMarketManager(
            proposal_key_name="_",
            termination_key_name="_",
            market_name=MARKET_A,
            market_code=MARKET_A,
            asset_name=ASSET,
            asset_dp=18,
        ).initialise(vega=vega)
        ConfigurableMarketManager(
            proposal_key_name="_",
            termination_key_name="_",
            market_name=MARKET_B,
            market_code=MARKET_B,
            asset_name=ASSET,
            asset_dp=18,
        ).initialise(vega=vega)

        market_a_id = vega.find_market_id(name=MARKET_A)
        market_b_id = vega.find_market_id(name=MARKET_B)
        asset_id = vega.find_asset_id(symbol=ASSET)

        # Create the auxiliaries
        create_auxiliary_parties(vega)
        mint_settlement_asset(vega=vega, asset_id=asset_id)

        provide_liquidity(vega, market_a_id)
        provide_liquidity(vega, market_b_id)

        best_ask_a, best_bid_a = exit_auction(
            vega, market_a_id, PRICE_PROCESS[0], 10, 1
        )
        best_ask_b, best_bid_b = exit_auction(
            vega, market_b_id, PRICE_PROCESS[0], 10, 1
        )

        # Create the parties
        vega.create_key(name=PARTY_A)
        vega.mint(key_name=PARTY_A, asset=asset_id, amount=2000)
        vega.create_key(name=PARTY_B)
        vega.mint(key_name=PARTY_B, asset=asset_id, amount=2000)

        # Party A takes a large short position in Market A
        vega.submit_order(
            trading_key=PARTY_A,
            market_id=market_a_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_SELL",
            price=PRICE_PROCESS[0],
            volume=5,
        )
        vega.submit_order(
            trading_key=PARTY_B,
            market_id=market_a_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY",
            price=PRICE_PROCESS[0],
            volume=5,
        )
        # Party A takes a small short position in Market b
        vega.submit_order(
            trading_key=PARTY_A,
            market_id=market_b_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_SELL",
            price=PRICE_PROCESS[0],
            volume=1,
        )
        vega.submit_order(
            trading_key=PARTY_B,
            market_id=market_b_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY",
            price=PRICE_PROCESS[0],
            volume=1,
        )
        vega.wait_fn(1)

        # Part A submits a large short GTT order in market b and we expire it
        vega.submit_order(
            trading_key=PARTY_A,
            market_id=market_b_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTT",
            side="SIDE_SELL",
            price=PRICE_PROCESS[0],
            volume=105,
        )
        vega.wait_fn(240)

        logging.info(vega.wallet.public_key(name=PARTY_A))
        # input("Waiting after GTT order expired.")

        # Gradually increment the price in market b to avoid price monitoring auctions
        for price in PRICE_PROCESS:
            move_market(vega, market_a_id, best_ask_a, best_bid_a, price, 10, 1)
            vega.wait_fn(300)

            positions = vega.positions_by_market(key_name=PARTY_A)
            accounts = vega.list_accounts(key_name=PARTY_A, asset_id=asset_id)
            if positions[market_a_id].open_volume == 0:
                logging.info("Party A closed out in Market A!")
                logging.info(f"liquidation_price={price}")
                logging.info(
                    f"remaining_funds={sum([account.balance for account in accounts])}"
                )
                return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--console", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main(console=args.console)
