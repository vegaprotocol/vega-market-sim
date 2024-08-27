import logging

from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class Network(Enum):
    NETWORK_UNSPECIFIED = 0
    NETWORK_LOCAL = 1
    NETWORK_MAINNET = 2
    NETWORK_TESTNET = 3
    NETWORK_STAGNET = 4

    @property
    def config(self) -> Path:
        match self.value:
            case 0:
                return None
            case 1:
                return None
            case _:
                return Path(__file__).parent / f"{self.name.lower().split('_')[1]}.toml"
