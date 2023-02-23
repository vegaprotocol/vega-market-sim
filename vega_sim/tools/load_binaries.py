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


def download_binaries():
    version = vega_sim.__version__
    platf = platform.system().lower()

    # We have no Windows specific builds, so people have to use WSL to run
    platf = "linux" if platf == "windows" else platf

    chipset = platform.processor()

    if os.path.exists(vega_sim.vega_bin_path):
        shutil.rmtree(vega_sim.vega_bin_path)

    with tempfile.TemporaryDirectory() as dir:
        os.mkdir(vega_sim.vega_bin_path)
        for remote_file in FILES:
            file_name = remote_file.format(platform=platf, chipset=chipset)
            logger.info(f"Downloading {file_name}")

            url = URL_BASE.format(version=version) + file_name
            res = requests.get(url)
            with open(os.path.join(dir, f"{file_name}"), "wb") as f:
                f.write(res.content)
            with zipfile.ZipFile(os.path.join(dir, f"{file_name}"), "r") as zip_ref:
                zip_ref.extractall(vega_sim.vega_bin_path)

        for bin_file in os.listdir(vega_sim.vega_bin_path):
            os.chmod(os.path.join(vega_sim.vega_bin_path, bin_file), 0o775)


def ensure_binaries_exist():
    if not os.path.exists(vega_sim.vega_bin_path):
        logger.info("Vega Protocol binaries not found, downloading relevant versions")
        download_binaries()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_binaries()
