from collections import namedtuple

PartyConfig = namedtuple("PartyConfig", ["wallet_name", "wallet_pass", "key_name"])

MARKET_CREATOR = PartyConfig("vega", "pass", "Market Creator")
MARKET_SETTLER = PartyConfig("vega", "pass", "Market Settler")

AUCTION_PASS_BID = PartyConfig("vega", "pass", "Auction Pass (Bid)")
AUCTION_PASS_ASK = PartyConfig("vega", "pass", "Auction Pass (Ask)")

INT_MARKET_MAKER_KEY_A = PartyConfig("vega", "pass", "Key A (Internal)")
INT_MARKET_MAKER_KEY_B = PartyConfig("vega", "pass", "Key B (External)")
INT_INFORMED_TRADER = PartyConfig("vega", "pass", "Informed Trader")
INT_RANDOM_TRADER = PartyConfig("vega", "pass", "Random Trader (Internal)")

EXT_MARKET_MAKER = PartyConfig("vega", "pass", "External Market Maker")
EXT_RANDOM_TRADER = PartyConfig("vega", "pass", "Random Trader (External)")
