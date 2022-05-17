"""
Prefect Agent management through Helm and kubectl
"""

import base64
from os import getenv

import requests
from typer import Typer
import yaml

from datario_cli.constants import Constants as constants
from datario_cli.logger import log
from datario_cli.utils import (
    check_for_env_vars,
    check_requirements,
    echo_and_run,
    file_exists,
    get_confirmation,
    get_current_kubectl_context,
    load_env_file,
    random_emoji,
    random_emoji,
    update_git_repo,
)

app = Typer()


def to_single_base64(text: str) -> str:
    """
    Converts a string to a single base64 representation.
    """
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')


def to_double_base64(text: str) -> str:
    """
    Converts a string to a double base64 representation.
    """
    first_step = to_single_base64(text)
    second_step = to_single_base64(first_step)
    return second_step


def build_secrets_yaml():
    """
    Builds the secrets.yaml file.
    """
    # Get inputs
    project_name: str = getenv("TF_VAR_project_id")
    bd_prod_sa_path: str = getenv("BASEDOSDADOS_CREDENTIALS_PROD_PATH")
    bd_staging_sa_path: str = getenv("BASEDOSDADOS_CREDENTIALS_STAGING_PATH")
    vault_token: str = getenv("VAULT_TOKEN")
    prefect_api_key: str = getenv("PREFECT_TOKEN")
    prefect_tenant_id: str = getenv("PREFECT_TENANT_ID")

    # Open and split secrets documents
    with open(constants.IAC_PREFECT_SECRETS_BASE_PATH.value) as secrets_base_file:
        txt = secrets_base_file.read()
    documents = txt.split("---")
    yamls = [yaml.safe_load(document) for document in documents]
    yamls = [yaml for yaml in yamls if yaml]
    yamls_dict = {yaml["metadata"]["name"]: yaml for yaml in yamls}

    # Update values on secrets
    # GCP SA
    # Open up the prod credentials file
    with open(bd_prod_sa_path) as bd_prod_sa_file:
        txt = bd_prod_sa_file.read()
    yamls_dict["gcp-sa"]["data"]["creds.json"] = to_single_base64(txt)
    # DBT credentials
    with open(bd_prod_sa_path) as bd_prod_sa_file:
        txt = bd_prod_sa_file.read()
    yamls_dict["credentials-dev"]["data"]["dev.json"] = to_single_base64(txt)
    yamls_dict["credentials-prod"]["data"]["prod.json"] = to_single_base64(txt)
    # Prefect
    # Open up the auth.toml file
    with open(constants.IAC_PREFECT_AUTH_TOML_PATH.value) as auth_toml_file:
        txt = auth_toml_file.read()
    txt = txt.replace("prefect-api-key", prefect_api_key)
    txt = txt.replace("prefect-tenant-id", prefect_tenant_id)
    yamls_dict["prefect-auth-toml"]["data"]["auth.toml"] = to_single_base64(
        txt)
    # Basedosdados
    # First the basedosdados config.toml
    with open(constants.IAC_PREFECT_BD_CONFIG_BASE_PATH.value) as bd_config_base_file:
        txt = bd_config_base_file.read()
    txt = txt.replace("your-project-name", project_name)
    yamls_dict["gcp-credentials"]["data"]["BASEDOSDADOS_CONFIG"] = to_double_base64(
        txt)
    # Basedosdados prod service account
    with open(bd_prod_sa_path) as bd_prod_sa_file:
        txt = bd_prod_sa_file.read()
    yamls_dict["gcp-credentials"]["data"]["BASEDOSDADOS_CREDENTIALS_PROD"] = to_double_base64(
        txt)
    # Basedosdados staging service account
    with open(bd_staging_sa_path) as bd_staging_sa_file:
        txt = bd_staging_sa_file.read()
    yamls_dict["gcp-credentials"]["data"]["BASEDOSDADOS_CREDENTIALS_STAGING"] = to_double_base64(
        txt)
    # Vault
    # Now the Vault address
    yamls_dict["vault-credentials"]["data"]["VAULT_ADDRESS"] = to_single_base64(
        constants.DATARIO_VAULT_EXTERNAL_ADDRESS.value)
    # And finally the Vault token
    yamls_dict["vault-credentials"]["data"]["VAULT_TOKEN"] = to_single_base64(
        vault_token)

    # Dump secrets.yaml
    with open(constants.IAC_PREFECT_SECRETS_PATH.value, "w") as secrets_file:
        yaml.safe_dump_all(yamls_dict.values(), secrets_file)


def build_values_yaml():
    """
    Builds the values.yaml file.
    """
    # Get inputs
    project_name: str = getenv("TF_VAR_project_id")

    # Open base file
    with open(constants.IAC_PREFECT_VALUES_BASE_PATH.value) as values_base_file:
        values = yaml.safe_load(values_base_file)

    # Add labels to the Prefect Agent
    values["agent"]["prefectLabels"] = [project_name]

    # Modify the Apollo URL
    values["agent"]["apollo_url"] = "https://prefect.dados.rio/api/"

    # Dump values.yaml
    with open(constants.IAC_PREFECT_VALUES_PATH.value, "w") as values_file:
        yaml.safe_dump(values, values_file)


def accept_existing_helm_repo(status_code):
    if status_code == 1:
        return
    raise Exception("Error while adding the helm repo")


