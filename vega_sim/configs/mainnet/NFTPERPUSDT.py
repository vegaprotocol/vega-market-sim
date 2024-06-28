"""NFTPERPUSDT.py

Market config matching latest proposal for LDO/USDT market on mainnet.
https://governance.vega.xyz/proposals/e62ca044c123068ead98934deaa6ba71e7d71ad1578f98074d1a6943fb8369c0
"""

from vega_sim.api.market import MarketConfig

CONFIG = MarketConfig(
    {
        "linearSlippageFactor": "0.001",
        "decimalPlaces": "6",
        "positionDecimalPlaces": "1",
        "tickSize": 1,
        "instrument": {
            "name": "NFTPerp MCAP (Futures market)",
            "code": "NFTPERP/USDT.MCAP",
            "future": {
                "settlementAsset": "bf1e88d19db4b3ca0d1d5bdb73718a01686b18cf731ca26adedf3c8b83802bba",
                "quoteName": "USDT",
                "dataSourceSpecForSettlementData": {
                    "external": {
                        "ethOracle": {
                            "sourceChainId": "42161",
                            "address": "0x302461E6dBF45e59acb3BE9a9c84C0a997779612",
                            "abi": '[{"type":"function","name":"getData","inputs":[{"name":"identifier","type":"tuple","internalType":"struct SettlementOracle.Identifier","components":[{"name":"liveness","type":"uint64","internalType":"uint64"},{"name":"bondCurrency","type":"address","internalType":"contract IERC20"},{"name":"minimumBond","type":"uint256","internalType":"uint256"},{"name":"maximumBond","type":"uint256","internalType":"uint256"},{"name":"marketCode","type":"string","internalType":"string"},{"name":"quoteName","type":"string","internalType":"string"},{"name":"enactmentDate","type":"string","internalType":"string"},{"name":"ipfsLink","type":"string","internalType":"string"}]}],"outputs":[{"name":"","type":"bool","internalType":"bool"},{"name":"","type":"uint256","internalType":"uint256"}],"stateMutability":"nonpayable"}]',
                            "method": "getData",
                            "args": [
                                {
                                    "liveness": 28800,
                                    "bondCurrency": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
                                    "minimumBond": 500000000,
                                    "maximumBond": 100000000000,
                                    "ipfsLink": "ipfs://bafybeiepzqdjoxwzeh2vzwi5c4473vddemqjihc26tbuu32vkasisk537i",
                                    "marketCode": "NFTPERP/USDT.MCAP",
                                    "quoteName": "USDT",
                                    "enactmentDate": "2024-03-20T11:00:00Z",
                                }
                            ],
                            "requiredConfirmations": "64",
                            "trigger": {"timeTrigger": {"every": "600"}},
                            "filters": [
                                {
                                    "key": {
                                        "name": "resolved",
                                        "type": "TYPE_BOOLEAN",
                                    },
                                    "conditions": [
                                        {
                                            "operator": "OPERATOR_EQUALS",
                                            "value": "true",
                                        }
                                    ],
                                },
                                {
                                    "key": {
                                        "name": "price",
                                        "type": "TYPE_INTEGER",
                                        "numberDecimalPlaces": "18",
                                    },
                                    "conditions": [
                                        {
                                            "operator": "OPERATOR_GREATER_THAN_OR_EQUAL",
                                            "value": "0",
                                        }
                                    ],
                                },
                            ],
                            "normalisers": [
                                {"name": "resolved", "expression": "$[0]"},
                                {"name": "price", "expression": "$[1]"},
                            ],
                        }
                    }
                },
                "dataSourceSpecForTradingTermination": {
                    "external": {
                        "ethOracle": {
                            "sourceChainId": "42161",
                            "address": "0x6d0b3a00265b8b4a1d22cf466c331014133ba614",
                            "abi": '[{"type":"function","name":"getData","inputs":[{"name":"identifier","type":"tuple","internalType":"struct TerminationOracle.Identifier","components":[{"name":"bondCurrency","type":"address","internalType":"contract IERC20"},{"name":"minimumBond","type":"uint256","internalType":"uint256"},{"name":"maximumBond","type":"uint256","internalType":"uint256"},{"name":"liveness","type":"uint64","internalType":"uint64"},{"name":"marketCode","type":"string","internalType":"string"},{"name":"quoteName","type":"string","internalType":"string"},{"name":"enactmentDate","type":"string","internalType":"string"},{"name":"ipfsLink","type":"string","internalType":"string"},{"name":"conditionalSettlementOracle","type":"address","internalType":"contract SettlementOracle"}]}],"outputs":[{"name":"","type":"bool","internalType":"bool"},{"name":"","type":"uint256","internalType":"uint256"},{"name":"","type":"bool","internalType":"bool"}],"stateMutability":"nonpayable"}]',
                            "method": "getData",
                            "args": [
                                {
                                    "liveness": 28800,
                                    "bondCurrency": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
                                    "minimumBond": 500000000,
                                    "maximumBond": 100000000000,
                                    "ipfsLink": "ipfs://bafybeiepzqdjoxwzeh2vzwi5c4473vddemqjihc26tbuu32vkasisk537i",
                                    "marketCode": "NFTPERP/USDT.MCAP",
                                    "quoteName": "USDT",
                                    "enactmentDate": "2024-03-20T11:00:00Z",
                                    "conditionalSettlementOracle": "0x302461E6dBF45e59acb3BE9a9c84C0a997779612",
                                }
                            ],
                            "requiredConfirmations": "64",
                            "trigger": {"timeTrigger": {"every": "600"}},
                            "filters": [
                                {
                                    "key": {
                                        "name": "resolved",
                                        "type": "TYPE_BOOLEAN",
                                    },
                                    "conditions": [
                                        {
                                            "operator": "OPERATOR_EQUALS",
                                            "value": "true",
                                        }
                                    ],
                                },
                                {
                                    "key": {
                                        "name": "terminated",
                                        "type": "TYPE_BOOLEAN",
                                    },
                                    "conditions": [
                                        {
                                            "operator": "OPERATOR_EQUALS",
                                            "value": "true",
                                        }
                                    ],
                                },
                            ],
                            "normalisers": [
                                {"name": "resolved", "expression": "$[0]"},
                                {"name": "terminated", "expression": "$[2]"},
                            ],
                        }
                    }
                },
                "dataSourceSpecBinding": {
                    "settlementDataProperty": "price",
                    "tradingTerminationProperty": "terminated",
                },
            },
        },
        "metadata": [
            "base:NFTPERP",
            "quote:USDT",
            "enactment:2024-03-20T11:00:00Z",
            "settlement:fromOracle",
            "class:fx/crypto",
            "oracle:uma",
            "sector:defi",
            "oracleChain:arbitrum",
            "domain:nftperp.xyz",
        ],
        "priceMonitoringParameters": {
            "triggers": [
                {
                    "horizon": "120",
                    "probability": "0.9999999",
                    "auctionExtension": "60",
                },
                {
                    "horizon": "120",
                    "probability": "0.9999999",
                    "auctionExtension": "60",
                },
                {
                    "horizon": "120",
                    "probability": "0.9999999",
                    "auctionExtension": "60",
                },
                {
                    "horizon": "120",
                    "probability": "0.9999999",
                    "auctionExtension": "60",
                },
                {
                    "horizon": "120",
                    "probability": "0.9999999",
                    "auctionExtension": "60",
                },
                {
                    "horizon": "200",
                    "probability": "0.9999999",
                    "auctionExtension": "300",
                },
                {
                    "horizon": "200",
                    "probability": "0.9999999",
                    "auctionExtension": "300",
                },
                {
                    "horizon": "200",
                    "probability": "0.9999999",
                    "auctionExtension": "300",
                },
                {
                    "horizon": "200",
                    "probability": "0.9999999",
                    "auctionExtension": "300",
                },
                {
                    "horizon": "200",
                    "probability": "0.9999999",
                    "auctionExtension": "300",
                },
                {
                    "horizon": "400",
                    "probability": "0.9999999",
                    "auctionExtension": "900",
                },
                {
                    "horizon": "400",
                    "probability": "0.9999999",
                    "auctionExtension": "900",
                },
                {
                    "horizon": "400",
                    "probability": "0.9999999",
                    "auctionExtension": "900",
                },
                {
                    "horizon": "400",
                    "probability": "0.9999999",
                    "auctionExtension": "900",
                },
                {
                    "horizon": "400",
                    "probability": "0.9999999",
                    "auctionExtension": "900",
                },
                {
                    "horizon": "400",
                    "probability": "0.9999999",
                    "auctionExtension": "900",
                },
                {
                    "horizon": "500",
                    "probability": "0.9999999",
                    "auctionExtension": "1800",
                },
                {
                    "horizon": "500",
                    "probability": "0.9999999",
                    "auctionExtension": "1800",
                },
                {
                    "horizon": "500",
                    "probability": "0.9999999",
                    "auctionExtension": "1800",
                },
                {
                    "horizon": "500",
                    "probability": "0.9999999",
                    "auctionExtension": "1800",
                },
                {
                    "horizon": "500",
                    "probability": "0.9999999",
                    "auctionExtension": "1800",
                },
                {
                    "horizon": "500",
                    "probability": "0.9999999",
                    "auctionExtension": "1800",
                },
                {
                    "horizon": "500",
                    "probability": "0.9999999",
                    "auctionExtension": "1800",
                },
                {
                    "horizon": "620",
                    "probability": "0.9999999",
                    "auctionExtension": "3600",
                },
                {
                    "horizon": "620",
                    "probability": "0.9999999",
                    "auctionExtension": "3600",
                },
                {
                    "horizon": "620",
                    "probability": "0.9999999",
                    "auctionExtension": "3600",
                },
                {
                    "horizon": "620",
                    "probability": "0.9999999",
                    "auctionExtension": "3600",
                },
                {
                    "horizon": "620",
                    "probability": "0.9999999",
                    "auctionExtension": "3600",
                },
                {
                    "horizon": "620",
                    "probability": "0.9999999",
                    "auctionExtension": "3600",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "2700",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "43200",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "43200",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "43200",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "43200",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "43200",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "43200",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "43200",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "43200",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "43200",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "43200",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "43200",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "43200",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
            ]
        },
        "logNormal": {
            "tau": 0.0002281542323,
            "riskAversionParameter": 0.01,
            "params": {"mu": 0, "r": 0, "sigma": 5},
        },
        "liquiditySlaParameters": {
            "priceRange": "0.05",
            "commitmentMinTimeFraction": "0.5",
            "performanceHysteresisEpochs": "0",
            "slaCompetitionFactor": "0.8",
        },
        "liquidationStrategy": {
            "disposalTimeStep": "5",
            "disposalFraction": "0.1",
            "fullDisposalSize": "10000",
            "maxFractionConsumed": "0.1",
        },
        "liquidityFeeSettings": {
            "method": "METHOD_CONSTANT",
            "feeConstant": "0.005",
        },
        "liquidityMonitoringParameters": {
            "targetStakeParameters": {"timeWindow": "3600", "scalingFactor": "0.05"}
        },
        "markPriceConfiguration": {
            "compositePriceType": "COMPOSITE_PRICE_TYPE_LAST_TRADE"
        },
    }
)
