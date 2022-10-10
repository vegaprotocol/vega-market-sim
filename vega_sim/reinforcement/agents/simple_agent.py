"""
A simple agent framework which you can extend with some custom logic.

As-is, this agent will faucet itself some tokens in the setup phase
and then do nothing for the rest of the trading session.

Fill in your own logic into the `step` function to make them trade
however you'd like.

Below, we have a range of helpful functions to get you started, 
copy and paste these into your code to 

### Pull best bid/ask prices

### Place a Limit Order

### Place a Market Order

### Cancel an Order

### Retrieve current position

### Retrieve current orders

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
        self.market_id = [
            m.id
            for m in self.vega.all_markets()
            if m.tradable_instrument.instrument.name == self.market_name
        ][0]
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
        import pdb

        pdb.set_trace()
        pass
