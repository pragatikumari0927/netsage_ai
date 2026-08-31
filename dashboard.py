"""Compatibility entry point for the NetSage static report generator."""

from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from netsage.dashboard import *
from netsage.dashboard import main


if __name__ == "__main__":
    main()
