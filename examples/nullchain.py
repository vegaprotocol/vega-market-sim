import logging
import numpy as np
from collections import namedtuple

from vega_sim.null_service import VegaServiceNull
import vega_sim.proto.vega as vega_protos
from vega_sim.proto.vega.governance_pb2 import UpdateMarketConfiguration


WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Set up parties in the market/ Submit liquidity provision/ Control midprice
MM_WALLET = WalletConfig("mm", "pin")
MM_WALLET2 = WalletConfig("mm2", "pin2")

# The party to send selling/buying MOs to hit LP orders
TRADER_WALLET = WalletConfig("Zl3pLs6Xk6SwIK7Jlp2x", "bJQDDVGAhKkj3PVCc7Rr")

# The party randomly post LOs at buy/sell side to simulate real Market situation
RANDOM_WALLET = WalletConfig("OJpVLvU5fgLJbhNPdESa", "GmJTt9Gk34BHDlovB7AJ")

# The party to terminate the market and send settlment price
TERMINATE_WALLET = WalletConfig("FJMKnwfZdd48C8NqvYrG", "bY3DxwtsCstMIIZdNpKs")

wallets = [MM_WALLET, MM_WALLET2, TRADER_WALLET, RANDOM_WALLET, TERMINATE_WALLET]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with VegaServiceNull(
        run_with_console=False,
        launch_graphql=False,
        start_order_feed=True,
        retain_log_files=True,
        use_full_vega_wallet=True,
        store_transactions=True,
    ) as vega:
        for wallet in wallets:
            vega.create_key(wallet.name, wallet.passphrase)

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

        vega.create_simple_market(
            market_name="BTC:DAI_Mar22",
            proposal_wallet=MM_WALLET.name,
            settlement_asset_id=tdai_id,
            termination_wallet=TERMINATE_WALLET.name,
            market_decimals=5,
        )
        vega.wait_for_total_catchup()

        market_id = vega.all_markets()[0].id
        vega.submit_liquidity(
            wallet_name=MM_WALLET.name,
            market_id=market_id,
            commitment_amount=10000,
            fee=0.001,
            buy_specs=[("PEGGED_REFERENCE_MID", i * 2, i) for i in range(1, 10)],
            sell_specs=[("PEGGED_REFERENCE_MID", i * 2, i) for i in range(1, 10)],
            is_amendment=False,
        )
        vega.submit_order(
            trading_wallet=MM_WALLET.name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_SELL",
            volume=1,
            price=100,
        )
        vega.submit_order(
            trading_wallet=MM_WALLET2.name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_BUY",
            volume=1,
            price=100,
        )

        # for i in range(1, 100, 2):
        #     trader = np.random.choice([MM_WALLET.name, MM_WALLET2.name])

        #     vega.submit_order(
        #         trading_wallet=trader,
        #         market_id=market_id,
        #         time_in_force="TIME_IN_FORCE_GTC",
        #         order_type="TYPE_LIMIT",
        #         side="SIDE_BUY",
        #         volume=10 * np.random.random() + 1,
        #         price=100 - 0.25 * i,
        #     )

        #     vega.submit_order(
        #         trading_wallet=trader,
        #         market_id=market_id,
        #         time_in_force="TIME_IN_FORCE_GTC",
        #         order_type="TYPE_LIMIT",
        #         side="SIDE_SELL",
        #         volume=10 * np.random.random() + 1,
        #         price=100 + 0.25 * i,
        #     )

        # for wallet in [MM_WALLET, MM_WALLET2]:
        #     vega.submit_order(
        #         trading_wallet=wallet.name,
        #         market_id=market_id,
        #         time_in_force="TIME_IN_FORCE_GTC",
        #         order_type="TYPE_LIMIT",
        #         side="SIDE_BUY",
        #         volume=10,
        #         price=99.5,
        #     )
        #     vega.submit_order(
        #         trading_wallet=wallet.name,
        #         market_id=market_id,
        #         time_in_force="TIME_IN_FORCE_GTC",
        #         order_type="TYPE_LIMIT",
        #         side="SIDE_BUY",
        #         volume=10,
        #         price=99,
        #     )
        #     vega.submit_order(
        #         trading_wallet=wallet.name,
        #         market_id=market_id,
        #         time_in_force="TIME_IN_FORCE_GTC",
        #         order_type="TYPE_LIMIT",
        #         side="SIDE_BUY",
        #         volume=10,
        #         price=98,
        #     )
        #     vega.submit_order(
        #         trading_wallet=wallet.name,
        #         market_id=market_id,
        #         time_in_force="TIME_IN_FORCE_GTC",
        #         order_type="TYPE_LIMIT",
        #         side="SIDE_SELL",
        #         volume=10,
        #         price=101,
        #     )
        #     vega.submit_order(
        #         trading_wallet=wallet.name,
        #         market_id=market_id,
        #         time_in_force="TIME_IN_FORCE_GTC",
        #         order_type="TYPE_LIMIT",
        #         side="SIDE_SELL",
        #         volume=10,
        #         price=102,
        #     )
        #     vega.submit_order(
        #         trading_wallet=wallet.name,
        #         market_id=market_id,
        #         time_in_force="TIME_IN_FORCE_GTC",
        #         order_type="TYPE_LIMIT",
        #         side="SIDE_SELL",
        #         volume=10,
        #         price=103,
        #     )

        to_cancel = vega.submit_order(
            trading_wallet=MM_WALLET.name,
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
            trading_wallet=MM_WALLET.name,
            market_id=market_id,
            time_in_force="TIME_IN_FORCE_GTC",
            order_type="TYPE_LIMIT",
            side="SIDE_BUY",
            volume=5,
            price=110.5,
            wait=True,
        )
        vega.submit_simple_liquidity(
            wallet_name=MM_WALLET.name,
            market_id=market_id,
            commitment_amount=5000,
            fee=0.002,
            reference_buy="PEGGED_REFERENCE_MID",
            reference_sell="PEGGED_REFERENCE_MID",
            delta_buy=10,
            delta_sell=10,
            is_amendment=True,
        )

        margin_levels = vega.margin_levels(MM_WALLET2.name)
        print(f"Margin levels are: {margin_levels}")
        vega.forward("10s")

        input("Pausing to observe the market, press Enter to continue.")
        vega.settle_market(
            settlement_wallet=TERMINATE_WALLET.name,
            settlement_price=100,
            market_id=market_id,
        )
        input("Press Enter to finish")
