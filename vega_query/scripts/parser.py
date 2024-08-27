import datetime

from argparse import ArgumentParser

PARSER = ArgumentParser()

general_options = PARSER.add_argument_group("General options")
general_options.add_argument(
    "-n",
    "--network",
    required=True,
    type=str,
    help="Specify network to request data from.",
)
general_options.add_argument(
    "-m",
    "--market",
    default=True,
    type=str,
    help="Specify market to request data for.",
)
general_options.add_argument(
    "--port",
    required=False,
    type=str,
    help="Specify path to network config file (only required when network local).",
)
general_options.add_argument(
    "--config",
    required=False,
    type=str,
    help="Specify path to network config file (only required when network unspecified).",
)
general_options.add_argument(
    "-p",
    "--pages",
    required=False,
    default=None,
    type=int,
    help="Specify maximum number of pages service requests can return.",
)
general_options.add_argument(
    "--start-time",
    type=datetime.datetime.fromisoformat,
    help="Specify datetime to retrieve data from (format: YYYY-MM-DD:HH:mm:ss).",
)
general_options.add_argument(
    "--end-time",
    type=datetime.datetime.fromisoformat,
    help="Specify datetime to retrieve data to (format: YYYY-MM-DD:HH:mm:ss).",
)

output_options = PARSER.add_argument_group("Output options")
output_options.add_argument("--debug", action="store_true", help="Enables debug mode.")
output_options.add_argument(
    "--show", action="store_true", help="Shows plot at end of script."
)
output_options.add_argument(
    "--save", action="store_true", help="Saves plot at end of script."
)


if __name__ == "__main__":
    args = PARSER.parse_args()
    print(args)
