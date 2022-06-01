from collections import namedtuple
from typing import Dict, List, Optional

import numpy as np
from vega_sim.api.data import Order
from vega_sim.environment import StateAgent, VegaState
from vega_sim.environment.agent import StateAgentWithWallet
from vega_sim.null_service import VegaServiceNull
from vega_sim.proto.vega import markets as markets_protos
from vega_sim.proto.vega import vega as vega_protos, governance as gov_protos
from vega_sim.service import VegaService

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Set up parties in the market/ Submit liquidity provision/ Control midprice
MM_WALLET = WalletConfig("mm", "pin")

# The party to send selling/buying MOs to hit LP orders
TRADER_1_WALLET = WalletConfig("trader1", "t1p")
TRADER_2_WALLET = WalletConfig("trader2", "t2p")
TRADER_3_WALLET = WalletConfig("trader3", "t3p")
TRADER_4_WALLET = WalletConfig("trader4", "t4p")

# The party randomly post LOs at buy/sell side to simulate real Market situation
RANDOM_WALLET = WalletConfig("OJpVLvU5fgLJbhNPdESa", "GmJTt9Gk34BHDlovB7AJ")

# The party to terminate the market and send settlment price
TERMINATE_WALLET = WalletConfig("FJMKnwfZdd48C8NqvYrG", "bY3DxwtsCstMIIZdNpKs")

wallets = [
    MM_WALLET,
    TRADER_1_WALLET,
    TRADER_2_WALLET,
    TRADER_3_WALLET,
    TRADER_4_WALLET,
    RANDOM_WALLET,
    TERMINATE_WALLET,
]


def random_walk_price(
    terminal_time_seconds: int = 5,
    time_increment_seconds: int = 1,
    sigma=0.1,
    initial_price: float = 1,
    random_seed: Optional[int] = None,
    min_price: float = 0,
) -> List[float]:
    """
    Given the Midprice at time 0, calculate the asset price based on Random Walk Model

    Args:
        terminal_time:
            int, how many seconds to generate price walk for
        time_increment_seconds:
            int, how many seconds between sampling points
        sigma:
            float, volatility per second,
        initial_price:
            float, starting price of the asset
        min_price:
            float, floor price for asset, defaults to 0
    Returns:
        List[float], random walk prices
    """
    time_step = np.linspace(
        0, terminal_time_seconds, terminal_time_seconds // time_increment_seconds
    )
    random_state = np.random.RandomState(seed=random_seed)

    dW = np.sqrt(time_increment_seconds) * random_state.randn(len(time_step) - 1)
    S = np.zeros(len(time_step))

    # Decimal places
    S[0] = initial_price
    for i in range(len(time_step) - 1):
        S[i + 1] = max(S[i] + sigma * dW[i], min_price)

    return S


