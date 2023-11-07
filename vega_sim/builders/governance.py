"""vega_sim/builders/governance.py

Moule contains functions for building protobuf messages defined in
vega/protos/sources/vega/governance.proto

Attributes:
    logger (logging.Logger): module level logger
"""
import logging
import datetime

import vega_sim.proto.vega as vega_protos

from typing import *
from vega_sim.service import VegaService
from vega_sim.api.helpers import num_to_padded_int


logger = logging.getLogger(__name__)


def proposal_terms(
    closing_timestamp: datetime.datetime,
    enactment_timestamp: datetime.datetime,
    validation_timestamp: Optional[datetime.datetime] = None,
    update_market: Optional[vega_protos.governance.UpdateMarket] = None,
    new_market: Optional[vega_protos.governance.NewMarket] = None,
    update_network_parameter: Optional[
        vega_protos.governance.UpdateNetworkParameter
    ] = None,
    new_asset: Optional[vega_protos.governance.NewAsset] = None,
    new_freeform: Optional[vega_protos.governance.NewFreeform] = None,
    update_asset: Optional[vega_protos.governance.UpdateAsset] = None,
    new_spot_market: Optional[vega_protos.governance.NewSpotMarket] = None,
    update_spot_market: Optional[vega_protos.governance.UpdateSpotMarket] = None,
    new_transfer: Optional[vega_protos.governance.NewTransfer] = None,
    cancel_transfer: Optional[vega_protos.governance.CancelTransfer] = None,
    update_market_state: Optional[vega_protos.governance.UpdateMarketState] = None,
    update_referral_program: Optional[
        vega_protos.governance.UpdateReferralProgram
    ] = None,
    update_volume_discount_program: Optional[
        vega_protos.governance.UpdateVolumeDiscountProgram
    ] = None,
):
    proposal_terms = vega_protos.governance.ProposalTerms(
        closing_timestamp=int(closing_timestamp.timestamp()),
        enactment_timestamp=int(enactment_timestamp.timestamp()),
    )
    if validation_timestamp is not None:
        setattr(
            proposal_terms, "validation_timestamp", validation_timestamp.timestamp()
        )
    if update_market is not None:
        proposal_terms.update_market.CopyFrom(update_market)
    if new_market is not None:
        proposal_terms.update_market.CopyFrom(new_market)
    if update_network_parameter is not None:
        proposal_terms.update_network_parameter.CopyFrom(update_network_parameter)
    if update_market is not None:
        proposal_terms.update_market.CopyFrom(update_market)
    if new_asset is not None:
        proposal_terms.new_asset.CopyFrom(new_asset)
    if new_freeform is not None:
        proposal_terms.new_freeform.CopyFrom(new_freeform)
    if update_asset is not None:
        proposal_terms.update_asset.CopyFrom(update_asset)
    if new_spot_market is not None:
        proposal_terms.new_spot_market.CopyFrom(new_spot_market)
    if update_spot_market is not None:
        proposal_terms.update_spot_market.CopyFrom(update_spot_market)
    if new_transfer is not None:
        proposal_terms.new_transfer.CopyFrom(new_transfer)
    if cancel_transfer is not None:
        proposal_terms.cancel_transfer.CopyFrom(cancel_transfer)
    if update_market_state is not None:
        proposal_terms.update_market_state.CopyFrom(update_market_state)
    if update_referral_program is not None:
        proposal_terms.update_referral_program.CopyFrom(update_referral_program)
    if update_volume_discount_program is not None:
        proposal_terms.update_volume_discount_program.CopyFrom(
            update_volume_discount_program
        )
    return proposal_terms


def proposal_rational(
    description: str, title: str
) -> vega_protos.governance.ProposalRationale:
    return vega_protos.governance.ProposalRationale(
        description=description, title=title
    )


def new_transfer(
    changes: vega_protos.governance.NewTransferConfiguration,
) -> vega_protos.governance.NewTransfer:
    return vega_protos.governance.NewTransfer(changes=changes)


def new_transfer_configuration(
    vega_service: VegaService,
    source_type: vega_protos.vega.AccountType,
    transfer_type: vega_protos.governance.GovernanceTransferType,
    amount: float,
    asset: str,
    fraction_of_balance: float,
    destination_type: vega_protos.vega.AccountType,
    source: Optional[str] = None,
    destination: Optional[str] = None,
    one_off: Optional[str] = None,
    recurring: Optional[str] = None,
) -> vega_protos.governance.NewTransferConfiguration:
    new_transfer_configuration = vega_protos.governance.NewTransferConfiguration(
        source_type=source_type,
        transfer_type=transfer_type,
        amount=str(
            num_to_padded_int(
                to_convert=amount, decimals=vega_service.asset_decimals[asset]
            )
        ),
        asset=asset,
        fraction_of_balance=str(fraction_of_balance),
        destination_type=destination_type,
    )
    if source is not None:
        setattr(new_transfer_configuration, "source", source)
    if destination is not None:
        setattr(new_transfer_configuration, "destination", destination)
    if one_off is not None:
        new_transfer_configuration.one_off.CopyFrom(one_off)
    if recurring is not None:
        new_transfer_configuration.recurring.CopyFrom(recurring)
    return new_transfer_configuration


def one_off_transfer(
    deliver_on: Optional[datetime.datetime] = None,
) -> vega_protos.governance.OneOffTransfer:
    one_off_transfer = vega_protos.governance.OneOffTransfer()
    if deliver_on is not None:
        setattr(one_off_transfer, "deliver_on", int(deliver_on.timestamp() * 1e9))
    return one_off_transfer


def recurring_transfer(
    start_epoch: int,
    end_epoch: Optional[int] = None,
    dispatch_strategy: Optional[vega_protos.vega.DispatchStrategy] = None,
) -> vega_protos.governance.RecurringTransfer:
    recurring_transfer = vega_protos.governance.RecurringTransfer(
        start_epoch=int(start_epoch)
    )
    if end_epoch is not None:
        setattr(recurring_transfer, "end_epoch", int(end_epoch))
    if dispatch_strategy is not None:
        recurring_transfer.dispatch_strategy.CopyFrom(dispatch_strategy)
    return recurring_transfer


def vote_submission(proposal_id: str, value: vega_protos.governance.Vote.Value):
    return vega_protos.commands.v1.commands.VoteSubmission(
        proposal_id=proposal_id, value=value
    )
