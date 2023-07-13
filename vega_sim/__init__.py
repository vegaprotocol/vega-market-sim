from importlib import metadata
from pathlib import Path

VEGA_VERSION = "0.72.3"
try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = ""

vega_home_path = Path(__file__).parent / "vegahome"
vega_bin_path = Path(__file__).parent / "bin"
