from vega_sim.api.market import SpotMarketConfig

CONFIG = SpotMarketConfig(
    {
        "priceDecimalPlaces": "2",
        "sizeDecimalPlaces": "4",
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
                    "auctionExtension": "21600",
                },
                {
                    "horizon": "21600",
                    "probability": "0.9999999",
                    "auctionExtension": "21600",
                },
                {
                    "horizon": "21600",
                    "probability": "0.9999999",
                    "auctionExtension": "21600",
                },
                {
                    "horizon": "21600",
                    "probability": "0.9999999",
                    "auctionExtension": "21600",
                },
                {
                    "horizon": "4320",
                    "probability": "0.9999999",
                    "auctionExtension": "900",
                },
                {
                    "horizon": "4320",
                    "probability": "0.9999999",
                    "auctionExtension": "900",
                },
                {
                    "horizon": "4320",
                    "probability": "0.9999999",
                    "auctionExtension": "900",
                },
                {
                    "horizon": "4320",
                    "probability": "0.9999999",
                    "auctionExtension": "900",
                },
                {
                    "horizon": "1440",
                    "probability": "0.9999999",
                    "auctionExtension": "450",
                },
                {
                    "horizon": "1440",
                    "probability": "0.9999999",
                    "auctionExtension": "450",
                },
                {
                    "horizon": "1440",
                    "probability": "0.9999999",
                    "auctionExtension": "450",
                },
                {
                    "horizon": "1440",
                    "probability": "0.9999999",
                    "auctionExtension": "450",
                },
                {
                    "horizon": "360",
                    "probability": "0.9999999",
                    "auctionExtension": "75",
                },
                {
                    "horizon": "360",
                    "probability": "0.9999999",
                    "auctionExtension": "75",
                },
                {
                    "horizon": "360",
                    "probability": "0.9999999",
                    "auctionExtension": "75",
                },
                {
                    "horizon": "360",
                    "probability": "0.9999999",
                    "auctionExtension": "75",
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
