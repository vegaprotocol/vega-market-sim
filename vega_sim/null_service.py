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

from vega_sim import vega_home_path, vega_bin_path
from vega_sim.constants import (
    DATA_NODE_GRPC_PORT,
    DATA_NODE_REST_PORT,
    FAUCET_PORT,
    WALLET_DEFAULT_PORT,
    VEGA_NODE_PORT,
)
from vega_sim.service import VegaService

logger = logging.getLogger(__name__)


def _popen_process(
    popen_args: List[str], dir_root: str, log_name: str
) -> subprocess.Popen[bytes]:
    with open(path.join(dir_root, f"{log_name}.out"), "wb") as out, open(
        path.join(dir_root, f"{log_name}.err"), "wb"
    ) as err:
        sub_proc = subprocess.Popen(popen_args, stdout=out, stderr=err)
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
        print(tmp_vega_dir)
        logger.debug(f"Running NullChain from vegahome of {tmp_vega_dir}")
        shutil.copytree(vega_home_path, f"{tmp_vega_dir}/vegahome")

        tmp_vega_home = tmp_vega_dir + "/vegahome"
        _update_node_config(tmp_vega_home)

        dataNodeProcess = _popen_process(
            [data_node_path, "node", "--home=" + tmp_vega_home],
            dir_root=tmp_vega_dir,
            log_name="data_node",
        )

        vegaFaucetProcess = _popen_process(
            [
                vega_path,
                "faucet",
                "run",
                "--passphrase-file=" + tmp_vega_home + "/passphrase-file",
                "--home=" + tmp_vega_home,
            ],
            dir_root=tmp_vega_dir,
            log_name="faucet",
        )
        vegaNodeProcess = _popen_process(
            [
                vega_path,
                "node",
                "--nodewallet-passphrase-file=" + tmp_vega_home + "/passphrase-file",
                "--home=" + tmp_vega_home,
            ],
            dir_root=tmp_vega_dir,
            log_name="node",
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

        vegaWalletProcess = _popen_process(
            wallet_args,
            dir_root=tmp_vega_dir,
            log_name="vegawallet",
        )

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
        super().__init__(can_control_time=True)
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
    def _build_url(port: int, prefix: str = "http://"):
        return f"{prefix}localhost:{port}"

    def _default_wait_fn(self) -> None:
        self.forward("2s")

    def stop(self) -> None:
        if self.proc is None:
            logger.info("Stop called but nothing to stop")
        else:
            self.proc.terminate()

    def wallet_url(self) -> str:
        return self._build_url(self.wallet_port)

    def data_node_rest_url(self) -> str:
        return self._build_url(self.data_node_rest_port)

    def data_node_grpc_url(self) -> str:
        return self._build_url(self.data_node_grpc_port, prefix="")

    def faucet_url(self) -> str:
        return self._build_url(self.faucet_port)

    def vega_node_url(self) -> str:
        return self._build_url(self.vega_node_port)
