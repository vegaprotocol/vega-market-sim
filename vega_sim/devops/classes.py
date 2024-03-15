from dataclasses import dataclass
from typing import Optional, List, Union

from vega_sim.api.market import MarketConfig, SpotMarketConfig

from vega_sim.scenario.common.utils.price_process import Granularity


MAX_FAUCET = 1e10


@dataclass
class MarketManagerArgs:
    market_config: Union[MarketConfig, SpotMarketConfig]
    max_faucet: Optional[int] = MAX_FAUCET
    initial_mint: Optional[int] = MAX_FAUCET


@dataclass
class MarketMakerArgs:
    market_kappa: float
    market_order_arrival_rate: int
    order_kappa: float
    order_levels: int
    order_spacing: float
    order_size: int
    order_clipping: int
    inventory_upper_boundary: int
    inventory_lower_boundary: int
    fee_amount: float
    commitment_amount: int
    initial_mint: Optional[int] = MAX_FAUCET
    isolated_margin_factor: Optional[float]


@dataclass
class AuctionTraderArgs:
    initial_volume: float
    initial_mint: Optional[int] = MAX_FAUCET


@dataclass
class RandomTraderArgs:
    order_intensity: List[int]
    order_volume: List[float]
    step_bias: List[float]
    initial_mint: Optional[int] = MAX_FAUCET


@dataclass
class SensitiveTraderArgs:
    scale: List[int]
    max_order_size: List[float]
    initial_mint: Optional[int] = MAX_FAUCET


@dataclass
class SimulationArgs:
    n_steps: int
    granularity: Granularity
    coinbase_code: str
    start_date: Optional[str] = "2022-08-01 00:00:00"
    randomise_history: Optional[bool] = False
