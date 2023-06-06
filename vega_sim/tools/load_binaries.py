import logging
import os
import platform
import shutil
import tempfile
import zipfile

import requests

import vega_sim

logger = logging.getLogger(__name__)

URL_BASE = "https://github.com/vegaprotocol/vega/releases/download/v{version}/"
DATA_NODE = "data-node-{platform}-{chipset}64.zip"
VEGA_CORE = "vega-{platform}-{chipset}64.zip"
VEGAWALLET = "vegawallet-{platform}-{chipset}64.zip"

FILES = [DATA_NODE, VEGA_CORE, VEGAWALLET]

BIN_NAMES = {
    DATA_NODE: "data-node",
    VEGA_CORE: "vega",
    VEGAWALLET: "vegawallet",
}
python -m vega_sim.scenario.adhoc -s historic_shaped_market_maker --pause


def download_binaries(force: bool = False):
    platf = platform.system().lower()

    # We have no Windows specific builds, so people have to use WSL to run
    platf = "linux" if platf == "windows" else platf

    chipset = "arm" if "arm" in platform.machine() else "amd"

    if force and os.path.exists(vega_sim.vega_bin_path):
        shutil.rmtree(vega_sim.vega_bin_path)

    with tempfile.TemporaryDirectory() as dir:
        if not os.path.exists(vega_sim.vega_bin_path):
            os.mkdir(vega_sim.vega_bin_path)
        for remote_file in FILES:
            file_name = remote_file.format(platform=platf, chipset=chipset)
            if (
                not os.path.exists(
                    os.path.join(vega_sim.vega_bin_path, BIN_NAMES[remote_file])
                )
            ) or force:
                logger.info(f"Downloading {file_name}")

                url = URL_BASE.format(version=vega_sim.VEGA_VERSION) + file_name
                res = requests.get(url)
                file_path = os.path.join(dir, f"{file_name}")

                with open(file_path, "wb") as f:
                    f.write(res.content)
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(vega_sim.vega_bin_path)

        for bin_file in os.listdir(vega_sim.vega_bin_path):
            os.chmod(os.path.join(vega_sim.vega_bin_path, bin_file), 0o775)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_binaries()