def setup(check_build: bool = True):
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
    if check_build:
        if not file_exists(constants.IAC_PREFECT_SECRETS_PATH.value):
            log(f'{random_emoji("error")} Agent secrets file not found. Building...', "warning")
            build_secrets_yaml()
            log(f'{random_emoji("success")} Agent secrets file built.', "success")
        if not file_exists(constants.IAC_PREFECT_VALUES_PATH.value):
            log(f'{random_emoji("error")} Agent values file not found. Building...', "warning")
            build_values_yaml()
            log(f'{random_emoji("success")} Agent values file built.', "success")
    echo_and_run(
        "helm repo add prefeitura-rio https://helm.dados.rio", on_error=accept_existing_helm_repo)
    echo_and_run("helm repo update")


@app.command()
def apply(context: str = None):
    """
    Applies Prefect Agent manifests
    """
    setup()
    if context is None:
        context = get_current_kubectl_context()
    log(f'{random_emoji("technology")} Aplicando os manifestos do Kubernetes...')
    log(f'{random_emoji("technology")} Criando namespace...')
    echo_and_run(
        f"kubectl apply -f {constants.IAC_PREFECT_NAMESPACE_PATH.value}"
        f" --context {context}"
    )
    log(f'{random_emoji("technology")} Criando secrets...')
    echo_and_run(
        f"kubectl apply -f {constants.IAC_PREFECT_SECRETS_PATH.value}"
        f" --context {context}"
        " --namespace prefect"
    )
    log(f'{random_emoji("technology")} Instalando o Helm chart...')
    echo_and_run(
        "helm upgrade --install prefect-agent"
        " prefeitura-rio/prefect-agent"
        " --namespace prefect"
        f" --kube-context {context}"
        f" -f {constants.IAC_PREFECT_VALUES_PATH.value}"
    )
    log(f'{random_emoji("success")} O deployment do Prefect Agent foi um sucesso!', "success")


@app.command()
def build():
    """
    Builds Kubernetes manifests and Helm values
    """
    setup(check_build=False)
    log("Building agent secrets file...")
    build_secrets_yaml()
    log(f'{random_emoji("success")} Agent secrets file built.', "success")
    log("Building agent values...")
    build_values_yaml()
    log(f'{random_emoji("success")} Agent values file built.', "success")


@app.command()
def destroy(context: str = None):
    """
    Tears down Prefect Agent manifests
    """
    if get_confirmation("remover o Prefect Agent"):
        setup()
        if context is None:
            context = get_current_kubectl_context()
        log(f'{random_emoji("technology")} Removendo o Helm chart...')
        echo_and_run(
            "helm uninstall prefect-agent -n prefect"
            f" --kube-context {context}"
        )
        log(f'{random_emoji("technology")} Removendo os manifestos do Kubernetes...')
        log(f'{random_emoji("technology")} Removendo os secrets...')
        echo_and_run(
            f"kubectl delete -f {constants.IAC_PREFECT_SECRETS_PATH.value}"
            f" --context {context}"
            " --namespace prefect"
        )
        log(f'{random_emoji("technology")} Removendo o namespace...')
        echo_and_run(
            f"kubectl delete -f {constants.IAC_PREFECT_NAMESPACE_PATH.value}"
            f" --context {context}"
        )
        log(f'{random_emoji("success")} O Prefect Agent foi removido com sucesso!', "success")


@app.command()
def status(context: str = None):
    """
    Checks Prefect Agent status
    """
    value = ""

    def callback(output: str):
        nonlocal value
        value += output.strip()

    setup()
    if context is None:
        context = get_current_kubectl_context()

    prefect_api_key = getenv("PREFECT_TOKEN")

    log(f'{random_emoji("technology")} Verificando o status dos manifestos...')
    return_code = echo_and_run(
        f"kubectl diff -f {constants.IAC_PREFECT_SECRETS_PATH.value}"
        f" --context {context}"
        " --namespace prefect",
        stdout_callback=callback,
        on_error="return",
    )
    if value == "" and return_code == 0:
        log(f'{random_emoji("success")} Os manifestos do Prefect Agent estão OK!', "success")
    else:
        log(f'{random_emoji("error")} Os manifestos do Prefect Agent diferem do esperado!',
            "error")

    log(f'{random_emoji("technology")} Verificando o status do Helm chart...')
    return_code = echo_and_run(
        "helm status prefect-agent"
        f" --kube-context {context}"
        " --namespace prefect",
        stdout_callback=callback,
        on_error="return",
    )
    if "STATUS: deployed" in value and return_code == 0:
        log(f'{random_emoji("success")} O Helm chart do Prefect Agent está OK!', "success")
    else:
        log(f'{random_emoji("error")} O Helm chart do Prefect Agent está diferente do esperado!',
            "error")

    log(f'{random_emoji("technology")} Verificando capacidade de conexão com o Prefect Server...')
    value = ""
    try:
        response = requests.get("https://prefect.dados.rio/api", headers={
            "Authorization": f"Bearer {prefect_api_key}",
        })
        value = response.text
        return_code = 0
    except Exception:
        return_code = 1
    if "GET query missing" in value and return_code == 0:
        log(f'{random_emoji("success")} A conexão com o Prefect Server funciona!', "success")
    else:
        log(f'{random_emoji("error")} A conexão com o Prefect Server não funciona!', "error")
