from pathlib import Path
import sys

from edrio.logger import log
from edrio.utils import echo_and_run


def install():
    # Use pyinstaller to build the executable
    echo_and_run(
        f"pyinstaller --onefile --clean --windowed {Path(__file__).resolve().parent}/cli.py")

    # Get extension based on platform
    extension = ".exe" if sys.platform == "win32" else ""

    # Rename the executable
    echo_and_run(
        f"mv dist/cli{extension} dist/edrio{extension}")

    # Show after install instructions
    log(f"\n\nEdrio binary is located at: dist/edrio{extension}")
    log("If you want to install it to your system, run:")
    log(f"  sudo cp dist/edrio{extension} /usr/local/bin/edrio")


if __name__ == "__main__":
    install()
