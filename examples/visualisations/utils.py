"""utils.py

Module contains utility functions for creating, moving, and settling a market using
default auxiliary parties as well as utility functions for managing the parties. For
use of the functions, the following parties are setup.

    • AUX_PARTY_A       responsible for proposing a market
    • AUX_PARTY_B       responsible for settling a market
    • AUX_PARTY_C       responsible for providing liquidity
    • AUX_PARTY_D       responsible for submitting bids
    • AUX_PARTY_E       responsible for submitting asks
    
"""

from collections import namedtuple
from curses import KEY_A1
from typing import Optional, List
from vega_sim.null_service import VegaServiceNull

PartyConfig = namedtuple("WalletConfig", ["wallet_name", "wallet_pass", "key_name"])

WALLET_NAME = "auxiliary_parties_wallet"
WALLET_PASS = "passphrase"

AUX_PARTY_A = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="Market Proposer"
)
AUX_PARTY_B = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="Market Settler"
)
AUX_PARTY_C = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="Liquidity Provider"
)
AUX_PARTY_D = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="Asks Provider"
)
AUX_PARTY_E = PartyConfig(
    wallet_name=WALLET_NAME, wallet_pass=WALLET_PASS, key_name="Bids Provider"
)


def continuous_market(
    vega: VegaServiceNull,
    price: float,
    spread: float,
):
    """_summary_

    Args:
        vega (VegaServiceNull):
            _description_
    """

    create_auxiliary_parties(vega=vega)

    mint_governance_asset(vega=vega)

    asset_id = propose_asset(vega=vega)
    mint_settlement_asset(vega=vega, asset_id=asset_id)

    market_id = propose_market(vega=vega, asset_id=asset_id)
    provide_liquidity(vega=vega, market_id=market_id)

    best_ask_id, best_bid_id = exit_auction(
        vega=vega,
        market_id=market_id,
        price=price,
        spread=spread,
        volume=150,
    )

    return market_id, asset_id, best_ask_id, best_bid_id


def create_auxiliary_parties(
    vega: VegaServiceNull,
):
    for party in [AUX_PARTY_A, AUX_PARTY_B, AUX_PARTY_C, AUX_PARTY_D, AUX_PARTY_E]:
        vega.create_wallet(
            name=party.wallet_name,
            passphrase=party.wallet_pass,
            key_name=party.key_name,
        )


def mint_governance_asset(
    vega: VegaServiceNull,
):
    """_summary_

    Args:
        vega (VegaServiceNull): _description_
    """

    for party in [AUX_PARTY_A, AUX_PARTY_B]:
        vega.mint(
            wallet_name=party.wallet_name,
            key_name=party.key_name,
            asset="VOTE",
            amount=1000,
        )
        vega.wait_for_total_catchup()


def mint_settlement_asset(
    vega: VegaServiceNull,
    asset_id: str,
):
    """_summary_

    Args:
        vega (VegaServiceNull): _description_
        asset_id (str): _description_
    """

    for party in [AUX_PARTY_A, AUX_PARTY_B, AUX_PARTY_C, AUX_PARTY_D, AUX_PARTY_E]:
        vega.mint(
            wallet_name=party.wallet_name,
            key_name=party.key_name,
            asset=asset_id,
            amount=1e9,
        )
        vega.wait_for_total_catchup()


def propose_asset(
    vega: VegaServiceNull,
):
    """_summary_

    Args:
        vega (VegaServiceNull): _description_

    Returns:
        _type_: _description_
    """
    vega.create_asset(
        wallet_name=AUX_PARTY_A.wallet_name,
        key_name=AUX_PARTY_A.key_name,
        name="fDAI",
        symbol="fDAI",
        decimals=5,
        max_faucet_amount=1e9,
    )
    vega.wait_for_total_catchup()
    return vega.find_asset_id(symbol="fDAI")


def propose_market(
    vega: VegaServiceNull,
    asset_id: str,
):
    """_summary_

    Args:
        vega (VegaServiceNull): _description_
        asset_id (str): _description_

    Returns:
        _type_: _description_
    """
    vega.update_network_parameter(
        proposal_wallet=AUX_PARTY_A.wallet_name,
        key_name=AUX_PARTY_A.key_name,
        parameter="market.fee.factors.infrastructureFee",
        new_value="0.0",
    )
    vega.update_network_parameter(
        proposal_wallet=AUX_PARTY_A.wallet_name,
        key_name=AUX_PARTY_A.key_name,
        parameter="market.fee.factors.makerFee",
        new_value="0.0",
    )
    vega.create_simple_market(
        market_name="XYZ:DAI Visualisation Example",
        proposal_wallet=AUX_PARTY_A.wallet_name,
        key_name=AUX_PARTY_A.key_name,
        termination_wallet=AUX_PARTY_A.wallet_name,
        termination_key=AUX_PARTY_A.key_name,
        settlement_asset_id=asset_id,
        market_decimals=3,
    )
    vega.wait_for_total_catchup()
    return vega.all_markets()[0].id


