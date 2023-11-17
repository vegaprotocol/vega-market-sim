import json
import logging
import datetime
from typing import Callable, Optional, Union, Dict

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
import vega_sim.builders as builders

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


def get_blockchain_time(
    data_client: vac.VegaTradingDataClientV2, in_seconds: bool = False
) -> int:
    """Returns blockchain time in nanoseconds or seconds since the epoch

    Args:
        in_seconds: bool, if true, return time in seconds rather than nanoseconds"""
    blockchain_time = data_client.GetVegaTime(
        data_node_protos_v2.trading_data.GetVegaTimeRequest()
    ).timestamp
    return blockchain_time if not in_seconds else int(blockchain_time / 1e9)


def propose_market_from_config(
    data_client: vac.VegaTradingDataClientV2,
    wallet: Wallet,
    proposal_key_name: str,
    market_config: MarketConfig,
    closing_time: Union[str, int],
    enactment_time: Union[str, int],
    time_forward_fn: Optional[Callable[[], None]] = None,
    governance_asset: Optional[str] = "VOTE",
    proposal_wallet_name: Optional[str] = None,
) -> str:
    # Make sure Vega network has governance asset
    vote_asset_id = find_asset_id(
        governance_asset, raise_on_missing=True, data_client=data_client
    )
    pub_key = wallet.public_key(
        wallet_name=proposal_wallet_name, name=proposal_key_name
    )

    # Request accounts for party and check governance asset balance
    party_accounts = data_raw.list_accounts(
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
        closing_time=int(closing_time),
        enactment_time=int(enactment_time),
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


def __propose_market(
    key_name: str,
    wallet: Wallet,
    instrument: vega_protos.governance.InstrumentConfiguration,
    data_client: vac.VegaTradingDataClientV2,
    governance_asset: str = "VOTE",
    future_asset: str = "BTC",
    position_decimals: Optional[int] = None,
    price_decimals: Optional[int] = None,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    risk_model: Optional[vega_protos.markets.LogNormalRiskModel] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
    price_monitoring_parameters: Optional[
        vega_protos.markets.PriceMonitoringParameters
    ] = None,
    lp_price_range: float = 1,
    commitment_min_time_fraction: float = 0.95,
    performance_hysteresis_epochs: int = 1,
    sla_competition_factor: float = 1,
    wallet_name: Optional[str] = None,
    parent_market_id: Optional[str] = None,
    parent_market_insurance_pool_fraction: float = 1,
) -> str:
    # Make sure Vega network has governance asset
    vote_asset_id = find_asset_id(
        governance_asset, raise_on_missing=True, data_client=data_client
    )
    pub_key = wallet.public_key(wallet_name=wallet_name, name=key_name)

    # Request accounts for party and check governance asset balance
    party_accounts = data_raw.list_accounts(
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

    market_proposal = vega_protos.governance.NewMarket(
        changes=vega_protos.governance.NewMarketConfiguration(
            instrument=instrument,
            decimal_places=price_decimals,
            position_decimal_places=(
                0 if position_decimals is None else position_decimals
            ),
            metadata=[
                f"base:{future_asset}",
            ],
            liquidity_monitoring_parameters=vega_protos.markets.LiquidityMonitoringParameters(
                target_stake_parameters=vega_protos.markets.TargetStakeParameters(
                    time_window=3600, scaling_factor=1
                ),
                triggering_ratio="0.7",
                auction_extension=0,
            ),
            price_monitoring_parameters=price_monitoring_parameters,
            log_normal=risk_model,
            linear_slippage_factor="0.001",
            quadratic_slippage_factor="0",
            liquidity_sla_parameters=vega_protos.markets.LiquiditySLAParameters(
                price_range=str(lp_price_range),
                commitment_min_time_fraction=str(commitment_min_time_fraction),
                performance_hysteresis_epochs=int(performance_hysteresis_epochs),
                sla_competition_factor=str(sla_competition_factor),
            ),
            liquidation_strategy=vega_protos.markets.LiquidationStrategy(
                disposal_time_step=1,
                disposal_fraction="1",
                full_disposal_size=1000000000,
                max_fraction_consumed="0.5",
            ),
        ),
    )
    if parent_market_id is not None:
        market_proposal.changes.successor.CopyFrom(
            vega_protos.governance.SuccessorConfiguration(
                parent_market_id=parent_market_id,
                insurance_pool_fraction=str(parent_market_insurance_pool_fraction),
            )
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


def propose_future_market(
    market_name: str,
    key_name: str,
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
    lp_price_range: float = 1,
    commitment_min_time_fraction: float = 0.95,
    performance_hysteresis_epochs: int = 1,
    sla_competition_factor: float = 1,
    wallet_name: Optional[str] = None,
    parent_market_id: Optional[str] = None,
    parent_market_insurance_pool_fraction: float = 1,
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
        lp_price_range:
            float, Range allowed for LP price commitments from mid price to count for SLA
            (e.g. 2 allows mid-price +/- 2 * mid-price )
        commitment_min_time_fraction:
            float, default 0.95, Specifies the minimum fraction of time LPs must spend
                "on the book" providing their committed liquidity.
        performance_hysteresis_epochs:
            int, default 1, Specifies the number of liquidity epochs over which past performance
                will continue to affect rewards.
        sla_competition_factor:
            float, default 1, Specifies the maximum fraction of their accrued fees an
                LP that meets the SLA implied by market.liquidity.commitmentMinTimeFraction
                will lose to liquidity providers that achieved a higher SLA performance than them.
        key_name:
            Optional[str], key name stored in metadata. Defaults to None.
        parent_market_id:
            Optional[str], Market to set as the parent market on the proposal
        parent_market_insurance_pool_fraction:
            float, Fraction of parent market insurance pool to carry over.
                defaults to 1. No-op if parent_market_id is not set.

    Returns:
        str, the ID of the future market proposal on chain
    """
    price_decimals = 5 if market_decimals is None else market_decimals
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
                            number_decimal_places=price_decimals,
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
    instrument = vega_protos.governance.InstrumentConfiguration(
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
        ),
    )
    return __propose_market(
        key_name=key_name,
        wallet=wallet,
        instrument=instrument,
        data_client=data_client,
        governance_asset=governance_asset,
        future_asset=future_asset,
        position_decimals=position_decimals,
        price_decimals=price_decimals,
        closing_time=closing_time,
        enactment_time=enactment_time,
        risk_model=risk_model,
        time_forward_fn=time_forward_fn,
        price_monitoring_parameters=price_monitoring_parameters,
        lp_price_range=lp_price_range,
        commitment_min_time_fraction=commitment_min_time_fraction,
        performance_hysteresis_epochs=performance_hysteresis_epochs,
        sla_competition_factor=sla_competition_factor,
        wallet_name=wallet_name,
        parent_market_id=parent_market_id,
        parent_market_insurance_pool_fraction=parent_market_insurance_pool_fraction,
    )


def propose_perps_market(
    market_name: str,
    key_name: str,
    wallet: Wallet,
    settlement_asset_id: str,
    data_client: vac.VegaTradingDataClientV2,
    settlement_data_pub_key: str,
    governance_asset: str = "VOTE",
    perp_asset: str = "BTC",
    position_decimals: Optional[int] = None,
    market_decimals: Optional[int] = None,
    margin_funding_factor: Optional[float] = None,
    interest_rate: Optional[float] = None,
    clamp_lower_bound: Optional[float] = None,
    clamp_upper_bound: Optional[float] = None,
    funding_payment_frequency_in_seconds: Optional[int] = None,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    risk_model: Optional[vega_protos.markets.LogNormalRiskModel] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
    price_monitoring_parameters: Optional[
        vega_protos.markets.PriceMonitoringParameters
    ] = None,
    lp_price_range: float = 1,
    commitment_min_time_fraction: float = 0.95,
    performance_hysteresis_epochs: int = 1,
    sla_competition_factor: float = 1,
    wallet_name: Optional[str] = None,
    parent_market_id: Optional[str] = None,
    parent_market_insurance_pool_fraction: float = 1,
) -> str:
    """Propose a perps market as specified user.

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
        perp_asset:
            str, the symbol of the perp asset used
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
        lp_price_range:
            float, Range allowed for LP price commitments from mid price to count for SLA
            (e.g. 2 allows mid-price +/- 2 * mid-price )
        commitment_min_time_fraction:
            float, default 0.95, Specifies the minimum fraction of time LPs must spend
                "on the book" providing their committed liquidity.
        performance_hysteresis_epochs:
            int, default 1, Specifies the number of liquidity epochs over which past performance
                will continue to affect rewards.
        sla_competition_factor:
            float, default 1, Specifies the maximum fraction of their accrued fees an
                LP that meets the SLA implied by market.liquidity.commitmentMinTimeFraction
                will lose to liquidity providers that achieved a higher SLA performance than them.
        key_name:
            Optional[str], key name stored in metadata. Defaults to None.
        parent_market_id:
            Optional[str], Market to set as the parent market on the proposal
        parent_market_insurance_pool_fraction:
            float, Fraction of parent market insurance pool to carry over.
                defaults to 1. No-op if parent_market_id is not set.

    Returns:
        str, the ID of the future market proposal on chain
    """
    price_decimals = 5 if market_decimals is None else market_decimals
    data_source_spec_for_settlement_data = data_source_protos.DataSourceDefinition(
        external=data_source_protos.DataSourceDefinitionExternal(
            oracle=data_source_protos.DataSourceSpecConfiguration(
                signers=[
                    oracles_protos.data.Signer(
                        pub_key=oracles_protos.data.PubKey(key=settlement_data_pub_key)
                    )
                ],
                filters=[
                    oracles_protos.spec.Filter(
                        key=oracles_protos.spec.PropertyKey(
                            name=f"price.{perp_asset}.value",
                            type=oracles_protos.spec.PropertyKey.Type.TYPE_INTEGER,
                            number_decimal_places=price_decimals,
                        ),
                        conditions=[],
                    )
                ],
            )
        )
    )
    data_source_spec_for_settlement_schedule = data_source_protos.DataSourceDefinition(
        internal=data_source_protos.DataSourceDefinitionInternal(
            time_trigger=data_source_protos.DataSourceSpecConfigurationTimeTrigger(
                conditions=[
                    oracles_protos.spec.Condition(
                        operator="OPERATOR_GREATER_THAN_OR_EQUAL", value="0"
                    )
                ],
                triggers=[
                    oracles_protos.spec.InternalTimeTrigger(
                        every=(
                            60
                            if funding_payment_frequency_in_seconds is None
                            else funding_payment_frequency_in_seconds
                        )
                    )
                ],
            )
        )
    )
    instrument = vega_protos.governance.InstrumentConfiguration(
        name=market_name,
        code=market_name,
        perpetual=vega_protos.governance.PerpetualProduct(
            settlement_asset=settlement_asset_id,
            quote_name=perp_asset,
            margin_funding_factor=(
                "0" if margin_funding_factor is None else str(margin_funding_factor)
            ),
            interest_rate="0" if interest_rate is None else str(interest_rate),
            clamp_lower_bound=(
                "0" if clamp_lower_bound is None else str(clamp_lower_bound)
            ),
            clamp_upper_bound=(
                "0" if clamp_upper_bound is None else str(clamp_upper_bound)
            ),
            data_source_spec_for_settlement_schedule=data_source_spec_for_settlement_schedule,
            data_source_spec_for_settlement_data=data_source_spec_for_settlement_data,
            data_source_spec_binding=vega_protos.markets.DataSourceSpecToPerpetualBinding(
                settlement_data_property=f"price.{perp_asset}.value",
                settlement_schedule_property="vegaprotocol.builtin.timetrigger",
            ),
        ),
    )
    return __propose_market(
        key_name=key_name,
        wallet=wallet,
        instrument=instrument,
        data_client=data_client,
        governance_asset=governance_asset,
        future_asset=perp_asset,
        position_decimals=position_decimals,
        price_decimals=price_decimals,
        closing_time=closing_time,
        enactment_time=enactment_time,
        risk_model=risk_model,
        time_forward_fn=time_forward_fn,
        price_monitoring_parameters=price_monitoring_parameters,
        lp_price_range=lp_price_range,
        commitment_min_time_fraction=commitment_min_time_fraction,
        performance_hysteresis_epochs=performance_hysteresis_epochs,
        sla_competition_factor=sla_competition_factor,
        wallet_name=wallet_name,
        parent_market_id=parent_market_id,
        parent_market_insurance_pool_fraction=parent_market_insurance_pool_fraction,
    )


def propose_network_parameter_change(
    parameter: str,
    value: str,
    key_name: str,
    wallet: Wallet,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    data_client: Optional[vac.VegaTradingDataClientV2] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
    wallet_name: Optional[str] = None,
):
    network_param_update = _build_generic_proposal(
        pub_key=wallet.public_key(wallet_name=wallet_name, name=key_name),
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
    key_name: str,
    wallet: Wallet,
    market_update: vega_protos.governance.UpdateMarketConfiguration,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    data_client: Optional[vac.VegaTradingDataClientV2] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
    wallet_name: Optional[str] = None,
) -> str:
    network_param_update = _build_generic_proposal(
        pub_key=wallet.public_key(wallet_name=wallet_name, name=key_name),
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
    )
    network_param_update.terms.update_market.CopyFrom(
        vega_protos.governance.UpdateMarket(market_id=market_id, changes=market_update)
    )

    return _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        key_name=key_name,
        wallet=wallet,
        proposal=network_param_update,
        data_client=data_client,
        time_forward_fn=time_forward_fn,
    ).proposal.id


def propose_market_state_update(
    market_id: str,
    key_name: str,
    wallet: Wallet,
    market_state: vega_protos.governance.MarketStateUpdateType,
    price: Optional[str] = None,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    data_client: Optional[vac.VegaTradingDataClientV2] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
    wallet_name: Optional[str] = None,
) -> str:
    market_state_update = _build_generic_proposal(
        pub_key=wallet.public_key(wallet_name=wallet_name, name=key_name),
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
    )
    market_state_update.terms.update_market_state.CopyFrom(
        vega_protos.governance.UpdateMarketState(
            changes=vega_protos.governance.UpdateMarketStateConfiguration(
                market_id=market_id, price=price, update_type=market_state
            )
        )
    )

    return _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        key_name=key_name,
        wallet=wallet,
        proposal=market_state_update,
        data_client=data_client,
        time_forward_fn=time_forward_fn,
    ).proposal.id


def approve_proposal(
    key_name: str,
    proposal_id: str,
    wallet: Wallet,
    wallet_name: Optional[str] = None,
):
    wallet.submit_transaction(
        transaction=builders.governance.vote_submission(
            value=vega_protos.governance.Vote.Value.VALUE_YES, proposal_id=proposal_id
        ),
        wallet_name=wallet_name,
        transaction_type="vote_submission",
        key_name=key_name,
    )


def propose_asset(
    key_name: str,
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
    wallet_name: Optional[str] = None,
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
        pub_key=wallet.public_key(wallet_name=wallet_name, name=key_name),
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
    )
    proposal.terms.validation_timestamp = (
        validation_time
        if validation_time is not None
        else get_blockchain_time(data_client, in_seconds=True) + 10
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

        blockchain_time_seconds = get_blockchain_time(data_client, in_seconds=True)

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
    key_name: str,
    wallet: Wallet,
    proposal: commands_protos.commands.ProposalSubmission,
    data_client: vac.VegaTradingDataClientV2,
    time_forward_fn: Optional[Callable[[], None]] = None,
    wallet_name: Optional[str] = None,
) -> ProposalSubmission:
    wallet.submit_transaction(
        transaction=proposal,
        wallet_name=wallet_name,
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


def submit_oracle_data(
    key_name: str,
    payload: dict[str, str],
    wallet: Wallet,
    wallet_name: Optional[str] = None,
):
    """
    Submit oracle data

    Args:
        key_name:
            str, key name stored in metadata.
        payload:
            dict[str, str], payload to be encoded as JSON and submitted to the network
        wallet:
            str, the public key for the wallet authorised to send oracle signals
        wallet_name:
            str, the login token for the wallet authorised to send oracle signals
    """
    endcoded_payload = json.dumps(payload).encode()

    oracle_submission = commands_protos.data.OracleDataSubmission(
        payload=endcoded_payload,
        source=commands_protos.data.OracleDataSubmission.OracleSource.ORACLE_SOURCE_JSON,
    )

    wallet.submit_transaction(
        transaction=oracle_submission,
        wallet_name=wallet_name,
        transaction_type="oracle_data_submission",
        key_name=key_name,
    )


def submit_termination_and_settlement_data(
    key_name: str,
    wallet: Wallet,
    settlement_price: float,
    oracle_name: str,
    wallet_name: Optional[str] = None,
) -> None:
    """
    Terminate the market and send settlement price.

    Args:
        wallet_name:
            str, the login token for the wallet authorised to send
             termination/settlement oracle signals
        wallet:
            str, the public key for the wallet authorised to send
             termination/settlement oracle signals
        settlement_price:
            float, final settlement price for the asset
        oracle_name:
            str, the name of the oracle to settle
        key_name:
            str, key name stored in metadata.

    """

    # use oracle feed to terminate market
    submit_oracle_data(
        key_name=key_name,
        payload={"trading.terminated": "true"},
        wallet=wallet,
        wallet_name=wallet_name,
    )

    submit_settlement_data(
        key_name=key_name,
        wallet=wallet,
        settlement_price=settlement_price,
        oracle_name=oracle_name,
        wallet_name=wallet_name,
    )


def submit_settlement_data(
    key_name: str,
    wallet: Wallet,
    settlement_price: float,
    oracle_name: str,
    wallet_name: Optional[str] = None,
    additional_payload: Optional[dict[str, str]] = None,
) -> None:
    """
    Send settlement price.

    Args:
        wallet_name:
            str, the login token for the wallet authorised to send
             termination/settlement oracle signals
        wallet:
            str, the public key for the wallet authorised to send
             termination/settlement oracle signals
        settlement_price:
            float, final settlement price for the asset
        oracle_name:
            str, the name of the oracle to settle
        key_name:
            str, key name stored in metadata.

    """

    payload = {oracle_name: str(settlement_price)}
    if additional_payload != None:
        payload.update(additional_payload)
    submit_oracle_data(
        key_name=key_name, payload=payload, wallet=wallet, wallet_name=wallet_name
    )


def update_referral_program(
    key_name: str,
    wallet: Wallet,
    data_client: vac.VegaTradingDataClientV2,
    benefit_tiers: Optional[list[dict]] = None,
    staking_tiers: Optional[list[dict]] = None,
    end_of_program_timestamp: Optional[int] = None,
    window_length: Optional[int] = None,
    wallet_name: Optional[str] = None,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
):
    referral_program = vega_protos.governance.ReferralProgramChanges(
        end_of_program_timestamp=end_of_program_timestamp,
        window_length=window_length,
    )
    if benefit_tiers is not None:
        for benefit_tier in benefit_tiers:
            referral_program.benefit_tiers.extend(
                [
                    vega_protos.vega.BenefitTier(
                        minimum_running_notional_taker_volume=str(
                            benefit_tier["minimum_running_notional_taker_volume"]
                        ),
                        minimum_epochs=str(benefit_tier["minimum_epochs"]),
                        referral_reward_factor=str(
                            benefit_tier["referral_reward_factor"]
                        ),
                        referral_discount_factor=str(
                            benefit_tier["referral_discount_factor"]
                        ),
                    )
                ]
            )
    if staking_tiers is not None:
        for staking_tier in staking_tiers:
            referral_program.staking_tiers.extend(
                [
                    vega_protos.vega.StakingTier(
                        minimum_staked_tokens=str(
                            staking_tier["minimum_staked_tokens"]
                        ),
                        referral_reward_multiplier=str(
                            staking_tier["referral_reward_multiplier"]
                        ),
                    )
                ]
            )

    proposal = _build_generic_proposal(
        pub_key=wallet.public_key(wallet_name=wallet_name, name=key_name),
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
    )
    proposal.terms.update_referral_program.CopyFrom(
        vega_protos.governance.UpdateReferralProgram(changes=referral_program)
    )
    return _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        wallet=wallet,
        proposal=proposal,
        data_client=data_client,
        time_forward_fn=time_forward_fn,
        key_name=key_name,
    ).proposal.id


def update_volume_discount_program(
    key_name: str,
    wallet: Wallet,
    data_client: vac.VegaTradingDataClientV2,
    benefit_tiers: Optional[list[dict]] = None,
    end_of_program_timestamp: Optional[int] = None,
    window_length: Optional[int] = None,
    wallet_name: Optional[str] = None,
    closing_time: Optional[int] = None,
    enactment_time: Optional[int] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
):
    volume_discount_program = vega_protos.governance.VolumeDiscountProgramChanges(
        end_of_program_timestamp=end_of_program_timestamp,
        window_length=window_length,
    )
    if benefit_tiers is not None:
        for benefit_tier in benefit_tiers:
            volume_discount_program.benefit_tiers.extend(
                [
                    vega_protos.vega.VolumeBenefitTier(
                        minimum_running_notional_taker_volume=str(
                            benefit_tier["minimum_running_notional_taker_volume"]
                        ),
                        volume_discount_factor=str(
                            benefit_tier["volume_discount_factor"]
                        ),
                    )
                ]
            )

    proposal = _build_generic_proposal(
        pub_key=wallet.public_key(wallet_name=wallet_name, name=key_name),
        data_client=data_client,
        closing_time=closing_time,
        enactment_time=enactment_time,
    )
    proposal.terms.update_volume_discount_program.CopyFrom(
        vega_protos.governance.UpdateVolumeDiscountProgram(
            changes=volume_discount_program
        )
    )
    return _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        wallet=wallet,
        proposal=proposal,
        data_client=data_client,
        time_forward_fn=time_forward_fn,
        key_name=key_name,
    ).proposal.id


def new_transfer(
    asset_decimals: Dict[str, int],
    data_client: vac.VegaTradingDataClientV2,
    key_name: str,
    wallet: Wallet,
    source_type: vega_protos.vega.AccountType,
    transfer_type: vega_protos.governance.GovernanceTransferType,
    amount: float,
    asset: str,
    fraction_of_balance: float,
    destination_type: vega_protos.vega.AccountType,
    source: Optional[str] = None,
    destination: Optional[str] = None,
    closing_time: Optional[datetime.datetime] = None,
    enactment_time: Optional[datetime.datetime] = None,
    wallet_name: Optional[str] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
):
    new_transfer = builders.governance.new_transfer(
        changes=builders.governance.new_transfer_configuration(
            asset_decimals=asset_decimals,
            source_type=source_type,
            transfer_type=transfer_type,
            amount=amount,
            asset=asset,
            fraction_of_balance=fraction_of_balance,
            destination_type=destination_type,
            source=source,
            destination=destination,
            one_off=builders.governance.one_off_transfer(deliver_on=enactment_time),
        )
    )

    proposal = _build_generic_proposal(
        pub_key=wallet.public_key(wallet_name=wallet_name, name=key_name),
        data_client=data_client,
        closing_time=int(closing_time.timestamp()),
        enactment_time=int(enactment_time.timestamp()),
    )
    proposal.terms.new_transfer.CopyFrom(new_transfer)

    return _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        wallet=wallet,
        proposal=proposal,
        data_client=data_client,
        time_forward_fn=time_forward_fn,
        key_name=key_name,
    ).proposal.id


def submit_proposal(
    key_name: str,
    wallet: Wallet,
    data_client: vac.VegaTradingDataClientV2,
    proposal: vega_protos.commands.v1.commands.ProposalSubmission,
    wallet_name: Optional[str] = None,
    time_forward_fn: Optional[Callable[[], None]] = None,
):
    proposal = _make_and_wait_for_proposal(
        wallet_name=wallet_name,
        wallet=wallet,
        proposal=proposal,
        data_client=data_client,
        time_forward_fn=time_forward_fn,
        key_name=key_name,
    )
    return proposal.proposal.id
