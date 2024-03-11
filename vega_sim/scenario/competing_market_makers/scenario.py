import numpy as np
from typing import Optional, List, Dict

from vega_sim.api.market import MarketConfig
from vega_sim.scenario.scenario import Scenario
from vega_sim.scenario.constants import Network
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.configurable_market.agents import ConfigurableMarketManager
from vega_sim.scenario.common.utils.price_process import random_walk
from vega_sim.environment.environment import (
    MarketEnvironmentWithState,
    NetworkEnvironment,
)
from vega_sim.scenario.common.agents import (
    StateAgent,
    UncrossAuctionAgent,
    MarketOrderTrader,
    LimitOrderTrader,
    UniformLiquidityProvider,
)

# Mainnet market configuration as of 21/12/2023
BTCUSDPERP = {
    "decimalPlaces": 1,
    "positionDecimalPlaces": 4,
    "instrument": {
        "code": "BTC/USD-PERP",
        "perpetual": {
            "quoteName": "USD",
            "marginFundingFactor": "0.9",
            "interestRate": "0.1095",
            "clampLowerBound": "-0.0005",
            "clampUpperBound": "0.0005",
            "dataSourceSpecForSettlementSchedule": {
                "internal": {
                    "timeTrigger": {
                        "conditions": [
                            {"operator": "OPERATOR_GREATER_THAN_OR_EQUAL", "value": "0"}
                        ],
                        "triggers": [{"initial": "1701727200", "every": "28800"}],
                    }
                }
            },
            "dataSourceSpecForSettlementData": {
                "external": {
                    "ethOracle": {
                        "address": "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",
                        "abi": '[{"inputs":[],"name":"latestAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"}]',
                        "method": "latestAnswer",
                        "args": [],
                        "trigger": {
                            "timeTrigger": {"initial": "1701727200", "every": "300"}
                        },
                        "requiredConfirmations": "3",
                        "filters": [
                            {
                                "key": {
                                    "name": "btc.price",
                                    "type": "TYPE_INTEGER",
                                    "numberDecimalPlaces": "8",
                                },
                                "conditions": [
                                    {"operator": "OPERATOR_GREATER_THAN", "value": "0"}
                                ],
                            }
                        ],
                        "normalisers": [{"name": "btc.price", "expression": "$[0]"}],
                    }
                }
            },
            "dataSourceSpecBinding": {
                "settlementDataProperty": "btc.price",
                "settlementScheduleProperty": "vegaprotocol.builtin.timetrigger",
            },
        },
    },
    "metadata": [
        "base:BTC",
        "quote:USDT",
        "class:fx/crypto",
        "perpetual",
        "sector:defi",
        "enactment:2023-12-01T18:00:00Z",
    ],
    "priceMonitoringParameters": {
        "triggers": [
            {"horizon": "4320", "probability": "0.9999999", "auctionExtension": "300"},
            {"horizon": "1440", "probability": "0.9999999", "auctionExtension": "180"},
            {"horizon": "360", "probability": "0.9999999", "auctionExtension": "120"},
        ]
    },
    "liquidityMonitoringParameters": {
        "targetStakeParameters": {"timeWindow": "3600", "scalingFactor": 0.05},
        "triggeringRatio": "0.1",
        "auctionExtension": "1",
    },
    "logNormal": {
        "riskAversionParameter": 0.000001,
        "tau": 0.000003995,
        "params": {"mu": 0, "r": 0, "sigma": 1},
    },
    "linearSlippageFactor": "0.001",
    "quadraticSlippageFactor": "0",
    "liquiditySlaParameters": {
        "priceRange": "0.03",
        "commitmentMinTimeFraction": "0.85",
        "performanceHysteresisEpochs": "1",
        "slaCompetitionFactor": "0.5",
    },
}


