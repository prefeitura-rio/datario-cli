from pathlib import Path
import sys

from datario_cli.logger import log
from datario_cli.utils import echo_and_run


def install():
    # Use pyinstaller to build the executable
    echo_and_run(
        f"pyinstaller --onefile --clean --windowed {Path(__file__).resolve().parent}/cli.py")

    # Get extension based on platform
    extension = ".exe" if sys.platform == "win32" else ""

    # Rename the executable
    echo_and_run(
        f"mv dist/cli{extension} dist/datario_cli{extension}")

    # Show after install instructions
    log(f"\n\ndatario_cli binary is located at: dist/datario_cli{extension}")
    log("If you want to install it to your system, run:")
    log(f"  sudo cp dist/datario_cli{extension} /usr/local/bin/datario_cli")


if __name__ == "__main__":
    install()
