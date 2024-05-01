from typing import Union, Optional
from vega_sim.api.market import MarketConfig, SpotMarketConfig


class BenchmarkConfig:
    def __init__(
        self,
        market_config: Union[MarketConfig, SpotMarketConfig],
        initial_price: float,
        annualised_volatility: float,
        notional_trade_volume: int,
        historic_data_code: Optional[str] = None,
    ):
        self.market_config = market_config
        self.initial_price = initial_price
        self.annualised_volatility = annualised_volatility
        self.notional_trade_volume = notional_trade_volume
        self.historic_data_code = historic_data_code
