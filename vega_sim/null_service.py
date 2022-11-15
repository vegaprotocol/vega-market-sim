from __future__ import annotations

import atexit
import functools
from io import BufferedWriter
import logging
import multiprocessing
from optparse import Option
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import webbrowser
from collections import namedtuple
from contextlib import closing
from enum import Enum, auto
from os import path
from typing import Dict, List, Optional, Set

import requests
import toml
from urllib3.exceptions import MaxRetryError

from vega_sim import vega_bin_path, vega_home_path
from vega_sim.api.helpers import num_to_padded_int
from vega_sim.service import VegaService
from vega_sim.wallet.base import Wallet
from vega_sim.wallet.slim_wallet import (
    SlimWallet,
)
from vega_sim.wallet.vega_wallet import VegaWallet

logger = logging.getLogger(__name__)

PortUpdateConfig = namedtuple(
    "PortUpdateConfig", ["file_path", "config_path", "key", "val_func"]
)


class Ports(Enum):
    DATA_NODE_GRPC = auto()
    DATA_NODE_REST = auto()
    DATA_NODE_GRAPHQL = auto()
    DATA_NODE_POSTGRES = auto()
    FAUCET = auto()
    WALLET = auto()
    VEGA_NODE = auto()
    CORE_GRPC = auto()
    CORE_REST = auto()
    BROKER = auto()
    METRICS = auto()
    PPROF = auto()
    CONSOLE = auto()


PORT_UPDATERS = {
    Ports.DATA_NODE_GRPC: [
        PortUpdateConfig(
            ("config", "data-node", "config.toml"),
            ["API"],
            "Port",
            lambda port: port,
        ),
        PortUpdateConfig(
            ("config", "data-node", "config.toml"),
            ["Gateway", "Node"],
            "Port",
            lambda port: port,
        ),
        PortUpdateConfig(
            ("config", "wallet-service", "networks", "local.toml"),
            ["API", "GRPC"],
            "Hosts",
            lambda port: [f"localhost:{port}"],
        ),
    ],
    Ports.DATA_NODE_REST: [
        PortUpdateConfig(
            ("config", "data-node", "config.toml"),
            ["Gateway", "REST"],
            "Port",
            lambda port: port,
        ),
        PortUpdateConfig(
            ("config", "wallet-service", "networks", "local.toml"),
            ["API", "REST"],
            "Hosts",
            lambda port: [f"localhost:{port}"],
        ),
    ],
    Ports.DATA_NODE_POSTGRES: [
        PortUpdateConfig(
            ("config", "data-node", "config.toml"),
            ["SQLStore", "ConnectionConfig"],
            "Port",
            lambda port: port,
        ),
    ],
    Ports.FAUCET: [
        PortUpdateConfig(
            ("config", "faucet", "config.toml"), [], "Port", lambda port: port
        ),
    ],
    Ports.WALLET: [
        PortUpdateConfig(
            ("config", "wallet-service", "networks", "local.toml"),
            [],
            "Port",
            lambda port: port,
        ),
    ],
    Ports.VEGA_NODE: [
        PortUpdateConfig(
            ("config", "node", "config.toml"),
            ["Blockchain", "Null"],
            "Port",
            lambda port: port,
        ),
    ],
    Ports.DATA_NODE_GRAPHQL: [
        PortUpdateConfig(
            ("config", "data-node", "config.toml"),
            ["Gateway", "GraphQL"],
            "Port",
            lambda port: port,
        ),
        PortUpdateConfig(
            ("config", "wallet-service", "networks", "local.toml"),
            ["API", "GraphQL"],
            "Hosts",
            lambda port: [f"localhost:{port}"],
        ),
    ],
    Ports.CORE_GRPC: [
        PortUpdateConfig(
            ("config", "faucet", "config.toml"),
            ["Node"],
            "Port",
            lambda port: port,
        ),
        PortUpdateConfig(
            ("config", "node", "config.toml"),
            ["API"],
            "Port",
            lambda port: port,
        ),
        PortUpdateConfig(
            ("config", "data-node", "config.toml"),
            ["API"],
            "CoreNodeGRPCPort",
            lambda port: port,
        ),
    ],
    Ports.CORE_REST: [
        PortUpdateConfig(
            ("config", "node", "config.toml"),
            ["API", "REST"],
            "Port",
            lambda port: port,
        ),
    ],
    Ports.BROKER: [
        PortUpdateConfig(
            ("config", "data-node", "config.toml"),
            ["Broker", "SocketConfig"],
            "Port",
            lambda port: port,
        ),
        PortUpdateConfig(
            ("config", "node", "config.toml"),
            ["Broker", "Socket"],
            "Port",
            lambda port: port,
        ),
    ],
    Ports.METRICS: [
        PortUpdateConfig(
            ("config", "data-node", "config.toml"),
            ["Metrics"],
            "Port",
            lambda port: port,
        ),
        PortUpdateConfig(
            ("config", "node", "config.toml"),
            ["Metrics"],
            "Port",
            lambda port: port,
        ),
    ],
    Ports.PPROF: [
        PortUpdateConfig(
            ("config", "data-node", "config.toml"),
            ["Pprof"],
            "Port",
            lambda port: port,
        ),
        PortUpdateConfig(
            ("config", "node", "config.toml"),
            ["Pprof"],
            "Port",
            lambda port: port,
        ),
    ],
    Ports.CONSOLE: [
        PortUpdateConfig(
            ("config", "wallet-service", "networks", "local.toml"),
            ["Console"],
            "LocalPort",
            lambda port: port,
        ),
    ],
}


