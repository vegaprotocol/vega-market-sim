"""network_service.py

This module contains functions and classes for the creation of the
VegaServiceNetwork class. A VegaServiceNetwork object can be used to
communicate with either a public or internal Vega network and run a
Vega Wallet service for communication with the chosen Vega network.
The VegaServiceNetwork inherits properties and methods from the VegaService
class. Inherited methods can be used to communicate with the Vega datanode
and Vega wallet services. Redundant properties and methods are overwritten.

A vegawallet executable should either be in PATH whilst executing, or 
the VEGA_WALLET_PATH environment variable set to a location of a wallet.

Similarly, specify VEGA_NETWORK_CONFIG for the path to the network config
of your chosen network

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

import grpc
import toml
import time
import signal
import logging
import tempfile
import itertools
import subprocess
import webbrowser
import multiprocessing
import requests

from typing import Optional

from os import getcwd, path, environ

import vega_sim.grpc.client as vac

from vega_sim import vega_bin_path
from vega_sim.service import VegaService, DatanodeBehindError, DatanodeSlowResponseError
from vega_sim.wallet.base import Wallet
from vega_sim.wallet.vega_wallet import VegaWallet
from vega_sim.null_service import find_free_port, _popen_process

from vega_sim.constants import DATA_NODE_GRPC_PORT
from vega_sim.scenario.constants import Network

logger = logging.getLogger(__name__)


class VegaWalletStartupTimeoutError(Exception):
    pass


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
        raise ValueError("No network config file at the specified path.")

    vega_wallet_path = environ.get("VEGA_WALLET_PATH", "vegawallet")

    args = [
        vega_wallet_path,
        "network",
        "import",
        "--from-file",
        network_config_path,
        "--force",
    ]

    subprocess.call(args=args)


def manage_vega_processes(
    network: str,
    vega_console_path: str,
    vega_console_port: int,
    data_node_query_url: str,
    wallet_url: str,
    run_with_wallet: Optional[bool] = True,
    run_with_console: Optional[bool] = True,
    log_dir: Optional[str] = None,
):
    processes = []

    tmp_vega_dir = tempfile.mkdtemp(prefix="vega-sim-") if log_dir is None else log_dir

    if run_with_wallet:
        vega_wallet_path = environ.get("VEGA_WALLET_PATH", "vegawallet")
        vegaWalletProcess = _popen_process(
            popen_args=[
                vega_wallet_path,
                "service",
                "run",
                "--network",
                network,
                "--automatic-consent",
                "--load-tokens",
                "--tokens-passphrase-file",
                environ.get("VEGA_WALLET_TOKENS_PASSPHRASE_FILE"),
                "--no-version-check",
            ],
            dir_root=tmp_vega_dir,
            log_name="vegawallet",
        )
        processes.append(vegaWalletProcess)

    if run_with_console:
        env_copy = environ.copy()
        env_copy.update(
            {
                "NX_VEGA_URL": data_node_query_url,
                "NX_VEGA_WALLET_URL": wallet_url,
                "NX_VEGA_ENV": "CUSTOM",
                "NX_PORT": f"{vega_console_port}",
            }
        )

        vegaConsoleProcess = _popen_process(
            popen_args=[
                "yarn",
                "--cwd",
                vega_console_path,
                "nx",
                "serve",
                "--port",
                f"{vega_console_port}",
                "-o",
                "trading",
            ],
            dir_root=tmp_vega_dir,
            log_name="console",
            env=env_copy,
        )
        processes.append(vegaConsoleProcess)

    signal.sigwait([signal.SIGKILL, signal.SIGTERM])
    for process in processes:
        process.terminate()
    for process in processes:
        return_code = process.poll()
        if return_code is not None:
            continue
        time.sleep(5)
        process.kill()


def _find_network_config_toml(
    network: Network, config_path: Optional[str] = None
) -> Optional[str]:
    search_paths = (
        [config_path]
        if config_path is not None
        else [
            path.join(
                getcwd(),
                "vega_sim",
                "bin",
                "networks-internal",
                network.name.lower(),
            ),
            path.join(
                getcwd(),
                "vega_sim",
                "bin",
                "networks",
                network.name.lower(),
            ),
        ]
    )
    for search_path in search_paths:
        full_path = path.join(
            search_path,
            f"{network.value}.toml",
        )

        if path.exists(full_path):
            return full_path


class VegaServiceNetwork(VegaService):
    """Class for handling services for communicating with a Vega network."""

    def __init__(
        self,
        network: Network,
        run_with_wallet: bool = True,
        run_with_console: bool = True,
        vega_console_path: Optional[str] = None,
        network_config_path: Optional[str] = None,
        wallet_path: Optional[str] = None,
        vega_home_path: Optional[str] = None,
        wallet_token_path: Optional[str] = None,
    ):
        """Method initialises the class.

        Args:
            network (Network):
                Defines which network to connect service to.
            run_with_wallet (bool, optional):
                Defines whether to start a wallet process.
            run_with_console (bool, optional):
                Defines whether to start a console process.
            vega_console_path (str, optional):
                Path to the directory containing console files if
                wishing to run a local console
            network_config_path (str, optional):
                Path to the directory containing network config files.
                If not passed will search first the environment variable
                VEGA_NETWORK_CONFIG then two default paths.
                Note: Only needed if creating keys
            vega_home_path (str, optional):
                Path to the directory containing wallet binary. Otherwise
                uses VEGA_HOME environment variable.
                Note: Only needed if creating keys
            wallet_token_path (str, optional):
                Path to the json file containing wallet tokens. Otherwise
                uses VEGA_WALLET_TOKENS_FILE environment variable.
        """

        # Run init method inherited from VegaService with network arguments.
        super().__init__(can_control_time=False, warn_on_raw_data_access=False)

        self.network = network
        self.run_with_wallet = run_with_wallet
        self.run_with_console = run_with_console

        self._wallet = None
        self._wallet_url = None
        self._data_node_grpc_url = None
        self._data_node_query_url = None
        self._network_config = None

        self.vega_console_path = (
            vega_console_path
            if vega_console_path is not None
            else path.join(vega_bin_path, "console")
        )
        self._base_network_config_path = (
            network_config_path
            if network_config_path is not None
            else environ.get("VEGA_NETWORK_CONFIG")
        )

        self._wallet_path = (
            wallet_path
            if wallet_path is not None
            else environ.get("VEGA_WALLET_PATH", "vegawallet")
        )

        self._vega_home = (
            vega_home_path if vega_home_path is not None else environ.get("VEGA_HOME")
        )

        self._token_path = (
            wallet_token_path
            if wallet_token_path is not None
            else environ.get("VEGA_WALLET_TOKENS_FILE")
        )
        if self._token_path is None:
            raise Exception(
                "Either path to tokens JSON must be passed to wallet class or"
                " VEGA_WALLET_TOKENS_FILE environment variable set"
            )

        self._network_config_path = _find_network_config_toml(
            network=self.network, config_path=self._base_network_config_path
        )
        if self._network_config_path is None:
            raise ValueError(
                f"ERROR! {self.network.name.lower()} network config could not be found"
            )

        self.log_dir = tempfile.mkdtemp(prefix="vega-sim-")

    def __enter__(self):
        """Defines behaviour when class entered by a with statement."""
        self.start()

        return self

    def __exit__(self, type, value, traceback):
        """Defines behaviour when class exited by a with statement."""
        self.stop()

    def start(self):
        ctx = multiprocessing.get_context()
        vega_console_port = find_free_port()
        self.proc = ctx.Process(
            target=manage_vega_processes,
            kwargs={
                "network": self.network.name.lower(),
                "log_dir": self.log_dir,
                "run_with_wallet": self.run_with_wallet,
                "run_with_console": self.run_with_console,
                "vega_console_path": self.vega_console_path,
                "vega_console_port": vega_console_port,
                "data_node_query_url": self.data_node_query_url,
                "wallet_url": self.wallet_url,
            },
        )
        self.proc.start()

        if self.run_with_console:
            logger.info(
                "Vega Running. Console launched at"
                f" http://localhost:{vega_console_port}"
            )
            webbrowser.open(f"http://localhost:{vega_console_port}/", new=2)

        started = False
        for _ in range(3600):
            try:
                response = requests.get(f"{self.wallet_url}/api/v2/health")
                response.raise_for_status()
                started = True
                break
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
            ):
                time.sleep(0.1)
        if not started:
            raise VegaWalletStartupTimeoutError(
                "Timed out waiting for Vega wallet service"
            )

        self.check_datanode(raise_on_error=False)

    def stop(self) -> None:
        super().stop()
        if self.proc is None:
            logger.info("Stop called but nothing to stop")
        else:
            self.proc.terminate()

    def wait_fn(self, wait_multiple: float = 1) -> None:
        """Overrides redundant parent method."""
        logging.debug(
            "Parent method overridden as VegaNetworkService incapable of controlling"
            " time."
        )

    def wait_for_datanode_sync(self) -> None:
        """Overrides redundant parent method."""
        logging.debug(
            "Parent method overridden as VegaNetworkService incapable of controlling"
            " time."
        )

    def wait_for_core_catchup(self) -> None:
        """Overrides redundant parent method."""
        logging.debug(
            "Parent method overridden as VegaNetworkService incapable of controlling"
            " time."
        )

    def wait_for_total_catchup(self) -> None:
        """Overrides redundant parent method."""
        logging.debug(
            "Parent method overridden as VegaNetworkService incapable of controlling"
            " time."
        )

    @property
    def network_config(self) -> dict:
        if self._network_config is None:
            self._network_config = toml.load(self._network_config_path)
            add_network_config(self._network_config_path)
        return self._network_config

    @property
    def data_node_grpc_url(self) -> str:
        if self._data_node_grpc_url is None:
            url = self.network_config["API"]["GRPC"]["Hosts"][0]
            self._data_node_grpc_url = f"{url.split(':')[0]}:{DATA_NODE_GRPC_PORT}"
        return self._data_node_grpc_url

    @property
    def data_node_query_url(self) -> str:
        if self._data_node_query_url is None:
            url = self.network_config["API"]["GraphQL"]["Hosts"][0]
            self._data_node_query_url = url
        return self._data_node_query_url

    @property
    def wallet_url(self) -> str:
        if self._wallet_url is None:
            self._wallet_url = f"http://127.0.0.1:1789"
        return self._wallet_url

    @property
    def wallet(self) -> Wallet:
        if self._wallet is None:
            self._wallet = VegaWallet.from_json(
                self._token_path,
                self.wallet_url,
                wallet_path=self._wallet_path,
                vega_home_dir=self._vega_home,
            )
        return self._wallet

    @property
    def core_state_client(self) -> None:
        logging.debug(
            (
                "Parent property overridden as VegaNetworkService does not need a core"
                " client."
            ),
        )
        pass

    @property
    def core_client(self) -> None:
        logging.debug(
            (
                "Parent property overridden as VegaNetworkService does not need a core"
                " client."
            ),
        )
        pass

    def check_datanode(
        self, max_time_diff: int = 30, raise_on_error: Optional[bool] = True
    ):
        """Checks if the current data-node connection is healthy.

        If the current data-node connection has timed out or the end-point is
        unresponsive then the service will attempt to establish a connection
        with a new healthy data-node.

        Args:
            max_time_diff (int, optional):
                Maximum allowable difference between system time and datanode time in
                seconds. Defaults to 30.
            raise_on_error (bool, optional):
                Whether to raise an error if data-node connection unhealthy.
        """

        try:
            self.ping_datanode(max_time_diff=max_time_diff)
            logging.debug(
                f"Connection to endpoint {self._data_node_grpc_url} successful."
            )
            return

        except grpc.FutureTimeoutError as e:
            if raise_on_error:
                raise e
            else:
                logging.warning(
                    f"Connection to endpoint {self._data_node_grpc_url} timed out."
                )
                self.switch_datanode()

        except grpc._channel._InactiveRpcError as e:
            if raise_on_error:
                raise e
            else:
                logging.warning(
                    f"Connection to endpoint {self._data_node_grpc_url} inactive."
                )
                self.switch_datanode()

        except DatanodeBehindError as e:
            if raise_on_error:
                raise e
            else:
                logging.warning(
                    f"Connection to endpoint {self._data_node_grpc_url} is behind."
                )
                self.switch_datanode()

        except DatanodeSlowResponseError as e:
            if raise_on_error:
                raise e
            else:
                logging.warning(
                    f"Connection to endpoint {self._data_node_grpc_url} is slow."
                )
                self.switch_datanode()

    def switch_datanode(self, max_attempts: Optional[int] = -1):
        """Attempts to establish a new data-node connection.

        Args:
            max_attempts (int, optional):
                Maximum number of connection attempts to attempt before raising an
                error. Defaults to -1 (infinite attempts).
        """

        attempts = 0
        for url in itertools.cycle(self.network_config["API"]["GRPC"]["Hosts"]):
            attempts += 1

            try:
                self._data_node_grpc_url = f"{url.split(':')[0]}:{DATA_NODE_GRPC_PORT}"

                logging.debug(f"Switched to endpoint {self._data_node_grpc_url}")

                channel = grpc.insecure_channel(
                    self.data_node_grpc_url,
                    options=(
                        ("grpc.enable_http_proxy", 0),
                        ("grpc.max_send_message_length", 1024 * 1024 * 20),
                        ("grpc.max_receive_message_length", 1024 * 1024 * 20),
                    ),
                )
                grpc.channel_ready_future(channel).result(timeout=30)
                self._trading_data_client_v2 = vac.VegaTradingDataClientV2(
                    self.data_node_grpc_url,
                    channel=channel,
                )

                # Ping the datanode to check it is not behind
                self.ping_datanode()
                logging.debug(
                    f"Connection to endpoint {self._data_node_grpc_url} successful."
                )

                return

            except grpc._channel._InactiveRpcError:
                logging.warning(
                    f"Connection to endpoint {self._data_node_grpc_url} inactive."
                )

            except grpc.FutureTimeoutError:
                logging.warning(
                    f"Connection to endpoint {self._data_node_grpc_url} timed out."
                )

            except DatanodeBehindError:
                logging.warning(
                    f"Connection to endpoint {self._data_node_grpc_url} is behind."
                )

            except DatanodeSlowResponseError:
                logging.warning(
                    f"Connection to endpoint {self._data_node_grpc_url} is slow."
                )

            if attempts == max_attempts:
                break

        raise Exception("Unable to establish connection to a data-node.")


if __name__ == "__main__":
    """Module Example"""

    log = logging.basicConfig(level=logging.INFO)

    # Create a service connected to the fairground network.
    with VegaServiceNetwork(
        network=Network.FAIRGROUND,
        run_with_wallet=True,
        run_with_console=True,
    ) as vega:
        # Show all the markets on the network
        markets = vega.all_markets()
        logging.info(markets)

        # Show data for a specific market
        market = vega.get_latest_market_data(market_id=markets[0].id)

    # Create a service connected to the stagnet3 network.
    with VegaServiceNetwork(
        network=Network.FAIRGROUND,
        run_with_wallet=True,
        run_with_console=True,
    ) as vega:
        # Show all the markets on the network
        markets = vega.all_markets()
        logging.info(markets)

        # Show data for a specific market
        market = vega.get_latest_market_data(market_id=markets[0].id)