def exit_auction(
    vega: VegaServiceNull,
    market_id: str,
    price: Optional[float] = 1000.000,
    spread: Optional[float] = 2.000,
    volume: Optional[int] = 1,
):
    """_summary_

    Args:
        vega (VegaServiceNull):
            _description_
        market_id (str):
            _description_
        price (Optional[float], optional):
            _description_. Defaults to 1000.000.
        spread (Optional[float], optional):
            _description_. Defaults to 2.000.
        volume (Optional[int], optional):
            _description_. Defaults to 1.

    Returns:
        _type_: _description_
    """
    vega.submit_order(
        trading_wallet=AUX_PARTY_D.wallet_name,
        key_name=AUX_PARTY_D.key_name,
        market_id=market_id,
        time_in_force="TIME_IN_FORCE_GTC",
        order_type="TYPE_LIMIT",
        side="SIDE_SELL",
        volume=volume,
        price=price + spread / 2,
        order_ref="best-ask",
    )
    vega.submit_order(
        trading_wallet=AUX_PARTY_E.wallet_name,
        key_name=AUX_PARTY_E.key_name,
        market_id=market_id,
        time_in_force="TIME_IN_FORCE_GTC",
        order_type="TYPE_LIMIT",
        side="SIDE_BUY",
        volume=volume,
        price=price - spread / 2,
        order_ref="best-bid",
    )
    vega.submit_order(
        trading_wallet=AUX_PARTY_D.wallet_name,
        key_name=AUX_PARTY_E.key_name,
        market_id=market_id,
        time_in_force="TIME_IN_FORCE_GTC",
        order_type="TYPE_LIMIT",
        side="SIDE_SELL",
        volume=1,
        price=price,
    )
    vega.submit_order(
        trading_wallet=AUX_PARTY_E.wallet_name,
        key_name=AUX_PARTY_E.key_name,
        market_id=market_id,
        time_in_force="TIME_IN_FORCE_GTC",
        order_type="TYPE_LIMIT",
        side="SIDE_BUY",
        volume=1,
        price=price,
    )

    orders = vega.order_status_from_feed(live_only=True)
    best_ask_id, _ = list(
        orders.get(market_id, {})
        .get(
            vega.wallet.public_key(
                name=AUX_PARTY_D.wallet_name, key_name=AUX_PARTY_D.key_name
            ),
            {},
        )
        .items()
    )[0]
    best_bid_id, _ = list(
        orders.get(market_id, {})
        .get(
            vega.wallet.public_key(
                name=AUX_PARTY_E.wallet_name, key_name=AUX_PARTY_E.key_name
            ),
            {},
        )
        .items()
    )[0]

    return best_ask_id, best_bid_id


def provide_liquidity(
    vega: VegaServiceNull,
    market_id: str,
):
    """_summary_

    Args:
        vega (VegaServiceNull): _description_
        market_id (str): _description_
    """
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


def move_market(
    vega: VegaServiceNull,
    market_id: str,
    best_bid_id: str,
    best_ask_id: str,
    price: int,
    spread: float,
):
    """_summary_

    Args:
        vega (VegaServiceNull): _description_
        market_id (str): _description_
        best_bid_id (str): _description_
        best_ask_id (str): _description_
        price (int): _description_
        spread (float): _description_
    """

    market_data = vega.market_data(market_id=market_id)
    market_info = vega.market_info(market_id=market_id)

    curr_price = int(market_data.mid_price) * 10**-market_info.decimal_places

    if price > curr_price:
        # Amend best-bid and best-ask
        vega.amend_order(
            trading_wallet=AUX_PARTY_D.wallet_name,
            key_name=AUX_PARTY_D.key_name,
            order_id=best_ask_id,
            market_id=market_id,
            price=price + spread / 2,
        )
        vega.wait_for_total_catchup()
        vega.amend_order(
            trading_wallet=AUX_PARTY_E.wallet_name,
            key_name=AUX_PARTY_E.key_name,
            order_id=best_bid_id,
            market_id=market_id,
            price=price - spread / 2,
        )
        vega.wait_for_total_catchup()
    else:
        vega.amend_order(
            trading_wallet=AUX_PARTY_E.wallet_name,
            key_name=AUX_PARTY_E.key_name,
            order_id=best_bid_id,
            market_id=market_id,
            price=price - spread / 2,
        )
        vega.wait_for_total_catchup()
        vega.amend_order(
            trading_wallet=AUX_PARTY_D.wallet_name,
            key_name=AUX_PARTY_D.key_name,
            order_id=best_ask_id,
            market_id=market_id,
            price=price + spread / 2,
        )
        vega.wait_for_total_catchup()

    # Move mark-price
    vega.submit_order(
        trading_wallet=AUX_PARTY_D.wallet_name,
        key_name=AUX_PARTY_D.key_name,
        market_id=market_id,
        time_in_force="TIME_IN_FORCE_GTC",
        order_type="TYPE_LIMIT",
        side="SIDE_BUY",
        volume=1,
        price=price,
    )
    vega.wait_for_total_catchup()
    vega.submit_order(
        trading_wallet=AUX_PARTY_E.wallet_name,
        key_name=AUX_PARTY_E.key_name,
        market_id=market_id,
        time_in_force="TIME_IN_FORCE_GTC",
        order_type="TYPE_LIMIT",
        side="SIDE_SELL",
        volume=1,
        price=price,
    )
    vega.wait_for_total_catchup()


if __name__ == "__main__":
    """_summary_"""

    with VegaServiceNull(
        run_with_console=True,
        warn_on_raw_data_access=False,
    ) as vega:

        market_id, asset_id, best_ask_id, best_bid_id = continuous_market(
            vega=vega, price=500, spread=10
        )
        input("Paused. Press enter to continue.")

        move_market(
            vega=vega,
            market_id=market_id,
            best_ask_id=best_ask_id,
            best_bid_id=best_bid_id,
            price=600,
            spread=10,
        )
        input("Paused. Press enter to continue.")

        move_market(
            vega=vega,
            market_id=market_id,
            best_ask_id=best_ask_id,
            best_bid_id=best_bid_id,
            price=400,
            spread=10,
        )
        input("Paused. Press enter to continue.")

        move_market(
            vega=vega,
            market_id=market_id,
            best_ask_id=best_ask_id,
            best_bid_id=best_bid_id,
            price=500,
            spread=10,
        )
        input("Paused. Press enter to continue.")
