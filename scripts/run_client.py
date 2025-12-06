#!/usr/bin/env python

"""
Launches the customer (client) desktop GUI.
"""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    # Project root = parent of this scripts/ directory
    root_dir = Path(__file__).resolve().parents[1]

    # Path to the client main view
    client_main = root_dir / "src" / "client" / "view" / "login_view.py"

    if not client_main.exists():
        raise SystemExit(f"[ERROR] Could not find client main view at: {client_main}")

    # Delegate to Python to run the UI file
    subprocess.run([sys.executable, str(client_main)], check=True)


if __name__ == "__main__":
    main()
