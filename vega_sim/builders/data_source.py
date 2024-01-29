"""vega_sim/builders/data_source.py

Moule contains functions for building protobuf messages defined in
vega/protos/sources/vega/data_source.proto

Attributes:
    logger (logging.Logger): module level logger
"""

import logging
import datetime

import vega_sim.proto.vega as vega_protos

from typing import Optional, List
from vega_sim.builders.exceptions import raise_custom_build_errors


logger = logging.getLogger(__name__)


@raise_custom_build_errors
def data_source_definition(
    internal: Optional[vega_protos.data_source.DataSourceDefinitionInternal] = None,
    external: Optional[vega_protos.data_source.DataSourceDefinitionExternal] = None,
) -> vega_protos.data_source.DataSourceDefinition:
    return vega_protos.data_source.DataSourceDefinition(
        internal=internal, external=external
    )


@raise_custom_build_errors
def data_source_definition_internal(
    time: Optional[vega_protos.data_source.DataSourceSpecConfigurationTime] = None,
    time_trigger: Optional[
        vega_protos.data_source.DataSourceSpecConfigurationTimeTrigger
    ] = None,
) -> vega_protos.data_source.DataSourceDefinitionInternal:
    proto = vega_protos.data_source.DataSourceDefinitionInternal()
    if time is not None:
        proto.time.CopyFrom(time)
    if time_trigger is not None:
        proto.time_trigger.CopyFrom(time_trigger)
    return proto


@raise_custom_build_errors
def data_source_spec_configuration_time(
    conditions: List[vega_protos.data.v1.spec.Condition],
) -> vega_protos.data_source.DataSourceSpecConfigurationTime:
    return vega_protos.data_source.DataSourceSpecConfigurationTime(
        conditions=conditions
    )


@raise_custom_build_errors
def data_source_spec_configuration_time_trigger(
    conditions: List[vega_protos.data.v1.spec.Condition],
    triggers: List[vega_protos.data.v1.spec.InternalTimeTrigger],
) -> vega_protos.data_source.DataSourceSpecConfigurationTimeTrigger:
    return vega_protos.data_source.DataSourceSpecConfigurationTimeTrigger(
        conditions=conditions,
        triggers=triggers,
    )


@raise_custom_build_errors
def data_source_definition_external(
    oracle: Optional[vega_protos.data_source.DataSourceSpecConfiguration] = None,
    eth_oracle: Optional[vega_protos.data_source.EthCallSpec] = None,
) -> vega_protos.data_source.DataSourceDefinitionExternal:
    proto = vega_protos.data_source.DataSourceDefinitionExternal()
    if oracle is not None:
        proto.oracle.CopyFrom(oracle)
    if eth_oracle is not None:
        proto.eth_oracle.CopyFrom(eth_oracle)
    return proto


@raise_custom_build_errors
def data_source_spec_configuration(
    signers: List[vega_protos.data.v1.data.Signer],
    filters: List[vega_protos.data.v1.spec.Filter],
):
    return vega_protos.data_source.DataSourceSpecConfiguration(
        signers=signers,
        filters=filters,
    )


@raise_custom_build_errors
def spec_binding_for_composite_price(
    price_source_property: str,
) -> vega_protos.data_source.SpecBindingForCompositePrice:
    return vega_protos.data_source.SpecBindingForCompositePrice(
        price_source_property=price_source_property
    )
