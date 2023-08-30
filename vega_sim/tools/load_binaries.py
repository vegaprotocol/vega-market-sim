import argparse
import logging
import os
import platform
import shutil
import tempfile
import zipfile
from typing import Optional

import requests

import vega_sim

logger = logging.getLogger(__name__)

URL_DEV_BASE = (
    "https://github.com/vegaprotocol/vega-dev-releases/releases/download/{version}/"
)
URL_BASE = "https://github.com/vegaprotocol/vega/releases/download/{version}/"
DATA_NODE = "data-node-{platform}-{chipset}64.zip"
VEGA_CORE = "vega-{platform}-{chipset}64.zip"

FILES = [DATA_NODE, VEGA_CORE]

BIN_NAMES = {
    DATA_NODE: "data-node",
    VEGA_CORE: "vega",
}


def download_binaries(
    force: bool = False,
    latest: bool = False,
    version: Optional[str] = None,
    dev: bool = False,
):
    if version is not None and latest:
        raise Exception(
            "Cannot specify both version and latest flag, please use only one"
        )

    platf = platform.system().lower()

    # We have no Windows specific builds, so people have to use WSL to run
    platf = "linux" if platf == "windows" else platf

    chipset = "arm" if "arm" in platform.machine() else "amd"

    if force and os.path.exists(vega_sim.vega_bin_path):
        shutil.rmtree(vega_sim.vega_bin_path)

    with tempfile.TemporaryDirectory() as dir:
        if not os.path.exists(vega_sim.vega_bin_path):
            os.mkdir(vega_sim.vega_bin_path)

        if version:
            vega_version = version
        elif latest:
            vega_versions = requests.get(
                "https://api.github.com/repos/vegaprotocol/vega-dev-releases/releases"
                if dev
                else "https://api.github.com/repos/vegaprotocol/vega/releases"
            ).json()
            vega_version = vega_versions[0]["tag_name"]
        else:
            vega_version = vega_sim.VEGA_VERSION

        logger.info(f"Downloading Vega version {vega_version}")

        for remote_file in FILES:
            file_name = remote_file.format(platform=platf, chipset=chipset)
            if (
                not os.path.exists(
                    os.path.join(vega_sim.vega_bin_path, BIN_NAMES[remote_file])
                )
            ) or force:
                logger.info(f"Downloading {file_name}")

                url_base = (URL_BASE if not dev else URL_DEV_BASE).format(
                    version=vega_version
                )
                url = url_base + file_name
                res = requests.get(url)
                res.raise_for_status()

                file_path = os.path.join(dir, f"{file_name}")

                with open(file_path, "wb") as f:
                    f.write(res.content)
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(vega_sim.vega_bin_path)

        for bin_file in os.listdir(vega_sim.vega_bin_path):
            os.chmod(os.path.join(vega_sim.vega_bin_path, bin_file), 0o775)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force binaries to download even if some are already present",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help=(
            "Load the latest built version, either from main repo or the dev builds"
            " depending on presence of dev flag"
        ),
    )
    parser.add_argument(
        "--version",
        required=False,
        help=(
            "Specify a specific version tag to use. Otherwise will be picked based on"
            " either presence of latest flag or the default vega sim version"
        ),
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help=(
            "Flag to specify loading versions from the Vega dev process (built on every"
            " release) vs main repo builds"
        ),
    )
    args = parser.parse_args()

    download_binaries(
        force=args.force, latest=args.latest, dev=args.dev, version=args.version
    )
