import random
from collections import namedtuple
from vega_sim.environment import StateAgent, VegaState
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import vega as vega_protos
from vega_sim.service import VegaService

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Set up parties in the market/ Submit liquidity provision/ Control midprice
MM_WALLET = WalletConfig("mm", "pin")

# The party to send selling/buying MOs to hit LP orders
TRADER_WALLET = WalletConfig("Zl3pLs6Xk6SwIK7Jlp2x", "bJQDDVGAhKkj3PVCc7Rr")

# The party randomly post LOs at buy/sell side to simulate real Market situation
RANDOM_WALLET = WalletConfig("OJpVLvU5fgLJbhNPdESa", "GmJTt9Gk34BHDlovB7AJ")

# The party to terminate the market and send settlment price
TERMINATE_WALLET = WalletConfig("FJMKnwfZdd48C8NqvYrG", "bY3DxwtsCstMIIZdNpKs")

wallets = [MM_WALLET, TRADER_WALLET, RANDOM_WALLET, TERMINATE_WALLET]

# def initialise_market(market_id: str, at_price: int, vega: VegaServiceNull):
#     vega.submit_order(
#         trading_wallet=RANDOM_WALLET.name,
#         market_id=market_id,
#         order_type="TYPE_LIMIT",
#         time_in_force="TIME_IN_FORCE_GTC",
#         side="SIDE_BUY",
#         volume=100,
#         price=at_price,
#     )

#     vega.submit_order(
#         trading_wallet=RANDOM_WALLET.name,
#         market_id=market_id,
#         order_type="TYPE_LIMIT",
#         time_in_force="TIME_IN_FORCE_GTC",
#         side="SIDE_SELL",
#         volume=100,
#         price=at_price,
#     )


class MarketMaker(StateAgent):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        terminate_wallet_name: str,
        terminate_wallet_pass: str,
    ):
        super().__init__(wallet_name, wallet_pass)
        self.terminate_wallet_name = terminate_wallet_name
        self.terminate_wallet_pass = terminate_wallet_pass

    def initialise(self, vega: VegaServiceNull):
        super().initialise(vega=vega)
        self.vega.create_wallet(self.terminate_wallet_name, self.terminate_wallet_pass)

        # Faucet ourselves some VOTE tokens
        self.vega.mint(
            self.wallet_name,
            asset="VOTE",
            amount=1e4,
        )
        self.vega.forward("2s")
        # Get the market's asset set up
        self.vega.create_asset(
            self.wallet_name,
            name="tDAI",
            symbol="tDAI",
            decimals=5,
            max_faucet_amount=1e10,
        )
        tdai_id = self.vega.find_asset_id(symbol="tDAI")
        self.vega.mint(
            self.wallet_name,
            asset=tdai_id,
            amount=1e5,
        )

        # Get the market set up
        self.vega.create_simple_market(
            market_name="BTC:DAI_Mar22",
            proposal_wallet=self.wallet_name,
            settlement_asset_id=tdai_id,
            termination_wallet=self.terminate_wallet_name,
        )
        self.vega.forward("2s")

        self.market_id = self.vega.all_markets()[0].id

        # Submit some orders to open the market
        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY",
            volume=100,
            price=1,
        )

        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_SELL",
            volume=100,
            price=1.01,
        )

        self.vega.submit_simple_liquidity(
            wallet_name=self.wallet_name,
            market_id=self.market_id,
            commitment_amount=200000,
            fee=0.002,
            reference_buy="PEGGED_REFERENCE_MID",
            reference_sell="PEGGED_REFERENCE_MID",
            delta_buy=0.1,
            delta_sell=0.1,
            is_amendment=False,
        )

    def step(self, vega_state: VegaState):
        market_state = vega_state[self.market_id].state

        if market_state == vega_protos.markets.Market.State.STATE_SUSPENDED:
            curr_buy = self.vega.order_status(self.order_id_buy)
            curr_sell = self.vega.order_status(self.order_id_sell)

            if curr_sell.status == vega_protos.vega.Order.Status.STATUS_FILLED:
                self.order_id_sell = self.vega.submit_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    order_type="TYPE_LIMIT",
                    time_in_force="TIME_IN_FORCE_GTC",
                    side="SIDE_SELL",
                    volume=1,
                    price=1.01,
                    wait=True,
                )

            if curr_buy.status == vega_protos.vega.Order.Status.STATUS_FILLED:
                self.order_id_buy = self.vega.submit_order(
                    trading_wallet=self.wallet_name,
                    market_id=self.market_id,
                    order_type="TYPE_LIMIT",
                    time_in_force="TIME_IN_FORCE_GTC",
                    side="SIDE_BUY",
                    volume=1,
                    price=1,
                    wait=True,
                )


class MarketOrderTraders(StateAgent):
    def initialise(self, vega: VegaService):
        self.market_id = self.vega.all_markets()[0].id

    def step(self, vega_state: VegaState):
        self.vega.submit_market_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            side="SIDE_BUY" if random.random() > 0.5 else "SIDE_SELL",
            volume=1,
        )
