import pytest
import logging
import datetime

import vega_protos as protos
from vega_sim.null_service import VegaServiceNull
from tests.integration.utils.fixtures import vega_service

logger = logging.getLogger(__name__)

ASSET = "asset"
PROPOSER = "proposer"
OWNER = "owner"
FUNDER = "funder"
AUX_BID = "bid"
AUX_ASK = "ask"


@pytest.fixture(scope="function")
def init_tests(vega_service):
    # Create a key for proposals.
    vega: VegaServiceNull = vega_service

    # Create proposer key and initialise network and market
    vega.create_key(PROPOSER)
    vega.create_key(OWNER)
    vega.create_key(FUNDER)
    vega.mint(PROPOSER, vega.find_asset_id(symbol="VOTE", enabled=True), 1000)
    vega.create_asset(PROPOSER, ASSET, ASSET, 18, quantum=1)
    vega.wait_for_total_catchup()
    asset_id = vega.find_asset_id(symbol=ASSET, raise_on_missing=True)
    vega.mint(OWNER, asset_id, 10000)
    vega.mint(FUNDER, asset_id, 10000)
    yield vega, asset_id


@pytest.mark.integration
def test_standard_vault(init_tests):
    vega: VegaServiceNull = init_tests[0]
    asset_id = init_tests[1]
    vault_id = vega.create_vault(
        key_name=PROPOSER,
        asset=asset_id,
        fee_period=datetime.timedelta(seconds=1),
        management_fee_factor=0.001,
        performance_fee_factor=0.001,
        redemption_dates=[
            protos.vega.vega.RedemptionDate(
                redemption_date=int(vega.get_blockchain_time(in_seconds=True) + 5),
                redemption_type=protos.vega.vega.RedemptionType.REDEMPTION_TYPE_NORMAL,
                max_fraction="1.0",
            )
        ],
        cut_off_period_length=datetime.timedelta(seconds=1),
    )
    vault_id = vault_id.lower()
    accs = vega.list_accounts()
    for acc in accs:
        if acc.owner == vega.wallet.public_key(FUNDER):
            og_balance = acc.balance
    vega.deposit_to_vault(
        key_name=FUNDER,
        vault_id=vault_id,
        asset_id=asset_id,
        amount=500,
    )
    vega.wait_fn(1)
    vega.wait_for_total_catchup()
    accs = vega.list_accounts()
    for acc in accs:
        if acc.owner == vault_id:
            assert acc.balance > 0
        if acc.owner == vega.wallet.public_key(FUNDER):
            ad_balance = acc.balance
            assert ad_balance < og_balance
