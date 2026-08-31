"""Compatibility entry point for the Streamlit NetSage dashboard."""

from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from netsage.dashboard_app import main


if __name__ == "__main__":
    main()
