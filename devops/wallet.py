"""wallet.py

Module contains agent information variables for each party in the devops scenario. An 
agent variable contains the wallet name, wallet pass, and key name for an agent.

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
    • momentum_trader_a
    • momentum_trader_b
    • momentum_trader_c
    • momentum_trader_d
    • momentum_trader_e
    • sensitive_trader_a
    • sensitive_trader_b
    • sensitive_trader_c

The wallet name and wallet passphrase can be modified with the environment variables
VEGA_USER_WALLET_NAME and VEGA_USER_WALLETS_PASS in the .env file.

"""

import os
import dotenv

from dataclasses import dataclass

DEFAULT_USER_WALLET_NAME = "network_agents"
DEFAULT_USER_WALLET_PASS = "passphrase"


# Set the default wallet_name and wallet_pass in this dataclass
@dataclass
class Agent:
    dotenv.load_dotenv()
    wallet_name: str = os.environ.get("VEGA_USER_WALLET_NAME", DEFAULT_USER_WALLET_NAME)
    wallet_pass: str = os.environ.get("VEGA_USER_WALLET_PASS", DEFAULT_USER_WALLET_PASS)
    key_name: str = None


# Market proper creates and approves a market creation proposal
MARKET_CREATOR_AGENT = Agent(key_name="market_creator")

# Market terminator creates and approves a market settle proposal
MARKET_SETTLER_AGENT = Agent(key_name="market_settler")

# Market maker makes a market by providing liquidity and an order book
MARKET_MAKER_AGENT = Agent(key_name="market_maker")

# Auction traders provide trades in auction trading modes
AUCTION_TRADER_AGENTS = [
    Agent(key_name="auction_trader_a"),
    Agent(key_name="auction_trader_b"),
]

# Random traders provide trades in continuous trading modes
RANDOM_TRADER_AGENTS = [
    Agent(key_name="random_trader_a"),
    Agent(key_name="random_trader_b"),
    Agent(key_name="random_trader_c"),
]

# Momentum traders provide realistic trades in continuous trading modes
MOMENTUM_TRADER_AGENTS = [
    Agent(key_name="momentum_trader_a"),
    Agent(key_name="momentum_trader_b"),
    Agent(key_name="momentum_trader_c"),
    Agent(key_name="momentum_trader_d"),
    Agent(key_name="momentum_trader_e"),
]

# Sensitive traders exploit over-exposed positions in continuous trading modes
SENSITIVE_TRADER_AGENTS = [
    Agent(key_name="sensitive_trader_a"),
    Agent(key_name="sensitive_trader_b"),
    Agent(key_name="sensitive_trader_c"),
]
