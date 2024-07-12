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
            "code": "BTC/USDT-FUTR",
            "name": "Bitcoin / Tether USD (Future)",
            "future": {
                "settlementAsset": "bf1e88d19db4b3ca0d1d5bdb73718a01686b18cf731ca26adedf3c8b83802bba",
                "quoteName": "USDT",
                "dataSourceSpecForSettlementData": {
                    "external": {
                        "oracle": {
                            "signers": [{"pubKey": {"key": None}}],
                            "filters": [
                                {
                                    "key": {
                                        "name": "prices.btc.value",
                                        "type": "TYPE_INTEGER",
                                        "numberDecimalPlaces": "18",
                                    },
                                    "conditions": [
                                        {
                                            "operator": "OPERATOR_GREATER_THAN",
                                            "value": "0",
                                        },
                                    ],
                                }
                            ],
                        }
                    }
                },
                "dataSourceSpecForTradingTermination": {
                    "external": {
                        "oracle": {
                            "signers": [{"pubKey": {"key": None}}],
                            "filters": [
                                {
                                    "key": {
                                        "name": "termination",
                                        "type": "TYPE_BOOLEAN",
                                    },
                                    "conditions": [
                                        {"operator": "OPERATOR_EQUALS", "value": "true"}
                                    ],
                                }
                            ],
                        }
                    }
                },
                "dataSourceSpecBinding": {
                    "settlementDataProperty": "prices.btc.value",
                    "tradingTerminationProperty": "termination",
                },
            },
        },
        "metadata": [
            "base:BTC",
            "quote:USDT",
            "class:fx/crypto",
            "future",
            "sector:defi",
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
            "compositePriceType": "COMPOSITE_PRICE_TYPE_LAST_TRADE",
        },
    }
)
