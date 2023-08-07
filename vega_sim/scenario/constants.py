from enum import Enum


class Network(Enum):
    NULLCHAIN = "nullchain"
    DEVNET1 = "vegawallet-devnet1"
    STAGNET1 = "vegawallet-stagnet1"
    STAGNET2 = "vegawallet-stagnet2"
    STAGNET3 = "vegawallet-stagnet3"
    FAIRGROUND = "vegawallet-fairground"
    MAINNET_MIRROR = "vegawallet-mainnet-mirror"
    TESTNET2 = "testnet2"
    CAPSULE = "config"
