import argparse
import datetime
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import vega_sim.proto.vega as vega_protos
from vega_sim.api.market import MarketConfig
from vega_sim.environment.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.common.agents import (
    ExponentialShapedMarketMaker,
    LimitOrderTrader,
    MarketOrderTrader,
    ArbitrageTrader,
    PriceSensitiveMarketOrderTrader,
    StateAgent,
    UncrossAuctionAgent,
)
from vega_sim.scenario.common.utils.price_process import (
    Granularity,
    get_historic_price_series,
    random_walk,
)
from vega_sim.scenario.configurable_market.agents import ConfigurableMarketManager
from vega_sim.scenario.constant_function_market.agents import (
    CFMMarketMaker,
    CFMV3MarketMaker,
)
from vega_sim.scenario.constants import Network
from vega_sim.scenario.scenario import Scenario
from vega_sim.tools.scenario_plots import (
    account_and_margin_plots,
    fuzz_plots,
    price_comp_plots,
    plot_run_outputs,
    reward_plots,
    sla_plot,
)


@dataclass
class MarketHistoryAdditionalData:
    at_time: datetime.datetime
    external_prices: Dict[str, float]


def state_extraction_fn(vega: VegaServiceNull, agents: dict):
    at_time = vega.get_blockchain_time()

    external_prices = {}

    for _, agent in agents.items():
        if isinstance(agent, (CFMMarketMaker, CFMV3MarketMaker)):
            external_prices[agent.market_id] = agent.curr_price

    return MarketHistoryAdditionalData(
        at_time=at_time,
        external_prices=external_prices,
    )


def additional_data_to_rows(data) -> List[pd.Series]:
    results = []
    for market_id in data.external_prices.keys():
        results.append(
            {
                "time": data.at_time,
                "market_id": market_id,
                "external_price": data.external_prices.get(market_id, np.NaN),
            }
        )
    return results


