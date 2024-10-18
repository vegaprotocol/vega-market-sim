"""vega_sim/builders/data/spec.py

Moule contains functions for building protobuf messages defined in
vega/protos/sources/data/spec.proto

Attributes:
    logger (logging.Logger): module level logger
"""

import logging
import datetime

import vega_protos.protos.vega as vega_protos

from typing import Optional, Dict, List
from vega_sim.builders.exceptions import raise_custom_build_errors

logger = logging.getLogger(__name__)


@raise_custom_build_errors
def filter(
    key: vega_protos.data.v1.spec.PropertyKey,
    conditions: Optional[List[vega_protos.data.v1.spec.Condition]] = None,
) -> vega_protos.data.v1.spec.Filter:
    proto = vega_protos.data.v1.spec.Filter(key=key)
    if conditions is not None:
        proto.conditions.extend(conditions)
    return proto


@raise_custom_build_errors
def property_key(
    name: str,
    type: vega_protos.data.v1.spec.PropertyKey.Type.Value,
    number_decimal_places: Optional[int] = None,
) -> vega_protos.data.v1.spec.PropertyKey:
    return vega_protos.data.v1.spec.PropertyKey(
        name=name,
        type=type,
        number_decimal_places=(
            int(number_decimal_places) if number_decimal_places is not None else None
        ),
    )


@raise_custom_build_errors
def condition(
    operator: vega_protos.data.v1.spec.Condition.Operator.Value,
    value: int,
) -> vega_protos.data.v1.spec.PropertyKey:
    return vega_protos.data.v1.spec.Condition(
        operator=operator,
        value=str(value),
    )


@raise_custom_build_errors
def internal_time_trigger(
    every: datetime.timedelta,
    initial: Optional[datetime.datetime] = None,
) -> vega_protos.data.v1.spec.InternalTimeTrigger:
    return vega_protos.data.v1.spec.InternalTimeTrigger(
        initial=int(initial.timestamp() // 1e9) if initial else None,
        every=int(every.seconds),
    )