class VegaStartupTimeoutError(Exception):
    pass


class ServiceNotStartedError(Exception):
    pass


class SocketNotFoundError(Exception):
    pass


def find_free_port(existing_set: Optional[Set[int]] = None):
    ret_sock = 0
    existing_set = (
        existing_set.union(set([ret_sock]))
        if existing_set is not None
        else set([ret_sock])
    )

    num_tries = 0
    while ret_sock in existing_set:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(("", 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            ret_sock = s.getsockname()[1]

        num_tries += 1
        if num_tries >= 100:
            # Arbitrary high number. If we try 100 times and fail to find
            # a port it seems reasonable to give up
            raise SocketNotFoundError("Failed finding a free socket")

    return ret_sock


def _terminate_proc(
    proc: subprocess.Popen[bytes], out_file: BufferedWriter, err_file: BufferedWriter
) -> None:
    proc.terminate()
    out_file.close()
    err_file.close()


def _popen_process(
    popen_args: List[str],
    dir_root: str,
    log_name: str,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.Popen[bytes]:
    out = open(path.join(dir_root, f"{log_name}.out"), "wb")
    err = open(path.join(dir_root, f"{log_name}.err"), "wb")
    sub_proc = subprocess.Popen(
        popen_args, stdout=out, stderr=err, env=env, close_fds=True
    )

    atexit.register(functools.partial(_terminate_proc, sub_proc, out, err))
    return sub_proc


def _update_node_config(
    vega_home: str,
    port_config: Dict[Ports, int],
    transactions_per_block: int = 1,
    block_duration: str = "1s",
) -> None:
    config_path = path.join(vega_home, "config", "node", "config.toml")
    config_toml = toml.load(config_path)
    config_toml["Blockchain"]["Null"]["GenesisFile"] = path.join(
        vega_home, "genesis.json"
    )
    config_toml["Blockchain"]["Null"]["BlockDuration"] = block_duration
    config_toml["Blockchain"]["Null"]["TransactionsPerBlock"] = transactions_per_block

    existing_ports = set(port_config.values())
    for port in Ports:
        if port in port_config:
            continue
        new_port = find_free_port(existing_ports)
        existing_ports.add(new_port)
        port_config[port] = new_port

    with open(config_path, "w") as f:
        toml.dump(config_toml, f)

    for port_key, update_configs in PORT_UPDATERS.items():
        for config in update_configs:
            file_path = path.join(vega_home, *config.file_path)
            config_toml = toml.load(file_path)
            elem = config_toml
            for k in config.config_path:
                elem = elem[k]
            elem[config.key] = config.val_func(port_config[port_key])

            with open(file_path, "w") as f:
                toml.dump(config_toml, f)


def manage_vega_processes(
    vega_path: str,
    data_node_path: str,
    vega_wallet_path: str,
    vega_console_path: Optional[str] = None,
    run_with_console: bool = False,
    port_config: Optional[Dict[Ports, int]] = None,
    transactions_per_block: int = 1,
    block_duration: str = "1s",
    run_wallet: bool = False,
    retain_log_files: bool = False,
    log_dir: Optional[str] = None,
    replay_from_path: Optional[str] = None,
    store_transactions: bool = True,
) -> None:
    logging.basicConfig(level=logging.INFO)
    port_config = port_config if port_config is not None else {}

    # Explicitly not using context here so that crashed logs are retained
    tmp_vega_dir = tempfile.mkdtemp(prefix="vega-sim-") if log_dir is None else log_dir
    logger.info(f"Running NullChain from vegahome of {tmp_vega_dir}")
    if port_config.get(Ports.DATA_NODE_GRAPHQL):
        logger.info(
            f"Launching GraphQL node at port {port_config.get(Ports.DATA_NODE_GRAPHQL)}"
        )
    if port_config.get(Ports.CONSOLE):
        logger.info(f"Launching Console at port {port_config.get(Ports.CONSOLE)}")
    shutil.copytree(vega_home_path, f"{tmp_vega_dir}/vegahome")

    tmp_vega_home = tmp_vega_dir + "/vegahome"
    _update_node_config(
        tmp_vega_home,
        port_config=port_config,
        transactions_per_block=transactions_per_block,
        block_duration=block_duration,
    )

    dataNodeProcess = _popen_process(
        [
            data_node_path,
            "start",
            "--home=" + tmp_vega_home,
            "--chainID=CUSTOM",
        ],
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

    vega_args = [
        vega_path,
        "start",
        "--nodewallet-passphrase-file=" + tmp_vega_home + "/passphrase-file",
        "--home=" + tmp_vega_home,
    ]

    if store_transactions:
        replay_file = (
            replay_from_path
            if replay_from_path is not None
            else tmp_vega_home + "/replay"
        )
        vega_args.extend(
            [
                f"--blockchain.nullchain.replay-file={replay_file}",
                "--blockchain.nullchain.record",
            ]
        )
    if replay_from_path is not None:
        vega_args.extend(
            [
                f"--blockchain.nullchain.replay-file={replay_from_path}",
                "--blockchain.nullchain.replay",
            ]
        )

    vegaNodeProcess = _popen_process(
        vega_args,
        dir_root=tmp_vega_dir,
        log_name="node",
    )

    processes = [dataNodeProcess, vegaFaucetProcess, vegaNodeProcess]

    if run_wallet:
        for _ in range(3000):
            try:
                requests.get(
                    f"http://localhost:{port_config.get(Ports.DATA_NODE_REST)}/time"
                ).raise_for_status()
                requests.get(
                    f"http://localhost:{port_config.get(Ports.CORE_REST)}/blockchain/height"
                ).raise_for_status()
                break
            except (
                MaxRetryError,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
            ):
                time.sleep(0.1)
        wallet_args = [
            vega_wallet_path,
            "service",
            "run",
            "--network",
            "local",
            "--home=" + tmp_vega_home,
            "--automatic-consent",
        ]

        vegaWalletProcess = _popen_process(
            wallet_args,
            dir_root=tmp_vega_dir,
            log_name="vegawallet",
        )
        processes.append(vegaWalletProcess)

    if run_with_console:
        env_copy = os.environ.copy()
        env_copy.update(
            {
                "NX_VEGA_URL": (
                    f"http://localhost:{port_config[Ports.DATA_NODE_GRAPHQL]}/query"
                ),
                "NX_VEGA_WALLET_URL": f"http://localhost:{port_config[Ports.WALLET]}",
                "NX_VEGA_ENV": "CUSTOM",
                "NX_PORT": f"{port_config[Ports.CONSOLE]}",
                "NODE_ENV": "development",
                "NX_VEGA_NETWORKS": "{}",
            }
        )
        console_process = _popen_process(
            [
                "yarn",
                "--cwd",
                vega_console_path,
                "nx",
                "serve",
                "--port",
                f"{port_config[Ports.CONSOLE]}",
                "-o",
                "trading",
            ],
            dir_root=tmp_vega_dir,
            log_name="console",
            env=env_copy,
        )
        processes.append(console_process)

    signal.sigwait([signal.SIGKILL, signal.SIGTERM])
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

    if not retain_log_files:
        shutil.rmtree(tmp_vega_dir)


class VegaServiceNull(VegaService):
    PORT_TO_FIELD_MAP = {
        Ports.WALLET: "wallet_port",
        Ports.DATA_NODE_GRPC: "data_node_grpc_port",
        Ports.DATA_NODE_REST: "data_node_rest_port",
        Ports.DATA_NODE_GRAPHQL: "data_node_graphql_port",
        Ports.DATA_NODE_POSTGRES: "data_node_postgres_port",
        Ports.FAUCET: "faucet_port",
        Ports.VEGA_NODE: "vega_node_port",
        Ports.CORE_GRPC: "vega_node_grpc_port",
        Ports.CORE_REST: "vega_node_rest_port",
        Ports.CONSOLE: "console_port",
    }

    def __init__(
        self,
        vega_path: Optional[str] = None,
        data_node_path: Optional[str] = None,
        vega_wallet_path: Optional[str] = None,
        vega_console_path: Optional[str] = None,
        start_immediately: bool = False,
        run_with_console: bool = False,
        run_wallet_with_token_dapp: bool = False,
        port_config: Optional[Dict[Ports, int]] = None,
        warn_on_raw_data_access: bool = True,
        transactions_per_block: int = 1,
        seconds_per_block: int = 1,
        use_full_vega_wallet: bool = False,
        start_order_feed: bool = True,
        retain_log_files: bool = False,
        launch_graphql: bool = False,
        store_transactions: bool = True,
        replay_from_path: Optional[str] = None,
    ):
        super().__init__(
            can_control_time=True,
            warn_on_raw_data_access=warn_on_raw_data_access,
            seconds_per_block=seconds_per_block,
        )
        self.retain_log_files = retain_log_files

        self.vega_path = vega_path or path.join(vega_bin_path, "vega")
        self.data_node_path = data_node_path or path.join(vega_bin_path, "data-node")
        self.vega_wallet_path = vega_wallet_path or path.join(
            vega_bin_path, "vegawallet"
        )
        self.vega_console_path = vega_console_path or path.join(
            vega_bin_path, "console"
        )
        self.proc = None
        self.run_with_console = run_with_console
        self.run_wallet_with_token_dapp = run_wallet_with_token_dapp

        self.transactions_per_block = transactions_per_block
        self.seconds_per_block = seconds_per_block

        self._wallet = None
        self._use_full_vega_wallet = use_full_vega_wallet
        self.store_transactions = store_transactions

        self.log_dir = tempfile.mkdtemp(prefix="vega-sim-")

        self._start_order_feed = start_order_feed
        self.launch_graphql = launch_graphql
        self.replay_from_path = replay_from_path

        if port_config is None:
            self._assign_ports()
        else:
            for key, name in self.PORT_TO_FIELD_MAP.items():
                setattr(self, name, port_config[key])

        if start_immediately:
            self.start()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def wait_fn(self, wait_multiple: float = 1) -> None:
        self.wait_for_core_catchup()
        self.forward(f"{int(wait_multiple * self.seconds_per_block)}s")
        self.wait_for_core_catchup()

    @property
    def wallet(self) -> Wallet:
        if self._wallet is None:
            if self._use_full_vega_wallet:
                self._wallet = VegaWallet(self.wallet_url)
            else:
                self._wallet = SlimWallet(
                    self.core_client,
                    full_wallet=VegaWallet(self.wallet_url)
                    if self.run_with_console
                    else None,
                    log_dir=self.log_dir,
                )
        return self._wallet

    def _assign_ports(self):
        self.wallet_port = 0
        self.data_node_rest_port = 0
        self.data_node_grpc_port = 0
        self.data_node_graphql_port = 0
        self.data_node_postgres_port = 0
        self.faucet_port = 0
        self.vega_node_port = 0
        self.vega_node_grpc_port = 0
        self.vega_node_rest_port = 0
        self.console_port = 0
        for port_opt in self.PORT_TO_FIELD_MAP.values():
            curr_ports = set(
                [getattr(self, port) for port in self.PORT_TO_FIELD_MAP.values()]
            )
            setattr(self, port_opt, find_free_port(curr_ports))

    def _check_started(self) -> None:
        if self.proc is None:
            raise ServiceNotStartedError("NullChain Vega accessed without starting")

    def _generate_port_config(self) -> Dict[Ports, int]:
        return {
            Ports.WALLET: self.wallet_port,
            Ports.DATA_NODE_GRPC: self.data_node_grpc_port,
            Ports.DATA_NODE_REST: self.data_node_rest_port,
            Ports.DATA_NODE_GRAPHQL: self.data_node_graphql_port,
            Ports.DATA_NODE_POSTGRES: self.data_node_postgres_port,
            Ports.FAUCET: self.faucet_port,
            Ports.VEGA_NODE: self.vega_node_port,
            Ports.CORE_GRPC: self.vega_node_grpc_port,
            Ports.CORE_REST: self.vega_node_rest_port,
            Ports.CONSOLE: self.console_port,
        }

    def start(self, block_on_startup: bool = True) -> None:
        ctx = multiprocessing.get_context()
        port_config = self._generate_port_config()
        self.proc = ctx.Process(
            target=manage_vega_processes,
            kwargs={
                "vega_path": self.vega_path,
                "data_node_path": self.data_node_path,
                "vega_wallet_path": self.vega_wallet_path,
                "vega_console_path": self.vega_console_path,
                "run_with_console": self.run_with_console,
                "port_config": port_config,
                "transactions_per_block": self.transactions_per_block,
                "block_duration": f"{int(self.seconds_per_block)}s",
                "run_wallet": self._use_full_vega_wallet or self.run_with_console,
                "retain_log_files": self.retain_log_files,
                "log_dir": self.log_dir,
                "store_transactions": self.store_transactions,
                "replay_from_path": self.replay_from_path,
            },
        )
        self.proc.start()

        if self.run_with_console:
            logger.info(
                "Vega Running. Console launched at"
                f" http://localhost:{self.console_port}"
            )

        if block_on_startup:
            # Wait for startup
            started = False
            for _ in range(600):
                try:
                    requests.get(
                        f"http://localhost:{self.data_node_rest_port}/time"
                    ).raise_for_status()
                    requests.get(
                        f"http://localhost:{self.vega_node_rest_port}/blockchain/height"
                    ).raise_for_status()
                    if self.run_with_console or self._use_full_vega_wallet:
                        requests.get(
                            f"http://localhost:{self.wallet_port}/api/v1/status"
                        ).raise_for_status()

                    started = True
                    break
                except (
                    MaxRetryError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.HTTPError,
                ):
                    time.sleep(0.1)
            if not started:
                raise VegaStartupTimeoutError(
                    "Timed out waiting for Vega simulator to start up"
                )

        if self.run_with_console:
            webbrowser.open(f"http://localhost:{port_config[Ports.CONSOLE]}/", new=2)

        if self.launch_graphql:
            webbrowser.open(
                f"http://localhost:{port_config[Ports.DATA_NODE_GRAPHQL]}/", new=2
            )

        if self._start_order_feed:
            self.start_order_monitoring()

    # Class internal as at some point the host may vary as well as the port
    @staticmethod
    def _build_url(port: int, prefix: str = "http://"):
        return f"{prefix}localhost:{port}"

    def stop(self) -> None:
        super().stop()
        if self.proc is None:
            logger.info("Stop called but nothing to stop")
        else:
            self.proc.terminate()

    @property
    def wallet_url(self) -> str:
        return self._build_url(self.wallet_port)

    @property
    def data_node_rest_url(self) -> str:
        return self._build_url(self.data_node_rest_port)

    @property
    def data_node_grpc_url(self) -> str:
        return self._build_url(self.data_node_grpc_port, prefix="")

    @property
    def faucet_url(self) -> str:
        return self._build_url(self.faucet_port)

    @property
    def vega_node_url(self) -> str:
        return self._build_url(self.vega_node_port)

    @property
    def vega_node_grpc_url(self) -> str:
        return self._build_url(self.vega_node_grpc_port, prefix="")

    def clone(self) -> VegaServiceNull:
        """Creates a clone of the service without the handle to other processes.

        This is required as when spinning a Nullchain service out into
        separate processes we need to start the various components in the main
        thread (as daemon processes cannot spawn daemon processes), however want
        to maintain a handle to these in the child.
        """
        return VegaServiceNull(
            self.vega_path,
            self.data_node_path,
            self.vega_wallet_path,
            start_immediately=False,
            port_config=self._generate_port_config(),
            use_full_vega_wallet=self._use_full_vega_wallet,
            warn_on_raw_data_access=self.warn_on_raw_data_access,
        )
