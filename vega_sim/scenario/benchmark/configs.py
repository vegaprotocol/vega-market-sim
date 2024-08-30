from typing import Union, List
from vega_sim.api.market import MarketConfig, SpotMarketConfig


class BenchmarkConfig:
    def __init__(
        self,
        market_config: Union[MarketConfig, SpotMarketConfig],
        initial_price: float,
        annualised_volatility: float,
        notional_trade_volume: int,
        risky_trader_funds: int = 1_000,
        process_theta: float = 0,
        drift: float = 0,
    ):
        self.market_config = market_config
        self.initial_price = initial_price
        self.process_theta = process_theta
        self.drift = drift
        self.annualised_volatility = annualised_volatility
        self.notional_trade_volume = notional_trade_volume
        self.risky_trader_funds = risky_trader_funds
        # Price process will be set later
        self.price_process: List[float] = None
