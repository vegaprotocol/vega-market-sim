from __future__ import annotations

import json
import atexit
import datetime
import functools
import logging
import multiprocessing
import os
import shutil
import signal
import socket
import subprocess
import tempfile
import threading
import time
import webbrowser
from collections import namedtuple
from contextlib import closing
from enum import Enum, auto
from io import BufferedWriter
from logging.handlers import QueueHandler
from multiprocessing import Queue
from os import path
from typing import Dict, List, Optional, Set

import docker
import grpc
import requests
import toml
from urllib3.exceptions import MaxRetryError

import vega_sim.api.governance as gov
import vega_sim.grpc.client as vac
from vega_sim import vega_bin_path, vega_home_path
from vega_sim.service import VegaService
from vega_sim.tools.load_binaries import download_binaries
from vega_sim.tools.retry import retry
from vega_sim.wallet.base import DEFAULT_WALLET_NAME, Wallet
from vega_sim.wallet.slim_wallet import SlimWallet
from vega_sim.wallet.vega_wallet import VegaWallet

logger = logging.getLogger(__name__)

PortUpdateConfig = namedtuple(
    "PortUpdateConfig", ["file_path", "config_path", "key", "val_func"]
)

PORT_DIR_NAME = "market_sim_ports"


class Ports(Enum):
    DATA_NODE_GRPC = auto()
    DATA_NODE_REST = auto()
    DATA_NODE_POSTGRES = auto()
    FAUCET = auto()
    WALLET = auto()
    VEGA_NODE = auto()
    CORE_GRPC = auto()
    CORE_REST = auto()
    BROKER = auto()
    METRICS = auto()
    DATA_NODE_METRICS = auto()
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
            ["Gateway"],
            "Port",
            lambda port: port,
        ),
        PortUpdateConfig(
            ("config", "wallet-service", "networks", "local.toml"),
            ["API", "REST"],
            "Hosts",
            lambda port: [f"localhost:{port}"],
        ),
        PortUpdateConfig(
            ("config", "wallet-service", "networks", "local.toml"),
            ["API", "GraphQL"],
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
            ("config", "wallet-service", "config.toml"),
            ["Server"],
            "Port",
            lambda port: port,
        ),
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
    Ports.DATA_NODE_METRICS: [
        PortUpdateConfig(
            ("config", "data-node", "config.toml"),
            ["Metrics"],
            "Port",
            lambda port: port,
        ),
    ],
    Ports.METRICS: [
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


def logger_thread(q):
    while True:
        record = q.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)


def find_free_port(existing_set: Optional[Set[int]] = None):
    ret_sock = 0
    existing_set = (
        existing_set.union(set([ret_sock]))
        if existing_set is not None
        else set([ret_sock])
    )

    # Synchronisation to try to avoid using the same ports across processes
    # launching at very similar times
    dated_path_dir = path.join(
        tempfile.gettempdir(),
        PORT_DIR_NAME,
        datetime.date.today().strftime("%Y-%d-%m-%H-%M"),
    )
    os.makedirs(dated_path_dir, exist_ok=True)
    existing_set.update(set(int(x) for x in os.listdir(dated_path_dir)))

    num_tries = 0
    while ret_sock in existing_set:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            ret_sock = s.getsockname()[1]

        num_tries += 1
        if num_tries >= 100:
            # Arbitrary high number. If we try 100 times and fail to find
            # a port it seems reasonable to give up
            raise SocketNotFoundError("Failed finding a free socket")

    open(path.join(dated_path_dir, str(ret_sock)), "x")
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
    use_docker_postgres: bool = False,
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

            if port_key == Ports.DATA_NODE_POSTGRES:
                config_toml["SQLStore"]["UseEmbedded"] = not use_docker_postgres

            with open(file_path, "w") as f:
                toml.dump(config_toml, f)


