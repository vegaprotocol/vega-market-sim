from vega_sim.api.market import MarketConfig


class BenchmarkConfig:
    def __init__(
        self,
        market_config: MarketConfig,
        initial_price: float,
        annualised_volatility: float,
        notional_trade_volume: int,
    ):
        self.market_config = market_config
        self.initial_price = initial_price
        self.annualised_volatility = annualised_volatility
        self.notional_trade_volume = notional_trade_volume
