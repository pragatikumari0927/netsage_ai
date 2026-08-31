"""Compatibility entry point for NetSage CSV validation."""

from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from netsage.data_validation import *
from netsage.data_validation import main


if __name__ == "__main__":
    main()
