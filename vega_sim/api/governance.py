import json
import logging
from typing import Callable, Optional

import vega_sim.api.data_raw as data_raw
import vega_sim.grpc.client as vac
import vega_sim.proto.data_node.api.v2 as data_node_protos_v2

import vega_sim.proto.vega as vega_protos
import vega_sim.proto.vega.commands.v1 as commands_protos
import vega_sim.proto.vega.data.v1 as oracles_protos
import vega_sim.proto.vega.data_source_pb2 as data_source_protos
from vega_sim.api.data import find_asset_id
from vega_sim.api.helpers import (
    ProposalNotAcceptedError,
    enum_to_str,
    generate_id,
    wait_for_acceptance,
)
from vega_sim.api.market import MarketConfig
from vega_sim.proto.vega.commands.v1.commands_pb2 import ProposalSubmission
from vega_sim.wallet.base import Wallet

logger = logging.getLogger(__name__)

ASSET_URL_BASE = "{node_url}/assets"


class LowBalanceError(Exception):
    pass


def _proposal_loader(
    proposal_ref: str,
    data_client: vac.VegaTradingDataClientV2,
) -> bool:
    request = data_node_protos_v2.trading_data.GetGovernanceDataRequest(
        reference=proposal_ref,
    )
    response = data_client.GetGovernanceData(request)
    return response.data


def _default_risk_model() -> vega_protos.markets.LogNormalRiskModel:
    return vega_protos.markets.LogNormalRiskModel(
        risk_aversion_parameter=0.01,
        tau=1.90128526884173e-06,
        params=vega_protos.markets.LogNormalModelParams(mu=0, r=0.016, sigma=3.0),
    )


def _default_price_monitoring_parameters() -> (
    vega_protos.markets.PriceMonitoringParameters
):
    return vega_protos.markets.PriceMonitoringParameters(
        triggers=[
            vega_protos.markets.PriceMonitoringTrigger(
                # in seconds, so 24h, the longer the wider bounds
                horizon=24 * 3600,
                # number close to but below 1 leads to wide bounds
                probability="0.999999",
                # in seconds
                auction_extension=5,
            )
        ]
    )


def get_blockchain_time(data_client: vac.VegaTradingDataClientV2) -> int:
    """Returns blockchain time in seconds since the epoch"""
    blockchain_time = data_client.GetVegaTime(
        data_node_protos_v2.trading_data.GetVegaTimeRequest()
    ).timestamp
    return int(blockchain_time / 1e9)


def propose_market_from_config(
    data_client: vac.VegaTradingDataClientV2,
    wallet: Wallet,
    proposal_wallet_name: str,
    market_config: MarketConfig,
    closing_time: str,
    enactment_time: str,
    time_forward_fn: Optional[Callable[[], None]] = None,
    governance_asset: Optional[str] = "VOTE",
    proposal_key_name: Optional[str] = None,
) -> str:
    # Make sure Vega network has governance asset
    vote_asset_id = find_asset_id(
        governance_asset, raise_on_missing=True, data_client=data_client
    )
    pub_key = wallet.public_key(proposal_wallet_name, proposal_key_name)

    # Request accounts for party and check governance asset balance
    party_accounts = data_raw.party_accounts(
        data_client=data_client, asset_id=vote_asset_id, party_id=pub_key
    )

    voting_balance = 0
    for account in party_accounts:
        if account.asset == vote_asset_id:
            voting_balance = account.balance
            break

    if voting_balance == 0:
        raise LowBalanceError(
            f"Public key {pub_key} is missing governance token {governance_asset}"
        )

    # Build NewMarketConfiguration proto
    changes = market_config.build()

    # Build ProposalTerms proto
    proposal = _build_generic_proposal(
        pub_key=pub_key,
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
    )
    proposal.terms.new_market.CopyFrom(changes)

    return _make_and_wait_for_proposal(
        wallet=wallet,
        wallet_name=proposal_wallet_name,
        key_name=proposal_key_name,
        proposal=proposal,
        data_client=data_client,
        time_forward_fn=time_forward_fn,
    ).proposal.id