def manage_vega_processes(
    child_conn: multiprocessing.Pipe,
    log_queue,
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
    log_level: Optional[int] = None,
    genesis_time: Optional[datetime.datetime] = None,
) -> None:
    logger.addHandler(QueueHandler(log_queue))
    logger.setLevel(log_level if log_level is not None else logging.INFO)

    port_config = port_config if port_config is not None else {}

    try:
        docker_client = docker.from_env()
        use_docker_postgres = True
    except:
        use_docker_postgres = False

    # Explicitly not using context here so that crashed logs are retained
    tmp_vega_dir = tempfile.mkdtemp(prefix="vega-sim-") if log_dir is None else log_dir
    logger.info(f"Running NullChain from vegahome of {tmp_vega_dir}")

    if port_config.get(Ports.CONSOLE):
        logger.info(f"Launching Console at port {port_config.get(Ports.CONSOLE)}")
    if port_config.get(Ports.DATA_NODE_REST):
        logger.info(
            "Launching Datanode REST + GRAPHQL at port"
            f" {port_config.get(Ports.DATA_NODE_REST)}"
        )
    if port_config.get(Ports.DATA_NODE_GRPC):
        logger.info(
            f"Launching Datanode GRPC at port {port_config.get(Ports.DATA_NODE_GRPC)}"
        )
    if port_config.get(Ports.CORE_REST):
        logger.info(f"Launching Core REST at port {port_config.get(Ports.CORE_REST)}")

    if port_config.get(Ports.CORE_GRPC):
        logger.info(f"Launching Core GRPC at port {port_config.get(Ports.CORE_GRPC)}")

    dest_dir = f"{tmp_vega_dir}/vegahome"
    shutil.copytree(vega_home_path, dest_dir)
    for dirpath, _, filenames in os.walk(dest_dir):
        os.utime(dirpath, None)
        for file in filenames:
            os.utime(os.path.join(dirpath, file), None)
    if genesis_time is not None:
        with open(f"{dest_dir}/genesis.json", "r") as file:
            data = json.load(file)
        data["genesis_time"] = genesis_time.isoformat() + "Z"
        with open(f"{dest_dir}/genesis.json", "w") as file:
            json.dump(data, file, indent=2)

    tmp_vega_home = tmp_vega_dir + "/vegahome"
    _update_node_config(
        tmp_vega_home,
        port_config=port_config,
        transactions_per_block=transactions_per_block,
        block_duration=block_duration,
        use_docker_postgres=use_docker_postgres,
    )

    if use_docker_postgres:
        data_node_docker_volume = docker_client.volumes.create()
        data_node_container = docker_client.containers.run(
            "timescale/timescaledb:2.11.2-pg15",
            command=[
                "-c",
                "max_connections=50",
                "-c",
                "log_destination=stderr",
                "-c",
                "work_mem=5MB",
                "-c",
                "huge_pages=off",
                "-c",
                "shared_memory_type=sysv",
                "-c",
                "dynamic_shared_memory_type=sysv",
                "-c",
                "shared_buffers=2GB",
                "-c",
                "temp_buffers=5MB",
            ],
            detach=True,
            ports={5432: port_config[Ports.DATA_NODE_POSTGRES]},
            volumes=[f"{data_node_docker_volume.name}:/var/lib/postgresql/data"],
            environment={
                "POSTGRES_USER": "vega",
                "POSTGRES_PASSWORD": "vega",
                "POSTGRES_DB": "vega",
            },
            remove=False,
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

    for _ in range(500):
        try:
            requests.get(
                f"http://localhost:{port_config[Ports.CORE_REST]}/blockchain/height"
            ).raise_for_status()
            break
        except:
            pass

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

    processes = {
        "data-node": dataNodeProcess,
        "faucet": vegaFaucetProcess,
        "vega": vegaNodeProcess,
    }

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

        subprocess.run(
            [
                vega_wallet_path,
                "wallet",
                "api-token",
                "init",
                f"--home={tmp_vega_home}",
                f"--passphrase-file={tmp_vega_home}/passphrase-file",
            ],
            capture_output=True,
        )

        subprocess.run(
            [
                vega_wallet_path,
                "wallet",
                "create",
                "--wallet",
                DEFAULT_WALLET_NAME,
                "--home",
                tmp_vega_home,
                "--passphrase-file",
                tmp_vega_home + "/passphrase-file",
                "--output",
                "json",
            ],
            capture_output=True,
        )

        subprocess.run(
            [
                vega_wallet_path,
                "wallet",
                "api-token",
                "generate",
                "--home=" + tmp_vega_home,
                "--tokens-passphrase-file=" + tmp_vega_home + "/passphrase-file",
                "--wallet-passphrase-file=" + tmp_vega_home + "/passphrase-file",
                "--wallet-name=" + DEFAULT_WALLET_NAME,
                "--description=" + DEFAULT_WALLET_NAME,
            ],
            capture_output=True,
        )

        wallet_args = [
            vega_wallet_path,
            "wallet",
            "service",
            "run",
            "--network",
            "local",
            "--home=" + tmp_vega_home,
            "--automatic-consent",
            "--load-tokens",
            "--tokens-passphrase-file=" + tmp_vega_home + "/passphrase-file",
        ]

        vegaWalletProcess = _popen_process(
            wallet_args,
            dir_root=tmp_vega_dir,
            log_name="vegawallet",
        )
        processes["wallet"] = vegaWalletProcess

    if run_with_console:
        env_copy = os.environ.copy()
        env_copy.update(
            {
                "NX_VEGA_URL": (
                    f"http://localhost:{port_config[Ports.DATA_NODE_REST]}/graphql"
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
                "-o",
                "trading",
                "--port",
                f"{port_config[Ports.CONSOLE]}",
            ],
            dir_root=tmp_vega_dir,
            log_name="console",
            env=env_copy,
        )
        processes["console"] = console_process

    # Send process pid values for resource monitoring
    child_conn.send({name: process.pid for name, process in processes.items()})

    # According to https://docs.oracle.com/cd/E19455-01/806-5257/gen-75415/index.html
    # There is no guarantee that signal will be catch by this thread. Usually the
    # parent process catches the signal and removes it from the list of pending
    # signals, this leave us with memory leak where we have orphaned vega processes
    # and the docker containers. Below is hack to maximize chance by catching the
    # signal.
    # We call signal.signal method as a workaround to move this thread on top of
    # the catch stack, then sigwait waits until singal is trapped.
    # As last resort We catches the `SIGCHLD`  in case the parent process exited
    # and this is the orphan now.
    # But to provide 100% guarantee this should be implemented in another way:
    #   - Signal should be trapped in the main process, and this should be synced
    #     the shared memory
    #   - or this entire process manager should be incorporated in the VegaServiceNull
    #     and containers/processes should be removed as inline call in the __exit__
    #
    #
    # Important assumption is that this signal can be caught multiple times as well
    def sighandler(signal, frame, logger_):
        if signal is None:
            logger_.info("VegaServiceNull exited normally")
        else:
            logger_.info(f"VegaServiceNull exited after trapping the {signal} signal")

        logger_.info("Received signal from parent process")

        logger_.info("Starting termination for processes")
        for name, process in processes.items():
            logger_.info(f"Terminating process {name}(pid: {process.pid})")
            process.terminate()

        for name, process in processes.items():
            attempts = 0
            while process.poll() is None:
                logger_.info(f"Process {name} still not terminated")
                time.sleep(1)
                attempts += 1
                if attempts > 60:
                    logger_.warning(
                        "Gracefully terminating process timed-out. Killing process"
                        f" {name}."
                    )
                    process.kill()
            logger_.debug(f"Process {name} stopped with {process.poll()}")
            if process.poll() == 0:
                logger_.info(f"Process {name} terminated.")
            if process.poll() == -9:
                logger_.info(f"Process {name} killed.")

        if use_docker_postgres:

            def kill_docker_container() -> None:
                try:
                    data_node_container.stop()
                    with open(tmp_vega_home + "/postgres.out", "wb") as f:
                        f.write(data_node_container.logs())
                    data_node_container.remove()
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        logger_.debug(
                            f"Container {data_node_container.name} has been already"
                            " killed"
                        )
                        return
                    else:
                        raise e

            logger_.debug(f"Stopping container {data_node_container.name}")
            retry(10, 1.0, kill_docker_container)

            removed = False
            logger_.debug(f"Removing volume {data_node_docker_volume.name}")
            for _ in range(20):
                if data_node_container.status == "running":
                    time.sleep(3)
                    continue
                try:
                    data_node_docker_volume.remove(force=True)
                    removed = True
                    break
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        removed = True
                        logger_.debug(
                            f"Data node volume {data_node_docker_volume.name} has been"
                            " already killed"
                        )
                        break
                    else:
                        time.sleep(1)
                except docker.errors.APIError:
                    time.sleep(1)
            if not removed:
                logger_.exception(
                    "Docker volume failed to cleanup, will require manual cleaning"
                )
        if not retain_log_files and os.path.exists(tmp_vega_dir):
            shutil.rmtree(tmp_vega_dir)

    # The below lines are workaround to put the signal listeners on top of the stack, so this process can handle it.
    signal.signal(signal.SIGINT, lambda _s, _h: None)
    signal.signal(signal.SIGTERM, lambda _s, _h: None)

    # The process had previously created one or more child processes with the fork() function.
    # One or more of these processes has since died.
    signal.sigwait(
        [
            signal.SIGKILL,  # The process was explicitly killed by somebody wielding the kill program.
            signal.SIGTERM,  # The process was explicitly killed by somebody wielding the terminate program.
            signal.SIGCHLD,
        ]
    )
    sighandler(None, None, logger_=logger)


class VegaServiceNull(VegaService):
    PORT_TO_FIELD_MAP = {
        Ports.CONSOLE: "console_port",
        Ports.CORE_GRPC: "vega_node_grpc_port",
        Ports.CORE_REST: "vega_node_rest_port",
        Ports.DATA_NODE_GRPC: "data_node_grpc_port",
        Ports.DATA_NODE_METRICS: "data_node_metrics_port",
        Ports.DATA_NODE_POSTGRES: "data_node_postgres_port",
        Ports.DATA_NODE_REST: "data_node_rest_port",
        Ports.FAUCET: "faucet_port",
        Ports.METRICS: "metrics_port",
        Ports.VEGA_NODE: "vega_node_port",
        Ports.WALLET: "wallet_port",
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
        retain_log_files: bool = False,
        launch_graphql: bool = False,
        store_transactions: bool = True,
        replay_from_path: Optional[str] = None,
        listen_for_high_volume_stream_updates: bool = False,
        check_for_binaries: bool = False,
        genesis_time: Optional[datetime.datetime] = None,
    ):
        super().__init__(
            can_control_time=True,
            warn_on_raw_data_access=warn_on_raw_data_access,
            seconds_per_block=seconds_per_block,
            listen_for_high_volume_stream_updates=listen_for_high_volume_stream_updates,
        )
        self.retain_log_files = retain_log_files

        self._using_all_custom_paths = all(
            [x is not None for x in [vega_path, data_node_path, vega_wallet_path]]
        )
        self.vega_path = vega_path or path.join(vega_bin_path, "vega")
        self.data_node_path = data_node_path or path.join(vega_bin_path, "data-node")
        self.vega_wallet_path = vega_wallet_path or path.join(vega_bin_path, "vega")
        self.vega_console_path = vega_console_path or path.join(
            vega_bin_path, "console"
        )
        self.proc = None
        self.run_with_console = run_with_console
        self.run_wallet_with_token_dapp = run_wallet_with_token_dapp
        self.genesis_time = genesis_time

        self.transactions_per_block = transactions_per_block
        self.seconds_per_block = seconds_per_block

        self._wallet = None
        self._use_full_vega_wallet = use_full_vega_wallet
        self.store_transactions = store_transactions

        self.log_dir = tempfile.mkdtemp(prefix="vega-sim-")

        self.launch_graphql = launch_graphql
        self.replay_from_path = replay_from_path
        self.check_for_binaries = check_for_binaries

        self.stopped = False
        self.logger_p = None

        self._assign_ports(port_config)

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
                self._wallet = VegaWallet(
                    self.wallet_url,
                    wallet_path=self.vega_wallet_path,
                    vega_home_dir=path.join(self.log_dir, "vegahome"),
                    passphrase_file_path=path.join(
                        self.log_dir, "vegahome", "passphrase-file"
                    ),
                )
            else:
                self._wallet = SlimWallet(
                    self.core_client,
                    full_wallet=None,
                    log_dir=self.log_dir,
                )
        return self._wallet

    def _check_started(self) -> None:
        if self.proc is None:
            raise ServiceNotStartedError("NullChain Vega accessed without starting")

    def _generate_port_config(self) -> Dict[Ports, int]:
        return {
            Ports.CONSOLE: self.console_port,
            Ports.CORE_GRPC: self.vega_node_grpc_port,
            Ports.CORE_REST: self.vega_node_rest_port,
            Ports.DATA_NODE_GRPC: self.data_node_grpc_port,
            Ports.DATA_NODE_METRICS: self.data_node_metrics_port,
            Ports.DATA_NODE_POSTGRES: self.data_node_postgres_port,
            Ports.DATA_NODE_REST: self.data_node_rest_port,
            Ports.FAUCET: self.faucet_port,
            Ports.METRICS: self.metrics_port,
            Ports.VEGA_NODE: self.vega_node_port,
            Ports.WALLET: self.wallet_port,
        }

    # set ports from port_config or alternatively find a free port
    # to use
    def _assign_ports(self, port_config: Optional[Dict[Ports, int]]):
        self.console_port = 0
        self.data_node_grpc_port = 0
        self.data_node_metrics_port = 0
        self.data_node_postgres_port = 0
        self.data_node_rest_port = 0
        self.faucet_port = 0
        self.metrics_port = 0
        self.vega_node_grpc_port = 0
        self.vega_node_port = 0
        self.vega_node_rest_port = 0
        self.wallet_port = 0

        for key, name in self.PORT_TO_FIELD_MAP.items():
            if port_config is not None and key in port_config:
                setattr(self, name, port_config[key])
            else:
                curr_ports = set(
                    [getattr(self, port) for port in self.PORT_TO_FIELD_MAP.values()]
                )
                setattr(self, name, find_free_port(curr_ports))

    def start(self, block_on_startup: bool = True) -> None:
        if self.check_for_binaries and not self._using_all_custom_paths:
            download_binaries()
        parent_conn, child_conn = multiprocessing.Pipe()
        ctx = multiprocessing.get_context()
        port_config = self._generate_port_config()
        self.queue = Queue()

        self.logger_p = threading.Thread(target=logger_thread, args=(self.queue,))
        self.logger_p.start()

        self.proc = ctx.Process(
            target=manage_vega_processes,
            kwargs={
                "child_conn": child_conn,
                "log_queue": self.queue,
                "vega_path": self.vega_path,
                "data_node_path": self.data_node_path,
                "vega_wallet_path": self.vega_wallet_path,
                "vega_console_path": self.vega_console_path,
                "run_with_console": self.run_with_console,
                "port_config": port_config,
                "transactions_per_block": self.transactions_per_block,
                "block_duration": f"{int(self.seconds_per_block)}s",
                "run_wallet": self._use_full_vega_wallet,
                "retain_log_files": self.retain_log_files,
                "log_dir": self.log_dir,
                "store_transactions": self.store_transactions,
                "replay_from_path": self.replay_from_path,
                "log_level": logging.getLogger().level,
                "genesis_time": self.genesis_time,
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
            for _ in range(500):
                try:
                    channel = grpc.insecure_channel(
                        self.data_node_grpc_url,
                        options=(
                            ("grpc.enable_http_proxy", 0),
                            ("grpc.max_send_message_length", 1024 * 1024 * 20),
                            ("grpc.max_receive_message_length", 1024 * 1024 * 20),
                        ),
                    )
                    grpc.channel_ready_future(channel).result(timeout=5)
                    trading_data_client = vac.VegaTradingDataClientV2(
                        self.data_node_grpc_url,
                        channel=channel,
                    )
                    gov.get_blockchain_time(trading_data_client)

                    requests.get(
                        f"http://localhost:{self.data_node_rest_port}/time"
                    ).raise_for_status()
                    requests.get(
                        f"http://localhost:{self.vega_node_rest_port}/blockchain/height"
                    ).raise_for_status()
                    requests.get(
                        f"http://localhost:{self.faucet_port}/api/v1/health"
                    ).raise_for_status()

                    if self._use_full_vega_wallet:
                        requests.get(
                            f"http://localhost:{self.wallet_port}/api/v2/health"
                        ).raise_for_status()

                    started = True
                    break
                except (
                    MaxRetryError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.HTTPError,
                    grpc.RpcError,
                    grpc.FutureTimeoutError,
                ):
                    time.sleep(0.1)
            if not started:
                self.stop()
                raise VegaStartupTimeoutError(
                    "Timed out waiting for Vega simulator to start up"
                )

            # TODO: Remove this once datanode fixes up startup timing
            time.sleep(6)
            self.process_pids = parent_conn.recv()

        # Initialise the data-cache
        self.data_cache

        if self.run_with_console:
            webbrowser.open(f"http://localhost:{port_config[Ports.CONSOLE]}/", new=2)

        if self.launch_graphql:
            webbrowser.open(
                f"http://localhost:{port_config[Ports.DATA_NODE_REST]}/graphql", new=2
            )

        # Create the VegaService key and mint assets to the treasury
        governance_asset = self.get_asset(
            self.find_asset_id(symbol="VOTE", enabled=True, raise_on_missing=True)
        )
        self.wallet.create_key(wallet_name=self.WALLET_NAME, name=self.KEY_NAME)
        self.mint(
            wallet_name=self.WALLET_NAME,
            key_name=self.KEY_NAME,
            asset=governance_asset.id,
            amount=governance_asset.details.builtin_asset.max_faucet_amount_mint,
            from_faucet=True,
        )

    # Class internal as at some point the host may vary as well as the port
    @staticmethod
    def _build_url(port: int, prefix: str = "http://"):
        return f"{prefix}localhost:{port}"

    def stop(self) -> None:
        logger.debug("Calling stop for veganullchain")
        if self.stopped:
            return
        self.stopped = True

        if self._core_client is not None:
            self.core_client.stop()
        if self._core_state_client is not None:
            self.core_state_client.stop()
        if self._trading_data_client_v2 is not None:
            self.trading_data_client_v2.stop()

        if self.proc is None:
            logger.info("Stop called but nothing to stop")
        else:
            os.kill(self.proc.pid, signal.SIGTERM)
        if self.queue is not None:
            if self.proc is not None:
                attempts = 0
                while self.proc.is_alive:
                    if attempts > 5:
                        break
                    time.sleep(1)
                    attempts += 1
            self.queue.put(None)
            self.logger_p.join()

        if isinstance(self.wallet, SlimWallet):
            self.wallet.stop()
        super().stop()

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
