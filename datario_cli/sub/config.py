"""
Configuration management through environment variables.
"""

from os import getenv
from pathlib import Path

from typer import Typer

from edrio.constants import Constants as constants
from edrio.logger import log
from edrio.utils import (
    check_for_env_vars,
    get_confirmation,
    load_env_file,
    prompt_env,
    random_emoji,
    random_emoji,
    save_env_file,
    setenv,
)

app = Typer()


def setup():
    """
    Setup the environment variables.
    """
    load_env_file()


@app.command()
def init():
    """
    Initialize configurations set
    """
    setup()

    if Path(constants.EDRIO_ENVIRONMENTS_FILE.value).exists():
        print("🤔 Você já tem um arquivo de configuração.")
        if get_confirmation("apagar o arquivo"):
            Path(constants.EDRIO_ENVIRONMENTS_FILE.value).unlink()
            print("🗑️ Arquivo apagado.")
            for key in constants.EDRIO_ENVIRONMENTS_LIST.value:
                setenv(key, "")

    # Check for environment variables
    check_for_env_vars(
        constants.EDRIO_ENVIRONMENTS_LIST.value.keys(),
        save=False,
    )

    # Save environment variables
    save_env_file(constants.EDRIO_ENVIRONMENTS_FILE.value)


@app.command()
def reset():
    """
    Resets the configurations
    """
    setup()
    accept = get_confirmation("deletar suas configurações atuais?")
    if accept:
        if Path(constants.EDRIO_ENVIRONMENTS_FILE.value).exists():
            Path(constants.EDRIO_ENVIRONMENTS_FILE.value).unlink()
            log(f'{random_emoji("success")} Arquivo de configurações apagado com sucesso!',
                "success")
        else:
            log(f'{random_emoji("error")} Arquivo de configurações não existe!'
                " Você pode iniciar um com o comando `edrio config init`.")
    else:
        log(f'{random_emoji("error")} Configurações não foram apagadas!')


@app.command()
def show():
    """
    Show configurations set
    """
    setup()
    log(f'{random_emoji("nerd")} Configurações atuais:')
    for key, value in constants.EDRIO_ENVIRONMENTS_LIST.value.items():
        val = getenv(key)
        if val:
            log(f'  * {value}: {val}')
        else:
            log(f'  * {value}: <not set>', level="warning")


@app.command()
def update():
    """
    Update configurations set
    """
    setup()
    for env_name in constants.EDRIO_ENVIRONMENTS_LIST.value:
        env_value = getenv(env_name)
        if env_value:
            prompt_env(
                constants.EDRIO_ENVIRONMENTS_LIST.value[env_name], env_value)
