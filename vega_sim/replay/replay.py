import argparse
import logging
import time
from contextlib import contextmanager

import vega_sim.proto.vega.api.v1.core_pb2 as core_proto
from vega_sim.api.faucet import mint
from vega_sim.null_service import VegaServiceNull
from vega_sim.wallet.slim_wallet import TRANSACTION_LEN_BYTES, TransactionType


@contextmanager
def replay_run_context(
    replay_path: str,
    console: bool = False,
    graphql: bool = False,
):
    with open(f"{replay_path}/replay/transactions", "rb") as tx_history:
        tx_per_block = int.from_bytes(tx_history.read(TRANSACTION_LEN_BYTES), "big")
        with VegaServiceNull(
            launch_graphql=graphql,
            run_with_console=console,
            transactions_per_block=tx_per_block,
            warn_on_raw_data_access=False,
            store_transactions=True,
            retain_log_files=True,
        ) as vega:
            vega.wait_for_total_catchup()
            next_tx_type = tx_history.read(TRANSACTION_LEN_BYTES)

            while next_tx_type:
                time.sleep(0.001)
                vega.wait_for_total_catchup()
                tx_type = TransactionType._value2member_map_[
                    int.from_bytes(next_tx_type, "big")
                ]
                if tx_type == TransactionType.TX:
                    tx_len = tx_history.read(TRANSACTION_LEN_BYTES)
                    int_len = int.from_bytes(tx_len, "big")
                    tx = tx_history.read(int_len)
                    transaction = core_proto.SubmitTransactionRequest()
                    transaction.ParseFromString(tx)
                    vega.wallet.submit_raw_transaction(transaction)

                elif tx_type == TransactionType.STEP:
                    steps = tx_history.read(TRANSACTION_LEN_BYTES)
                    vega.wait_fn(int.from_bytes(steps, "big"))

                elif tx_type == TransactionType.MINT:
                    pub_key_len = int.from_bytes(
                        tx_history.read(TRANSACTION_LEN_BYTES), "big"
                    )
                    asset_len = int.from_bytes(
                        tx_history.read(TRANSACTION_LEN_BYTES), "big"
                    )
                    pub_key = tx_history.read(pub_key_len).decode("utf-8")
                    asset = tx_history.read(asset_len).decode("utf-8")
                    amount = int.from_bytes(
                        tx_history.read(TRANSACTION_LEN_BYTES), "big"
                    )
                    mint(
                        pub_key,
                        asset,
                        amount,
                        faucet_url=vega.faucet_url,
                    )
                next_tx_type = tx_history.read(TRANSACTION_LEN_BYTES)
            yield vega


def replay_run(
    replay_path: str,
    console: bool = False,
    graphql: bool = False,
    pause_at_end: bool = False,
):
    with replay_run_context(
        replay_path=replay_path, console=console, graphql=graphql
    ) as vega:
        if pause_at_end:
            input("Pausing at completion. Press Return to continue")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--console", action="store_true")
    parser.add_argument("--graphql", action="store_true")
    parser.add_argument("--pause", action="store_true")

    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    replay = "/var/folders/yj/cjhtlxn90wldd1hvw5lkxnrc0000gn/T/vega-sim-wxrt33vu"
    replay_run(
        replay_path=replay,
        console=args.console,
        graphql=args.graphql,
        pause_at_end=args.pause,
    )
