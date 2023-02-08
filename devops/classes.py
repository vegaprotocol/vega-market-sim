from dataclasses import dataclass
from typing import Optional, List

from vega_sim.scenario.common.utils.price_process import Granularity


MAX_FAUCET = 1e10


@dataclass
class MarketManagerArgs:
    market_name: str
    market_code: str
    asset_name: str
    adp: int
    mdp: int
    pdp: int
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
class MomentumTraderArgs:
    order_intensity: int
    order_volume: float
    initial_mint: Optional[int] = MAX_FAUCET


@dataclass
class SensitiveTraderArgs:
    order_intensity: List[int]
    order_volume: List[float]
    price_half_life: List[float]
    initial_mint: Optional[int] = MAX_FAUCET


@dataclass
class SimulationArgs:
    n_steps: int
    step_length_seconds: float
    granularity: Granularity
    coinbase_code: str
    start_date: Optional[str] = "2022-08-01 00:00:00"
    randomise_history: Optional[bool] = False
