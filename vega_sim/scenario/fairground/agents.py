"""agents.py
 
Contains the wallet name, wallet passphrase, and name of wallet keys to use
for each agent in the Fairground scenario in scenario.py. To run the scenario
on a Vega network, all the variables must be modified to match a local wallet
on your system and keys in your local wallet.
"""

# Modify these to match a wallet on your local system
WALLET_NAME = "FAIRGROUND"
WALLET_PASS = "PASSPHRASE"

# Modify these to match a key name in the specified wallet
MARKET_MANAGER_KEY = "MARKET_MANAGER"

MARKET_MAKER_KEY = "MARKET_MAKER"

AUCTION_PASS_KEYS = ["AUCTION_PASS_BID", "AUCTION_PASS_SELL"]

RANDOM_MARKET_ORDER_AGENT_KEYS = [
    "RANDOM_MARKET_ORDER_AGENT_A",
    "RANDOM_MARKET_ORDER_AGENT_B",
    "RANDOM_MARKET_ORDER_AGENT_C",
]
MOMENTUM_MARKET_ORDER_AGENT_KEYS = [
    "MOMENTUM_MARKET_ORDER_AGENT_A",
    "MOMENTUM_MARKET_ORDER_AGENT_B",
    "MOMENTUM_MARKET_ORDER_AGENT_C",
    "MOMENTUM_MARKET_ORDER_AGENT_D",
    "MOMENTUM_MARKET_ORDER_AGENT_E",
]
SENSITIVE_MARKET_ORDER_AGENT_KEYS = [
    "SENSITIVE_MARKET_ORDER_AGENT_A",
    "SENSITIVE_MARKET_ORDER_AGENT_B",
    "SENSITIVE_MARKET_ORDER_AGENT_C",
]
