import logging
from collections import namedtuple
from random import randint
import argparse

from vega_sim.null_service import VegaServiceNull
from vega_sim.service import MarketStateUpdateType
import vega_sim.proto.vega as vega_protos


WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Set up parties in the market/ Submit liquidity provision/ Control midprice
MM_WALLET = WalletConfig("mm", "pin")
MM_WALLET2 = WalletConfig("mm2", "pin2")

# The party to send selling/buying MOs to hit LP orders
TRADER_WALLET = WalletConfig("Zl3pLs6Xk6SwIK7Jlp2x", "bJQDDVGAhKkj3PVCc7Rr")

# The party randomly post LOs at buy/sell side to simulate real Market situation
RANDOM_WALLET = WalletConfig("OJpVLvU5fgLJbhNPdESa", "GmJTt9Gk34BHDlovB7AJ")

# The party to interact with the network via governance
GOVERNANCE_WALLET = WalletConfig("FJMKnwfZdd48C8NqvYrG", "bY3DxwtsCstMIIZdNpKs")

wallets = [MM_WALLET, MM_WALLET2, TRADER_WALLET, RANDOM_WALLET, GOVERNANCE_WALLET]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--perps", action="store_true", default=False)
    args = parser.parse_args()

    with VegaServiceNull(
        run_with_console=False,
        launch_graphql=False,
        retain_log_files=True,
        use_full_vega_wallet=True,
        store_transactions=True,
    ) as vega:
        for wallet in wallets:
            vega.create_key(wallet.name)

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
            amount=100e5,
        )
        vega.mint(
            MM_WALLET2.name,
            asset=tdai_id,
            amount=100e5,
        )

        vega.wait_fn(10)
        vega.wait_for_total_catchup()

        if args.perps:
            vega.create_simple_perps_market(
                market_name="BTC:DAI_Perpetual",
                proposal_key=MM_WALLET.name,
                settlement_asset_id=tdai_id,
                settlement_data_key=GOVERNANCE_WALLET.name,
                funding_payment_frequency_in_seconds=10,
                market_decimals=5,
            )
        else:
            vega.create_simple_market(
                market_name="BTC:DAI_Mar22",
                proposal_key=MM_WALLET.name,
                settlement_asset_id=tdai_id,
                termination_key=GOVERNANCE_WALLET.name,
                market_decimals=5,
            )
        vega.wait_for_total_catchup()

        market_id = vega.all_markets()[0].id
        vega.submit_liquidity(
            key_name=MM_WALLET.name,
            market_id=market_id,
            commitment_amount=10000,
            fee=0.001,
            is_amendment=False,
        )

        vega.update_margin_mode(
            key_name=MM_WALLET.name,
            margin_mode="MODE_ISOLATED_MARGIN",
            margin_factor=0.5,
            market_id=market_id,
        )
        vega.submit_order(
            trading_key=MM_WALLET.name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=1,
            price=100,
        )
        vega.submit_order(
            trading_key=MM_WALLET2.name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_BUY",
            volume=1,
            price=100,
        )

        vega.submit_order(
            trading_key=MM_WALLET.name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=10,
            price=100.5,
            wait=True,
        )

        to_cancel = vega.submit_order(
            trading_key=MM_WALLET.name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=10,
            price=100.5,
            wait=True,
        )

        vega.cancel_order(MM_WALLET.name, market_id, to_cancel)

        vega.submit_order(
            trading_key=MM_WALLET.name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_BUY",
            volume=5,
            price=110.5,
            wait=True,
        )
        vega.submit_simple_liquidity(
            key_name=MM_WALLET.name,
            market_id=market_id,
            commitment_amount=5000,
            fee=0.002,
            is_amendment=True,
        )

        position = vega.positions_by_market(
            key_name=MM_WALLET2.name, market_id=market_id
        )
        margin_levels = vega.margin_levels(MM_WALLET2.name)
        print(f"Position is: {position}")
        print(f"Margin levels are: {margin_levels}")
        vega.forward("10s")

        if args.perps:
            for i in range(20):
                internal_price = 100 + randint(-5, 5)
                external_price = internal_price + randint(-50, 50)

                vega.submit_order(
                    trading_key=MM_WALLET.name,
                    market_id=market_id,
                    time_in_force="TIME_IN_FORCE_GTC",
                    order_type="TYPE_LIMIT",
                    side="SIDE_BUY",
                    volume=1,
                    price=internal_price,
                    wait=True,
                )
                vega.submit_order(
                    trading_key=MM_WALLET2.name,
                    market_id=market_id,
                    time_in_force="TIME_IN_FORCE_GTC",
                    order_type="TYPE_LIMIT",
                    side="SIDE_SELL",
                    volume=1,
                    price=internal_price,
                    wait=True,
                )
                vega.submit_settlement_data(
                    settlement_key=GOVERNANCE_WALLET.name,
                    settlement_price=external_price,
                    market_id=market_id,
                )
                vega.forward("4s")
                print(vega.get_latest_market_data(market_id=market_id).product_data)

        # suspend market
        print(
            "market state:"
            f" {vega_protos.markets.Market.State.Name(vega.get_latest_market_data(market_id).market_state)}"
        )
        update_type = MarketStateUpdateType.Suspend
        print(f"submitting proposal: {update_type}")
        vega.update_market_state(
            proposal_key=MM_WALLET.name, market_id=market_id, market_state=update_type
        )
        print(
            "market state:"
            f" {vega_protos.markets.Market.State.Name(vega.get_latest_market_data(market_id).market_state)}"
        )
        # resume market
        vega.wait_for_total_catchup()
        update_type = MarketStateUpdateType.Resume
        print(f"submitting proposal: {update_type}")
        vega.update_market_state(
            proposal_key=MM_WALLET.name, market_id=market_id, market_state=update_type
        )
        print(
            "market state:"
            f" {vega_protos.markets.Market.State.Name(vega.get_latest_market_data(market_id).market_state)}"
        )

        input("Pausing to observe the market, press Enter to continue.")
        if args.perps:
            # close market
            update_type = MarketStateUpdateType.Terminate
            print(f"submitting proposal: {update_type}")
            vega.update_market_state(
                proposal_key=MM_WALLET.name,
                market_id=market_id,
                market_state=update_type,
                price=100,
            )
        else:
            vega.submit_termination_and_settlement_data(
                settlement_key=GOVERNANCE_WALLET.name,
                settlement_price=100,
                market_id=market_id,
            )
        vega.wait_for_total_catchup()
        print(
            "market state:"
            f" {vega_protos.markets.Market.State.Name(vega.get_latest_market_data(market_id).market_state)}"
        )

        vega.forward("10s")
        input("Press Enter to finish")
