import pytest

from vega_query.service.service_trading_data import TradingDataService
from tests.vega_query.fixtures import logger, tds, governance_data
from typing import List, Any

import vega_protos.protos as protos
import pytest


@pytest.mark.vega_query
def test_list_governance_data(tds: TradingDataService):
    for governance_data in tds.list_governance_data(max_pages=1):
        assert isinstance(governance_data, protos.vega.governance.GovernanceData)


@pytest.mark.vega_query
@pytest.mark.parametrize(
    "proposal_state", protos.vega.governance.Proposal.State.values()
)
def test_list_governance_data_proposal_state(tds: TradingDataService, proposal_state):
    expected = protos.vega.governance.Proposal.State.Name(proposal_state)
    for governance_data in tds.list_governance_data(
        proposal_state=proposal_state,
        max_pages=1,
    ):
        try:
            assert governance_data.proposal.state == proposal_state
        except AssertionError as e:
            if (
                governance_data.proposal_type
                == protos.vega.governance.GovernanceData.Type.TYPE_BATCH
            ):
                continue
            id = governance_data.proposal.id
            actual = protos.vega.governance.Proposal.State.Name(
                governance_data.proposal.state
            )
            logger.error(f"Proposal: {id} | Expected: {expected} | Actual: {actual}")
            raise e
    logger.debug(f"Successfully tested proposal state: {expected}")


@pytest.mark.vega_query
@pytest.mark.parametrize(
    "proposal_type",
    protos.data_node.api.v2.trading_data.ListGovernanceDataRequest.Type.values(),
)
def test_list_governance_data_proposal_type(tds: TradingDataService, proposal_type):
    for governance_data in tds.list_governance_data(
        proposal_type=proposal_type,
        max_pages=1,
    ):
        # TODO: Add an advanced type check
        assert isinstance(governance_data, protos.vega.governance.GovernanceData)


def test_list_governance_data_proposer_party_id(
    tds: TradingDataService,
    governance_data: List[protos.vega.governance.GovernanceData],
):
    proposer_party_id = governance_data[0].proposal.party_id
    for result in tds.list_governance_data(
        proposer_party_id=proposer_party_id,
        max_pages=1,
    ):
        try:
            assert result.proposal.party_id == proposer_party_id
        except AssertionError as e:
            id = result.proposal.id
            actual = result.proposal.party_id
            logger.error(
                f"Proposal: {id} | Expected: {proposer_party_id} | Actual: {actual}"
            )
            raise e
