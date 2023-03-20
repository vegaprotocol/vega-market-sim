from abc import ABC, abstractmethod
from dataclasses import dataclass
from vega_sim.service import VegaService

from typing import Optional


@dataclass(frozen=True)
class State:
    @classmethod
    @abstractmethod
    def from_vega(
        cls, vega: VegaService, for_key_name: str, for_wallet_name: Optional[str] = None
    ):
        return cls()


@dataclass(frozen=True)
class SimpleState(State):
    balance: float
    position: float
    best_bid: float
    best_ask: float

    @classmethod
    def from_vega(
        cls,
        vega: VegaService,
        for_key_name: str,
        market_id: str,
        asset_id: str,
        for_wallet_name: Optional[str] = None,
    ):
        balance = sum(
            vega.party_account(
                for_key_name,
                asset_id=asset_id,
                market_id=market_id,
                wallet_name=for_wallet_name,
            )
        )
        position = vega.positions_by_market(
            key_name=for_key_name, wallet_name=for_wallet_name, market_id=market_id
        )
        position = position.open_volume if position is not None else 0
        best_bid, best_ask = vega.best_prices(market_id=market_id)
        return SimpleState(balance, position, best_bid, best_ask)
