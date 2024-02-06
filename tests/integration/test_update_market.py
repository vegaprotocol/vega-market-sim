import pytest

from tests.integration.utils.fixtures import (
    vega_service_with_market,
    vega_service,
    create_and_faucet_wallet,
    WalletConfig,
    MM_WALLET,
)
from vega_sim.null_service import VegaServiceNull
from vega_sim.service import MarketStateUpdateType
import vega_sim.proto.vega as vega_protos
import vega_sim.proto.vega.data.v1 as oracles_protos
import vega_sim.proto.vega.data_source_pb2 as data_source_protos


LIQ = WalletConfig("liq", "liq")


@pytest.mark.integration
def test_update_market_liquidity_monitoring(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    market_id = vega.all_markets()[0].id

    vega.wait_for_total_catchup()

    create_and_faucet_wallet(vega=vega, wallet=LIQ)

    pre_market = vega.market_info(market_id)

    vega.update_market(
        MM_WALLET.name,
        market_id=market_id,
        updated_liquidity_monitoring_parameters=vega_protos.markets.LiquidityMonitoringParameters(
            target_stake_parameters=vega_protos.markets.TargetStakeParameters(
                time_window=100, scaling_factor=10
            ),
        ),
    )
    vega.wait_for_total_catchup()
    after_market = vega.market_info(market_id)

    assert (
        pre_market.liquidity_monitoring_parameters.target_stake_parameters.time_window
        == 3600
    )
    assert (
        after_market.liquidity_monitoring_parameters.target_stake_parameters.time_window
        == 100
    )

    assert (
        pre_market.liquidity_monitoring_parameters.target_stake_parameters.scaling_factor
        == 1
    )
    assert (
        after_market.liquidity_monitoring_parameters.target_stake_parameters.scaling_factor
        == 10
    )


@pytest.mark.integration
def test_update_market_price_monitoring(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    market_id = vega.all_markets()[0].id

    vega.wait_for_total_catchup()

    create_and_faucet_wallet(vega=vega, wallet=LIQ)

    pre_market = vega.market_info(market_id)

    vega.update_market(
        MM_WALLET.name,
        market_id=market_id,
        updated_price_monitoring_parameters=vega_protos.markets.PriceMonitoringParameters(
            triggers=[
                vega_protos.markets.PriceMonitoringTrigger(
                    # in seconds, so 24h, the longer the wider bounds
                    horizon=600,
                    # # number close to but below 1 leads to wide bounds
                    probability="0.91",
                    # # in seconds
                    auction_extension=5,
                )
            ]
        ),
    )
    vega.wait_for_total_catchup()
    after_market = vega.market_info(market_id)

    assert pre_market.price_monitoring_settings.parameters.triggers[0].horizon == 86400
    assert after_market.price_monitoring_settings.parameters.triggers[0].horizon == 600


@pytest.mark.integration
def test_update_market_instrument(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    market_id = vega.all_markets()[0].id

    vega.wait_for_total_catchup()

    create_and_faucet_wallet(vega=vega, wallet=LIQ)

    pre_market = vega.market_info(market_id)
    curr_inst = pre_market.tradable_instrument.instrument
    curr_fut = curr_inst.future

    oracle_spec_for_settlement_data = data_source_protos.DataSourceDefinition(
        external=data_source_protos.DataSourceDefinitionExternal(
            oracle=data_source_protos.DataSourceSpecConfiguration(
                signers=curr_fut.data_source_spec_for_settlement_data.data.external.oracle.signers,
                filters=curr_fut.data_source_spec_for_settlement_data.data.external.oracle.filters,
            )
        )
    )

    oracle_spec_for_trading_termination = data_source_protos.DataSourceDefinition(
        external=data_source_protos.DataSourceDefinitionExternal(
            oracle=data_source_protos.DataSourceSpecConfiguration(
                signers=curr_fut.data_source_spec_for_trading_termination.data.external.oracle.signers,
                filters=curr_fut.data_source_spec_for_trading_termination.data.external.oracle.filters,
            )
        )
    )

    curr_fut_prod = vega_protos.governance.UpdateFutureProduct(
        quote_name=curr_fut.quote_name,
        data_source_spec_for_settlement_data=oracle_spec_for_settlement_data,
        data_source_spec_for_trading_termination=oracle_spec_for_trading_termination,
        data_source_spec_binding=curr_fut.data_source_spec_binding,
    )
    updated_instrument = vega_protos.governance.UpdateInstrumentConfiguration(
        code="BTCUSD",
        name="BTCUSD",
        future=curr_fut_prod,
    )
    vega.update_market(
        MM_WALLET.name,
        market_id=market_id,
        updated_instrument=updated_instrument,
    )
    vega.wait_for_total_catchup()
    after_market = vega.market_info(market_id)

    assert pre_market.tradable_instrument.instrument.code == "CRYPTO:BTCDAI/Jun23"
    assert after_market.tradable_instrument.instrument.code == "BTCUSD"


@pytest.mark.integration
def test_update_market_risk(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    market_id = vega.all_markets()[0].id

    vega.wait_for_total_catchup()

    create_and_faucet_wallet(vega=vega, wallet=LIQ)

    pre_market = vega.market_info(market_id)

    vega.update_market(
        MM_WALLET.name,
        market_id=market_id,
        updated_log_normal_risk_model=vega_protos.markets.LogNormalRiskModel(
            risk_aversion_parameter=0.05,
            tau=1.90128526884173e-06,
            params=vega_protos.markets.LogNormalModelParams(mu=0, r=0.016, sigma=3.0),
        ),
    )
    vega.wait_for_total_catchup()
    after_market = vega.market_info(market_id)

    assert (
        pre_market.tradable_instrument.log_normal_risk_model.risk_aversion_parameter
        == 1e-06
    )
    assert (
        after_market.tradable_instrument.log_normal_risk_model.risk_aversion_parameter
        == 0.05
    )


@pytest.mark.integration
def test_update_market_governance_changes(vega_service_with_market: VegaServiceNull):
    vega = vega_service_with_market
    market_id = vega.all_markets()[0].id

    vega.wait_for_total_catchup()

    create_and_faucet_wallet(vega=vega, wallet=LIQ)

    assert (
        vega_protos.markets.Market.State.Name(
            vega.get_latest_market_data(market_id).market_state
        )
        == "STATE_ACTIVE"
    )

    vega.update_market_state(
        market_id,
        MM_WALLET.name,
        MarketStateUpdateType.Suspend,
    )
    vega.wait_for_total_catchup()
    assert (
        vega_protos.markets.Market.State.Name(
            vega.get_latest_market_data(market_id).market_state
        )
        == "STATE_SUSPENDED_VIA_GOVERNANCE"
    )

    vega.update_market_state(
        market_id,
        MM_WALLET.name,
        MarketStateUpdateType.Resume,
    )
    vega.wait_for_total_catchup()
    assert (
        vega_protos.markets.Market.State.Name(
            vega.get_latest_market_data(market_id).market_state
        )
        == "STATE_ACTIVE"
    )

    vega.update_market_state(
        market_id,
        MM_WALLET.name,
        MarketStateUpdateType.Terminate,
        price=5.1,
    )
    vega.wait_for_total_catchup()
    assert (
        vega_protos.markets.Market.State.Name(
            vega.get_latest_market_data(market_id).market_state
        )
        == "STATE_CLOSED"
    )
    assert vega.get_latest_market_data(market_id).mark_price == 5.1
