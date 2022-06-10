import base64
import json
import logging
from typing import Optional

import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v1 as data_node_protos
import vega_sim.proto.vega as vega_protos
import vega_sim.proto.vega.oracles.v1 as oracles_protos
import vega_sim.proto.vega.commands.v1 as commands_protos
from vega_sim.api.helpers import (
    ProposalNotAcceptedError,
    generate_id,
    wait_for_acceptance,
    enum_to_str,
    forward,
)
from vega_sim.api.data import find_asset_id
from vega_sim.wallet.base import Wallet

logger = logging.getLogger(__name__)

ASSET_URL_BASE = "{node_url}/assets"


class LowBalanceError(Exception):
    pass


def _proposal_loader(
    proposal_ref: str,
    data_client: vac.VegaTradingDataClient,
) -> bool:
    request = data_node_protos.trading_data.GetProposalByReferenceRequest(
        reference=proposal_ref
    )
    return data_client.GetProposalByReference(request).data


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


def _default_risk_model() -> vega_protos.markets.LogNormalRiskModel:
    return vega_protos.markets.LogNormalRiskModel(
        risk_aversion_parameter=0.01,
        tau=1.90128526884173e-06,
        params=vega_protos.markets.LogNormalModelParams(mu=0, r=0.016, sigma=3.0),
    )


def get_blockchain_time(data_client: vac.VegaTradingDataClient) -> int:
    """Returns blockchain time in seconds since the epoch"""
    blockchain_time = data_client.GetVegaTime(
        data_node_protos.trading_data.GetVegaTimeRequest()
    ).timestamp
    return int(blockchain_time / 1e9)


def propose_future_market(
    market_name: str,
    wallet_name: str,
    wallet: Wallet,
    settlement_asset_id: str,
    data_client: vac.VegaTradingDataClient,
    termination_pub_key: str,
    governance_asset: str = "VOTE",
    future_asset: str = "BTC",
    position_decimals: Optional[int] = None,
    market_decimals: Optional[int] = None,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    validation_time: Optional[int] = None,
    liquidity_commitment: Optional[vega_protos.governance.NewMarketCommitment] = None,
    risk_model: Optional[vega_protos.markets.LogNormalRiskModel] = None,
    node_url_for_time_forwarding: Optional[str] = None,
) -> str:
    """Propose a future market as specified user.

    Args:
        market_name:
            str, name of the market
        wallet_name:
            str, the wallet name performing the action
        wallet:
            Wallet, wallet client
        login_token:
            str, the token returned from proposer wallet login
        settlement_asset_id:
            str, the asset id the market will use for settlement
        data_client:
            VegaTradingDataClient, an instantiated gRPC client for interacting with the
                Vega data node
        termination_pub_key:
            str, the public key of the oracle to be used for trading termination
        governance_asset:
            str, the governance asset on the market
        future_asset:
            str, the symbol of the future asset used
                (used for generating/linking names of oracles)
        position_decimals:
            int, the decimal place precision to use for positions
            (e.g. 2 means 2dp, so 200 => 2.00, 3 would mean 200 => 0.2)
        market_decimals:
            int, the decimal place precision to use for market prices
            (e.g. 2 means 2dp, so 200 => 2.00, 3 would mean 200 => 0.2)
    Returns:
        str, the ID of the future market proposal on chain
    """
    # Make sure Vega network has governance asset
    vote_asset_id = find_asset_id(
        governance_asset, raise_on_missing=True, data_client=data_client
    )
    pub_key = wallet.public_key(wallet_name)

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

    liquidity_commitment = (
        liquidity_commitment
        if liquidity_commitment is not None
        else _default_initial_liquidity_commitment()
    )

    risk_model = risk_model if risk_model is not None else _default_risk_model()

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
            ],
            liquidity_monitoring_parameters=vega_protos.markets.LiquidityMonitoringParameters(
                target_stake_parameters=vega_protos.markets.TargetStakeParameters(
                    time_window=3600, scaling_factor=100
                ),
                triggering_ratio=0.7,
                auction_extension=0,
            ),
            price_monitoring_parameters=vega_protos.markets.PriceMonitoringParameters(
                triggers=[
                    vega_protos.markets.PriceMonitoringTrigger(
                        horizon=2,
                        probability="0.01",
                        auction_extension=5,
                    )
                ]
            ),
            log_normal=risk_model,
        ),
        liquidity_commitment=liquidity_commitment,
    )

    proposal = _build_generic_proposal(
        pub_key=pub_key,
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
        validation_time=validation_time,
    )
    proposal.terms.new_market.CopyFrom(market_proposal)

    _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        wallet=wallet,
        proposal=proposal,
        data_client=data_client,
        node_url_for_time_forwarding=node_url_for_time_forwarding,
    )
    return proposal.reference


def propose_network_parameter_change(
    parameter: str,
    value: str,
    wallet_name: str,
    wallet: Wallet,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    validation_time: Optional[int] = None,
    data_client: Optional[vac.VegaTradingDataClient] = None,
    node_url_for_time_forwarding: Optional[str] = None,
):
    network_param_update = _build_generic_proposal(
        pub_key=wallet.public_key(wallet_name),
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
        validation_time=validation_time,
    )
    network_param_update.terms.update_network_parameter.CopyFrom(
        vega_protos.governance.UpdateNetworkParameter(
            changes=vega_protos.vega.NetworkParameter(key=parameter, value=value)
        )
    )

    _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        wallet=wallet,
        proposal=network_param_update,
        data_client=data_client,
        node_url_for_time_forwarding=node_url_for_time_forwarding,
    )
    return network_param_update.reference


