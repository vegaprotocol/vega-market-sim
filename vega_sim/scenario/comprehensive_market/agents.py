from collections import namedtuple

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Set up wallets for parties proposing market
MM_WALLET = WalletConfig("mm", "pin")

# Set up wallets for parties submitting market orders
lp_agents = 5
LP_WALLETS = [WalletConfig("lp_trader_" + str(i), "pass") for i in range(lp_agents)]

# Set up wallets for parties submitting market orders
mo_agents = 5
MO_WALLETS = [WalletConfig("mo_trader_" + str(i), "pass") for i in range(mo_agents)]

# Set up wallets for parties submitting / cancelling limit orders
lo_agents = 20
LO_WALLETS = [WalletConfig("lo_trader_" + str(i), "pass") for i in range(lo_agents)]

# Set up wallets for parties to force auction pass
AUCTION1_WALLET = WalletConfig("AUCTION1", "AUCTION1pass")
AUCTION2_WALLET = WalletConfig("AUCTION2", "AUCTION2pass")

# Set up the wallet for market termination
TERMINATE_WALLET = WalletConfig("FJMKnwfZdd48C8NqvYrG", "bY3DxwtsCstMIIZdNpKs")
