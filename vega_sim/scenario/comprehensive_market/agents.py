from collections import namedtuple

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Set up wallets for parties proposing market
MM_WALLET = WalletConfig("mm", "pin")

# Set up wallets for parties to force auction pass
AUCTION1_WALLET = WalletConfig("AUCTION1", "AUCTION1pass")
AUCTION2_WALLET = WalletConfig("AUCTION2", "AUCTION2pass")

# Set up the wallet for market termination
TERMINATE_WALLET = WalletConfig("FJMKnwfZdd48C8NqvYrG", "bY3DxwtsCstMIIZdNpKs")

# informed trader wallet
INFORMED_WALLET = WalletConfig("INFORMED", "INFORMEDpass")


def create_agent_wallets(n: int = 1, prefix: str = "agent"):
    """Function creates a list of n WalletConfig tuples for use in a scenario"""
    return [WalletConfig(prefix + str(i), "pass") for i in range(n)]
