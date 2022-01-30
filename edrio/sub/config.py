"""
Configuration management through environment variables.
"""

from os import getenv

from typer import Typer

from edrio.constants import Constants as constants
from edrio.logger import log
from edrio.utils import load_env_file

app = Typer()


@app.command()
def init():
    """
    Initialize configurations set
    """
    # TODO: implement


@app.command()
def update():
    """
    Update configurations set
    """
    # TODO: implement


@app.command()
def view():
    """
    View configurations set
    """
    load_env_file()
    log(":nerd_face: Configurações atuais:")
    for key, value in constants.EDRIO_ENVIRONMENTS_LIST.value.items():
        log(f'  * {value}: {getenv(key, "Not configured.")}')