class MarketMaker(StateAgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        terminate_wallet_name: str,
        terminate_wallet_pass: str,
        price_process: List[float],
        spread: float = 2,
    ):
        super().__init__(wallet_name, wallet_pass)
        self.terminate_wallet_name = terminate_wallet_name
        self.terminate_wallet_pass = terminate_wallet_pass
        self.price_process = iter(price_process)
        self.spread = spread
        self.buy_order_num = 0
        self.sell_order_num = 0
        self.buy_order_keepalive_num = 0
        self.sell_order_keepalive_num = 0

    def initialise(self, vega: VegaServiceNull):
        super().initialise(vega=vega)
        self.vega.create_wallet(self.terminate_wallet_name, self.terminate_wallet_pass)

        # Faucet ourselves some VOTE tokens
        self.vega.mint(
            self.wallet_name,
            asset="VOTE",
            amount=1e4,
        )
        self.vega.forward("20s")
        # Get the market's asset set up
        self.vega.create_asset(
            self.wallet_name,
            name="tDAI",
            symbol="tDAI",
            decimals=5,
            max_faucet_amount=5e10,
        )
        self.vega.forward("10s")
        self.vega.wait_for_datanode_sync()

        self.asset_id = self.vega.find_asset_id(symbol="tDAI")
        self.vega.mint(
            self.wallet_name,
            asset=self.asset_id,
            amount=5e5,
        )

        self.vega.wait_for_datanode_sync()
        self.vega.forward("30s")
        self.vega.wait_for_datanode_sync()
        liquidity_commitment = gov_protos.NewMarketCommitment(
            commitment_amount="20000000000",
            fee="0.002",
            sells=[
                vega_protos.LiquidityOrder(
                    reference=vega_protos.PeggedReference.PEGGED_REFERENCE_MID,
                    proportion=1,
                    offset="50",
                )
            ],
            buys=[
                vega_protos.LiquidityOrder(
                    reference=vega_protos.PeggedReference.PEGGED_REFERENCE_MID,
                    proportion=1,
                    offset="50",
                )
            ],
            reference="",
        )

        # Get the market set up
        self.vega.create_simple_market(
            market_name="BTC:DAI_Mar22",
            proposal_wallet=self.wallet_name,
            settlement_asset_id=self.asset_id,
            termination_wallet=self.terminate_wallet_name,
            liquidity_commitment=liquidity_commitment,
        )
        self.vega.forward("2s")

        self.market_id = self.vega.all_markets()[0].id

        spot_price = next(self.price_process)
        # Submit some orders to open the market
        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY",
            volume=1,
            price=spot_price - self.spread / 2,
            wait=False,
            order_ref=f"buy_front{self.buy_order_num}",
        )

        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_SELL",
            volume=1,
            price=spot_price + self.spread / 2,
            wait=False,
            order_ref=f"sell_front{self.sell_order_num}",
        )

        self.vega.open_orders_by_market(self.market_id)
        # Submit some orders to keep the market open
        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_BUY",
            volume=1,
            price=spot_price - 5 * self.spread,
            wait=False,
            order_ref=f"buy_keep_alive{self.buy_order_keepalive_num}",
        )

        self.vega.submit_order(
            trading_wallet=self.wallet_name,
            market_id=self.market_id,
            order_type="TYPE_LIMIT",
            time_in_force="TIME_IN_FORCE_GTC",
            side="SIDE_SELL",
            volume=1,
            price=spot_price + 5 * self.spread,
            wait=False,
            order_ref=f"sell_keep_alive{self.sell_order_keepalive_num}",
        )

        # self.vega.submit_simple_liquidity(
        #     wallet_name=self.wallet_name,
        #     market_id=self.market_id,
        #     commitment_amount=2e5,
        #     fee=0.05,
        #     reference_buy="PEGGED_REFERENCE_BEST_BID",
        #     reference_sell="PEGGED_REFERENCE_BEST_ASK",
        #     delta_buy=0,
        #     delta_sell=0,
        #     is_amendment=True,
        # )

    def _place_or_amend(
        self,
        order_ref: str,
        order_map: Dict[str, Order],
        price: float,
        side: str,
        volume: float,
        index_name: str,
    ):
        index_num = getattr(self, index_name)
        full_ref = f"{order_ref}{index_num}"
        if (
            full_ref not in order_map
            or order_map[full_ref].status != vega_protos.Order.Status.STATUS_ACTIVE
        ):
            new_index = index_num + 1
            setattr(self, index_name, new_index)
            self.vega.submit_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                order_type="TYPE_LIMIT",
                time_in_force="TIME_IN_FORCE_GTC",
                side=side,
                volume=volume,
                price=price,
                wait=False,
                order_ref=f"{order_ref}{new_index}",
            )
        else:
            self.vega.amend_order(
                trading_wallet=self.wallet_name,
                market_id=self.market_id,
                order_id=order_map[full_ref].id,
                price=price,
            )

    def step(self, vega_state: VegaState):
        spot_price = next(self.price_process)

        refs = [
            f"sell_front{self.sell_order_num}",
            f"buy_front{self.buy_order_num}",
            f"buy_keep_alive{self.buy_order_keepalive_num}",
            f"sell_keep_alive{self.sell_order_keepalive_num}",
        ]

        # Something in the vega node is not fully updating even when forwarding
        # transactions. Needs further investigation.
        order_map = None
        for _ in range(10):
            try:
                order_map = {
                    ref: self.vega.order_status_by_reference(ref, self.market_id)
                    for ref in refs
                }
                break
            except:
                self.vega.forward("5s")
                continue
        if order_map is None:
            raise Exception("Max retries exceeded")

        self._place_or_amend(
            "sell_front",
            order_map=order_map,
            price=spot_price + self.spread / 2,
            side="SIDE_SELL",
            index_name="sell_order_num",
            volume=50,
        )
        self._place_or_amend(
            "buy_front",
            order_map=order_map,
            price=spot_price - self.spread / 2,
            side="SIDE_BUY",
            index_name="buy_order_num",
            volume=50,
        )
        self._place_or_amend(
            "buy_keep_alive",
            order_map=order_map,
            price=spot_price - 5 * self.spread,
            side="SIDE_BUY",
            index_name="buy_order_keepalive_num",
            volume=1,
        )
        self._place_or_amend(
            "sell_keep_alive",
            order_map=order_map,
            price=spot_price + 5 * self.spread,
            side="SIDE_SELL",
            index_name="sell_order_keepalive_num",
            volume=1,
        )


