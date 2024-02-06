"""vega_sim/builders/data/data.py

Moule contains functions for building protobuf messages defined in
vega/protos/sources/data/data.proto

Attributes:
    logger (logging.Logger): module level logger
"""

import logging
import datetime

import vega_sim.proto.vega as vega_protos

from typing import Optional, Dict, List
from vega_sim.builders.exceptions import raise_custom_build_errors

logger = logging.getLogger(__name__)


@raise_custom_build_errors
def signer(
    pub_key: vega_protos.data.v1.spec.PropertyKey,
    eth_address: Optional[str] = None,
) -> vega_protos.data.v1.spec.Filter:
    return vega_protos.data.v1.data.Signer(pub_key=pub_key, eth_address=eth_address)


@raise_custom_build_errors
def pub_key(key: str) -> vega_protos.data.v1.data.PubKey:
    return vega_protos.data.v1.data.PubKey(key=key)
