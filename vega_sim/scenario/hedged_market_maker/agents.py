from collections import namedtuple

PartyConfig = namedtuple("PartyConfig", ["wallet_name", "wallet_pass", "key_name"])

MARKET_CREATOR = PartyConfig("aux_parties", "pass", "Market Creator")
MARKET_SETTLER = PartyConfig("aux_parties", "pass", "Market Settler")

AUCTION_PASS_BID = PartyConfig("aux_parties", "pass", "Auction Pass (Bid)")
AUCTION_PASS_ASK = PartyConfig("aux_parties", "pass", "Auction Pass (Ask)")

INT_MARKET_MAKER_KEY_A = PartyConfig("market_maker", "pass", "Key A (Internal)")
INT_MARKET_MAKER_KEY_B = PartyConfig("market_maker", "pass", "Key B (External)")
INT_INFORMED_TRADER = PartyConfig("aux_parties", "pass", "Informed Trader")
INT_RANDOM_TRADER = PartyConfig("aux_parties", "pass", "Random Trader (Internal)")

EXT_MARKET_MAKER = PartyConfig("aux_parties", "pass", "External Market Maker")
EXT_RANDOM_TRADER = PartyConfig("aux_parties", "pass", "Random Trader (External)")