class MarketOrderTraders(StateAgent):
    def __init__(
        self,
        market_agents: List[StateAgentWithWallet],
        buy_order_arrival_rate: float = 1,
        sell_order_arrival_rate: float = 1,
    ):
        super().__init__()
        self.market_agents = market_agents
        self.buy_order_arrival_rate = buy_order_arrival_rate
        self.sell_order_arrival_rate = sell_order_arrival_rate

    def initialise(self, vega: VegaService):
        super().initialise(vega=vega)
        self.market_id = self.vega.all_markets()[0].id

        tdai_id = self.vega.find_asset_id(symbol="tDAI")

        for trader in self.market_agents:
            trader.initialise(vega=vega)
            self.vega.mint(
                trader.wallet_name,
                asset=tdai_id,
                amount=1e5,
            )
        self.vega.forward("1s")

    def step(self, vega_state: VegaState):
        if (
            vega_state.market_state[self.market_id].trading_mode
            == markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS
        ):
            buy_arrival = np.random.poisson(self.buy_order_arrival_rate)
            sell_arrival = np.random.poisson(self.sell_order_arrival_rate)

            buy_trader = np.random.choice(self.market_agents)
            sell_trader = np.random.choice(self.market_agents)

            if (
                vega_state.market_state[self.market_id].state
                == markets_protos.Market.State.STATE_ACTIVE
            ):
                if buy_arrival > 0:
                    self.vega.submit_market_order(
                        trading_wallet=buy_trader.wallet_name,
                        market_id=self.market_id,
                        side="SIDE_BUY",
                        volume=buy_arrival,
                        wait=False,
                    )
                if sell_arrival > 0:
                    self.vega.submit_market_order(
                        trading_wallet=sell_trader.wallet_name,
                        market_id=self.market_id,
                        side="SIDE_SELL",
                        volume=sell_arrival,
                        wait=False,
                    )
            # else:
            #     if buy_arrival > 0:
            #         self.vega.submit_order(
            #             trading_wallet=buy_trader.wallet_name,
            #             market_id=self.market_id,
            #             order_type="TYPE_LIMIT",
            #             time_in_force="TIME_IN_FORCE_GTC",
            #             side="SIDE_BUY",
            #             volume=1,
            #             price=2000,
            #             wait=False,
            #         )
            #     if sell_arrival > 0:
            #         self.vega.submit_order(
            #             trading_wallet=sell_trader.wallet_name,
            #             market_id=self.market_id,
            #             order_type="TYPE_LIMIT",
            #             time_in_force="TIME_IN_FORCE_GTC",
            #             side="SIDE_SELL",
            #             price=0.1,
            #             volume=1,
            #             wait=False,
            #         )
