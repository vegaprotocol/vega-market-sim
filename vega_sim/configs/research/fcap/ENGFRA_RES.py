"""ENGFRA.py

Market config for a fully collateralised binary settlement, capped
future market. Market setup as a market for taking bets on the result
of a football game.
"""

from vega_sim.api.market import MarketConfig

CONFIG = MarketConfig(
    {
        "decimalPlaces": "4",
        "positionDecimalPlaces": "1",
        "tickSize": "1",
        "instrument": {
            "code": "ENGvFRA-RES/USDT-FCAP",
            "name": "Euro 2024 England vs. France (Final Result) / Tether USD (Capped Future)",
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
                                        "name": "prices.engfra.value",
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
                    "settlementDataProperty": "prices.engfra.value",
                    "tradingTerminationProperty": "termination",
                },
                "cap": {
                    "maxPrice": 10000,
                    "binarySettlement": True,
                    "fullyCollateralised": True,
                },
            },
        },
        "metadata": [
            "quote:USDT",
            "class:fcap",
            "future",
            "sector:defi",
        ],
        "priceMonitoringParameters": {"triggers": []},
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
