from vega_sim.environment.agent import AgentWithWallet
from vega_sim.service import VegaService


class SimpleAgent(AgentWithWallet):
    def __init__(
        self,
        wallet_name: str,
        wallet_pass: str,
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

    def initialise(self, vega: VegaService):
        super().initialise(vega=vega, create_wallet=True)
