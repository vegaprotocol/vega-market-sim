import atexit
import logging
import shutil
import signal
import subprocess
import tempfile
import time
from multiprocessing import Process
from os import path
from typing import List, Optional

import requests
import toml
from urllib3.exceptions import MaxRetryError

# import vegaapiclient as vac

import vega_sim.constants as constants
from vega_sim import vega_home_path, vega_bin_path
from vega_sim.api.test_fns import propose_market
from vega_sim.constants import (
    DATA_NODE_GRPC_PORT,
    DATA_NODE_REST_PORT,
    FAUCET_PORT,
    WALLET_DEFAULT_PORT,
    VEGA_NODE_PORT,
)
from vega_sim.service import VegaService

logger = logging.getLogger(__name__)


def _popen_process(popen_args: List[str]) -> subprocess.Popen[bytes]:
    sub_proc = subprocess.Popen(popen_args)
    atexit.register(lambda: sub_proc.terminate())
    return sub_proc


def _update_node_config(vega_home: str) -> None:
    config_path = path.join(vega_home, "config", "node", "config.toml")
    config_toml = toml.load(config_path)
    config_toml["Blockchain"]["Null"]["GenesisFile"] = path.join(
        vega_home, "genesis.json"
    )

    with open(config_path, "w") as f:
        toml.dump(config_toml, f)


def manage_vega_processes(
    vega_path: str,
    data_node_path: str,
    vega_wallet_path: str,
    run_wallet_with_console: bool = False,
    run_wallet_with_token_dapp: bool = False,
) -> None:
    with tempfile.TemporaryDirectory() as tmp_vega_dir:

        shutil.copytree(vega_home_path, f"{tmp_vega_dir}/vegahome")

        tmp_vega_home = tmp_vega_dir + "/vegahome"
        _update_node_config(tmp_vega_home)

        dataNodeProcess = _popen_process(
            [
                data_node_path,
                "node",
                "--home=" + tmp_vega_home,
            ]
        )

        vegaFaucetProcess = _popen_process(
            [
                vega_path,
                "faucet",
                "run",
                "--passphrase-file=" + tmp_vega_home + "/passphrase-file",
                "--home=" + tmp_vega_home,
            ]
        )
        vegaNodeProcess = _popen_process(
            [
                vega_path,
                "node",
                "--nodewallet-passphrase-file=" + tmp_vega_home + "/passphrase-file",
                "--home=" + tmp_vega_home,
            ]
        )

        wallet_args = [
            vega_wallet_path,
            "service",
            "run",
            "--network",
            "local",
            "--home=" + tmp_vega_home,
            "--automatic-consent",
        ]
        if run_wallet_with_console:
            wallet_args += ["--with-console"]
        if run_wallet_with_token_dapp:
            wallet_args += ["--with-token-dapp"]
        if run_wallet_with_token_dapp or run_wallet_with_console:
            wallet_args += ["--no-browser"]

        vegaWalletProcess = _popen_process(wallet_args)

        signal.sigwait([signal.SIGKILL, signal.SIGTERM])
        processes = [
            dataNodeProcess,
            vegaFaucetProcess,
            vegaWalletProcess,
            vegaNodeProcess,
        ]
        for process in processes:
            process.terminate()
        for process in processes:
            return_code = process.poll()
            if return_code is not None:
                continue
            # Could mean 5s wait per process, but we're not holding the outer process
            # and would really be a symptom of these children taking too long to close
            time.sleep(5)
            process.kill()


class VegaStartupTimeoutError(Exception):
    pass


class ServiceNotStartedError(Exception):
    pass


class VegaServiceNull(VegaService):
    def __init__(
        self,
        vega_path: Optional[str] = None,
        data_node_path: Optional[str] = None,
        vega_wallet_path: Optional[str] = None,
        wallet_port: int = WALLET_DEFAULT_PORT,
        data_node_rest_port: int = DATA_NODE_REST_PORT,
        data_node_grpc_port: int = DATA_NODE_GRPC_PORT,
        vega_node_port: int = VEGA_NODE_PORT,
        faucet_port: Optional[int] = FAUCET_PORT,
        start_immediately: bool = False,
        run_wallet_with_console: bool = False,
        run_wallet_with_token_dapp: bool = False,
    ):
        super().__init__()
        self.vega_path = vega_path or path.join(vega_bin_path, "vega")
        self.data_node_path = data_node_path or path.join(vega_bin_path, "data-node")
        self.vega_wallet_path = vega_wallet_path or path.join(
            vega_bin_path, "vegawallet"
        )
        self.wallet_port = wallet_port
        self.data_node_rest_port = data_node_rest_port
        self.data_node_grpc_port = data_node_grpc_port
        self.faucet_port = faucet_port
        self.vega_node_port = vega_node_port
        self.proc = None
        self.run_wallet_with_console = run_wallet_with_console
        self.run_wallet_with_token_dapp = run_wallet_with_token_dapp

        if start_immediately:
            self.start()
        # self.core_client = vac.VegaCoreClient(self.data_node_grpc_port)

    def _check_started(self) -> None:
        if self.proc is None:
            raise ServiceNotStartedError("NullChain Vega accessed without starting")

    def start(self) -> None:
        self.proc = Process(
            target=manage_vega_processes,
            kwargs={
                "vega_path": self.vega_path,
                "data_node_path": self.data_node_path,
                "vega_wallet_path": self.vega_wallet_path,
                "run_wallet_with_token_dapp": self.run_wallet_with_token_dapp,
                "run_wallet_with_console": self.run_wallet_with_console,
            },
            daemon=True,
        )
        self.proc.start()
        # Wait for startup
        for _ in range(300):
            try:
                requests.get(
                    f"http://localhost:{self.wallet_port}/api/v1/status"
                ).raise_for_status()
                return
            except (
                MaxRetryError,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
            ):
                time.sleep(0.5)
        raise VegaStartupTimeoutError(
            "Timed out waiting for Vega simulator to start up"
        )

    # Class internal as at some point the host may vary as well as the port
    @staticmethod
    def _build_url(port: int):
        return f"http://localhost:{port}"

    def stop(self) -> None:
        if self.proc is None:
            logger.info("Stop called but nothing to stop")
        else:
            self.proc.terminate()

    def propose_market(self):
        self._check_started()
        propose_market(
            wallet_name=constants.WALLET_NAME_MM,
            wallet_passphrase=constants.WALLET_PASSPHRASE_MM,
            pubkey=constants.PUBKEY_LP,
            node_url_rest=self.data_node_rest_url(),
            wallet_server_url=self.wallet_url(),
        )

    def wallet_url(self) -> str:
        return self._build_url(self.wallet_port)

    def data_node_rest_url(self) -> str:
        return self._build_url(self.data_node_rest_port)

    def faucet_url(self) -> str:
        return self._build_url(self.faucet_port)

    def vega_node_url(self) -> str:
        return self._build_url(self.vega_node_port)
