"""EGLPUSDT.py

Market config matching latest proposal for EGLP/USDT.POINTS market on mainnet.
https://governance.vega.xyz/proposals/2b93e5121c2704a00d0df3075aecbfb7e25b1106319cf47f53320f921b2f6d27
"""

from vega_sim.api.market import MarketConfig

CONFIG = MarketConfig(
    {
        "tickSize": "2",
        "instrument": {
            "name": "EigenLayer Points / USDT (Futures market)",
            "code": "EGLP/USDT.POINTS",
            "future": {
                "settlementAsset": "bf1e88d19db4b3ca0d1d5bdb73718a01686b18cf731ca26adedf3c8b83802bba",
                "quoteName": "USDT",
                "dataSourceSpecForSettlementData": {
                    "external": {
                        "ethOracle": {
                            "address": "0x302461E6dBF45e59acb3BE9a9c84C0a997779612",
                            "abi": '[{"type":"function","name":"getData","inputs":[{"name":"identifier","type":"tuple","internalType":"struct SettlementOracle.Identifier","components":[{"name":"liveness","type":"uint64","internalType":"uint64"},{"name":"bondCurrency","type":"address","internalType":"contract IERC20"},{"name":"minimumBond","type":"uint256","internalType":"uint256"},{"name":"maximumBond","type":"uint256","internalType":"uint256"},{"name":"marketCode","type":"string","internalType":"string"},{"name":"quoteName","type":"string","internalType":"string"},{"name":"enactmentDate","type":"string","internalType":"string"},{"name":"ipfsLink","type":"string","internalType":"string"}]}],"outputs":[{"name":"","type":"bool","internalType":"bool"},{"name":"","type":"uint256","internalType":"uint256"}],"stateMutability":"nonpayable"}]',
                            "method": "getData",
                            "args": [
                                {
                                    "bondCurrency": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
                                    "enactmentDate": "2024-03-12T11:00:00Z",
                                    "ipfsLink": "ipfs://bafybeiazlsl2ilitnh4p3fm7hsem73qsf5bk5l24in2zlso2gtr5t22eai",
                                    "liveness": 28800,
                                    "marketCode": "EGLP/USDT.POINTS",
                                    "maximumBond": 100000000000,
                                    "minimumBond": 500000000,
                                    "quoteName": "USDT",
                                }
                            ],
                            "trigger": {
                                "timeTrigger": {"initial": "1710241200", "every": "600"}
                            },
                            "requiredConfirmations": "64",
                            "filters": [
                                {
                                    "key": {"name": "resolved", "type": "TYPE_BOOLEAN"},
                                    "conditions": [
                                        {"operator": "OPERATOR_EQUALS", "value": "true"}
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
                                {"name": "price", "expression": "$[1]"},
                                {"name": "resolved", "expression": "$[0]"},
                            ],
                            "sourceChainId": "42161",
                        }
                    }
                },
                "dataSourceSpecForTradingTermination": {
                    "external": {
                        "ethOracle": {
                            "address": "0x6d0b3a00265b8b4a1d22cf466c331014133ba614",
                            "abi": '[{"type":"function","name":"getData","inputs":[{"name":"identifier","type":"tuple","internalType":"struct TerminationOracle.Identifier","components":[{"name":"bondCurrency","type":"address","internalType":"contract IERC20"},{"name":"minimumBond","type":"uint256","internalType":"uint256"},{"name":"maximumBond","type":"uint256","internalType":"uint256"},{"name":"liveness","type":"uint64","internalType":"uint64"},{"name":"marketCode","type":"string","internalType":"string"},{"name":"quoteName","type":"string","internalType":"string"},{"name":"enactmentDate","type":"string","internalType":"string"},{"name":"ipfsLink","type":"string","internalType":"string"},{"name":"conditionalSettlementOracle","type":"address","internalType":"contract SettlementOracle"}]}],"outputs":[{"name":"","type":"bool","internalType":"bool"},{"name":"","type":"uint256","internalType":"uint256"},{"name":"","type":"bool","internalType":"bool"}],"stateMutability":"nonpayable"}]',
                            "method": "getData",
                            "args": [
                                {
                                    "bondCurrency": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
                                    "conditionalSettlementOracle": "0x302461E6dBF45e59acb3BE9a9c84C0a997779612",
                                    "enactmentDate": "2024-03-12T11:00:00Z",
                                    "ipfsLink": "ipfs://bafybeiazlsl2ilitnh4p3fm7hsem73qsf5bk5l24in2zlso2gtr5t22eai",
                                    "liveness": 28800,
                                    "marketCode": "EGLP/USDT.POINTS",
                                    "maximumBond": 100000000000,
                                    "minimumBond": 500000000,
                                    "quoteName": "USDT",
                                }
                            ],
                            "trigger": {
                                "timeTrigger": {"initial": "1710241200", "every": "600"}
                            },
                            "requiredConfirmations": "64",
                            "filters": [
                                {
                                    "key": {"name": "resolved", "type": "TYPE_BOOLEAN"},
                                    "conditions": [
                                        {"operator": "OPERATOR_EQUALS", "value": "true"}
                                    ],
                                },
                                {
                                    "key": {
                                        "name": "terminated",
                                        "type": "TYPE_BOOLEAN",
                                    },
                                    "conditions": [
                                        {"operator": "OPERATOR_EQUALS", "value": "true"}
                                    ],
                                },
                            ],
                            "normalisers": [
                                {"name": "resolved", "expression": "$[0]"},
                                {"name": "terminated", "expression": "$[2]"},
                            ],
                            "sourceChainId": "42161",
                        }
                    }
                },
                "dataSourceSpecBinding": {
                    "settlementDataProperty": "price",
                    "tradingTerminationProperty": "terminated",
                },
            },
        },
        "decimalPlaces": "5",
        "metadata": [
            "base:EGLPOINT",
            "quote:USDT",
            "enactment:2024-03-12T11:00:00Z",
            "settlement:fromOracle",
            "class:fx/crypto",
            "oracle:uma",
            "sector:defi",
            "oracleChain:arbitrum",
            "domain:eigenlayer.xyz",
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
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "750",
                    "probability": "0.9999999",
                    "auctionExtension": "7200",
                },
                {
                    "horizon": "800",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "800",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "800",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "800",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "800",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "800",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "800",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "800",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "800",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "800",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "800",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
                {
                    "horizon": "800",
                    "probability": "0.9999999",
                    "auctionExtension": "28800",
                },
            ]
        },
        "liquidityMonitoringParameters": {
            "targetStakeParameters": {"timeWindow": "3600", "scalingFactor": 0.05},
            "triggeringRatio": "",
            "auctionExtension": "0",
        },
        "logNormal": {
            "riskAversionParameter": 0.001,
            "tau": 0.0006844626968,
            "params": {"mu": 0, "r": 0, "sigma": 7},
        },
        "positionDecimalPlaces": "-2",
        "linearSlippageFactor": "0.001",
        "quadraticSlippageFactor": "",
        "liquiditySlaParameters": {
            "priceRange": "0.2",
            "commitmentMinTimeFraction": "0.5",
            "performanceHysteresisEpochs": "1",
            "slaCompetitionFactor": "0.8",
        },
        "liquidityFeeSettings": {"method": "METHOD_MARGINAL_COST"},
        "liquidationStrategy": {
            "disposalTimeStep": "5",
            "disposalFraction": "0.1",
            "fullDisposalSize": "10000",
            "maxFractionConsumed": "0.1",
        },
        "markPriceConfiguration": {
            "compositePriceType": "COMPOSITE_PRICE_TYPE_LAST_TRADE",
        },
    }
)
