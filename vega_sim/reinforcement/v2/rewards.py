from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional, List

from vega_sim.scenario.common.agents import VegaService


class Reward(Enum):
    PNL = auto()
    SQ_INVENTORY_PENALTY = auto()
    UNIFIED_PNL = auto()


class BaseRewarder(ABC):
    def __init__(
        self,
        agent_key: str,
        market_id: str,
        asset_id: str,
        agent_wallet: Optional[str] = None,
    ):
        self.agent_key = agent_key
        self.agent_wallet = agent_wallet
        self.asset_id = asset_id
        self.market_id = market_id
        self.last_balance = None

    @abstractmethod
    def get_reward(self, vega: VegaService) -> float:
        pass


class BaseUnifiedRewarder(ABC):
    def __init__(
        self,
        agent_keys: List[str],
        market_id: str,
        asset_id: str,
        agent_wallets: Optional[List[str]] = None,
    ):
        self.agent_keys = agent_keys
        self.agent_wallets = (
            agent_wallets
            if agent_wallets is not None
            else [None for _ in range(len(self.agent_keys))]
        )
        self.asset_id = asset_id
        self.market_id = market_id
        self.last_balance = {}

    @abstractmethod
    def get_reward(self, vega: VegaService) -> float:
        pass


class PnlUnifiedRewarder(BaseUnifiedRewarder):
    def get_reward(self, vega: VegaService) -> float:
        reward = 0
        for key, wallet in zip(self.agent_keys, self.agent_wallets):
            balance = vega.party_account(
                key_name=key,
                wallet_name=wallet,
                asset_id=self.asset_id,
                market_id=self.market_id,
            )
            balance = sum(k for k in balance)
            if self.last_balance.get(key):
                key_reward = balance - self.last_balance.get(key)
            else:
                key_reward = 0
            self.last_balance[key] = balance
            reward += key_reward
        return reward


class PnlRewarder(BaseRewarder):
    def get_reward(self, vega: VegaService) -> float:
        balance = vega.party_account(
            key_name=self.agent_key,
            wallet_name=self.agent_wallet,
            asset_id=self.asset_id,
            market_id=self.market_id,
        )
        balance = sum(k for k in balance)
        if self.last_balance is not None:
            reward = balance - self.last_balance
        else:
            reward = 0
        self.last_balance = balance
        return reward


class SquareInventoryPenalty(BaseRewarder):
    def get_reward(self, vega: VegaService) -> float:
        posn = vega.positions_by_market(
            key_name=self.agent_key,
            wallet_name=self.agent_wallet,
            market_id=self.market_id,
        )

        return (-1 * posn.open_volume**2) if posn is not None else 0


REWARD_ENUM_TO_CLASS = {
    Reward.PNL: PnlRewarder,
    Reward.SQ_INVENTORY_PENALTY: SquareInventoryPenalty,
    Reward.UNIFIED_PNL: PnlUnifiedRewarder,
}
