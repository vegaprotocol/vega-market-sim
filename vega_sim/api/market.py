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
• liquidity_sla_parameters.price_range
• liquidity_sla_parameters.commitment_min_time_fraction
• liquidity_sla_parameters.performance_hysteresis_epochs
• liquidity_sla_parameters.sla_competition_factor
• log_normal.tau
• log_normal.risk_aversion_parameter
• log_normal.params.mu
• log_normal.params.r
• log_normal.params.sigma
• instrument.name
• instrument.code
• instrument.future.settlement_asset
• instrument.future.quote_name
• instrument.future.number_decimal_places
• instrument.future.terminating_key
• instrument.perpetual.settlement_asset
• instrument.perpetual.quote_name
• instrument.perpetual.number_decimal_places
• instrument.perpetual.settlement_key
• instrument.perpetual.funding_payment_frequency_in_seconds
• instrument.perpetual.margin_funding_factor
• instrument.perpetual.interest_rate
• instrument.perpetual.clamp_lower_bound
• instrument.perpetual.clamp_upper_bound


Examples:

    A default futures MarketConfig object can be built with the following:

    $ market_config = MarketConfig("futures")


    Pre-configured liquidity monitoring parameters can be loaded with the following:

    $ market_config = market_config.liquidity_monitoring_parameters.load("strict")


    Individual market parameter settings can be set with the following:

    $ market_config = market_config.set("decimal_places", 4)


    The NewMarketConfiguration proto can be built with the following:

    $ new_market_configuration_proto = market_config.build()

