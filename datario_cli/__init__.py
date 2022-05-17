__all__ = ["app"]
__version__ = "0.1.0"

import readline

from datario_cli.cli import app
from datario_cli.utils import autocomplete_paths

readline.set_completer_delims(" \t\n;")
readline.parse_and_bind("tab: complete")
readline.set_completer(autocomplete_paths)
