import argparse
import logging

from vega_sim.null_service import VegaServiceNull


def replay_run(
    replay_path: str,
    console: bool = False,
    graphql: bool = False,
    pause_at_end: bool = False,
    retain_log_files: bool = False,
):
    with VegaServiceNull(
        launch_graphql=graphql,
        run_with_console=console,
        replay_from_path=replay_path,
        retain_log_files=retain_log_files,
    ) as vega:
        vega.wait_for_total_catchup()

        if pause_at_end:
            input("Pausing at completion. Press Return to continue")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--console", action="store_true")
    parser.add_argument("--graphql", action="store_true")
    parser.add_argument("--pause", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--retain_log_files", action="store_true")

    parser.add_argument(
        "--dir",
        default="",
        type=str,
        help="The vega-sim log dir containing the replay log",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    replay_run(
        replay_path=args.dir,
        console=args.console,
        graphql=args.graphql,
        pause_at_end=args.pause,
        retain_log_files=args.retain_log_files,
    )
