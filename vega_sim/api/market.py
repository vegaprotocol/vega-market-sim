"""market.py

Module contains classes to build a MarketConfig object containing market parameters
which can be passed to service methods or market manager agents to propose markets.

A MarketConfig class has the following attributes which can be set:

• decimal_places
• position_decimal_places
• meta_data
• price_monitoring_parameters.horizon
• price_monitoring_parameters.probability
• price_monitoring_parameters.auction_extension
• liquidity_monitoring_parameters.triggering_ratio
• liquidity_monitoring_parameters.auction_extension
• liquidity_monitoring_parameters.target_stake_parameters.time_window
• liquidity_monitoring_parameters.target_stake_parameters.scaling_factor
• log_normal.tau
• log_normal.risk_aversion_parameters
• log_normal.params.mu
• log_normal.params.r
• log_normal.params.sigma
• instrument.name
• instrument.code
• instrument.future.settlement_asset
• instrument.future.quote_name
• instrument.future.settlement_data_decimals
• instrument.future.terminating_key


Examples:

    A default MarketConfig object can be built with the following:

    $ market_config = MarketConfig("default")


    Pre-configured liquidity monitoring parameters can be loaded with the following:

    $ market_config = market_config.liquidity_monitoring_parameters.load("strict")


    Individual market parameter settings can be set with the following:

    $ market_config = market_config.set("decimal_places", 4)


    The NewMarketConfiguration proto can be built with the following:

    $ new_market_configuration_proto = market_config.build()

"""

import functools
import logging
from typing import Optional

import vega_sim.proto.vega as vega_protos
import vega_sim.proto.vega.data.v1 as oracles_protos
import vega_sim.proto.vega.data_source_pb2 as data_source_protos


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition(".")
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))


class Config:
    OPTS = {}

    def __init__(self, opt: Optional[str] = None) -> None:
        self.load(opt=opt)

    def load(self, opt: Optional[str] = None):
        if opt is None:
            opt = list(self.OPTS.keys())[0]
            logging.debug(f"No 'opt' arg given. Using default value '{opt}'.")

        if opt not in self.OPTS:
            raise ValueError(f"Invalid 'opt' arg '{opt}' specified.")

        return opt


class MarketConfig(Config):
    OPTS = {
        "default": {
            "decimal_places": 4,
            "position_decimal_places": 2,
            "metadata": None,
            "price_monitoring_parameters": "default",
            "liquidity_monitoring_parameters": "default",
            "log_normal": "default",
            "instrument": "default",
        }
    }

    def load(self, opt: Optional[str] = None):
        opt = super().load(opt=opt)

        self.decimal_places = self.OPTS[opt]["decimal_places"]
        self.position_decimal_places = self.OPTS[opt]["position_decimal_places"]
        self.metadata = self.OPTS[opt]["metadata"]

        self.instrument = InstrumentConfiguration(opt=self.OPTS[opt]["instrument"])
        self.price_monitoring_parameters = PriceMonitoringParameters(
            opt=self.OPTS[opt]["price_monitoring_parameters"]
        )
        self.liquidity_monitoring_parameters = LiquidityMonitoringParameters(
            opt=self.OPTS[opt]["liquidity_monitoring_parameters"]
        )
        self.log_normal = LogNormalRiskModel(opt=self.OPTS[opt]["log_normal"])

    def build(self):
        return vega_protos.governance.NewMarket(
            changes=vega_protos.governance.NewMarketConfiguration(
                decimal_places=self.decimal_places,
                position_decimal_places=self.position_decimal_places,
                metadata=self.metadata,
                instrument=self.instrument.build(),
                price_monitoring_parameters=self.price_monitoring_parameters.build(),
                liquidity_monitoring_parameters=self.liquidity_monitoring_parameters.build(),
                log_normal=self.log_normal.build(),
            )
        )

    def set(self, parameter, value):
        rsetattr(self, attr=parameter, val=value)


class PriceMonitoringParameters(Config):
    OPTS = {
        "default": {
            "horizon": 24 * 3600,
            "probability": "0.999999",
            "auction_extension": 5,
        }
    }

    def load(self, opt: Optional[str] = None):
        opt = super().load(opt=opt)

        self.horizon = self.OPTS[opt]["horizon"]
        self.probability = self.OPTS[opt]["probability"]
        self.auction_extension = self.OPTS[opt]["auction_extension"]

    def build(self):
        return vega_protos.markets.PriceMonitoringParameters(
            triggers=[
                {
                    "horizon": self.horizon,
                    "probability": self.probability,
                    "auction_extension": self.auction_extension,
                }
            ]
        )


class LiquidityMonitoringParameters(Config):
    OPTS = {
        "default": {
            "triggering_ratio": 0.7,
            "auction_extension": 0,
            "target_stake_parameters": "default",
        }
    }

    def load(self, opt: Optional[str] = None):
        opt = super().load(opt=opt)

        self.triggering_ratio = self.OPTS[opt]["triggering_ratio"]
        self.auction_extension = self.OPTS[opt]["auction_extension"]

        self.target_stake_parameters = TargetStakeParameters(
            opt=self.OPTS[opt]["target_stake_parameters"]
        )

    def build(self):
        return vega_protos.markets.LiquidityMonitoringParameters(
            triggering_ratio=self.triggering_ratio,
            auction_extension=self.auction_extension,
            target_stake_parameters=self.target_stake_parameters.build(),
        )