def approve_proposal(
    wallet_name: str,
    proposal_id: str,
    wallet: Wallet,
):
    wallet.submit_transaction(
        transaction=commands_protos.commands.VoteSubmission(
            value=vega_protos.governance.Vote.Value.VALUE_YES, proposal_id=proposal_id
        ),
        name=wallet_name,
        transaction_type="vote_submission",
    )


def propose_asset(
    wallet_name: str,
    wallet: Wallet,
    name: str,
    symbol: str,
    total_supply: int,
    decimals: int,
    data_client: vac.VegaTradingDataClient,
    quantum: int = 1,
    max_faucet_amount: int = 10e9,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    validation_time: Optional[int] = None,
    node_url_for_time_forwarding: Optional[str] = None,
):
    asset_detail = vega_protos.assets.AssetDetails(
        name=name,
        symbol=symbol,
        total_supply=str(int(total_supply)),
        decimals=decimals,
        quantum=str(int(quantum)),
        builtin_asset=vega_protos.assets.BuiltinAsset(
            max_faucet_amount_mint=str(int(max_faucet_amount))
        ),
    )
    proposal = _build_generic_proposal(
        pub_key=wallet.public_key(wallet_name),
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
        validation_time=validation_time,
    )
    proposal.terms.new_asset.CopyFrom(
        vega_protos.governance.NewAsset(changes=asset_detail)
    )
    _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        wallet=wallet,
        proposal=proposal,
        data_client=data_client,
        node_url_for_time_forwarding=node_url_for_time_forwarding,
    )
    return proposal.reference


def _build_generic_proposal(
    pub_key: str,
    data_client: vac.VegaTradingDataClient,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    validation_time: Optional[int] = None,
) -> commands_protos.commands.ProposalSubmission:

    # Set closing/enactment and validation timestamps to valid time offsets
    # from the current Vega blockchain time if not already set
    none_times = [i is None for i in [closing_time, enactment_time, validation_time]]
    if any(none_times):
        if not all(none_times):
            logger.warn(
                "Some times for proposal were not set. Defaulting all of them and"
                " ignoring values for those which were"
            )

        blockchain_time_seconds = get_blockchain_time(data_client)

        closing_time = blockchain_time_seconds + 172800
        enactment_time = blockchain_time_seconds + 172900
        validation_time = blockchain_time_seconds + 100

    # Propose market
    proposal_ref = f"{pub_key}-{generate_id(6)}"

    # Set closing/enactment and validation timestamps to valid time offsets
    # from the current Vega blockchain time
    return commands_protos.commands.ProposalSubmission(
        reference=proposal_ref,
        terms=vega_protos.governance.ProposalTerms(
            closing_timestamp=closing_time,
            enactment_timestamp=enactment_time,
            validation_timestamp=validation_time,
        ),
        rationale=vega_protos.governance.ProposalRationale(
            description="Making a proposal"
        ),
    )


def _make_and_wait_for_proposal(
    wallet_name: str,
    wallet: Wallet,
    proposal: commands_protos.commands.ProposalSubmission,
    data_client: vac.VegaTradingDataClient,
    node_url_for_time_forwarding: Optional[str] = None,
):
    wallet.submit_transaction(
        transaction=proposal, name=wallet_name, transaction_type="proposal_submission"
    )
    logger.debug("Waiting for proposal acceptance")
    proposal = wait_for_acceptance(
        proposal.reference,
        lambda p: _proposal_loader(p, data_client),
        time_forward_fn=lambda: forward(
            time="1s", vega_node_url=node_url_for_time_forwarding
        )
        if node_url_for_time_forwarding is not None
        else None,
    )

    prop_state = enum_to_str(
        vega_protos.governance.Proposal.State, proposal.proposal.state
    )
    if prop_state in ["STATE_REJECTED", "STATE_DECLINED", "STATE_FAILED"]:
        raise ProposalNotAcceptedError(
            f"Your proposal was {prop_state} due to"
            f" {enum_to_str(vega_protos.governance.ProposalError, proposal.proposal.reason)}."
            f" Any further info: {proposal.proposal.error_details}"
        )


def settle_oracle(
    wallet_name: str,
    wallet: Wallet,
    settlement_price: float,
    oracle_name: str,
) -> None:
    """
    Settle the market and send settlement price.

    Args:
        login_token:
            str, the login token for the wallet authorised to send
             termination/settlement oracle signals
        pub_key:
            str, the public key for the wallet authorised to send
             termination/settlement oracle signals
        settlement_price:
            float, final settlement price for the asset
        oracle_name:
            str, the name of the oracle to settle

    """

    # Use oracle feed to terminate market
    payload = {"trading.terminated": "true"}
    payload = json.dumps(payload).encode()

    oracle_submission = commands_protos.oracles.OracleDataSubmission(
        payload=payload,
        source=commands_protos.oracles.OracleDataSubmission.OracleSource.ORACLE_SOURCE_JSON,
    )

    wallet.submit_transaction(
        transaction=oracle_submission,
        name=wallet_name,
        transaction_type="oracle_data_submission",
    )

    logger.info(f"Settling market at price {settlement_price} for {oracle_name}")

    # use oracle to settle market
    payload = {oracle_name: str(settlement_price)}
    payload = json.dumps(payload).encode()

    oracle_submission = commands_protos.oracles.OracleDataSubmission(
        payload=payload,
        source=commands_protos.oracles.OracleDataSubmission.OracleSource.ORACLE_SOURCE_JSON,
    )

    wallet.submit_transaction(
        transaction=oracle_submission,
        name=wallet_name,
        transaction_type="oracle_data_submission",
    )
