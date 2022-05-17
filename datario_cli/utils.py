"""
General utilities for the datario_cli CLI tool.
"""

import base64
from functools import partial
import glob
import json
from os import getenv, environ
from pathlib import Path
from random import choice
import subprocess
from sys import exit
from typing import Callable, List, Union

from typer import prompt, confirm

from datario_cli.constants import Constants as constants
from datario_cli.logger import log, logger


def append_output_to_string(output: str, wrapped_string: List[str]) -> None:
    """
    Appends the given output to the given string
    """
    wrapped_string[0] += output


def autocomplete_paths(text, state):
    return (glob.glob(text + "*") + [None])[state]


def build_directory_tree(directory: str) -> None:
    """
    Builds the directory tree for the given directory
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def check_for_env_vars(
    env_vars: List[str],
    path: str = constants.DATARIO_ENVIRONMENTS_FILE.value,
    save: bool = True,
) -> Callable:
    """
    Decorator that checks for required environment variables, and if they are missing, prompts
    values for them using `prompt_env`, sets them and saves to environment files.
    """
    load_env_file(path)
    missing_vars = []
    for env_var in env_vars:
        if not getenv(env_var):
            missing_vars.append(env_var)
    if missing_vars:
        log(
            f"Variáveis de ambiente faltando: {missing_vars}", level="warning")
        for i, env_var in enumerate(missing_vars):
            setenv(
                env_var,
                prompt_env(
                    message=f'[{i+1}/{len(missing_vars)}] '
                    f'{constants.DATARIO_ENVIRONMENTS_LIST.value[env_var]["prompt_text"]}',
                    callback_function=constants.DATARIO_ENVIRONMENTS_LIST.value[
                        env_var]["callback_function"]
                ))
        if save:
            save_env_file(path)


def check_requirements(requirements_list: List[str]) -> None:
    """
    Asserts that the required commands are installed. If something is missing, raise errors to the
    user.
    """
    INITIAL_MESSAGE = "The following required commands are missing:"
    msg = INITIAL_MESSAGE

    for requirement in requirements_list:
        if not command_exists(requirement):
            msg += f"\n  * {requirement}"

    if msg != INITIAL_MESSAGE:
        logger.error(msg)
        raise Exception(msg)


def clone_git_repository(repository: str, directory: str) -> None:
    """
    Clones the given git repository to the given directory
    """
    build_directory_tree(directory)
    echo_and_run(f"git clone {repository} {directory}",
                 stdout_callback=lambda _: None)


def command_exists(command: str) -> bool:
    """
    Asserts that the given command exists
    """
    try:
        echo_and_run(f"which {command}", stdout_callback=lambda _: None)
        return True
    except subprocess.CalledProcessError:
        return False


def directory_exists(directory: str) -> bool:
    """
    Asserts that the given directory exists
    """
    return Path(directory).exists()


def echo_and_run(
    command: str,
    stdout_callback: Callable = partial(print, end=""),
    on_error: Union[Callable, str] = "raise",
) -> int:
    """
    Echoes the command and then runs it, sending output to stdout_callback
    """
    allowed_on_errors = ["raise", "return"]
    if on_error not in allowed_on_errors and not callable(on_error):
        log(f"Invalid on_error value: {on_error}", "error")
        raise ValueError(f"Invalid on_error: {on_error}")
    log(f'{random_emoji("technology")} {command}')
    popen = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        stdout_callback(stdout_line)
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        if callable(on_error):
            on_error(return_code)
        elif on_error == "raise":
            log(f'{random_emoji("error")} {command} failed with exit code {return_code}', "error")
            exit(return_code)
        else:
            return return_code
    return return_code


def file_exists(path: str) -> bool:
    """
    Asserts that the given file exists
    """
    return Path(path).exists()


def get_confirmation(action: str) -> bool:
    """
    Prompts the user for confirmation
    """
    return confirm(f"😱 Tem certeza que deseja {action}?")


def get_current_kubectl_context() -> str:
    """
    Gets the current kubectl context
    """
    current_context = ""

    def callback(output: str):
        nonlocal current_context
        current_context = output.strip()

    echo_and_run(
        f"kubectl config current-context",
        stdout_callback=callback,
    )
    return current_context


def load_env_file(path: str = constants.DATARIO_ENVIRONMENTS_FILE.value) -> bool:
    """
    Loads the given environment file
    """
    if not Path(path).exists():
        return False
    with open(path) as f:
        env_file = json.load(f)
        for key, value in env_file.items():
            setenv(key, base64.b64decode(value).decode("utf-8"))
    return True


def prompt_env(message: str, default: str = None, callback_function: Callable = None) -> str:
    """
    Prompts the user for the given environment variable
    """
    if default:
        val = prompt(f"{message}", default=default)
    else:
        val = prompt(f"{message}")
    if callback_function:
        val = callback_function(val)
    return val


def random_emoji(category: str = None) -> str:
    """
    Returns a random emoji
    """
    if category:
        return choice(constants.EMOJIS.value[category])
    category = choice(list(constants.EMOJIS.value.keys()))
    return choice(constants.EMOJIS.value[category])


def save_env_file(path: str = constants.DATARIO_ENVIRONMENTS_FILE.value) -> bool:
    """
    Saves the current environment file to the given path
    """
    build_directory_tree(Path(path).parent)
    env_file = {}
    for key, value in environ.items():
        if key in constants.DATARIO_ENVIRONMENTS_LIST.value:
            env_file[key] = base64.b64encode(
                value.encode("utf-8")).decode("utf-8")
    with open(path, "w") as f:
        json.dump(env_file, f, indent=4)


def setenv(key: str, value: str) -> None:
    """
    Sets the given environment variable
    """
    environ[key] = value


def update_git_repo() -> None:
    """
    Updates the git repository
    """
    if directory_exists(constants.IAC_DIRECTORY.value):
        echo_and_run(
            f"cd {constants.IAC_DIRECTORY.value} && git pull --ff-only",
            stdout_callback=lambda _: None)
    else:
        echo_and_run(
            f"git clone {constants.IAC_GIT_REPOSITORY.value} {constants.IAC_DIRECTORY.value}",
            stdout_callback=lambda _: None)


def upgrade() -> None:
    """
    Upgrades the datario-cli
    """
    log(f"{random_emoji('technology')} Para atualizar o datario-cli, execute o comando:")
    log(f"curl -sSL https://get.dados.rio/ | bash")