class TargetStakeParameters(Config):
    OPTS = {
        "default": {
            "time_window": 60 * 60,
            "scaling_factor": 1,
        }
    }

    def load(self, opt: Optional[str] = None):
        opt = super().load(opt=opt)

        self.time_window = self.OPTS[opt]["time_window"]
        self.scaling_factor = self.OPTS[opt]["scaling_factor"]

    def build(self):
        return vega_protos.markets.TargetStakeParameters(
            time_window=self.time_window,
            scaling_factor=self.scaling_factor,
        )


class LogNormalRiskModel(Config):
    OPTS = {
        "default": {
            "risk_aversion_parameter": 0.01,
            "tau": 1.90128526884173e-06,
            "params": "default",
        }
    }

    def load(self, opt: Optional[str] = None):
        opt = super().load(opt=opt)

        self.risk_aversion_parameter = self.OPTS[opt]["risk_aversion_parameter"]
        self.tau = self.OPTS[opt]["tau"]

        self.params = LogNormalModelParams(opt=self.OPTS[opt]["params"])

    def build(self):
        return vega_protos.markets.LogNormalRiskModel(
            risk_aversion_parameter=self.risk_aversion_parameter,
            tau=self.tau,
            params=self.params.build(),
        )


class LogNormalModelParams(Config):
    OPTS = {
        "default": {
            "mu": 0,
            "r": 0.016,
            "sigma": 3.0,
        }
    }

    def __init__(self, opt: Optional[str] = None) -> None:
        super().__init__(opt)

    def load(self, opt: Optional[str] = None):
        opt = super().load(opt=opt)

        self.mu = self.OPTS[opt]["mu"]
        self.r = self.OPTS[opt]["r"]
        self.sigma = self.OPTS[opt]["sigma"]

    def build(self):
        return vega_protos.markets.LogNormalModelParams(
            mu=self.mu,
            r=self.r,
            sigma=self.sigma,
        )


class InstrumentConfiguration(Config):
    OPTS = {
        "default": {
            "name": None,
            "code": None,
            "future": "default",
        }
    }

    def load(self, opt: Optional[str] = None):
        opt = super().load(opt=opt)

        self.name = self.OPTS[opt]["name"]
        self.code = self.OPTS[opt]["code"]
        self.future = FutureProduct(opt=self.OPTS[opt]["future"])

    def build(self):
        return vega_protos.governance.InstrumentConfiguration(
            name=self.name, code=self.code, future=self.future.build()
        )


class FutureProduct(Config):
    OPTS = {
        "default": {
            "settlement_asset": None,
            "quote_name": None,
            "settlement_data_decimals": None,
            "terminating_key": None,
        }
    }

    def load(self, opt: Optional[str] = None):
        opt = super().load(opt=opt)

        self.settlement_asset = self.OPTS[opt]["settlement_asset"]
        self.quote_name = self.OPTS[opt]["quote_name"]
        self.settlement_data_decimals = self.OPTS[opt]["settlement_data_decimals"]
        self.terminating_key = self.OPTS[opt]["terminating_key"]

    def build(self):
        if None in [
            self.settlement_asset,
            self.quote_name,
            self.settlement_data_decimals,
            self.terminating_key,
        ]:
            print(
                [
                    self.settlement_asset,
                    self.quote_name,
                    self.settlement_data_decimals,
                    self.terminating_key,
                ]
            )
            raise ValueError(
                f"MarketConfig has not been updated with settlement asset information."
            )

        data_source_spec_for_settlement_data = data_source_protos.DataSourceDefinition(
            external=data_source_protos.DataSourceDefinitionExternal(
                oracle=data_source_protos.DataSourceSpecConfiguration(
                    signers=[
                        oracles_protos.data.Signer(
                            pub_key=oracles_protos.data.PubKey(key=self.terminating_key)
                        )
                    ],
                    filters=[
                        oracles_protos.spec.Filter(
                            key=oracles_protos.spec.PropertyKey(
                                name=f"price.{self.quote_name}.value",
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
                            pub_key=oracles_protos.data.PubKey(key=self.terminating_key)
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
        data_source_spec_binding = vega_protos.markets.DataSourceSpecToFutureBinding(
            settlement_data_property=f"price.{self.quote_name}.value",
            trading_termination_property="trading.terminated",
        )

        return vega_protos.governance.FutureProduct(
            settlement_asset=self.settlement_asset,
            quote_name=self.quote_name,
            data_source_spec_for_settlement_data=data_source_spec_for_settlement_data,
            data_source_spec_for_trading_termination=data_source_spec_for_trading_termination,
            data_source_spec_binding=data_source_spec_binding,
            settlement_data_decimals=self.settlement_data_decimals,
        )
