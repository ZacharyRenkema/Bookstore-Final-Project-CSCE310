"""
Launches the manager desktop GUI.
"""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    # Project root = parent of this scripts/ directory
    root_dir = Path(__file__).resolve().parents[1]

    # Start from the manager login window
    manager_entry = root_dir / "src" / "manager" / "manager_login.py"

    if not manager_entry.exists():
        raise SystemExit(f"[ERROR] Could not find manager login at: {manager_entry}")

    subprocess.run([sys.executable, str(manager_entry)], check=True)


if __name__ == "__main__":
    main()
