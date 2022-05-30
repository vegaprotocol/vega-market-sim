import argparse
import logging
from multiprocessing import Pool
import datetime
from typing import List, Optional

from examples.agent_market.agents import (
    MM_WALLET,
    TERMINATE_WALLET,
    TRADER_WALLET,
    MarketMaker,
    MarketOrderTraders,
    random_walk_price,
)
from vega_sim.environment import MarketEnvironmentWithState
from vega_sim.null_service import VegaServiceNull


def main(
    num_steps: int = 60,
    block_size: int = 1,
    run_with_console: bool = False,
    pause_at_completion: bool = False,
    order_arrival_rate: float = 2,
    vega: Optional[VegaServiceNull] = None,
):
    market_maker = MarketMaker(
        wallet_name=MM_WALLET.name,
        wallet_pass=MM_WALLET.passphrase,
        terminate_wallet_name=TERMINATE_WALLET.name,
        terminate_wallet_pass=TERMINATE_WALLET.passphrase,
        price_process=random_walk_price(
            terminal_time_seconds=num_steps + 10, sigma=0.1, initial_price=100
        ),
    )
    mo_traders = MarketOrderTraders(
        wallet_name=TRADER_WALLET.name,
        wallet_pass=TRADER_WALLET.passphrase,
        buy_order_arrival_rate=order_arrival_rate,
    )
    env = MarketEnvironmentWithState(
        agents=[market_maker, mo_traders],
        n_steps=num_steps,
        transactions_per_block=block_size,
        vega_service=vega,
    )
    env.run(run_with_console=run_with_console, pause_at_completion=pause_at_completion)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num-procs", default=1, type=int)
    args = parser.parse_args()

    if args.num_procs > 1:
        ress = []
        vega_services: List[VegaServiceNull] = []
        with Pool(args.num_procs) as p:
            start = datetime.datetime.now()
            for _ in range(args.num_procs):
                vega_service = VegaServiceNull(warn_on_raw_data_access=False)
                vega_service.start(block_on_startup=True)
                vega_services.append(vega_service)
                ress.append(
                    p.apply_async(
                        main,
                        kwds={
                            "num_steps": int(1 * 60 * 60 * 1),
                            "block_size": 10,
                            "pause_at_completion": False,
                            "run_with_console": False,
                            "vega": vega_service.clone(),
                        },
                    )
                )

            [res.get() for res in ress]
            print(f"Run took {(datetime.datetime.now() - start).seconds}s")
            for vega_service in vega_services:
                vega_service.stop()
    else:
        with VegaServiceNull(warn_on_raw_data_access=False) as vega:
            main(
                **{
                    "num_steps": int(1 * 60 * 60 * 1),
                    "block_size": 10,
                    "pause_at_completion": False,
                    "run_with_console": False,
                    "vega": vega,
                },
            )