def propose_future_market(
    market_name: str,
    wallet_name: str,
    wallet: Wallet,
    settlement_asset_id: str,
    data_client: vac.VegaTradingDataClientV2,
    termination_pub_key: str,
    governance_asset: str = "VOTE",
    future_asset: str = "BTC",
    position_decimals: Optional[int] = None,
    market_decimals: Optional[int] = None,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    risk_model: Optional[vega_protos.markets.LogNormalRiskModel] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
    price_monitoring_parameters: Optional[
        vega_protos.markets.PriceMonitoringParameters
    ] = None,
    key_name: Optional[str] = None,
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
            VegaTradingDataClientV2, an instantiated gRPC client for interacting with the
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
        risk_model:
            LogNormalRiskModel, A parametrised risk model on which the market will run
        price_monitoring_parameters:
            PriceMonitoringParameters, A set of parameters determining when the market
                will drop into a price auction. If not passed defaults to a very
                permissive setup
        key_name:
            Optional[str], key name stored in metadata. Defaults to None.

    Returns:
        str, the ID of the future market proposal on chain
    """
    # Make sure Vega network has governance asset
    vote_asset_id = find_asset_id(
        governance_asset, raise_on_missing=True, data_client=data_client
    )
    pub_key = wallet.public_key(wallet_name, key_name)

    # Request accounts for party and check governance asset balance
    party_accounts = data_raw.party_accounts(
        data_client=data_client, asset_id=vote_asset_id, party_id=pub_key
    )

    voting_balance = 0
    for account in party_accounts:
        if account.asset == vote_asset_id:
            voting_balance = account.balance
            break

    if voting_balance == 0:
        raise LowBalanceError(
            f"Public key {pub_key} is missing governance token {governance_asset}"
        )

    risk_model = risk_model if risk_model is not None else _default_risk_model()
    price_monitoring_parameters = (
        price_monitoring_parameters
        if price_monitoring_parameters is not None
        else _default_price_monitoring_parameters()
    )

    data_source_spec_for_settlement_data = data_source_protos.DataSourceDefinition(
        external=data_source_protos.DataSourceDefinitionExternal(
            oracle=data_source_protos.DataSourceSpecConfiguration(
                signers=[
                    oracles_protos.data.Signer(
                        pub_key=oracles_protos.data.PubKey(key=termination_pub_key)
                    )
                ],
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
        )
    )
    data_source_spec_for_trading_termination = data_source_protos.DataSourceDefinition(
        external=data_source_protos.DataSourceDefinitionExternal(
            oracle=data_source_protos.DataSourceSpecConfiguration(
                signers=[
                    oracles_protos.data.Signer(
                        pub_key=oracles_protos.data.PubKey(key=termination_pub_key)
                    )
                ],
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
        )
    )

    price_decimals = 5 if market_decimals is None else market_decimals
    market_proposal = vega_protos.governance.NewMarket(
        changes=vega_protos.governance.NewMarketConfiguration(
            instrument=vega_protos.governance.InstrumentConfiguration(
                name=market_name,
                code=market_name,
                future=vega_protos.governance.FutureProduct(
                    settlement_asset=settlement_asset_id,
                    quote_name=future_asset,
                    data_source_spec_for_settlement_data=data_source_spec_for_settlement_data,
                    data_source_spec_for_trading_termination=data_source_spec_for_trading_termination,
                    data_source_spec_binding=vega_protos.markets.DataSourceSpecToFutureBinding(
                        settlement_data_property=f"price.{future_asset}.value",
                        trading_termination_property="trading.terminated",
                    ),
                    settlement_data_decimals=price_decimals,
                ),
            ),
            decimal_places=price_decimals,
            position_decimal_places=0
            if position_decimals is None
            else position_decimals,
            metadata=[
                f"base:{future_asset}",
            ],
            liquidity_monitoring_parameters=vega_protos.markets.LiquidityMonitoringParameters(
                target_stake_parameters=vega_protos.markets.TargetStakeParameters(
                    time_window=3600, scaling_factor=1
                ),
                triggering_ratio=0.7,
                auction_extension=0,
            ),
            price_monitoring_parameters=price_monitoring_parameters,
            log_normal=risk_model,
        ),
    )

    proposal = _build_generic_proposal(
        pub_key=pub_key,
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
    )
    proposal.terms.new_market.CopyFrom(market_proposal)

    return _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        wallet=wallet,
        proposal=proposal,
        data_client=data_client,
        time_forward_fn=time_forward_fn,
        key_name=key_name,
    ).proposal.id


def propose_network_parameter_change(
    parameter: str,
    value: str,
    wallet_name: str,
    wallet: Wallet,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    data_client: Optional[vac.VegaTradingDataClientV2] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
    key_name: Optional[str] = None,
):
    network_param_update = _build_generic_proposal(
        pub_key=wallet.public_key(wallet_name, key_name),
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
    )
    network_param_update.terms.update_network_parameter.CopyFrom(
        vega_protos.governance.UpdateNetworkParameter(
            changes=vega_protos.vega.NetworkParameter(key=parameter, value=value)
        )
    )
    return _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        wallet=wallet,
        proposal=network_param_update,
        data_client=data_client,
        time_forward_fn=time_forward_fn,
        key_name=key_name,
    ).proposal.id


def propose_market_update(
    market_id: str,
    wallet_name: str,
    wallet: Wallet,
    market_update: vega_protos.governance.UpdateMarketConfiguration,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    data_client: Optional[vac.VegaTradingDataClientV2] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
    key_name: Optional[str] = None,
) -> str:
    network_param_update = _build_generic_proposal(
        pub_key=wallet.public_key(wallet_name, key_name),
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
    )
    network_param_update.terms.update_market.CopyFrom(
        vega_protos.governance.UpdateMarket(market_id=market_id, changes=market_update)
    )

    return _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        wallet=wallet,
        proposal=network_param_update,
        data_client=data_client,
        time_forward_fn=time_forward_fn,
    ).proposal.id


def approve_proposal(
    wallet_name: str,
    proposal_id: str,
    wallet: Wallet,
    key_name: Optional[str] = None,
):
    wallet.submit_transaction(
        transaction=commands_protos.commands.VoteSubmission(
            value=vega_protos.governance.Vote.Value.VALUE_YES, proposal_id=proposal_id
        ),
        name=wallet_name,
        transaction_type="vote_submission",
        key_name=key_name,
    )


def propose_asset(
    wallet_name: str,
    wallet: Wallet,
    name: str,
    symbol: str,
    decimals: int,
    data_client: vac.VegaTradingDataClientV2,
    quantum: int = 1,
    max_faucet_amount: int = 10e9,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    validation_time: Optional[int] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
    key_name: Optional[str] = None,
) -> str:
    asset_detail = vega_protos.assets.AssetDetails(
        name=name,
        symbol=symbol,
        decimals=decimals,
        quantum=str(int(quantum)),
        builtin_asset=vega_protos.assets.BuiltinAsset(
            max_faucet_amount_mint=str(int(max_faucet_amount))
        ),
    )
    proposal = _build_generic_proposal(
        pub_key=wallet.public_key(wallet_name, key_name),
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
    )
    proposal.terms.validation_timestamp = (
        validation_time
        if validation_time is not None
        else get_blockchain_time(data_client) + 10
    )

    proposal.terms.new_asset.CopyFrom(
        vega_protos.governance.NewAsset(changes=asset_detail)
    )
    return _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        wallet=wallet,
        proposal=proposal,
        data_client=data_client,
        time_forward_fn=time_forward_fn,
        key_name=key_name,
    ).proposal.id


def _build_generic_proposal(
    pub_key: str,
    data_client: vac.VegaTradingDataClientV2,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
) -> commands_protos.commands.ProposalSubmission:
    # Set closing/enactment timestamps to valid time offsets
    # from the current Vega blockchain time if not already set
    none_times = [i is None for i in [closing_time, enactment_time]]
    if any(none_times):
        if not all(none_times):
            logger.warn(
                "Some times for proposal were not set. Defaulting all of them and"
                " ignoring values for those which were"
            )

        blockchain_time_seconds = get_blockchain_time(data_client)

        closing_time = blockchain_time_seconds + 172800
        enactment_time = blockchain_time_seconds + 172900

    # Propose market
    proposal_ref = f"{pub_key}-{generate_id(6)}"

    return commands_protos.commands.ProposalSubmission(
        reference=proposal_ref,
        terms=vega_protos.governance.ProposalTerms(
            closing_timestamp=closing_time,
            enactment_timestamp=enactment_time,
        ),
        rationale=vega_protos.governance.ProposalRationale(
            description="Making a proposal", title="This is a proposal"
        ),
    )


def _make_and_wait_for_proposal(
    wallet_name: str,
    wallet: Wallet,
    proposal: commands_protos.commands.ProposalSubmission,
    data_client: vac.VegaTradingDataClientV2,
    time_forward_fn: Optional[Callable[[], None]] = None,
    key_name: Optional[str] = None,
) -> ProposalSubmission:
    wallet.submit_transaction(
        transaction=proposal,
        name=wallet_name,
        transaction_type="proposal_submission",
        key_name=key_name,
    )
    logger.debug("Waiting for proposal acceptance")

    # Allow one failure, forward once more
    try:
        time_forward_fn()
        proposal = wait_for_acceptance(
            proposal.reference,
            lambda p: _proposal_loader(p, data_client),
        )
    except ProposalNotAcceptedError:
        time_forward_fn()
        proposal = wait_for_acceptance(
            proposal.reference,
            lambda p: _proposal_loader(p, data_client),
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
    return proposal


def settle_oracle(
    wallet_name: str,
    wallet: Wallet,
    settlement_price: float,
    oracle_name: str,
    key_name: Optional[str] = None,
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
        key_name:
            Optional[str], key name stored in metadata. Defaults to None.

    """

    # Use oracle feed to terminate market
    payload = {"trading.terminated": "true"}
    payload = json.dumps(payload).encode()

    oracle_submission = commands_protos.data.OracleDataSubmission(
        payload=payload,
        source=commands_protos.data.OracleDataSubmission.OracleSource.ORACLE_SOURCE_JSON,
    )

    wallet.submit_transaction(
        transaction=oracle_submission,
        name=wallet_name,
        transaction_type="oracle_data_submission",
        key_name=key_name,
    )

    # use oracle to settle market
    payload = {oracle_name: str(settlement_price)}
    payload = json.dumps(payload).encode()

    oracle_submission = commands_protos.data.OracleDataSubmission(
        payload=payload,
        source=commands_protos.data.OracleDataSubmission.OracleSource.ORACLE_SOURCE_JSON,
    )

    wallet.submit_transaction(
        transaction=oracle_submission,
        name=wallet_name,
        transaction_type="oracle_data_submission",
        key_name=key_name,
    )