class CompetingMarketMakers(Scenario):
    def __init__(
        self,
        num_steps: int = 3000,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        step_length_seconds: Optional[float] = None,
        market_name: str = "CompetingMarketMakers",
        market_code: str = "CMM",
        asset_name: str = "USDT",
        asset_decimals: int = 18,
        output: bool = True,
        market_config: Optional[MarketConfig] = None,
        lps_min_bps: List[float] = [1, 50],
        lps_max_bps: List[float] = [50, 100],
        lps_commitment_amount: List[float] = [5e6, 5e6],
        tau_scaling: Optional[float] = 10,
        epoch_length: Optional[str] = "10m",
        distribution_time_step: Optional[str] = "1m",
    ):
        super().__init__()

        # Set simulation parameters
        self.num_steps = num_steps
        self.step_length_seconds = (
            step_length_seconds
            if step_length_seconds is not None
            else block_length_seconds
        )
        self.block_length_seconds = block_length_seconds
        self.transactions_per_block = transactions_per_block

        # Set market parameters
        self.market_name = market_name
        self.market_code = market_code
        self.asset_name = asset_name
        self.asset_decimals = asset_decimals

        if market_config is None:
            self.market_config = MarketConfig("perpetual")
            self.market_config.load(BTCUSDPERP)

        # Validate and set LP parameters
        lengths = [
            len(var) for var in [lps_min_bps, lps_max_bps, lps_commitment_amount]
        ]
        if lengths[:-1] != lengths[1:]:
            raise ValueError(
                "The lengths of 'lps_min_bps', 'lps_max_bps', and "
                + "'lps_commitment_amount' must all be the same."
            )
        self.lps_min_bps = lps_min_bps
        self.lps_max_bps = lps_max_bps
        self.lps_commitment_amount = lps_commitment_amount

        # Set network parameters
        self.tau_scaling = tau_scaling
        self.epoch_length = epoch_length
        self.distribution_time_step = distribution_time_step

        self.output = output

    def configure_agents(
        self,
        vega: VegaServiceNull,
        tag: str,
        random_state: Optional[np.random.RandomState],
        **kwargs,
    ) -> List[StateAgent]:
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

        starting_price = 40000
        price_process = random_walk(
            num_steps=self.num_steps + 1,
            sigma=0.1 * 0.001 * starting_price,
            starting_price=starting_price,
            decimal_precision=self.asset_decimals,
        )

        agents = []

        agents.append(
            ConfigurableMarketManager(
                proposal_key_name="configurable_market_manager",
                termination_key_name="configurable_market_manager",
                market_config=self.market_config,
                market_name=self.market_name,
                market_code=self.market_code,
                asset_name=self.asset_name,
                asset_dp=self.asset_decimals,
                settlement_price=price_process[-1],
                network_parameters={
                    "market.liquidity.probabilityOfTrading.tau.scaling": str(
                        self.tau_scaling
                    ),
                    "market.liquidity.providersFeeCalculationTimeStep": self.distribution_time_step,
                    "validators.epoch.length": self.epoch_length,
                },
            )
        )
        for min_bps, max_bps, commitment_amount in zip(
            self.lps_min_bps, self.lps_max_bps, self.lps_commitment_amount
        ):
            agents.append(
                UniformLiquidityProvider(
                    key_name=f"mm_{min_bps}-{max_bps}",
                    market_name=self.market_name,
                    asset_name=self.asset_name,
                    bps_range_min=min_bps,
                    bps_range_max=max_bps,
                    levels=50,
                    fee=0.001,
                    initial_asset_mint=commitment_amount * 10,
                    commitment_amount=commitment_amount,
                    tag=f"mm_{min_bps}-{max_bps}",
                    random_state=random_state,
                    price_process=iter(price_process),
                )
            )
        agents.append(
            UncrossAuctionAgent(
                key_name="uncross_auction_agent_bid",
                side="SIDE_BUY",
                initial_asset_mint=1e9,
                price_process=iter(price_process),
                market_name=self.market_name,
                asset_name=self.asset_name,
                uncrossing_size=10**-self.market_config.position_decimal_places,
                tag="bid",
            )
        )
        agents.append(
            UncrossAuctionAgent(
                key_name="uncross_auction_agent_ask",
                side="SIDE_SELL",
                initial_asset_mint=1e9,
                price_process=iter(price_process),
                market_name=self.market_name,
                asset_name=self.asset_name,
                uncrossing_size=10**-self.market_config.position_decimal_places,
                tag="ask",
            )
        )
        agents.append(
            MarketOrderTrader(
                key_name="market_order_trader",
                market_name=self.market_name,
                asset_name=self.asset_name,
                buy_intensity=10,
                sell_intensity=10,
                base_order_size=10**-self.market_config.position_decimal_places,
                step_bias=1,
            )
        )
        [
            agents.append(
                LimitOrderTrader(
                    key_name="limit_order_trader",
                    market_name=self.market_name,
                    asset_name=self.asset_name,
                    time_in_force_opts={"TIME_IN_FORCE_GTT": 1},
                    buy_volume=10**-self.market_config.position_decimal_places,
                    sell_volume=10**-self.market_config.position_decimal_places,
                    buy_intensity=10,
                    sell_intensity=10,
                    submit_bias=1,
                    cancel_bias=0,
                    duration=5,
                    price_process=price_process,
                    spread=0,
                    mean=-3,
                    sigma=0.5,
                    tag=i,
                )
            )
            for i in range(10)
        ]

        return {agent.name: agent for agent in agents}

    def configure_environment(
        self,
        vega: VegaServiceNull,
        **kwargs,
    ) -> MarketEnvironmentWithState:
        if kwargs.get("network", Network.NULLCHAIN) == Network.NULLCHAIN:
            return MarketEnvironmentWithState(
                agents=list(self.agents.values()),
                n_steps=self.num_steps,
                random_agent_ordering=False,
                transactions_per_block=self.transactions_per_block,
                vega_service=vega,
                step_length_seconds=self.step_length_seconds,
                block_length_seconds=vega.seconds_per_block,
            )
        else:
            return NetworkEnvironment(
                agents=list(self.agents.values()),
                n_steps=self.num_steps,
                vega_service=vega,
                step_length_seconds=self.step_length_seconds,
                raise_datanode_errors=kwargs.get("raise_datanode_errors", False),
                raise_step_errors=kwargs.get("raise_step_errors", False),
                random_state=self.random_state,
                create_keys=True,
                mint_keys=True,
            )
