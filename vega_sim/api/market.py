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
• log_normal.risk_aversion_parameter
• log_normal.params.mu
• log_normal.params.r
• log_normal.params.sigma
• instrument.name
• instrument.code
• instrument.future.settlement_asset
• instrument.future.quote_name
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

import copy
import functools
import logging
from typing import Optional, Union

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

    def load(self, opt: Optional[Union[dict, str]] = None) -> dict:
        if opt is None:
            opt = list(self.OPTS.keys())[0]
            logging.debug(f"No 'opt' arg given. Using default value '{opt}'.")

        if isinstance(opt, str):
            if opt not in self.OPTS:
                raise ValueError(f"Invalid 'opt' arg '{opt}' specified.")
            return self.OPTS[opt]

        if isinstance(opt, dict):
            defaults = self.OPTS["default"]
            for key in defaults.keys():
                if key not in opt.keys():
                    opt[key] = defaults[key]
            return opt

        else:
            raise TypeError(f"Invalid type '{type(opt)}' for arg 'opt'.")


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
            "lp_price_range": 0.5,
            "linear_slippage_factor": 1e-3,
            "quadratic_slippage_factor": 0,
            "successor": None,
        }
    }

    def load(self, opt: Optional[str] = None):
        config = super().load(opt=opt)

        self.decimal_places = config["decimal_places"]
        self.position_decimal_places = config["position_decimal_places"]
        self.lp_price_range = str(config["lp_price_range"])
        self.linear_slippage_factor = str(config["linear_slippage_factor"])
        self.quadratic_slippage_factor = str(config["quadratic_slippage_factor"])
        self.metadata = config["metadata"]

        self.successor = (
            Successor(opt=config["successor"])
            if config["successor"] is not None
            else None
        )

        self.instrument = InstrumentConfiguration(opt=config["instrument"])
        self.price_monitoring_parameters = PriceMonitoringParameters(
            opt=config["price_monitoring_parameters"]
        )
        self.liquidity_monitoring_parameters = LiquidityMonitoringParameters(
            opt=config["liquidity_monitoring_parameters"]
        )
        self.log_normal = LogNormalRiskModel(opt=config["log_normal"])

    def build(self):
        new_market = vega_protos.governance.NewMarket(
            changes=vega_protos.governance.NewMarketConfiguration(
                decimal_places=self.decimal_places,
                position_decimal_places=self.position_decimal_places,
                lp_price_range=self.lp_price_range,
                metadata=self.metadata,
                instrument=self.instrument.build(),
                price_monitoring_parameters=self.price_monitoring_parameters.build(),
                liquidity_monitoring_parameters=self.liquidity_monitoring_parameters.build(),
                log_normal=self.log_normal.build(),
                linear_slippage_factor=self.linear_slippage_factor,
                quadratic_slippage_factor=self.quadratic_slippage_factor,
            )
        )
        if self.successor is not None:
            new_market.changes.successor.CopyFrom(self.successor.build())
        return new_market

    def set(self, parameter, value):
        rsetattr(self, attr=parameter, val=value)


class Successor(Config):
    OPTS = {
        "default": {
            "parent_market_id": None,
            "insurance_pool_fraction": 1,
        }
    }

    def load(self, opt: Optional[str] = None):
        config = super().load(opt=opt)
        self.parent_market_id = config["parent_market_id"]
        self.insurance_pool_fraction = config.get("insurance_pool_fraction", 1)

    def build(self) -> Optional[vega_protos.governance.SuccessorConfiguration]:
        if self.parent_market_id is not None:
            return vega_protos.governance.SuccessorConfiguration(
                parent_market_id=self.parent_market_id,
                insurance_pool_fraction=str(self.insurance_pool_fraction),
            )


class PriceMonitoringParameters(Config):
    OPTS = {
        "default": {
            "triggers": [
                {
                    "horizon": 900,  # 15 minutes
                    "probability": "0.90001",
                    "auction_extension": 60,
                },
                {
                    "horizon": 3600,  # 1 hour
                    "probability": "0.90001",
                    "auction_extension": 300,
                },
                {
                    "horizon": 14_400,  # 4 hour
                    "probability": "0.90001",
                    "auction_extension": 900,
                },
                {
                    "horizon": 86_400,  # 1 day
                    "probability": "0.90001",
                    "auction_extension": 3600,
                },
            ]
        }
    }

    def load(self, opt: Optional[str] = None):
        config = super().load(opt=opt)
        self.triggers = config["triggers"]

    def build(self):
        return vega_protos.markets.PriceMonitoringParameters(triggers=self.triggers)


class LiquidityMonitoringParameters(Config):
    OPTS = {
        "default": {
            "triggering_ratio": "0.7",
            "auction_extension": 0,
            "target_stake_parameters": "default",
        }
    }

    def load(self, opt: Optional[str] = None):
        config = super().load(opt=opt)

        self.triggering_ratio = config["triggering_ratio"]
        self.auction_extension = config["auction_extension"]

        self.target_stake_parameters = TargetStakeParameters(
            opt=config["target_stake_parameters"]
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
        config = super().load(opt=opt)

        self.time_window = config["time_window"]
        self.scaling_factor = config["scaling_factor"]

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
        config = super().load(opt=opt)

        self.risk_aversion_parameter = config["risk_aversion_parameter"]
        self.tau = config["tau"]

        self.params = LogNormalModelParams(opt=config["params"])

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
        config = super().load(opt=opt)

        self.mu = config["mu"]
        self.r = config["r"]
        self.sigma = config["sigma"]

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
        config = super().load(opt=opt)

        self.name = config["name"]
        self.code = config["code"]
        self.future = FutureProduct(opt=config["future"])

    def build(self):
        return vega_protos.governance.InstrumentConfiguration(
            name=self.name, code=self.code, future=self.future.build()
        )


class FutureProduct(Config):
    OPTS = {
        "default": {
            "settlement_asset": None,
            "quote_name": None,
            "number_decimal_places": None,
            "terminating_key": None,
        }
    }

    def load(self, opt: Optional[Union[dict, str]] = None):
        config = super().load(opt=opt)

        self.settlement_asset = config["settlement_asset"]
        self.quote_name = config["quote_name"]
        self.number_decimal_places = config["number_decimal_places"]
        self.terminating_key = config["terminating_key"]

    def build(self):
        if None in [
            self.settlement_asset,
            self.quote_name,
            self.number_decimal_places,
            self.terminating_key,
        ]:
            raise ValueError(
                "MarketConfig has not been updated with settlement asset information."
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
                                number_decimal_places=self.number_decimal_places,
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
        )
