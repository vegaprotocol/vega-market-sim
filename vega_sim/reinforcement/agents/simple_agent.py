"""

#######################################################################
A simple agent framework which you can extend with some custom logic.

As-is, this agent will faucet itself some tokens in the setup phase
and then do nothing for the rest of the trading session.

Fill in your own logic into the `step` function to make them trade
however you'd like.

Below, we have a range of building blocks,
copy and paste these into your code to get started

#######################################################################

### Pull best bid/ask prices
best_bid, best_ask = self.vega.best_prices(self.market_id)

### Pull market depth (up to a specified number of levels)
market_depth = self.vega.market_depth(self.market_id, num_levels=5)

### Place a Limit Order
self.vega.submit_order(
    trading_wallet=self.wallet_name,
    market_id=self.market_id,
    order_type="TYPE_LIMIT",
    # https://docs.vega.xyz/docs/mainnet/grpc/vega/vega.proto#ordertimeinforce
    time_in_force="TIME_IN_FORCE_GTC",
    # https://docs.vega.xyz/docs/mainnet/grpc/vega/vega.proto#side
    side="SIDE_BUY",
    volume=1.0,
    price=100.0,
    # If this is true, function waits for confirmation and returns the order_id
    wait=False,
)

### Place a Market Order
self.vega.submit_market_order(
    trading_wallet=self.wallet_name,
    market_id=self.market_id,
    # https://docs.vega.xyz/docs/mainnet/grpc/vega/vega.proto#side
    side="SIDE_BUY",
    volume=1.0,
    # If this is true, function waits for confirmation and returns the order_id
    wait=False,
    # If this is true, order errors if the entire volume cannot be traded.
    # Otherwise, whatever can be traded will be.
    fill_or_kill=False,
)

### Amend an Order
self.vega.amend_order(
    trading_wallet=self.wallet_name,
    market_id=self.market_id,
    order_id=order_to_amend_id,
    price=10.1,
    volume_delta=10, # Note: Change in volume from existing order
)

### Cancel an Order
self.vega.cancel_order(
    self.wallet_name,
    self.market_id,
    order_id
)

### Retrieve Current Position & PnL (Profit & Loss)
positions = self.vega.positions_by_market(
    wallet_name=self.wallet_name, market_id=self.market_id
)
if len(positions) > 0:
    position = positions[0]
    volume = position.open_volume
    pnl = position.realised_pnl + position.unrealised_pnl
    entry_price = position.average_entry_price

### Retrieve Current Orders
orders = self.vega.orders_for_party_from_feed(
    self.wallet_name,
    self.market_id,
    live_only=True,  # set to False to also retrieve dead orders
)

### Retrieve Account Balance
curr_acct = self.party_account(
    wallet_name=wallet_name, asset_id=asset, market_id=None
)
general_balance = curr_acct.general  # The balance not currently in use by the market
margin_balance = curr_acct.margin  # The balance already being used as margin

#######################################################################
"""


from vega_sim.environment.agent import AgentWithWallet
from vega_sim.service import VegaService


class SimpleAgent(AgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
        market_name: str,
        asset_name: str,
        initial_balance: float,
    ):
        """Agent to extend with custom logic. A barebones skeleton which will
        currently faucet itself some tokens but then do nothing.

        Args:
            wallet_name:
                str, The name to use for this agent's wallet
            wallet_pass:
                str, The password which this agent uses to log in to the wallet
        """
        super().__init__(wallet_name=wallet_name, wallet_pass=wallet_pass)

        self.market_name = market_name
        self.asset_name = asset_name
        self.initial_balance = initial_balance

    def initialise(self, vega: VegaService):
        # Initialise wallet
        super().initialise(vega=vega, create_wallet=True)

        # Get market id
        self.market_id = self.vega.find_market_id(name=self.market_name)

        # Get asset id
        self.asset_id = self.vega.find_asset_id(symbol=self.asset_name)
        # Top up asset
        self.vega.mint(
            self.wallet_name,
            asset=self.asset_id,
            amount=self.initial_balance,
        )
        self.vega.wait_fn(2)

    def step(self, vega: VegaService):
        """This function is called once each loop through of the simulation.

        Here you want to put you main logic, what the trader will do at every
        time, perhaps placing an order.

        Args:
            vega:
                VegaService, a client with which to interact with the Vega
                network itself. Use this to query for the current state of
                the world
        """
        pass
