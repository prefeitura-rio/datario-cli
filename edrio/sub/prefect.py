"""
Prefect Agent management through Helm and kubectl
"""

import base64
from os import getenv

from typer import Typer
import yaml

from edrio.constants import Constants as constants
from edrio.logger import log
from edrio.utils import (
    check_for_env_vars,
    check_requirements,
    file_exists,
    load_env_file,
    update_git_repo,
)

app = Typer()


def build_secrets_yaml():
    """
    Builds the secrets.yaml file.
    """
    # Get inputs
    project_name: str = getenv("TF_VAR_project_id")
    bd_prod_sa_path: str = getenv("BASEDOSDADOS_CREDENTIALS_PROD_PATH")
    bd_staging_sa_path: str = getenv("BASEDOSDADOS_CREDENTIALS_STAGING_PATH")
    vault_token: str = getenv("VAULT_TOKEN")

    # Open and split secrets documents
    with open(constants.IAC_PREFECT_SECRETS_BASE_PATH.value) as secrets_base_file:
        txt = secrets_base_file.read()
    documents = txt.split("---")
    yamls = [yaml.safe_load(document) for document in documents]
    yamls = [yaml for yaml in yamls if yaml]
    yamls_dict = {yaml["metadata"]["name"]: yaml for yaml in yamls}

    # Update values on secrets
    # First the basedosdados config.toml
    with open(constants.IAC_PREFECT_BD_CONFIG_BASE_PATH.value) as bd_config_base_file:
        txt = bd_config_base_file.read()
    txt.replace("your-project-name", project_name)
    yamls_dict["gcp-credentials"]["data"]["BASEDOSDADOS_CONFIG"] = base64.b64encode(
        txt.encode()).decode()
    # Basedosdados prod service account
    with open(bd_prod_sa_path) as bd_prod_sa_file:
        txt = bd_prod_sa_file.read()
    yamls_dict["gcp-credentials"]["data"]["BASEDOSDADOS_CREDENTIALS_PROD"] = base64.b64encode(
        txt.encode()).decode()
    # Basedosdados staging service account
    with open(bd_staging_sa_path) as bd_staging_sa_file:
        txt = bd_staging_sa_file.read()
    yamls_dict["gcp-credentials"]["data"]["BASEDOSDADOS_CREDENTIALS_STAGING"] = base64.b64encode(
        txt.encode()).decode()
    # Now the Vault address
    yamls_dict["vault-credentials"]["data"]["VAULT_ADDRESS"] = base64.b64encode(
        constants.DATARIO_VAULT_EXTERNAL_ADDRESS.value.encode()).decode()
    # And finally the Vault token
    yamls_dict["vault-credentials"]["data"]["VAULT_TOKEN"] = base64.b64encode(
        vault_token.encode()).decode()

    # Dump secrets.yaml
    with open(constants.IAC_PREFECT_SECRETS_PATH.value, "w") as secrets_file:
        yaml.safe_dump_all(yamls_dict.values(), secrets_file)


def build_values_yaml():
    """
    Builds the values.yaml file.
    """
    # TODO: implement this


def setup():
    """
    Setup before running commands.
    """
    check_requirements([
        "git",
        "helm",
        "kubectl",
    ])
    check_for_env_vars([
        "BASEDOSDADOS_CREDENTIALS_PROD_PATH",
        "BASEDOSDADOS_CREDENTIALS_STAGING_PATH",
        "TF_VAR_project_id",
        "VAULT_TOKEN",
    ])
    load_env_file()
    update_git_repo()
    if not file_exists(constants.IAC_PREFECT_SECRETS_PATH.value):
        build_secrets_yaml()


@app.command()
def apply():
    """
    Applies Prefect Agent manifests
    """
    setup()
    # TODO: implement


@app.command()
def destroy():
    """
    Tears down Prefect Agent manifests
    """
    setup()
    # TODO: implement


@app.command()
def status():
    """
    Checks Prefect Agent status
    """
    setup()
    # TODO: implement
