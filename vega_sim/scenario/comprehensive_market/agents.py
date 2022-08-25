from collections import namedtuple

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Set up wallets for parties submitting / amending liquidity provisions
MM_WALLET = WalletConfig("mm", "pin")

BG_WALLET = WalletConfig("bg", "pin")

# Set up wallets for parties submitting market orders
MO_WALLETS = (
    WalletConfig("mo_trader_a", "pass"),
    WalletConfig("mo_trader_b", "pass"),
    WalletConfig("mo_trader_c", "pass"),
    WalletConfig("mo_trader_d", "pass"),
    WalletConfig("mo_trader_e", "pass"),
)

# Set up wallets for parties submitting / cancelling limit orders
LO_WALLETS = (
    WalletConfig("lo_trader_a", "pass"),
    WalletConfig("lo_trader_b", "pass"),
    WalletConfig("lo_trader_c", "pass"),
    WalletConfig("lo_trader_d", "pass"),
    WalletConfig("lo_trader_e", "pass"),
)

# Set up wallets for parties to force auction pass
AUCTION1_WALLET = WalletConfig("AUCTION1", "AUCTION1pass")
AUCTION2_WALLET = WalletConfig("AUCTION2", "AUCTION2pass")

# Set up the wallet for market termination
TERMINATE_WALLET = WalletConfig("FJMKnwfZdd48C8NqvYrG", "bY3DxwtsCstMIIZdNpKs")
