import logging
from collections import namedtuple
from math import exp

from vega_sim.null_service import VegaServiceNull

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

MM_WALLET = WalletConfig("mm", "pin")
MM_WALLET2 = WalletConfig("mm2", "pin2")
TRADER_WALLET = WalletConfig("trader", "password123")

wallets = [MM_WALLET, MM_WALLET2, TRADER_WALLET]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with VegaServiceNull(
        run_with_console=True,
    ) as vega:
        for wallet in wallets:
            vega.create_wallet(wallet.name, wallet.passphrase)

        vega.mint(
            MM_WALLET.name,
            asset="VOTE",
            amount=1e4,
        )

        vega.update_network_parameter(
            MM_WALLET.name, parameter="market.fee.factors.makerFee", new_value="0.1"
        )
        vega.forward("10s")
        vega.wait_for_total_catchup()

        vega.create_asset(
            MM_WALLET.name,
            name="tDAI",
            symbol="tDAI",
            decimals=5,
            max_faucet_amount=1e10,
        )

        vega.wait_for_total_catchup()
        tdai_id = vega.find_asset_id(symbol="tDAI")
        print("TDAI: ", tdai_id)

        vega.mint(
            MM_WALLET.name,
            asset=tdai_id,
            amount=1e10,
        )
        vega.mint(
            MM_WALLET2.name,
            asset=tdai_id,
            amount=1e10,
        )

        vega.mint(
            TRADER_WALLET.name,
            asset=tdai_id,
            amount=1e2,
        )

        vega.wait_fn(10)
        vega.wait_for_total_catchup()

        market_decimals=2
        vega.create_simple_market(
            market_name="XYZ:DAI_Mar22",
            proposal_wallet=MM_WALLET.name,
            settlement_asset_id=tdai_id,
            termination_wallet=MM_WALLET2.name,
            market_decimals=market_decimals,
        )
        vega.wait_for_total_catchup()

        market_id = vega.all_markets()[0].id
        
        vega.submit_simple_liquidity(
            wallet_name=MM_WALLET.name,
            market_id=market_id,
            commitment_amount=5000,
            fee=0.001,
            reference_buy="PEGGED_REFERENCE_BEST_BID",
            reference_sell="PEGGED_REFERENCE_BEST_ASK",
            delta_buy=2,
            delta_sell=2,
            is_amendment=False,
        )

        mid_price = 100
        price_delta=10**(-market_decimals+1)
        for i in range(0,22):
            if i == 1:
                continue # widen the spread
            size = 1 if i==0 else exp(-0.075*i+9)
            vega.submit_order(
                trading_wallet=MM_WALLET.name,
                market_id=market_id,
                time_in_force="TIME_IN_FORCE_GTC",
                order_type="TYPE_LIMIT",
                side="SIDE_SELL",
                volume=size,
                price=mid_price+i*price_delta
            )
            vega.submit_order(
                trading_wallet=MM_WALLET2.name,
                market_id=market_id,
                time_in_force="TIME_IN_FORCE_GTC",
                order_type="TYPE_LIMIT",
                side="SIDE_BUY",
                volume=size,
                price=mid_price-i*price_delta
            )
        
        matching_price = mid_price+price_delta
        vega.submit_order(
                trading_wallet=TRADER_WALLET.name,
                market_id=market_id,
                time_in_force="TIME_IN_FORCE_GTC",
                order_type="TYPE_LIMIT",
                side="SIDE_SELL",
                volume=1,
                price=matching_price
            )
        
        msg = "\nPausing for screenshot. Press \033]8;;{}\033\\{}\033]8;;\033\\ to continue.\n".format(
            "https://ux.stackexchange.com/questions/54461/should-i-use-the-name-enter-or-return-key",
            "Enter/Return")
        input(msg)

        vega.submit_order(
            trading_wallet=MM_WALLET2.name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_BUY",
            volume=1,
            price=matching_price
        )
        vega.wait_fn(2)
        input(msg)