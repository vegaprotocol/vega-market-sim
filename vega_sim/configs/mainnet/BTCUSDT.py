"""BTCUSDT.py

Market config matching latest proposal for BTCUSD market on mainnet.
https://governance.vega.xyz/proposals/dbde48b2ec84bf58d9e59aab2d9eb04dc888e2fd4aa7488c7a80e2dc44eba39e
"""

from vega_sim.api.market import MarketConfig

CONFIG = MarketConfig(
    {
        "decimalPlaces": "1",
        "positionDecimalPlaces": "4",
        "tickSize": "2",
        "instrument": {
            "code": "BTC/USDT",
            "name": "Bitcoin / Tether USD (Perpetual)",
            "perpetual": {
                "quoteName": "USDT",
                "marginFundingFactor": "0.9",
                "interestRate": "0.1095",
                "clampLowerBound": "-0.0005",
                "clampUpperBound": "0.0005",
                "dataSourceSpecForSettlementSchedule": {
                    "internal": {
                        "timeTrigger": {
                            "conditions": [
                                {"operator": "OPERATOR_GREATER_THAN", "value": "0"}
                            ],
                            "triggers": [{"initial": "1709575200", "every": "28800"}],
                        }
                    }
                },
                "dataSourceSpecForSettlementData": {
                    "external": {
                        "ethOracle": {
                            "address": "0x719abd606155442c21b7d561426d42bd0e40a776",
                            "abi": '[{"inputs": [{"internalType": "bytes32", "name": "id", "type": "bytes32"}], "name": "getPrice", "outputs": [{"internalType": "int256", "name": "", "type": "int256" }], "stateMutability": "view", "type": "function"}]',
                            "method": "getPrice",
                            "args": ["5i32yLSoX+GmfbRNwS3l2zMPesZrctxliv7fD0pBW0M="],
                            "trigger": {
                                "timeTrigger": {"initial": "1709575200", "every": "60"}
                            },
                            "requiredConfirmations": "3",
                            "filters": [
                                {
                                    "key": {
                                        "name": "btc.price",
                                        "type": "TYPE_INTEGER",
                                        "numberDecimalPlaces": "18",
                                    },
                                    "conditions": [
                                        {
                                            "operator": "OPERATOR_GREATER_THAN",
                                            "value": "0",
                                        }
                                    ],
                                }
                            ],
                            "normalisers": [
                                {"name": "btc.price", "expression": "$[0]"}
                            ],
                            "sourceChainId": "100",
                        }
                    }
                },
                "dataSourceSpecBinding": {
                    "settlementDataProperty": "btc.price",
                    "settlementScheduleProperty": "vegaprotocol.builtin.timetrigger",
                },
                "fundingRateScalingFactor": "1",
                "fundingRateLowerBound": "-0.001",
                "fundingRateUpperBound": "0.001",
                "internalCompositePriceConfiguration": {
                    "decayWeight": "1",
                    "decayPower": "1",
                    "cashAmount": "50000000",
                    "sourceWeights": ["0", "0.999", "0.001", "0"],
                    "sourceStalenessTolerance": ["1m0s", "1m0s", "10m0s", "10m0s"],
                    "compositePriceType": "COMPOSITE_PRICE_TYPE_WEIGHTED",
                    "dataSourcesSpec": [
                        {
                            "external": {
                                "ethOracle": {
                                    "address": "0x719abd606155442c21b7d561426d42bd0e40a776",
                                    "abi": '[{"inputs": [{"internalType": "bytes32", "name": "id", "type": "bytes32"}], "name": "getPrice", "outputs": [{"internalType": "int256", "name": "", "type": "int256" }], "stateMutability": "view", "type": "function"}]',
                                    "method": "getPrice",
                                    "args": [
                                        "5i32yLSoX+GmfbRNwS3l2zMPesZrctxliv7fD0pBW0M="
                                    ],
                                    "trigger": {"timeTrigger": {"every": "60"}},
                                    "requiredConfirmations": "3",
                                    "filters": [
                                        {
                                            "key": {
                                                "name": "btc.price",
                                                "type": "TYPE_INTEGER",
                                                "numberDecimalPlaces": "18",
                                            },
                                            "conditions": [
                                                {
                                                    "operator": "OPERATOR_GREATER_THAN",
                                                    "value": "0",
                                                }
                                            ],
                                        }
                                    ],
                                    "normalisers": [
                                        {"name": "btc.price", "expression": "$[0]"}
                                    ],
                                    "sourceChainId": "100",
                                }
                            }
                        }
                    ],
                    "dataSourcesSpecBinding": [{"priceSourceProperty": "btc.price"}],
                },
            },
        },
        "metadata": [
            "base:BTC",
            "quote:USDT",
            "oracle:pyth",
            "oracleChain:gnosis",
            "class:fx/crypto",
            "perpetual",
            "sector:defi",
            "enactment:2023-12-01T18:00:00Z",
        ],
        "priceMonitoringParameters": {
            "triggers": [
                {
                    "horizon": "21600",
                    "probability": "0.9999999",
                    "auctionExtension": "86400",
                },
                {
                    "horizon": "4320",
                    "probability": "0.9999999",
                    "auctionExtension": "3600",
                },
                {
                    "horizon": "1440",
                    "probability": "0.9999999",
                    "auctionExtension": "1800",
                },
                {
                    "horizon": "360",
                    "probability": "0.9999999",
                    "auctionExtension": "300",
                },
            ]
        },
        "liquidityMonitoringParameters": {
            "targetStakeParameters": {"timeWindow": "3600", "scalingFactor": 0.05},
            "triggeringRatio": "",
            "auctionExtension": "0",
        },
        "logNormal": {
            "riskAversionParameter": 0.000001,
            "tau": 0.000003995,
            "params": {"mu": 0, "r": 0, "sigma": 1},
        },
        "linearSlippageFactor": "0.001",
        "quadraticSlippageFactor": "",
        "liquiditySlaParameters": {
            "priceRange": "0.03",
            "commitmentMinTimeFraction": "0.75",
            "performanceHysteresisEpochs": "1",
            "slaCompetitionFactor": "0.8",
        },
        "liquidityFeeSettings": {"method": "METHOD_MARGINAL_COST"},
        "liquidationStrategy": {
            "disposalTimeStep": "1",
            "disposalFraction": "1",
            "fullDisposalSize": "1000000",
            "maxFractionConsumed": "0.1",
            "disposalSlippageRange": "0.03",
        },
        "markPriceConfiguration": {
            "decayWeight": "1",
            "decayPower": "1",
            "cashAmount": "50000000",
            "sourceWeights": [],
            "sourceStalenessTolerance": [
                "1m0s",
                "1m0s",
                "168h0m0s",
                "168h0m0s",
                "1m0s",
            ],
            "compositePriceType": "COMPOSITE_PRICE_TYPE_MEDIAN",
            "dataSourcesSpec": [
                {
                    "external": {
                        "ethOracle": {
                            "address": "0x719abd606155442c21b7d561426d42bd0e40a776",
                            "abi": '[{"inputs": [{"internalType": "bytes32", "name": "id", "type": "bytes32"}], "name": "getPrice", "outputs": [{"internalType": "int256", "name": "", "type": "int256" }], "stateMutability": "view", "type": "function"}]',
                            "method": "getPrice",
                            "args": ["5i32yLSoX+GmfbRNwS3l2zMPesZrctxliv7fD0pBW0M="],
                            "trigger": {"timeTrigger": {"every": "60"}},
                            "requiredConfirmations": "3",
                            "filters": [
                                {
                                    "key": {
                                        "name": "btc.price",
                                        "type": "TYPE_INTEGER",
                                        "numberDecimalPlaces": "18",
                                    },
                                    "conditions": [
                                        {
                                            "operator": "OPERATOR_GREATER_THAN",
                                            "value": "0",
                                        }
                                    ],
                                }
                            ],
                            "normalisers": [
                                {"name": "btc.price", "expression": "$[0]"}
                            ],
                            "sourceChainId": "100",
                        }
                    }
                },
                {
                    "external": {
                        "ethOracle": {
                            "address": "0x719abd606155442c21b7d561426d42bd0e40a776",
                            "abi": '[{"inputs": [{"internalType": "bytes32", "name": "id", "type": "bytes32"}], "name": "getPrice", "outputs": [{"internalType": "int256", "name": "", "type": "int256" }], "stateMutability": "view", "type": "function"}]',
                            "method": "getPrice",
                            "args": ["5i32yLSoX+GmfbRNwS3l2zMPesZrctxliv7fD0pBW0M="],
                            "trigger": {"timeTrigger": {"every": "60"}},
                            "requiredConfirmations": "3",
                            "filters": [
                                {
                                    "key": {
                                        "name": "btc.price",
                                        "type": "TYPE_INTEGER",
                                        "numberDecimalPlaces": "18",
                                    },
                                    "conditions": [
                                        {
                                            "operator": "OPERATOR_GREATER_THAN",
                                            "value": "0",
                                        }
                                    ],
                                }
                            ],
                            "normalisers": [
                                {"name": "btc.price", "expression": "$[0]"}
                            ],
                            "sourceChainId": "100",
                        }
                    }
                },
            ],
            "dataSourcesSpecBinding": [
                {"priceSourceProperty": "btc.price"},
                {"priceSourceProperty": "btc.price"},
            ],
        },
    }
)
