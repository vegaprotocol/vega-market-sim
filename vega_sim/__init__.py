from importlib import metadata
from pathlib import Path

VEGA_VERSION = "0.71.4"
__version__ = metadata.version(__package__)

vega_home_path = Path(__file__).parent / "vegahome"
vega_bin_path = Path(__file__).parent / "bin"
