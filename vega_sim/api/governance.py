import logging
import time
from typing import List, Optional
from google.protobuf.json_format import MessageToDict

import requests
import vegaapiclient as vac
import vegaapiclient.generated.data_node.api.v1 as data_node_protos
import vegaapiclient.generated.vega as vega_protos
import vegaapiclient.generated.vega.oracles.v1 as oracles_protos
import vegaapiclient.generated.vega.commands.v1 as commands_protos
from vega_sim.api.helpers import generate_id, wait_for_acceptance

logger = logging.getLogger(__name__)

ASSET_URL_BASE = "{node_url}/assets"


class MissingAssetError(Exception):
    pass


class LowBalanceError(Exception):
    pass


def _find_asset_id(
    asset_name: str,
    all_assets: List[vac.vega.assets.Asset],
    raise_on_missing: bool = False,
) -> Optional[str]:
    for asset in all_assets:
        if asset.details.symbol == asset_name:
            return asset.id
    if raise_on_missing:
        raise MissingAssetError(
            f"{asset_name} asset not found on specified Vega network, "
            + "please propose and create this asset first"
        )


def _default_initial_liquidity_commitment() -> vega_protos.governance.NewMarketCommitment:
    return vega_protos.governance.NewMarketCommitment(
        commitment_amount="10000",
        fee="0.002",
        sells=[
            vega_protos.vega.LiquidityOrder(
                reference=vega_protos.vega.PeggedReference.PEGGED_REFERENCE_MID,
                proportion=1,
                offset="50",
            )
        ],
        buys=[
            vega_protos.vega.LiquidityOrder(
                reference=vega_protos.vega.PeggedReference.PEGGED_REFERENCE_MID,
                proportion=1,
                offset="50",
            )
        ],
        reference="",
    )


