"""network_service.py

This module contains functions and classes for the creation of the
VegaServiceNetwork class. A VegaServiceNetwork object can be used to
communicate with either a public or internal Vega network and run a
Vega Wallet service for communication with the chosen Vega network.
The VegaServiceNetwork inherits properties and methods from the VegaService
class. Inherited methods can be used to communicate with the Vega datanode
and Vega wallet services. Redundant properties and methods are overwritten.
Example:

    For an example, try running the below command. It will create a
    VegaServiceNetwork object, the relevant services and try sending some
    commands.

        $ python -m vega_sim.network_service

    If the above example is throwing errors, check you have cloned the
    required bin folders with the following command.

        $ make networks

Todo:
    • Test all public and internal Vega networks are compatible.
    • Test all market sim agents are compatible.
"""

import subprocess
import logging
import toml

from os import getcwd, path

from vega_sim.service import VegaService
from vega_sim.wallet.base import Wallet
from vega_sim.wallet.vega_wallet import VegaWallet

from vega_sim.constants import DATA_NODE_GRPC_PORT


def start_wallet_service(
    network: str,
    automatic_consent: bool = True,
    no_version_check: bool = False,
) -> subprocess.Popen:
    """Starts a subprocess running a wallet service connected to a network.
    Function uses the local install of vega wallet to start a wallet service
    connected to the specified network. By default the automatic-consent flag
    is enabled and the no-version-check flag is disabled.

    Args:
        network (str):
            Name of the network config file to use to run the service.
        automatic_consent (bool, optional):
            Run the service with the --automatic-consent flag. Default is True.
        no_version_check (bool, optional):
            Run the service with the --no_version_check flag. Default is False.
    Returns:

        process (subprocess.Popen):

            A process running the wallet service which can be killed.
    """

    args = [
        "vega",
        "wallet",
        "service",
        "run",
        "--network",
        network,
    ]

    if automatic_consent:
        args.append("--automatic-consent")
    if no_version_check:
        args.append("--no-version-check")

    process = subprocess.Popen(args=args)

    return process


def add_network_config(
    network_config_path: str,
):
    """Creates a network config file for the specified network.
    Method creates a copy of the config file specified in the local vega path
    networks folder. This config file is used to run a wallet service.

    Args:
        network_config_path (str):
            Path to the network config file to create a local network from.

    Raises:
        ValueError:
            If no file exists at the specified path.
    """

    if not path.exists(network_config_path):
        raise ValueError(f"No network config file at the specified path.")

    args = [
        "vega",
        "wallet",
        "network",
        "import",
        "--from-file",
        network_config_path,
        "--force",
    ]

    subprocess.call(args=args)


class VegaServiceNetwork(VegaService):
    """Class for handling services for communicating with a Vega network."""

    def __init__(
        self,
        network: str,
        automatic_consent: bool = True,
        no_version_check: bool = False,
    ):
        """Method initialises the class.

        Args:

            network (str):
                Defines which network to connect service to.
            automatic_consent (bool, optional):
                Whether to run the vega wallet service with the
                --automatic-consent flag. Default value is True.
            no_version_check (bool, optional):
                Whether to run the vega wallet service with the
                --automatic-consent flag. Default value is False.
        """

        # Run init method inherited from VegaService with network arguments.
        super().__init__(can_control_time=False, warn_on_raw_data_access=False)

        self.network = network
        self.automatic_consent = automatic_consent
        self.no_version_check = no_version_check

        self._wallet = None
        self._wallet_url = None
        self._data_node_grpc_url = None
        self._network_config = None

    def __enter__(self):
        """Defines behaviour when class entered by a with statement.
        Special attributes starts the process running the wallet service.
        """
        self.process = start_wallet_service(
            self.network, self.automatic_consent, self.no_version_check
        )
        return self

    def __exit__(self, type, value, traceback):
        """Defines behaviour when class exited by a with statement.
        Special attribute kills the process running the wallet service.
        """
        self.process.kill()

    def wait_fn(self, wait_multiple: float = 1) -> None:
        """Overrides redundant parent method."""
        logging.debug(
            "Parent method overridden as VegaNetworkService incapable of controlling time."
        )

    def wait_for_datanode_sync(self) -> None:
        """Overrides redundant parent method."""
        logging.debug(
            "Parent method overridden as VegaNetworkService incapable of controlling time."
        )

    def wait_for_core_catchup(self) -> None:
        """Overrides redundant parent method."""
        logging.debug(
            "Parent method overridden as VegaNetworkService incapable of controlling time."
        )

    def wait_for_total_catchup(self) -> None:
        """Overrides redundant parent method."""
        logging.debug(
            "Parent method overridden as VegaNetworkService incapable of controlling time."
        )

    @property
    def network_config(self) -> dict:
        if self._network_config is None:

            public_path = path.join(
                getcwd(),
                "vega_sim",
                "bin",
                "networks-internal",
                self.network,
                f"{self.network}.toml",
            )
            internal_path = path.join(
                getcwd(),
                "vega_sim",
                "bin",
                "networks",
                self.network,
                f"{self.network}.toml",
            )

            if path.exists(public_path):
                self._network_config = toml.load(public_path)
                add_network_config(public_path)

            elif path.exists(internal_path):
                self._network_config = toml.load(internal_path)
                add_network_config(internal_path)

            else:
                raise ValueError(f"ERROR! {self.network} network does not exist")

        return self._network_config

    @property
    def data_node_grpc_url(self) -> str:
        if self._data_node_grpc_url is None:
            url = self.network_config["API"]["GRPC"]["Hosts"][1]
            self._data_node_grpc_url = f"{url.split(':')[0]}:{DATA_NODE_GRPC_PORT}"
        return self._data_node_grpc_url

    @property
    def wallet_url(self) -> str:
        if self._wallet_url is None:
            self._wallet_url = (
                f"http://{self.network_config['Host']}:{self.network_config['Port']}"
            )
        return self._wallet_url

    @property
    def wallet(self) -> Wallet:
        if self._wallet is None:
            self._wallet = VegaWallet(self.wallet_url)
        return self._wallet

    @property
    def core_state_client(self) -> None:
        logging.debug(
            "Parent property overridden as VegaNetworkService does not need a core client.",
        )
        pass

    @property
    def core_client(self) -> None:
        logging.debug(
            "Parent property overridden as VegaNetworkService does not need a core client.",
        )
        pass


if __name__ == "__main__":
    """Module Example"""

    log = logging.basicConfig(level=logging.INFO)

    # Create a service connected to the fairground network.
    with VegaServiceNetwork(
        network="fairground",
        automatic_consent=True,
        no_version_check=True,
    ) as vega:

        # Show all the markets on the network
        markets = vega.all_markets()
        logging.info(markets)

        # Show data for a specific market
        market = vega.market_data(market_id=markets[0].id)

    # Create a service connected to the stagnet3 network.
    with VegaServiceNetwork(
        network="stagnet3",
        automatic_consent=True,
        no_version_check=True,
    ) as vega:

        # Show all the markets on the network
        markets = vega.all_markets()
        logging.info(markets)

        # Show data for a specific market
        market = vega.market_data(market_id=markets[0].id)
