from vega_sim.api.market import SpotMarketConfig

CONFIG = SpotMarketConfig(
    {
        "decimalPlaces": "2",
        "positionDecimalPlaces": "4",
        "tickSize": "10",
        "instrument": {
            "name": "Bitcoin / Ethereum (Spot)",
            "code": "BTC/ETH-SPOT",
            "spot": {
                "baseAsset": None,
                "quoteAsset": None,
                "name": "BTC/ETH",
            },
        },
        "metadata": [
            "base:BTC",
            "quote:ETH",
            "class:fx/crypto",
            "spot",
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
        "targetStakeParameters": {"timeWindow": "3600", "scalingFactor": 0.05},
        "logNormal": {
            "riskAversionParameter": 0.000001,
            "tau": 0.000003995,
            "params": {"mu": 0, "r": 0, "sigma": 1},
        },
        "liquiditySlaParameters": {
            "priceRange": "0.03",
            "commitmentMinTimeFraction": "0.75",
            "performanceHysteresisEpochs": "1",
            "slaCompetitionFactor": "0.8",
        },
        "liquidityFeeSettings": {"method": "METHOD_MARGINAL_COST"},
    },
)
