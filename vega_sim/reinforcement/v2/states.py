from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional
import numpy as np

from vega_sim.proto.vega import markets as markets_protos
from vega_sim.service import VegaService


@dataclass(frozen=True)
class State:
    @classmethod
    @abstractmethod
    def from_vega(
        cls, vega: VegaService, for_key_name: str, for_wallet_name: Optional[str] = None
    ):
        return cls()

    @abstractmethod
    def to_array(self) -> np.array:
        pass


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
    ) -> "SimpleState":
        balance = sum(
            vega.party_account(
                for_key_name,
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

    def to_array(self) -> np.array:
        arr = np.nan_to_num(
            np.array([self.balance, self.position, self.best_bid, self.best_ask])
        )
        norm_factor = max(1e-12, np.linalg.norm(arr))
        arr = arr / norm_factor
        return arr


@dataclass(frozen=True)
class PriceStateWithFees(State):
    position: float
    full_balance: float
    market_in_auction: bool
    bid_prices: list[float]
    ask_prices: list[float]
    bid_volumes: list[float]
    ask_volumes: list[float]
    trading_fee: float

    def to_array(self) -> np.array:
        arr = np.nan_to_num(
            np.array(
                [
                    self.position,
                    self.full_balance,
                    int(self.market_in_auction),
                    self.trading_fee,
                ]
                + self.bid_prices
                + self.bid_volumes
                + self.ask_prices
                + self.ask_volumes
            )
        )
        norm_factor = max(1e-12, np.linalg.norm(arr))
        arr = arr / norm_factor
        return arr

    @classmethod
    def from_vega(
        cls,
        vega: VegaService,
        for_key_name: str,
        market_id: str,
        asset_id: str,
        for_wallet_name: Optional[str] = None,
    ) -> "PriceStateWithFees":
        position = vega.positions_by_market(
            for_key_name, market_id, wallet_name=for_wallet_name
        )

        position = position.open_volume if position else 0
        account = vega.party_account(
            key_name=for_key_name,
            market_id=market_id,
            wallet_name=for_wallet_name,
        )
        book_state = vega.market_depth(
            market_id, num_levels=5
        )  # make num_levels as a parameter?

        market_info = vega.market_info(market_id=market_id)
        fee = (
            float(market_info.fees.factors.liquidity_fee)
            + float(market_info.fees.factors.maker_fee)
            + float(market_info.fees.factors.infrastructure_fee)
        )

        bid_prices = [level.price for level in book_state.buys] + [0] * max(
            0, 5 - len(book_state.buys)
        )
        ask_prices = [level.price for level in book_state.sells] + [0] * max(
            0, 5 - len(book_state.sells)
        )

        return cls(
            position=position,
            full_balance=(account.margin + account.general),
            market_in_auction=(
                not market_info.trading_mode
                == markets_protos.Market.TradingMode.TRADING_MODE_CONTINUOUS
            ),
            bid_prices=bid_prices,
            ask_prices=ask_prices,
            bid_volumes=[level.volume for level in book_state.buys]
            + [0] * max(0, 5 - len(book_state.buys)),
            ask_volumes=[level.volume for level in book_state.sells]
            + [0] * max(0, 5 - len(book_state.sells)),
            trading_fee=fee,
        )


@dataclass(frozen=True)
class PositionOnly(State):
    position: float

    def to_array(self) -> np.array:
        return np.nan_to_num(
            np.array(
                [
                    self.position,
                ]
            )
        )

    @classmethod
    def from_vega(
        cls,
        vega: VegaService,
        for_key_name: str,
        market_id: str,
        asset_id: str,
        for_wallet_name: Optional[str] = None,
    ) -> "PositionOnly":
        position = vega.positions_by_market(
            for_key_name, market_id, wallet_name=for_wallet_name
        )

        return cls(
            position=position.open_volume if position else 0,
        )