def propose_future_market(
    market_name: str,
    pub_key: str,
    login_token: str,
    settlement_asset: str,
    data_client: vac.VegaTradingDataClient,
    termination_pub_key: str,
    wallet_server_url: str,
    governance_asset: str = "VOTE",
    future_asset: str = "BTC",
    position_decimals: Optional[int] = None,
    market_decimals: Optional[int] = None,
    liquidity_commitment: Optional[vega_protos.governance.NewMarketCommitment] = None,
) -> str:
    """Propose a future market as specified user.

    Args:
        market_name:
            str, name of the market
        pub_key:
            str, public key of the proposer
        login_token:
            str, the token returned from proposer wallet login
        settlement_asset:
            str, the asset the market will use for settlement
        data_client:
            VegaTradingDataClient, an instantiated gRPC client for interacting with the
                Vega data node
        termination_pub_key:
            str, the public key of the oracle to be used for trading termination
        wallet_server_url:
            str, the URL for the wallet server
        governance_asset:
            str, the governance asset on the market
        position_decimals:
            int, the decimal place precision to use for positions
            (e.g. 2 means 2dp, so 200 => 2.00, 3 would mean 200 => 0.2)
        market_decimals:
            int, the decimal place precision to use for market prices
            (e.g. 2 means 2dp, so 200 => 2.00, 3 would mean 200 => 0.2)
    Returns:
        str, the ID of the future market proposal on chain
    """
    headers = {"Authorization": f"Bearer {login_token}"}
    # Make sure Vega network has the settlement asset
    asset_request = data_node_protos.trading_data.AssetsRequest()
    assets = data_client.Assets(asset_request).assets
    # Find settlement asset
    settlement_asset_id = _find_asset_id(
        settlement_asset, assets, raise_on_missing=True
    )

    # Make sure Vega network has governance asset
    vote_asset_id = _find_asset_id(governance_asset, assets, raise_on_missing=True)

    # Request accounts for party and check governance asset balance

    party_accounts = data_client.PartyAccounts(
        data_node_protos.trading_data.PartyAccountsRequest(
            party_id=pub_key, asset=vote_asset_id
        )
    ).accounts

    voting_balance = 0
    for account in party_accounts:
        if account.asset == vote_asset_id:
            voting_balance = account.balance
            break

    if voting_balance == 0:
        raise LowBalanceError(
            f"Public key {pub_key} is missing governance token {governance_asset}"
        )

    # Get blockchain time
    # Request the current blockchain time, and convert to time in seconds

    blockchain_time = data_client.GetVegaTime(
        data_node_protos.trading_data.GetVegaTimeRequest()
    ).timestamp
    blockchain_time_seconds = int(blockchain_time / 1e9)

    logger.debug(
        f"Blockchain time: {blockchain_time} ({blockchain_time_seconds} seconds "
        "past epoch)",
    )
    # Propose market
    proposal_ref = f"{pub_key}-{generate_id(6)}"

    # Set closing/enactment and validation timestamps to valid time offsets
    # from the current Vega blockchain time
    closing_time = blockchain_time_seconds + 360
    enactment_time = blockchain_time_seconds + 480
    validation_time = blockchain_time_seconds + 1
    liquidity_commitment = (
        liquidity_commitment
        if liquidity_commitment is not None
        else _default_initial_liquidity_commitment()
    )

    oracle_spec_for_settlement_price = oracles_protos.spec.OracleSpecConfiguration(
        pub_keys=[termination_pub_key],
        filters=[
            oracles_protos.spec.Filter(
                key=oracles_protos.spec.PropertyKey(
                    name=f"price.{future_asset}.value",
                    type=oracles_protos.spec.PropertyKey.Type.TYPE_INTEGER,
                ),
                conditions=[],
            )
        ],
    )
    oracle_spec_for_trading_termination = oracles_protos.spec.OracleSpecConfiguration(
        pub_keys=[termination_pub_key],
        filters=[
            oracles_protos.spec.Filter(
                key=oracles_protos.spec.PropertyKey(
                    name="trading.terminated",
                    type=oracles_protos.spec.PropertyKey.Type.TYPE_BOOLEAN,
                ),
                conditions=[],
            )
        ],
    )

    market_proposal = vega_protos.governance.NewMarket(
        changes=vega_protos.governance.NewMarketConfiguration(
            instrument=vega_protos.governance.InstrumentConfiguration(
                name=market_name,
                code=market_name,
                future=vega_protos.governance.FutureProduct(
                    settlement_asset=settlement_asset_id,
                    quote_name=future_asset,
                    oracle_spec_for_settlement_price=oracle_spec_for_settlement_price,
                    oracle_spec_for_trading_termination=oracle_spec_for_trading_termination,
                    oracle_spec_binding=vega_protos.markets.OracleSpecToFutureBinding(
                        settlement_price_property=f"price.{future_asset}.value",
                        trading_termination_property="trading.terminated",
                    ),
                ),
            ),
            decimal_places=5 if market_decimals is None else market_decimals,
            position_decimal_places=0
            if position_decimals is None
            else position_decimals,
            metadata=[
                f"base:{future_asset}",
                f"quote:{settlement_asset}",
            ],
            liquidity_monitoring_parameters=vega_protos.markets.LiquidityMonitoringParameters(
                target_stake_parameters=vega_protos.markets.TargetStakeParameters(
                    time_window=3600, scaling_factor=100
                ),
                triggering_ratio=0.7,
                auction_extension=0,
            ),
            log_normal=vega_protos.markets.LogNormalRiskModel(
                risk_aversion_parameter=0.01,
                tau=1.90128526884173e-06,
                params=vega_protos.markets.LogNormalModelParams(
                    mu=0, r=0.016, sigma=1.5
                ),
            ),
        ),
        liquidity_commitment=liquidity_commitment,
    )
    proposal = commands_protos.commands.ProposalSubmission(
        reference=proposal_ref,
        terms=vega_protos.governance.ProposalTerms(
            closing_timestamp=closing_time,
            enactment_timestamp=enactment_time,
            validation_timestamp=validation_time,
            new_market=market_proposal,
        ),
    )

    submission = {
        "proposalSubmission": MessageToDict(proposal),
        "pubKey": pub_key,
        "propagate": True,
    }
    # Sign the new market proposal transaction
    url = f"{wallet_server_url}/api/v1/command/sync"
    response = requests.post(url, headers=headers, json=submission)
    logger.debug("Signed market proposal and sent to Vega")

    response.raise_for_status()

    # Wait for proposal to be included in a block and to be accepted by Vega network

    def _proposal_loader(order_ref: str) -> bool:
        request = data_node_protos.trading_data.GetProposalByReferenceRequest(
            reference=order_ref
        )
        return bool(data_client.GetProposalByReference(request).data)

    # Wait for proposal to be included in a block and to be accepted by Vega network
    logger.debug("Waiting for proposal acceptance")
    wait_for_acceptance(proposal_ref, _proposal_loader)

    return proposal_ref


def accept_market_proposal(
    login_token: str,
    proposal_id: str,
    pub_key: str,
    wallet_server_url: str,
) -> None:
    headers = {"Authorization": f"Bearer {login_token}"}

    # Vote on the market
    # Create a vote message, to vote on the proposal
    vote = {
        "voteSubmission": {
            "value": "VALUE_YES",
            "proposalId": proposal_id,
        },
        "pubKey": pub_key,
        "propagate": True,
    }

    # Sign the vote transaction
    url = f"{wallet_server_url}/api/v1/command/sync"
    response = requests.post(url, headers=headers, json=vote)
    response.raise_for_status()
    logger.debug("Signed vote on proposal and sent to Vega")

    logger.debug("The market has been set up.")
