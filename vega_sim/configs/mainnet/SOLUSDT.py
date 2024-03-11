"""SOLUSDT.py

Market config matching latest proposal for SOLUSD market on mainnet.
https://governance.vega.xyz/proposals/6adf4314db2c637dc1fb2276386ee4c2ed9a7b998ed55e8c30991b8cc82bf921
"""

from vega_sim.api.market import MarketConfig

CONFIG = MarketConfig(
    {
        "decimalPlaces": "2",
        "positionDecimalPlaces": "1",
        "tickSize": "2",
        "instrument": {
            "name": "Solana / Tether USD (Perpetual)",
            "code": "SOL/USDT",
            "perpetual": {
                "settlementAsset": "bf1e88d19db4b3ca0d1d5bdb73718a01686b18cf731ca26adedf3c8b83802bba",
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
                            "triggers": [{"initial": "1709676000", "every": "28800"}],
                        }
                    }
                },
                "dataSourceSpecForSettlementData": {
                    "external": {
                        "ethOracle": {
                            "address": "0x719abd606155442c21b7d561426d42bd0e40a776",
                            "abi": '[{"inputs": [{"internalType": "bytes32", "name": "id", "type": "bytes32"}], "name": "getPrice", "outputs": [{"internalType": "int256", "name": "", "type": "int256" }], "stateMutability": "view", "type": "function"}]',
                            "method": "getPrice",
                            "args": ["7w2Lb9os66QdoV1AldHaOSoNL47Qxse8D0z6yMKAtW0="],
                            "trigger": {
                                "timeTrigger": {"initial": "1709676000", "every": "60"}
                            },
                            "requiredConfirmations": "3",
                            "filters": [
                                {
                                    "key": {
                                        "name": "sol.price",
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
                                {"name": "sol.price", "expression": "$[0]"}
                            ],
                            "sourceChainId": "100",
                        }
                    }
                },
                "dataSourceSpecBinding": {
                    "settlementDataProperty": "sol.price",
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
                                        "7w2Lb9os66QdoV1AldHaOSoNL47Qxse8D0z6yMKAtW0="
                                    ],
                                    "trigger": {"timeTrigger": {"every": "60"}},
                                    "requiredConfirmations": "3",
                                    "filters": [
                                        {
                                            "key": {
                                                "name": "sol.price",
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
                                        {"name": "sol.price", "expression": "$[0]"}
                                    ],
                                    "sourceChainId": "100",
                                }
                            }
                        }
                    ],
                    "dataSourcesSpecBinding": [{"priceSourceProperty": "sol.price"}],
                },
            },
        },
        "decimalPlaces": "2",
        "metadata": [
            "base:SOL",
            "quote:USDT",
            "oracle:pyth",
            "oracleChain:gnosis",
            "class:fx/crypto",
            "perpetual",
            "sector:defi",
            "enactment:2024-03-05T22:00:00Z",
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
            "tau": 0.0000071,
            "params": {"mu": 0, "r": 0, "sigma": 1.5},
        },
        "positionDecimalPlaces": "1",
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
        },
        "markPriceConfiguration": {
            "decayWeight": "1",
            "decayPower": "1",
            "cashAmount": "0",
            "sourceWeights": [
                "1",
                "1",
                # "1",
                "1",
            ],
            "sourceStalenessTolerance": [
                "1m0s",
                "1m0s",
                # "1m0s",
                "1m0s",
            ],
            "compositePriceType": "COMPOSITE_PRICE_TYPE_WEIGHTED",
            # "dataSourcesSpec": [
            #     {
            #         "external": {
            #             "ethOracle": {
            #                 "address": "0x719abd606155442c21b7d561426d42bd0e40a776",
            #                 "abi": '[{"inputs": [{"internalType": "bytes32", "name": "id", "type": "bytes32"}], "name": "getPrice", "outputs": [{"internalType": "int256", "name": "", "type": "int256" }], "stateMutability": "view", "type": "function"}]',
            #                 "method": "getPrice",
            #                 "args": ["7w2Lb9os66QdoV1AldHaOSoNL47Qxse8D0z6yMKAtW0="],
            #                 "trigger": {"timeTrigger": {"every": "60"}},
            #                 "requiredConfirmations": "3",
            #                 "filters": [
            #                     {
            #                         "key": {
            #                             "name": "sol.price",
            #                             "type": "TYPE_INTEGER",
            #                             "numberDecimalPlaces": "18",
            #                         },
            #                         "conditions": [
            #                             {
            #                                 "operator": "OPERATOR_GREATER_THAN",
            #                                 "value": "0",
            #                             }
            #                         ],
            #                     }
            #                 ],
            #                 "normalisers": [
            #                     {"name": "sol.price", "expression": "$[0]"}
            #                 ],
            #                 "sourceChainId": "100",
            #             }
            #         }
            #     }
            # ],
            # "dataSourcesSpecBinding": [{"priceSourceProperty": "sol.price"}],
        },
    }
)