class CFMScenario(Scenario):
    def __init__(
        self,
        num_steps: int = 60 * 24 * 30 * 3,
        transactions_per_block: int = 4096,
        block_length_seconds: float = 1,
        step_length_seconds: Optional[float] = None,
        market_config: Optional[dict] = None,
        output: bool = True,
        pause_every_n_steps: Optional[int] = None,
    ):
        super().__init__(
            state_extraction_fn=lambda vega, agents: state_extraction_fn(vega, agents),
            additional_data_output_fns={
                "additional_data.csv": lambda data: additional_data_to_rows(data),
            },
        )

        self.market_config = market_config

        self.pause_every_n_steps = pause_every_n_steps
        self.num_steps = num_steps
        self.step_length_seconds = (
            step_length_seconds
            if step_length_seconds is not None
            else block_length_seconds
        )

        self.block_length_seconds = block_length_seconds
        self.transactions_per_block = transactions_per_block

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

        self.agents = []
        self.initial_asset_mint = 10e9

        # Define the market and the asset:
        market_name = "CFM:Perp"
        asset_name = "USD"
        asset_dp = 18

        market_agents = {}
        # Create fuzzed market config
        market_config = MarketConfig()

        if self.market_config is not None:
            for param in self.market_config:
                market_config.set(param=self.market_config[param])

        i_market = 0
        # Create fuzzed price process
        # price_process = [1000] * self.num_steps
        # price_process = random_walk(
        #     random_state=self.random_state,
        #     starting_price=1000,
        #     num_steps=self.num_steps,
        #     decimal_precision=int(market_config.decimal_places),
        # )
        # price_process = get_historic_price_series(
        #     product_id="ETH-USD",
        #     granularity=Granularity.MINUTE,
        #     start=str(datetime.datetime(2023, 10, 23, 10)),
        #     end=str(
        #         datetime.datetime(2023, 10, 23, 10) + datetime.timedelta(minutes=1000)
        #     ),
        # ).values
        # price_process = get_historic_price_series(
        #     product_id="ETH-USD",
        #     granularity=Granularity.MINUTE,
        #     start=str(datetime.datetime(2022, 11, 8)),
        #     end=str(datetime.datetime(2022, 11, 8) + datetime.timedelta(minutes=1000)),
        # ).values

        price_process = get_historic_price_series(
            product_id="ETH-USD",
            granularity=Granularity.MINUTE,
            start=str(datetime.datetime(2023, 7, 8)),
            end=str(datetime.datetime(2023, 7, 8) + datetime.timedelta(minutes=1000)),
        ).values

        # Create fuzzed market managers
        market_agents["market_managers"] = [
            ConfigurableMarketManager(
                proposal_wallet_name="MARKET_MANAGER",
                proposal_key_name="PROPOSAL_KEY",
                termination_wallet_name="MARKET_MANAGER",
                termination_key_name="TERMINATION_KEY",
                market_config=market_config,
                market_name=market_name,
                market_code=market_name,
                asset_dp=asset_dp,
                asset_name=asset_name,
                settlement_price=price_process[-1],
                tag="MARKET",
            )
        ]

        market_agents["auction_traders"] = [
            UncrossAuctionAgent(
                wallet_name="AUCTION_TRADERS",
                key_name=f"MARKET_{str(i_market).zfill(3)}_{side}",
                side=side,
                initial_asset_mint=self.initial_asset_mint,
                price_process=iter(price_process),
                market_name=market_name,
                asset_name=asset_name,
                uncrossing_size=0.01,
                tag=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
            )
            for i_agent, side in enumerate(["SIDE_BUY", "SIDE_SELL"])
        ]

        market_agents["market_makers"] = [
            # ExponentialShapedMarketMaker(
            #     wallet_name="MARKET_MAKERS",
            #     key_name=f"MARKET_{str(i_market).zfill(3)}",
            #     price_process_generator=iter(price_process),
            #     initial_asset_mint=self.initial_asset_mint,
            #     market_name=market_name,
            #     asset_name=asset_name,
            #     commitment_amount=1e6,
            #     market_decimal_places=market_config.decimal_places,
            #     asset_decimal_places=asset_dp,
            #     num_steps=self.num_steps,
            #     kappa=2.4,
            #     tick_spacing=0.05,
            #     market_kappa=50,
            #     state_update_freq=10,
            #     tag=f"MARKET_{str(i_market).zfill(3)}",
            # )
            # CFMMarketMaker(
            #     key_name="CFM_MAKER",
            #     num_steps=self.num_steps,
            #     initial_asset_mint=self.initial_asset_mint,
            #     market_name=market_name,
            #     asset_name=asset_name,
            #     commitment_amount=10e6,
            #     market_decimal_places=market_config.decimal_places,
            #     fee_amount=0.001,
            #     k_scaling_large=600e6,
            #     k_scaling_small=5e6,
            #     min_trade_unit=0.01,
            #     initial_price=price_process[0],
            #     num_levels=20,
            #     volume_per_side=100,
            #     tick_spacing=0.5,
            #     asset_decimal_places=asset_dp,
            #     tag="MARKET_CFM",
            #     price_process_generator=iter(price_process),
            # )
            CFMV3MarketMaker(
                key_name="CFM_MAKER",
                num_steps=self.num_steps,
                initial_asset_mint=10_000,
                market_name=market_name,
                asset_name=asset_name,
                commitment_amount=1_000,
                market_decimal_places=market_config.decimal_places,
                fee_amount=0.001,
                initial_price=max(price_process),
                # initial_price=price_process[0],
                num_levels=200,
                tick_spacing=0.1,
                price_width_above=0.2,
                price_width_below=0.2,
                margin_usage_at_bound_above=0,
                margin_usage_at_bound_below=0.8,
                asset_decimal_places=asset_dp,
                price_process_generator=iter(price_process),
                tag="MARKET_CFM",
            )
        ]

        # market_agents["price_sensitive_traders"] = [
        #     PriceSensitiveMarketOrderTrader(
        #         key_name=f"PRICE_SENSITIVE_{str(i_agent).zfill(3)}",
        #         market_name=market_name,
        #         asset_name=asset_name,
        #         price_process_generator=iter(price_process),
        #         initial_asset_mint=self.initial_asset_mint,
        #         buy_intensity=5,
        #         sell_intensity=5,
        #         price_half_life=0.2,
        #         tag=f"SENSITIVE_AGENT_{str(i_agent).zfill(3)}",
        #         random_state=random_state,
        #         base_order_size=0.2,
        #         wallet_name="SENSITIVE_TRADERS",
        #     )
        #     for i_agent in range(6)
        # ]

        market_agents["arb_traders"] = [
            ArbitrageTrader(
                key_name=f"PRICE_SENSITIVE_{str(i_agent).zfill(3)}",
                market_name=market_name,
                asset_name=asset_name,
                price_process_generator=iter(price_process),
                initial_asset_mint=self.initial_asset_mint,
                buy_intensity=100,
                sell_intensity=100,
                spread_offset=0.0001,
                tag=f"ARB_AGENT_{str(i_agent).zfill(3)}",
                random_state=random_state,
                base_order_size=0.1,
                wallet_name="ARB_TRADERS",
            )
            for i_agent in range(2)
        ]

        # market_agents["random_traders"] = [
        #     MarketOrderTrader(
        #         wallet_name="RANDOM_TRADERS",
        #         key_name=(
        #             f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
        #         ),
        #         market_name=market_name,
        #         asset_name=asset_name,
        #         buy_intensity=10,
        #         sell_intensity=10,
        #         base_order_size=0.01,
        #         step_bias=0.5,
        #         tag=f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}",
        #         random_state=random_state,
        #     )
        #     for i_agent in range(20)
        #     # for i_agent in range(1)
        # ]

        # for i_agent in range(1):
        #     market_agents["random_traders"].append(
        #         LimitOrderTrader(
        #             wallet_name=f"RANDOM_TRADERS",
        #             key_name=(
        #                 f"LIMIT_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
        #             ),
        #             market_name=market_name,
        #             asset_name=asset_name,
        #             time_in_force_opts={"TIME_IN_FORCE_GTT": 1},
        #             buy_volume=0.1,
        #             sell_volume=0.1,
        #             buy_intensity=1,
        #             sell_intensity=1,
        #             submit_bias=1,
        #             cancel_bias=0,
        #             duration=120,
        #             price_process=price_process,
        #             spread=0,
        #             mean=-3,
        #             sigma=0.5,
        #             tag=(
        #                 f"MARKET_{str(i_market).zfill(3)}_AGENT_{str(i_agent).zfill(3)}"
        #             ),
        #         )
        #     )

        for _, agent_list in market_agents.items():
            self.agents.extend(agent_list)

        return {agent.name(): agent for agent in self.agents}

    def configure_environment(
        self,
        vega: VegaServiceNull,
        **kwargs,
    ) -> MarketEnvironmentWithState:
        return MarketEnvironmentWithState(
            agents=list(self.agents.values()),
            n_steps=self.num_steps,
            random_agent_ordering=False,
            transactions_per_block=self.transactions_per_block,
            vega_service=vega,
            step_length_seconds=self.step_length_seconds,
            block_length_seconds=vega.seconds_per_block,
            pause_every_n_steps=self.pause_every_n_steps,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

    scenario = CFMScenario(
        num_steps=600,
        step_length_seconds=10,
        block_length_seconds=1,
        transactions_per_block=4096,
        # pause_every_n_steps=100,
    )

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        run_with_console=True,
        use_full_vega_wallet=False,
        retain_log_files=True,
        launch_graphql=False,
        seconds_per_block=scenario.block_length_seconds,
        transactions_per_block=scenario.transactions_per_block,
    ) as vega:
        scenario.run_iteration(
            vega=vega,
            pause_at_completion=False,
            log_every_n_steps=10,
            output_data=True,
        )

    figs = price_comp_plots()
    for i, fig in enumerate(figs.values()):
        fig.savefig(f"./cfm_plots/trading-{i}.jpg")

    account_fig = account_and_margin_plots(
        agent_types=[CFMMarketMaker, CFMV3MarketMaker]
    )
    account_fig.savefig("./cfm_plots/accounts.jpg")
    plt.close(account_fig)

    fig = sla_plot()
    fig.savefig("./cfm_plots/sla.jpg")
    plt.close(fig)
