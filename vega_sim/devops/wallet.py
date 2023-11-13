"""wallet.py

Module contains agent information variables for each party in the devops scenario. An 
agent variable contains the wallet name and key name for an agent.

When deploying a devops scenario to an existing network; A wallet with the following key
names must exist locally.

    • market_creator
    • market_settler
    • market_maker
    • auction_trader_a
    • auction_trader_b
    • random_trader_a
    • random_trader_b
    • random_trader_c
    • sensitive_trader_a
    • sensitive_trader_b
    • sensitive_trader_c

The wallet name and wallet passphrase can be modified with the environment variables
VEGA_USER_WALLET_NAME and VEGA_USER_WALLETS_PASS.

"""

import os
import dotenv

from dataclasses import dataclass
from typing import Optional


DEFAULT_USER_WALLET_NAME = "vega-market-sim"
DEFAULT_USER_WALLET_PASS = "passphrase"


# Set the default wallet_name and wallet_pass in this dataclass
@dataclass
class Agent:
    dotenv.load_dotenv()
    wallet_name: str = os.environ.get("VEGA_USER_WALLET_NAME", DEFAULT_USER_WALLET_NAME)
    wallet_pass: str = os.environ.get("VEGA_USER_WALLET_PASS", DEFAULT_USER_WALLET_PASS)
    key_name: str = None


@dataclass
class ScenarioWallet:
    market_creator_agent: Optional[Agent]
    market_settler_agent: Optional[Agent]
    market_maker_agent: Optional[Agent]
    auction_trader_agents: list[Agent]
    random_trader_agents: list[Agent]
    sensitive_trader_agents: list[Agent]


def default_scenario_wallet() -> ScenarioWallet:
    return ScenarioWallet(
        # Market proper creates and approves a market creation proposal
        market_creator_agent=Agent(key_name="market_creator"),
        # Market terminator creates and approves a market settle proposal
        market_settler_agent=Agent(key_name="market_settler"),
        # Market maker makes a market by providing liquidity and an order book
        market_maker_agent=Agent(key_name="market_maker"),
        # Auction traders provide trades in auction trading modes
        auction_trader_agents=[
            Agent(key_name="auction_trader_a"),
            Agent(key_name="auction_trader_b"),
        ],
        # Random traders provide trades in continuous trading modes
        random_trader_agents=[
            Agent(key_name="random_trader_a"),
            Agent(key_name="random_trader_b"),
            Agent(key_name="random_trader_c"),
        ],
        # Sensitive traders exploit over-exposed positions in continuous trading modes
        sensitive_trader_agents=[
            Agent(key_name="sensitive_trader_a"),
            Agent(key_name="sensitive_trader_b"),
            Agent(key_name="sensitive_trader_c"),
        ],
    )
