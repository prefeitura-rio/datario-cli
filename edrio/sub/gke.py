"""
GKE cluster management through Terraform
"""

from functools import partial
from sys import argv

from typer import Typer

from edrio.constants import Constants as constants
from edrio.logger import log
from edrio.utils import (
    append_output_to_string,
    check_for_env_vars,
    check_requirements,
    echo_and_run,
    random_error_emoji,
    random_success_emoji,
    update_git_repo,
)

app = Typer()


def setup():
    """
    Setup before running commands.
    """
    check_requirements([
        "git",
        "terraform"
    ])
    check_for_env_vars(
        env_vars=[
            "GOOGLE_APPLICATION_CREDENTIALS",
            "TF_VAR_bucket_name",
            "TF_VAR_project_id",
        ]
    )
    update_git_repo()
    echo_and_run(
        f"cd {constants.IAC_DIRECTORY.value}/gke && terraform init && terraform refresh",
        stdout_callback=lambda _: None,
    )


@app.command()
def apply():
    """
    Applies the changes to the GKE cluster.
    """
    setup()
    echo_and_run(
        f"cd {constants.IAC_DIRECTORY.value}/gke && terraform apply -auto-approve",
    )


@app.command()
def destroy():
    """
    Tears down the GKE cluster.
    """
    setup()
    echo_and_run(
        f"cd {constants.IAC_DIRECTORY.value}/gke && terraform destroy -auto-approve",
    )


@app.command()
def plan():
    """
    Plans the changes to the GKE cluster.
    """
    setup()
    echo_and_run(
        f"cd {constants.IAC_DIRECTORY.value}/gke && terraform plan",
    )


@app.command()
def status():
    """
    Prints the status of the GKE cluster.
    """
    setup()
    output_str = [""]
    echo_and_run(
        f"cd {constants.IAC_DIRECTORY.value}/gke && terraform plan -refresh-only",
        stdout_callback=partial(append_output_to_string,
                                wrapped_string=output_str)
    )
    output_str = output_str[0]
    if (
        (output_str.find("0 to add, 0 to change, 0 to destroy") != -1)
        or
        (output_str.find("No changes.") != -1)
    ):
        log(f"{random_success_emoji()} Tudo certo!")
    else:
        log(
            f"{random_error_emoji()} Ainda há mudanças que precisam ser aplicadas.")
        log(f"Execute `{argv[0]} gke plan` para verificar as mudanças.")