"""

import uuid
import copy
import functools
import logging
from typing import Optional, Union

import vega_python_protos.protos.vega as vega_protos
import vega_python_protos.protos.vega.data.v1 as oracles_protos
import vega_python_protos.protos.vega.data_source_pb2 as data_source_protos

from vega_sim.api.helpers import get_enum


import vega_sim.builders as build


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

            # Recursively ensure all keys are in snake case for protos
            def ensure_snake_case(config_dict: dict) -> str:
                new_dict = {}
                for key, value in config_dict.items():
                    new_key = "".join(
                        ["_" + c.lower() if c.isupper() else c for c in key]
                    ).lstrip("_")
                    if isinstance(value, dict):
                        new_dict[new_key] = ensure_snake_case(value)
                    elif isinstance(value, list):
                        new_list = []
                        for element in value:
                            if isinstance(element, dict):
                                new_list.append(ensure_snake_case(element))
                            else:
                                new_list.append(element)
                        new_dict[new_key] = new_list
                    else:
                        new_dict[new_key] = value
                return new_dict

            opt = ensure_snake_case(opt)
            defaults = self.OPTS["default"]
            for key in defaults.keys():
                if key not in opt.keys():
                    opt[key] = defaults[key]
            return opt

        else:
            raise TypeError(f"Invalid type '{type(opt)}' for arg 'opt'.")


class SpotMarketConfig(Config):
    OPTS = {
        "default": {
            "instrument": "spot",
            "price_decimal_places": 4,
            "metadata": None,
            "price_monitoring_parameters": "default",
            "target_stake_parameters": "default",
            "log_normal": "default",
            "size_decimal_places": 2,
            "liquidity_sla_parameters": "default",
            "liquidity_fee_settings": "default",
            "tick_size": "2",
        },
    }

    def load(self, opt: Optional[str] = None):
        config = super().load(opt=opt)

        self.price_decimal_places = int(config["price_decimal_places"])
        self.size_decimal_places = int(config["size_decimal_places"])
        self.metadata = config["metadata"]
        self.tick_size = int(config["tick_size"])

        self.instrument = InstrumentConfiguration(opt=config["instrument"])
        self.liquidity_sla_parameters = LiquiditySLAParameters(
            opt=config["liquidity_sla_parameters"]
        )
        self.price_monitoring_parameters = PriceMonitoringParameters(
            opt=config["price_monitoring_parameters"]
        )
        self.target_stake_parameters = TargetStakeParameters(
            opt=config["target_stake_parameters"]
        )
        self.log_normal = LogNormalRiskModel(opt=config["log_normal"])
        self.liquidity_fee_settings = LiquidityFeeSettings(
            opt=config["liquidity_fee_settings"]
        )

    def build(self, oracle_pubkey: str):
        new_spot_market = vega_protos.governance.NewSpotMarket(
            changes=build.governance.new_spot_market_configuration(
                instrument=self.instrument.build(oracle_pubkey=oracle_pubkey),
                price_decimal_places=int(self.price_decimal_places),
                price_monitoring_parameters=self.price_monitoring_parameters.build(),
                target_stake_parameters=self.target_stake_parameters.build(),
                log_normal=self.log_normal.build(),
                size_decimal_places=int(self.size_decimal_places),
                sla_params=self.liquidity_sla_parameters.build(),
                liquidity_fee_settings=self.liquidity_fee_settings.build(),
                tick_size=str(self.tick_size),
                metadata=self.metadata,
            )
        )
        return new_spot_market

    def is_future(self) -> bool:
        return self.instrument.future is not None

    def is_perp(self) -> bool:
        return self.instrument.perpetual is not None

    def is_spot(self) -> bool:
        return self.instrument.spot is not None


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
            "linear_slippage_factor": 1e-3,
            "quadratic_slippage_factor": 0,
            "successor": None,
            "liquidity_sla_parameters": "default",
            "liquidity_fee_settings": "default",
            "liquidation_strategy": "default",
            "mark_price_configuration": "default",
            "tick_size": "1",
        },
        "future": {
            "decimal_places": 4,
            "position_decimal_places": 2,
            "metadata": None,
            "price_monitoring_parameters": "default",
            "liquidity_monitoring_parameters": "default",
            "log_normal": "default",
            "instrument": "future",
            "linear_slippage_factor": 1e-3,
            "quadratic_slippage_factor": 0,
            "successor": None,
            "liquidity_sla_parameters": "default",
            "liquidity_fee_settings": "default",
            "liquidation_strategy": "default",
            "mark_price_configuration": "default",
            "tick_size": "1",
        },
        "perpetual": {
            "decimal_places": 4,
            "position_decimal_places": 2,
            "metadata": None,
            "price_monitoring_parameters": "default",
            "liquidity_monitoring_parameters": "default",
            "log_normal": "default",
            "instrument": "perpetual",
            "linear_slippage_factor": 1e-3,
            "quadratic_slippage_factor": 0,
            "successor": None,
            "liquidity_sla_parameters": "default",
            "liquidity_fee_settings": "default",
            "liquidation_strategy": "default",
            "mark_price_configuration": "default",
            "tick_size": "1",
        },
    }

    def load(self, opt: Optional[str] = None):
        config = super().load(opt=opt)

        self.decimal_places = int(config["decimal_places"])
        self.position_decimal_places = int(config["position_decimal_places"])
        self.liquidity_sla_parameters = LiquiditySLAParameters(
            opt=config["liquidity_sla_parameters"]
        )
        self.linear_slippage_factor = str(config["linear_slippage_factor"])
        self.quadratic_slippage_factor = str(config["quadratic_slippage_factor"])
        self.metadata = config["metadata"]
        self.tick_size = int(config["tick_size"])

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
        self.liquidity_fee_settings = LiquidityFeeSettings(
            opt=config["liquidity_fee_settings"]
        )
        self.liquidation_strategy = LiquidationStrategy(
            opt=config["liquidation_strategy"]
        )
        self.mark_price_configuration = CompositePriceConfiguration(
            opt=config["mark_price_configuration"]
        )

    def build(self, oracle_pubkey: str):
        new_market = vega_protos.governance.NewMarket(
            changes=vega_protos.governance.NewMarketConfiguration(
                decimal_places=int(self.decimal_places),
                position_decimal_places=int(self.position_decimal_places),
                liquidity_sla_parameters=self.liquidity_sla_parameters.build(),
                metadata=self.metadata,
                instrument=self.instrument.build(oracle_pubkey=oracle_pubkey),
                price_monitoring_parameters=self.price_monitoring_parameters.build(),
                liquidity_monitoring_parameters=self.liquidity_monitoring_parameters.build(),
                log_normal=self.log_normal.build(),
                linear_slippage_factor=self.linear_slippage_factor,
                quadratic_slippage_factor=self.quadratic_slippage_factor,
                successor=(
                    self.successor.build() if self.successor is not None else None
                ),
                liquidity_fee_settings=self.liquidity_fee_settings.build(),
                liquidation_strategy=self.liquidation_strategy.build(),
                mark_price_configuration=self.mark_price_configuration.build(
                    oracle_pubkey=oracle_pubkey
                ),
                tick_size=str(self.tick_size),
            )
        )
        return new_market

    def set(self, parameter, value):
        rsetattr(self, attr=parameter, val=value)

    def is_future(self) -> bool:
        return self.instrument.future is not None

    def is_perp(self) -> bool:
        return self.instrument.perpetual is not None

    def is_spot(self) -> bool:
        return self.instrument.spot is not None


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
            return build.governance.successor_configuration(
                parent_market_id=self.parent_market_id,
                insurance_pool_fraction=self.insurance_pool_fraction,
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
        return build.markets.price_monitoring_parameters(
            triggers=[
                build.markets.price_monitoring_trigger(
                    trigger["horizon"],
                    trigger["probability"],
                    trigger["auction_extension"],
                )
                for trigger in self.triggers
            ]
        )


class LiquidityMonitoringParameters(Config):
    OPTS = {
        "default": {
            "target_stake_parameters": "default",
        }
    }

    def load(self, opt: Optional[str] = None):
        config = super().load(opt=opt)

        self.target_stake_parameters = TargetStakeParameters(
            opt=config["target_stake_parameters"]
        )

    def build(self):
        return build.markets.liquidity_monitoring_parameters(
            target_stake_parameters=self.target_stake_parameters.build(),
        )


class LiquiditySLAParameters(Config):
    OPTS = {
        "default": {
            "price_range": 0.5,
            "commitment_min_time_fraction": 1,
            "performance_hysteresis_epochs": 1,
            "sla_competition_factor": 1,
        }
    }

    def load(self, opt: Optional[str] = None):
        config = super().load(opt=opt)

        self.price_range = config["price_range"]
        self.commitment_min_time_fraction = config["commitment_min_time_fraction"]

        self.performance_hysteresis_epochs = config["performance_hysteresis_epochs"]
        self.sla_competition_factor = config["sla_competition_factor"]

    def build(self):
        return build.markets.liquidity_sla_parameters(
            price_range=self.price_range,
            commitment_min_time_fraction=self.commitment_min_time_fraction,
            performance_hysteresis_epochs=self.performance_hysteresis_epochs,
            sla_competition_factor=self.sla_competition_factor,
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
        return build.markets.target_stake_parameters(
            time_window=self.time_window, scaling_factor=self.scaling_factor
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
        return build.markets.log_normal_risk_model(
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
        return build.markets.log_normal_model_params(
            mu=self.mu,
            r=self.r,
            sigma=self.sigma,
        )


class CompositePriceConfiguration(Config):
    OPTS = {
        "default": {
            "decay_weight": None,
            "composite_price_type": vega_protos.markets.COMPOSITE_PRICE_TYPE_LAST_TRADE,
            "source_staleness_tolerance": None,
            "decay_power": None,
            "cash_amount": None,
            "source_weights": None,
            "data_sources_spec": None,
            "data_sources_spec_binding": None,
        }
    }

    def load(self, opt: Optional[str] = None):
        config = super().load(opt=opt)

        self.decay_weight = (
            str(config["decay_weight"]) if config["decay_weight"] is not None else None
        )
        self.composite_price_type = config["composite_price_type"]
        self.source_staleness_tolerance = config["source_staleness_tolerance"]
        self.decay_power = config["decay_power"]
        self.cash_amount = (
            str(config["cash_amount"]) if config["cash_amount"] is not None else None
        )
        self.source_weights = (
            [str(w) for w in config["source_weights"]]
            if config["source_weights"] is not None
            else None
        )

        self.data_sources_spec = (
            [
                DataSourceDefinition(data_source_spec)
                for data_source_spec in config["data_sources_spec"]
            ]
            if config["data_sources_spec"] is not None
            else None
        )
        self.data_sources_spec_binding = (
            [
                SpecBindingForCompositePrice(data_source_spec_binding)
                for data_source_spec_binding in config["data_sources_spec_binding"]
            ]
            if config["data_sources_spec_binding"] is not None
            else None
        )

    def build(self, oracle_pubkey: str):
        return vega_protos.markets.CompositePriceConfiguration(
            composite_price_type=get_enum(
                self.composite_price_type, vega_protos.markets.CompositePriceType
            ),
            decay_weight=(
                str(self.decay_weight) if self.decay_weight is not None else None
            ),
            decay_power=int(self.decay_power) if self.decay_power is not None else None,
            cash_amount=str(self.cash_amount) if self.cash_amount is not None else None,
            source_weights=self.source_weights,
            source_staleness_tolerance=self.source_staleness_tolerance,
            data_sources_spec=(
                [
                    data_sources_spec.build(oracle_pubkey=oracle_pubkey)
                    for data_sources_spec in self.data_sources_spec
                ]
                if self.data_sources_spec is not None
                else None
            ),
            data_sources_spec_binding=(
                [
                    data_source_spec_binding.build()
                    for data_source_spec_binding in self.data_sources_spec_binding
                ]
                if self.data_sources_spec_binding is not None
                else None
            ),
        )


class LiquidityFeeSettings(Config):
    OPTS = {
        "default": {
            "method": vega_protos.markets.LiquidityFeeSettings.Method.METHOD_MARGINAL_COST,
            "fee_constant": None,
        }
    }

    def load(self, opt: Optional[str] = None):
        config = super().load(opt=opt)

        self.method = config["method"]
        self.fee_constant = config["fee_constant"]

    def build(self):
        return build.markets.liquidity_fee_settings(
            method=self.method,
            fee_constant=self.fee_constant,
        )


class LiquidationStrategy(Config):
    OPTS = {
        "default": {
            "disposal_time_step": 30,
            "disposal_fraction": 0.1,
            "full_disposal_size": 0,
            "max_fraction_consumed": 0.1,
            "disposal_slippage_range": 0.5,
        }
    }

    def load(self, opt: Optional[str] = None):
        config = super().load(opt=opt)

        self.disposal_time_step = config["disposal_time_step"]
        self.disposal_fraction = config["disposal_fraction"]
        self.full_disposal_size = config["full_disposal_size"]
        self.max_fraction_consumed = config["max_fraction_consumed"]
        self.disposal_slippage_range = config["disposal_slippage_range"]

    def build(self):
        return build.markets.liquidation_strategy(
            disposal_time_step=self.disposal_time_step,
            disposal_fraction=self.disposal_fraction,
            full_disposal_size=self.full_disposal_size,
            max_fraction_consumed=self.max_fraction_consumed,
            disposal_slippage_range=self.disposal_slippage_range,
        )


class InstrumentConfiguration(Config):
    OPTS = {
        "default": {
            "name": None,
            "code": None,
            "future": None,
            "perpetual": None,
            "spot": None,
        },
        "future": {
            "name": None,
            "code": None,
            "future": "default",
            "perpetual": None,
            "spot": None,
        },
        "perpetual": {
            "name": None,
            "code": None,
            "future": None,
            "perpetual": "default",
            "spot": None,
        },
        "spot": {
            "name": None,
            "code": None,
            "future": None,
            "perpetual": None,
            "spot": "default",
        },
    }

    def load(self, opt: Optional[str] = None):
        config = super().load(opt=opt)

        self.name: str = config["name"]
        self.code: str = config["code"]
        self.future = (
            None if config["future"] is None else FutureProduct(opt=config["future"])
        )
        self.perpetual = (
            None
            if config["perpetual"] is None
            else PerpetualProduct(opt=config["perpetual"])
        )
        self.spot = None if config["spot"] is None else SpotProduct(opt=config["spot"])

    def build(self, oracle_pubkey: str):
        if self.future != None:
            return vega_protos.governance.InstrumentConfiguration(
                name=self.name,
                code=self.code,
                future=self.future.build(oracle_pubkey=oracle_pubkey),
            )
        if self.perpetual != None:
            return vega_protos.governance.InstrumentConfiguration(
                name=self.name,
                code=self.code,
                perpetual=self.perpetual.build(oracle_pubkey=oracle_pubkey),
            )
        if self.spot != None:
            return vega_protos.governance.InstrumentConfiguration(
                name=self.name, code=self.code, spot=self.spot.build()
            )
        raise ValueError("No product specified for the instrument")


class FutureProduct(Config):
    OPTS = {
        "default": {
            "settlement_asset": None,
            "quote_name": None,
            "number_decimal_places": 18,
            "terminating_key": None,
            "data_source_spec_for_settlement_data": {
                "external": {
                    "oracle": {
                        "signers": [{"pubKey": {"key": None}}],
                        "filters": [
                            {
                                "key": {
                                    "name": "future.settlement",
                                    "type": "TYPE_INTEGER",
                                    "numberDecimalPlaces": "18",
                                },
                                "conditions": [
                                    {
                                        "operator": "OPERATOR_GREATER_THAN",
                                        "value": "0",
                                    },
                                ],
                            }
                        ],
                    }
                }
            },
            "data_source_spec_for_trading_termination": {
                "external": {
                    "oracle": {
                        "signers": [{"pubKey": {"key": None}}],
                        "filters": [
                            {
                                "key": {
                                    "name": "future.termination",
                                    "type": "TYPE_BOOLEAN",
                                },
                                "conditions": [
                                    {"operator": "OPERATOR_EQUALS", "value": "true"}
                                ],
                            }
                        ],
                    }
                }
            },
            "data_source_spec_binding": {
                "settlement_data_property": "future.settlement",
                "trading_termination_property": "future.termination",
            },
            "cap": None,
        }
    }

    def load(self, opt: Optional[Union[dict, str]] = None):
        config = super().load(opt=opt)

        self.settlement_asset = config["settlement_asset"]
        self.quote_name = config["quote_name"]
        self.number_decimal_places = config["number_decimal_places"]
        self.terminating_key = config["terminating_key"]

        self.data_source_spec_for_trading_termination = (
            DataSourceDefinition(config["data_source_spec_for_trading_termination"])
            if config["data_source_spec_for_trading_termination"] is not None
            else None
        )
        self.data_source_spec_for_settlement_data = (
            DataSourceDefinition(config["data_source_spec_for_settlement_data"])
            if config["data_source_spec_for_settlement_data"] is not None
            else None
        )
        self.data_source_spec_binding = (
            DataSourceSpecToFutureBinding(config["data_source_spec_binding"])
            if config["data_source_spec_binding"] is not None
            else None
        )
        self.cap = FutureCap(config["cap"]) if config["cap"] is not None else None

    def build(self, oracle_pubkey: str):
        if None in [
            self.settlement_asset,
        ]:
            raise ValueError(
                "MarketConfig has not been updated with settlement asset information."
            )

        proto = build.governance.future_product(
            settlement_asset=self.settlement_asset,
            quote_name=self.quote_name,
            data_source_spec_for_settlement_data=self.data_source_spec_for_settlement_data.build(
                oracle_pubkey=oracle_pubkey
            ),
            data_source_spec_for_trading_termination=self.data_source_spec_for_trading_termination.build(
                oracle_pubkey=oracle_pubkey
            ),
            data_source_spec_binding=self.data_source_spec_binding.build(),
            cap=self.cap.build() if self.cap is not None else None,
        )
        return proto

    def is_capped(self):
        return self.cap is not None

    def is_binary(self):
        if not self.is_capped():
            return False
        return self.cap.binary_settlement == True


class FutureCap(Config):
    OPTS = {
        "default": {
            "max_price": 1,
            "binary_settlement": False,
            "fully_collateralised": False,
        }
    }

    def load(self, opt: Optional[Union[dict, str]] = None):
        config = super().load(opt=opt)

        self.max_price = config["max_price"]
        self.binary_settlement = config["binary_settlement"]
        self.fully_collateralised = config["fully_collateralised"]

    def build(self):
        return build.markets.future_cap(
            max_price=self.max_price,
            binary_settlement=self.binary_settlement,
            fully_collateralised=self.fully_collateralised,
        )


class PerpetualProduct(Config):
    OPTS = {
        "default": {
            "settlement_asset": None,
            "quote_name": None,
            "number_decimal_places": 18,
            "settlement_key": None,
            "funding_payment_frequency_in_seconds": 300,
            "margin_funding_factor": 1,
            "interest_rate": 0,
            "clamp_lower_bound": 0,
            "clamp_upper_bound": 0,
            "funding_rate_scaling_factor": None,
            "funding_rate_lower_bound": None,
            "funding_rate_upper_bound": None,
            "internal_composite_price_configuration": "default",
            "data_source_spec_for_settlement_data": {
                "external": {
                    "oracle": {
                        "signers": [{"pubKey": {"key": None}}],
                        "filters": [
                            {
                                "key": {
                                    "name": "perpetual.settlement",
                                    "type": "TYPE_INTEGER",
                                    "numberDecimalPlaces": "18",
                                },
                                "conditions": [
                                    {
                                        "operator": "OPERATOR_GREATER_THAN",
                                        "value": "0",
                                    },
                                ],
                            }
                        ],
                    }
                }
            },
            "data_source_spec_binding": {
                "settlement_data_property": "perpetual.settlement",
                "settlement_schedule_property": "vegaprotocol.builtin.timetrigger",
            },
        }
    }

    def load(self, opt: Optional[Union[dict, str]] = None):
        config = super().load(opt=opt)

        self.settlement_asset = config["settlement_asset"]
        self.quote_name = config["quote_name"]
        self.number_decimal_places = config["number_decimal_places"]
        self.settlement_key = config["settlement_key"]
        self.funding_payment_frequency_in_seconds = config[
            "funding_payment_frequency_in_seconds"
        ]
        self.margin_funding_factor = config["margin_funding_factor"]
        self.interest_rate = config["interest_rate"]
        self.clamp_lower_bound = config["clamp_lower_bound"]
        self.clamp_upper_bound = config["clamp_upper_bound"]
        self.funding_rate_scaling_factor = config["funding_rate_scaling_factor"]
        self.funding_rate_lower_bound = config["funding_rate_lower_bound"]
        self.funding_rate_upper_bound = config["funding_rate_upper_bound"]

        self.data_source_spec_for_settlement_data = (
            DataSourceDefinition(config["data_source_spec_for_settlement_data"])
            if config["data_source_spec_for_settlement_data"] is not None
            else None
        )

        self.data_source_spec_binding = (
            DataSourceSpecToPerpetualBinding(config["data_source_spec_binding"])
            if config["data_source_spec_binding"] is not None
            else None
        )

    def build(self, oracle_pubkey: str):
        if None in [
            self.settlement_asset,
        ]:
            raise ValueError(
                "MarketConfig has not been updated with settlement asset information."
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
                            every=self.funding_payment_frequency_in_seconds
                        )
                    ],
                )
            )
        )

        return build.governance.perpetual_product(
            settlement_asset=self.settlement_asset,
            quote_name=self.quote_name,
            margin_funding_factor=self.margin_funding_factor,
            interest_rate=self.interest_rate,
            clamp_lower_bound=self.clamp_lower_bound,
            clamp_upper_bound=self.clamp_upper_bound,
            data_source_spec_for_settlement_schedule=data_source_spec_for_settlement_schedule,
            data_source_spec_for_settlement_data=self.data_source_spec_for_settlement_data.build(
                oracle_pubkey=oracle_pubkey
            ),
            data_source_spec_binding=self.data_source_spec_binding.build(),
            funding_rate_scaling_factor=self.funding_rate_scaling_factor,
            funding_rate_lower_bound=self.funding_rate_lower_bound,
            funding_rate_upper_bound=self.funding_rate_upper_bound,
        )


class SpotProduct(Config):
    OPTS = {"default": {"base_asset": None, "quote_asset": None, "name": None}}

    def load(self, opt: Optional[Union[dict, str]] = None):
        config = super().load(opt=opt)

        self.base_asset = str(config["base_asset"])
        self.quote_asset = str(config["base_asset"])

    def build(self):
        return build.governance.spot_product(
            base_asset=self.base_asset,
            quote_asset=self.quote_asset,
        )


class DataSourceDefinition(Config):
    OPTS = {"default": {"internal": None, "external": None}}

    def load(self, opt: Union[dict, str] = None) -> dict:
        config = super().load(opt)
        self.internal = (
            DataSourceDefinitionInternal(config["internal"])
            if config["internal"] is not None
            else None
        )
        self.external = (
            DataSourceDefinitionExternal(config["external"])
            if config["external"] is not None
            else None
        )

    def build(self, oracle_pubkey: str):
        return build.data_source.data_source_definition(
            internal=self.internal.build() if self.internal is not None else None,
            external=(
                self.external.build(oracle_pubkey=oracle_pubkey)
                if self.external is not None
                else None
            ),
        )


class DataSourceDefinitionInternal(Config):
    OPTS = {
        "default": {
            "time": None,
            "time_trigger": None,
        }
    }

    def load(self, opt: Optional[Union[dict, str]] = None):
        config = super().load(opt=opt)
        self.time = config["time"]
        self.time_trigger = config["time_trigger"]

    def build(self):
        return build.data_source.data_source_definition_internal(
            time=self.time,
            time_trigger=self.time_trigger,
        )


class DataSourceDefinitionExternal(Config):
    OPTS = {
        "default": {
            "oracle": None,
            "eth_oracle": None,
        }
    }

    def load(self, opt: Optional[Union[dict, str]] = None):
        config = super().load(opt=opt)
        self.oracle = (
            DataSourceSpecConfiguration(config["oracle"])
            if config["oracle"] is not None
            else None
        )
        self.eth_oracle = (
            EthOracleSpec(config["eth_oracle"])
            if config["eth_oracle"] is not None
            else None
        )

    def build(self, oracle_pubkey: str):
        return build.data_source.data_source_definition_external(
            oracle=(
                self.oracle.build(oracle_pubkey=oracle_pubkey)
                if self.oracle is not None
                else None
            ),
            eth_oracle=(
                self.eth_oracle.build(oracle_pubkey=oracle_pubkey)
                if self.eth_oracle is not None
                else None
            ),
        )


class DataSourceSpecConfiguration(Config):
    OPTS = {
        "default": {
            "filters": None,
        }
    }

    def load(self, opt: Optional[Union[dict, str]] = None):
        config = super().load(opt=opt)
        self.filters = config["filters"]

    def build(self, oracle_pubkey: str):
        return build.data_source.data_source_spec_configuration(
            signers=[
                build.data.data.signer(
                    pub_key=build.data.data.pub_key(key=oracle_pubkey)
                )
            ],
            filters=[
                build.data.spec.filter(
                    key=build.data.spec.property_key(
                        name=filter["key"]["name"],
                        type=filter["key"]["type"],
                        number_decimal_places=filter["key"].get("number_decimal_places", None),
                    ),
                    conditions=[
                        build.data.spec.condition(
                            operator=condition["operator"], value=condition["value"]
                        )
                        for condition in filter.get("conditions", [])
                    ],
                )
                for filter in self.filters
            ],
        )


class EthOracleSpec(Config):
    OPTS = {
        "default": {
            "filters": None,
        }
    }

    def load(self, opt: Union[dict, str, None] = None) -> dict:
        config = super().load(opt)
        self.filters = config["filters"]

    def build(self, oracle_pubkey: str):
        return build.data_source.data_source_spec_configuration(
            signers=[
                build.data.data.signer(
                    pub_key=build.data.data.pub_key(key=oracle_pubkey)
                )
            ],
            filters=[
                build.data.spec.filter(
                    key=build.data.spec.property_key(
                        name=filter["key"]["name"],
                        type=filter["key"]["type"],
                        number_decimal_places=filter["key"].get(
                            "number_decimal_places", None
                        ),
                    ),
                    conditions=[],
                )
                for filter in self.filters
            ],
        )


class DataSourceSpecToFutureBinding(Config):
    OPTS = {
        "default": {
            "settlement_data_property": None,
            "trading_termination_property": None,
        }
    }

    def load(self, opt: Optional[Union[dict, str]] = None):
        config = super().load(opt=opt)
        self.settlement_data_property = config["settlement_data_property"]
        self.trading_termination_property = config["trading_termination_property"]

    def build(self):
        return build.markets.data_source_spec_to_future_binding(
            settlement_data_property=self.settlement_data_property,
            trading_termination_property=self.trading_termination_property,
        )


class DataSourceSpecToPerpetualBinding(Config):
    OPTS = {
        "default": {
            "settlement_data_property": "btc.price",
            "settlement_schedule_property": "vegaprotocol.builtin.timetrigger",
        }
    }

    def load(self, opt: Optional[Union[dict, str]] = None):
        config = super().load(opt=opt)
        self.settlement_data_property = config["settlement_data_property"]
        self.settlement_schedule_property = config["settlement_schedule_property"]

    def build(self):
        return build.markets.data_source_spec_to_perpetual_binding(
            settlement_data_property=self.settlement_data_property,
            settlement_schedule_property=self.settlement_schedule_property,
        )


class SpecBindingForCompositePrice(Config):
    OPTS = {"default": {"price_source_property": "price"}}

    def load(self, opt: Optional[Union[dict, str]] = None):
        config = super().load(opt=opt)
        self.price_source_property = config["price_source_property"]

    def build(self):
        return build.data_source.spec_binding_for_composite_price(
            price_source_property=self.price_source_property
        )
