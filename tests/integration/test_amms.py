import pytest

from vega_sim.null_service import VegaServiceNull

from tests.integration.utils.fixtures import (
    WalletConfig,
    vega_service,
    vega_service_with_market,
    create_and_faucet_wallet,
)

import vega_protos as protos


def next_epoch(vega: VegaServiceNull):
    forwards = 0
    epoch_seq = vega.statistics().epoch_seq
    while epoch_seq == vega.statistics().epoch_seq:
        vega.wait_fn(1)
        forwards += 1
        if forwards > 2 * 10 * 60:
            raise Exception(
                "Epoch not started after forwarding the duration of two epochs."
            )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()


AMM = WalletConfig("amm", "amm")
TRADER = WalletConfig("trader", "trader")


@pytest.mark.integration
def test_amm(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market

    create_and_faucet_wallet(vega=vega, wallet=AMM, amount=1e9)
    create_and_faucet_wallet(vega=vega, wallet=TRADER, amount=1e9)
    vega.wait_for_total_catchup()

    # Create the AMM
    market_id = vega.all_markets()[0].id
    vega.submit_amm(
        key_name=AMM.name,
        market_id=market_id,
        commitment_amount=10000,
        slippage_tolerance=0.1,
        base=0.3,
        lower_bound=0.2,
        upper_bound=0.4,
        leverage_at_lower_bound=2.0,
        leverage_at_upper_bound=2.0,
        proposed_fee=0.001,
    )
    vega.wait_fn(2)
    vega.wait_for_total_catchup()

    # Check querying by owner or sub-account id returns the same AMM
    amm0 = vega.list_amms(market_id=market_id, key_name=AMM.name)[0]
    amm1 = vega.list_amms(market_id=market_id, amm_party_id=amm0.amm_party_id)[0]
    assert amm0 == amm1

    # Amend the AMM
    new_commitment = 20000
    new_lower_bound = 0.1
    new_upper_bound = 0.5
    vega.amend_amm(
        key_name=AMM.name,
        market_id=market_id,
        commitment_amount=new_commitment,
        slippage_tolerance=0.1,
        base=0.3,
        lower_bound=new_lower_bound,
        upper_bound=new_upper_bound,
        leverage_at_lower_bound=2.0,
        leverage_at_upper_bound=2.0,
        proposed_fee=0.001,
    )
    vega.wait_fn(2)
    vega.wait_for_total_catchup()
    amm2 = vega.list_amms(market_id=market_id, key_name=AMM.name)[0]
    assert amm2.commitment == new_commitment
    assert amm2.parameters.lower_bound == new_lower_bound
    assert amm2.parameters.upper_bound == new_upper_bound

    # Cancel the AMM
    vega.cancel_amm(
        key_name=AMM.name,
        market_id=market_id,
        method=protos.vega.commands.v1.commands.CancelAMM.Method.METHOD_IMMEDIATE,
    )
    vega.wait_fn(2)
    vega.wait_for_total_catchup()
    amm3 = vega.list_amms(market_id=market_id, key_name=AMM.name)[0]
    assert amm3.status == protos.vega.events.v1.events.AMM.Status.STATUS_CANCELLED
